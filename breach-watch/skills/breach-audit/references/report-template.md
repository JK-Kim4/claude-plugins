# 점검 보고서 형식

`docs/security/breach-audit/YYYY-MM-DD.md`. 같은 날 두 번이면 `YYYY-MM-DD-2.md`.

맨 위 메타 블록은 다음 증분 점검이 기계적으로 읽는다. 키 이름을 바꾸지 않는다.

```markdown
<!-- breach-audit
catalog_version: 1.0.0
catalog_researched_through: 2026-11-07
mode: full            # full | incremental
since: -              # incremental 이면 이전 catalog_version
tags: node,web,github-actions,aws,llm-app
audited_at: 2026-11-07
previous: -           # 이전 보고서 파일명
-->

# 사고 기반 취약점 점검 — {프로젝트명}

{한 문장 결론. 예: "critical 2건(서명키 장기 사용, Firestore 공개 규칙)이 실제 사고와 같은 경로로 열려 있다."}

## 요약

| 판정 | critical | high | medium | low |
|---|---|---|---|---|
| FAIL | | | | |
| PARTIAL | | | | |
| MANUAL | | | | |
| PASS | | | | |
| N/A | | | | |

## 열린 지적

다음 점검이 재확인할 목록. FAIL·PARTIAL만, 심각도 순.

### [critical] `credential-key/signing-key-lifecycle` — FAIL

- **사고 경로**: 쿠팡(2025-11) — 퇴사자가 보유한 서명키로 인증 토큰을 위조.
- **근거**: `src/auth/jwt.ts:12` HS256 대칭키를 환경변수 하나로 사용, 로테이션·kid 없음.
- **조치**: {카탈로그 remediation을 이 코드에 맞게 구체화}
- **심각도 조정**: 없음 / {이유}

## 확인이 필요한 질문 (MANUAL)

1. `social-engineering-identity/helpdesk-reset-verification` — {구체적 질문}

## 통과 (PASS)

| 항목 | 근거 |
|---|---|

## 해당 없음 (N/A)

| 항목 | 이유 |
|---|---|

## 카탈로그 밖 관찰

카탈로그 항목은 아니지만 점검 중 본 위험. breach-update 때 새 항목 후보.

## 이전 점검 대비

증분 점검일 때만. 이전 열린 지적 중 해소된 것 / 그대로인 것 / 악화된 것.

## 점검 범위와 한계

- 읽은 범위(루트, 제외한 디렉터리), 돌린 도구, 돌리지 않은 도구와 이유.
- 저장소 밖(운영 설정, 클라우드 콘솔, 조직 절차)은 MANUAL로만 다뤘다.
```
