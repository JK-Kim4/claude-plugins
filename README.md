# jongwan-plugins 마켓플레이스

jongwan의 Claude Code 플러그인 마켓플레이스. 현재 네 개의 플러그인을 제공한다.

| 플러그인 | 설명 |
|----------|------|
| **document-generator** | 작업 보고서·진행 추적·기술 설계·온보딩 가이드를 목적과 독자에 맞는 형식으로 생성. Markdown·HTML·Notion 출력 지원. |
| **pr-automator** | 현재 브랜치 작업을 원격에 push하고 GitHub PR 생성을 자동화. 커밋 컨벤션 레포당 1회 확정·저장, 미커밋 커밋·브랜치 안전장치·기존 PR 갱신 처리. |
| **pr-reviewer** | 지정한 GitHub PR을 컨벤션·코드(보안·동시성·로직) 두 축으로 분석해 P0~P2 우선순위 라벨을 단 단일 PR Review로 게시. 리뷰 기준 컨벤션 레포당 1회 확정·저장. |
| **architecture-reviewer** | APoSD·DDD 관점으로 코드의 아키텍처 품질(복잡도·모듈 깊이·정보 은닉·결합도)을 7축 루브릭으로 진단하거나, 제안한 아키텍처 방향을 현 코드 기준으로 검증. 지적마다 P0~P2 + 개선 스케치. |
| **dlc** | AI-DLC 방법론의 명시 호출형 생명주기 스킬셋. 라우터(dlc) + 스테이지 9개(init·analyze·intent·practices·requirements·design·plan·build·verify), 프로파일 3개(full·express·bugfix). 산출물·진행 상태를 docs/dlc/ 에 남기고 python3 stdlib 스크립트가 상태 전이·다음 단계 판정·산출물 검사를 맡는다. Claude Code·Codex CLI 실측, Gemini CLI 발견 확인(`npx skills add`). |

## 구성

```
doc-gen-plugin/
├── .claude-plugin/
│   └── marketplace.json          # 마켓플레이스 카탈로그
├── document-generator/
│   ├── .claude-plugin/plugin.json
│   └── skills/document-generator/
├── pr-automator/
│   ├── .claude-plugin/plugin.json
│   └── skills/pr-automator/
│       ├── SKILL.md
│       ├── references/           # 커밋 컨벤션·PR 본문 템플릿
│       └── evals/                # 스킬 평가 케이스
├── pr-reviewer/
│   ├── .claude-plugin/plugin.json
│   └── skills/pr-reviewer/
│       ├── SKILL.md
│       ├── references/           # 컨벤션·코드리뷰 기준·게시 형식
│       └── evals/                # 스킬 평가 케이스
├── architecture-reviewer/
│   ├── .claude-plugin/plugin.json
│   └── skills/architecture-reviewer/
│       ├── SKILL.md
│       ├── references/           # 7축 루브릭·red flags·출처
│       └── evals/                # 스킬 평가 케이스
├── dlc/
│   ├── .claude-plugin/plugin.json
│   ├── evals/                    # claude plugin eval 케이스 8개 + run.sh
│   └── skills/
│       ├── dlc/                  # 라우터 + 공유 스파인(references/, scripts/dlc.py, tests/)
│       ├── dlc-init/  dlc-analyze/  dlc-intent/  dlc-practices/  dlc-requirements/
│       └── dlc-design/  dlc-plan/  dlc-build/  dlc-verify/
└── archive/                      # 스킬 이전 버전 보관 — archive/<스킬명>/<교체일>/
```

## 스킬 버전 관리

플러그인의 `skills/` 아래에는 최신 버전만 둔다. 스킬을 고치는 PR에서 이전 버전을 `archive/<스킬명>/<YYYY-MM-DD>/`로 옮기고 `plugin.json` 버전을 올린다. 절차와 보관 목록은 [`archive/README.md`](archive/README.md).

## 설치 (다른 PC 포함)

```bash
# 1. 마켓플레이스 추가
/plugin marketplace add JK-Kim4/claude-plugins

# 2. 원하는 플러그인 설치
/plugin install document-generator@jongwan-plugins
/plugin install pr-automator@jongwan-plugins
/plugin install pr-reviewer@jongwan-plugins
/plugin install architecture-reviewer@jongwan-plugins
/plugin install dlc@jongwan-plugins
```

> 로컬 개발·테스트: `/plugin marketplace add ~/doc-gen-plugin`

업데이트:

```bash
/plugin marketplace update jongwan-plugins
```

## 사용

- **document-generator**: "보고서 만들어줘", "문서로 남겨줘", "노션에 정리해줘" 등으로 자동 트리거. 직접 호출: `/document-generator:document-generator`
- **pr-automator**: "PR 올려줘", "이 브랜치 push하고 PR 만들어줘", "작업 끝났으니 PR 생성" 등으로 자동 트리거. 직접 호출: `/pr-automator:pr-automator`
  - 전제: 해당 레포가 git 레포이고, `gh`(GitHub CLI)가 설치·인증돼 있어야 한다.
- **pr-reviewer**: "이 PR 리뷰해줘", "PR #123 코드리뷰 코멘트 달아줘", "PR 컨벤션 점검" 등으로 트리거. 직접 호출: `/pr-reviewer:pr-reviewer`
  - 전제: git 레포 + `gh` 설치·인증. 대상 PR 번호/URL이 필요하다.
- **architecture-reviewer**: "이 모듈 아키텍처 리뷰해줘", "이 디렉터리 구조 점검", "이런 구조로 바꾸려는데 괜찮아?" 등으로 트리거. 직접 호출: `/architecture-reviewer:architecture-reviewer`
  - 진단 모드(지정 대상의 현 구조)와 방향 검증 모드(제안을 현 코드 기준으로 검증)를 지원한다.
- **dlc**: 자동 트리거 없음. `/dlc:dlc`(안내), `/dlc:dlc --all`(전체 진행), `/dlc:dlc-init` 등 스테이지 스킬을 이름으로 부른다. Codex CLI는 `$dlc-init`. 설치·호출·제약 표는 `dlc/README.md`.

## 검증

```bash
claude plugin validate ~/doc-gen-plugin
```
