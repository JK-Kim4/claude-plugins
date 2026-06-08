# 컨벤션 해석 & 스택별 범용 컨벤션

pr-reviewer가 컨벤션 리뷰(축 A)를 할 때 참고하는 카탈로그다.

## 1. 기술 스택 탐지

레포 루트의 매니페스트와 확장자 분포로 스택을 추정한다.

| 신호 | 스택 |
|------|------|
| `package.json` | node/javascript (+ `tsconfig.json` → typescript) |
| `build.gradle`(.kts)·`pom.xml` | jvm (kotlin/java, 소스 확장자로 구분) |
| `go.mod` | go |
| `pyproject.toml`·`requirements.txt` | python |
| `Cargo.toml` | rust |
| `Gemfile` | ruby |
| `composer.json` | php |

여러 개면 모두 기록한다(예: `["typescript", "go"]`). 매니페스트가 없으면 변경 파일 확장자로 추정한다.

## 2. conventionSource 해석 절차

1. 인터뷰에서 "팀 컨벤션 문서가 있나요?"를 묻는다.
2. **있음(`doc`)**: 경로를 `conventionRef`에 기록한다. 흔한 위치 — `CONTRIBUTING.md`, `docs/` 하위 스타일 가이드, `.editorconfig`, 린터 설정(`.eslintrc*`, `ktlint`, `.rubocop.yml`, `ruff.toml` 등). 리뷰 시 이 문서/설정이 **권위 기준**이며 아래 범용 컨벤션과 충돌하면 팀 문서를 우선한다.
3. **없음(`universal`)**: 아래 스택별 범용 컨벤션을 기준으로 점검한다.

## 3. 스택별 범용 컨벤션 (요약)

문서가 없을 때의 기본 점검 항목. 깊은 규칙이 아니라 "널리 합의된 관용구" 위주다.

**공통**
- 네이밍 일관성(같은 개념에 같은 단어), 매직 넘버·하드코딩 지양, 죽은 코드·주석 처리 코드 미포함.
- 함수 한 가지 책임, 과도한 중첩·긴 함수 지양.

**javascript / typescript**
- `const`/`let`(no `var`), 엄격 동등(`===`), 명시적 타입(ts에서 `any` 남용 지양), async/await 일관.

**jvm (kotlin/java)**
- 불변 우선(`val`, `final`), null 안전(kotlin nullable 명시), 네이밍(클래스 PascalCase·함수 camelCase), 예외 무시(빈 catch) 금지.

**python**
- PEP 8(snake_case, 4-space), 타입 힌트, 가변 기본 인자 금지, 광범위 `except:` 지양.

**go**
- 에러 명시적 처리(`if err != nil`), exported 식별자 주석, `gofmt` 정렬, 패키지명 소문자.

**rust**
- `Result`/`Option` 명시적 처리, `unwrap()` 남용 지양(특히 라이브러리 코드), `clippy` 관용구.

## 출처(권고 근거)

- 각 언어 공식 스타일 가이드(PEP 8, Effective Go, Kotlin coding conventions 등)
- 널리 쓰이는 린터 기본 규칙
