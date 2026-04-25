#!/bin/bash
# Slack 스레드에 결과 메시지 전송
# 사용법: notify.sh <channel> <reply_ts> <message>

JARVIS_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
source "$JARVIS_ROOT/.env" 2>/dev/null

CHANNEL="$1"
REPLY_TS="$2"
MESSAGE="$3"

if [ -z "$CHANNEL" ] || [ -z "$MESSAGE" ]; then
  echo "Usage: notify.sh <channel> <reply_ts> <message>" >&2
  exit 1
fi

PAYLOAD=$(python3 -c "
import json, sys
channel = sys.argv[1]
reply_ts = sys.argv[2]
message = sys.argv[3]
obj = {'channel': channel, 'text': message}
if reply_ts:
    obj['thread_ts'] = reply_ts
print(json.dumps(obj))
" "$CHANNEL" "$REPLY_TS" "$MESSAGE")

curl -s -X POST "https://slack.com/api/chat.postMessage" \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" | python3 -c "
import json, sys
r = json.load(sys.stdin)
if r.get('ok'):
    print('OK')
else:
    print('ERROR: ' + r.get('error','unknown'), file=sys.stderr)
    sys.exit(1)
"
