# jongwan-plugins 마켓플레이스

jongwan의 Claude Code 플러그인 마켓플레이스. 현재 두 개의 플러그인을 제공한다.

| 플러그인 | 설명 |
|----------|------|
| **document-generator** | 작업 보고서·진행 추적·기술 설계·온보딩 가이드를 목적과 독자에 맞는 형식으로 생성. Markdown·HTML·Notion 출력 지원. |
| **pr-automator** | 현재 브랜치 작업을 원격에 push하고 GitHub PR 생성을 자동화. 커밋 컨벤션 레포당 1회 확정·저장, 미커밋 커밋·브랜치 안전장치·기존 PR 갱신 처리. |

## 구성

```
doc-gen-plugin/
├── .claude-plugin/
│   └── marketplace.json          # 마켓플레이스 카탈로그
├── document-generator/
│   ├── .claude-plugin/plugin.json
│   └── skills/document-generator/
└── pr-automator/
    ├── .claude-plugin/plugin.json
    └── skills/pr-automator/
        ├── SKILL.md
        ├── references/           # 커밋 컨벤션·PR 본문 템플릿
        └── evals/                # 스킬 평가 케이스
```

## 설치 (다른 PC 포함)

```bash
# 1. 마켓플레이스 추가
/plugin marketplace add JK-Kim4/claude-plugins

# 2. 원하는 플러그인 설치
/plugin install document-generator@jongwan-plugins
/plugin install pr-automator@jongwan-plugins
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

## 검증

```bash
claude plugin validate ~/doc-gen-plugin
```
