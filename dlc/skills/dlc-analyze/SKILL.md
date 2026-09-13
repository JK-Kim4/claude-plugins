---
name: dlc-analyze
description: 기존 코드베이스를 읽어 구조·기술 스택·관례와 제약을 docs/dlc/codebase.md로 정리한다. 기존 코드가 있는 저장소(brownfield)에서만 실행된다.
disable-model-invocation: true
metadata:
  author: JK-Kim4
  version: "0.1.0"
---

# dlc-analyze — 코드베이스 분석

기존 코드가 있을 때 뒤 단계가 공유하는 사실 기반을 만든다. 산출물 `docs/dlc/codebase.md`는 작업 폴더 밖에 있어 같은 저장소의 모든 작업이 함께 쓴다. 소스가 바뀌지 않았으면(지문 일치) `dlc.py next`가 이 단계를 자동으로 건너뛴다.

공통 절차는 [../dlc/references/protocol.md](../dlc/references/protocol.md), 출처 규칙은 [../dlc/references/grounding.md](../dlc/references/grounding.md)에 있다. 스크립트 위치 `<skills>/dlc/scripts/dlc.py`의 뜻은 protocol.md의 "스크립트 위치" 절을 따른다. 아래는 이 단계에서만 다른 것이다.

## 읽을 것

- `state.md`의 `workspace`·`languages`·`build`·`fingerprint`. `workspace`가 greenfield면 이 스킬은 할 일이 없다. 사용자에게 알리고 끝낸다.
- `docs/dlc/codebase.md`가 이미 있으면 **갱신 모드**다. 기존 내용을 읽고, 바뀐 부분만 고치고, 남은 내용은 보존한다.

## 순서에서 다른 점

- protocol.md 1단계에서 `dlc.py next`가 analyze를 가리키지 않는데 사용자가 이 스킬을 명시 호출했다면, 지문이 같아 건너뛴 경우다. 사용자에게 "codebase.md가 현재 소스와 일치합니다. 다시 분석할까요?"를 묻고, 예면 `dlc.py start analyze --force`로 시작한다. 아니면 끝낸다.
- 조사는 아래 "조사 항목" 순서로 코드를 직접 읽는다. 코드에서 읽을 수 있는 것은 묻지 않는다.

## 조사 항목

| 항목 | 어디서 읽는가 |
|---|---|
| 디렉터리 구조와 모듈 경계 | 최상위와 깊이 3까지의 폴더, 각 폴더의 역할이 드러나는 파일 이름 |
| 기술 스택과 버전 | 빌드 파일(`build.gradle.kts`, `package.json`, `pyproject.toml`, `go.mod` 등), 런타임 버전 파일(`.nvmrc`, `.python-version`, `.tool-versions`) |
| 진입점과 실행 방법 | main 함수, 서버 부트스트랩, 스크립트 `scripts` 항목, Makefile 타깃, README의 실행 절 |
| 테스트 위치와 실행 명령 | 테스트 디렉터리, 테스트 러너 설정, CI 워크플로우(`.github/workflows/`, `.gitlab-ci.yml`) |
| 코드 관례 | 린터·포맷터 설정(`.editorconfig`, `.eslintrc*`, `ruff.toml`, `.ktlint`), 네이밍이 드러나는 대표 파일 2~3개 |
| 기존 규약 문서 | `README.md`, `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, `docs/` 아래 설계·ADR 문서 |
| 외부 의존과 경계 | 설정 파일의 DB·큐·외부 API 주소, 환경변수 예시(`.env.sample`), 인프라 정의 |

파일을 통째로 읽지 않는다. 구조는 목록으로, 설정은 관련 부분만 본다. 큰 저장소면 `languages` 상위 언어의 주 소스 트리부터 본다.

## 질문 주제

코드로 판단할 수 없는 것만 묻는다. 대개 0~2개이며 depth 상한(minimal 4, standard 8)을 넘지 않는다. 질문이 없으면 `analyze-questions.md`를 만들지 않는다.

- 곧 폐기되거나 손대면 안 되는 영역이 있는가
- 코드에 드러나지 않는 외부 시스템의 소유자·계약(SLA, 호출 한도)
- 서로 다른 관례가 공존할 때 어느 쪽이 현재 표준인가
- 테스트가 없는 영역이 의도된 것인가

질문 파일은 작업 폴더의 `analyze-questions.md`. 형식과 답변 검사는 protocol.md.

## 산출물 골격

### codebase.md

첫 줄 제목 바로 아래에 지문 주석을 둔다. 값은 `state.md`의 `fingerprint`다. init 뒤 소스가 바뀌었으면 `dlc.py check analyze`가 기대 값을 알려주므로 그 값으로 고친다.

```markdown
# 코드베이스 분석

<!-- fingerprint: 3f9a1c0b2d4e -->

## 개요
저장소가 무엇인지 2~4문장. 언어·빌드 도구·규모(소스 파일 수). [code:README.md]

## 구조
| 경로 | 역할 | 출처 |
|---|---|---|
| `src/main/kotlin/inventory/` | 재고 도메인. 엔티티·서비스·리포지토리 | [code:src/main/kotlin/inventory/] |

## 기술 스택
| 영역 | 내용 | 출처 |
|---|---|---|
| 언어·런타임 | Kotlin 1.9, JVM 17 | [code:build.gradle.kts] |
| 프레임워크 | Spring Boot 3.2 | [code:build.gradle.kts] |
| 테스트 | JUnit 5, `./gradlew test` | [code:build.gradle.kts] |

## 관례와 제약
| 항목 | 내용 | 출처 |
|---|---|---|
| 포맷터 | ktlint. 커밋 전 `./gradlew ktlintCheck` | [code:.editorconfig] |
| 레이어 규칙 | 도메인 패키지는 인프라를 import하지 않는다 | [code:CLAUDE.md] |
| 손대지 않는 영역 | `legacy/` 는 2026-12 폐기 예정 | [Q1] |

## 가정과 열린 질문
- 결제 모듈의 외부 PG 계약 조건은 코드에 없다. [assumption]
```

- 표의 데이터 행마다 `출처` 열에 태그를 단다. 코드에서 직접 확인한 사실은 `[code:<경로>]`, 사용자 답변은 `[Q<n>]`. 근거 없는 추정은 `## 가정과 열린 질문`에만 `[assumption]`으로 둔다.
- 갱신 모드에서는 기존 행을 지우지 않고 바뀐 행만 고친다. 사라진 모듈은 행을 지우고 `dlc.py note analyze "<무엇을 왜 지웠는지>"`로 남긴다.

## 완료 기준

- `dlc.py check analyze`가 OK: 필수 절 다섯 개가 있고, 지문 주석이 현재 소스와 같고, 가정 절이 비어 있지 않다.
- 뒤 단계가 이 문서만 읽고 "어디에 무엇이 있고 어떻게 테스트하는가"에 답할 수 있다.
- 사용자가 승인 게이트에서 승인했다(protocol.md 10단계). 승인 뒤 `dlc.py approve analyze`.

## 출력 언어

사용자 대면 출력과 산출물은 한국어. 코드, 식별자, 경로, 명령은 원문 유지.
