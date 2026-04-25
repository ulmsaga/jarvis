#!/bin/bash
# queue에 대기 중인 작업을 Claude Code 세션에 주입
# UserPromptSubmit hook으로 실행됨

QUEUE="/Users/sclee1115/Project/Dev/jarvis/bridge/queue"
PROCESSING="/Users/sclee1115/Project/Dev/jarvis/bridge/processing"

mkdir -p "$PROCESSING"

found=0
for f in "$QUEUE"/*.json; do
    [ -f "$f" ] || continue
    fname=$(basename "$f")
    mv "$f" "$PROCESSING/$fname"
    found=1
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔔 JARVIS QUEUE 작업 감지"
    echo "파일: $fname"
    echo "내용:"
    cat "$PROCESSING/$fname"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "[JARVIS] 위 Slack 요청을 처리해주세요. 처리 완료 후 결과를 Slack으로 전송하세요."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
done
