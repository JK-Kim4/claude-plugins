---
name: breach-update
description: breach-watch 카탈로그(최근 해킹 사고 → 점검 항목)를 갱신한다. 마지막 조사일 이후 국내·해외에서 새로 공개된 침해 사고와 AI가 관여한 공격 사례를 웹에서 조사하고, 근본 원인별로 분류해 사건을 추가하고, 기존 점검 항목에 근거를 잇거나 새 항목을 만든 뒤, 카탈로그 버전을 올리고 변경 이력을 남긴다. 사용자가 "해킹 사례 카탈로그 업데이트", "최근 보안 사고 추가 조사해줘", "점검 목록 갱신", "breach-watch 갱신", "새로 터진 해킹 반영해줘", "이번 달 침해 사고 정리해서 점검 항목 추가" 등을 말할 때 사용한다. 카탈로그로 프로젝트를 점검하는 일은 breach-audit이 맡는다.
---

# breach-update — 사고 조사와 카탈로그 갱신

카탈로그는 **사건 → 근본 원인 → 점검 항목**의 사슬이다. 이 스킬은 사슬을 늘리고, 그때마다 버전을 올려 "어느 점검이 어느 버전에 들어왔는지"를 남긴다. breach-audit은 이 버전으로 증분 점검을 한다.

## 파일

| 파일 | 쓰는 때 |
|---|---|
| `<skills>/breach-audit/scripts/catalog.py` | 위치 확인·검사·버전 올리기·목록 생성. `<skills>`는 이 스킬 폴더의 부모 |
| `<skills>/breach-audit/catalog/*.json` | 번들 카탈로그(정본 스키마는 `references/schema.md`) |
| `references/sources.md` | 조사할 곳과 검색어 |
| `references/criteria.md` | 사건 채택 기준, AI 관여 판정, 분류 규칙 |
| `references/schema.md` | 사건·점검 항목 필드와 좋은 점검 항목 쓰는 법 |

## 버전 규칙 (semver)

| 올림 | 언제 | 점검 보고서와의 관계 |
|---|---|---|
| **major** | 점검 항목 id를 바꾸거나 지움, 카테고리 id를 바꾸거나 지움, 판정 기준을 뒤집음 | 이전 보고서와 항목 비교가 안 된다 → 다음 점검은 전체 |
| **minor** | 사건 추가, 점검 항목 추가, 카테고리 추가, 기존 항목의 확인 방법·통과 기준 강화 | 증분 점검이 `--since`로 바뀐 항목만 본다 |
| **patch** | 오탈자, 출처 보강, `signals` 정규식 개선처럼 판정에 영향 없는 수정 | 다시 점검할 것 없음 |

- 항목을 지우지 않는다. 쓸모없어진 항목은 `status: deprecated` + `deprecated_reason`(minor).
- 새로 넣거나 기준을 바꾼 항목에는 `added_in: "next"` 또는 `updated_in: "next"`를 쓴다. 버전 숫자를 손으로 적지 않는다. `bump`가 바꾼다.

## 절차

### 1. 어디에 쓸지 정하기

```bash
python3 <skills>/breach-audit/scripts/catalog.py where
```

| mode | 뜻 | 할 일 |
|---|---|---|
| `source` | 플러그인 원본 저장소 안 | 번들 카탈로그를 바로 고친다. 끝나면 `plugin.json` 버전도 올린다(아래 7) |
| `local` / `env` | 사용자 카탈로그 | 그대로 고친다. 끝나면 그 폴더에서 git commit |
| `bundled-readonly` | 설치본 | 고치지 않는다. `init-local`로 `~/.claude/breach-watch/catalog`를 만들고 거기서 진행한다고 알린다 |

`where`가 "번들이 더 최근"이라고 하면 먼저 `sync`로 병합할지 묻는다.

### 2. 조사 범위

- 기간: 카탈로그 `researched_through` 다음 날 ~ 오늘. 사용자가 기간·분야를 지정하면 따른다.
- 기존 사건 id와 조직 목록을 먼저 뽑아 둔다(중복 방지): `python3 -c "import json;[print(i['id'],i['org']) for i in json.load(open('<catalog>/incidents.json'))]"`
- `CHANGELOG.md` 최신 항목의 **보류** 목록을 조사 대상에 넣는다. 원인이 새로 공개됐으면 채택하고, 여전히 미달이면 이번 CHANGELOG의 보류로 옮긴다.

