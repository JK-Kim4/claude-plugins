# jongwan-plugins 마켓플레이스

jongwan의 Claude Code 플러그인 마켓플레이스. 일곱 개의 플러그인을 제공한다. 목록의 정본은 `.claude-plugin/marketplace.json`이다.

| 플러그인 | 버전 | 구성 | 설명 |
|----------|------|------|------|
| **document-generator** | 1.5.0 | 스킬 1 | 작업 보고서·진행 추적·기술 설계·온보딩 가이드를 목적과 독자에 맞는 형식으로 생성. Markdown·HTML·Notion 출력 지원. |
| **pr-reviewer** | 1.1.0 | 스킬 1 | 지정한 GitHub PR을 컨벤션·코드(보안·동시성·로직) 두 축으로 분석해 Pn 룰(P1~P5) 우선순위 라벨을 단 단일 PR Review로 게시. `craft:code-reviewer` 페르소나 연동. 리뷰 기준 컨벤션 레포당 1회 확정·저장. |
| **architecture-reviewer** | 1.0.0 | 스킬 1 | APoSD·DDD 관점으로 코드의 아키텍처 품질(복잡도·모듈 깊이·정보 은닉·결합도)을 7축 루브릭으로 진단하거나, 제안한 아키텍처 방향을 현 코드 기준으로 검증. 지적마다 P0~P2 + 개선 스케치. |
| **craft** | 0.3.0 | 에이전트 4 · 스킬 6 | 개발 파이프라인 페르소나 sub agent 4종(verifier·interface-designer·tdd-implementer·code-reviewer)과 오케스트레이션 스킬(triage·diagnosing-bugs·design-it-twice·tdd·implement·test-audit). |
| **llm-wiki** | 0.2.4 | 스킬 4 | 흩어진 마크다운·AI 세션 기록을 하나의 LLM wiki로 통합(wiki-bootstrap)·가공(wiki-digest)·점검(wiki-lint)·조회(wiki-recall). python3 stdlib만 사용. |
| **agent-workflow** | 0.1.0 | 스킬 2 | 에이전트 작업 위생 — 토큰 낭비를 줄이는 규율(token-efficiency), 최신 `origin/develop` 기준 격리 Git worktree 생성과 작업 경로 고정(worktree). |
| **dlc** | 0.1.0 | 스킬 10 | AI-DLC 방법론의 명시 호출형 생명주기 스킬셋. 라우터(dlc) + 스테이지 9개(init·analyze·intent·practices·requirements·design·plan·build·verify), 프로파일 3개(full·express·bugfix). 산출물·진행 상태를 `docs/dlc/`에 남기고 python3 stdlib 스크립트가 상태 전이·다음 단계 판정·산출물 검사를 맡는다. |

## 구성

```
claude-plugins/
├── .claude-plugin/
│   └── marketplace.json          # 마켓플레이스 카탈로그 (플러그인 7개)
├── document-generator/
│   ├── .claude-plugin/plugin.json
│   └── skills/document-generator/  # SKILL.md · assets/ · references/ · evals/
├── pr-reviewer/
│   ├── .claude-plugin/plugin.json
│   └── skills/pr-reviewer/         # SKILL.md · references/(컨벤션·코드리뷰 기준·게시 형식) · evals/
├── architecture-reviewer/
│   ├── .claude-plugin/plugin.json
│   └── skills/architecture-reviewer/  # SKILL.md · references/(7축 루브릭·red flags·출처) · evals/
├── craft/
│   ├── .claude-plugin/plugin.json
│   ├── README.md
│   ├── agents/                   # verifier · interface-designer · tdd-implementer · code-reviewer
│   └── skills/                   # triage · diagnosing-bugs · design-it-twice · tdd · implement · test-audit
├── llm-wiki/
│   ├── .claude-plugin/plugin.json
│   ├── README.md
│   └── skills/                   # wiki-bootstrap · wiki-digest · wiki-lint · wiki-recall (형제로 함께 설치)
├── agent-workflow/
│   ├── .claude-plugin/plugin.json
│   ├── README.md
│   └── skills/                   # token-efficiency · worktree
├── dlc/
│   ├── .claude-plugin/plugin.json
│   ├── README.md
│   ├── evals/                    # claude plugin eval 케이스 8개 + run.sh
│   └── skills/
│       ├── dlc/                  # 라우터 + 공유 스파인(references/, scripts/dlc.py, tests/)
│       ├── dlc-init/  dlc-analyze/  dlc-intent/  dlc-practices/  dlc-requirements/
│       └── dlc-design/  dlc-plan/  dlc-build/  dlc-verify/
├── archive/                      # 스킬 이전 버전 보관 — archive/<스킬명>/<교체일>/
├── docs/                         # design/(플러그인 설계) · research/ · review/(설계·구현 리뷰 기록)
└── pr-automator/                 # 마켓플레이스 목록에 없음 — 설치 대상 아님
```

