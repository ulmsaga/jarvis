"""작업 분해 · 스킬 위임 결정 — repo:, branch:, skill:, reviewers: 파싱 지원"""
import json
import re
from openai import AsyncOpenAI
from src.config import settings

_client = AsyncOpenAI(api_key=settings.openai_api_key)

# 구조화 명령 정규식: repo:xxx branch:xxx skill:xxx reviewers:@a,@b
_PARTS = re.compile(
    r"repo:(?P<repo>[\w./-]+)|"
    r"branch:(?P<branch>[\w/-]+)|"
    r"skill:(?P<skill>[\w-]+)|"
    r"reviewers?:(?P<reviewers>[@\w,|]+)",
    re.IGNORECASE,
)

SYSTEM_PROMPT = """당신은 Jarvis Brain입니다. Slack 명령을 분석해 실행할 스킬을 결정합니다.

사용 가능한 스킬:
- code-review      : GitHub PR URL 또는 repo 코드 리뷰
- safe-security-fix: 보안 취약점 탐지 및 수정
- generate-docs    : docstring / README 자동 생성
- help             : 도움말
- unknown          : 위에 해당 없음

반드시 아래 JSON만 응답하세요:
{
  "skill": "<스킬명>",
  "repo": "<owner/repo 또는 repo명, 없으면 빈 문자열>",
  "branch": "<브랜치명, 기본값 main>",
  "target": "<PR URL 또는 파일 경로 또는 설명>",
  "reviewers": ["<@유저1>", "<@유저2>"]
}"""


async def decide(user_message: str, history: list[dict]) -> dict:
    # 구조화 파싱 (regex 선추출)
    extracted: dict[str, str] = {}
    for m in _PARTS.finditer(user_message):
        for k, v in m.groupdict().items():
            if v:
                extracted[k] = v

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history[-6:])
    messages.append({"role": "user", "content": user_message})

    response = await _client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0,
    )

    try:
        result = json.loads(response.choices[0].message.content)
    except Exception:
        result = {"skill": "unknown", "repo": "", "branch": "main", "target": user_message, "reviewers": []}

    # regex 추출값으로 빈 필드 보완
    if not result.get("repo") and extracted.get("repo"):
        result["repo"] = extracted["repo"]
    if not result.get("branch") and extracted.get("branch"):
        result["branch"] = extracted["branch"]
    if not result.get("branch"):
        result["branch"] = "main"
    if not result.get("reviewers") and extracted.get("reviewers"):
        result["reviewers"] = [r for r in extracted["reviewers"].split(",") if r]

    return result
