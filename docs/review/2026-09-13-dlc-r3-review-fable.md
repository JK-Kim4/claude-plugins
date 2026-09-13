# [Fable 리뷰] dlc 플러그인 3라운드 — 스테이지 스킬 4개 (design·plan·build·verify) + express 완주 (2026-09-13)

> 리뷰 주체: Claude Fable 5.1 서브에이전트(읽기 전용). 사람이 아닌 모델 리뷰이며 채택·기각은 오케스트레이터가 정한다. 조치 결과는 이 문서 3절에 있고, 전부 같은 라운드에 반영했다.

## 1. 범위와 방법

- 대상: 브랜치 `feature/dlc-plugin` 워킹트리(HEAD `6d45c82` + 미커밋 변경). 신규 `dlc/skills/dlc-{design,plan,build,verify}/SKILL.md`·`agents/openai.yaml`, 수정된 `dlc.py`(빌드 추적성 커버리지, decisions.md 필수 절)·`test_dlc.py`(골격 비교 확장)·라우터·protocol.md·state-format.md·README·설계 문서 §4·§6·§8.
- 기준: 이슈 #3 본문(만들 스킬 표, 완료 조건), 설계 문서 §3~§8, `grounding.md`, `dlc.py`의 `ARTIFACTS`·`BUILD_UNIT_SECTIONS`·`QUESTION_STAGES`·`check_stage`·`check_build`. R2 스킬의 작성 관례, R2 통합 리뷰 U16.
- 실행: `python3 -m unittest discover -s dlc/skills/dlc/tests` 79건 GREEN(리뷰 시점), `claude plugin validate ./dlc` 통과. 실측 산출물 `/tmp/dlc-r3-express`(express 완주)와 `/tmp/dlc-r3-full`(full design)에서 `check` 재실행, trace `express.jsonl`·`design.jsonl` grep·파싱.
- 리뷰 관점 6개(계약 일치 / 이슈 요구 충족 / 문서 간 모순 / 실행 가능성 / 테스트·스크립트 / 실측 산출물)를 모두 봤다. 인용 없는 지적은 내지 않았다.

## 2. 지적표

