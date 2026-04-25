#!/bin/bash
# JARVIS Processor — 단순 접수/라우터 (실행은 메인 세션이 담당)

JARVIS_ROOT="/Users/sclee1115/Project/Dev/jarvis"
INBOX="$JARVIS_ROOT/bridge/inbox"
QUEUE="$JARVIS_ROOT/bridge/queue"
PENDING="$JARVIS_ROOT/bridge/pending"
BOT_TOKEN="${SLACK_BOT_TOKEN}"

mkdir -p "$INBOX" "$QUEUE" "$PENDING"

slack_send() {
  local channel="$1"
  local text="$2"
  curl -s -X POST "https://slack.com/api/chat.postMessage" \
    -H "Authorization: Bearer $BOT_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"channel\": \"$(echo "$channel" | sed 's/user://')\", \"text\": $(echo "$text" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')}" \
    > /dev/null 2>&1
}

route_file() {
  local file="$1"
  local filename=$(basename "$file")

  local command=$(python3 -c "import json; d=json.load(open('$file')); print(d.get('command',''))" 2>/dev/null)
  local channel=$(python3 -c "import json; d=json.load(open('$file')); print(d.get('channel',''))" 2>/dev/null)

  [ -z "$command" ] && { mv "$file" "$QUEUE/"; return; }

  # 대기 중인 선택 응답인지 확인
  if [ -f "$PENDING/current.json" ]; then
    echo "REPLY:$filename:$command"
    mv "$file" "$QUEUE/$filename"
  else
    echo "NEW_TASK:$filename:$command"
    slack_send "$channel" "⚙️ 접수됨 — JARVIS가 처리합니다"
    mv "$file" "$QUEUE/$filename"
  fi
}

echo "PROCESSOR_STARTED"

while true; do
  for file in "$INBOX"/*.json; do
    [ -f "$file" ] || continue
    route_file "$file"
  done
  sleep 2
done
