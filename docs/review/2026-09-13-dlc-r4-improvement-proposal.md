# [개선 제안] dlc 플러그인 4라운드 종료 — 최종 개선 제안 (2026-09-13)

> 작성 주체: 오케스트레이터(Claude Fable 5.1). 입력은 Opus 대조 리뷰(`2026-09-13-dlc-r4-review-opus.md`, 9건)와 eval 완성도 평가(`2026-09-13-dlc-r4-eval-results.md`), 설계 문서 §8 R4 실측·잔여다. 채택·기각·우선순위는 사용자가 정한다. 초안을 Opus 서브에이전트가 1회 리뷰(16건)했고 지적은 전부 이 문서에 반영했다 — 리뷰표와 조치는 6절.

## 1. 입력과 판정 기준

- Opus 리뷰 9건: P1 0 / P2 3(eval 채점기 근거 문장·발동 지표·재실행 표기) / P3 3(check plan 유닛 열 파싱, 라우터 케이스 부정 패턴, bugfix eval 독립성) / P4 3(run.sh bash 3.2, 검사 형식 변형 경계, README 합산 표기). 스킬 결함 0.
- eval 최종 8/8. 평가 문서가 남긴 개선 후보 4건(검사 설명 구체성, 선택지 맞춤, NFR 분류 편차, 질문 수)과 미측정 영역 4건(design·build·verify eval 없음, 다중 턴, Codex·Gemini eval, ablation).
- 설계 §8 R4 잔여 (2): Codex 답변→요약 확인→승인 턴과 관련 없는 프롬프트의 자동 발동 차단 확인. Codex 실측에서 관찰된 `X. Other` 한국어화.
- 우선순위 정의: **P0** 기록의 사실 오류·채점기가 잘못 증명하는 것(방치하면 다음 라운드가 틀린 전제를 재생산). **P1** 기계 검사·채점기의 증명력 강화(코드·grader 변경, 회귀 테스트 동반). **P2** 스킬 문장·문서 개선과 측정 범위 확장(효과는 있으나 비용 대비 선택). **보류** 근거가 아직 없거나 외부 조건에 막힌 것.
- 비용 표기: 문서 = 텍스트만, 코드 = `dlc.py`·테스트, grader = `case.yaml`(재실행 검증 필요, 케이스당 $0.2~0.9), 실측 = 헤드리스·외부 CLI 실행.

## 2. 제안 목록

