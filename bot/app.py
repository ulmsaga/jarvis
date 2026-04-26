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

    # 채널 멘션 <#CHANNELID|채널명> 또는 <#CHANNELID> 또는 #project-name 태그로 프로젝트 추출
    channel_mention = re.search(r"<#([A-Z0-9]+)(?:\|([^>]+))?>", clean)
    project_tag = re.search(r"(?<!<)#([A-Za-z0-9_-]+)", clean)
    if channel_mention:
        channel_id = channel_mention.group(1)
        channel_name = channel_mention.group(2)
        if not channel_name:
            try:
                info = client.conversations_info(channel=channel_id)
                channel_name = info["channel"]["name"]
            except Exception:
                channel_name = channel_id
        project = channel_name
        command = re.sub(r"<#[A-Z0-9]+(?:\|[^>]+)?>", "", clean).strip()
    elif project_tag:
        project = project_tag.group(1)
        command = re.sub(r"#[A-Za-z0-9_-]+", "", clean).strip()
    else:
        project = "unknown"
        command = clean

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
    print(f"[MENTION] {event.get('user')} → {text}", flush=True)

    task = parse_message(text, client, event)
    print(f"[TASK] from={task['from']} project={task['project']} command={task['command']}", flush=True)

    if not task["command"]:
        say(text="명령어를 입력해 주세요.")
        # thread_ts=event["ts"]  # 댓글 비활성화
        return

    path = save_task(task)
    print(f"[QUEUE] 저장됨: {path}", flush=True)

    client.chat_postMessage(
        channel=event["channel"],
        # thread_ts=event["ts"],  # 댓글 비활성화 — 직접 메시지로 전송
        text="작업 중입니다. 잠시만 기다려 주세요.",
    )
    print(f"[SLACK] 접수 응답 전송 완료", flush=True)


@app.event("message")
def handle_message(event, client):
    # 봇 자신의 메시지, 서브타입 메시지 무시
    if event.get("subtype") or event.get("bot_id"):
        return

    # DM 처리 (channel_type이 im인 경우)
    if event.get("channel_type") != "im":
        return

    text = event.get("text", "").strip()
    if not text:
        return

    print(f"[DM] {event.get('user')} → {text}", flush=True)

    task = parse_message(text, client, event)
    print(f"[TASK] from={task['from']} project={task['project']} command={task['command']}", flush=True)

    if not task["command"]:
        client.chat_postMessage(channel=event["channel"], text="명령어를 입력해 주세요.")
        return

    path = save_task(task)
    print(f"[QUEUE] 저장됨: {path}", flush=True)

    client.chat_postMessage(
        channel=event["channel"],
        # thread_ts=event["ts"],  # 댓글 비활성화 — 직접 메시지로 전송
        text="작업 중입니다. 잠시만 기다려 주세요.",
    )
    print(f"[SLACK] 접수 응답 전송 완료", flush=True)


if __name__ == "__main__":
    app_token = os.environ.get("SLACK_APP_TOKEN", "")
    if not app_token:
        print("ERROR: SLACK_APP_TOKEN이 .env에 없습니다.")
        print("Slack App 설정 → Socket Mode → App-Level Token(connections:write)을 발급하세요.")
        exit(1)

    print("🤖 Jarvis Bot 시작 (Socket Mode)")
    handler = SocketModeHandler(app, app_token)
    handler.start()
