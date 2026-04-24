"""Openclaw 오케스트레이터 — Brain · Skills · Memory를 연결"""
from src.openclaw import brain, skills, memory


async def handle(
    user_message: str,
    channel_id: str,
    user_id: str,
    thread_ts: str | None = None,
) -> str:
    session_id = f"{channel_id}:{user_id}"

    # Memory에서 히스토리 로드
    history = await memory.get_history(session_id)

    # Brain: 어떤 스킬을 쓸지 결정
    decision = await brain.decide(user_message, history)
    skill_name = decision.get("skill", "unknown")
    target = decision.get("target", user_message)

    # Skills: Claude Code로 실행
    result = await skills.run(skill_name, target)

    # Memory: 대화 기록 저장
    await memory.append_history(session_id, channel_id, user_id, "user", user_message)
    await memory.append_history(session_id, channel_id, user_id, "assistant", result)

    return result
