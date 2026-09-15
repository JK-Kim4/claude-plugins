---
name: dlc-build
description: 구현. plan.md의 유닛 순서대로, 합의된 seam에서 실패하는 테스트를 먼저 쓰고 통과시키는 방식으로 코드를 프로젝트 원래 위치에 쓴다. 유닛마다 build/<unit>.md(변경 파일, 요구사항→파일 추적, 테스트 결과)를 남기고 사용자에게 보고한다.
disable-model-invocation: true
metadata:
  author: JK-Kim4
  version: "0.1.0"
---

# dlc-build — 구현

계획을 코드로 옮긴다. 코드는 프로젝트 저장소의 원래 위치(`src/`, `lib/`, `tests/` 등)에 쓰고, 작업 폴더에는 유닛마다 기록 `build/<unit>.md` 하나만 남긴다. 질문 파일이 없는 스테이지다. 빈 곳은 질문이 아니라 계획으로 돌아가 채운다.

공통 절차는 [../dlc/references/protocol.md](../dlc/references/protocol.md), 출처 규칙과 ID 형식은 [../dlc/references/grounding.md](../dlc/references/grounding.md)에 있다. 스크립트 위치 `${CLAUDE_PLUGIN_ROOT}/skills/dlc/scripts/dlc.py`의 뜻은 protocol.md의 "스크립트 위치" 절을 따른다. protocol.md의 4~7단계(질문·답변·요약 확인)는 이 단계에 없다. 아래는 이 단계에서만 다른 것이다.

## 읽을 것

- `plan.md`. `## 유닛 순서`가 진행 순서, `## Seam과 테스트 예산`이 유닛별 테스트 약속, `## 완료 정의`가 끝의 기준이다.
- `units.md`의 `## 계약`. 시그니처·경로·페이로드를 여기 적힌 이름 그대로 구현한다.
- `requirements.md`. 유닛의 `covers`에 적힌 FR의 수용 기준이 첫 테스트의 기대값이다.
- `design.md`·`decisions.md`(full). 컴포넌트 경계와 ADR을 구현이 뒤집지 않는다.
- `docs/dlc/practices.md`의 `## 테스트`·`## 코드 스타일` 절(있으면). 테스트 시점·수준·실행 명령·린터가 `[practice]` 출처다. 없으면 plan.md의 실행 명령을 쓴다.
- `docs/dlc/codebase.md`(brownfield). 기존 관례(디렉터리 배치, 네이밍, 테스트 위치)를 따른다.

## 테스트 규율의 원천

이 에이전트의 스킬 목록에 `craft:test-first`(또는 `test-first`)가 있으면 그 스킬 본문이 테스트 규율의 원천이다. 첫 유닛을 시작하기 전에 한 번 로드해 그대로 따른다. 로드 방법은 에이전트마다 다르다. Claude Code는 Skill 도구로 `craft:test-first`를 호출한다(로드하기 전에는 다른 플러그인의 설치 경로를 알 수 없다. 로드 결과 첫 줄에 절대 경로가 온다). `npx skills add`로 설치한 Codex·Gemini CLI는 `<skills>/test-first/SKILL.md`를 Read한다. 목록에 있는데 로드하지 않고 폴백으로 가지 않는다. 이 스킬은 seam 확인·예산·기록만 자기 절차로 갖는다.

*(폴백)* craft:test-first가 없으면 다음 다섯 줄이 규율이다.

1. **Red before green.** 실패하는 테스트를 먼저 쓰고 실패를 눈으로 확인한 뒤, 통과할 만큼만 구현한다.
2. **한 번에 슬라이스 하나.** 사이클마다 seam 하나, 테스트 하나, 최소 구현 하나. 테스트를 한꺼번에 쓰고 구현을 한꺼번에 하지 않는다.
3. **행위당 테스트 하나.** public 경계(seam)에서 행위를 검증한다. private 메서드, 내부 협력자 mock, 사이드 채널(DB 직접 조회) 검증은 하지 않는다.
4. **최저 충분 레벨.** 순수 로직은 인프라 없이 단위 테스트로. 실제 인프라를 쓰는 테스트는 plan.md의 예산 안에서만.
5. **기대값은 독립 출처에서.** 수용 기준, 손으로 푼 예제, 알려진 정답 리터럴. 코드와 같은 방식으로 재계산한 기대값은 쓰지 않는다. 리팩토링은 이 루프의 일부가 아니다(verify의 리뷰 발견으로 넘긴다).

Claude Code에 `craft` 플러그인이 있으면 사용자가 이 단계 대신 `craft:implement-spec`를 쓸 수도 있다고 한 번 안내한다. 그 스킬은 명시 호출형이라 이 스킬이 대신 부를 수 없고, 사용자가 그쪽을 골라도 아래 기록(`build/<unit>.md`)과 승인 게이트는 그대로 필요하다.

## 유닛 하나의 순서

plan.md의 순서대로 유닛을 하나씩 끝낸다. 다음 유닛을 앞당겨 시작하지 않는다.

