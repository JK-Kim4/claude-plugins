# [Opus 리뷰] dlc 플러그인 3라운드 — 설계 문서 대 구현 대조 (2026-09-13)

> 리뷰 주체: Claude Opus 서브에이전트(읽기 전용). 사람이 아닌 모델 리뷰이며 채택·기각은 오케스트레이터가 정한다.

## 1. 범위와 방법

- 읽은 것: 설계 문서 `docs/design/2026-09-13-dlc-plugin-design.md` 전문(§1~§9), `dlc/` 전체(`plugin.json`, `README.md`, 라우터 `skills/dlc/SKILL.md`, 참조 3개, `scripts/dlc.py` 672줄, `tests/test_dlc.py`, 스테이지 스킬 9개와 `agents/openai.yaml` 10개, `evals/express-requirements/`), 마켓플레이스 `.claude-plugin/marketplace.json`의 dlc 항목, 이슈 #3 본문, 앞선 `docs/review/2026-09-13-dlc-r3-review-fable.md`.
- 실행: `python3 -m unittest discover -s dlc/skills/dlc/tests` → **80건 GREEN**. `claude plugin validate ./dlc` → **통과**. 실측 산출물에 `dlc.py check` 재실행 7회(express의 requirements·plan·build·verify, full의 practices·requirements·design) **전부 OK**, `status`는 express 전부 done·`next`가 `done`, full은 `next`가 `plan`. 생성 코드의 테스트 `python3 -m unittest discover -s tests`(cwd `/tmp/dlc-r3-express`) → **10건 GREEN**.
- trace 파싱: `/tmp/dlc-r3-logs/express.jsonl`의 `result` 이벤트 24턴·$4.01569, `design.jsonl` 7턴·$1.8757725. 도구 사용 집계 express Bash 21회·Skill 1회·Write 0회, design Bash 6회. 질문 파일의 `## Q` 수 requirements 4·plan 4·design 6.
- R2 eval 기록 대조: `dlc/evals/results/` 3회 실행이 각각 CLI 2.1.269/18턴/$0.8879/점수 0.909(10/11), 2.1.270/18턴/$0.8929/점수 1.0(11/11), 2.1.270/18턴/$0.8027/점수 1.0(10/10). 설계 §8의 R2 문단 수치와 전부 일치한다.
- 인용 없는 지적은 내지 않았다. 심각도는 P1(설계 결정 위반·실행 불가), P2(모순·오도), P3(개선), P4(경미).

## 2. 설계 ↔ 구현 대응표

