---
name: dlc-plan
description: 구현 계획. 유닛 순서(의존 위상 정렬), 유닛별로 테스트할 seam, 통합테스트 예산, 완료 정의를 사용자와 합의해 plan.md를 만든다. design이 없는 프로파일(express·bugfix)에서는 units.md도 함께 만든다.
disable-model-invocation: true
metadata:
  author: JK-Kim4
  version: "0.1.0"
---

# dlc-plan — 구현 계획

구현 단계가 그대로 따를 순서와 테스트 약속을 정한다. 산출물 `plan.md`의 seam과 통합테스트 예산은 사용자와 **합의**한 것이어야 한다. 에이전트가 정해서 통보하지 않는다.

공통 절차는 [../dlc/references/protocol.md](../dlc/references/protocol.md), 출처 규칙과 ID 형식은 [../dlc/references/grounding.md](../dlc/references/grounding.md)에 있다. 스크립트 위치 `<skills>/dlc/scripts/dlc.py`의 뜻은 protocol.md의 "스크립트 위치" 절을 따른다. 아래는 이 단계에서만 다른 것이다.

## 읽을 것

- `requirements.md`. 수용 기준 줄이 seam 후보의 근거다.
- `units.md`(full 프로파일, design이 만든 것). `## 유닛`의 `depends_on`이 순서를, `## 계약`이 seam 후보를 준다.
- `design.md`·`decisions.md`(있으면). 상호작용과 ADR을 뒤집는 계획을 세우지 않는다.
- `docs/dlc/practices.md`의 `## 테스트` 절. 테스트 시점(구현 전·후)·수준·실행 명령·커버리지 목표가 `[practice]` 출처다. express·bugfix는 이 파일이 없을 수 있다. 그때는 실행 명령을 `docs/dlc/codebase.md`나 저장소의 빌드 파일에서 찾고, 없으면 질문한다.
- `state.md`의 `profile`. design이 없는 프로파일이면 아래 "유닛 표를 함께 만드는 경우"를 먼저 한다.

## 유닛 표를 함께 만드는 경우 (express·bugfix, 또는 design이 skipped)

`state.md`에서 design 행이 없거나 `skipped`면 이 단계가 `units.md`를 만든다. `dlc.py check plan`이 그때만 units.md의 필수 절과 요구사항 커버리지를 함께 검사한다.

- 유닛 분해안을 첫 질문으로 묻는다. 선택지마다 유닛 이름과 각 유닛이 맡는 FR/NFR을 보인다. minimal depth에서는 유닛 1~3개가 보통이다. bugfix는 대개 유닛 하나(결함 수정 + 회귀 테스트)다.
- 골격은 아래 `### units.md`. 규칙(`## 유닛` 절 안의 네 열 표, `covers`가 모든 최상위 FR/NFR을 덮음, `depends_on` 순환 없음)은 dlc-design과 같다.

## 질문 주제

depth minimal(express·bugfix)은 2~4개, standard(full)는 5~8개가 기준이다. 앞 산출물에서 답이 나오는 주제는 묻지 않는다. 순서대로 빈 것만 묻는다. full에서는 1번(유닛 분해)과 6번(테스트 수준)이 해당하지 않아 주제가 넷뿐이므로 5~8 기준을 채우려고 질문을 지어내지 않는다. 넷보다 적어도 된다.

| 순위 | 주제 | 묻는 것 |
|---|---|---|
| 1 | 유닛 분해 | (units.md를 이 단계가 만들 때만) 분해안 선택 |
| 2 | seam | 유닛마다 테스트를 다는 public 경계. 후보를 계약·수용 기준에서 뽑아 선택지로 보인다 |
| 3 | 통합테스트 예산 | 실제 인프라(DB·네트워크·파일시스템)를 쓰는 테스트의 대상과 개수. 기본 제안은 0 |
| 4 | 완료 정의 | 무엇이 되면 build가 끝인가. 전체 테스트 GREEN 외에 더 있는가(커버리지, 수동 확인, 문서) |
| 5 | 순서 조정 | 위상 정렬이 여러 순서를 허용할 때 어느 유닛을 먼저 할지. 위험한 것 먼저가 기본 제안 |
| 6 | 테스트 수준 | (practices.md가 없을 때) 단위·통합 중 어디까지, 실행 명령 |

질문 파일은 작업 폴더의 `plan-questions.md`. 형식과 답변 검사는 protocol.md.

## seam과 예산

