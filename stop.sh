#!/bin/bash
# Jarvis 종료 스크립트

PID=$(pgrep -f "processor.sh")
if [ -n "$PID" ]; then
  kill "$PID"
  echo "🛑 Processor: stopped (PID: $PID)"
else
  echo "ℹ️  Processor: not running"
fi

PID=$(pgrep -f "openclaw")
if [ -n "$PID" ]; then
  kill "$PID"
  echo "🛑 OpenClaw: stopped (PID: $PID)"
else
  echo "ℹ️  OpenClaw: not running"
fi
