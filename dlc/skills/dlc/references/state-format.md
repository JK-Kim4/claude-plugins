# 상태와 산출물의 위치·형식

## 디렉터리

```
docs/dlc/
  active                      활성 작업 폴더 이름 한 줄. 사용자별 커서라 .gitignore 에 넣어도 된다
  codebase.md                 dlc-analyze 산출물. 저장소 단위라 작업 폴더 밖에 둔다
  practices.md                dlc-practices 산출물. 저장소 단위
  <YYMMDD>-<slug>/            작업 하나
    state.md                  dlc.py 가 관리. 손으로 고치지 않는다
    log.md                    전이·결정 기록. dlc.py 가 추가만 한다
    analyze-questions.md  practices-questions.md   (공유 산출물의 질문 파일도 작업 폴더에 둔다)
    intent.md
    intent-questions.md
    requirements.md
    requirements-questions.md
    design.md  decisions.md  units.md  design-questions.md
    plan.md  plan-questions.md   (design 이 없는 프로파일에서는 units.md 도 plan 이 만든다)
    build/<unit>.md           유닛마다 하나
    verify.md
```

애플리케이션 코드는 이 폴더에 두지 않는다. 프로젝트 저장소의 원래 위치에 쓴다.

작업 폴더 이름의 `<YYMMDD>`는 `dlc.py init`을 실행한 PC의 로컬 날짜다(사람이 보는 이름). `state.md`와 `log.md`의 시각은 UTC다. 자정 근처에는 둘이 하루 다를 수 있다.

## state.md

```markdown
# DLC State

- profile: express
- depth: minimal
- description: 재고 API
- created: 2026-09-13T02:10:00Z
- workspace: brownfield
- languages: kotlin, java
- build: gradle
- fingerprint: 3f9a1c0b2d4e

## Stages

| stage | status | updated | note |
|---|---|---|---|
| init | done | 2026-09-13T02:10:00Z | |
| analyze | pending | 2026-09-13T02:10:00Z | |
| requirements | pending | 2026-09-13T02:10:00Z | |
```

상태 값은 넷뿐이다.

| 값 | 뜻 |
|---|---|
| pending | 아직 시작 안 함 |
| active | 진행 중 (start 기록됨) |
| done | 승인됨 |
| skipped | 사유와 함께 건너뜀 |

프로파일에 없는 스테이지는 표에 아예 없다. `analyze`는 greenfield면 init 시점에 `skipped`로 기록되고, brownfield여도 `codebase.md`의 fingerprint가 현재 소스와 같으면 `next`가 건너뛴다. fingerprint는 소스 파일들의 경로와 내용을 함께 해시한 값이라 파일명이 같아도 내용이 바뀌면 달라진다. 건너뛴 analyze를 다시 돌리려면 `dlc.py start analyze --force`.

## 프로파일

| 프로파일 | 스테이지 | depth |
|---|---|---|
| full | init, analyze, intent, practices, requirements, design, plan, build, verify | standard |
| express | init, analyze, requirements, plan, build, verify | minimal |
| bugfix | express와 같음. requirements 질문이 재현·기대 동작·회귀 테스트 중심 | minimal |

## log.md

한 줄에 하나. `- <UTC 시각> | <stage> | <event> | <text>`. event는 created, start, approve, skip, note.

## 산출물 필수 절

`dlc.py check`가 보는 H2 목록이다. 스테이지 스킬의 골격과 같아야 한다.

| 산출물 | 필수 절 |
|---|---|
| codebase.md | 개요, 구조, 기술 스택, 관례와 제약, 가정과 열린 질문 |
| intent.md | 문제, 대상과 가치, 성공 지표, 범위, 타당성, 가정과 열린 질문 |
| practices.md | 작업 방식, 테스트, 배포, 코드 스타일, 가정과 열린 질문 |
| requirements.md | 의도 요약, 기능 요구사항, 비기능 요구사항, 제약, 범위 밖, 가정과 열린 질문 |
| design.md | 컴포넌트, 엔티티 소유권, 상호작용, 가정과 열린 질문 |
| decisions.md | 결정, 가정과 열린 질문 |
| units.md | 유닛, 계약, 가정과 열린 질문 |
| plan.md | 유닛 순서, Seam과 테스트 예산, 완료 정의, 가정과 열린 질문 |
| build/<unit>.md | 변경 파일, 추적성, 테스트, 가정과 열린 질문 |
| verify.md | 테스트 결과, 추적성, 리뷰 발견, 판정, 가정과 열린 질문 |

`build/<unit>.md`는 `units.md`의 유닛마다 하나이며, `## 추적성` 절에 적힌 FR/NFR을 모든 유닛에 걸쳐 모으면 requirements.md의 모든 최상위 ID를 덮어야 한다(`dlc.py check build`). `units.md`의 유닛 표는 `## 유닛` 절 안의 `| unit | kind | depends_on | covers |` 네 열 표이며, `unit`이 `u<n>-<slug>` 형식인 행만 유닛으로 읽는다(다른 절의 표는 무시). `covers`에 적힌 FR/NFR을 모아 requirements.md의 모든 최상위 ID를 덮어야 한다. design이 프로파일에 있고 건너뛰지 않았으면 design이, 없거나 skipped면 plan이 이 파일을 만들고 검사받는다. `codebase.md`는 첫 줄 근처에 `<!-- fingerprint: <값> -->`을 둔다. 값은 현재 소스의 지문이며 `dlc.py check analyze`가 다르면 기대 값을 알려준다(init 뒤 소스가 바뀌었으면 state.md의 값과 다를 수 있다). 유닛 표의 행 끝 `|`는 있어도 없어도 된다.
