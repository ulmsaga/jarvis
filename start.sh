#!/bin/bash
# Jarvis 시작 스크립트

JARVIS_ROOT="/Users/sclee1115/Project/Dev/jarvis"
TMUX_SESSION="jarvis"

# .env 로드
if [ -f "$JARVIS_ROOT/.env" ]; then
  export $(grep -v '^#' "$JARVIS_ROOT/.env" | xargs)
fi

# nvm 로드 (비로그인 셸에서도 동작하도록)
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"

# tmux 세션 (jarvis) — Claude Code 실행
if tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
  echo "✅ tmux[$TMUX_SESSION]: already running"
else
  tmux new-session -d -s "$TMUX_SESSION" -x 220 -y 50
  # Claude Code 자동 시작 (jarvis 워크스페이스)
  tmux send-keys -t "$TMUX_SESSION" "cd $JARVIS_ROOT && claude" Enter
  echo "🚀 tmux[$TMUX_SESSION]: started → claude 실행 중"
fi

# processor
if pgrep -f "processor.sh" > /dev/null; then
  echo "✅ Processor: already running (PID: $(pgrep -f processor.sh))"
else
  bash "$JARVIS_ROOT/processor.sh" >> "$JARVIS_ROOT/bridge/processor.log" 2>&1 &
  echo "🚀 Processor: started (PID: $!)"
fi

# OpenClaw (node 22 필요)
if pgrep -f "openclaw" > /dev/null; then
  echo "✅ OpenClaw: already running (PID: $(pgrep -f openclaw))"
else
  nvm use 22 --silent 2>/dev/null || nvm install 22 --silent
  openclaw >> "$JARVIS_ROOT/bridge/openclaw.log" 2>&1 &
  echo "🚀 OpenClaw: started (PID: $!)"
fi

echo ""
echo "🔍 상태 확인: bash $JARVIS_ROOT/status.sh"
