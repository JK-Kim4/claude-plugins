# jongwan-plugins 마켓플레이스

jongwan의 Claude Code 플러그인 마켓플레이스. 현재 세 개의 플러그인을 제공한다.

| 플러그인 | 설명 |
|----------|------|
| **document-generator** | 작업 보고서·진행 추적·기술 설계·온보딩 가이드를 목적과 독자에 맞는 형식으로 생성. Markdown·HTML·Notion 출력 지원. |
| **pr-automator** | 현재 브랜치 작업을 원격에 push하고 GitHub PR 생성을 자동화. 커밋 컨벤션 레포당 1회 확정·저장, 미커밋 커밋·브랜치 안전장치·기존 PR 갱신 처리. |
| **pr-reviewer** | 지정한 GitHub PR을 컨벤션·코드(보안·동시성·로직) 두 축으로 분석해 P0~P2 우선순위 라벨을 단 단일 PR Review로 게시. 리뷰 기준 컨벤션 레포당 1회 확정·저장. |

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
└── pr-reviewer/
    ├── .claude-plugin/plugin.json
    └── skills/pr-reviewer/
        ├── SKILL.md
        ├── references/           # 컨벤션·코드리뷰 기준·게시 형식
        └── evals/                # 스킬 평가 케이스
```

## 설치 (다른 PC 포함)

```bash
# 1. 마켓플레이스 추가
/plugin marketplace add JK-Kim4/claude-plugins

# 2. 원하는 플러그인 설치
/plugin install document-generator@jongwan-plugins
/plugin install pr-automator@jongwan-plugins
/plugin install pr-reviewer@jongwan-plugins
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

## 검증

```bash
claude plugin validate ~/doc-gen-plugin
```
