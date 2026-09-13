---
name: dlc-design
description: 설계. 컴포넌트 경계와 엔티티 소유권, 상호작용을 정하고(design.md), 대안을 비교한 결정 기록(decisions.md)과 요구사항을 모두 덮는 유닛 표(units.md)를 만든다. full 프로파일만.
disable-model-invocation: true
metadata:
  author: JK-Kim4
  version: "0.1.0"
---

# dlc-design — 설계

요구사항을 "무엇을 어디에 둘 것인가"로 옮긴다. 산출물 셋: `design.md`(컴포넌트·소유권·상호작용), `decisions.md`(대안을 비교한 결정 기록), `units.md`(구현 단위와 계약). express·bugfix 프로파일에는 이 단계가 없고 유닛 표는 plan이 만든다.

공통 절차는 [../dlc/references/protocol.md](../dlc/references/protocol.md), 출처 규칙과 ID 형식은 [../dlc/references/grounding.md](../dlc/references/grounding.md)에 있다. 스크립트 위치 `<skills>/dlc/scripts/dlc.py`의 뜻은 protocol.md의 "스크립트 위치" 절을 따른다. 아래는 이 단계에서만 다른 것이다.

## 읽을 것

- `requirements.md`. 모든 `FR<n>`·`NFR<n>`이 이 단계의 입력이며 유닛 표가 전부 덮어야 한다.
- `intent.md`의 `## 범위`·`## 타당성`. 범위 밖 항목을 컴포넌트로 만들지 않는다.
- `docs/dlc/practices.md`의 테스트·코드 스타일 절. 유닛 크기와 계약 형식(모듈 경계, 파일 크기 제한)에 영향을 준다.
- `docs/dlc/codebase.md`(brownfield). `## 구조`가 기존 컴포넌트 경계와 엔티티 소유권의 `[practice]` 출처다. 기존 경계를 바꾸는 설계는 ADR로 남긴다.

## 질문 주제

depth는 standard(5~8개)다. 앞 산출물에서 답이 나오는 주제는 묻지 않는다. 순서대로 빈 것만 묻는다.

| 순위 | 주제 | 묻는 것 |
|---|---|---|
| 1 | 컴포넌트 경계 | 요구사항 묶음을 어떤 경계로 나눌 것인가. brownfield면 기존 컴포넌트에 넣을지 새로 둘지 |
| 2 | 엔티티 소유권 | 두 컴포넌트가 같은 엔티티를 쓰고 싶어 할 때 누가 소유하고 나머지는 어떻게 읽는가 |
| 3 | 외부 계약 | 밖에서 부르는 형태(HTTP·CLI·이벤트·함수 호출)와 입력·출력 형식 |
| 4 | 저장과 상태 | 무엇을 어디에 저장하는가, 기존 저장소를 쓰는가 |
| 5 | 쟁점 결정 | 대안이 둘 이상인 지점. 각 대안의 비용·이득을 선택지로 보이고 고르게 한다 |
| 6 | 유닛 크기 | 구현 단위를 얼마나 잘게 나눌 것인가(유닛 하나가 한 세션에 끝나는 크기가 기준) |

선택지에는 대안의 이름만 쓰지 않고 "고르면 무엇이 달라지는지"를 한 줄씩 붙인다. 질문 파일은 작업 폴더의 `design-questions.md`. 형식과 답변 검사는 protocol.md.

**인터페이스 대안이 쟁점일 때.** 이 에이전트의 스킬 목록에 `craft:design-it-twice`(또는 `design-it-twice`)가 있으면 그 스킬의 절차로 대안 3개 이상을 만들어 비교한 뒤 그 결과를 5번 질문의 선택지로 쓴다. 로드 방법: Claude Code는 Skill 도구로 `craft:design-it-twice`를 호출하고(로드하기 전에는 다른 플러그인의 설치 경로를 알 수 없다), `npx skills add`로 설치한 Codex·Gemini CLI는 `<skills>/design-it-twice/SKILL.md`를 Read한다. 없으면 대안 2개 이상을 스스로 만들어 같은 방식으로 묻는다.

## 설계 규칙

- **한 엔티티는 한 컴포넌트가 소유한다.** 다른 컴포넌트는 소유 컴포넌트의 계약을 통해서만 읽고 쓴다. 두 컴포넌트가 같은 테이블·파일을 직접 고치는 설계는 내지 않는다.
- **컴포넌트마다 맡는 요구사항 ID를 적는다.** 어느 컴포넌트에도 없는 FR은 설계가 덜 된 것이다.
- **결정은 ADR로 남긴다.** 결정마다 대안 2개 이상과 각 대안의 기각 이유가 있어야 한다. 대안이 하나뿐이면 결정이 아니라 사실이며 design.md에 적는다.
- **유닛은 구현 순서의 단위다.** `depends_on`은 유닛 이름만 적고 순환이 없어야 한다. `covers`에 적은 ID를 모으면 requirements.md의 모든 최상위 FR/NFR이 나와야 한다(`dlc.py check design`이 잡는다). 하위 ID(`FR1.2`)를 맡으면 상위도 덮은 것으로 친다.
- **유닛 표는 `## 유닛` 절 안에만 둔다.** `dlc.py`는 이 절의 `| u<n>-<slug> | kind | depends_on | covers |` 행만 유닛으로 읽는다. `## 계약`의 표는 유닛이 아니다.

