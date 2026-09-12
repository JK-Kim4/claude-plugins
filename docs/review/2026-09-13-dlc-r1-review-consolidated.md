# dlc 1라운드 리뷰 통합 분석 (2026-09-13)

이슈 #1의 1·2단계 산출물이다. Fable 리뷰(`2026-09-13-dlc-r1-review-fable.md`, F1~F15)와 Codex 리뷰(`2026-09-13-dlc-r1-review-codex.md`, C1~C10 + 경계 1건 + 문서 정정 1건)를 대조하고, 모든 지적을 오케스트레이터가 커밋 `5b5aa7e` 작업 트리에서 직접 재현한 뒤 수용·기각을 정했다.

- 재현 방법: `dlc.py`를 import해 CLI를 호출하는 스크립트로 26개 시나리오 실행. `npx skills` 1.5.26으로 로컬 설치 2회. Python 3.9.6 / 3.12.13 / 3.14.6으로 `--help`와 unittest 실행.
- 재현 결과: 두 리뷰의 지적 **전부 재현됨**. 기각 0건. 리뷰가 놓친 결함 2건 추가(M1, M2).
- 두 리뷰가 상충하는 지적: **없음**. 같은 결함을 다르게 본 지점만 있고 아래 통합표에 적었다.

## 1. 지적 통합표

심각도는 두 리뷰 중 높은 쪽을 따르되, 재현 결과로 조정한 곳은 비고에 적었다.

