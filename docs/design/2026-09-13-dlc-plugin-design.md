# dlc 플러그인 설계 (2026-09-13)

AI-DLC(awslabs/aidlc-workflows)의 방법론을 에이전트 종속 없이 쓸 수 있는 명시 호출형 스킬셋으로 다시 만든다. 이 문서는 구현 전에 확정한 설계 결정의 기록이다.

## 1. 목표와 비목표

**목표**

- 한 저장소의 `SKILL.md` 묶음이 Claude Code, Codex CLI, Gemini CLI, Cursor에서 그대로 동작한다. Agent Skills 개방 표준(agentskills.io) 형식만 쓴다.
- 스킬은 개발자가 이름을 쳐서 호출할 때만 실행된다(Matt Pocock의 user-invoked 원칙). 대화 중 자동 트리거되지 않는다.
- 단계별 스킬을 따로 쓸 수도 있고, 라우터 스킬 하나로 전체를 순서대로 돌 수도 있다.
- 산출물과 진행 상태를 프로젝트 저장소 안에 남겨 세션·에이전트·PC가 바뀌어도 이어간다.

**비목표**

- 배포·운영 단계(AI-DLC Operation phase)는 이번 범위에서 뺀다. 나중에 스테이지 스킬을 추가하는 방식으로 확장한다.
- Claude 전용 기능(sub agent, hooks, AskUserQuestion, statusline)에 의존하지 않는다. 질문은 파일 기반 Q&A로, 승인은 채팅 응답 + 스크립트 기록으로 처리한다.
- AI-DLC의 TypeScript 엔진, 95종 감사 이벤트, 센서 6종, 스웜은 옮기지 않는다.

## 2. 확정 결정

| 항목 | 결정 | 근거 |
|---|---|---|
| 생명주기 범위 | 착수 전 검토 + 요구사항·설계 + 구현·테스트 | 사용자 결정(2026-09-13). AI-DLC의 Ideation·Inception·Construction에 해당 |
| 산출물·상태 위치 | 프로젝트 저장소 `docs/dlc/<YYMMDD>-<slug>/` + `state.md` | 사용자 결정. 커밋 대상이라 세션·에이전트 무관하게 재개 가능 |
| 활성 작업 커서 | `docs/dlc/active` 한 줄(작업 폴더 이름). `dlc.py init`이 쓴다. 에이전트가 손으로 쓰는 유일한 예외는 라우터의 "다른 작업으로 바꾸기"(R4 기록, R3 Opus 리뷰 5) | 사용자별 커서라 `.gitignore`에 넣어도 된다. 커밋하지 않으면 다른 PC의 첫 재개에서 라우터가 `docs/dlc/` 작업 폴더 목록을 보이고 고르게 하는 분기를 반드시 지난다. 산출물·`state.md`가 커밋되므로 재개 자체는 막히지 않는다 |
| 보조 스크립트 | python3 표준 라이브러리 단일 파일 `dlc.py` | llm-wiki 선례, 세 에이전트 모두 셸 실행 가능, 외부 패키지 없음. macOS bash 3.2는 부적합 |
| 기존 플러그인 의존 | 하드 의존 없음. craft:tdd·design-it-twice 소프트 참조 | 아래 3절 |
| 명시 호출 | Claude `disable-model-invocation: true`, Codex `agents/openai.yaml`의 `policy.allow_implicit_invocation: false` | Gemini CLI는 자동 활성 차단 설정이 문서에 없음. 제약으로 기록 |
| 출력 언어 | 한국어 기본, 코드·식별자·경로 원문 | 저장소 관례 |
| 플러그인 이름 | `dlc` | 짧고 슬래시 명령이 읽기 쉬움. 스킬 이름은 전부 `dlc-` 접두로 Codex의 평면 네임스페이스 충돌을 피함 |

## 3. 기존 플러그인 분석과 의존 판단

| 대상 | 상태 (2026-09-13) | 판단 |
|---|---|---|
| craft:tdd | upstream matt-pocock v1.2.3(2026-08-05) 반영. 상위 저장소 최신 태그도 v1.2.3 | 현행. 구현 단계의 테스트 규율 원천으로 참조한다 |
| craft:implement | 2026-07-17 포크, 이후 갱신 기록 없음. `disable-model-invocation: true` | 명시 호출형이라 다른 스킬이 부를 수 없다. 구현 단계에서 사용자에게 "이 스킬을 쓸 수 있다"고 안내만 한다 |
| craft:design-it-twice | 현행, 모델 호출형 | 설계 단계에서 인터페이스 대안이 쟁점일 때 선택 참조 |
| craft:diagnosing-bugs, triage | 현행 | 생명주기 밖. 참조하지 않는다 |
| pr-reviewer | GitHub PR과 gh 전제 | 검증 단계 뒤 "PR을 올렸다면 쓸 수 있다"고 안내만 |
| document-generator | 현행 | 산출물은 고정 템플릿이라 불필요 |

원칙: 규칙의 원천은 한 곳에 둔다. 구현 단계 스킬은 seam 합의·통합테스트 예산·red-green 게이트만 자기 절차로 갖고, 테스트 규율 본문은 craft:tdd를 가리킨다. craft가 없는 환경을 위한 축약 규칙 5줄은 폴백으로 둔다. craft 스킬들이 같은 "(폴백)" 패턴을 이미 쓴다.

## 4. 스킬 구성

라우터 1개 + 스테이지 9개. AI-DLC의 26개 스테이지(초기화 3 + Ideation 7 + Inception 9 + Construction 7)를 실무 단위로 압축했다. Operation 7개는 범위 밖이다.