| 설계 항목(§절) | 설계가 정한 것 | 구현 위치 | 상태 | 비고 |
|---|---|---|---|---|
| §2 생명주기 범위 | 착수 전 검토 + 요구사항·설계 + 구현·테스트. Operation 제외 | `dlc.py:31` `STAGE_ORDER` 9개 | 일치 | 배포·운영 스테이지 없음 |
| §2 산출물·상태 위치 | `docs/dlc/<YYMMDD>-<slug>/` + `state.md` | `dlc.py:138` `dlc_root`, `dlc.py:465` 폴더 이름, `state-format.md:5-22` | 일치 | 커서 `docs/dlc/active`는 설계에 없음 → 지적 5 |
| §2 보조 스크립트 | python3 표준 라이브러리 단일 파일 | `dlc.py:20-27` import 8개 전부 stdlib | 일치 | 외부 패키지 0 |
| §2 기존 플러그인 의존 | 하드 의존 없음. craft 소프트 참조 | `dlc-build/SKILL.md:27-35`(원천 + 폴백 5줄), `dlc-plan:51`, `dlc-design:38` | 일치 | 없는 환경 폴백 존재 |
| §2 명시 호출 | Claude `disable-model-invocation: true`, Codex `policy.allow_implicit_invocation: false` | 10개 SKILL.md 프런트매터 + `agents/openai.yaml` 10개 | 일치 | 라우터·스테이지 모두 양쪽 있음 |
| §2 출력 언어 | 한국어 기본, 코드·식별자·경로 원문 | 각 스킬 말미 "출력 언어" 절(예: `dlc-build:96-98`) | 일치 | 10개 전부 |
| §2 플러그인·스킬 이름 | 플러그인 `dlc`, 스킬 전부 `dlc-` 접두 | `plugin.json` `"name": "dlc"`, 스킬 10개 이름 | 일치 | Codex 평면 네임스페이스 충돌 회피 |
| §3 craft:tdd | 구현 단계 테스트 규율의 원천으로 참조 | `dlc-build:27` "그 스킬 본문이 테스트 규율의 원천이다" | 일치 | 실측에서 실제 로드됨 → 지적 1 |
| §3 craft:implement | 쓸 수 있다고 안내만 | `dlc-build:37`, 절차 진입점 `:43` | 일치 | R3 실측 미수행(Fable 14번과 같음) |
| §3 craft:design-it-twice | 설계 단계 선택 참조 | `dlc-design:38` | 일치 | 없으면 대안 2개 자작 폴백 |
| §3 pr-reviewer | 검증 뒤 안내만 | `dlc-verify:51` "이 스킬이 대신 부르지 않고, PR을 만들지도 않는다" | 일치 | — |
| §3 document-generator | 불필요(고정 템플릿) | 참조 없음 | 일치 | — |
| §4 구성 | 라우터 1 + 스테이지 9 | `dlc/skills/` 아래 10개 디렉터리 | 일치 | — |
| §4 라우터 | 산출물 없음. 상태 읽고 안내, `--all`로 전체 진행 | `dlc/SKILL.md:38-49` 안내 모드·전체 진행 모드 | 일치 | "다른 작업으로 바꾸기" 절은 설계에 없음 → 지적 5 |
| §4 dlc-init | 작업 폴더, `state.md`, 스캔 결과 | `dlc.py:459-488` `cmd_init`, `dlc-init:52-54` | 일치 | `log.md`·`active`도 만든다(§4 표엔 없음) |
| §4 dlc-analyze | `docs/dlc/codebase.md`. brownfield만 | `dlc.py:50` `ARTIFACTS`, `dlc.py:229-234` `analyze_is_current` | 일치 | 지문 일치면 `next`가 건너뜀 |
| §4 dlc-intent | `intent.md`(문제·대상·성공 지표·범위·타당성) | `dlc.py:51`, `dlc-intent:41-77` 골격 | 일치 | H2 6개 동일 |
| §4 dlc-practices | `docs/dlc/practices.md` | `dlc.py:52`, `dlc-practices:49-85` | 일치 | 갱신 모드 규칙 `:21` |
| §4 dlc-requirements | `requirements.md`(의도 요약·FR/NFR·제약·범위 밖·가정) | `dlc.py:53-54`, `dlc-requirements:57-94` | 일치 | H2 6개 동일 |
| §4 dlc-design | `design.md`·`decisions.md`·`units.md` | `dlc.py:55-57`, `dlc-design:48-112` | 일치 | `decisions.md` 필수 절은 `## 결정`+가정(R3 확정) |
| §4 dlc-plan | `plan.md`. design 없으면 `units.md`도 | `dlc.py:58`, `dlc.py:436-438` `plan_owns_units`, `dlc-plan:24-29` | 일치 | — |
| §4 dlc-build | 코드 + `build/<unit>.md` | `dlc.py:61` `BUILD_UNIT_SECTIONS`, `dlc-build:55-88` | 일치 | 코드는 저장소 원래 위치 |
| §4 dlc-verify | `verify.md`(테스트·추적성·리뷰 발견) | `dlc.py:59`, `dlc-verify:53-86` | 일치 | 판정 절 추가로 H2 5개 |
| §4 프로파일 3개 | full·express·bugfix. init에서 사용자가 고름 | `dlc.py:36-42` `PROFILES`, `dlc-init:25`·`:40-46` | 일치 | 자동 감지 없음 |
| §4 bugfix | express와 같은 단계. 질문만 재현·회귀 중심 | `dlc.py:40-41`(스테이지 동일), `dlc-requirements:37-45` | 일치 | 한 번도 실행되지 않음 → 지적 8 |
| §4 depth 질문 수 | minimal 2~4, standard 5~8 | `protocol.md:20`, 각 스킬 질문 절 | 부분 | `dlc-plan:33`이 full 예외를, `dlc-analyze:45`가 하향 예외를 둠. §4:74는 단일 규칙으로만 적음 |
| §4 analyze 조건부 | 프로파일 무관, brownfield + 지문 불일치일 때만 | `dlc.py:242`, `dlc.py:479-480`(greenfield면 init에서 skipped) | 일치 | `start analyze --force`로 재실행 |
| §4 design 없는 프로파일의 유닛 표 | plan이 `units.md`를 만들고 `check plan`이 함께 검사 | `dlc.py:436-438`, `dlc.py:450-451` | 일치 | 유닛 표 형식은 프로파일 무관 하나 |
| §5 공유 스파인 위치 | 공유 문서는 라우터 스킬 안, 타 스킬은 `../dlc/references/...` | `dlc/skills/dlc/references/` 3개, 스테이지 스킬 머리말(예: `dlc-plan:14`) | 일치 | R1에서 `npx skills add` 복사 확인 |
| §5 디렉터리 트리 | `SKILL.md`·`references/`(3)·`scripts/`·`tests/` | 같음 | 부분 | `agents/openai.yaml`이 트리에 없음 → 지적 9 |
| §5 질문 파일 | A~E + `X. Other`, `[Answer]:` 태그 | `protocol.md:29-53`, `dlc.py:312-333` `check_questions` | 일치 | 번호 연속·요약 확인까지 기계 검사 |
| §5 승인 게이트 | 요약·검사 결과를 보이고 채팅 승인, `approve`로 기록, `state.md` 손 수정 금지 | `protocol.md:26`·`:59`, `dlc.py:204` 경고 주석, `dlc.py:579-584`(active + check 통과 전제) | 일치 | 침묵은 승인 아님(`protocol.md:57`) |
| §5 출처 태그 5종 | `[desc]`·`[Q<n>]`·`[practice]`·`[code:<경로>]`·`[assumption]` | `grounding.md:5-13` | 부분 | `[code:]`·`[assumption]` 정의가 R3에 확장됐고 §5:99가 옛 상태 → 지적 2 |
| §5 가정 절 필수 | 모든 산출물에 두고 없으면 `None.` | `grounding.md:20`, `dlc.py:283-284`(빈 절 검출) | 일치 | 10개 산출물 골격 전부 |
| §6 `init` | 폴더·`state.md` 생성, 워크스페이스 스캔 | `dlc.py:459-488` | 일치 | `--description` 추가 인자 |
| §6 `status` | 작업·프로파일·스테이지 상태 출력 | `dlc.py:491-506` | 일치 | 다음 스테이지도 함께 출력 |
| §6 `next` | 다음 스테이지와 스킬 이름, 완료면 `done` | `dlc.py:509-518` | 일치 | depth·profile·workspace 부가 출력 |
| §6 `check <stage>` | 필수 절·질문 답변·ID 연속성·ID 참조·유닛 커버리지·빌드 추적성·지문 | `dlc.py:429-454` + `274`·`312`·`349`·`370`·`391`·`411`·`402` | 일치 | R3 추가분(빌드 추적성)은 표 행만 셈(`dlc.py:421`) |
| §6 `start`·`approve`·`skip` | `next`가 가리키는 스테이지만, approve는 start + check 전제, skip은 pending·active만 | `dlc.py:539-545`·`574-591`·`594-608` | 일치 | skip은 사유 필수 |
| §6 `start analyze --force` | 지문 일치로 건너뛴 analyze 재실행 | `dlc.py:548-556` `require_forceable` | 일치 | analyze·brownfield·pending만 |
| §6 `note` | `log.md`에 한 줄 추가, 상태 변화 없음 | `dlc.py:611-615` | 일치 | — |
| §6 실행 환경 | python3 3.9+, stdlib, unittest로 검증 | `dlc.py:16`, 테스트 80건 GREEN | 일치 | `from __future__ import annotations`로 3.9 하한 충족 |
| §6 스크립트 없는 환경 폴백 | 각 스킬이 `protocol.md`의 수동 체크리스트를 따른다 | `protocol.md:62-69`, `dlc-init:54` | 일치 | 지문 검사 불가를 알리게 함 |
| §6 "판단은 코드에" 원칙 | 라우팅 판단을 프로즈에 두지 않는다 | `dlc.py` `next_stage`·`plan_owns_units` | 부분 | 유닛 집합 일치·실행 명령·판정 문자열은 프로즈만 → 지적 6·7 |
| §6 책임 경계 | 전이·다음 판정·승인 전 기계 검사 셋뿐 | 서브명령 8개 전부 이 셋 안 | 일치 | 세 책임 밖의 명령 없음. `--root`는 실행 위치 지정뿐 |
| §7 Claude Code | `/plugin install dlc@jongwan-plugins`, `/dlc:dlc-requirements` | `README.md:33-40`, `marketplace.json` name `jongwan-plugins` | 일치 | 마켓플레이스 등록 확인 |
| §7 Codex CLI | `npx skills add`, `$dlc-requirements`, openai.yaml | `README.md:42-50`, yaml 10개 | 일치 | README는 `--skill` 10개 열거 요구(§7에 없음) → 지적 11 |
| §7 Gemini CLI | 차단 설정 없음. description을 사람용 한 줄로 | 스킬 description 1~2문장 | 부분 | 실기기 확인은 §9 열린 질문으로 남음 |
| §7 Cursor | 미확인 | `README.md:42` 제목에 포함, `plugin.json`·marketplace 설명은 세 에이전트만 | 부분 | 표기 불일치 → 지적 11 |
| §8 R3 실측 수치 | 24턴·$4.02 / 7턴·$1.88, 질문 4·4·6, 유닛 2·4, check 4개 OK, 테스트 10건 | trace `result` 이벤트, `check` 재실행, 테스트 재실행 | 일치 | red 확인 4회도 기록과 일치(u1 1회 + u2 3회) |
| §8 R2 eval 수치 | 18턴 3회, $0.89·$0.89·$0.80, 10/11 → 11/11 → 10/10 | `evals/results/` 6개 파일 | 일치 | CLI 2.1.269 → 2.1.270 갱신도 일치 |
| §8 craft 로드 관찰 | "있었는데 읽지 않았다(결함)" | trace 이벤트 169·172·173 | 누락·오기 | 실제로 로드됨 → 지적 1 |
| §8 라운드 계획 R4 | Codex openai.yaml, README, evals, Codex 실행 | 앞 셋은 이미 구현 | 오기 | 지적 3 |
| §9 열린 질문 | 3건(Gemini 슬래시, npx 설치 방식, practices 병행) + codebase.md 태그 | §9:173-176 | 부분 | R3에서 생긴 미실측 항목 미반영 → 지적 8 |