### 3. 조사 (병렬)

`references/sources.md`의 세 갈래를 서브에이전트 셋에 나눠 맡긴다. 각 브리프에 **기간, 기존 사건 목록(중복 제외용), `references/criteria.md` 채택 기준, 아래 출력 형식**을 넣는다. WebSearch는 standard로 시작하고 최근 1~2개월 사건은 extended를 쓰게 한다.

1. 국내 — 금융·통신·커머스·플랫폼·공공·가상자산. 과기정통부·개보위 조사 결과 우선.
2. 해외 — 벤더·CISA·위협 인텔리전스 1차 분석 우선.
3. AI 관여 — 공격자의 AI 사용, AI 개발 도구·에이전트 공급망, AI 앱 취약점.

출력 형식: 사건마다 `id, date, region, org, sector, impact, attack_vector, root_causes[], cves[], ai_involvement{level, basis}, sources[{title,url}], confidence`. 그리고 **기존 사건의 새 사실**(예: 정부 최종 조사 결과 발표)도 따로 보고하게 한다.

### 4. 거르기

`references/criteria.md`로 각 후보를 채택·보류·제외한다. 서브에이전트의 요약을 그대로 믿지 않는다. 채택 후보 중 critical 근거가 될 사건은 출처 하나를 직접 열어 근본 원인 서술을 확인한다.

### 5. 분류와 점검 항목 잇기

사건마다:

1. `categories`를 고른다(여럿 가능). 맞는 카테고리가 없을 때만 새 카테고리를 제안하고 사용자 확인 후 추가한다.
2. 근본 원인마다 기존 점검 항목이 막을 수 있는지 본다(`list-checks --category X`).
   - **막는다** → 그 항목의 `incidents`에 id를 더한다. 확인 방법이 이 사고 경로를 못 잡으면 `how_to_check`를 보강하고 `updated_in: "next"`.
   - **못 막는다** → 새 항목을 쓴다. `references/schema.md`의 '좋은 점검 항목' 기준을 지킨다.
3. 기존 사건의 새 사실은 해당 사건을 고치고 `updated_in: "next"`.

### 6. 검사와 릴리스

```bash
python3 <skills>/breach-audit/scripts/catalog.py validate      # ERROR 0 이어야 한다
python3 <skills>/breach-audit/scripts/catalog.py bump minor \
  --note "2026-12 정기 조사: 국내 n건, 해외 n건, AI n건" \
  --researched-through YYYY-MM-DD
python3 <skills>/breach-audit/scripts/catalog.py stats
```

`bump`가 `next`를 새 버전으로 바꾸고, `CHANGELOG.md` 맨 위에 항목을 넣고, `CHECKLIST.md`를 다시 만든다. CHANGELOG의 자동 줄 아래에 **이번 조사에서 보인 경향 2~3줄**(예: "SaaS OAuth 토큰 경유 유출이 3건 더 나옴")을 사람이 읽게 덧붙인다.

### 7. 저장

- `local`: 카탈로그 폴더에서 `git add -A && git commit -m "catalog X.Y.Z: <요약>"` 후 `git tag catalog-vX.Y.Z`. 이 폴더는 사용자 개인 것이라 묻지 않고 커밋해도 된다.
- `source`: `breach-watch/.claude-plugin/plugin.json`의 version을 patch 올리고(카탈로그 major면 minor), 루트 README 표의 버전도 맞춘다. 커밋·푸시·PR은 사용자에게 묻고 한다. 카탈로그 갱신은 데이터 변경이라 `archive/` 보관 대상이 아니다.

### 8. 보고

대화에는 새 버전, 추가된 사건·점검 수, **새로 생긴 critical·high 점검 항목 이름**만 쓴다. 그리고 "breach-audit 증분 점검으로 이 항목들만 다시 볼 수 있다"고 한 줄 안내한다.

## 정기 갱신

사용자가 원하면 `/schedule`로 매월 1회 이 스킬을 돌리는 루틴을 제안한다. 루틴은 `local` 모드에서 커밋까지 하고, `source` 모드에서는 브랜치와 PR 초안까지만 만든다. 사용자가 요청하기 전에는 만들지 않는다.
