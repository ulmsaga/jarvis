"""@bot 멘션 이벤트 핸들러"""
import re
from slack_bolt.async_app import AsyncApp
from src.openclaw import gateway


def register(app: AsyncApp) -> None:
    @app.event("app_mention")
    async def handle_mention(event: dict, say):
        raw_text: str = event.get("text", "")
        # <@BOT_ID> 제거
        user_message = re.sub(r"<@[A-Z0-9]+>", "", raw_text).strip()
        channel_id: str = event["channel"]
        user_id: str = event["user"]
        thread_ts: str = event.get("thread_ts", event["ts"])

        if not user_message:
            await say(text="무엇을 도와드릴까요? `@jarvis help`로 명령어를 확인하세요.", thread_ts=thread_ts)
            return

        # 처리 중 표시
        await say(text=f"⚙️ 처리 중... (`{user_message[:60]}`)", thread_ts=thread_ts)

        result = await gateway.handle(
            user_message=user_message,
            channel_id=channel_id,
            user_id=user_id,
            thread_ts=thread_ts,
        )
        await say(text=result, thread_ts=thread_ts)