| ID | 우선순위 | 출처 | 무엇을 | 어디를 | 왜 (효과) | 비용 | 검증 |
|---|---|---|---|---|---|---|---|
| I1 | P0 | Opus 1 | 설계 §8의 grader 근거 문장 정정 — "라우터 SKILL.md 본문이 슬래시 명령 확장으로 trace에 들어간다"를 "trace에는 `dlc.py`의 출력과 에이전트가 Read한 스킬 파일 본문이 남는다"로 | `docs/design/…design.md` §8 R4 evals 문단 | 보관 trace 2건에 라우터 본문은 0회. 틀린 원인 문장이 다음 grader 설계의 전제가 되는 것을 막는다 | 문서 | 없음 |
| I2 | P2 | Opus 3, eval §3 | 설계 §8 eval 표의 "재실행 (grader 수정 뒤)" 열 제목을 행별 사실로 — plan 행은 "수정 전 패턴으로 재실행, 수정 패턴은 최종 실행에서 검증" | 같은 §8 표 머리말 | 러너 기록의 패턴이 1차와 문자 단위로 같음. 정정 문장은 같은 절의 "최종 실행" 문단에 이미 있어 사실 오류가 방치된 상태는 아니다. 표 머리말만 맞추는 표기 정리라 P2 | 문서 | 없음 |
| I3 | 해소 | Opus 9 | Opus 지적 9의 대상은 `dlc/README.md:52` 하나였고 최종 실행 뒤 "eval 8 케이스 최종 실행 8/8 1.0(1차는 5/8, …)"로 이미 바뀌었다. 초안은 이슈 #4 코멘트에도 "7개 1.0" 서술이 있다고 봤으나 코멘트에 그 문자열은 없다(리뷰 지적 1) — 코멘트 2/2는 행마다 "(재실행)" 표시로 합산 여부를 이미 드러낸다 | — | 조치 없음 | — | — |
| I4 | P1 | Opus 1 | 라우터 세 케이스에 안내 문장 grader 복원 — `router-guide-empty`에 `/dlc:dlc-init`, `router-guide-next`·`router-no-cursor`에 `/dlc:dlc-requirements`를 부르세요 류 문장. 안전 근거를 케이스 주석에 구분해 적는다: `/dlc:dlc-init`은 `dlc/skills/**` 전체에 0회라 **구조적으로** 안전하고, `/dlc:dlc-requirements`는 라우터 `dlc/SKILL.md:41`의 예시 문장과 문자 단위로 같아 "라우터 본문은 trace에 들어가지 않는다"는 **행위 전제**(보관 trace 3건에서 확인) 위에서만 안전하다. **I5와 한 쌍이다** — `router-guide-empty`는 I5로 발동 지표를 걷어내면 오염 없는 양성 앵커가 0이 되므로 I4를 먼저 넣는다 | `router-guide-empty`·`router-guide-next`·`router-no-cursor`의 `case.yaml` | 세 케이스의 최종 trace 모두 스테이지 스킬 Read 0회, 제안 문장이 assistant 텍스트에 실제로 있다(리뷰 지적 2·3 확인). 지금 grader는 "안내했다"를 측정하지 않는다 | grader | 묶음 B suite에 포함 + 음성 확인(패턴을 trace에서 지워 불매치). suite를 돌리지 않으면 세 케이스만 약 $0.6 |
| I5 | P1 | Opus 2 | 스킬 본문에 문자열로 존재해 오염된 발동 지표 5개를 교체 — `router-guide-empty`·`router-guide-next`의 `skill-fired-status-run`(`dlc\.py status`, 라우터 SKILL·dlc.py에 4회), `router-all-gate-waits`의 `skill-fired-next-run`(`dlc\.py next`, 5파일 8회), `express-requirements`·`bugfix-requirements`의 `skill-fired-dlc-py-used`(`init\|start\|approve` alternation). 대체 앵커는 `dlc.py` **출력** 중 스킬 본문에 없는 것 — `다음: requirements → dlc-requirements`(렌더 결과), `requirements: done`, `check plan: OK`, 경로가 붙은 `작업 폴더: docs/dlc/\d{6}-<slug>`(`작업 폴더:`만은 `dlc.py:518`에 있으므로 경로 포함 형태로) — 또는 인자 채워진 실행 형태(`init --profile express --slug`). **변경 없음**: `requirements-vague-followup`의 `skill-fired-start-requirements`·`plan-supplies-units`의 `skill-fired-start-plan`은 스킬 본문에 0회라 이미 깨끗하다. 설계 §8 R2 표 "발동 채점" 행과 §9 앵커 항목에 "이 지표는 스킬 파일 Read와 구분되지 않는다"는 한계를 적는다 | 위 5개 `case.yaml`, 설계 §8·§9 | R3 지적 12가 `tool_used: Skill`에 한 지적이 대체 지표에서 재발했다. 다른 네 케이스에는 깨끗한 출력 grader가 이미 있지만 `router-guide-empty`는 양성 grader 둘(`dlc\.py status`, `활성 작업이 없습니다`)이 모두 dlc.py 문자열이라 I4 없이는 앵커를 잃는다 | grader + 문서 | 묶음 B suite에 포함 |
| I6 | P1 | Opus 5, 리뷰 지적 8 | 부정 패턴이 스킬 본문 문자열과 겹치는 grader 3개를 실행·출력 형태로 좁힌다 — `router-guide-next`·`router-no-cursor`의 `dlc\.py init`(3파일에 존재)·`dlc\.py start`(6파일)를 `init --profile (?:full\|express\|bugfix)`·`start (?:requirements\|plan\|build\|verify)`로, `plan-supplies-units`의 `build-not-started`(`dlc\.py start build`, `dlc-build/SKILL.md:53`에 존재)는 `start`의 출력 `build: active` 부재로. **변경 없음**: `stops-after-requirements`·`next-stage-not-started`의 `dlc\.py start plan`은 스킬 본문에 0회 | 세 `case.yaml` | 에이전트가 참조 문서 하나만 Read하면 거짓 실패한다. `router-guide-empty` 최종 trace에는 dlc.py 안내 문구에서 온 `dlc.py init`이 4회 있어 기전이 실증됐고, 다른 두 케이스는 아직 0회라 잠재 상태다 | grader | 묶음 B suite에 포함 |
| I7 | P1 | Opus 4 | `check_plan_rules`의 유닛 집합을 `## 유닛 순서` 절 전체 텍스트가 아니라 표의 `unit` 열(2열)에서만 모은다. plan 표 전용 행 정규식을 **새로** 두고 2열만 뽑는다 — `UNIT_ROW_RE`(`dlc.py:254`)는 units.md의 4열·unit 1열 표용이라 재사용할 수 없고, `UNIT_NAME_RE`는 다른 용도가 있어 제자리 수정하지 않는다. R3·R4 실측 plan.md 두 벌은 6열 표에 u1·u2가 2열에 있어 그대로 통과한다. 회귀 테스트 1건: 순서 행은 없고 `depends_on` 열에만 있는 유닛이 실패해야 한다 | `dlc.py` `check_plan_rules`(+ 새 정규식), `test_dlc.py` | 문서 셋(`dlc-plan:109`, 설계 §6, state-format)이 "표의 unit 집합"이라 말하는데 구현은 절의 문자열이다. 목록형도 통과한다 | 코드 | unittest 88건 |
| I8 | P1 | Opus 8 | 두 새 검사의 형식 변형 경계를 정한다 — `- 실행 명령:`·`**실행 명령**:`(목록·볼드)와 `**승인**`(볼드 판정)을 받을지 거절할지. 받으면 `RUN_COMMAND_RE`·`check_verdict`에 접두 허용 + 테스트 1건, 거절하면 실패 메시지에 "줄머리에 그대로"를 덧붙인다. `plan-md-has-run-command` grader는 어느 쪽이든 `check`와 같은 형태로 | `dlc.py:257`·`:422-424`, `plan-supplies-units/case.yaml:47`, `dlc-plan:111`·`dlc-verify:89` | 골격을 따르면 안 나지만, 실패 메시지가 원인(형식)을 알려주지 않는다. grader와 check의 기준이 다르다 | 코드 + grader (거절 쪽의 메시지 수정도 `dlc.py` 문자열 편집이고, 두 선택지 모두 `case.yaml:47`을 고친다) | unittest + 묶음 B suite에 포함 |
| I9 | P2 | eval §5 관찰 1 | state-format.md의 검사 문단(현재 한 단락)을 "산출물 → 검사 항목 → 실패 메시지" 표로 바꾼다 | `references/state-format.md` "산출물 필수 절" 절 | eval 5회 중 3회 에이전트가 `dlc.py` 소스를 grep해 검사 규칙을 확인했다. 문서가 답하면 턴·비용이 줄고 스크립트가 없는 환경의 수동 체크리스트도 정확해진다 | 문서 | 묶음 B suite 실행에서 `grep.*dlc\.py` 횟수 비교(정성) |
| I10 | P2 | Opus 6, eval §5 | `bugfix-requirements` 프롬프트의 답변 목록을 주제 이름 없이 순서를 섞은 문장으로 바꾸고, §9 bugfix 해소 근거에서 Codex 실측을 앞에 둔다 | `bugfix-requirements/case.yaml`, 설계 §9 | 지금 프롬프트는 bugfix 주제 순서와 이름을 그대로 줘 "스킬이 주제를 바꿨다"의 독립 증거가 못 된다 | grader + 문서 | 묶음 B suite에 포함 |
| I11 | P2 | eval §5 관찰 3 | `dlc-requirements` 여섯 차원 표에 분류 지침을 넣되 두 곳을 함께 고친다 — 표 아래 한 줄 "기술 차원의 답은 `## 제약`, 품질 차원의 답은 FR의 수용 기준으로. NFR은 수치와 측정 방법이 있는 것만"과, 이와 충돌하는 비기능 행(`SKILL.md:32` "성능·보안·가용성·호환 중 이번에 중요한 것과 그 수치")에 "보안·성능 주제라도 수치·측정 방법이 없으면 `## 제약`"을 덧붙여 두 문장이 서로를 가리키게 한다. 편차 사례(SSO 인증·읽기 전용 접근)는 보안 주제라 지금 비기능 행이 자기 것이라고 말하기 때문이다 | `dlc-requirements/SKILL.md` 질문 주제 절(표 + 아래 한 줄) | 같은 답변을 한 실행은 NFR1~3(SSO·읽기 전용·테스트 2건)으로, 다른 실행은 제약·수용 기준으로 배치했다. 뒤 단계의 ID 참조가 실행마다 달라진다 | 문서 | 묶음 B suite의 requirements 케이스에서 NFR 수 관찰 |
| I12 | P2 | Opus 7 | `run.sh`의 `for d in "${MOVED[@]}"`에 bash 3.2 빈 배열 가드 | `dlc/evals/run.sh:19` | Docker Desktop이 없는 PC에서 EXIT trap이 `unbound variable` 한 줄을 낸다(종료 코드는 0) | 코드(셸 1줄) | 빈 배열로 `bash -n` + 실행 |
| I13 | P2 | Codex 실측 관찰 | 질문 파일의 마지막 선택지 `X. Other (please specify)`를 `check_questions`가 볼지 결정 — 강제하면 Codex의 한국어화(`X. 기타 — 직접 설명한다`)가 실패한다. 제안: 강제하지 않고 protocol.md에 "`X.`로 시작하는 마지막 선택지면 된다. 문구는 에이전트 언어를 따를 수 있다"를 적어 규칙을 현실에 맞춘다 | `references/protocol.md` 질문 파일 형식 절 | 규칙과 실행이 다르면 R5 리뷰가 또 지적한다. 형식의 핵심은 `[Answer]: X - <서술>` 파싱이며 `check`는 답변 값만 본다 | 문서 | 없음 |
| I14 | P2 | eval §6 | build 스테이지 eval 1건 — R3 `wcl` 픽스처(requirements·plan·units·u1 기록·u1 코드)를 scaffold로 옮기고 u2 구현을 시킨다. grader: `note build "재개"` 또는 `start build`, `build/u2-cli.md` 존재, `check build: OK`, 전체 테스트 GREEN 출력 | 새 `dlc/evals/build-resume/` | design·build·verify 중 eval 공백이 가장 큰 곳. R4 헤드리스 재개 실측($2.30, 19턴)이 그대로 케이스가 된다 | grader — 픽스처 12파일(`active`·`state.md`·`log.md`·requirements 2·plan 2·`units.md`·`build/u1-count.md`·`wcl/__init__.py`·`wcl/count.py`·`tests/test_count.py`) 합계 279줄/17KB, heredoc scaffold 약 300줄(현재 최대 `plan-supplies-units/scaffold.sh` 111줄의 약 3배) | 케이스 실행 $2~3 |
| I15 | 실측 잔여 | 설계 §8 R4 잔여 (2) | Codex `exec resume --last`로 답변→요약 확인→승인까지, 그 뒤 새 세션에서 관련 없는 프롬프트(예: "이 저장소 파일 목록을 보여줘")로 dlc 스킬이 발동하지 않음을 확인 | `/tmp/dlc-r4-codex` 세션, 설계 §7·§8, 이슈 #4 코멘트 | 이슈 #4 완료 조건 첫 항목("Codex에서 init→requirements 승인까지 실행 기록")이 아직 질문 생성·대기까지다 | 실측(Codex 한도 해제 뒤) | log.md에 `approve` 행, 코멘트 |
| I16 | 보류 | eval §6 | design·verify 스테이지 eval, Codex·Gemini에서의 eval, ablation 비교 | — | design은 full 픽스처가 필요하고 verify는 build 산출물이 필요해 I14 뒤에만 의미가 있다. Codex·Gemini eval은 러너가 Claude 전용이다. ablation은 명시 호출 스킬에 성립하지 않는다(플러그인 없이는 슬래시 명령이 없음) | — | — |
| I17 | 보류 | 설계 §7, README | Gemini CLI 모델 호출 실측, Cursor 실측 | — | Gemini는 이 PC의 계정 티어로 막혀 있고(API 키·Antigravity 계정이 있을 때), Cursor는 설치 환경이 없다. 조건이 생기면 README 표의 "미실측" 행만 채운다 | 실측 | — |