| 통합# | 한 줄 요약 | 출처 | 심각도 | 두 리뷰가 다르게 본 지점 / 재현 결과 |
|---|---|---|---|---|
| U1 | approve가 스테이지 순서를 강제하지 않는다. pending이면 `next`와 무관하게 승인된다 | F1, C6 | P1 | Fable은 설계 §6 "라우팅 판단을 코드에" 위반으로, Codex는 "이후 requirements를 확정해도 승인된 plan을 다시 보지 않는다"는 흐름 결함으로 봤다. 같은 원인이다. 재현: express에서 requirements pending인 채 `approve plan` → exit 0, `plan: done` |
| U2 | 유닛 표 파싱이 units.md의 모든 4열 표를 유닛으로 읽는다 | F2 | P1 | Codex 미지적. 재현: `## 계약` 절의 endpoint 표가 있으면 유닛이 `['u1-api', 'endpoint', 'get-stock']` |
| U3 | 라우터 안내 모드가 active 커서 없음을 "작업 없음"으로 단정 → 다른 PC 재개 불가 | F3 | P1 | Codex 미지적. 문서 결함이라 코드 재현 대상 아님. SKILL.md:40 확인 |
| U4 | 전역 `--root`가 서브파서 기본값 `.`에 덮여 무시된다 | C1 | P1 | Fable 미지적. 재현: 다른 cwd에서 `dlc.py --root <t> init ...` → exit 0, `<t>`에 docs 없음, cwd에 생성 |
| U5 | express/bugfix는 design이 없는데 build 검사가 units.md를 요구한다 | C2 | P1 | Fable 미지적. 코드 확인: `check_stage("build")`가 프로파일 무관하게 `units_table` 비면 실패. **설계 결정 필요(3절)** |
| U6 | FR/NFR 정의 집합을 requirements.md 전문에서 뽑아 `범위 밖`·가정 절의 언급까지 센다 | F4 | P2 | Codex 미지적. 재현: `범위 밖`에 "FR7 후보였으나 제외" → "FR3~FR6 비었습니다" 오탐. 같은 이유로 `requirement_ids`가 FR7을 정의된 ID로 취급해 design이 FR7을 참조해도 통과한다 |
| U7 | fingerprint가 파일 경로 목록만 해시한다 | F5, C3 | P2 | Fable은 문서 표현("현재 소스와 같으면")이 과하다고, Codex는 캐시 무효화 실패로 봤다. 재현: app.py 내용을 바꿔도 지문 동일 |
| U8 | 지문이 일치하면 analyze를 다시 돌릴 방법이 없다 | F6 | P2 | Codex 미지적. 재현: `next` → requirements, `start analyze` → 거부 |
| U9 | 하위 ID 참조를 검사하지 않고, build 산출물은 참조 검사 자체가 없다 | F7, C7 | P2 | Fable은 `FR1.9`(상위 존재, 하위 없음), Codex는 `FR999.1`(상위도 없음)과 build/u1.md의 `FR999`. 재현: 셋 다 `OK` |
| U10 | state.md에 profile이 없거나 값이 이상하면 traceback | F8, C9(일부) | P2 | Codex의 여러 줄 description 재현이 `KeyError: 'unknown'`으로 끝나는 것도 같은 경로. 재현: `KeyError: 'profile'` |
| U11 | skip이 done 스테이지를 skipped로 되돌린다 | F9 | P2 | Codex 미지적. 재현: 승인된 requirements에 `skip --reason undo` → skipped |
| U12 | Python 3.9에서 `str \| None` 평가로 `--help`·import부터 실패 | C4 | P2 | Fable 미지적. 재현: `/usr/bin/python3`(3.9.6) `--help` → TypeError, unittest errors=1. 3.12·3.14 OK |
| U13 | README의 `--skill 'dlc*'`가 동작하지 않는다 | C5 | P2 | Fable 미지적. 재현: skills 1.5.26 `No matching skills found for: dlc*`. `--skill dlc`는 `.agents/skills/dlc/`에 정상 복사 |
| U14 | 질문에 `[Answer]:` 행이 없으면 미답변을 못 잡는다 | C8 | P2 | Fable 미지적. 재현: Q1에 답변 행 없이 요약만 `Looks correct` → `check requirements: OK` |
| U15 | 여러 줄 description이 state.md 메타로 해석되고 둘째 줄부터 유실된다 | C9 | P2 | Fable 미지적. 재현: `"첫 줄\n- profile: unknown"` → init 성공, `next`에서 KeyError. `"첫 줄\n둘째 줄"` → status에 "첫 줄"만 |
| U16 | active 커서의 절대경로·심링크로 프로젝트 밖에 쓴다 | C10 | P2 | Fable 미지적. 재현: A의 active에 B 작업 절대경로 → A에서 `start`가 B의 state.md 변경. active를 외부 파일 심링크로 → init이 그 파일을 작업 이름으로 덮어씀 |
| U17 | 빈 skip 사유가 통과한다 | C(경계) | P2 | Fable 미지적. 재현: `--reason ""` → exit 0, `skipped ()` |
| U18 | 오류 메시지에 `None` 노출 (프로파일 밖 스테이지, 완료 후 start) | F10 | P3 | Codex 미지적. 재현: "현재 None", "지금 시작할 스테이지는 None 입니다" |
| U19 | 질문 번호 연속성 미검사, 빈 요약 답변이 두 건으로 중복 보고 | F11 | P3 | Codex 미지적. 재현: Q1·Q3만 있어도 번호 지적 없음. 빈 요약 답변이 "답변이 비어 있습니다"와 "정확히 Looks correct 여야" 두 줄로 나옴 |
| U20 | 스크립트 경로 표기가 세 가지(`<이 스킬 디렉터리>/scripts`, `<skills>/dlc/scripts`, README의 `dlc/scripts`) | F12 | P3 | Codex 미지적. SKILL.md:14, protocol.md:7·10, README "동작 원리" 확인 |
| U21 | 설계 문서 §6 테스트 경로 `dlc/tests` 오기, §6 명령 표에 `note` 없음, state-format 필수 절 표에 decisions.md 없음 | F13, C(문서) | P3 | 테스트 경로는 두 리뷰 모두 지적. `note`·decisions.md는 Fable만 |
| U22 | 안내 모드와 "상태만 보기"가 중복 | F14 | P3 | Codex 미지적. SKILL.md:38-42와 51-53 확인 |
| U23 | 작업 폴더 날짜(로컬)와 state.md created(UTC)의 기준이 다르다 | F15 | P4 | Codex 미지적. 재현: 로컬 `260913`, UTC `2026-09-12T17:23:18Z` (KST 02:23 시점) |
| M1 | `check analyze`가 codebase.md의 `<!-- fingerprint: -->` 존재·일치를 검사하지 않는다 | 오케스트레이터 추가 | P3 | state-format.md:87은 codebase.md에 지문 주석을 요구하고 `next`는 그 값으로 analyze를 건너뛴다. 지문 없이 승인되면 다음 작업의 init마다 analyze가 다시 뜬다. 재현: 필수 절만 있는 codebase.md → `check analyze: OK` |
| M2 | `check verify`가 verify.md의 ID 참조를 검사하지 않는다 | 오케스트레이터 추가 | P3 | U9의 연장. grounding.md:27은 "설계·계획·빌드"만 명시해 verify는 문서상 빠져 있으나, verify.md의 `## 추적성` 절이 ID를 쓰는 산출물이다. 재현: `FR999 ok` → `check verify: OK` |

