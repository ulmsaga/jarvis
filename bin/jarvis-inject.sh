#!/bin/bash
# Slack 큐 작업을 Claude Code 세션(iTerm2)에 직접 주입

QUEUE="/Users/sclee1115/Project/Dev/jarvis/bridge/queue"
PROCESSING="/Users/sclee1115/Project/Dev/jarvis/bridge/processing"
TTY_FILE="/tmp/jarvis-tty"

mkdir -p "$PROCESSING"

[ -f "$TTY_FILE" ] || { echo "ERROR: TTY 파일 없음 ($TTY_FILE)"; exit 1; }
TARGET_TTY=$(cat "$TTY_FILE")

for f in "$QUEUE"/*.json; do
    [ -f "$f" ] || continue

    fname=$(basename "$f")
    mv "$f" "$PROCESSING/$fname"

    COMMAND=$(python3 -c "import json; d=json.load(open('$PROCESSING/$fname')); print(d.get('command',''))" 2>/dev/null)
    FROM=$(python3 -c "import json; d=json.load(open('$PROCESSING/$fname')); print(d.get('from',''))" 2>/dev/null)
    CHANNEL=$(python3 -c "import json; d=json.load(open('$PROCESSING/$fname')); print(d.get('channel',''))" 2>/dev/null)

    # 메시지 이스케이프 (AppleScript 문자열용)
    ESCAPED_CMD=$(echo "$COMMAND" | sed "s/\"/\\\\\"/g" | sed "s/'/\\\\'/g")

    osascript <<OSASCRIPT
tell application "iTerm2"
  repeat with w in windows
    repeat with t in tabs of w
      repeat with s in sessions of t
        if tty of s is "$TARGET_TTY" then
          write text "[SLACK] from:$FROM channel:$CHANNEL | $ESCAPED_CMD"
          return "ok"
        end if
      end repeat
    end repeat
  end repeat
  return "tty_not_found"
end tell
OSASCRIPT

    echo "주입됨: $fname → $TARGET_TTY"
done
