---
name: worktree
description: 사용자가 `$worktree`를 명시적으로 호출했을 때만 사용한다. 선택적으로 브랜치명을 받아 최신
  `origin/develop` 기준의 격리 Git worktree를 생성하고 이후 작업 경로를 그 worktree로 고정한다. 일반적인 코드
  변경 요청만으로 자동 호출하지 않는다.
---
# Worktree

사용자가 명시적으로 요청한 Git worktree를 안전하게 생성한다. 이 스킬은 일반적인 구현 요청만으로 실행하지 않는다.

## 호출 계약

다음 두 형식을 지원한다.

```text
$worktree <branch-name>
$worktree
```

- 브랜치명이 주어지면 그대로 사용한다.
- 브랜치명이 없고 현재 작업 문맥이 명확하면 이름을 자동 생성한다.
- 이슈·스펙 번호가 있으면 번호와 간결한 작업명을 결합한다. 예: `058-feature-name`.
- 번호가 없으면 명확한 작업 목적을 lowercase kebab-case로 변환한다.
- 문맥이 모호하면 추측하지 말고 브랜치명만 한국어로 질문한다.

## 완료 조건

다음을 모두 만족해야 완료다.

- 최신 `origin/develop`과 같은 커밋에서 새 로컬 브랜치가 시작된다.
- 프로젝트의 주 worktree 아래 `.worktrees/<branch-name>`에 격리 worktree가 생성된다.
- 이후 모든 파일 읽기·쓰기·명령 실행은 새 worktree를 작업 디렉터리로 사용한다.
- 생성 경로, 브랜치명, 기준 커밋을 사용자에게 한국어로 보고한다.

## 절차

1. 현재 위치가 Git 저장소인지 `git rev-parse --show-toplevel`로 확인한다. 저장소가 아니면 오류를 보고하고 중단한다.
2. `git worktree list --porcelain`을 읽어 주 worktree의 절대 경로를 확정한다. 현재 연결 worktree 안에서 호출됐더라도 그 안에 중첩 worktree를 만들지 않는다.
3. 주 worktree의 `.worktrees`가 `git check-ignore -q .worktrees`로 ignore되는지 확인한다. ignore되지 않으면 메인 디렉터리나 `.gitignore`를 수정하지 말고 오류로 중단한다.
4. 호출 계약에 따라 브랜치명을 결정하고 `git check-ref-format --branch <branch-name>`으로 검증한다. 유효하지 않으면 오류로 중단한다.
5. 주 worktree에서 `git fetch origin develop`을 실행한다. fetch가 실패하거나 `refs/remotes/origin/develop`이 존재하지 않으면 다른 브랜치를 대신 사용하지 말고 오류로 중단한다.
6. 다음 충돌을 모두 확인한다.
   - 같은 이름의 로컬 브랜치
   - 같은 이름의 원격 브랜치
   - 같은 브랜치를 사용하는 기존 worktree
   - 생성 대상 경로에 이미 존재하는 파일 또는 디렉터리
7. 충돌이 하나라도 있으면 기존 항목을 재사용·삭제하거나 숫자 접미사를 붙이지 말고 정확한 충돌 원인을 보고한 뒤 중단한다.
8. 주 worktree에서 다음 명령과 동등한 방식으로 생성한다.

```bash
git worktree add ".worktrees/<branch-name>" \
  -b "<branch-name>" \
  origin/develop
```

9. 새 worktree에서 다음을 검증한다.
   - 현재 브랜치가 요청한 브랜치명과 같다.
   - `HEAD`가 갱신된 `origin/develop`과 같다.
   - `git status --short`가 비어 있다.
10. 이후 도구 호출의 `cwd` 또는 `workdir`를 새 worktree 절대 경로로 지정한다. 원래 디렉터리에서 작업을 계속하지 않는다.
11. 같은 사용자 요청에 구현 작업이 포함되어 있으면 새 worktree의 프로젝트 지침을 다시 읽은 뒤 그 위치에서 계속한다. worktree 생성만 요청됐다면 생성 결과를 보고하고 종료한다.

## 중단 규칙

다음 상황에서는 예외 없이 오류를 보고하고 중단한다.

- `origin/develop`이 없거나 갱신할 수 없음
- 브랜치명이나 작업 문맥이 모호함
- 브랜치·worktree·경로 충돌
- `.worktrees`가 ignore되지 않음
- 생성 후 브랜치·기준 커밋·clean 상태 검증 실패

작업이 사소하거나 긴급하다는 이유로 기준 브랜치를 바꾸거나 메인 디렉터리에서 먼저 수정하지 않는다.
