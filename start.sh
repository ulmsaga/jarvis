#!/bin/bash
# Jarvis 시작 — Bot + Injector

JARVIS_ROOT="$(cd "$(dirname "$0")" && pwd)"

source "$JARVIS_ROOT/.env" 2>/dev/null

PYTHON="$JARVIS_ROOT/.venv/bin/python3"
BOT_PID="/tmp/jarvis-bot.pid"
INJECTOR_PID="/tmp/jarvis-injector.pid"
BOT_LOG="$JARVIS_ROOT/bridge/bot.log"
INJECTOR_LOG="$JARVIS_ROOT/bridge/injector.log"

# Slack Bot
if [ -f "$BOT_PID" ] && kill -0 "$(cat "$BOT_PID")" 2>/dev/null; then
  echo "✅ Bot: already running (PID: $(cat "$BOT_PID"))"
else
  nohup "$PYTHON" -u "$JARVIS_ROOT/bot/app.py" >> "$BOT_LOG" 2>&1 &
  echo $! > "$BOT_PID"
  echo "🚀 Bot: started (PID: $!)"
fi

# Queue Injector
if [ -f "$INJECTOR_PID" ] && kill -0 "$(cat "$INJECTOR_PID")" 2>/dev/null; then
  echo "✅ Injector: already running (PID: $(cat "$INJECTOR_PID"))"
else
  nohup bash "$JARVIS_ROOT/bridge/injector.sh" >> "$INJECTOR_LOG" 2>&1 &
  echo $! > "$INJECTOR_PID"
  echo "🚀 Injector: started (PID: $!)"
fi

echo ""

# Claude Code 실행 (tmux 세션 안에 있을 때만)
if [ -n "$TMUX" ]; then
  tmux display-message -p '#{session_name}:#{window_index}.#{pane_index}' > /tmp/jarvis-pane
  echo "🖥  pane 등록: $(cat /tmp/jarvis-pane)"
  echo "🤖 Claude Code 시작..."
  exec claude
else
  echo "⚠️  tmux 밖에서 실행됨 — 'tmux attach -t jarvis' 후 다시 실행하세요"
fi
