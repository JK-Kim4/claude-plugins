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
| `dlc-requirements` | requirements-analysis·user-stories | `requirements.md` (FR/NFR ID, 스토리, 제약, 가정, 범위 밖) |
| `dlc-design` | domain-design·units-generation·contract-design | `design.md`, `decisions.md`(ADR), `units.md`(유닛 DAG) |
| `dlc-plan` | delivery-planning·code-generation-plan | `plan.md` (유닛 순서, seam, 테스트 예산, 완료 정의) |
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

## 5. 공유 스파인

스테이지 스킬과 라우터가 함께 읽는 것은 라우터 스킬 `dlc/` 안에 둔다. 다른 스킬은 `../dlc/references/...`로 가리킨다. Claude 플러그인(`<plugin>/skills/<name>/`)과 `npx skills add`(`~/.agents/skills/<name>/`) 둘 다 스킬 디렉터리가 형제로 놓이므로 상대 경로가 같다. 이 가정은 1라운드에서 실제 설치로 검증한다.

```
dlc/
  SKILL.md                      라우터
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

**출처 태그.** 산출물의 실질 문단·표 행은 `[desc]`, `[Q<n>]`, `[practice]`, `[assumption]` 중 하나를 단다. 근거 없는 내용은 `## 가정과 열린 질문` 절에만 둔다. 이 절은 필수이며 없으면 `None.`을 쓴다.

## 6. dlc.py 책임

세 가지로 제한한다. 라우팅 판단이 프로즈에 있으면 실행마다 흔들리므로 코드에 둔다.

| 명령 | 역할 |
|---|---|
| `init --profile <p> --slug <s>` | 작업 폴더와 `state.md` 생성, 워크스페이스 스캔(greenfield/brownfield, 언어·빌드 도구 감지) |
| `status` | 현재 작업, 프로파일, 스테이지별 상태 출력 |
| `next` | 다음 실행 스테이지와 호출할 스킬 이름 출력. 완료면 `done` |
| `check <stage>` | 산출물 필수 절 존재, 질문 파일 미답변 여부, FR/NFR ID 연속성 검사. 실패 목록 출력 |
| `start`, `approve`, `skip --reason` | 상태 전이 기록. `approve`는 `check` 통과가 전제 |

python3 표준 라이브러리만 쓴다. `python3 -m unittest discover -s dlc/tests`로 검증한다. 스크립트가 없는 환경에서는 각 스킬이 `references/protocol.md`의 수동 체크리스트를 따르도록 폴백을 둔다.

## 7. 에이전트별 호출과 제약

| 에이전트 | 설치 | 호출 | 명시 호출 강제 |
|---|---|---|---|
| Claude Code | `/plugin install dlc@jongwan-plugins` | `/dlc:dlc-requirements` | `disable-model-invocation: true` |
| Codex CLI | `npx skills add JK-Kim4/claude-plugins` | `$dlc-requirements` | `agents/openai.yaml`의 `policy.allow_implicit_invocation: false` |
| Gemini CLI | 위와 같음 | `/dlc-requirements` | 차단 설정 없음. description을 사람용 한 줄로 줄여 오발동을 낮춘다 |
| Cursor | 위와 같음 | 슬래시 | 미확인 |

Codex의 `agents/openai.yaml`은 Agent Skills 표준 밖의 확장이지만 다른 에이전트는 무시하므로 함께 넣는다.

## 8. 구현 라운드

| 라운드 | 내용 | 검증 |
|---|---|---|
| R1 | 플러그인 골격, 마켓플레이스 등록, 라우터 스킬, 공유 참조 3개, `dlc.py` + 테스트 | unittest GREEN, `claude plugin validate`, `npx skills add` 로컬 설치로 형제 경로 가정 확인 |
| R2 | 스테이지 스킬 5개: init, analyze, intent, practices, requirements | 빈 디렉터리에서 Claude로 express 프로파일 1회 실행. 기존 코드가 있는 디렉터리에서 analyze 1회 실행 |
| R3 | 스테이지 스킬 4개: design, plan, build, verify | 같은 실행을 verify까지 완주 |
| R4 | Codex `openai.yaml`, README, evals, Codex에서 1회 실행 | Codex에서 `$dlc-requirements` 동작 확인 |

## 9. 열린 질문

- Gemini CLI의 슬래시 호출이 현재 릴리스에 들어갔는지 실측이 필요하다. 이슈 #21760과 관련 PR은 확인했으나 설치된 버전에서 동작하는지는 R4에서 본다.
- ~~`npx skills add`가 스킬 디렉터리를 복사하는지 심링크하는지에 따라 `../dlc/` 상대 경로 해석이 달라질 수 있다.~~ R1에서 확인: 로컬 경로 설치 시 `mode: copy`로 `.agents/skills/<name>/`에 형제 디렉터리로 복사된다. 상대 경로 가정 성립. `tests/`도 함께 복사되는데 무해하다.
- `practices.md`를 작업 단위 밖(`docs/dlc/`)에 두는 것이 여러 작업이 병행될 때 충돌하지 않는지 R2 실행에서 본다.
