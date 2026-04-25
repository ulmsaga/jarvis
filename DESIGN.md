# JARVIS 설계 문서

## 1. 시스템 개요

Slack으로 작업을 전달하면 Claude Code 세션이 자동으로 수행하고, 결과를 Slack으로 돌려주는 자동화 시스템.

```
[Slack 사용자]
    │  @jarvis 메시지
    ▼
[Slack Bot]  ────────────────────────────────────────────────────────────
    │  "작업 중입니다. 잠시만 기다려 주세요." 즉시 응답
    │  task JSON 저장
    ▼
[bridge/queue/task-{ts}.json]
    │
    ▼
[injector.sh]  (queue 감시 루프)
    │  pane 상태 확인 후 tmux send-keys 주입
    ▼
[Claude Code 세션]  (터미널에서 thinking... 표시)
    │  작업 수행
    ▼
[scripts/notify.sh]
    │  결과 전송
    ▼
[Slack 결과 메시지]
```

---

## 2. 컴포넌트

### 2-1. Slack Bot (`bot/app.py`)

- **역할:** Slack 이벤트 수신 → 파싱 → queue 저장 → 즉시 응답
- **방식:** Slack Bolt (Socket Mode) — 외부 포트/ngrok 불필요
- **수신 조건:** `@jarvis` 멘션 또는 지정 채널 메시지
- **파싱 항목:**

  | 필드 | 설명 | 추출 방법 |
  |------|------|-----------|
  | `from` | 보낸 사람 | Slack user_id → display name |
  | `channel` | 채널 ID | 이벤트에서 직접 |
  | `project` | 프로젝트명 | `#project-name` 태그 또는 첫 번째 단어 |
  | `command` | 작업 내용 | 멘션/태그 제거 후 나머지 텍스트 |
  | `ts` | 타임스탬프 | 파일명 및 스레드 reply용 |

- **Slack 즉시 응답:** 스레드 reply로 `"작업 중입니다. 잠시만 기다려 주세요."`
- **저장 형식:** `bridge/queue/task-{ts}.json`

```json
{
  "ts": "1777200000000",
  "from": "sclee",
  "channel": "C12345678",
  "project": "vizops",
  "command": "메인 페이지 로딩 속도 개선해줘",
  "reply_ts": "1777200000.001"
}
```

---

### 2-2. Queue Injector (`bridge/injector.sh`)

- **역할:** queue 디렉토리 감시 → Claude Code 세션에 프롬프트 주입
- **실행 방식:** 백그라운드 루프 (`while true; sleep 1`)
- **주입 대상:** `/tmp/jarvis-pane` 에 저장된 tmux pane ID

**신뢰성 확보 로직:**
1. `/tmp/jarvis-pane` 존재 여부 확인
2. 해당 pane이 실제로 살아있는지 `tmux list-panes` 로 검증
3. pane의 현재 출력 끝이 Claude Code 프롬프트(`>`) 상태인지 확인
4. 텍스트 send-keys → 300ms 대기 → Enter send-keys (2단계 분리)
5. 주입 후 파일을 `bridge/processing/` 으로 이동

**주입 프롬프트 형식:**
```
[JARVIS] from:sclee project:vizops | 메인 페이지 로딩 속도 개선해줘
```

---

### 2-3. Claude Code 세션

- **역할:** 주입된 프롬프트를 받아 실제 작업 수행
- **실행 위치:** 터미널에서 직접 `claude` 실행 (tmux 불필요, 선택 사항)
- **pane 등록:** Claude Code 시작 시 수동 또는 별도 스크립트로 `/tmp/jarvis-pane` 등록
- **작업 완료 후:** `scripts/notify.sh` 를 호출하여 Slack에 결과 전송

---

### 2-4. Slack Notifier (`scripts/notify.sh`)

- **역할:** 작업 결과를 Slack 스레드에 reply
- **호출:** Claude Code가 작업 완료 시 직접 실행
- **인자:** `channel`, `reply_ts`, `message`

```bash
bash scripts/notify.sh "C12345678" "1777200000.001" "✅ 완료\n- PR: https://..."
```

---

### 2-5. 시작 스크립트 (`start.sh`)

- Slack Bot 백그라운드 실행
- Queue Injector 백그라운드 실행
- PID 저장 (`/tmp/jarvis-bot.pid`, `/tmp/jarvis-injector.pid`)

### 2-6. 종료 스크립트 (`stop.sh`)

- 저장된 PID로 Bot + Injector 종료

---

## 3. 파일 구조

```
jarvis/
├── bot/
│   └── app.py                  # Slack Bot (Bolt, Socket Mode)
├── bridge/
│   ├── queue/                  # 대기 중인 작업 JSON
│   ├── processing/             # 처리 중인 작업 JSON
│   ├── done/                   # 완료된 작업 JSON
│   └── injector.sh             # queue → tmux 주입 루프
├── scripts/
│   └── notify.sh               # Slack 결과 전송
├── .env                        # SLACK_BOT_TOKEN, SLACK_APP_TOKEN
├── start.sh                    # bot + injector 시작
├── stop.sh                     # 전체 종료
├── status.sh                   # 실행 상태 확인
├── CLAUDE.md                   # Claude Code 지침
└── DESIGN.md                   # 이 문서
```

---

## 4. 환경 변수 (`.env`)

| 변수 | 설명 |
|------|------|
| `SLACK_BOT_TOKEN` | `xoxb-...` (Bot Token) |
| `SLACK_APP_TOKEN` | `xapp-...` (Socket Mode용 App Token) |

> **참고:** Socket Mode를 사용하므로 `SLACK_APP_TOKEN` 추가 발급 필요.  
> Slack App 설정 → Socket Mode 활성화 → App-Level Token 생성 (`connections:write` scope)

---

## 5. 데이터 흐름 상세

```
① Slack 메시지 수신
   bot/app.py → Slack API로 "작업 중입니다. 잠시만 기다려 주세요." 스레드 reply

② JSON 파일 생성
   bridge/queue/task-{ts}.json

③ injector.sh 감지 (1초 폴링)
   pane 상태 확인 → 프롬프트 대기 중이면 주입
   → bridge/processing/task-{ts}.json 으로 이동

④ Claude Code 작업 수행
   터미널에 thinking... 표시되며 진행

⑤ 완료 후 notify.sh 호출
   Slack 스레드에 결과 reply
   → bridge/done/task-{ts}.json 으로 이동
```

---

## 6. 구현 순서

| 단계 | 작업 | 비고 |
|------|------|------|
| 1 | `.env` 정비 — `SLACK_APP_TOKEN` 추가 | Slack 콘솔에서 발급 |
| 2 | `scripts/notify.sh` 구현 | 가장 단순, 먼저 검증 |
| 3 | `bot/app.py` 구현 | Socket Mode + queue 저장 |
| 4 | `bridge/injector.sh` 구현 | pane 상태 체크 포함 |
| 5 | `start.sh` / `stop.sh` 정비 | bot + injector 관리 |
| 6 | 통합 테스트 | Slack → 터미널 → Slack |

---

## 7. 선결 조건

- [ ] Slack App에 **Socket Mode** 활성화
- [ ] `SLACK_APP_TOKEN` (`xapp-...`) 발급 및 `.env` 추가
- [ ] Slack Bot이 대상 채널에 초대되어 있는지 확인
- [ ] Claude Code를 실행한 터미널에서 `/tmp/jarvis-pane` 등록 방법 결정
      → 옵션 A: `start.sh` 에 pane 등록 명령 포함
      → 옵션 B: Claude Code 시작 후 별도 명령으로 수동 등록