1. **seam 확인.** 첫 유닛이면 그 전에 위 `craft:implement-spec` 안내를 한 번 한다. plan.md의 `## Seam과 테스트 예산`에서 이 유닛의 seam을 읽는다. 없으면 멈추고 사용자에게 알린다. seam 없이 테스트를 쓰지 않고, 테스트 없이 구현하지도 않는다(plan이 "테스트 없음"으로 합의한 유닛은 예외이며 기록의 `## 테스트`에 그 출처를 적는다).
2. **red.** seam에 첫 테스트를 쓴다. 기대값은 `covers`의 수용 기준에서 가져온다. 실행 명령으로 돌려 실패를 확인한다. 실패 이유가 "아직 구현이 없어서"가 아니면(컴파일·환경 문제) 먼저 그것을 푼다.
3. **green.** 통과할 만큼만 구현한다. 다시 돌려 통과를 확인한다.
4. **반복.** 이 유닛의 `covers`에 있는 요구사항의 수용 기준을 모두 seam의 테스트가 확인할 때까지 2~3을 반복한다. 실제 인프라를 쓰는 테스트 수가 예산을 넘으면 멈추고 사용자에게 묻는다.
5. **린터·전체 실행.** practices.md에 린터가 있으면 돌린다. 유닛이 끝나면 실행 명령으로 전체 테스트를 한 번 돌려 다른 유닛을 깨지 않았는지 본다.
6. **기록.** `build/<unit>.md`를 아래 골격으로 쓴다.
7. **보고.** 사용자에게 (a) 변경 파일 목록, (b) 테스트 실행 결과(명령과 통과·실패 수), (c) 추적성 표, (d) 계획과 다르게 한 것, 또는 수용 기준의 예시값과 다른 픽스처를 쓴 것이 있으면 한 줄을 보이고 "다음 유닛으로 갈까요?"를 묻는다. 사용자가 이 스테이지에 한해 "전부 진행"이라고 했으면 보고만 하고 이어간다. 그 허가는 build 한 번에만 유효하다.

계획과 다르게 해야 할 때(seam이 실제 코드와 안 맞음, 유닛 분해가 틀림, 예산 초과 필요)는 조용히 바꾸지 않는다. 사용자에게 알리고 결정을 `dlc.py note build "<결정>"`으로 기록한 뒤 진행한다. units.md·plan.md를 고치는 것은 사용자가 그렇게 결정했을 때만이며, 고친 내용도 note로 남긴다.

**재개.** 세션이 끊겨 다시 시작하면 `state.md`의 build가 이미 `active`다. `dlc.py start build`는 다시 실행하지 않고 `dlc.py note build "재개"`로 기록한 뒤, `build/<unit>.md`가 이미 있는 유닛은 건너뛰고 다음 유닛부터 한다. 기록이 없는데 코드만 있는 유닛은 그 코드를 읽고 테스트를 돌려 기록을 먼저 채운다.

## 산출물 골격

### build/<unit>.md

파일 이름은 유닛 이름 그대로(`build/u1-stock-query.md`).

```markdown
# u1-stock-query

## 변경 파일
| 파일 | 변경 | 출처 |
|---|---|---|
| `src/inventory/stock_query.py` | 신규. `get_stock(sku)` | [code:src/inventory/stock_query.py] |
| `tests/inventory/test_stock_query.py` | 신규. seam 테스트 3건 | [code:tests/inventory/test_stock_query.py] |

## 추적성
| 요구사항 | 파일 | 테스트 | 출처 |
|---|---|---|---|
| FR1.1 | `src/inventory/stock_query.py` | `test_returns_total_for_existing_sku` | [code:tests/inventory/test_stock_query.py] |
| FR1.2 | `src/inventory/stock_query.py` | `test_splits_quantity_by_warehouse` | [code:tests/inventory/test_stock_query.py] |
| NFR1 | `src/inventory/stock_query.py` | 부하 측정은 verify에서 | [assumption] |

## 테스트
- 실행: `python3 -m pytest tests/inventory -q` → 3 passed. [code:tests/inventory/test_stock_query.py]
- red 확인: 첫 테스트가 `ImportError`로 실패한 것을 보고 구현했다. [code:tests/inventory/test_stock_query.py]
- 실제 인프라 테스트: 0건 (예산 0). [practice]

## 가정과 열린 질문
- NFR1 응답 시간은 이 유닛에서 측정하지 않았다. [assumption]
```

- `## 추적성` 표에는 이 유닛의 `covers`에 있는 ID를 전부 적는다. 모든 유닛이 끝나면 `dlc.py check build`가 requirements.md의 모든 최상위 FR/NFR이 어느 유닛의 추적성 표 행에든 나오는지 검사한다. 표 밖의 산문에 적은 ID는 세지 않는다. 하위 ID를 적으면 상위도 덮은 것이다.
- 테스트로 확인하지 못한 요구사항(수동 측정, 다음 단계로 미룸)은 표에 남기되 출처를 `[assumption]`으로 달고 가정 절에도 적는다. 표에서 빼지 않는다.
- 이 기록에 코드 본문을 붙여넣지 않는다. 파일 경로와 테스트 이름이면 된다.

## 완료 기준

- units.md의 모든 유닛에 `build/<unit>.md`가 있고(plan.md 순서 표의 유닛 집합이 units.md와 같은지는 `dlc.py check plan`이 이미 봤다) `dlc.py check build`가 OK: 필수 절 넷, requirements.md에 없는 ID 참조 없음, 모든 최상위 FR/NFR이 추적성 어딘가에 있음.
- 전체 테스트가 GREEN이고 실제 인프라 테스트 수가 예산 이하다. plan.md의 `## 완료 정의`를 항목마다 확인했다.
- 사용자가 승인 게이트에서 승인했다(protocol.md 10단계 — 요약에는 전체 테스트 결과와 유닛 수를 넣는다). 승인 뒤 `dlc.py approve build`.

## 출력 언어

사용자 대면 출력과 기록은 한국어. 코드, 식별자, 경로, 명령, 테스트 이름은 원문 유지. 코드 안의 주석·문자열은 프로젝트 관례(practices.md·codebase.md)를 따른다.