매핑 확인: F1~F15 → U1, U2, U3, U6, U7, U8, U9, U10, U11, U18, U19, U20, U21, U22, U23. C1~C10 → U4, U5, U7, U12, U13, U1, U9, U14, U15, U16. C 경계 → U17. C 문서 → U21. 빠진 항목 없음.

## 2. 한쪽만 잡은 결함과 이유

두 리뷰의 축이 달랐다. Fable은 설계 문서·프로토콜과 코드의 정합성을 읽고 논리 결함을 찾았고, Codex는 CLI를 43회 실행하며 환경·입력 경계를 밀어붙였다.

| 한쪽만 | 항목 | 이유 추정 |
|---|---|---|
| Fable만 | U2, U3, U6, U8, U11, U18, U19, U20, U22, U23 | 문서 대 코드 대조에서 나오는 것들. U2·U6·U9(하위 ID)는 산출물 형식 문서(state-format, grounding)를 읽고 "문서가 허용하는 입력을 코드가 오독하는가"를 물어야 보인다. U3·U20·U22는 SKILL.md 품질 축이라 코드 실행으로는 안 나온다 |
| Codex만 | U4, U5, U12, U13, U14, U15, U16, U17 | 실행 QA에서 나오는 것들. U4·U12·U13은 다른 cwd·다른 Python·실제 설치 도구를 써야 드러난다. U5는 "R2·R3가 이 계약대로 구현되면 어떻게 되는가"를 앞당겨 본 결과. U14~U17은 비정형 입력(답변 행 생략, 줄바꿈, 절대경로, 빈 문자열) 경계 테스트 |

기각할 이유가 있는 항목은 없다. 두 리뷰 합집합이 그대로 결함 목록이다.

## 3. 설계 결정이 필요한 항목

### 3-1. design을 건너뛰는 프로파일에서 units.md는 누가 만드는가 (U5)

현재 계약: units.md는 design 산출물. express·bugfix는 design이 없으므로 build 검사가 항상 실패한다.

| 선택지 | 내용 | 장점 | 단점 |
|---|---|---|---|
| **A (권장)** | design이 프로파일에 없으면 **plan 스테이지가 units.md도 만든다**. `check plan`이 그 경우 units.md(필수 절 `## 유닛`, `## 계약`, `## 가정과 열린 질문`)를 함께 검사하고 커버리지 검사도 여기서 한다 | 유닛 표 파서·build 검사·문서 형식이 프로파일 무관하게 하나. R3의 dlc-plan 스킬이 "design이 없으면 유닛 표를 먼저 쓴다" 한 절만 추가하면 된다 | plan이 산출물 두 개를 갖는 경우가 생김 |
| B | express·bugfix에서는 units.md 없이 plan.md의 `## 유닛 순서` 표에서 유닛을 읽는다 | 파일 하나 덜 만듦 | 유닛 표 위치가 프로파일마다 달라 파서·문서·스킬이 두 갈래. 커버리지 검사도 두 갈래 |
| C | express·bugfix에도 design을 넣되 minimal depth로 돌린다 | 계약 변경 없음 | 사용자가 2026-09-13에 확정한 프로파일 구성(설계 §4)을 뒤집는다 |

