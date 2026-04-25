"""명령 파싱 — 순수 Regex 기반 (OpenAI API 불필요)"""
import re

# skill: 키워드 매핑
_SKILL_KEYWORDS: dict[str, list[str]] = {
    "code-review":       ["review", "리뷰", "코드리뷰", "pr"],
    "safe-security-fix": ["fix", "security", "보안", "취약점", "수정", "secure"],
    "generate-docs":     ["doc", "문서", "readme", "docstring", "docs"],
    "help":              ["help", "도움말", "도움", "사용법", "명령어"],
}

# 구조화 파라미터 패턴
_REPO      = re.compile(r"repo:([\w./-]+)",       re.I)
_BRANCH    = re.compile(r"branch:([\w/-]+)",      re.I)
_SKILL     = re.compile(r"skill:([\w-]+)",         re.I)
_REVIEWERS = re.compile(r"reviewers?:([@\w,|]+)", re.I)
_URL       = re.compile(r"https?://\S+")


def _detect_skill(msg: str) -> str:
    lower = msg.lower()
    for skill, keywords in _SKILL_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return skill
    return "unknown"


async def decide(user_message: str, history: list[dict]) -> dict:
    """Slack 메시지를 파싱해 실행할 스킬과 파라미터를 반환한다."""
    repo_m      = _REPO.search(user_message)
    branch_m    = _BRANCH.search(user_message)
    skill_m     = _SKILL.search(user_message)
    reviewers_m = _REVIEWERS.search(user_message)
    url_m       = _URL.search(user_message)

    skill_name = skill_m.group(1) if skill_m else _detect_skill(user_message)
    reviewers  = reviewers_m.group(1).split(",") if reviewers_m else []

    return {
        "skill":     skill_name,
        "repo":      repo_m.group(1) if repo_m else "",
        "branch":    branch_m.group(1) if branch_m else "main",
        "target":    url_m.group(0) if url_m else user_message,
        "reviewers": [r.strip() for r in reviewers if r.strip()],
    }
