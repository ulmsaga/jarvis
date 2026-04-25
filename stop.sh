#!/bin/bash
# Jarvis 종료 스크립트

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