| 스킬 | AI-DLC 대응 | 산출물 |
|---|---|---|
| `dlc` (라우터) | 오케스트레이터 | 없음. 상태를 읽고 다음 스킬을 안내하거나, `--all`로 전체를 순서대로 진행 |
| `dlc-init` | workspace-scaffold·detection·state-init | 작업 폴더, `state.md`, 워크스페이스 스캔 결과 |
| `dlc-analyze` | reverse-engineering | `docs/dlc/codebase.md` (작업 단위 밖, 프로젝트 공유). 기존 코드가 있을 때만 실행 |
| `dlc-intent` | intent-capture·feasibility·scope-definition | `intent.md` (문제, 대상, 성공 지표, 범위 안팎, 타당성) |
| `dlc-practices` | practices-discovery | `docs/dlc/practices.md` (작업 단위 밖, 프로젝트 공유) |
| `dlc-requirements` | requirements-analysis·user-stories | `requirements.md` (의도 요약, FR/NFR ID, 제약, 범위 밖, 가정) |
| `dlc-design` | domain-design·units-generation·contract-design | `design.md`, `decisions.md`(ADR), `units.md`(유닛 DAG) |
| `dlc-plan` | delivery-planning·code-generation-plan | `plan.md` (유닛 순서, seam, 테스트 예산, 완료 정의). design이 없는 프로파일이면 `units.md`도 |
| `dlc-build` | code-generation | 코드 + `build/<unit>.md` (변경 파일, 추적성) |
| `dlc-verify` | build-and-test + 리뷰 | `verify.md` (테스트 결과, 추적성 검사, 리뷰 발견) |

**프로파일**은 이번 작업에 어느 스테이지를 돌리고 스테이지당 질문을 몇 개 할지 미리 묶어 둔 설정이다. AI-DLC의 scope(엔진 용어)·workflow profile(사용자 용어)과 같은 개념이다. 차이는 고르는 방식이다. AI-DLC는 프롬프트의 키워드로 자동 감지하지만, 이 스킬셋은 명시 호출 철학에 따라 `dlc-init`에서 사용자가 직접 고른다. AI-DLC의 11개 중 배포·운영 관련은 범위 밖이고, classic·feature·enterprise·mvp는 이번 범위에서는 모두 "전부 돌기"로 같아지므로 full 하나로 합쳐진다.

`dlc-analyze`는 프로파일과 무관하게 워크스페이스 스캔 결과가 brownfield일 때만 실행되는 조건부 스테이지다. `docs/dlc/codebase.md`가 이미 있고 스캔 지문이 같으면 건너뛴다.

프로파일은 셋으로 확정했다(사용자 결정 2026-09-13). `(analyze)`는 brownfield일 때만 끼어드는 조건부 단계다.

| 프로파일 | 실행 스테이지 | depth | 용도 |
|---|---|---|---|
| `full` | init → (analyze) → intent → practices → requirements → design → plan → build → verify | standard | 새 기능, 새 프로젝트 |
| `express` | init → (analyze) → requirements → plan → build → verify | minimal | 요구가 이미 명확한 작은 기능 |
| `bugfix` | express와 같은 단계. requirements 질문이 재현 조건·기대 동작·회귀 테스트 중심 | minimal | 알려진 결함 수정 |

depth는 스테이지당 질문 수(minimal 2~4, standard 5~8)와 산출물 상세도를 정한다.

**design이 없는 프로파일의 유닛 표.** express·bugfix는 design을 건너뛰지만 build는 유닛 단위로 진행하므로 유닛 표가 필요하다. 이 경우 **plan 스테이지가 `plan.md`와 함께 `units.md`를 만든다**(1라운드 리뷰 반영, 사용자 결정 2026-09-13). `dlc.py check plan`은 프로파일에 design이 없거나 design을 건너뛰었을 때만 `units.md`의 필수 절과 요구사항 커버리지를 함께 검사한다. 유닛 표의 형식과 build 검사는 프로파일과 무관하게 하나다.

## 5. 공유 스파인

스테이지 스킬과 라우터가 함께 읽는 것은 라우터 스킬 `dlc/` 안에 둔다. 다른 스킬은 `../dlc/references/...`로 가리킨다. Claude 플러그인(`<plugin>/skills/<name>/`)과 `npx skills add`(`~/.agents/skills/<name>/`) 둘 다 스킬 디렉터리가 형제로 놓이므로 상대 경로가 같다. 이 가정은 1라운드에서 실제 설치로 검증한다.

```
dlc/
  SKILL.md                      라우터
  agents/openai.yaml            Codex 전용 메타(allow_implicit_invocation: false). 스테이지 스킬 9개에도 같은 파일이 있다
  references/
    protocol.md                 스테이지 공통 절차: 질문 파일 형식, 답변 검사, 요약 확인, 승인 게이트
    state-format.md             state.md 형식과 상태 기호
    grounding.md                산출물 출처 태그 규칙, 가정 절 필수
  scripts/
    dlc.py                      상태·검사 스크립트
  tests/
    test_dlc.py
```

**질문 파일.** AI-DLC 형식을 그대로 쓴다. A~E 선택지 + `X. Other`, `[Answer]:` 태그. 사용자는 채팅으로 답하거나 파일을 직접 고친다. 이 형식은 특정 도구에 의존하지 않아 이식성의 핵심이다.

**승인 게이트.** 스테이지 끝에 에이전트가 산출물 요약과 검사 결과를 보이고 채팅으로 승인을 묻는다. 사용자가 승인하면 `dlc.py approve <stage>`로 상태를 기록한다. 에이전트가 `state.md`를 손으로 고치는 것은 금지한다.

