---
name: pr-automator
description: >-
  현재 브랜치의 작업을 원격에 push하고 GitHub PR을 생성하는 것을 자동화한다.
  사용자가 "PR 올려줘/만들어줘", "푸시하고 PR", "이 브랜치 올려줘",
  "작업 끝났으니 PR 생성", "push하고 풀리퀘스트 열어줘" 등 브랜치 작업을
  원격에 반영하고 PR을 만들려 할 때 사용한다. 커밋 컨벤션을 레포당 1회 확정·저장하고,
  미커밋 변경 커밋·기본 브랜치 안전장치·기존 PR 갱신까지 처리한다.
  단순 git push만 원하거나(PR 의도 없음) 코드 리뷰·머지 자체는 이 스킬의 범위가 아니다.
---

# PR Automator

현재 브랜치의 작업을 GitHub PR로 올리는 흐름을 자동화한다. 핵심 순서는
**컨벤션 확정 → 커밋 → push → PR 생성**이다. 코드 리뷰·머지는 범위 밖이다.

원칙:
- 추측하지 않는다. 불확실하면 멈추고 사용자에게 확인한다.
- 검증하지 않은 것을 PR 본문에 검증했다고 쓰지 않는다.
- 작성 언어 기본값은 한국어(코드·식별자·명령어는 원문 유지).

## 1단계: 사전 점검

다음을 순서대로 확인하고, 하나라도 실패하면 무엇이 빠졌는지 알리고 중단한다.

```bash
git rev-parse --is-inside-work-tree   # git 레포인지
gh auth status                         # gh 설치·인증
git remote get-url origin              # origin 원격 존재
```

- git 레포가 아니면: "여기는 git 레포가 아닙니다" 안내 후 중단.
- `gh` 미설치/미인증이면: 설치(`brew install gh`) 또는 `gh auth login` 안내 후 중단.
- origin 이 없으면: 원격을 먼저 추가해 달라고 안내 후 중단.

## 2단계: 브랜치 안전장치

현재 브랜치와 기본 브랜치를 확인한다.

```bash
git branch --show-current
git remote show origin | sed -n 's/.*HEAD branch: //p'   # 기본 브랜치명
```

현재 브랜치가 기본 브랜치(main/master 등)와 같으면:
1. 변경 내용·맥락에 맞는 작업 브랜치명을 제안한다(예: `feat/login-form`). 컨벤션 설정이 있으면 그 톤을 따른다.
2. 사용자에게 이 이름으로 만들지 확인받는다.
3. 승인되면 새 브랜치를 만들고 전환한다: `git switch -c <브랜치명>` (작업 중 변경은 그대로 따라온다).
4. 사용자가 다른 이름을 원하면 그 이름을 쓴다.

현재 브랜치가 기본 브랜치가 아니면 이 단계는 건너뛴다.

## 3단계: 커밋 컨벤션 확정 (커밋 메시지 생성 전 1회)

설정 파일 경로: 레포 루트의 `.claude/pr-automator.json`.

해석 순서:
1. 설정 파일이 있으면 → 읽어서 그대로 사용한다(질문하지 않음). 단, 사용자가 "컨벤션 다시 설정"이라고 요청하면 아래 2번부터 다시 한다.
2. 없으면 → 사용자에게 어떤 커밋 컨벤션을 쓸지 묻는다. `references/conventions.md` 의 카탈로그를 후보로 제시한다(기본 후보: Conventional Commits). 답이 있으면 그 값으로 확정한다.
3. 사용자가 답하지 않으면(생략/모름) → 기존 커밋 히스토리를 분석해 추론한다(`references/conventions.md` 의 `inferred` 절차).
4. 히스토리도 없으면(첫 커밋) → Conventional Commits(범용)을 쓴다.
5. 확정값을 설정 파일에 저장한다(아래 형식). `resolvedFrom` 으로 출처를 기록한다.

설정 파일 형식:
```json
{
  "commitConvention": "conventional-commits",
  "language": "ko",
  "prBodyTemplate": "summary-changes-test",
  "resolvedFrom": "user"
}
```

- `commitConvention`: `conventional-commits` | `inferred` | 사용자가 설명한 규칙 문자열
- `language`: 커밋·PR 작성 언어 (기본 `ko`)
- `prBodyTemplate`: PR 본문 템플릿 식별자 (기본 `summary-changes-test`)
- `resolvedFrom`: `user` | `inferred-from-history` | `default`

설정 파일은 기본적으로 git에 커밋한다(팀 공유 → 레포 전체 일관성). 단 해당 레포의 `.gitignore`에서 `.claude/`가 무시되고 있으면 사용자에게 알리고 그 정책을 따른다.

## 4단계: 변경 커밋

```bash
git status --porcelain   # 변경 유무 확인
```

- 출력이 비어 있으면(미커밋 변경 없음) → 이 단계 건너뜀.
- 변경이 있으면:
  1. `git status` / `git diff` 로 무엇이 바뀌었는지 파악한다.
  2. 확정된 컨벤션에 맞는 커밋 메시지를 만든다(`references/conventions.md` 참고). 검증 안 한 것을 했다고 쓰지 않는다.
  3. 커밋한다:
     ```bash
     git add -A
     git commit -m "<생성한 메시지>"
     ```
  4. 변경 범위가 서로 다른 성격이면 한 줄 요약으로 묶되, 명백히 분리되는 작업이면 여러 커밋으로 나눠도 된다(과도하게 쪼개지 않는다).

## 5단계: Push

현재 브랜치를 origin 에 upstream 설정과 함께 push 한다.

```bash
git push -u origin HEAD
```

push 실패 시(예: 원격이 앞서 있음) 원인을 사용자에게 그대로 전달하고 중단한다. 임의로 force push 하지 않는다.

## 6단계: PR 처리

먼저 이 브랜치에 열린 PR이 있는지 확인한다.

```bash
gh pr view --json number,url,state 2>/dev/null
```

- **열린 PR이 이미 있으면**: 새 PR을 만들지 않는다. 방금 push가 그 PR에 반영됐음을 알리고 PR 번호·URL을 안내한다.
- **없으면** 새 PR을 만든다:
  1. base 브랜치 확정:
     - 사용자가 base 를 명시했으면 그 값을 쓴다.
     - 명시하지 않았으면 **인터뷰**한다. 원격 기본 브랜치(2단계에서 구한 값)를 기본 후보로 제시하고 확인받는다.
  2. 확정 컨벤션 기반 PR 제목과 `summary-changes-test` 템플릿 기반 본문을 만든다(`references/conventions.md`). 본문은 실제 커밋·diff에 근거해 작성하고, 검증하지 않은 것을 검증했다고 쓰지 않는다.
  3. **Ready** 상태로 PR을 만든다(draft 아님):
     ```bash
     gh pr create --base <base> --title "<제목>" --body "<본문>"
     ```
  4. 생성된 PR URL을 사용자에게 안내한다.

리뷰어·라벨은 자동 지정하지 않는다(사용자가 GitHub에서 직접).

## 마무리

완료 후 사용자에게 다음을 간결히 보고한다: 만들어진/전환된 브랜치, 커밋 여부, push 결과, PR URL(또는 갱신된 기존 PR 링크).
