#!/bin/bash
# Jarvis 실행 — tmux jarvis 세션 생성/접속 후 start.sh 자동 실행

tmux new-session -A -s jarvis "bash ~/Project/Dev/jarvis/start.sh; exec zsh"
