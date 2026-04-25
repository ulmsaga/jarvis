#!/bin/bash
# Jarvis 종료 스크립트

PID=$(pgrep -f "processor.sh")
if [ -n "$PID" ]; then
  kill "$PID"
  echo "🛑 Jarvis processor stopped (PID: $PID)"
else
  echo "ℹ️  Jarvis processor not running"
fi
