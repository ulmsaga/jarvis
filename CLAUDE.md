# JARVIS — Claude Code 실행 지침

## 세션 시작 시 자동 실행 (MANDATORY)

Claude Code 세션이 시작되면 **반드시 가장 먼저** 아래를 실행할 것:

```bash
pgrep -f "processor.sh" > /dev/null || bash /Users/sclee1115/Project/Dev/jarvis/start.sh
```

processor가 이미 실행 중이면 스킵, 아니면 자동 시작. 사용자에게 별도 안내 불필요.

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