**출처 태그.** 산출물의 실질 문단·표 행은 `[desc]`, `[Q<n>]`, `[practice]`, `[code:<경로>]`, `[assumption]` 중 하나를 단다. `[code:<경로>]`는 저장소 파일을 직접 읽어 확인한 사실, 또는 그 파일을 실행·측정해 얻은 결과(명령을 함께 적는다)용이며 `codebase.md`처럼 코드가 근거인 산출물과 build·verify 기록에서 쓴다(R2 추가, R3에 실행·측정 결과 포함). 근거 없는 내용은 `## 가정과 열린 질문` 절에만 둔다. 예외 하나(R3): `build/<unit>.md`·`verify.md`의 추적성·검증 표에서 테스트로 확인하지 못한 행은 표에서 빼지 않고 `[assumption]`을 달되 같은 내용을 가정 절에도 둔다. 이 절은 필수이며 없으면 `None.`을 쓴다.

## 6. dlc.py 책임

세 가지로 제한한다. 라우팅 판단이 프로즈에 있으면 실행마다 흔들리므로 코드에 둔다.

| 명령 | 역할 |
|---|---|
| `init --profile <p> --slug <s>` | 작업 폴더와 `state.md`·`log.md` 생성, 커서 `docs/dlc/active` 기록, 워크스페이스 스캔(greenfield/brownfield, 언어·빌드 도구 감지) |
| `status` | 현재 작업, 프로파일, 스테이지별 상태 출력 |
| `next` | 다음 실행 스테이지와 호출할 스킬 이름 출력. 완료면 `done` |
| `check <stage>` | 산출물 필수 절 존재, 질문 파일 미답변·번호 연속, FR/NFR ID 연속성, 설계·계획·빌드·검증의 ID 참조, 유닛 커버리지, 빌드 추적성 커버리지(모든 최상위 FR/NFR이 어느 `build/<unit>.md`의 추적성에든 있음, R3 추가), plan의 유닛 순서 표 유닛 집합 = units.md 유닛 집합·`실행 명령:` 줄 존재, verify의 `## 판정` 첫 단어(`반려`면 실패)(R4 추가, R3 Opus 리뷰 6·7), codebase.md 지문 검사. 실패 목록 출력 |
| `start`, `approve`, `skip --reason` | 상태 전이 기록. `start`·`approve`는 `next`가 가리키는 스테이지만, `approve`는 `start` 후 `check` 통과가 전제. `skip`은 pending·active만 |
| `start analyze --force` | 지문 일치로 건너뛴 analyze를 다시 돌린다 |
| `note <stage> <text>` | `log.md`에 결정·메모 한 줄 추가 (상태 변화 없음) |

python3 3.9 이상, 표준 라이브러리만 쓴다. `python3 -m unittest discover -s dlc/skills/dlc/tests`로 검증한다. 스크립트가 없는 환경에서는 각 스킬이 `references/protocol.md`의 수동 체크리스트를 따르도록 폴백을 둔다.

## 7. 에이전트별 호출과 제약

| 에이전트 | 설치 | 호출 | 명시 호출 강제 | 실측(R4, 2026-09-13) |
|---|---|---|---|---|
| Claude Code 2.1.270 | `/plugin install dlc@jongwan-plugins` | `/dlc:dlc-requirements` | `disable-model-invocation: true` | R2~R4 전 스테이지 + eval suite |
| Codex CLI 0.154.0 | `npx skills add JK-Kim4/claude-plugins --skill … --agent codex -y` → 프로젝트 `.agents/skills/` 복사 | `$dlc-requirements` | `agents/openai.yaml`의 `policy.allow_implicit_invocation: false` | `$dlc-init`(bugfix) → `$dlc-requirements` 질문 파일 생성·대기까지 확인. 스크립트는 `.agents/skills/dlc/scripts/dlc.py` 프로젝트 상대 경로로 해석됨(형제 경로 가정 성립). 답변 이후 턴은 계정 사용량 한도로 중단(아래 §8) |
| Gemini CLI 0.34.0 | 같은 명령, `--agent gemini-cli` | 슬래시 없음. 이름을 말하면 모델이 `activate_skill` 호출(확인 프롬프트) | 차단 설정 없음. description을 사람용 한 줄로 줄여 오발동을 낮춘다 | `gemini skills list`가 `.agents/skills/`의 10개를 발견. 모델 호출은 개인 계정 티어 종료로 미실측 |
| Cursor | 같은 명령 | 슬래시 | 미확인 | 미실측 |

Codex의 `agents/openai.yaml`은 Agent Skills 표준 밖의 확장이지만 다른 에이전트는 무시하므로 함께 넣는다.

## 8. 구현 라운드

