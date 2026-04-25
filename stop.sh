#!/bin/bash
# Jarvis 종료 스크립트

TMUX_SESSION="jarvis"

# processor 종료
PID=$(pgrep -f "processor.sh")
if [ -n "$PID" ]; then
  kill $PID 2>/dev/null
  echo "🛑 Processor: stopped (PID: $PID)"
else
  echo "ℹ️  Processor: not running"
fi

# OpenClaw 종료
PID=$(pgrep -f "openclaw")
if [ -n "$PID" ]; then
  kill $PID 2>/dev/null
  echo "🛑 OpenClaw: stopped (PID: $PID)"
else
  echo "ℹ️  OpenClaw: not running"
fi

# tmux jarvis 세션 종료
if tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
  tmux kill-session -t "$TMUX_SESSION"
  echo "🛑 tmux[$TMUX_SESSION]: stopped"
else
  echo "ℹ️  tmux[$TMUX_SESSION]: not running"
fi