## 3. 지적표

| 번호 | 심각도 | 파일:줄 또는 §절 | 지적 | 근거 인용 | 권장 조치 |
|---|---|---|---|---|---|
| 1 | P2 | 설계 §8:148 (`docs/design/2026-09-13-dlc-plugin-design.md`) | R3 실측 관찰이 trace와 반대다. 에이전트는 `craft:tdd`를 **Skill 도구로 실제 로드했다**. 원인 설명("스킬이 로드 방법을 안 적어 도달 불가능한 분기")도 반증된다 — 실행 당시 스킬 본문에는 로드 방법이 없었는데도 로드됐다 | 설계 §8:148 "헤드리스 세션의 init 이벤트 `skills` 목록(147개)에 `craft:tdd`가 있었지만 에이전트는 로드하지 않고 dlc-build의 폴백 5줄로 진행했다. 스킬이 '읽는다'고만 적고 로드 방법을 안 적은 탓이다". 반면 `/tmp/dlc-r3-logs/express.jsonl`은 plan 승인 직후 `{"name":"Skill","input":{"skill":"craft:tdd"}}`(순번 169) → 결과 `"Launching skill: craft:tdd"`(172) → 본문 주입 `"Base directory for this skill: …/craft/0.2.0/skills/tdd" … "# Test-Driven Development"`(173) → 첫 red 테스트 작성(179)을 남겼다. 같은 trace에 남은 실행 당시 `dlc-build` 본문은 "`craft:tdd`(또는 `tdd`)가 있으면 그 스킬 본문이 테스트 규율의 원천이다. 첫 유닛을 시작하기 전에 한 번 읽고 그대로 따른다"로 로드 방법이 없는 수정 전 문장이다. `express-prompt.md`에는 craft·tdd 언급이 없어 에이전트의 자발적 로드다 | §8 관찰을 "`craft:tdd`를 Skill 도구로 로드했다(순번 169·173). 로드 방법이 적혀 있지 않았는데도 Claude Code에서는 로드됐다"로 정정한다. Fable 1번의 조치(에이전트별 로드 방법 명시)는 Codex·Gemini 경로 때문에 유지할 값이 있으므로 되돌릴 필요는 없다. 다만 §8의 "폴백 자체는 동작했다"는 근거가 두 원천을 구분하지 못하므로 함께 지운다 — 기록의 정정이고 코드 변경의 철회가 아니다 |
| 2 | P2 | 설계 §5:99 ↔ `grounding.md:12-13` | 정본인 설계 문서의 출처 태그 절이 R3에 바뀐 `grounding.md`를 반영하지 않아 두 문서가 다른 규칙을 말한다. 태그 정의(실행·측정 결과 포함)와 `[assumption]` 예외(추적성·검증 표의 미확인 행) 둘 다 빠졌다 | §5:99 "`[code:<경로>]`는 저장소 파일을 직접 읽어 확인한 사실용이며 `codebase.md`처럼 코드가 근거인 산출물에서 쓴다(R2 추가). 근거 없는 내용은 `## 가정과 열린 질문` 절에만 둔다" / `grounding.md:12` "또는 그 파일을 실행·측정해 얻은 결과(테스트 실행 결과, 소요 시간 등. 명령을 함께 적는다) … build·verify 기록에서 쓴다" / `grounding.md:13` "예외 하나: `build/<unit>.md`·`verify.md`의 추적성·검증 표에서 테스트로 확인하지 못한 행('미확인')은 표에서 빼지 않고 이 태그를 달되" | §5:99에 R3 변경 두 줄을 반영한다. Fable 2·8번 조치가 참조 문서만 고치고 설계 문서를 남긴 결과다 |
| 3 | P2 | 설계 §8:135 (R4 행) | R4로 적힌 네 항목 중 셋이 R1~R3에 앞당겨 들어와 있어, 남은 일을 오도한다 | §8:135 "R4 \| Codex `openai.yaml`, README, evals, Codex에서 1회 실행". 구현에는 스킬 10개 전부 `agents/openai.yaml`(`policy.allow_implicit_invocation: false`), `dlc/README.md` 61줄, `dlc/evals/express-requirements/case.yaml` + 실행 결과 3회분이 이미 있다 | R4 행을 실제 잔여로 다시 쓴다: Codex·Gemini 실기기 1회 실행, eval suite를 라우터·스테이지 스킬까지 확장, 기존 `evals.json`(skill-creator 형식) 병행 여부 결정, §8:149의 Bash heredoc 앵커 반영 |
| 4 | P3 | 설계 §8:147 ↔ `express.jsonl` | 라우터가 다음 스킬 파일을 "Read"했다고 적었으나 실제 채널은 Bash `cat`이고 경로도 상대 경로가 아닌 절대 경로였다. §8:149가 Write에 대해 이미 기록한 교훈("권한 우회 모드에서 Bash 우선")의 두 번째 사례이며, Read 입력에 앵커링한 R4 grader를 무력화한다 | §8:147 "네 번 모두 `next` 재실행 → `../dlc-<stage>/SKILL.md` Read → 절차 수행" / trace의 도구 집계는 Bash 21회·Skill 1회이고 Read는 0회다. 스킬 파일은 `cat $S/dlc-init/SKILL.md` 형태로 5개(init·requirements·plan·build·verify) 읽혔다 / §8:149 "**Write 도구 호출 0회.** … 두 실행 모두 파일을 Bash heredoc으로 썼다" | §8:147을 "`<skills>/dlc-<stage>/SKILL.md`를 Bash `cat`으로 읽었다(Read 0회)"로 정정하고, §8:149의 앵커 결정에 읽기 쪽도 포함한다 |
| 5 | P3 | 설계 §2:25·§6:107 ↔ `state-format.md:7`, `dlc/SKILL.md:53` | 구현의 활성 작업 커서 `docs/dlc/active`가 설계 문서에 한 번도 나오지 않는다. 모든 명령의 전제이고, 커밋되지 않아도 되는 유일한 상태이며, 에이전트가 손으로 쓰는 유일한 예외라 설계 결정으로 기록할 값이 있다 | `state-format.md:7` "active — 활성 작업 폴더 이름 한 줄. 사용자별 커서라 .gitignore 에 넣어도 된다" / `dlc/SKILL.md:53` "고른 이름을 `docs/dlc/active`에 한 줄로 쓴다. 이것이 `active` 파일을 직접 쓰는 유일한 경우다" / `dlc.py:483` `cursor_path(root).write_text(name + "\n", …)`, `dlc.py:153-160` `no_active_message` / 설계 §2:25는 위치를 "`docs/dlc/<YYMMDD>-<slug>/` + `state.md`"로만, §6:107은 init 역할을 "작업 폴더와 `state.md` 생성"으로만 적는다 | §2 또는 §6에 커서 한 줄을 추가한다. §2:25의 근거("커밋 대상이라 세션·에이전트 무관하게 재개 가능")와의 관계도 적는다 — 커서를 커밋하지 않으면 다른 PC의 첫 재개에서 라우터의 "다른 작업으로 바꾸기" 분기를 반드시 지난다 |
| 6 | P3 | `dlc-plan/SKILL.md:109`·`:111`, `dlc-build/SKILL.md:92`, `dlc.py:429-454` | 기계로 검사할 수 있는 plan 규칙 둘이 프로즈에만 있고 `check plan`이 보지 않는다. build 완료 기준이 그 규칙을 전제로 삼으므로, 유닛 집합이 어긋나면 `check build`는 units.md 기준으로만 돌아 조용히 통과한다. 설계 §6:103의 "판단이 프로즈에 있으면 실행마다 흔들린다"에 걸린다 | `dlc-plan:109` "`## 유닛 순서` 표의 unit 집합은 units.md의 유닛 집합과 같아야 한다" / `:111` "실행 명령이 없으면 build가 테스트를 돌릴 수 없다. 반드시 한 줄 둔다" / `dlc-build:92` "units.md의 모든 유닛에 `build/<unit>.md`가 있고(plan.md 순서 표의 유닛 집합은 units.md와 같아야 한다 — dlc-plan의 규칙)" / `check_stage`의 plan 분기는 필수 절·ID 참조·(plan이 만들 때의) units 커버리지·질문 파일뿐이다 | `check plan`에 유닛 집합 일치와 실행 명령 존재 두 검사를 추가하거나, 설계 §6에 "이 둘은 의도적으로 기계 검사 밖에 둔다"를 명시한다 |
| 7 | P3 | `dlc-verify/SKILL.md:89`·`:95`, `dlc.py:429-454`·`574-591` | 마지막 게이트의 핵심 조건인 판정 문자열이 기계 검사 밖이다. `## 판정`에 `반려`라고 적힌 `verify.md`로도 `approve verify`가 통과해 작업이 `done`이 된다 | `dlc-verify:89` "`## 판정` 첫 단어는 `승인`, `조건부 승인`, `반려` 중 하나다" / `:95` "판정이 `승인` 또는 `조건부 승인`이다. `반려`는 승인 게이트로 가지 않는다" / `check_stage`의 verify 분기는 `check_sections` + `check_references`뿐이고 `cmd_approve`는 그 결과만 본다 | `check verify`에 판정 첫 단어 검사(반려면 실패)를 추가한다. 회귀 테스트 1건을 함께 둔다 |
| 8 | P3 | 설계 §9:173-176 | R3에서 새로 드러난 미실측 항목이 열린 질문에 들어오지 않았다. 넷이다: bugfix 프로파일은 R1~R3 어느 실행에도 없었고, 라우터의 "여기까지" 중단, 다음 세션 재개 경로(build·verify의 `active` 재개), R4 evals의 앵커 결정이 모두 미결이다 | §9에는 Gemini 슬래시·`npx skills add`·practices 병행·codebase.md 태그 네 항목만 있다 / bugfix는 `dlc.py:40-41`에서 express와 스테이지·depth가 같고 차이는 `dlc-requirements:37-45`의 질문 주제뿐인데 실행 기록이 없다 / §8:147 "사용자의 '여기까지' 중단은 이번에 실측하지 않았다" / `dlc-build:53`·`dlc-verify:49`가 규정한 재개 경로의 실행 기록 없음 / §8:149 "R4 evals는 … Bash heredoc … 도 앵커로 허용해야 한다" | §9에 네 항목을 추가한다. bugfix는 질문 주제 차이만 검증하면 되므로 requirements 1스테이지 실행으로 족하다 |
| 9 | P4 | 설계 §5:82-93 | 공유 스파인 트리에 `agents/openai.yaml`이 없다. 라우터 스킬에도 이 파일이 있어 실제 배치와 다르다 | §5의 트리는 `SKILL.md`·`references/`(3개)·`scripts/dlc.py`·`tests/test_dlc.py`만 그린다 / `dlc/skills/dlc/agents/openai.yaml` 존재. §7:126이 파일의 존재 이유를 따로 설명한다 | 트리에 한 줄 추가 |
| 10 | P4 | `dlc-build/SKILL.md:27`, `dlc-design/SKILL.md:38`, `dlc-plan/SKILL.md:51` | 괄호 설명이 과한 단정이다. Claude Code는 스킬을 로드할 때 절대 경로를 함께 준다. 모르는 것은 *로드하기 전 다른 플러그인의 캐시 경로*이지 스킬 경로 일반이 아니다 | `dlc-build:27` "(플러그인 스킬은 파일 경로를 알 수 없어 Read로는 읽지 못한다)" / trace 순번 173은 로드 결과 첫 줄이 `"Base directory for this skill: /Users/…/plugins/cache/jongwan-plugins/craft/0.2.0/skills/tdd"`임을 보인다. 같은 실행에서 에이전트는 자기 스킬 경로를 `S=…/dlc/skills`로 잡아 Bash로 썼다 | "로드하기 전에는 다른 플러그인의 설치 경로를 알 수 없다"로 좁힌다 |
| 11 | P4 | `README.md:22`·`:42`, `plugin.json` description, `marketplace.json` dlc 항목, 설계 §7:124 | 같은 사실을 세 곳이 다르게 말한다. Cursor는 설계 §7에 "미확인"으로 한 행이 있고 README 제목에는 지원처로 올라 있으나 `plugin.json`·marketplace 설명에는 "Claude Code·Codex·Gemini CLI 공용"만 있다. README의 프로파일 요약도 조건부 analyze를 "9단계 전부"로 뭉갠다 | `README.md:42` "### Codex CLI, Gemini CLI, Cursor" / 설계 §7:124 "Cursor \| 위와 같음 \| 슬래시 \| 미확인" / `marketplace.json` "Claude Code·Codex·Gemini CLI 공용" / `README.md:22` "`full`(9단계 전부, 질문 5~8개), `express`(init·analyze·requirements·plan·build·verify …)" — 설계 §4:70은 `(analyze)` 괄호로 조건부임을 표시한다 | README 제목에 Cursor 미확인 표시를 붙이거나 세 곳의 표기를 맞춘다. 프로파일 요약에 괄호 표기를 쓴다 |
| 12 | P4 | 설계 §9:174-176, §8:161 | 두 가지 경미한 기록 문제. 해소된 열린 질문 셋 중 하나만 취소선이라 남은 둘이 아직 열린 것처럼 보인다. 그리고 R2가 확정한 "`tool_used: Skill`은 발동 지표로 쓸 수 없다"는 R3 trace에서 Skill 호출이 1회(대상 `craft:tdd`) 있었으므로, R4에서 그 지표를 쓰면 dlc 스킬 발동이 아닌 호출에 매치될 여지가 남는다 | §9:174는 `~~취소선~~` + "R1에서 확인", §9:175-176은 본문에 "R2에서 … 해소했다"만 / §8:161 "Skill 도구 호출은 0회" / R3 express trace의 Skill 1회는 `{"skill":"craft:tdd"}` | 해소 표기를 통일한다. §8:161에 "다른 스킬의 Skill 호출과 구분되지 않는다"를 한 구절 덧붙인다 |

