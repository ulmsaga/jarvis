# Jarvis Skills

## code-review
대상: GitHub PR URL
동작: PR의 변경된 파일을 분석하여 코드 품질, 버그, 보안 이슈를 리뷰하고 Slack 스레드에 코멘트를 작성한다.
엔진: Claude Code (Anthropic)

## safe-security-fix
대상: Python/JavaScript 코드 파일 경로 또는 GitHub 레포
동작: 보안 취약점(SQL Injection, XSS, 하드코딩 비밀번호 등)을 탐지하고 수정 제안을 생성한다.
엔진: Claude Code (Anthropic)

## generate-docs
대상: 함수/클래스/모듈 또는 레포 경로
동작: 함수별 docstring, README.md, API 문서를 자동 생성한다.
엔진: Claude Code (Anthropic)

## help
동작: 사용 가능한 모든 스킬 목록과 사용법을 Slack에 출력한다.
