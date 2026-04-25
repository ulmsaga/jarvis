#!/bin/bash
# Slack 큐 작업을 Claude Code 세션(tmux jarvis)에 직접 주입

QUEUE="/Users/sclee1115/Project/Dev/jarvis/bridge/queue"
PROCESSING="/Users/sclee1115/Project/Dev/jarvis/bridge/processing"
TMUX_SESSION="jarvis"

mkdir -p "$PROCESSING"

tmux has-session -t "$TMUX_SESSION" 2>/dev/null || { echo "ERROR: tmux 세션 '$TMUX_SESSION' 없음"; exit 1; }

for f in "$QUEUE"/*.json; do
    [ -f "$f" ] || continue

    fname=$(basename "$f")
    mv "$f" "$PROCESSING/$fname"

    COMMAND=$(python3 -c "import json; d=json.load(open('$PROCESSING/$fname')); print(d.get('command',''))" 2>/dev/null)
    FROM=$(python3 -c "import json; d=json.load(open('$PROCESSING/$fname')); print(d.get('from',''))" 2>/dev/null)
    CHANNEL=$(python3 -c "import json; d=json.load(open('$PROCESSING/$fname')); print(d.get('channel',''))" 2>/dev/null)

    tmux send-keys -t "$TMUX_SESSION" "[SLACK] from:$FROM channel:$CHANNEL | $COMMAND" Enter

    echo "주입됨: $fname → tmux:$TMUX_SESSION"
done
