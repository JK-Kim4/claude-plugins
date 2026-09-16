---
name: dlc-practices
description: 팀 관행을 확정한다. 작업 방식·테스트·배포·코드 스타일 네 영역을 기존 코드의 증거로 채우고 빈 것만 물어 docs/dlc/practices.md를 만든다.
disable-model-invocation: true
metadata:
  author: JK-Kim4
  version: "0.1.0"
---

# dlc-practices — 팀 관행 확정

뒤 단계(계획·구현·검증)가 따를 작업 규칙을 한 곳에 적는다. 산출물 `docs/dlc/practices.md`는 작업 폴더 밖에 있어 같은 저장소의 모든 작업이 공유한다. express·bugfix 프로파일에는 이 단계가 없다.

공통 절차는 [../dlc/references/protocol.md](../dlc/references/protocol.md), 출처 규칙은 [../dlc/references/grounding.md](../dlc/references/grounding.md)에 있다. 스크립트 위치 `${CLAUDE_PLUGIN_ROOT}/skills/dlc/scripts/dlc.py`의 뜻은 protocol.md의 "스크립트 위치" 절을 따른다. 아래는 이 단계에서만 다른 것이다.

## 읽을 것

- `state.md`의 `workspace`·`languages`·`build`.
- `docs/dlc/codebase.md`(brownfield일 때). "관례와 제약"·"기술 스택" 절이 네 영역의 주 증거다.
- `intent.md`(있으면). 제약 절의 기한·규제가 배포·테스트 관행에 영향을 준다.
- `docs/dlc/practices.md`가 이미 있으면 **갱신 모드**다. 다른 작업이 이미 확정한 내용을 이 작업이 바꾸면 그 작업에도 영향이 가므로, 바꾸는 항목은 반드시 사용자에게 "기존 값 → 새 값, 다른 작업에도 적용됨"을 알리고 확인받는다. 바꿀 것이 없으면 질문 파일 없이 `dlc.py check practices` 뒤 승인 게이트로 간다.

## 네 영역과 묻는 것

| 영역 | 항목 |
|---|---|
| 작업 방식 | 브랜치를 어떻게 쓰는가, 커밋 단위, 코드 리뷰를 누가 언제 하는가, 작업 추적(이슈·티켓) |
| 테스트 | 테스트를 언제 쓰는가(구현 전·후), 어느 수준까지(단위·통합·E2E), 커버리지 목표, 실행 명령 |
| 배포 | 어느 환경이 있는가, 무엇이 자동인가, 되돌리는 방법, 배포 전 확인 항목 |
| 코드 스타일 | 린터·포맷터, 네이밍, 파일·함수 크기 제한, 금지 패턴 |

**brownfield.** codebase.md에서 읽히는 항목은 `[practice]` 태그로 그대로 채우고, 코드에 드러나지 않는 것만 묻는다. 예: 린터 설정은 코드에 있지만 "리뷰를 누가 하는가"는 없다.

**greenfield.** 증거가 없으므로 네 영역을 다 묻되, 각 질문의 A 선택지에 제안 답을 두고 "(제안)"을 붙인다. 제안 답은 다음 기본값이다.

| 영역 | 제안 답 | 질문에 쓰는 표현 (프레임워크 용어 없이) |
|---|---|---|
| 작업 방식 | trunk-based | "모두 한 주 브랜치에 바로 합치고, 브랜치는 하루 이틀짜리 짧은 것만 쓴다" |
| 테스트 | test-after, 커버리지 80% | "기능을 구현한 뒤 같은 작업 안에서 테스트를 쓰고, 새 코드의 8할 이상을 테스트가 지나가게 한다" |
| 배포 | staging 자동 배포 | "주 브랜치에 합쳐지면 검증용 서버에 자동으로 올라가고, 실서비스 배포는 사람이 버튼을 누른다" |
| 코드 스타일 | 프로젝트 린터 우선 | "언어 표준 린터·포맷터를 설정해 두고 그 결과를 스타일의 기준으로 삼는다" |

사용자가 다른 것을 고르면 그것이 답이다. 제안은 선택지일 뿐 기본 적용이 아니다. "(제안)" 표시는 위 표의 네 기본값에만 붙인다. 표에 없는 항목(커밋 형식, 롤백 방법 등)은 제안 없이 선택지만 나열한다.

## 질문 수

depth를 따른다(full은 standard, 5~8개). brownfield는 빈 항목 수만큼이라 그보다 적을 수 있다. 네 영역 중 하나라도 증거도 답도 없는 채로 두지 않는다. 질문 파일은 작업 폴더의 `practices-questions.md`. 형식과 답변 검사는 protocol.md.

## 산출물 골격

### practices.md

```markdown
# 팀 관행

## 작업 방식
| 항목 | 내용 | 출처 |
|---|---|---|
| 브랜치 | `feature/<설명>` 브랜치, PR로 `main`에 합친다 | [practice] |
| 커밋 | `<type>(<scope>): <설명>` 형식, 하나의 논리 변경 단위 | [practice] |
| 리뷰 | PR마다 팀원 1명 승인 | [Q1] |

## 테스트
| 항목 | 내용 | 출처 |
|---|---|---|
| 시점 | 도메인 로직은 테스트 먼저, 어댑터는 구현 뒤 | [Q2] |
| 수준 | 단위 + 통합(TestContainers). E2E 없음 | [practice] |
| 실행 | `./gradlew test` | [practice] |

## 배포
| 항목 | 내용 | 출처 |
|---|---|---|
| 환경 | dev, staging, prod | [Q3] |
| 자동화 | main 머지 시 staging 자동, prod는 수동 승인 | [Q3] |
| 롤백 | 이전 이미지 태그로 재배포 | [Q4] |

## 코드 스타일
| 항목 | 내용 | 출처 |
|---|---|---|
| 린터 | ktlint, 커밋 전 `./gradlew ktlintCheck` | [practice] |
| 크기 | 함수 60줄, 파일 300줄 이하 | [practice] |

## 가정과 열린 질문
- prod 배포 승인자는 미정. [assumption]
```

- 네 영역 절은 모두 `항목 | 내용 | 출처` 표다. 데이터 행마다 태그를 단다.
- 갱신 모드에서 바뀐 행은 `dlc.py note practices "<항목>: <기존> → <새 값>"`으로 기록한다.

## 완료 기준

- `dlc.py check practices`가 OK: 필수 절 다섯 개, 질문 파일이 있으면 그 모든 답변과 `Looks correct`, 가정 절.
- 네 영역에 빈 표가 없다.
- 사용자가 승인 게이트에서 승인했다(protocol.md 10단계). 승인 뒤 `dlc.py approve practices`.

## 출력 언어

사용자 대면 출력과 산출물은 한국어. 코드, 식별자, 경로, 명령은 원문 유지.
