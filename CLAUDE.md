# JARVIS — Claude Code 실행 지침

## 세션 시작 시 자동 실행

```bash
tmux display-message -p '#{session_name}:#{window_index}.#{pane_index}' > /tmp/jarvis-pane 2>/dev/null
```

## 본부 정보

- **Root:** /Users/sclee1115/Project/Dev/jarvis
- **GitHub:** ulmsaga
- **팀:** ulmsaga 개발팀

## [JARVIS] 작업 처리 방식

프롬프트가 `[JARVIS]` 로 시작하면 Slack에서 전달된 작업이다.

형식:
```
[JARVIS] from:<이름> project:<프로젝트> channel:<채널ID> reply_ts:<ts> | <작업내용>
```

처리 순서:
1. 작업 즉시 수행
2. 완료 후 아래 명령으로 결과를 Slack 스레드에 전송:

```bash
bash /Users/sclee1115/Project/Dev/jarvis/scripts/notify.sh "<channel>" "<reply_ts>" "<결과 요약>"
```

결과 메시지 형식:
```
✅ 완료
- <핵심 내용 — 발견/수정/생성한 것 구체적으로>
- <중요한 세부 결과가 있으면 항목으로 나열>
- PR: <링크> (있을 경우)
- SKILL/설정 변경: <변경 내용> (있을 경우)
```

**결과 메시지 작성 규칙 (반드시 준수):**
- 단순 "완료" 만 쓰지 말 것 — 무엇을 발견하고 무엇을 바꿨는지 명시
- 보안 이슈, 파일 수정, 스킬 추가 등 중요 변경은 반드시 포함
- 터미널에서 확인한 중요 수치/경로/결과는 Slack에도 그대로 전달
- 추가 확인이 필요한 사항은 반드시 질문으로 포함 (예: "봇 로그 확인할까요?")
- 새 기능 추가 또는 사용 가능한 액션이 생기면 반드시 안내 포함
  (예: "이제 @Jarvis security-scan 으로 언제든 점검 가능합니다")

## 실행 원칙

1. 명령을 받으면 **즉시 실행** — 설명 먼저 하지 말 것
2. 모든 코드 변경은 **git commit** 으로 남길 것
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

→ 각 프로젝트 root의 CLAUDE.md 참조