## 3. 묶음과 순서 (R5 후보)

같은 파일을 건드리는 것은 한 커밋으로, 검증(재실행)이 필요한 것은 한 번의 suite 실행으로 모은다.

| 묶음 | 항목 | 한 줄 | 검증 |
|---|---|---|---|
| A. 기록 정정 | I1, I2, I3 | 설계 §8 두 문장·표 머리말, 이슈 코멘트 단서. 코드 변경 없음 | 없음 |
| B. 채점기 정비 | I4 → I5, I6, I10 | 안내 문장 grader 복원을 먼저(I4), 그 다음 발동 지표 교체(I5) — `router-guide-empty`가 앵커를 잃지 않게. 부정 패턴 좁힘, bugfix 프롬프트 독립화. 설계 §8·§9의 채점 결정 문장 갱신 | 전체 suite 1회(약 $4) 또는 바뀐 케이스만(5절 결정) + 각 grader 음성 확인 1회 |
| C. 검사 경계 | I7, I8, I12 | `check_plan_rules` 유닛 열 파싱(새 정규식), 형식 변형 경계 결정, run.sh 가드. 회귀 테스트 2~3건 | unittest. plan 케이스 재실행은 B에 합침 |
| D. 스킬·참조 문장 | I9, I11, I13 | 검사 표, NFR 분류 지침, `X.` 선택지 규칙 | B의 suite 실행에서 정성 관찰 |
| E. 실측·확장 | I15, I14 | Codex 잔여 턴, build eval 1건 | Codex 세션 resume, 새 케이스 실행 |

