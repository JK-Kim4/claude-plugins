---
name: pr-reviewer
description: >-
  지정한 GitHub PR을 컨벤션 리뷰와 코드 리뷰(보안 취약점·동시성 이슈·로직 오류)
  두 축으로 분석해, P0~P2 우선순위 라벨을 단 단일 PR Review(요약 + 인라인 코멘트)로
  게시한다. 사용자가 "이 PR 리뷰해줘", "PR 코드리뷰 코멘트 달아줘", "#123 리뷰해줘",
  "PR 컨벤션 점검", "이 풀리퀘스트 봐줘" 등 특정 PR에 리뷰 코멘트를 남기려 할 때 사용한다.
  대상 PR 번호 또는 URL이 반드시 필요하다. PR 생성·push·머지는 이 스킬의 범위가 아니다
  (그쪽은 pr-automator).
---

# PR Reviewer

지정한 GitHub PR을 **컨벤션 리뷰 + 코드 리뷰** 두 축으로 분석해, 우선순위(P0~P2)
라벨을 단 **단일 PR Review**로 일괄 게시한다. 핵심 순서는
**사전 점검 → PR 수집 → 컨벤션 확정 → 리뷰 분석 → 게시 → 보고**이다.

원칙:
- 추측하지 않는다. 불확실한 지적은 "가능성"으로 명시하거나 빼고, 검증 안 한 것을 단정하지 않는다.
- diff에 실제로 존재하는 변경만 리뷰 대상으로 삼는다.
- 작성 언어 기본값은 한국어(코드·식별자·명령어는 원문 유지).
- 승인/변경요청 판정(APPROVE/REQUEST_CHANGES)은 자동으로 하지 않는다. 항상 `COMMENT`로 게시한다.

## 1단계: 사전 점검

다음을 확인하고, 하나라도 실패하면 무엇이 빠졌는지 알리고 중단한다.

```bash
git rev-parse --is-inside-work-tree   # git 레포인지
gh auth status                         # gh 설치·인증
```

- **대상 PR 식별자(번호 또는 URL)가 프롬프트에 없으면** → 사용자에게 요청하고 중단한다. 임의로 현재 브랜치 PR을 추정하지 않는다.
- git 레포가 아니거나 `gh` 미설치·미인증이면 → 설치(`brew install gh`)·인증(`gh auth login`) 안내 후 중단.

## 2단계: PR 수집

대상 PR의 메타데이터와 diff를 가져온다.

```bash
gh pr view <번호|URL> --json number,title,headRefOid,baseRefName,url,files
gh pr diff <번호|URL>
```

- `headRefOid`(head SHA)는 게시 단계에서 commit_id로 쓴다.
- diff에서 **파일별 변경 라인 번호와 side**를 파악한다. 이것이 인라인 코멘트 매핑의 근거다.
- diff가 비어 있으면(변경 없음) 안내 후 중단한다.

## 3단계: 컨벤션 확정 (리뷰 기준, 레포당 1회)

설정 파일 경로: 레포 루트의 `.claude/pr-reviewer.json` (pr-automator의 설정과 별개 파일).

해석 순서:
1. 설정 파일이 있으면 → 읽어서 그대로 사용한다(질문하지 않음). 단 사용자가 "컨벤션 다시 설정"이라고 하면 2번부터 다시 한다.
2. 없으면 → **기술 스택을 탐지**하고(매니페스트·확장자, `references/conventions.md` 참고) 사용자에게 **인터뷰**한다:
   - "팀/프로젝트 코드 컨벤션 문서가 있나요?" (예: `CONTRIBUTING.md`, 스타일 가이드, 린터 설정)
   - **있음** → 그 위치를 최우선 리뷰 기준으로 삼고 경로를 기록한다(`conventionSource: "doc"`).
   - **없음** → 탐지된 스택의 **범용 컨벤션**을 기준으로 삼는다(`conventionSource: "universal"`).
3. 확정값을 `.claude/pr-reviewer.json`에 저장한다(아래 형식).

설정 파일 형식:
```json
{
  "stack": ["kotlin", "spring"],
  "conventionSource": "doc",
  "conventionRef": "CONTRIBUTING.md",
  "language": "ko"
}
```

- `stack`: 탐지된 기술 스택 식별자 배열
- `conventionSource`: `doc`(팀 문서 존재) | `universal`(스택 범용)
- `conventionRef`: `doc`일 때 컨벤션 문서 경로. `universal`이면 `null`
- `language`: 리뷰 작성 언어(기본 `ko`)

설정 파일은 기본적으로 git에 커밋한다(팀 공유 → 레포 전체 일관성). 단 `.gitignore`에서 `.claude/`가 무시되고 있으면 사용자에게 알리고 그 정책을 따른다.

## 4단계: 리뷰 분석

두 축으로 분석하고, 각 지적에 우선순위(P0~P2)를 매긴다. 기준 체크리스트는 `references/review-criteria.md`, 컨벤션 해석은 `references/conventions.md`를 따른다.

**축 A. 컨벤션 리뷰**
- `conventionSource: "doc"`이면 그 문서가 **권위 기준**이다. 범용 베스트프랙티스와 충돌하면 **팀 문서를 우선**한다.
- `conventionSource: "universal"`이면 스택 범용 컨벤션(네이밍·구조·언어 관용구)으로 점검한다.

**축 B. 코드 리뷰** (스택 특성 반영)
- 보안 취약점 / 동시성 이슈 가능 지점 / 로직 오류

**우선순위 매핑**

| 라벨 | 의미 | 예 |
|------|------|-----|
| 🔴 P0 | 치명 — 머지 전 반드시 수정 | 명확한 보안 취약점, 데이터 손상·크래시 유발 로직 오류 |
| 🟠 P1 | 중요 — 수정 권장 | 동시성 이슈, 버그 가능성, 팀 강제 컨벤션 위반 |
| 🟡 P2 | 제안 — 선택적 개선 | 가독성, 경미한 컨벤션·스타일 |

## 5단계: 게시

`references/posting.md`의 형식대로 **단일 PR Review**(요약 본문 + 인라인 코멘트)를 구성한다.

게시 **직전에 한 줄 고지**한다(별도 승인 대기는 없음):

> "총 N건 — 🔴 P0 x · 🟠 P1 y · 🟡 P2 z 를 PR #<번호>에 제출합니다."

고지 후 즉시 제출한다. 제출 실패 시 원인을 그대로 전달하고 중단한다(임의 재시도·우회 금지).

## 6단계: 마무리 보고

게시한 코멘트 수, 우선순위 분포(P0/P1/P2), 생성된 Review URL을 간결히 보고한다.
