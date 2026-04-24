"""작업 분해 · 스킬 위임 결정 (OpenAI / Codex 기반)"""
from openai import AsyncOpenAI
from src.config import settings

_client = AsyncOpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = """당신은 Jarvis의 Brain입니다. 팀원의 Slack 메시지를 분석하여 어떤 스킬을 실행할지 결정합니다.

사용 가능한 스킬:
- code-review : GitHub PR URL이 포함된 경우
- safe-security-fix : 보안 취약점 수정 요청 (fix, 보안, security, 취약점)
- generate-docs : 문서/docstring 생성 요청 (doc, 문서, readme)
- help : 도움말 요청

응답은 반드시 아래 JSON 형식으로만 답하세요:
{
  "skill": "<스킬명>",
  "target": "<URL 또는 파일 경로 또는 설명>",
  "reason": "<한 줄 이유>"
}

알 수 없는 요청이면 skill을 "unknown"으로 설정하세요."""


async def decide(user_message: str, history: list[dict]) -> dict:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history[-6:])  # 최근 3턴
    messages.append({"role": "user", "content": user_message})

    response = await _client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0,
    )

    import json
    try:
        return json.loads(response.choices[0].message.content)
    except Exception:
        return {"skill": "unknown", "target": user_message, "reason": "파싱 실패"}
