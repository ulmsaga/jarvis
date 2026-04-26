# SKILL.md — JARVIS 공통 스킬 정의

> 프로젝트별 스킬은 projects/<project>/SKILL.md 에 별도 정의

---

## 📁 프로젝트 관리

### new-project
새 프로젝트 생성
```
입력: 프로젝트명, (선택) git repo URL
동작:
  1. projects/<name>/ 폴더 생성
  2. git init 또는 clone
  3. 기본 구조 생성 (README.md)
  4. GitHub repo 생성 (gh repo create)
  5. Slack 보고: 생성 완료 + repo 링크
```

### clone-project
기존 repo를 projects/에 clone
```
입력: repo URL 또는 repo 이름 (ulmsaga/<name>)
동작:
  1. projects/ 하위에 clone
  2. 구조 파악 후 Slack 보고
```

---

## 🔒 보안

### safe-security-fix
보안 취약점 탐지 및 수정
```
동작:
  1. 전체 코드 스캔 (하드코딩 키, SQL Injection, XSS, CSRF, eval/exec)
  2. 발견된 취약점 실제 수정
  3. git commit + PR 생성
  4. 완료 보고: "N applied · M skipped"
```

### security-scan
프로젝트 보안 전체 점검 (보고만, 수정 없음)
```
동작:
  1. 하드코딩된 시크릿 스캔 (token, password, secret, API key 패턴)
  2. .gitignore 검사 (.env, *.log, build 산출물 누락 여부)
  3. git 트래킹 중인 민감 파일 확인
  4. git history 전체 토큰/키 패턴 검색
  5. public repo 여부 확인
  6. Slack 보고: 심각도별 (🔴 critical / 🟡 warning / 🟢 ok)
  7. 수정 필요 시 safe-security-fix 또는 git history 재작성 제안
```

---

## 📝 문서화

### generate-docs
코드 문서 자동 생성
```
동작:
  1. 함수/클래스 Google 스타일 docstring 추가
  2. README.md 업데이트
  3. git commit + PR 생성
```

---

## 🔍 코드 리뷰

### code-review
코드 품질 분석 및 개선 제안
```
입력: (선택) PR URL
동작:
  1. 코드 품질 · 가독성 분석
  2. 버그 및 보안 이슈 탐지
  3. 구체적 개선 제안 (파일명:줄번호)
  4. GitHub PR comment 또는 Slack 보고
```

---

## 🐳 인프라

### docker-setup
Docker 환경 구성
```
입력: 서비스 종류 (mysql, redis, postgres 등)
동작:
  1. docker-compose.yml 생성
  2. 컨테이너 실행
  3. 초기 데이터 설정
  4. 연결 확인 후 Slack 보고
```

---

## 📊 보고

### status
현재 작업 상태 보고
```
동작:
  1. 실행 중인 작업 확인
  2. 최근 완료된 작업 요약
  3. Slack으로 상태 전송
```
