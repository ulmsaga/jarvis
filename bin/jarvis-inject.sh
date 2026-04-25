#!/bin/bash
# Slack queue 작업을 Claude Code 세션(tmux pane)에 직접 주입

QUEUE="/Users/sclee1115/Project/Dev/jarvis/bridge/queue"
PROCESSING="/Users/sclee1115/Project/Dev/jarvis/bridge/processing"
PANE_FILE="/tmp/jarvis-active-pane"

mkdir -p "$PROCESSING"

# 대상 pane 확인
PANE=$(cat "$PANE_FILE" 2>/dev/null)
if [ -z "$PANE" ]; then
  echo "ERROR: /tmp/jarvis-active-pane 없음 — 'jarvis' 명령으로 Claude Code를 시작했는지 확인"
  exit 1
fi

for f in "$QUEUE"/*.json; do
  [ -f "$f" ] || continue

  fname=$(basename "$f")
  mv "$f" "$PROCESSING/$fname"

  COMMAND=$(python3 -c "import json; d=json.load(open('$PROCESSING/$fname')); print(d.get('command',''))" 2>/dev/null)
  FROM=$(python3 -c "import json; d=json.load(open('$PROCESSING/$fname')); print(d.get('from',''))" 2>/dev/null)
  CHANNEL=$(python3 -c "import json; d=json.load(open('$PROCESSING/$fname')); print(d.get('channel',''))" 2>/dev/null)

  tmux send-keys -t "$PANE" "[SLACK] from:$FROM channel:$CHANNEL | $COMMAND" Enter

  echo "주입됨: $fname → $PANE"
done
