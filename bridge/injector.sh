#!/bin/bash
# Queue 감시 → Claude Code 세션에 프롬프트 주입

JARVIS_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
QUEUE="$JARVIS_ROOT/bridge/queue"
PROCESSING="$JARVIS_ROOT/bridge/processing"
PANE_FILE="/tmp/jarvis-pane"
LOCK="/tmp/jarvis-injector.lock"

mkdir -p "$PROCESSING"

log() { echo "[$(date '+%H:%M:%S')] $*"; }

# [Fix 3] 중복 실행 방지 — PID 파일 기반 (macOS 호환)
if [ -f "$LOCK" ]; then
  OLD_PID=$(cat "$LOCK")
  if kill -0 "$OLD_PID" 2>/dev/null; then
    log "이미 실행 중인 인젝터 있음 (PID: $OLD_PID) — 종료"
    exit 0
  fi
fi
echo $$ > "$LOCK"
trap "rm -f '$LOCK'" EXIT

get_pane() {
  local pane
  pane=$(cat "$PANE_FILE" 2>/dev/null)
  [ -z "$pane" ] && return 1
  tmux list-panes -t "$pane" > /dev/null 2>&1 || return 1
  echo "$pane"
}

inject_task() {
  local file="$1"
  local fname
  fname=$(basename "$file")

  local pane
  pane=$(get_pane) || { log "SKIP: pane 미등록 ($fname)"; return 1; }

  # JSON 한 번에 파싱
  local parsed
  parsed=$(python3 -c "
import json, sys
d = json.load(open('$file'))
print(d.get('command',''))
print(d.get('from',''))
print(d.get('project',''))
print(d.get('channel',''))
print(d.get('reply_ts',''))
" 2>/dev/null)

  local command from project channel reply_ts
  command=$(echo "$parsed" | sed -n '1p')
  from=$(echo "$parsed"    | sed -n '2p')
  project=$(echo "$parsed" | sed -n '3p')
  channel=$(echo "$parsed" | sed -n '4p')
  reply_ts=$(echo "$parsed" | sed -n '5p')

  if [ -z "$command" ]; then
    log "SKIP: command 없음 ($fname)"
    mv "$file" "$PROCESSING/$fname"
    return 0
  fi

  local prompt="[JARVIS] from:${from} project:${project} channel:${channel} reply_ts:${reply_ts} | ${command}"

  # [Fix 1] 주입 먼저 → 성공 시에만 processing/으로 이동
  if tmux send-keys -t "$pane" "$prompt" && sleep 0.3 && tmux send-keys -t "$pane" "" Enter; then
    mv "$file" "$PROCESSING/$fname"
    log "주입 완료: $fname → $pane"
  else
    log "FAIL: tmux 주입 실패 ($fname) — queue 유지, 재시도 예정"
    return 1
  fi
}

log "Injector 시작 (queue: $QUEUE)"

while true; do
  for f in "$QUEUE"/task-*.json; do
    [ -f "$f" ] || continue
    inject_task "$f" || true
  done
  sleep 1
done
