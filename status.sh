#!/bin/bash
# Jarvis 상태 확인

JARVIS_ROOT="/Users/sclee1115/Project/Dev/jarvis"

echo "=== Jarvis Status ==="
echo ""

# processor
if pgrep -f "processor.sh" > /dev/null; then
  echo "✅ Processor: running (PID: $(pgrep -f processor.sh))"
else
  echo "❌ Processor: stopped"
fi

# openclaw
if pgrep -f "openclaw" > /dev/null; then
  echo "✅ OpenClaw:  running (PID: $(pgrep -f openclaw))"
else
  echo "❌ OpenClaw:  stopped"
fi

# 큐 상태
INBOX=$(ls "$JARVIS_ROOT/bridge/inbox/"*.json 2>/dev/null | wc -l | tr -d ' ')
QUEUE=$(ls "$JARVIS_ROOT/bridge/queue/"*.json 2>/dev/null | wc -l | tr -d ' ')
PENDING=$(ls "$JARVIS_ROOT/bridge/pending/"*.json 2>/dev/null | wc -l | tr -d ' ')

echo "📥 Inbox:   $INBOX"
echo "📦 Queue:   $QUEUE"
echo "⏳ Pending: $PENDING"
echo ""

# 최근 로그
echo "=== Recent Log ==="
tail -5 "$JARVIS_ROOT/bridge/processor.log" 2>/dev/null || echo "(no log)"
