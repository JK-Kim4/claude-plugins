# 카탈로그 스키마

파일 셋, 모두 JSON. `catalog.py validate`가 이 규칙을 검사한다.

## catalog.json

```json
{
  "schema": 1,
  "version": "1.0.0",
  "released": "2026-11-07",
  "researched_through": "2026-11-07",
  "categories": [
    {"id": "credential-key", "name": "자격증명·키 관리", "description": "한 줄"}
  ]
}
```

- `researched_through`: 조사가 덮은 마지막 날짜. 다음 조사는 그다음 날부터.

## incidents.json — 사건

```json
{
  "id": "2025-11-coupang-signing-key",
  "date": "2025-11",
  "region": "KR",
  "org": "쿠팡",
  "sector": "커머스",
  "impact": "고객 계정 약 3,370만 건 정보 노출",
  "summary": "두세 문장",
  "attack_vector": "한 문장",
  "root_causes": ["퇴사자가 보유한 인증 서명키를 폐기·교체하지 않음"],
  "cves": [],
  "categories": ["credential-key", "detection-response"],
  "ai_involvement": {"level": "none-reported", "basis": "공식 발표에 언급 없음"},
  "sources": [{"title": "…", "url": "https://…"}],
  "confidence": "high",
  "added_in": "1.0.0"
}
```

- `id`: `YYYY-MM-<영문-slug>`. 바꾸지 않는다.
- `date`: 발생일을 모르면 공개일. `YYYY-MM` 또는 `YYYY-MM-DD`.
- `region`: `KR` | `global`.
- 선택: `cves`, `updated_in`.

## checks.json — 점검 항목

```json
{
  "id": "credential-key/signing-key-lifecycle",
  "category": "credential-key",
  "title": "토큰 서명키의 수명·폐기 관리",
  "severity": "critical",
  "method": "code",
  "applies_to": ["web"],
  "why": "한 문장. 어떤 사고가 이 경로로 났는가",
  "how_to_check": ["구체 단계 1", "구체 단계 2"],
  "signals": {
    "files": ["**/*jwt*"],
    "patterns": ["(?i)jwt[_-]?secret", "HS256"],
    "pattern_files": ["*.ts", "*.js", "*.py", "*.env*"]
  },
  "pass_criteria": "무엇이 보이면 통과인가",
  "remediation": "무엇을 하면 막히는가",
  "incidents": ["2025-11-coupang-signing-key"],
  "added_in": "1.0.0",
  "status": "active"
}
```

- `id`: `<category>/<영문-slug>`. **바꾸거나 지우면 major.**
- `severity`: critical | high | medium | low. 근거 사건의 피해 규모가 아니라 **이 약점이 열려 있을 때 일반적 위험**.
- `method`: `code`(소스) | `config`(설정·IaC·CI) | `infra`(저장소 밖 운영 확인이 주) | `process`(조직 절차).
- `applies_to`: profile 태그. 모든 시스템이면 `["any"]`. 태그 목록은 `catalog.py`의 `PROFILE_FILES`·`PROFILE_DEPS`.
- `signals`(선택): `scan`이 후보를 찾는 데 쓴다. `files`는 glob, `patterns`는 Python 정규식, `pattern_files`는 패턴을 적용할 파일 glob(없으면 전체).
- 선택: `updated_in`, `deprecated_reason`(status가 deprecated일 때 필수).

## 좋은 점검 항목

1. **사건과 이어진다.** `incidents`가 비면 경고. "있으면 좋은 보안 습관"은 카탈로그 대상이 아니다.
2. **저장소에서 확인 가능한 단계로 쓴다.** ❌ "키 관리가 안전한지 확인" ✅ "JWT 서명 키가 어디서 로드되는지 찾는다 → `kid` 헤더와 키 목록(JWKS 등)으로 여러 키를 동시에 받는지 본다 → 키 교체 절차·주기가 코드나 런북에 있는지 본다".
3. **통과 기준이 관찰 가능하다.** 에이전트가 PASS/FAIL을 근거 인용으로 가를 수 있어야 한다.
4. **신호는 넓게, 판정은 좁게.** `signals`는 놓치지 않게 넓게 잡고, 오탐은 판정 단계에서 거른다.
5. **조직 절차 항목도 질문으로 쓴다.** `method: process`면 `how_to_check`에 사람에게 물을 질문을 쓴다.
