#!/bin/bash
# Jarvis 종료 — Bot + Injector

stop_pid() {
  local name="$1"
  local pidfile="$2"
  local pattern="$3"

  if [ -f "$pidfile" ] && kill -0 "$(cat "$pidfile")" 2>/dev/null; then
    kill "$(cat "$pidfile")" 2>/dev/null
    rm -f "$pidfile"
    echo "🛑 $name: stopped"
  else
    pkill -f "$pattern" 2>/dev/null && echo "🛑 $name: stopped" || echo "ℹ️  $name: not running"
    rm -f "$pidfile"
  fi
}

stop_pid "Bot"      "/tmp/jarvis-bot.pid"      "bot/app.py"
stop_pid "Injector" "/tmp/jarvis-injector.pid" "injector.sh"