순서 제안: A → C → D → B(A·C·D의 변경을 한 suite 실행으로 함께 검증) → E. 2절의 검증 열은 그래서 "묶음 B suite에 포함"으로 통일했고 개별 금액은 suite를 돌리지 않을 때의 대안이다. A는 문서라 검증이 없고, C는 unittest로 닫히며, D의 프로즈 변경은 에이전트 행위에 영향을 주므로 B 뒤 suite 1회가 A·C·D를 함께 덮는다. A~D는 한 세션 안에서 끝나는 크기(문서 5곳, 코드 3곳, grader 9곳)이고, E는 외부 조건(Codex 한도, 비용 결정)에 걸린다.

## 4. 하지 않을 것과 이유

- **안내 문장 grader를 스테이지 케이스에는 추가하지 않는다.** 스테이지 스킬을 Read하는 케이스(requirements·plan·gate)에는 스킬 본문이 trace에 들어가 거짓 양성이 난다. 라우터 세 케이스(안내 모드 둘 + 커서 없음)만 대상이다(I4).
- **질문 수가 minimal 기준(2~4)을 넘는 것은 조치하지 않는다.** 주제 수에 비례하며 기준이 상한이 아님은 R2에 기록됐다(eval §5 관찰 4).
- **`X. Other (please specify)` 문구를 기계 검사로 강제하지 않는다.** 이식성의 핵심은 `[Answer]:` 태그와 `X - ` 접두이고, 문구 강제는 한국어 에이전트 출력과 충돌한다(I13).
- **eval 케이스의 사전 답변 방식을 바꾸지 않는다.** 러너가 다중 턴을 지원하지 않는다(설계 §8 R2). 다중 턴 증거는 Codex `exec resume` 실측이 맡는다.
- **루트 README의 dlc 외 항목(`pr-automator` 행, "네 개의 플러그인")은 이 플러그인 범위 밖이다.** 별도 정리 작업으로 넘긴다.