A를 권장한다. 결론은 설계 문서 §4 프로파일 표 아래와 state-format.md 산출물 표에 반영한다.

### 3-2. fingerprint를 무엇으로 만들 것인가 (U7)

| 선택지 | 내용 | 판단 |
|---|---|---|
| **내용 해시 (권장)** | 경로 + 파일 내용 sha1. `EXCLUDED_DIRS`·`SCAN_DEPTH` 범위는 그대로 | PC가 바뀌어도 같은 소스면 같은 값이라 설계 §1 "PC가 바뀌어도 이어간다"에 맞는다. 소스 파일을 다 읽지만 node_modules 등은 제외되고 깊이 4 제한이 있어 실무 규모에서 문제 없음 |
| mtime·크기 혼합 | 읽지 않고 stat만 | clone·checkout마다 mtime이 바뀌어 다른 PC에서 항상 analyze가 다시 뜬다. 부적합 |
| 문서만 정정 | "파일 목록 지문"이라고 명시 | 내용 변경을 못 잡는 캐시는 R2 analyze 스킬의 가치를 깎는다. 부적합 |

### 3-3. analyze 재실행 경로 (U8)

`dlc.py start analyze --force`를 둔다. 조건: analyze가 프로파일에 있고 status가 pending이며 workspace가 brownfield일 때만. 지문 일치로 `next`가 건너뛴 상태를 사용자가 명시 호출로 뒤집는 유일한 경로다. "codebase.md를 지우고 호출" 방식은 프로젝트 공유 산출물을 지우게 해서 부적합하다. `--force`는 다른 스테이지·다른 상태에서는 거부한다.

### 3-4. 작업 폴더 날짜 기준 (U23)

폴더 이름은 사람이 보는 것이라 **로컬 날짜를 유지**하고 state-format.md에 "폴더 이름의 날짜는 init을 실행한 PC의 로컬 날짜, state.md의 시각은 UTC"라고 적는다. 코드 변경 없음. UTC로 통일하면 KST 오전에 만든 작업이 전날 폴더에 들어간다.

## 4. 개선 목표

목표 하나 = 커밋 하나. 각 목표는 테스트를 먼저 추가(RED)한 뒤 고친다(GREEN). 완료 확인 명령은 모두 저장소 루트 기준이다.

### G1. 상태 전이의 순서와 경계를 코드가 강제한다

- **왜**: `state.md`를 코드가 도맡는 이유는 전이가 프로즈에 따라 흔들리지 않게 하려는 것(설계 §6)인데, 지금은 approve·skip이 순서·상태를 보지 않아 그 보장이 없다. 손상된 state.md와 조작된 active 커서도 코드가 걸러야 한다.
- **속한 지적**: U1(approve 순서), U11(skip이 done 되돌림), U17(빈 skip 사유), U18(None 메시지), U10(profile 누락·이상값 traceback), U16(active 경로·심링크)
- **동작 결정**:
  - `approve <stage>`는 `stage == next_stage()`이고 status가 `active`일 때만. pending이면 "먼저 start", 프로파일 밖이면 "이 프로파일에 없는 스테이지", 완료 후면 "모든 스테이지가 끝났습니다"로 각각 문장을 낸다.
  - `skip <stage>`는 status가 pending·active일 때만. `--reason`은 공백 제거 후 비어 있으면 거부.
  - `read_state`가 profile 누락·미지 값이면 SystemExit 메시지. 
  - `active_work`는 커서 내용이 `^\d{6}-[a-z0-9][a-z0-9-]*$`가 아니면 거부, 작업 경로가 `docs/dlc/` 안에서 벗어나면 거부, 커서 파일이 심링크면 거부. `init`도 심링크 커서에 쓰지 않는다.
