"""스킬 실행 — Claude Code CLI subprocess 우선, API fallback"""
import asyncio
import re
import shutil
from pathlib import Path
from anthropic import AsyncAnthropic
from src.config import settings

_client = AsyncAnthropic(api_key=settings.anthropic_api_key)
_SKILLS_PATH = Path(__file__).parent.parent.parent / "SKILLS.md"


def load_skills() -> dict[str, str]:
    text = _SKILLS_PATH.read_text(encoding="utf-8")
    skills: dict[str, str] = {}
    current = None
    lines: list[str] = []
    for line in text.splitlines():
        m = re.match(r"^## (.+)$", line)
        if m:
            if current:
                skills[current] = "\n".join(lines).strip()
            current = m.group(1).strip()
            lines = []
        elif current:
            lines.append(line)
    if current:
        skills[current] = "\n".join(lines).strip()
    return skills


SKILLS = load_skills()


def _build_prompt(skill_name: str, worktree: Path | None, target: str) -> str:
    loc = f"워크트리: {worktree}" if worktree else f"대상: {target}"
    prompts = {
        "code-review": f"""이 코드베이스를 리뷰해주세요.
{loc}

리뷰 항목:
1. 코드 품질 · 가독성
2. 잠재적 버그
3. 보안 이슈
4. 개선 제안

파일명과 줄 번호를 포함해 구체적으로 작성하세요.""",

        "safe-security-fix": f"""이 코드베이스의 보안 취약점을 찾아 실제로 수정하세요.
{loc}

수행:
1. SQL Injection / XSS / CSRF 탐지 및 수정
2. 하드코딩된 비밀번호·API 키 제거
3. 안전하지 않은 함수 교체
4. 수정 후 요약: "N applied · M skipped · X/Y tests pass"

각 수정 사항을 파일명과 함께 보고하세요.""",

        "generate-docs": f"""이 코드베이스의 문서를 생성하고 파일에 적용하세요.
{loc}

생성:
- Google 스타일 docstring (함수·클래스 전체)
- README.md 업데이트
- 완료 후 요약 보고""",
    }
    return prompts.get(skill_name, f"다음 요청을 처리하세요: {target}")


async def _run_claude_cli(prompt: str, cwd: Path) -> str:
    """Claude Code CLI로 워크트리에서 실행"""
    proc = await asyncio.create_subprocess_exec(
        "claude", "--print", "--dangerously-skip-permissions", prompt,
        cwd=str(cwd),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=300)
    output = stdout.decode().strip()
    return output or stderr.decode().strip()


async def _run_claude_api(prompt: str, worktree: Path | None) -> str:
    """Anthropic SDK fallback — worktree 파일 목록 컨텍스트 포함"""
    full_prompt = prompt
    if worktree:
        py_files = list(worktree.rglob("*.py"))[:20]
        js_files = list(worktree.rglob("*.js"))[:10]
        all_files = py_files + js_files
        file_list = "\n".join(str(f.relative_to(worktree)) for f in all_files[:25])
        if file_list:
            full_prompt += f"\n\n파일 목록:\n{file_list}"

    msg = await _client.messages.create(
        model=settings.claude_model,
        max_tokens=4096,
        messages=[{"role": "user", "content": full_prompt}],
    )
    return msg.content[0].text


async def run(skill_name: str, target: str, worktree: Path | None = None) -> str:
    if skill_name == "help":
        lines = ["*Jarvis 사용 가능한 스킬:*"]
        for k, v in SKILLS.items():
            lines.append(f"• `{k}` — {v.splitlines()[0]}")
        lines.append("\n*사용법:* `@bot fix repo:내저장소 branch:main skill:safe-security-fix`")
        return "\n".join(lines)

    if skill_name == "unknown":
        return "❓ 요청을 이해하지 못했습니다. `@bot help`로 스킬 목록을 확인하세요."

    prompt = _build_prompt(skill_name, worktree, target)

    # Claude Code CLI가 설치돼 있고 worktree가 있으면 우선 사용
    if shutil.which("claude") and worktree:
        try:
            return await _run_claude_cli(prompt, worktree)
        except Exception:
            pass  # fallback으로

    return await _run_claude_api(prompt, worktree)
