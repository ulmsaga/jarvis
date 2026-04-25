#!/bin/bash
# Queue 감시 → Claude Code 세션에 프롬프트 주입

JARVIS_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
QUEUE="$JARVIS_ROOT/bridge/queue"
PROCESSING="$JARVIS_ROOT/bridge/processing"
PANE_FILE="/tmp/jarvis-pane"

mkdir -p "$PROCESSING"

log() { echo "[$(date '+%H:%M:%S')] $*"; }

get_pane() {
  local pane
  pane=$(cat "$PANE_FILE" 2>/dev/null)
  [ -z "$pane" ] && return 1
  # pane이 실제 존재하는지 확인
  tmux list-panes -t "$pane" > /dev/null 2>&1 || return 1
  echo "$pane"
}

inject_task() {
  local file="$1"
  local fname
  fname=$(basename "$file")

  local pane
  pane=$(get_pane) || { log "SKIP: pane 미등록 ($fname)"; return 1; }

  local command from project channel reply_ts
  command=$(python3  -c "import json; d=json.load(open('$file')); print(d.get('command',''))" 2>/dev/null)
  from=$(python3     -c "import json; d=json.load(open('$file')); print(d.get('from',''))" 2>/dev/null)
  project=$(python3  -c "import json; d=json.load(open('$file')); print(d.get('project',''))" 2>/dev/null)
  channel=$(python3  -c "import json; d=json.load(open('$file')); print(d.get('channel',''))" 2>/dev/null)
  reply_ts=$(python3 -c "import json; d=json.load(open('$file')); print(d.get('reply_ts',''))" 2>/dev/null)

  [ -z "$command" ] && { log "SKIP: command 없음 ($fname)"; mv "$file" "$PROCESSING/$fname"; return 0; }

  mv "$file" "$PROCESSING/$fname"

  local prompt="[JARVIS] from:${from} project:${project} channel:${channel} reply_ts:${reply_ts} | ${command}"
  tmux send-keys -t "$pane" "$prompt"
  sleep 0.3
  tmux send-keys -t "$pane" "" Enter

  log "주입 완료: $fname → $pane"
}

log "Injector 시작 (queue: $QUEUE)"

while true; do
  for f in "$QUEUE"/task-*.json; do
    [ -f "$f" ] || continue
    inject_task "$f" || true
  done
  sleep 1
done
