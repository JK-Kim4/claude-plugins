#!/bin/bash
# eval 러너의 cwd 에 픽스처를 만든다. 형식은 dlc.py 가 쓰는 state.md/log.md 와 같다.
set -e
rm -rf docs
W=docs/dlc/260913-inventory-lookup
mkdir -p "$W"
printf '260913-inventory-lookup\n' > docs/dlc/active
cat > "$W/state.md" <<'EOF'
# DLC State

<!-- dlc.py 가 관리한다. 손으로 고치지 말고 start/approve/skip 을 쓴다. -->

- profile: express
- depth: minimal
- description: 창고 관리자가 SKU 로 현재 재고 수량을 조회하는 사내 API
- created: 2026-09-13T02:10:00Z
- workspace: greenfield
- languages: -
- build: -
- fingerprint: da39a3ee5e6b

## Stages

| stage | status | updated | note |
|---|---|---|---|
| init | done | 2026-09-13T02:10:00Z |  |
| analyze | skipped | 2026-09-13T02:10:00Z | greenfield |
| requirements | done | 2026-09-13T02:10:00Z |  |
| plan | pending | 2026-09-13T02:10:00Z |  |
| build | pending | 2026-09-13T02:10:00Z |  |
| verify | pending | 2026-09-13T02:10:00Z |  |
EOF
cat > "$W/log.md" <<'EOF'
# DLC Log

- 2026-09-13T02:10:00Z | init | created | profile=express workspace=greenfield
- 2026-09-13T02:20:00Z | requirements | start | 
- 2026-09-13T02:40:00Z | requirements | approve | 사전 승인(fixture)
EOF
cat > "$W/requirements.md" <<'EOF'
# 요구사항

## 의도 요약
창고 관리자가 사내 관리 화면에서 SKU 로 현재 재고 수량을 조회하는 읽기 전용 API 를 만든다. [desc]

## 기능 요구사항

### FR1. SKU 단위 재고 조회 [Q1]
- FR1.1 SKU 하나의 현재 총수량을 돌려준다. [Q1]
- FR1.2 창고별 수량 목록을 함께 돌려준다. 창고가 0개면 총수량 0 과 빈 목록. [Q2]
- 수용 기준: 존재하는 SKU 는 200 과 수량, 없는 SKU 는 404. [Q4]

### FR2. 사내 SSO 토큰 인증 [Q3]
- FR2.1 유효한 SSO 토큰이 없는 요청은 401. [Q3]
- 수용 기준: 토큰 없는 요청이 401 을 받는 테스트 1건. [Q3]

## 비기능 요구사항

### NFR1. 응답 시간 [Q4]
- 조회 API p95 300ms 이하. 측정: 부하 테스트 100 rps. [Q4]

## 제약
| 항목 | 내용 | 출처 |
|---|---|---|
| 데이터베이스 | 기존 PostgreSQL 의 inventory 테이블을 읽기 전용으로 조회한다 | [Q3] |

## 범위 밖
- 입출고 등록. [Q1]

## 가정과 열린 질문
- 창고 수는 최대 20개로 가정한다. [assumption]
EOF
cat > "$W/requirements-questions.md" <<'EOF'
# 요구사항 질문

## Q1. 이 API 가 하는 일은 무엇입니까?
A. SKU 하나의 총수량 조회
B. 총수량과 창고별 수량 조회
X. Other (please specify)

[Answer]: B

## Q2. 창고가 0개인 SKU 는 어떻게 응답합니까?
A. 404
B. 200 과 총수량 0, 빈 목록
X. Other (please specify)

[Answer]: B

## Q3. 어느 데이터와 인증에 붙습니까?
A. 기존 PostgreSQL inventory 읽기 전용, 사내 SSO 토큰
X. Other (please specify)

[Answer]: A

## Q4. 무엇이 되면 완료입니까?
A. 200·404 통합 테스트 2건, p95 300ms 이하(100 rps)
X. Other (please specify)

[Answer]: A

## Consolidated Summary Confirmation
- SKU 조회 API, 총수량 + 창고별 수량, 0개면 200/0/빈 목록
- PostgreSQL 읽기 전용, SSO 토큰
- 완료: 통합 테스트 2건, p95 300ms

- Looks correct
- Request changes

[Answer]: Looks correct
EOF
