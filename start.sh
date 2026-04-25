#!/bin/bash
# Jarvis 시작 스크립트

JARVIS_ROOT="/Users/sclee1115/Project/Dev/jarvis"

# .env 로드
if [ -f "$JARVIS_ROOT/.env" ]; then
  export $(grep -v '^#' "$JARVIS_ROOT/.env" | xargs)
fi

# 이미 실행 중이면 스킵
if pgrep -f "processor.sh" > /dev/null; then
  echo "✅ Jarvis processor already running (PID: $(pgrep -f processor.sh))"
else
  bash "$JARVIS_ROOT/processor.sh" >> "$JARVIS_ROOT/bridge/processor.log" 2>&1 &
  echo "🚀 Jarvis processor started (PID: $!)"
fi

echo ""
echo "📋 다음 단계:"
echo "  1. OpenClaw 앱 실행 (Slack 수신)"
echo "  2. Claude Code Monitor: $JARVIS_ROOT/bridge/processor.log"
echo ""
echo "🔍 상태 확인: bash $JARVIS_ROOT/status.sh"