| 번호 | 심각도 | 파일:줄 | 지적 | 근거 인용 | 권장 조치 |
|---|---|---|---|---|---|
| 1 | P2 | `dlc/skills/dlc-build/SKILL.md:27-28`, `dlc-plan/SKILL.md:51`, 설계 §8 | craft:tdd 참조 지시가 실행되지 않았고, 설계 문서는 원인을 잘못 적었다. express 세션에 `craft:tdd`가 있었는데 에이전트는 읽지 않고 폴백으로 갔다. 스킬이 "어떻게 읽는가"(Claude Code 플러그인 스킬은 경로를 알 수 없고 Skill 도구 호출로만 본문이 로드됨)를 안 적어 도달 불가능한 분기다 | 스킬: "이 에이전트의 스킬 목록에 `craft:tdd`(또는 `tdd`)가 있으면 그 스킬 본문이 테스트 규율의 원천이다. 첫 유닛을 시작하기 전에 한 번 읽고". 설계 §8: "헤드리스 환경에는 craft 플러그인이 없어". trace init 이벤트 `skills` 147개에 `craft:tdd` 포함, `craft/skills/tdd/SKILL.md` Read 0회 | 스킬에 로드 방법 명시(Claude Code: Skill 도구 호출, Codex·Gemini: `<skills>/tdd/SKILL.md` Read). 설계 §8 정정 |
| 2 | P2 | `grounding.md:13,19` ↔ `dlc-build/SKILL.md:75,87`, `dlc-verify/SKILL.md:73` | 출처 규칙은 `[assumption]`을 가정 절 안에서만 쓰라 하는데 build·verify 스킬은 추적성 표 데이터 행에 달라고 지시한다. 실측 산출물도 그렇게 나왔다 | grounding: "`[assumption]` \| 근거 없음. `## 가정과 열린 질문` 절 안에서만 쓴다". dlc-build:87 "표에 남기되 출처를 `[assumption]`으로 달고 가정 절에도 적는다". 실측 `build/u1-count.md:15` `\| NFR1 \| … \| [assumption] \|` | grounding.md에 추적성·검증 표의 "미확인" 행 예외를 명시 |
| 3 | P2 | `dlc-verify/SKILL.md:28`, `dlc-build/SKILL.md:44` | verify 추적성 표의 "수용 기준" 열이 requirements.md 원문이 아니라 테스트 픽스처에 맞춰 고쳐 적혔다. 스킬에 "수용 기준은 원문 그대로"가 없고, build의 "기대값은 수용 기준에서" 위반도 기록에 남지 않았다 | requirements.md:12 "`3 5 20 a.txt`" / verify.md:15 "`2 5 24 a.txt`" / `tests/test_cli.py:29` "# FR1 수용 기준: 줄 2·단어 5·문자 24" / `build/u2-cli.md`에 편차 언급 없음 | dlc-verify 3단계에 원문 인용·픽스처 편차 처리 규칙 추가. dlc-build 보고 (d)에 픽스처 편차 한 줄 추가 |
| 4 | P3 | `dlc-verify/SKILL.md:12` ↔ `:49` | 자기모순. "코드를 고치는 단계가 아니다"와 반려 경로 (a) "이 세션에서 고친다". 고칠 때 red-green 규율을 따르라는 말도 없다 | :12 "코드를 고치는 단계가 아니다. 고칠 것이 나오면 판정으로 돌려보낸다" / :49 "(a) 이 세션에서 고친다 — 고친 유닛의 `build/<unit>.md`를 갱신하고" | :12를 "리뷰 중에는 고치지 않는다"로, (a)에 dlc-build 2~5단계로 고친다고 명시 |
| 5 | P3 | `dlc-verify/SKILL.md:27` ↔ `:45-47` | 커버리지 목표는 있는데 도구가 없어 "측정하지 않음"인 경우 판정 규칙 세 행 어디에도 해당하지 않는다 | :27 "도구가 없으면 측정하지 않았다고 적고 가정 절에 남긴다" / :45 "커버리지 기준 충족(또는 기준 없음)" / :47 "커버리지 기준 미달" | 조건부 승인 행에 "커버리지 미측정(사용자 수락)" 추가 |
| 6 | P3 | `dlc-verify/SKILL.md:49` (b) | 다음 세션 재개 시 `start verify`를 다시 실행하지 말라는 안내가 없다. `dlc.py start`는 active 스테이지를 다시 받아 log에 start가 중복된다. build에는 같은 상황의 "재개" 문단이 있다 | :49 "(b) 멈춘다 — verify는 `active`로 남고 다음 세션에서 1부터 다시 한다" / protocol.md:18 / `dlc.py` `cmd_start`에 active 재시작 차단 없음 | dlc-build:53과 같은 재개 문단 추가 |
| 7 | P3 | `dlc-plan/SKILL.md:33,37-42` | full에서 물을 수 있는 주제는 4개뿐인데(1번은 plan이 units.md를 만들 때만, 6번은 practices.md가 없을 때만) "standard(full)는 5~8개"를 기준으로 둬 채우려면 질문을 지어내야 한다 | :33 "standard(full)는 5~8개" / :37 "(units.md를 이 단계가 만들 때만)" / :42 "(practices.md가 없을 때)" | "full에서는 주제가 넷이라 5~8 기준을 채우지 않아도 된다" 명시 |
| 8 | P3 | `grounding.md:12` ↔ `dlc-build/SKILL.md:78`, `dlc-verify/SKILL.md:61` | 테스트 실행 결과·수동 측정값에 `[code:<경로>]`를 달게 하는데 태그 정의는 "파일을 직접 읽어 확인한 사실"이라 실행·측정 결과를 담는 태그가 없다 | grounding:12 / dlc-verify:61 "실행: `python3 -m pytest -q` → 12 passed … [code:tests/]" / 실측 verify.md:8 "최선 0.113초 … [code:wcl/__main__.py]" | `[code:]` 정의에 "실행·측정해 얻은 결과 포함" 추가 |
| 9 | P3 | `dlc-plan/SKILL.md:55` | full에서 순환 발견 시 "사용자가 design을 고치도록 안내"하지만 design은 이미 `done`이라 되돌릴 전이가 없다. units.md를 고친 뒤 `check design`을 다시 돌리라는 말도 없다 | :55 / `dlc.py` `cmd_check`에 `require_is_next` 없음 | units.md 수정 → `check design` 재실행 → `note plan`으로 구체화 |
| 10 | P4 | `grounding.md:28` | R3의 빌드 추적성 커버리지 검사가 식별자 절에 반영되지 않았다(protocol.md·state-format.md는 갱신됨) | grounding:28 "존재하지 않는 ID 참조(하위 ID 포함)와 어느 유닛도 맡지 않은 요구사항을 잡는다" / dlc.py `gaps` | 한 구절 추가 |
| 11 | P4 | `dlc-build/SKILL.md:92` | 완료 기준은 "plan.md의 모든 유닛"이라 하는데 스크립트는 units.md의 유닛 표로 파일을 요구한다 | :92 / dlc.py `units = units_table(work)` / state-format.md:91 | "units.md의 모든 유닛"으로 고치고 집합 일치 규칙을 전제로 명시 |
| 12 | P4 | `dlc.py:421` | 추적성 커버리지가 `## 추적성` 절의 산문 속 ID까지 센다. 표에 넣지 않고 문장만 써도 통과한다. 스킬은 표에 적으라고 한다 | dlc.py:421 `ids_in(section_body(text, "## 추적성"))` / dlc-build:86-87 | 표 행(`\|`로 시작하는 줄)만 세도록 좁히고 회귀 테스트 1건 추가 |
| 13 | P4 | 실측 `verify.md:25,30` ↔ `dlc-verify/SKILL.md:49` | 산출물이 1차 P1을 "P1 (수정됨)"으로 표에 남긴 채 판정에 "P1 0건"을 적어 표와 판정이 어긋난다. 스킬이 "이전 발견을 표에 남겨도 되는가"를 정하지 않은 결과 | verify.md:25 "\| 1 \| P1 (수정됨) \|" / :30 "P1 0건(1차 발견 1건은 …)" | "이전 실행의 발견은 표에서 빼고 판정 절에 note 시각으로만 언급" 명시 |
| 14 | P4 | `dlc-build/SKILL.md:37` | craft가 있으면 `craft:implement`를 쓸 수 있다고 안내하라는 지시가 express 실행에서 수행되지 않았다. 안내 시점이 절차 번호에 없어 건너뛰기 쉽다 | :37 / trace의 `craft:implement` 매치 2건은 모두 시스템 스킬 목록 문자열 | 절차의 첫 유닛 1단계 앞에 두거나 §8 관찰에 기록 |

