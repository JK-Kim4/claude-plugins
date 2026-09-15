# dlc

AI-DLC(awslabs/aidlc-workflows) 방법론을 **에이전트 종속 없이** 쓰는 명시 호출형 생명주기 스킬셋. Claude Code, Codex CLI, Gemini CLI에서 같은 `SKILL.md`가 동작한다(Cursor는 Agent Skills 표준을 따르므로 설치는 같지만 실측하지 않았다).

설계 기록: `docs/design/2026-09-13-dlc-plugin-design.md`

## 구성

| 스킬 | 역할 | 산출물 |
|---|---|---|
| `dlc` | 라우터. 상태를 보이고 다음 스킬을 안내하거나 `--all`로 전체 진행 | — |
| `dlc-init` | 작업 폴더 생성, 저장소 스캔, 프로파일 선택 | `state.md` |
| `dlc-analyze` | 기존 코드베이스 분석 (brownfield일 때만) | `docs/dlc/codebase.md` |
| `dlc-intent` | 착수 전 검토: 문제, 대상, 성공 지표, 범위, 타당성 | `intent.md` |
| `dlc-practices` | 팀 관행 확정: 작업 방식, 테스트, 배포, 코드 스타일 | `docs/dlc/practices.md` |
| `dlc-requirements` | 6차원 질문, FR/NFR ID 요구사항서 | `requirements.md` |
| `dlc-design` | 컴포넌트 경계, 엔티티 소유권, ADR, 유닛 분해, 계약 | `design.md`, `decisions.md`, `units.md` |
| `dlc-plan` | 유닛 순서, seam, 테스트 예산, 완료 정의 | `plan.md` (design이 없는 프로파일이면 `units.md`도) |
| `dlc-build` | 유닛별 구현, 요구사항→파일 추적 | 코드, `build/<unit>.md` |
| `dlc-verify` | 전체 테스트, 추적성 검사, 리뷰 발견, 판정 | `verify.md` |

프로파일: `full`(init → (analyze) → intent → practices → requirements → design → plan → build → verify, 질문 5~8개), `express`(init → (analyze) → requirements → plan → build → verify, 질문 2~4개), `bugfix`(express와 같은 단계, requirements 질문이 결함 재현·기대 동작·영향 범위·회귀 테스트 중심). `(analyze)`는 기존 코드가 있을 때만 끼어드는 조건부 단계다.

## 동작 원리

- 산출물과 진행 상태는 프로젝트 저장소의 `docs/dlc/<YYMMDD>-<slug>/`에 남는다. 커밋 대상이라 세션·에이전트·PC가 바뀌어도 이어간다.
- `${CLAUDE_PLUGIN_ROOT}/skills/dlc/scripts/dlc.py`(python3 표준 라이브러리만)가 상태 전이, 다음 단계 판정, 산출물 검사(필수 절, 질문 답변, FR/NFR ID 연속·참조, 유닛·추적성 커버리지, plan 유닛 집합·실행 명령, verify 판정)를 맡는다. Claude Code는 `${CLAUDE_PLUGIN_ROOT}`를 플러그인 절대 경로로 치환하고, `npx skills add` 설치 환경에서는 `.agents/skills/dlc/scripts/dlc.py`로 읽는다. 에이전트는 `state.md`를 손으로 고치지 않는다.
- 질문은 A~E + `X. Other` 선택지와 `[Answer]:` 태그가 있는 파일로 주고받는다. 특정 도구의 질문 UI에 의존하지 않는다.
- 스테이지마다 승인 게이트가 있다. 침묵은 승인이 아니다.

## 설치

### Claude Code

```
/plugin marketplace add JK-Kim4/claude-plugins
/plugin install dlc@jongwan-plugins
```

호출: `/dlc:dlc`, `/dlc:dlc-requirements` 등. 모든 스킬이 `disable-model-invocation: true`라 이름을 쳐야만 실행된다.

### Codex CLI, Gemini CLI (Cursor는 미실측)