- `pr-automator/`는 폴더와 `plugin.json`이 남아 있지만 craft 플러그인을 추가한 커밋(`d6084d8`)에서 `marketplace.json` 목록에서 빠졌다. `/plugin install`로 설치할 수 없다.
- 로컬에만 두고 커밋하지 않는 것(`.gitignore`): `docs/handoff/`(사내 경로·이메일 포함), `*/evals/results/`(eval 실행 결과), `.omc/`(세션 상태).

## 설치 (다른 PC 포함)

```bash
# 1. 마켓플레이스 추가
/plugin marketplace add JK-Kim4/claude-plugins

# 2. 원하는 플러그인 설치
/plugin install document-generator@jongwan-plugins
/plugin install pr-reviewer@jongwan-plugins
/plugin install architecture-reviewer@jongwan-plugins
/plugin install craft@jongwan-plugins
/plugin install llm-wiki@jongwan-plugins
/plugin install agent-workflow@jongwan-plugins
/plugin install dlc@jongwan-plugins
```

> 로컬 개발·테스트: `/plugin marketplace add <이 저장소를 클론한 경로>`

업데이트:

```bash
/plugin marketplace update jongwan-plugins
claude plugin update <플러그인>@jongwan-plugins   # 설치된 플러그인을 새 버전으로. 재시작 후 적용
```

Codex·Gemini CLI 등 다른 에이전트는 스킬만 `npx skills add JK-Kim4/claude-plugins --skill <스킬명> --agent <에이전트>`로 설치한다. 플러그인별 절차와 제약은 `craft/README.md`, `dlc/README.md`.

## 사용

- **document-generator**: "보고서 만들어줘", "문서로 남겨줘", "노션에 정리해줘" 등으로 자동 트리거. 직접 호출: `/document-generator:document-generator`
- **pr-reviewer**: "이 PR 리뷰해줘", "PR #123 코드리뷰 코멘트 달아줘", "PR 컨벤션 점검" 등으로 트리거. 직접 호출: `/pr-reviewer:pr-reviewer`
  - 전제: git 레포 + `gh` 설치·인증. 대상 PR 번호/URL이 필요하다.
- **architecture-reviewer**: "이 모듈 아키텍처 리뷰해줘", "이 디렉터리 구조 점검", "이런 구조로 바꾸려는데 괜찮아?" 등으로 트리거. 직접 호출: `/architecture-reviewer:architecture-reviewer`
  - 진단 모드(지정 대상의 현 구조)와 방향 검증 모드(제안을 현 코드 기준으로 검증)를 지원한다.
- **craft**: 스킬이 상황에 맞는 페르소나 agent(`craft:verifier` 등)를 스폰한다. `triage`·`implement`는 자동 트리거 없이 `/craft:triage`·`/craft:implement`로 부른다. 나머지 스킬은 "진단해줘", "TDD로", "리텐션 전략 세워줘" 등으로 트리거. 페르소나·스킬 표는 `craft/README.md`.
- **llm-wiki**: "지식베이스 만들어줘", "이 세션 정리해줘", "위키 점검", "전에 어떻게 했더라" 등으로 트리거. 연산별 설명은 `llm-wiki/README.md`.
- **agent-workflow**: `token-efficiency`는 도구를 쓰는 모든 작업에 적용된다. `worktree`는 사용자가 명시적으로 호출했을 때만 동작한다.
- **dlc**: 자동 트리거 없음. `/dlc:dlc`(안내), `/dlc:dlc --all`(전체 진행), `/dlc:dlc-init` 등 스테이지 스킬을 이름으로 부른다. Codex CLI는 `$dlc-init`. 설치·호출·제약 표는 `dlc/README.md`.

## 스킬 버전 관리

플러그인의 `skills/` 아래에는 최신 버전만 둔다. 스킬을 고치는 PR에서 이전 버전을 `archive/<스킬명>/<YYYY-MM-DD>/`로 옮기고 `plugin.json` 버전을 올린다. 절차와 보관 목록은 [`archive/README.md`](archive/README.md).

## 검증

```bash
claude plugin validate .   # 클론 루트에서
```

스크립트가 있는 플러그인은 테스트도 돌린다. 명령은 `llm-wiki/README.md`의 테스트 절, `dlc/README.md`의 검증 절.