## 5. 사용자 결정이 필요한 것

1. **I8 — 형식 변형을 받을지 거절할지.** 받으면 `- 실행 명령:`·`**승인**`처럼 골격과 조금 다른 표기도 `check`가 통과시킨다(관대함, 코드 2곳 + 테스트). 거절하면 지금처럼 골격 그대로만 통과하고 실패 메시지만 "줄머리에 그대로 적으세요"로 친절해진다(엄격함, 메시지 1줄). 어느 쪽이든 plan 케이스 grader를 같은 기준으로 맞춘다.
2. **I14 — build eval을 만들지.** 만들면 design·build·verify 중 하나가 eval에 들어오고 R4 재개 실측이 재현 가능한 케이스가 된다. 비용은 케이스당 $2~3(다른 케이스의 3배)이고 scaffold가 약 300줄(픽스처 12파일 279줄, 현재 최대의 3배)로 파이썬 코드 픽스처를 품는다. 만들지 않으면 세 스테이지는 헤드리스 실측 기록으로만 남는다.
3. **묶음 B 검증 비용.** 전체 suite 1회(8 케이스, 약 $4)로 A·C·D의 변경까지 함께 검증할지, grader가 바뀐 케이스만(라우터 3 + bugfix + plan, 약 $2) 돌릴지. 전체를 돌리면 D의 프로즈 변경(I9·I11)이 requirements 케이스에 미치는 영향까지 한 번에 보이고, 부분만 돌리면 비용은 절반이지만 D의 효과는 다음 라운드로 미뤄진다.
4. **I13 — `X.` 선택지 문구 규칙 완화.** 완화하면 Codex 산출물이 규칙 위반이 아니게 되고 protocol.md 한 줄이 바뀐다. 유지하면 Codex 실측 관찰을 "규칙 위반, check 미검출"로 기록해 두고 R5에서 검사 추가를 검토한다.

