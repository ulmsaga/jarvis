"""SKILLS.md 파싱 + Claude Code(Anthropic)로 스킬 실행"""
import re
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


def _skill_prompt(skill_name: str, target: str) -> str:
    spec = SKILLS.get(skill_name, "")
    prompts = {
        "code-review": f"""다음 GitHub PR을 코드 리뷰해 주세요.

PR: {target}

리뷰 항목:
1. 코드 품질 및 가독성
2. 잠재적 버그
3. 보안 이슈
4. 개선 제안

Slack 메시지에 적합한 형식(짧고 명확하게)으로 작성하세요.""",

        "safe-security-fix": f"""다음 대상의 보안 취약점을 분석해 주세요.

대상: {target}

분석 항목:
- SQL Injection / XSS / CSRF
- 하드코딩된 비밀번호/키
- 안전하지 않은 함수 사용
- 인증/인가 이슈

각 취약점에 대해 [심각도] 설명 / 수정 방법을 제시하세요.""",

        "generate-docs": f"""다음 대상에 대한 문서를 생성해 주세요.

대상: {target}

생성 내용:
- 함수/클래스별 docstring (Google 스타일)
- 주요 사용 예시

마크다운 형식으로 출력하세요.""",

        "help": f"""스킬 목록:\n{chr(10).join(f'• *{k}*: {v.splitlines()[0]}' for k, v in SKILLS.items())}

사용법: `@jarvis review <PR URL>` · `@jarvis fix <경로>` · `@jarvis doc <경로>`""",
    }
    return prompts.get(skill_name, f"다음 요청을 처리해 주세요: {target}")


async def run(skill_name: str, target: str) -> str:
    if skill_name == "help":
        return _skill_prompt("help", target)

    if skill_name == "unknown":
        return "❓ 요청을 이해하지 못했습니다. `@jarvis help`로 사용 가능한 스킬을 확인하세요."

    prompt = _skill_prompt(skill_name, target)
    msg = await _client.messages.create(
        model=settings.claude_model,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text