- **완료 확인**: 다음 시나리오 테스트가 GREEN — 순서 어긴 approve 거부, skipped·done·프로파일 밖·완료 후 approve/start 메시지, done skip 거부, 빈 사유 거부, profile 없는 state.md 메시지, 절대경로·심링크 active 거부. `python3 -m unittest discover -s dlc/skills/dlc/tests`.

### G2. 산출물 계약이 모든 프로파일에서 성립하고 검사가 문서대로 동작한다

- **왜**: R2·R3 스테이지 스킬이 이 계약 위에 쓰인다. 계약이 프로파일에 따라 깨지거나(U5) 검사가 문서(state-format·grounding·protocol)보다 약하면(나머지) 스킬이 아무리 잘 써져도 승인 게이트가 거짓 통과·거짓 실패를 낸다.
- **속한 지적**: U5(express/bugfix units.md — 3-1 결정 A), U2(유닛 표 절 한정 + `u<n>-<slug>` 패턴), U6(정의 집합을 기능·비기능 절로 한정), U9(하위 ID 집합 대조, build 참조 검사), U14(질문마다 답변 행 필수), U19(질문 번호 연속, 중복 보고 제거), M1(codebase.md 지문 주석 검사), M2(verify.md 참조 검사)
- **동작 결정**:
  - 정의 집합 = `## 기능 요구사항`·`## 비기능 요구사항` 절 본문의 `FR<n>`, `FR<n>.<m>`, `NFR<n>`, `NFR<n>.<m>`. 연속성 검사도 이 집합으로.
  - 참조 검사 대상 = design.md, decisions.md, units.md, plan.md, build/*.md, verify.md. 상위·하위 ID 모두 정의 집합에 있어야 한다.
  - 유닛 표 = `## 유닛` 절 안의 `| u<n>-<slug> | ... |` 행만.
  - design이 프로파일에 없으면 `check plan`이 units.md도 검사하고 커버리지도 본다.
  - 질문 파일: `## Q<n>.` 블록마다 `[Answer]:` 행이 있고 값이 비어 있지 않아야 한다. 번호는 1부터 연속. 요약 확인은 별도 한 건으로만 보고.
  - `check analyze`: codebase.md에 `<!-- fingerprint: <값> -->`이 있고 현재 워크스페이스 지문과 같아야 한다.
- **완료 확인**: 계약 표 포함 units.md, `범위 밖`의 FR 언급, `FR1.9`·`FR999.1`·build의 `FR999`·verify의 `FR999`, `[Answer]:` 없는 Q, Q1·Q3, 지문 없는 codebase.md, express 프로파일 requirements→plan(units.md 포함)→build→verify 완주 테스트가 GREEN.

### G3. 캐시와 입력 처리가 실제 변화를 반영한다

- **왜**: analyze 캐시는 "소스가 같으면 건너뛴다"는 약속인데 경로만 보면 약속이 거짓이다. 사용자가 명시 호출로 다시 돌릴 길도 있어야 한다(설계 §1). 자유 텍스트 입력이 상태 파일 문법과 섞이면 상태가 오염된다.
- **속한 지적**: U7(내용 해시 — 3-2), U8(`start analyze --force` — 3-3), U15(여러 줄 description)
- **동작 결정**: description은 저장 시 줄바꿈을 공백 하나로 접는다. `read_state`는 `## Stages` 앞의 `- key: value`만 메타로 읽는다.
- **완료 확인**: 내용만 바꾼 파일의 지문 변화, `--force` 허용·거부 조건, `"첫 줄\n- profile: unknown"` description의 status 정상 출력 테스트가 GREEN.

### G4. 이식성과 환경 — 문서대로 치면 어느 환경에서든 뜬다

- **왜**: 세 에이전트·여러 PC에서 같은 파일이 동작하는 것이 이 플러그인의 존재 이유(설계 §1)다. 기본 Python에서 시작조차 못 하거나 설치 명령이 실패하면 나머지가 무의미하다.
- **속한 지적**: U4(전역 `--root`), U12(Python 3.9), U13(README 설치 선택자)
- **동작 결정**: 서브파서의 `--root`는 `default=argparse.SUPPRESS`로 두어 전역 값을 덮지 않는다. `from __future__ import annotations` 한 줄로 3.9 호환. README·protocol에 "Python 3.9 이상" 명시. README 설치 명령은 `--skill dlc`로 바꾸고 "스테이지 스킬은 2·3라운드에서 이름을 추가한다"고 적는다.
- **완료 확인**: `--root` 앞·뒤 양쪽 위치 테스트 GREEN. `/usr/bin/python3`(3.9.6)·`python3.12`·`python3.14` 각각에서 `dlc.py --help` exit 0과 unittest OK. `npx skills add <repo> --skill dlc -y`가 임시 디렉터리에 설치됨.

### G5. 문서와 코드가 일치한다

- **왜**: 스킬은 프로즈가 곧 실행 절차다. 경로 표기가 셋이면 에이전트가 하나를 골라 틀리고, 안내 모드가 "작업 없음"이라고 하면 다른 PC의 사용자가 새 작업을 또 만든다.
- **속한 지적**: U3(active 없을 때 기존 작업 나열), U20(경로 표기 통일), U21(설계 §6 경로·note·decisions.md), U22(상태만 보기 절 제거), U23(날짜 기준 명시 — 3-4), 3-1 결정의 설계 문서·state-format 반영
- **동작 결정**:
  - `active_work` 오류 메시지가 `docs/dlc/` 아래 작업 폴더를 나열한다(코드). SKILL.md 안내 모드는 그 목록이 있으면 "다른 작업으로 바꾸기"로 보내고, 없을 때만 dlc-init을 안내한다.
  - 경로 표기는 `<skills>/dlc/scripts/dlc.py` 하나로 통일하고 `<skills>`는 "이 스킬이 로드될 때 보인 스킬 디렉터리의 부모"라고 한 줄 정의한다. README의 `dlc/scripts/dlc.py`도 같은 표기로.
  - "상태만 보기" 절을 없애고 안내 모드에 "인자가 `status`면 2단계의 안내 문장을 생략한다"로 접는다.
  - 설계 §6 검증 명령 경로 정정, 명령 표에 `note`·`start --force` 추가, state-format 필수 절 표에 decisions.md(존재만 검사) 추가, 날짜 기준 한 줄 추가, §4에 3-1 결정 추가.
- **완료 확인**: 문서 grep — `dlc/tests`가 설계 문서에 없음, `<이 스킬 디렉터리>` 표기 없음, SKILL.md에 "## 상태만 보기" 없음. `active_work` 나열 테스트 GREEN. `claude plugin validate ./dlc` 통과.

### 실행 순서와 커밋

G4 → G1 → G3 → G2 → G5. G4를 먼저 하는 이유는 3.9 호환과 `--root`가 이후 모든 테스트의 전제이기 때문이다. G2가 가장 크므로 G1·G3로 상태·파서 기반을 먼저 다진다. 각 목표는 `fix(dlc): ...` 또는 `docs(dlc): ...` 커밋 하나. 전부 끝나면 세 Python 버전 테스트, `claude plugin validate`, Fable 재리뷰(P1·P2 0건 목표) 순으로 검증하고 사용자 승인 후 push.

## 5. 범위 밖 메모

- 저장소 루트의 `.omc/`(oh-my-claudecode 세션 상태)가 추적되지 않은 채 남아 있다. `.gitignore`에 `.omc/`를 넣는 것은 이 이슈 범위 밖이라 손대지 않았다.
- `log.md`의 `note` 텍스트에 줄바꿈이 들어가면 한 줄 형식이 깨진다. 읽는 코드가 없어 결함으로 세지 않았다.

## 조치 결과

(3단계 완료 후 목표별 커밋 해시를 기록한다.)