요약: P1 0건, P2 3건, P3 6건, P4 5건.

## 3. 조치 결과 (같은 라운드)

14건 전부 반영했다. 기각 없음.

| 번호 | 조치 |
|---|---|
| 1 | dlc-build "테스트 규율의 원천" 절, dlc-plan "seam과 예산", dlc-design "인터페이스 대안이 쟁점일 때"에 에이전트별 로드 방법(Claude Code는 Skill 도구 호출, Codex·Gemini는 `<skills>/<name>/SKILL.md` Read)과 "목록에 있는데 로드하지 않고 폴백으로 가지 않는다"를 명시. **정정(같은 날, Opus 리뷰 1번):** 이 지적의 사실 관계는 틀렸다. trace 순번 169에 `Skill {"skill":"craft:tdd"}` 호출과 173에 본문 주입이 있어 에이전트는 실제로 로드했다. "읽지 않았다"는 파일 Read만 센 오류다. 로드 방법 명시는 Codex·Gemini 경로 때문에 유지하고, 설계 §8 관찰은 "Skill 도구로 로드했다"로 되돌려 적었다 |
| 2 | grounding.md `[assumption]` 정의에 build·verify 추적성·검증 표의 "미확인" 행 예외를 추가(같은 내용을 가정 절에도 둔다) |
| 3 | dlc-verify 3단계: 수용 기준 열은 requirements.md 원문 그대로, 픽스처 편차는 확인 열에 적고 판정 조건 검증 여부로 미확인 판정. dlc-build 7단계 (d)에 픽스처 편차 보고 추가 |
| 4 | dlc-verify 머리말을 "리뷰 중에는 고치지 않는다. 고치는 것은 반려 뒤 사용자 결정으로만"으로. (a) 경로에 dlc-build 2~5단계로 고친다고 명시 |
| 5 | 조건부 승인 조건에 "커버리지 목표는 있는데 도구가 없어 측정하지 못했고 사용자가 받아들임" 추가 |
| 6 | (b) 경로에 재개 규칙(`start verify` 재실행 금지, `note verify "재개"`) 추가 |
| 7 | dlc-plan 질문 수 문장에 "full에서는 주제가 넷이라 5~8 기준을 채우려고 질문을 지어내지 않는다" 추가 |
| 8 | grounding.md `[code:<경로>]` 정의에 "그 파일을 실행·측정해 얻은 결과(명령을 함께 적는다)" 추가, build·verify 기록에서 쓴다고 명시 |
| 9 | dlc-plan 순환 처리: design은 `done`이라 되돌릴 전이가 없음을 적고, units.md 수정 → `check design` 재실행 → `note plan`으로 구체화 |
| 10 | grounding.md 식별자 절에 build 추적성 커버리지 검사 추가 |
| 11 | dlc-build 완료 기준을 "units.md의 모든 유닛"으로, plan.md 집합 일치 규칙을 전제로 명시 |
| 12 | `dlc.py check_build`가 `## 추적성` 절의 `\|`로 시작하는 표 행만 세도록 수정. 회귀 테스트 `test_build_traceability_counts_only_table_rows` 추가(옛 로직에서 FAIL 확인 후 GREEN). 스킬에 "표 밖의 산문은 세지 않는다" 명시 |
| 13 | dlc-verify (a)/(b) 문단에 "이전 실행에서 찾아 고친 발견은 표에서 빼고 판정 절에 note 시각으로만 언급. 표의 심각도별 수와 판정의 수가 같아야 한다" 추가 |
| 14 | dlc-build 유닛 순서 1단계에 "첫 유닛이면 그 전에 `craft:implement` 안내를 한 번 한다" 추가. 설계 §8 관찰에 미수행 사실 기록 |

반영 뒤: `python3 -m unittest discover -s dlc/skills/dlc/tests` 80건 GREEN, `claude plugin validate ./dlc` 통과, 스킬 4개 모두 300줄 이하. 실측 산출물(`/tmp`)은 다시 만들지 않았다. 3·13번은 산출물 품질 지적이며 스킬 문장 수정으로 다음 실행부터 적용된다.

## 4. 이 리뷰가 확인한 이슈 #3 완료 조건

- 확인: 스킬 4개 + openai.yaml 4개, `claude plugin validate` 통과. 골격 H2 비교 테스트가 `ARTIFACTS`·`BUILD_UNIT_SECTIONS`·plan의 units.md까지 11개 골격 검사. express 완주(`status` 전부 done, `next`가 `done`, 실제 코드·테스트 생성). full design 1회 실행 `check design` 통과. 라우터 `--all`이 스테이지마다 멈추고 승인 뒤 다음 스킬 파일을 읽어 이어감(trace에서 `../dlc-<stage>/SKILL.md` Read 5회). 실행 중 결함은 이 문서의 14건이며 같은 라운드에 수정 + 테스트.
- 미확인(이 리뷰 범위 밖): 커밋·push.
