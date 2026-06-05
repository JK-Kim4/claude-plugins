# document-generator plugin

작업 보고서·진행 추적·기술 설계·온보딩 가이드를 **목적과 독자에 맞는 best-practice 형식**으로 생성하는 Claude Code 플러그인입니다. Markdown·HTML 파일은 물론 Notion 페이지 출력도 지원합니다.

## 구성

```
doc-gen-plugin/
├── .claude-plugin/
│   ├── marketplace.json      # 마켓플레이스 카탈로그
│   └── plugin.json           # 플러그인 매니페스트
└── skills/
    └── document-generator/   # 스킬 본체
        ├── SKILL.md
        ├── references/       # 문서 유형별 작성 가이드
        ├── assets/           # HTML 출력용 CSS
        └── evals/            # 스킬 평가 케이스
```

## 설치 (다른 PC 포함)

GitHub에서 마켓플레이스를 추가한 뒤 플러그인을 설치합니다. 어느 PC에서든 동일합니다.

```bash
# 1. 마켓플레이스 추가
/plugin marketplace add JK-Kim4/claude-plugins

# 2. 플러그인 설치
/plugin install document-generator@jongwan-plugins
```

> 로컬에서 개발·테스트할 때는 로컬 경로로도 추가할 수 있습니다:
> `/plugin marketplace add ~/doc-gen-plugin`

업데이트가 있을 때는:

```bash
/plugin marketplace update jongwan-plugins
```

## 사용

설치 후에는 "보고서 만들어줘", "문서로 남겨줘", "노션에 정리해줘" 같은 요청에 스킬이 자동으로 트리거됩니다. 직접 호출하려면:

```
/document-generator:document-generator
```

## 검증

```bash
claude plugin validate ~/doc-gen-plugin
```