```
npx skills add JK-Kim4/claude-plugins --skill dlc --skill dlc-init --skill dlc-analyze --skill dlc-intent --skill dlc-practices --skill dlc-requirements --skill dlc-design --skill dlc-plan --skill dlc-build --skill dlc-verify --agent codex -y
```

Gemini CLI는 `--agent gemini-cli`(에이전트 이름이 `gemini`가 아니다). 프로젝트 안에서 실행하면 `.agents/skills/<name>/`에 형제 디렉터리로 **복사**되고(`skills-lock.json`이 함께 생긴다), `-g`를 붙이면 `~/.agents/skills/`에 간다. `--skill`은 정확한 스킬 이름만 받는다(와일드카드 불가). 스테이지 스킬은 `../dlc/scripts/dlc.py`로 라우터 스킬의 스크립트를 찾으므로 **`dlc` 라우터는 항상 함께 설치**한다.

| 에이전트 | 호출 | 명시 호출 강제 | 실측 (2026-09-13) |
|---|---|---|---|
| Claude Code 2.1.270 | `/dlc:dlc`, `/dlc:dlc-requirements` | `disable-model-invocation: true` | R2~R4 전 스테이지 실행. eval 8 케이스 최종 실행 8/8 1.0(1차는 5/8, 실패 3건은 채점기 결함으로 수정. `docs/review/2026-09-13-dlc-r4-eval-results.md`) |
| Codex CLI 0.154.0 | `$dlc-init`, `$dlc-requirements` | `agents/openai.yaml`의 `policy.allow_implicit_invocation: false` | `$dlc-init` → `$dlc-requirements` 질문 파일 생성·대기까지 확인. 에이전트가 `.agents/skills/dlc/scripts/dlc.py`를 프로젝트 상대 경로로 찾았다. 스킬이 많은 환경에서는 "Skill descriptions were shortened to fit the skills context budget" 경고가 뜬다(동작에는 영향 없음) |
| Gemini CLI 0.34.0 | `activate_skill` 도구(모델이 고름) 또는 `/skills list`로 확인 | 차단 설정 없음. description을 사람용 한 줄로 둔다 | `gemini skills list`가 프로젝트 `.agents/skills/`의 dlc 스킬 10개를 전부 발견. 모델 호출은 이 PC의 개인 계정 티어(`oauth-personal`, "Gemini Code Assist for individuals" 지원 종료)로 막혀 실측하지 못했다. 우회: API 키 또는 Antigravity 계정으로 인증 |
| Cursor | 슬래시 | 미확인 | 미실측 |

Gemini CLI에는 스킬 이름을 슬래시로 직접 부르는 명령이 없다(0.34.0 문서 기준. `/skills`는 list·enable·disable·link만). 사용자는 "dlc-requirements 스킬을 활성화해라"처럼 이름을 말하고, 모델이 `activate_skill`을 호출하면 확인 프롬프트를 거쳐 스킬 본문이 주입된다. 자동 활성을 막는 설정은 없으므로 관련 없는 대화에서 활성화 확인이 뜨면 거절한다.

## 요구 환경

python3 3.9 이상. 외부 패키지 없음.

## 검증

```bash
python3 -m unittest discover -s dlc/skills/dlc/tests   # 87건
claude plugin validate ./dlc
dlc/evals/run.sh                                         # eval 8 케이스 (Bash 허용 eval 의 ~/.docker 심링크 문제를 우회)
```

eval 케이스는 `dlc/evals/<case>/case.yaml`(+ 픽스처 `scaffold.sh`)이다. 라우터 4(안내 모드 빈 상태·다음 안내·커서 없음·`--all` 승인 게이트 대기), requirements 3(express·모호어 후속 질문·bugfix), plan 1(units.md 공급). 단일 프롬프트라 질문 답·요약 확인·승인을 프롬프트에 사전 제공한다. 내용 grader는 Write 입력과 Bash heredoc 양쪽을 앵커로 받는다.
