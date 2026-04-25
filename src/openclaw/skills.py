"""스킬 실행 — Claude Code CLI 전용 (Pro 구독, API 키 불필요)"""
import asyncio
import re
import shutil
from pathlib import Path

_SKILLS_PATH = Path(__file__).parent.parent.parent / "SKILLS.md"


def load_skills() -> dict[str, str]:
    text = _SKILLS_PATH.read_text(encoding="utf-8")
    skills: dict[str, str] = {}
    current, lines = None, []
    for line in text.splitlines():
        m = re.match(r"^## (.+)$", line)
        if m:
            if current:
                skills[current] = "\n".join(lines).strip()
            current, lines = m.group(1).strip(), []
        elif current:
            lines.append(line)
    if current:
        skills[current] = "\n".join(lines).strip()
    return skills


SKILLS = load_skills()

_HELP_TEXT = """*Jarvis 사용 가능한 스킬:*
• `code-review` — GitHub PR 또는 코드베이스 리뷰
• `safe-security-fix` — 보안 취약점 탐지 및 수정
• `generate-docs` — docstring / README 자동 생성

*사용법:*
```
@bot review  repo:vizops branch:main skill:code-review
@bot fix     repo:vizops branch:main skill:safe-security-fix
@bot doc     repo:vizops branch:main skill:generate-docs
```
"""


def _build_prompt(skill_name: str, worktree: Path | None, target: str) -> str:
    loc = f"작업 디렉토리: {worktree}" if worktree else f"대상: {target}"
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

수행 항목:
1. SQL Injection / XSS / CSRF 탐지 및 수정
2. 하드코딩된 비밀번호·API 키 제거
3. 안전하지 않은 함수 교체
4. 수정 완료 후 요약: "N applied · M skipped"

수정한 파일명과 변경 내용을 보고하세요.""",

        "generate-docs": f"""이 코드베이스의 문서를 생성하고 파일에 적용하세요.
{loc}

생성 항목:
- Google 스타일 docstring (모든 함수·클래스)
- README.md 업데이트
- 완료 후 요약 보고""",
    }
    return prompts.get(skill_name, f"다음 요청을 처리하세요: {target}")


async def _run_claude_cli(prompt: str, cwd: Path) -> str:
    proc = await asyncio.create_subprocess_exec(
        "claude", "--print", "--dangerously-skip-permissions", prompt,
        cwd=str(cwd),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=300)
    output = stdout.decode().strip()
    return output or stderr.decode().strip()


async def run(skill_name: str, target: str, worktree: Path | None = None) -> str:
    if skill_name == "help":
        return _HELP_TEXT

    if skill_name == "unknown":
        return "❓ 요청을 이해하지 못했습니다. `@bot help`로 사용 가능한 스킬을 확인하세요."

    if not shutil.which("claude"):
        return (
            "❌ Claude Code CLI가 설치되어 있지 않습니다.\n"
            "설치: `npm install -g @anthropic-ai/claude-code`\n"
            "설치 후 `claude login`으로 Pro 계정 연결해주세요."
        )

    prompt = _build_prompt(skill_name, worktree, target)
    cwd = worktree if worktree else Path.cwd()
    return await _run_claude_cli(prompt, cwd)
