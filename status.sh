#!/bin/bash
# Jarvis 상태 확인

JARVIS_ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "=== Jarvis Status ==="

check() {
  local name="$1"
  local pidfile="$2"
  if [ -f "$pidfile" ] && kill -0 "$(cat "$pidfile")" 2>/dev/null; then
    echo "✅ $name: running (PID: $(cat "$pidfile"))"
  else
    echo "❌ $name: not running"
  fi
}

check "Bot"      "/tmp/jarvis-bot.pid"
check "Injector" "/tmp/jarvis-injector.pid"

echo ""
PANE=$(cat /tmp/jarvis-pane 2>/dev/null)
if [ -n "$PANE" ]; then
  echo "🖥  Claude Code pane: $PANE"
else
  echo "⚠️  Claude Code pane: 미등록"
fi

QUEUE_COUNT=$(ls "$JARVIS_ROOT/bridge/queue"/task-*.json 2>/dev/null | wc -l | tr -d ' ')
echo "📬 Queue 대기: ${QUEUE_COUNT}건"

echo ""
echo "=== Recent Bot Log ==="
tail -5 "$JARVIS_ROOT/bridge/bot.log" 2>/dev/null || echo "(no log)"
