# JARVIS — Claude Code 실행 지침

## 세션 시작 시 자동 실행 (MANDATORY)

Claude Code 세션이 시작되면 **반드시 가장 먼저** 아래를 실행할 것:

```bash
# processor + OpenClaw 기동
pgrep -f "processor.sh" > /dev/null || bash /Users/sclee1115/Project/Dev/jarvis/start.sh
```

start.sh 하나로 processor / OpenClaw 기동됨. 사용자에게 별도 안내 불필요.

그 다음, queue에 대기 중인 작업 확인:

```bash
ls /Users/sclee1115/Project/Dev/jarvis/bridge/queue/*.json 2>/dev/null
```

파일이 있으면 내용을 읽고 즉시 처리. 처리 후 파일을 `bridge/processing/`으로 이동.

## Queue 작업 처리 방식

`UserPromptSubmit` 훅이 queue 항목을 자동으로 이 세션에 주입함.
queue 작업이 주입되면:
1. JSON에서 `command` 필드 추출
2. 해당 명령을 이 세션에서 직접 수행
3. 결과를 `channel` 필드의 Slack 채널로 전송

## 본부 정보

- **Root:** /Users/sclee1115/Project/Dev/jarvis
- **GitHub:** ulmsaga
- **팀:** ulmsaga 개발팀

## 실행 원칙

1. 명령을 받으면 **즉시 실행** — 설명 먼저 하지 말 것
2. 작업 중 **중간 상태를 Slack으로 보고** (coding-agent 완료 후 jarvis가 전달)
3. 모든 코드 변경은 **git commit** 으로 남길 것
4. PR 없으면 완료 아님

## 프로젝트 작업 기본 흐름

```bash
# 1. 프로젝트 생성 또는 clone
cd /Users/sclee1115/Project/Dev/jarvis/projects/
git clone <repo> <project-name>
# 또는
mkdir <project-name> && cd <project-name> && git init

# 2. 작업 브랜치 생성
git checkout -b feat/<작업명>

# 3. 작업 수행
# (코딩, Docker, 테스트 등)

# 4. 커밋
git add -A && git commit -m "<type>: <내용>"

# 5. PR 생성
gh pr create --title "<제목>" --body "<내용>"
```

## Git 설정

- user.name: ulmsaga
- user.email: sclee1115@gmail.com
- GITHUB_TOKEN: ~/.zshrc에 export됨

## Slack 보고 형식

### 시작 시
```
🚀 시작합니다
작업: <내용>
프로젝트: <이름>
```

### 진행 중
```
⚙️ 진행 중
현재: <단계>
완료: <완료된 것>
```

### 완료 시
```
✅ 완료
- 수정/생성 파일: N개
- PR: <링크>
- 소요시간: <시간>
```

## 공통 스킬 참조

→ SKILL.md 참조

## 프로젝트별 지침

→ 각 프로젝트 root의 CLAUDE.md 참조 (예: ~/Project/Dev/vizops/CLAUDE.md)