| 라운드 | 내용 | 검증 | 완료 커밋 |
|---|---|---|---|
| R1 | 플러그인 골격, 마켓플레이스 등록, 라우터 스킬, 공유 참조 3개, `dlc.py` + 테스트 | unittest GREEN, `claude plugin validate`, `npx skills add` 로컬 설치로 형제 경로 가정 확인 | `f0852a6`(골격) → 리뷰 반영 `341b878`~`573910e`, 이슈 #1 |
| R2 | 스테이지 스킬 5개: init, analyze, intent, practices, requirements | 빈 디렉터리에서 Claude로 express 프로파일 1회 실행 — 수동 대신 `claude plugin eval` 케이스 1건(`dlc/evals/`)으로 수행해 기록을 남기고, 명시 호출 스킬이 eval 프롬프트에서 발동되는지 확정. 기존 코드가 있는 디렉터리에서 analyze 1회 실행 | `1dae4d1` → 리뷰 반영 `e939a4d`·`34698c2`, 이슈 #2 |
| R3 | 스테이지 스킬 4개: design, plan, build, verify. `dlc.py check build`에 빌드 추적성 커버리지 추가, decisions.md 필수 절(`## 결정`·가정) 확정, 골격 비교 테스트를 `BUILD_UNIT_SECTIONS`·plan의 units.md까지 확장(R2 리뷰 U16) | 빈 디렉터리에서 라우터 `--all`로 express 프로파일 init→verify 완주(헤드리스). full 프로파일 픽스처 위에서 design 1회 실행. 결과는 아래 | `933aa38` → 리뷰 `e8c780d`·`d1e8eb3`, 이슈 #3 |
| R4 | Codex·Gemini CLI 실기기 1회 실행, README의 설치·호출·제약 표를 실측으로 확정, eval suite를 라우터·스테이지 스킬로 확장(기존 `evals.json` 병행 여부 결정), R3 Opus 리뷰가 넘긴 항목(이슈 #4 본문 "R3 이월 항목"), 버전 확정, main PR. `agents/openai.yaml` 10개·README·eval 케이스 1건은 R2·R3에서 이미 만들었다 | Codex에서 `$dlc-init`→`$dlc-requirements` 확인. evals 8 케이스 `--threshold 1.0`. 앵커는 Write와 Bash heredoc 양쪽(R3 관찰). 결과는 아래 "R4 실측 결과" | `9bdd578`(검사·프로즈) · `a42c44c`(evals·실측·README·설계), 이슈 #4. 잔여 실측 2건은 후속 커밋 |

**R3 실측 결과 (2026-09-13).** 두 실행 모두 `claude -p --plugin-dir ./dlc --dangerously-skip-permissions --output-format stream-json`(2.1.270), 빈 임시 디렉터리, 답변·승인 사전 제공. eval 러너가 아니라 헤드리스 CLI를 쓴 것은 다중 스테이지 한 프롬프트 실행에 러너의 이점(scaffold·grader)이 필요 없었기 때문이며, trace는 stream-json으로 남겼다.

| 실행 | 프롬프트 | 결과 |
|---|---|---|
| express 완주 | `/dlc:dlc --all express wcl <설명>` + requirements·plan 답변, 전 스테이지 사전 승인, build "전부 진행" | 24턴, 약 $4.02. init→requirements(질문 4)→plan(질문 4, units.md 유닛 2개)→build(유닛 2개, 코드 `wcl/` 3파일·테스트 `tests/` 2파일, red 확인 4회 기록)→verify. `status` 전부 done, `next`가 `done`, `check` 4개 OK, 생성 테스트 10건 GREEN |
| full design | 픽스처(practices·requirements 승인, intent skip) 위에서 `/dlc:dlc-design` + 답변 6개 | 7턴, 약 $1.88. 질문 6개(standard 5~8 안), ADR 1건에 대안 3개·기각 이유, 유닛 4개가 FR/NFR 전부를 덮음, `check design` OK, 승인 |

관찰:

- **verify의 반려 경로가 실제로 돌았다.** 1차 검증이 P1 1건(`except OSError`만 잡아 UTF-8이 아닌 파일에서 크래시)을 재현 테스트와 함께 찾아 판정 `반려`로 기록하고, 프롬프트의 "반려면 이 세션에서 고친다"에 따라 seam 테스트를 red로 확인한 뒤 수정, `build/u2-cli.md` 갱신, `note verify` 2줄, 재검증 통과 후 승인. log.md에 `start → note → note → approve` 순서가 남았다.
- **라우터 `--all`이 스테이지마다 멈추고 승인 뒤 다음 스킬 파일을 읽어 이어갔다.** requirements→plan→build→verify 네 번 모두 `next` 재실행 → `<skills>/dlc-<stage>/SKILL.md`를 Bash `cat`(절대 경로)으로 읽음(Read 도구 호출 0회, R3 Opus 리뷰 4로 정정) → 절차 수행. 사용자의 "여기까지" 중단은 이번에 실측하지 않았다.
- **craft:tdd를 Skill 도구로 로드했다.** 헤드리스 세션의 init 이벤트 `skills` 목록(147개)에 `craft:tdd`가 있었고, 에이전트는 plan 승인 직후 Skill 도구로 그것을 호출해(trace 순번 169 호출, 173 본문 주입) 첫 red 테스트 전에 본문을 읽었다. 실행 당시 dlc-build 본문에는 로드 방법이 적혀 있지 않았는데도 Claude Code에서는 로드됐다. Fable 리뷰 1번은 파일 Read만 세어 "읽지 않았다"고 했고 이 문단의 첫 기록도 그것을 따랐다가 Opus 리뷰 1번(trace 순번 인용)으로 정정했다. dlc-build·dlc-plan·dlc-design에 에이전트별 로드 방법을 명시한 조치는 Codex·Gemini(`npx skills add` 설치, Skill 도구 없음) 경로 때문에 유지한다. 유닛 기록에는 red 확인 내역과 "red 없이 통과한 테스트"가 구분돼 적혔다.
- **Write 도구 호출 0회.** `--dangerously-skip-permissions`로 돌린 두 실행 모두 파일을 Bash heredoc으로 썼다(Claude Code가 권한 우회 모드에서 Bash 우선을 안내한다). R2에서 확정한 "Write 입력 앵커" grader는 이 모드에서는 매치되지 않으므로, R4 evals는 러너 기본 권한 모드(R2 실행과 같음)를 유지하거나 Bash heredoc(`cat > <경로> <<'EOF'`)도 앵커로 허용해야 한다. 읽기 쪽도 같다 — 스킬 파일은 Read가 아니라 Bash `cat`으로 읽혔으므로 읽기 앵커는 Read와 `cat` 양쪽을 받는다.
- dlc-build의 "`craft:implement`를 쓸 수 있다고 한 번 안내한다"도 수행되지 않았다(리뷰 14번). 안내 시점을 첫 유닛 1단계 앞으로 옮겼다.
- 승인이 사전 제공된 자동 실행이라 plan의 start→approve 간격이 10초였다(R2 관찰 (a)와 같은 압축). 전이 순서는 지켜졌다.
- 두 실행 자체는 스크립트 오류 없이 끝났다. 실행 뒤 Fable 리뷰(`docs/review/2026-09-13-dlc-r3-review-fable.md`)가 위 craft 로드 결함을 포함해 스킬 문장의 결함을 찾아 같은 라운드에 반영했다.

**R4 실측 결과 (2026-09-13).**

*Codex CLI 0.154.0.* 빈 임시 프로젝트(`git init`만)에서 `npx skills add <저장소 로컬 경로> --skill dlc … --agent codex -y`로 10개를 설치했다. `.codex/` 디렉터리는 만들지 않고 프로젝트 `.agents/skills/<name>/`에 복사되며 `skills-lock.json`이 생긴다. `codex exec --json -s workspace-write -c approval_policy=never`로 1턴 `$dlc-init bugfix sku-zero-warehouse <설명>`, `codex exec resume --last`로 2턴 `$dlc-requirements`. 관찰:

- (a) 형제 경로: 에이전트는 `cat .agents/skills/dlc-init/SKILL.md .agents/skills/dlc/references/protocol.md …`로 스킬과 참조를 읽고 `python3 .agents/skills/dlc/scripts/dlc.py init …`로 스크립트를 프로젝트 상대 경로로 실행했다. `../dlc/` 가정이 Codex 설치 구조에서 성립한다(프롬프트에 "스크립트 위치는 이 프로젝트의 .agents/skills다"라는 힌트 한 줄을 줬다).
- (c) 질문 파일·게이트: 2턴에서 `dlc.py next` → `start requirements` → `requirements-questions.md` 작성(bugfix 주제 순서대로 재현 조건·영향 범위·회귀 테스트 3개, 답변란 비움) → 채팅으로 질문을 보이고 대기. bugfix 프로파일의 질문 주제 전환이 첫 실측에서 확인됐다. 선택지 마지막을 `X. Other (please specify)` 대신 `X. 기타 — 직접 설명한다`로 한국어화했다(check는 이 문구를 보지 않는다).
- 3턴(답변 3개 전송)은 Codex 계정의 사용량 한도("You've hit your usage limit … try again at 9:08 PM")로 `turn.failed`. 요약 확인·승인·(b) 관련 없는 프롬프트로 자동 발동 차단 확인은 한도 해제 뒤 같은 세션을 `resume`해 이어간다. 1·2턴 합계 입력 533k 토큰(캐시 446k), 출력 2.4k.
- Codex가 "Skill descriptions were shortened to fit the skills context budget" 경고를 냈다. 이 PC의 `~/.codex/skills/`에 스킬이 많아서이며 동작에는 영향이 없었다. README에 기록.

*Gemini CLI 0.34.0.* skills CLI의 에이전트 이름은 `gemini`가 아니라 `gemini-cli`다(`gemini`는 "Invalid agents"). 같은 명령으로 프로젝트 `.agents/skills/`에 복사되고 `gemini skills list`가 dlc 10개를 전부 `[Enabled]`로 발견했다(`~/.agents/skills/`의 사용자 스킬도 함께). 모델 호출은 이 PC의 인증 방식(`oauth-personal`)이 "This client is no longer supported for Gemini Code Assist for individuals"(`IneligibleTierError`)로 거부돼 실측하지 못했다. 공식 문서(2026-04-30)는 스킬 활성화를 모델의 `activate_skill` 도구 호출 + 사용자 확인으로만 정의하고, 슬래시는 `/skills list|enable|disable|link`뿐이다. 즉 §9의 "슬래시 호출" 질문은 "없다"로 닫힌다. 우회는 API 키 또는 Antigravity 계정 인증이며, 자동 활성 차단 설정이 없다는 제약은 그대로다.

*evals.* 케이스 8개(R2의 express-requirements 포함). 실행기 `dlc/evals/run.sh`가 `~/.docker/cli-plugins`·`bin/lib`의 심링크 디렉터리를 실행 동안 옮기고 trap으로 되돌린다 — `DOCKER_CONFIG`를 빈 디렉터리로 바꿔도 러너가 같은 오류를 내므로(R4 확인) 이동이 유일한 우회다. 거짓 양성 회피: 라우터 SKILL.md 본문이 슬래시 명령 확장으로 trace에 들어가므로 "`/dlc:dlc-requirements`를 안내했다", "`dlc-init`을 안내했다" 같은 문자열 grader는 두지 않았고, 안내는 `dlc.py` 출력 문구(`활성 작업이 없습니다`, `다음: requirements → dlc-requirements`)와 부정 grader(`dlc.py init`·`start` 미실행)로 증명한다. 모호어 후속 질문 케이스는 `[Answer]:` 접두를 앵커로 써 프롬프트 본문과 구분하고, 후속 답에 프롬프트의 "후속 답변" 절에만 있는 토큰 `test_stock_404`를 두어 후속 질문이 실제로 파일에 추가됐음을 잡는다. 결과는 아래 표.

1차 전체 실행: Claude Code 2.1.270, `-j 2`, 362초, 약 $4.41. 8 케이스 중 5개 1.0, 3개 grader 결함(스킬 결함 0). 재실행에서 2개가 1.0으로 닫혔고 plan 케이스는 계정 한도로 미완이다.

| 케이스 | 대상 | 1차 (turns / $ / grader) | 재실행 (grader 수정 뒤, `--keep-temp`) |
|---|---|---|---|
| `bugfix-requirements` | bugfix 프로파일 init→requirements | 16 / 0.76 / 9/9 | — |
| `express-requirements` | express init→requirements + "여기까지" 중단(R2 케이스 + grader 1) | 18 / 0.88 / 11/11 | — |
| `plan-supplies-units` | plan이 units.md 공급, 유닛 집합·실행 명령 검사 | 23 / 0.93 / 8/9 (실패: units-md-has-unit-rows) | 15 / 0.69 / 6/9 — Claude 계정 **세션 한도**("session limit · resets 9:40pm")로 plan.md 작성 직후 중단, check·approve 미실행. 한도 해제 뒤 재실행 필요. grader 결함 — units.md 앵커 뒤 JSON 문자열 통과 구간을 빠뜨려 표 앞의 제목 줄에서 실패. 1차 trace는 `check plan: OK`·`plan: done`을 통과했으므로 스킬 결함 아님 |
| `requirements-vague-followup` | requirements 모호어 후속 질문 | 14 / 0.67 / 6/6 | — |
| `router-all-gate-waits` | 라우터 `--all`, 승인 게이트 대기(침묵≠승인) | 13 / 0.62 / 5/6 (실패: gate-not-approved-by-silence) | 13 / 0.64 / 6/6 통과. grader 거짓 양성 — `dlc.py approve requirements`가 dlc-requirements 완료 기준 문장에 있음. approve 출력 `requirements: done` 부재로 바꿈 |
| `router-guide-empty` | 라우터 안내 모드, 작업 없음 | 3 / 0.16 / 3/4 (실패: does-not-init-by-itself) | 4 / 0.15 / 4/4 통과. grader 거짓 양성 — `dlc.py init`이 dlc.py 안내 문구에 있음. 패턴을 `init --profile (full|express|bugfix)`로 좁힘 |
| `router-guide-next` | 라우터 안내 모드, 다음 스킬 안내 | 4 / 0.17 / 4/4 | — |
| `router-no-cursor` | 라우터, 커서 없음 → 기존 작업 나열 | 6 / 0.22 / 5/5 | — |

grader 교훈(R2 U1의 연장): trace에는 에이전트가 읽은 스킬·참조 문서와 `dlc.py`의 안내 문구까지 들어가므로, 부정 grader의 패턴은 실제 명령·출력에만 있는 형태(`init --profile express`, `requirements: done`)로 좁혀야 한다. Write 앵커 뒤에는 반드시 JSON 문자열 통과 구간 `(?:[^"\\]|\\.)*?`를 둔다.

**최종 실행(2026-09-13 19:05 KST, 2.1.270).** grader 수정을 반영한 전체 suite 1회: 8 케이스 전부 1.0, grader 54개 전부 통과, 324초, 약 $4.15, `--threshold 1.0` 종료 코드 0. 세 실행 사이에 스킬·스크립트 변경은 없었으므로 1차 실패 3건이 채점기 결함이었음이 확정됐다. 케이스별 행위·품질 관찰과 grader가 보지 못한 것은 `docs/review/2026-09-13-dlc-r4-eval-results.md`. 위 표의 "재실행" 열 제목은 plan 행에는 맞지 않는다 — 그 재실행은 수정 전 패턴으로 돌았고(Opus 리뷰 지적 3) 수정 패턴은 최종 실행에서 검증됐다.

**R4 잔여(계정 한도 해제 뒤).** ~~(1) `dlc/evals/run.sh --case plan-supplies-units` 재실행과 전체 suite 1회로 깨끗한 리포트 확보(Claude 세션 한도 21:40 KST 해제).~~ → 위 최종 실행으로 해소. (2) Codex 3턴 이후(답변 → 요약 확인 → 승인)와 관련 없는 프롬프트의 자동 발동 차단 확인(Codex 한도 21:08 KST 해제, `codex exec resume --last`).

*build 재개 경로.* R3 express 산출물(`wcl`) 복사본에서 `build/u2-cli.md`·`wcl/__main__.py`·`tests/test_cli.py`를 지우고 state.md의 build를 `active`, verify를 `pending`으로 되돌린 픽스처 위에서 `claude -p --plugin-dir ./dlc --dangerously-skip-permissions`로 `/dlc:dlc-build` 재개 프롬프트를 실행했다. 19턴, 약 $2.30. 에이전트는 `dlc.py next`로 build를 확인한 뒤 state가 `active`임을 보고 `start build`를 다시 실행하지 않고 `note build "재개"`를 기록했다(log.md: `build | start`(R3) → `build | note | 재개` → `build | approve`). `build/u1-count.md`가 있는 u1은 건너뛰고 u2-cli부터 진행 — `craft:tdd`를 Skill 도구로 로드하고 seam 테스트 5건을 red→green 3회(모듈 없음·옵션을 파일로 취급·없는 파일 예외 전파)로 구현, red 없이 통과한 2건은 기록에 구분해 적었다. `python3 -m unittest discover -s tests` 8건 OK, `check build` OK, 승인 뒤 `verify pending`에서 지시대로 멈췄다. verify의 재개 규칙(`dlc-verify` "재개" 절)은 build와 같은 문장이며 이번에 따로 돌리지 않았다.

기존 `evals.json`(skill-creator 형식)은 dlc에 만들지 않는다. 다른 플러그인 4개가 그 형식을 쓰지만 dlc는 `claude plugin eval`이 실행·채점·리포트를 다 맡으므로 병행하면 같은 케이스를 두 번 적게 된다(R4 결정).

**evals 시점(2026-09-13 결정).** 평가 suite는 R4에서 만든다. R1 시점에 만들면 스테이지 스킬이 없어 라우터의 "멈추고 안내" 분기만 검사할 수 있고, R2·R3에서 프로즈가 바뀌면 grader를 다시 써야 한다. 결정적인 부분(`dlc.py`)은 unittest가 라운드마다 회귀를 잡는다. 케이스 하나가 기본 3회 실행(ablation 시 6회)이라 라운드마다 suite를 돌리면 비용이 곱해진다. 단, 라우터·스테이지 스킬이 `disable-model-invocation: true`인데 eval 프롬프트에서 발동되는지는 공식 문서에 없으므로, R2의 express 1회 실행을 eval 케이스 1건으로 수행해 이 미지수를 먼저 푼다. 저장소의 기존 `evals.json`(skill-creator 형식)과의 병행 여부는 R4에서 정한다.

**R2 eval 실행 결과 (2026-09-13).** 케이스 `dlc/evals/express-requirements/`를 `--runs 1 --ablation none --scaffold --allow-tools Bash Write Edit`로 실행했다. `--allow-tools`는 case.yaml `allowed_tools`(모델에 보이는 도구 목록: Bash·Read·Write·Edit·Glob·Grep) 중 게이트 도구(Bash·Write·Edit)에 대한 운영자 허가이며 Read·Glob·Grep은 게이트가 아니라 허가가 필요 없다. 1차(Claude Code 2.1.269) 18턴, 약 $0.89, grader 10/11 통과. 실패 1건은 아래 러너 제약(glob)이며 스킬 결함이 아니다. 그 grader를 trace 기반으로 바꿔 재실행한 2차(2.1.270, 두 실행 사이 CLI 자동 갱신) 18턴, 약 $0.89, 11/11 통과(점수 1.0). 그러나 R2 리뷰(통합 U1)에서 내용 grader 3개가 참조 문서의 Read 결과에도 매치되는 거짓 양성이 확인돼 Write 입력에 앵커링한 grader로 바꾸고 3차를 실행했다(결과는 아래 표 뒤). 결과가 정한 것:

| 미지수 | 확정 | R4 evals에 미치는 것 |
|---|---|---|
| 명시 호출 스킬의 발동 | 프롬프트 첫 줄을 슬래시 명령(`/dlc:dlc --all express …`)으로 시작하면 CLI(sdk-cli 진입점)가 명령을 펼쳐 `disable-model-invocation: true` 스킬이 발동된다. 에이전트가 곧바로 스킬 본문의 절차(`dlc.py next` 실행, 참조 문서 Read)를 따랐다 | 케이스 프롬프트는 슬래시 명령으로 시작한다 |
| 발동 채점 | Skill 도구 호출은 0회. `tool_used: Skill`은 발동 지표로 쓸 수 없다. R3 express trace에는 Skill 호출이 1회 있었지만 대상이 `craft:tdd`였으므로, 이 지표는 dlc 스킬 발동과 다른 스킬 호출을 구분하지 못한다(R3 Opus 리뷰 12) | 발동 지표는 스킬만 아는 행위의 trace regex(`dlc\.py (init\|next\|…)`)로 잡는다 |
| 다중 턴 | 지원하지 않는다. `context.history_file`은 이전 대화 주입만 한다 | 질문 답·요약 확인·승인을 프롬프트에 사전 제공한다. 명시 사전 승인이라 protocol.md의 "침묵은 승인 아님"과 충돌하지 않는다. 라우터 `--all`에 "작업이 없으면 init부터" 분기를 넣어 한 프롬프트로 init→requirements를 이었다 |
| scaffold | `context.scaffold_script`는 케이스 디렉터리 기준 상대 경로의 bash 파일. 에이전트 cwd(`<tmp>/home/cwd`)에서 실행되고 그 디렉터리가 에이전트의 cwd다. HOME·`CLAUDE_CONFIG_DIR`가 격리되고 CLAUDE.md는 로드되지 않는다(`CLAUDE_CODE_DISABLE_CLAUDE_MDS=1`). 플러그인은 대상 경로의 절대 경로로 로드되어 `<skills>`는 `<plugin>/skills`로 풀린다 | 픽스처는 scaffold가 cwd에 만든다 |
| 파일 내용 채점 | `regex`의 `target: {source: file, path}`는 glob을 받지 않는다(리터럴 경로만). 작업 폴더 이름에 날짜가 있어 파일을 가리킬 수 없다. `file_exists`의 `path`는 glob을 받는다 | 존재는 `file_exists` glob으로 본다. 내용은 trace regex로 보되, trace에는 에이전트가 Read한 참조 문서 본문도 남으므로 **Write 도구 입력에 앵커링**해야 한다(`<경로>","content":"` 뒤 JSON 문자열 안에서만 매치). 앵커 없는 패턴은 protocol.md·grounding.md·SKILL.md의 예시에 매치돼 거짓 양성이 난다(R2 리뷰 U1에서 Read 결과만으로 3개 모두 통과함을 재현) |
| 실행 환경 | Bash를 허용하는 eval은 `~/.docker` 안에 심볼릭 링크(Docker Desktop의 `cli-plugins/`, `bin/lib/`)가 있으면 샌드박스가 실행을 거부한다. 실행 동안 두 폴더를 `~/.docker` 바깥으로 옮기고 끝나면 되돌리는 우회가 필요했다 | 실행 절차에 기록. 자동화 여부는 R4에서 판단 |

3차(2.1.270, Write 앵커 grader 10개): 18턴, 약 $0.80, 10/10 통과(점수 1.0). 앵커 패턴은 실행 전 1차 trace로 양성(원 trace 매치)·음성(Write 호출·결과 제거 시 불매치)을 확인했다.

산출물 관찰: 질문 5개(minimal 기준 2~4를 넘음. 사용자가 주제 5개를 제공한 결과이며 기준은 상한이 아니다), FR3·NFR1, 모든 행에 출처 태그, FR마다 수용 기준, 가정 7건. 같은 날 full 프로파일(intent·practices) 헤드리스 실행(`claude -p --plugin-dir ./dlc`, 빈 임시 디렉터리, 답변 사전 제공)은 첫 시도가 계정 세션 사용량 한도로 첫 턴에서 멈췠고, 한도 해제 뒤 재실행에서 9턴, 약 $1.70으로 init→intent→practices 승인까지 끝났다. intent 질문 8개·practices 질문 7개(standard 기준 5~8 안), 두 산출물 모두 `check` 통과, 가정 절에 각 3건. 관찰 둘: (a) 에이전트가 `start`와 산출물 작성을 같은 배치로 묶어 start→approve 간격이 8초였다. 답이 사전 제공된 자동 실행에서만 생기는 압축이며 log의 전이 순서는 지켜졌다. (b) greenfield 질문에서 "(제안)" 표시가 프레임워크 기본값 외 항목(커밋 형식)에도 붙어, `dlc-practices`에 "표의 네 기본값에만 붙인다"를 명시했다. analyze는 `llm-wiki/` 복사본에서 직접 실행해 codebase.md 생성·지문 기록·`check analyze` 통과·승인, 두 번째 작업의 `next`가 analyze를 건너뛰고 requirements를 가리키는 것, `start analyze --force` 재실행까지 확인했다.

## 9. 열린 질문

해소된 항목은 취소선을 치고 뒤에 `→ 해소(R<n>)`로 결론을 적는다. 취소선이 없는 항목이 미해결이다.

- ~~Gemini CLI의 슬래시 호출이 현재 릴리스에 들어갔는지 실측이 필요하다. 이슈 #21760과 관련 PR은 확인했으나 설치된 버전에서 동작하는지는 R4에서 본다.~~ → 해소(R4): 0.34.0 문서·CLI에 스킬 이름 슬래시 호출은 없다. `/skills`는 list·enable·disable·link뿐이고 활성화는 모델의 `activate_skill` + 사용자 확인이다. 발견(`gemini skills list`)은 확인했고 모델 호출은 이 PC의 계정 티어로 실측 불가(§8 R4).
- ~~`npx skills add`가 스킬 디렉터리를 복사하는지 심링크하는지에 따라 `../dlc/` 상대 경로 해석이 달라질 수 있다.~~ → 해소(R1): 로컬 경로 설치 시 `mode: copy`로 `.agents/skills/<name>/`에 형제 디렉터리로 복사된다. 상대 경로 가정 성립. `tests/`도 함께 복사되는데 무해하다.
- ~~`practices.md`를 작업 단위 밖(`docs/dlc/`)에 두는 것이 여러 작업이 병행될 때 충돌하지 않는지 R2 실행에서 본다.~~ → 해소(R2, 규칙으로): `dlc-practices`에 갱신 모드 규칙을 넣었다(기존 값을 바꾸는 항목은 "다른 작업에도 적용됨"을 알리고 확인받고, `note`로 기록). 병행 실측은 하지 않았고 규칙이 충돌을 사용자 결정으로 돌린다.
- ~~`codebase.md`의 출처 태그. `[practice]`는 codebase.md·practices.md에 기록된 사실을 가리키므로 codebase.md 자신에게는 순환이다.~~ → 해소(R2): `[code:<경로>]` 태그를 grounding.md에 추가했다.
- ~~bugfix 프로파일은 R1~R3 어느 실행에도 없었다. express와 스테이지·depth가 같고 차이는 `dlc-requirements`의 질문 주제뿐이므로 requirements 1스테이지 실행으로 검증한다(R3 Opus 리뷰 8, R4).~~ → 해소(R4): eval `bugfix-requirements`(Claude, 16턴, 9/9)와 Codex `$dlc-init bugfix`→`$dlc-requirements` 두 경로에서 질문 주제가 재현·영향·회귀로 바뀌는 것을 확인했다(§8 R4).
- ~~라우터 `--all`의 "여기까지" 중단이 실제로 멈추는지. R2 eval 케이스 `express-requirements`의 프롬프트가 requirements 승인 뒤 "여기까지"를 지시하고 있어 이 케이스에 "다음 스테이지 `start`가 없다"는 grader를 붙이면 실측이 된다(R4).~~ → 해소(R4): `express-requirements`에 `dlc.py start plan` 부재 grader를 붙여 11/11 통과. `bugfix-requirements`·`plan-supplies-units`(1차)도 같은 grader로 멈춤을 확인했다.
- ~~build·verify의 재개 경로(`state.md`가 이미 `active`일 때 `start`를 다시 하지 않고 `note "재개"` 뒤 남은 유닛부터). 실행 기록이 없다(R4).~~ → 해소(R4): build 재개를 픽스처(u2 기록·코드 제거, build `active`) 위에서 실측 — `start` 재실행 없이 `note "재개"` → 남은 유닛 구현 → `check build` OK → 승인(§8 R4). verify는 같은 규칙 문장이라 별도 실측 없이 닫는다.
- ~~R4 evals의 앵커. 파일 쓰기는 Write 도구와 Bash heredoc 양쪽, 스킬 파일 읽기는 Read와 Bash `cat` 양쪽을 받아야 한다(§8 R3 관찰).~~ → 해소(R4): 쓰기 앵커는 `(?:","content":"|\s*<<\s*-?'?\w+'?\\n)`로 Write 입력과 heredoc 양쪽을 받는다. 읽기 앵커는 두지 않았다 — 스킬 파일 읽기는 발동의 증거로 쓰지 않고 `dlc.py` 실행 흔적으로 대신한다.