## 4. 요약

P1 0건, P2 3건, P3 5건, P4 4건 — 총 12건. Fable 리뷰와 중복되는 지적은 없다(1번은 Fable 1번의 근거를 정정하는 것이고, 조치 자체를 되돌리라는 말은 아니다).

전체 판정: 설계 문서가 확정한 결정은 코드와 스킬에 거의 그대로 들어와 있다. §2의 결정 일곱 개, §4의 스킬 열 개와 프로파일 세 개, §5의 질문 파일·승인 게이트·가정 절 필수, §6의 명령 여덟 개와 세 책임 경계, §7의 명시 호출 강제는 전부 확인됐고 `dlc.py`가 세 책임 밖의 일을 하지도 않는다. 설계 위반이나 실행 불가는 없다. 결함은 반대 방향에 몰려 있다 — **구현과 참조 문서가 R3에서 앞으로 나갔는데 정본인 설계 문서가 따라오지 않았다.** 출처 태그 절(§5), 라운드 계획의 R4 행(§8), 열린 질문(§9)이 그렇고, 실측 문단은 수치는 전부 정확하지만 `craft:tdd` 관찰 하나가 trace와 반대로 적혀 그 위에서 원인 진단까지 틀렸다. 이 한 건이 이번 리뷰에서 가장 값이 큰 발견이다. 잘못된 원인 기록은 다음 라운드에서 같은 결론을 재생산한다.

R4로 넘길 항목:

1. 설계 문서 정정 네 곳 — §8의 craft 로드 관찰과 Read/Bash 채널(지적 1·4), §5의 출처 태그(지적 2), §8의 R4 행(지적 3), §9의 열린 질문 네 항목(지적 8).
2. `dlc.py` 검사 추가 두 건 — `check plan`의 유닛 집합·실행 명령(지적 6), `check verify`의 판정 문자열(지적 7). 각각 회귀 테스트 1건.
3. 설계에 커서 `docs/dlc/active` 기록(지적 5).
4. bugfix 프로파일 1회 실행(requirements 스테이지만으로 충분) — 세 프로파일 중 유일한 미실행.
5. Codex·Gemini 실기기 실행과 eval suite 확장. 앵커는 Write와 Bash heredoc 양쪽, 읽기 쪽도 Read와 `cat` 양쪽을 받아야 한다.
6. 문서 표기 정리 — Cursor 취급, 프로파일 요약의 조건부 analyze, 스파인 트리의 `agents/openai.yaml`(지적 9·11·12).