- **seam**은 테스트가 사는 public 경계다. 내부 구조가 바뀌어도 테스트가 살아남는 곳(함수 시그니처, HTTP 경로, CLI 인자와 출력, 이벤트 페이로드)이다. private 메서드나 내부 협력자는 seam이 아니다.
- 유닛마다 seam이 하나 이상 있어야 한다. seam이 없는 유닛은 "테스트 없이 구현"이라는 뜻이며 사용자가 명시적으로 그렇게 답한 경우에만 허용하고 가정 절에 남긴다.
- **통합테스트 예산**은 실제 인프라를 쓰는 테스트의 개수다. 기본 0. 예산을 넘겨야 할 이유가 있으면 이유와 함께 선택지로 묻는다. 구현 단계는 이 숫자를 넘지 않는다.
- 이 에이전트의 스킬 목록에 `craft:test-first`(또는 `test-first`)가 있으면 그 스킬의 "Seam"·"테스트 비용 규율" 절이 seam·예산의 정의 원천이다. 여기 요약과 다르면 그쪽을 따른다. 로드 방법: Claude Code는 Skill 도구로 `craft:test-first`를 호출하고(로드하기 전에는 다른 플러그인의 설치 경로를 알 수 없다), `npx skills add`로 설치한 Codex·Gemini CLI는 `<skills>/test-first/SKILL.md`를 Read한다.

## 순서

유닛 순서는 `depends_on`의 위상 정렬이다. 순환이 있으면 멈추고 사용자에게 알린다. full이면 design이 이미 `done`이라 되돌릴 전이가 없다. 사용자 결정으로 `units.md`의 `depends_on`을 고치고 `dlc.py check design`을 다시 돌려 커버리지·ID 참조가 여전히 OK인지 확인한 뒤, 고친 내용을 `dlc.py note plan "<무엇을 고쳤는가>"`로 남긴다(`check`는 어느 스테이지든 다시 실행할 수 있다). 이 단계가 units.md를 만들었으면 여기서 바로 고친다. 같은 깊이의 유닛이 여럿이면 5번 질문으로 정하거나, 묻지 않기로 했으면 "의존받는 수가 많은 것 먼저"를 쓰고 가정 절에 적는다.

## 산출물 골격

### plan.md

```markdown
# 구현 계획

## 유닛 순서
| 순서 | unit | depends_on | covers | 이유 | 출처 |
|---|---|---|---|---|---|
| 1 | u1-stock-query | | FR1, NFR1 | 다른 유닛이 의존한다 | [Q2] |
| 2 | u2-stock-change | u1-stock-query | FR2 | | [Q2] |

## Seam과 테스트 예산
| unit | seam | 테스트 수준 | 실제 인프라 | 출처 |
|---|---|---|---|---|
| u1-stock-query | `GET /stock/{sku}` 응답 (200·404, 페이로드) | 단위 (저장소는 인메모리 대체) | 0 | [Q1] [practice] |
| u2-stock-change | `changeStock(sku, delta)` 반환값과 이후 조회 결과 | 단위 | 0 | [Q1] |

통합테스트 예산: 총 0건. [Q3]
실행 명령: `./gradlew test` [practice]

## 완료 정의
- 모든 유닛의 `build/<unit>.md`가 있고 `dlc.py check build`가 OK. [practice]
- 전체 테스트 GREEN, 새 코드 커버리지 80% 이상(practices.md). [practice]
- FR마다 수용 기준을 확인하는 테스트가 seam에 하나 이상. [Q4]

## 가정과 열린 질문
- 부하 테스트(NFR1)는 이번 build에서 하지 않고 verify에서 수동 측정한다. [assumption]
```

### units.md

design이 없는 프로파일에서만 이 단계가 만든다. 골격은 dlc-design과 같다.

```markdown
# 유닛

## 유닛
| unit | kind | depends_on | covers |
|---|---|---|---|
| u1-stock-query | service | | FR1, NFR1 |

## 계약
| 계약 | 형태 | 제공 유닛 | 사용 측 | 출처 |
|---|---|---|---|---|
| 재고 조회 | `GET /stock/{sku}` → `{sku, total}` | u1-stock-query | 관리 화면 | [Q1] |

## 가정과 열린 질문
None.
```

- `## 유닛 순서` 표의 unit 집합은 units.md의 유닛 집합과 같아야 한다. 빠지거나 더해진 유닛이 없다. `dlc.py check plan`이 두 집합을 비교한다.
- `## Seam과 테스트 예산` 표의 데이터 행마다 출처를 단다. seam은 질문으로 합의한 `[Q<n>]`이거나 계약 표에서 그대로 가져온 것이어야 한다.
- 실행 명령이 없으면 build가 테스트를 돌릴 수 없다. `## Seam과 테스트 예산` 절에 `실행 명령: <명령>` 줄을 반드시 하나 둔다. `dlc.py check plan`이 이 줄을 찾는다.

## 완료 기준

- `dlc.py check plan`이 OK: plan.md 필수 절 넷, requirements.md에 없는 ID 참조 없음, 유닛 순서 표의 유닛 집합 = units.md 유닛 집합, `실행 명령:` 줄 존재, 질문 파일의 모든 답변과 `Looks correct`, 가정 절. 이 단계가 units.md를 만들었으면 그 필수 절과 요구사항 커버리지도.
- 모든 유닛에 seam이 있고(예외는 가정 절에), 통합테스트 예산이 숫자로 적혀 있고, 실행 명령이 있다.
- 사용자가 승인 게이트에서 승인했다(protocol.md 10단계). 승인 뒤 `dlc.py approve plan`.

## 출력 언어

사용자 대면 출력과 산출물은 한국어. 코드, 식별자, 경로, 명령은 원문 유지.