## 6. 서브에이전트 리뷰와 조치

리뷰 주체: Claude Opus 서브에이전트(읽기 전용, 2026-09-13). 대상은 이 문서의 초안이며 아래 표는 리뷰어가 보낸 그대로다. 총 16건 — P1 1 / P2 4 / P3 6 / P4 5. 전제 확인: I4는 보관 trace 3건 모두 스테이지 스킬 Read 0회·안내 문장 실재로 성립하되 `/dlc:dlc-requirements`는 라우터 SKILL.md 예시와 같아 행위 전제가 필요하고, I6은 `router-guide-empty` trace의 `dlc.py init` 4회로 기전이 실증됐다. 전체 판정은 "네 곳(I3·I4·I9·I5)을 고친 뒤 채택". 오케스트레이터가 지적 1·5·6·8의 grep 근거와 지적 9·15의 수치를 직접 재확인했고, 16건 전부 위 본문에 반영했다(조치 열).

| 번호 | 심각도 | 대상 | 지적 | 근거 인용 | 권장 조치 | 조치 |
|---|---|---|---|---|---|---|
| 1 | P1 | I3 | 남은 조치가 존재하지 않는 문장을 고치려 한다. 이슈 #4 코멘트에 "7개 1.0" 서술이 없다 | `gh issue view 4 --comments`에서 `7개` 0회. 코멘트 2/2는 케이스별 표이고 행마다 "(재실행)" 표시로 합산 여부를 드러낸다. Opus 지적 9의 대상은 `dlc/README.md:52` 하나였고 이미 반영됨 | I3을 "해소, 조치 없음"으로 닫는다 | 반영 — I3 행을 "해소"로 |
| 2 | P2 | I4 | 안전 근거("스테이지 스킬 Read가 없다")가 `router-guide-next`에는 성립하지 않는다. 오염원이 라우터 SKILL.md다 | `dlc/skills/dlc/SKILL.md:41` 예시 문장이 trace 이벤트 9의 assistant 텍스트와 문자 단위로 같다. `/dlc:dlc-init`은 `dlc/skills/**` 전체에 0회 | 구조적 안전(`dlc-init`)과 행위 전제 위의 안전(`dlc-requirements`)을 케이스 주석에 구분해 적는다 | 반영 — I4 본문에 두 근거 구분 |
| 3 | P2 | I4, 4절 | `router-no-cursor`를 근거 없이 제외했다. 같은 안내 문장을 내고 스킬 Read가 없다 | `/private/tmp/e-4t4d9O/out/trace.jsonl` 마지막 assistant 텍스트에 같은 안내 문장, `SKILL.md` 0회 | I4를 세 케이스로 넓힌다 | 반영 — I4 세 케이스, 4절 문장 수정 |
| 4 | P2 | I9 | 문서 전용 변경이 P1에 있다 | 1절 P1 정의 "코드·grader 변경, 회귀 테스트 동반" / I9 비용 "문서", 검증 "정성" | P2로 내린다 | 반영 |
| 5 | P2 | I5 | "각 케이스에 출력 grader가 이미 있다"가 `router-guide-empty`에 성립하지 않는다. 교체 뒤 깨끗한 발동 앵커가 0이 된다 | 양성 grader 둘(`dlc\.py status`, `활성 작업이 없습니다`)이 모두 dlc.py 소스 리터럴 | I4·I5를 한 쌍으로 적고 묶음 B에서 I4를 먼저 | 반영 — I4·I5 본문, 묶음 B 순서 |
| 6 | P3 | I5 "어디를" | "5개 `case.yaml`"이 어느 것인지 없다. `skill-fired-*`는 7개 케이스에 있고 2개는 깨끗하다 | `grep -rn "name: skill-fired" dlc/evals/` 7건. `dlc\.py start requirements`·`start plan`은 스킬 본문 0회 | 교체 대상 5개를 이름으로, 2개는 "변경 없음" | 반영 |
| 7 | P3 | I5 앵커 | `작업 폴더:`만 스킬 파일(`dlc.py:518`)에 있다 | 기존 grader는 경로까지 붙여 안전 | 경로 포함 형태로 | 반영 |
| 8 | P3 | I6 | 같은 결함의 부정 grader 1건 누락 — `plan-supplies-units`의 `build-not-started`(`dlc\.py start build`가 `dlc-build/SKILL.md`에 존재) | `grep -rEn 'dlc\.py start build' dlc/skills/` 1건. `start plan`은 0회 | I6에 추가, 나머지는 "0회, 변경 없음" | 반영 — 출력 `build: active` 부재로 |
| 9 | P3 | I7 "어디를" | `UNIT_ROW_RE`는 units.md 4열·unit 1열용이라 재사용 불가, `UNIT_NAME_RE` 제자리 수정은 다른 용도를 건드린다. plan 표는 6열·unit 2열 | `dlc.py:254`, `dlc-plan/SKILL.md:65`, 실측 plan.md 두 벌 | plan 표 전용 정규식을 새로 두고 2열만 모은다 | 반영 |
| 10 | P3 | I11 | 제안 문장이 여섯 차원 표의 비기능 행("성능·보안·가용성·호환 … 수치")과 충돌한다 | `dlc-requirements/SKILL.md:32` | 비기능 행도 함께 손봐 두 문장이 서로를 가리키게 | 반영 |
| 11 | P3 | 5절 | 묶음 B의 suite 1회 약 $4 지출이 결정 항목에 없다 | 3절 B 검증 열 | 전체 suite인지 바뀐 케이스만인지 결정 항목으로 | 반영 — 5절 3번 |
| 12 | P3 | 2절 검증 열 ↔ 3절 | 검증 비용 이중 계상(I4 $0.4, I10 $0.7, I5 $4를 각각 적고 3절은 한 suite로 합친다). 순서 자체는 타당 | — | 검증 열을 "묶음 B suite에 포함"으로 통일 | 반영 |
| 13 | P4 | I2 | P0 과배치. 정정 문장이 §8 같은 절에 이미 있다 | 설계 §8 "최종 실행" 문단 | P2로 | 반영 |
| 14 | P4 | I8 | 비용 "코드 또는 문서"가 어느 선택지에도 맞지 않는다. 거절 쪽 메시지 수정도 코드, 양쪽 모두 grader 수정 | `dlc.py:417`·`:426`, `case.yaml:47` | "코드 + grader" | 반영 |
| 15 | P4 | I14 | 픽스처 크기가 "큼"으로만 적혀 결정 근거가 안 된다 | 12파일 279줄/17,163바이트, 현재 최대 scaffold 111줄 | 수치를 5절 결정 항목에 | 반영 — I14·5절 2번 |
| 16 | P4 | 1절·4절 | eval 관찰 4(질문 수)의 처분이 없다 | eval §5 관찰 4는 "기준이 상한이 아님(R2)"으로 닫힘 | 4절에 "조치 없음" 한 줄 | 반영 |
