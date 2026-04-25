import json
import os
import re
import time
from pathlib import Path

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

JARVIS_ROOT = Path(__file__).parent.parent
load_dotenv(JARVIS_ROOT / ".env")

app = App(token=os.environ["SLACK_BOT_TOKEN"])
QUEUE_DIR = JARVIS_ROOT / "bridge" / "queue"
QUEUE_DIR.mkdir(parents=True, exist_ok=True)


def parse_message(text: str, client, event: dict) -> dict:
    # 멘션 제거
    clean = re.sub(r"<@[A-Z0-9]+>", "", text).strip()

    # #project-name 태그 추출
    project_match = re.search(r"#(\S+)", clean)
    project = project_match.group(1) if project_match else "unknown"
    command = re.sub(r"#\S+", "", clean).strip()

    # 보낸 사람 display name
    try:
        user_info = client.users_info(user=event["user"])
        sender = user_info["user"]["profile"].get("display_name") or user_info["user"]["name"]
    except Exception:
        sender = event.get("user", "unknown")

    return {
        "ts": event.get("ts", str(int(time.time() * 1000))),
        "from": sender,
        "channel": event["channel"],
        "project": project,
        "command": command,
        "reply_ts": event.get("ts", ""),
    }


def save_task(task: dict) -> Path:
    filename = QUEUE_DIR / f"task-{task['ts'].replace('.', '')}.json"
    filename.write_text(json.dumps(task, ensure_ascii=False, indent=2))
    return filename


@app.event("app_mention")
def handle_mention(event, client, say):
    text = event.get("text", "")
    task = parse_message(text, client, event)

    if not task["command"]:
        say(text="명령어를 입력해 주세요.", thread_ts=event["ts"])
        return

    save_task(task)

    client.chat_postMessage(
        channel=event["channel"],
        thread_ts=event["ts"],
        text="작업 중입니다. 잠시만 기다려 주세요.",
    )


@app.event("message")
def handle_message(event, client):
    # 봇 자신의 메시지, 서브타입 메시지 무시
    if event.get("subtype") or event.get("bot_id"):
        return


if __name__ == "__main__":
    app_token = os.environ.get("SLACK_APP_TOKEN", "")
    if not app_token:
        print("ERROR: SLACK_APP_TOKEN이 .env에 없습니다.")
        print("Slack App 설정 → Socket Mode → App-Level Token(connections:write)을 발급하세요.")
        exit(1)

    print("🤖 Jarvis Bot 시작 (Socket Mode)")
    handler = SocketModeHandler(app, app_token)
    handler.start()