## 산출물 골격

### design.md

```markdown
# 설계

## 컴포넌트
| 컴포넌트 | 책임 | 맡는 요구사항 | 출처 |
|---|---|---|---|
| Inventory | 재고 수량의 조회와 변경 | FR1, FR2, NFR1 | [Q1] |
| AuditLog | 조회·변경 이력 기록 | FR3 | [Q1] [practice] |

## 엔티티 소유권
| 엔티티 | 소유 컴포넌트 | 다른 컴포넌트의 접근 | 출처 |
|---|---|---|---|
| Stock | Inventory | AuditLog는 이벤트로만 읽는다 | [Q2] |

## 상호작용
- 관리 화면 → Inventory: `GET /stock/{sku}` (FR1). [Q3]
- Inventory → AuditLog: `StockQueried` 이벤트, 비동기. [Q2] [ADR-1]

## 가정과 열린 질문
- 이벤트 브로커는 기존 것을 쓴다고 가정한다. [assumption]
```

### decisions.md

```markdown
# 결정 기록

## 결정

### ADR-1. 이력 기록은 이벤트로 분리한다
- 맥락: FR3 이력 기록이 조회 응답 시간(NFR1)에 영향을 주면 안 된다. [Q2]
- 대안 A. 조회 트랜잭션 안에서 동기 기록 — 기각: p95 300ms 목표에 DB 쓰기 1회가 더해진다. [Q4]
- 대안 B. 이벤트 발행 후 AuditLog가 비동기 기록 — 채택. [Q2]
- 대안 C. 배치로 하루 한 번 집계 — 기각: 이력이 실시간이어야 한다는 답과 충돌한다. [Q2]
- 결과: Inventory는 AuditLog를 모른다. 이벤트 유실 시 이력만 빠지고 조회는 영향 없다.

## 가정과 열린 질문
None.
```

### units.md

```markdown
# 유닛

## 유닛
| unit | kind | depends_on | covers |
|---|---|---|---|
| u1-stock-query | service | | FR1, NFR1 |
| u2-stock-change | service | u1-stock-query | FR2 |
| u3-audit-log | adapter | u1-stock-query | FR3 |

## 계약
| 계약 | 형태 | 제공 유닛 | 사용 측 | 출처 |
|---|---|---|---|---|
| 재고 조회 | `GET /stock/{sku}` → `{sku, total, byWarehouse[]}` | u1-stock-query | 관리 화면 | [Q3] |
| StockQueried | 이벤트 `{sku, at, actor}` | u1-stock-query | u3-audit-log | [ADR-1] |

## 가정과 열린 질문
None.
```

- `kind`는 한 단어다. 흔한 값: `service`(도메인 로직), `adapter`(외부 시스템·저장소 연결), `cli`, `ui`, `lib`(공용 코드), `infra`(설정·빌드). 다른 값을 써도 된다.
- `depends_on`은 쉼표로 구분한 유닛 이름. 없으면 빈칸.
- `## 계약`은 유닛 사이와 바깥으로 드러나는 인터페이스다. 형태에는 시그니처·경로·페이로드를 실제 이름으로 적는다. 구현 단계가 이 표를 seam 후보로 쓴다.
- ADR은 `## 결정` 절 아래 `### ADR-<n>.` 소절이다. 번호는 1부터 연속. design.md의 상호작용·units.md의 계약에서 `[ADR-<n>]`으로 가리킨다.

## 완료 기준

- `dlc.py check design`이 OK: design.md 필수 절 넷, decisions.md의 `## 결정`과 가정 절, units.md 필수 절 셋, 세 파일이 requirements.md에 없는 ID를 참조하지 않음, 유닛 표가 모든 최상위 FR/NFR을 덮음, 질문 파일의 모든 답변과 `Looks correct`.
- 모든 ADR에 대안 2개 이상과 기각 이유가 있다. 모든 엔티티에 소유 컴포넌트가 하나다.
- 사용자가 승인 게이트에서 승인했다(protocol.md 10단계). 승인 뒤 `dlc.py approve design`.

## 출력 언어

사용자 대면 출력과 산출물은 한국어. 코드, 식별자, 경로, 명령은 원문 유지.
