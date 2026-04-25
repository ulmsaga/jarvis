#!/bin/bash
# Jarvis 종료 스크립트

TMUX_SESSION="jarvis"

# processor 종료
if pgrep -f "processor.sh" > /dev/null; then
  pkill -f "processor.sh"
  echo "🛑 Processor: stopped"
else
  echo "ℹ️  Processor: not running"
fi

# OpenClaw 종료
if pgrep -f "openclaw" > /dev/null; then
  pkill -f "openclaw"
  echo "🛑 OpenClaw: stopped"
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
