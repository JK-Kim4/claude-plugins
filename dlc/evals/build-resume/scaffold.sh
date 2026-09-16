#!/bin/bash
# build 재개 픽스처(R4 실측 `wcl` 산출물, 2026-09-13). u1-count 완료, u2-cli 미착수, build active. 파일 본문은 heredoc 으로 인라인한다.
set -e
rm -rf docs wcl tests
mkdir -p docs/dlc/260913-wcl/build wcl tests
cat > docs/dlc/active <<'EOF_DLC'
260913-wcl
EOF_DLC
cat > docs/dlc/260913-wcl/state.md <<'EOF_DLC'
# DLC State

<!-- dlc.py 가 관리한다. 손으로 고치지 말고 start/approve/skip 을 쓴다. -->

- profile: express
- depth: minimal
- description: 파일의 줄·단어·문자 수를 세는 파이썬 CLI 유틸 wcl
- created: 2026-09-13T08:02:40Z
- workspace: greenfield
- languages: -
- build: -
- fingerprint: da39a3ee5e6b

## Stages

| stage | status | updated | note |
|---|---|---|---|
| init | done | 2026-09-13T08:02:40Z |  |
| analyze | skipped | 2026-09-13T08:02:40Z | greenfield |
| requirements | done | 2026-09-13T08:04:34Z |  |
| plan | done | 2026-09-13T08:04:45Z |  |
| build | active | 2026-09-13T08:04:45Z |  |
| verify | pending | 2026-09-13T08:07:55Z |  |
EOF_DLC
cat > docs/dlc/260913-wcl/log.md <<'EOF_DLC'
# DLC Log

- 2026-09-13T08:02:40Z | init | created | profile=express workspace=greenfield
- 2026-09-13T08:02:55Z | requirements | start | 
- 2026-09-13T08:04:34Z | requirements | approve | 사전 승인(R3 실측)
- 2026-09-13T08:04:35Z | plan | start | 
- 2026-09-13T08:04:45Z | plan | approve | 사전 승인(R3 실측)
- 2026-09-13T08:04:45Z | build | start | 
EOF_DLC
cat > docs/dlc/260913-wcl/requirements.md <<'EOF_DLC'
# 요구사항

## 의도 요약
파일의 줄·단어·문자 수를 세는 파이썬 CLI 유틸 `wcl` 을 만든다. 개발자가 터미널에서 `python3 -m wcl <파일>...` 로 실행해 파일마다 한 줄의 집계 결과를 본다. [desc] [Q2]

## 기능 요구사항

### FR1. 파일별 줄·단어·문자 수 출력 [Q1] [Q2]
- FR1.1 파일 경로를 하나 이상 인자로 받는다. [Q1]
- FR1.2 파일마다 `줄 단어 문자 파일명` 형식의 한 줄을 stdout 에 출력한다. 파일 여러 개면 파일마다 한 줄. [Q1] [Q2]
- FR1.3 빈 파일은 `0 0 0 파일명` 을 출력한다. [Q2]
- 수용 기준: 줄 3개·단어 5개·문자 20개인 파일 `a.txt` 를 넘기면 stdout 에 `3 5 20 a.txt` 한 줄. 빈 파일이면 `0 0 0 <파일명>`. 파일 2개를 넘기면 순서대로 2줄. 종료 코드 0. [Q1] [Q2]

### FR2. 출력 항목 선택 옵션 [Q1]
- FR2.1 `-l`(줄), `-w`(단어), `-c`(문자) 옵션으로 출력 항목을 고른다. [Q1]
- FR2.2 옵션이 하나도 없으면 셋 다 출력한다. [Q1]
- 수용 기준: `-l` 만 주면 `줄 파일명`, `-w -c` 를 주면 `단어 문자 파일명` 형식. 옵션 없이 실행하면 FR1.2 형식. [Q1]

### FR3. 없는 파일 오류 처리 [Q1]
- FR3.1 존재하지 않는 파일이 있으면 stderr 에 오류 한 줄을 낸다. [Q1]
- FR3.2 종료 코드는 1 이다. [Q1]
- 수용 기준: 존재하지 않는 경로를 넘기면 stderr 에 그 경로를 포함한 오류 한 줄, `main()` 반환값(종료 코드) 1. [Q1]

## 비기능 요구사항

### NFR1. 처리 속도 [Q4]
- 10MB 텍스트 파일 한 개를 1초 안에 처리한다. 측정: 검증 단계에서 10MB 임시 파일을 만들어 `python3 -m wcl` 실행 시간을 잰다. 측정하지 못하면 "미확인" 으로 남긴다. [Q4]

## 제약
| 항목 | 내용 | 출처 |
|---|---|---|
| 언어·의존 | python3 표준 라이브러리만 사용. 외부 의존 없음 | [Q3] |
| 패키지 구조 | `wcl/` 패키지 (`__init__.py`, `__main__.py`, `count.py`) | [Q3] |
| 테스트 | `tests/` 에 unittest. 실행 명령 `python3 -m unittest discover -s tests` | [Q3] [Q4] |
| 완료 조건 | 위 명령이 GREEN 이고 count 함수와 CLI 출력·종료 코드를 seam 에서 검사하는 테스트가 있음 | [Q4] |

## 범위 밖
- 표준 입력(stdin) 읽기. 파일 경로 인자만 받는다. [Q1]
- 파일 여러 개의 합계 줄. 파일마다 한 줄만 낸다. [Q2]

## 가정과 열린 질문
- 단어는 공백 문자(스페이스·탭·개행) 로 구분된 토막으로 세고, 줄은 개행 문자 `\n` 의 개수로 센다(POSIX `wc` 와 같은 방식). [assumption]
- 문자 수는 바이트가 아니라 유니코드 문자 수이며, 파일은 UTF-8 로 읽는다. [assumption]
- 파일이 여러 개이고 그중 일부만 없으면, 존재하는 파일의 결과는 stdout 에 내고 없는 파일마다 stderr 오류 한 줄을 낸 뒤 종료 코드 1 로 끝낸다. [assumption]
- 옵션의 출력 순서는 옵션 지정 순서와 무관하게 항상 줄·단어·문자 순이다. [assumption]
EOF_DLC
cat > docs/dlc/260913-wcl/plan.md <<'EOF_DLC'
# 구현 계획

## 유닛 순서
| 순서 | unit | depends_on | covers | 이유 | 출처 |
|---|---|---|---|---|---|
| 1 | u1-count | | FR1, NFR1 | u2 가 의존하는 순수 계산. 먼저 seam 을 고정한다 | [Q1] [Q4] |
| 2 | u2-cli | u1-count | FR1, FR2, FR3 | u1 의 `count_text` 를 호출해 출력·종료 코드를 만든다 | [Q1] [Q4] |

## Seam과 테스트 예산
| unit | seam | 테스트 수준 | 실제 인프라 | 출처 |
|---|---|---|---|---|
| u1-count | `count_text(text) -> (lines, words, chars)` 반환값 | 단위 | 0 | [Q2] |
| u2-cli | `main(argv) -> int` 반환값과 stdout/stderr 캡처. 입력 파일은 `tempfile` 임시 파일 | 단위 | 0 (로컬 임시 파일은 예산에 세지 않음) | [Q2] [Q3] |

통합테스트 예산: 총 0건. [Q3]
실행 명령: `python3 -m unittest discover -s tests` [Q4]

## 완료 정의
- 모든 유닛의 `build/<unit>.md` 가 있고 `dlc.py check build` 가 OK. [Q4]
- `python3 -m unittest discover -s tests` 전체 GREEN. [Q4]
- FR1·FR2·FR3 마다 수용 기준을 확인하는 테스트가 seam 에 하나 이상. [Q4]
- 커버리지 기준 없음(practices 단계 없음). [Q4]

## 가정과 열린 질문
- NFR1(10MB 파일 1초 이내)은 build 에서 자동 테스트로 두지 않고 verify 단계에서 수동 측정한다. 측정 불가 시 미확인으로 남긴다. [assumption]
- 각 유닛은 seam 에서 실패하는 테스트(red)를 먼저 확인한 뒤 구현(green)한다. [assumption]
EOF_DLC
cat > docs/dlc/260913-wcl/units.md <<'EOF_DLC'
# 유닛

## 유닛
| unit | kind | depends_on | covers |
|---|---|---|---|
| u1-count | module | | FR1, NFR1 |
| u2-cli | cli | u1-count | FR1, FR2, FR3 |

- u1-count: `wcl/count.py`. 문자열을 받아 줄·단어·문자 수를 계산하는 순수 함수. FR1 의 계산 부분과 NFR1(처리 속도)을 맡는다. [Q1]
- u2-cli: `wcl/__main__.py`. 인자 파싱, 파일 읽기, 출력 형식, 없는 파일 오류와 종료 코드. u1 에 의존한다. [Q1]

## 계약
| 계약 | 형태 | 제공 유닛 | 사용 측 | 출처 |
|---|---|---|---|---|
| 텍스트 집계 | `count_text(text: str) -> tuple[int, int, int]` (lines, words, chars) | u1-count | u2-cli | [Q2] |
| CLI 진입점 | `main(argv: list[str]) -> int`. stdout 에 파일마다 한 줄, 없는 파일은 stderr 한 줄, 반환값이 종료 코드 | u2-cli | 터미널 사용자 (`python3 -m wcl`) | [Q2] |

## 가정과 열린 질문
- `wcl/__init__.py` 는 비어 있거나 `count_text` 를 재노출만 하며 별도 유닛으로 세지 않는다. [assumption]
EOF_DLC
cat > docs/dlc/260913-wcl/build/u1-count.md <<'EOF_DLC'
# u1-count

## 변경 파일
| 파일 | 변경 | 출처 |
|---|---|---|
| `wcl/__init__.py` | 신규. 빈 패키지 파일 | [code:wcl/__init__.py] |
| `wcl/count.py` | 신규. `count_text(text) -> (lines, words, chars)` | [code:wcl/count.py] |
| `tests/test_count.py` | 신규. seam 테스트 3건 | [code:tests/test_count.py] |

## 추적성
| 요구사항 | 파일 | 테스트 | 출처 |
|---|---|---|---|
| FR1.2 | `wcl/count.py` | `test_counts_lines_words_chars_of_two_line_text` | [code:tests/test_count.py] |
| FR1.3 | `wcl/count.py` | `test_returns_zeros_for_empty_text` | [code:tests/test_count.py] |
| NFR1 | `wcl/count.py` | 속도 측정은 verify 에서 수동으로 | [assumption] |

## 테스트
- 실행: `python3 -m unittest discover -s tests` → 3 tests OK. [code:tests/test_count.py]
- red 확인: 첫 테스트가 `ModuleNotFoundError: No module named 'wcl.count'` 로 실패한 것을 보고 구현했다. [code:tests/test_count.py]
- 빈 텍스트·유니코드 테스트 2건은 첫 구현이 이미 일반적이라 red 없이 바로 통과했다. [code:wcl/count.py]
- 실제 인프라 테스트: 0건 (예산 0). [Q3]

## 가정과 열린 질문
- NFR1 처리 속도는 이 유닛에서 측정하지 않았다. verify 에서 10MB 임시 파일로 잰다. [assumption]
- 단어는 `str.split()`(모든 공백 문자 기준), 줄은 `\n` 개수, 문자는 유니코드 문자 수로 센다. [assumption]
EOF_DLC
cat > wcl/count.py <<'EOF_DLC'
"""줄·단어·문자 수 계산 (순수 함수)."""


def count_text(text: str) -> tuple[int, int, int]:
    """텍스트의 (줄 수, 단어 수, 문자 수)를 돌려준다.

    줄은 개행 문자 개수, 단어는 공백으로 구분된 토막 수, 문자는 유니코드 문자 수다.
    """
    return text.count("\n"), len(text.split()), len(text)
EOF_DLC
cat > tests/test_count.py <<'EOF_DLC'
import unittest

from wcl.count import count_text


class CountTextTest(unittest.TestCase):
    def test_counts_lines_words_chars_of_two_line_text(self):
        # FR1 수용 기준: 손으로 센 값. "hello world\n"(12자) + "foo bar baz\n"(12자)
        self.assertEqual(count_text("hello world\nfoo bar baz\n"), (2, 5, 24))

    def test_returns_zeros_for_empty_text(self):
        # FR1.3 수용 기준: 빈 파일은 0 0 0
        self.assertEqual(count_text(""), (0, 0, 0))

    def test_counts_unicode_characters_not_bytes(self):
        # "안녕 세계\n" = 안,녕,공백,세,계,개행 → 6문자, 단어 2, 줄 1
        self.assertEqual(count_text("안녕 세계\n"), (1, 2, 6))


if __name__ == "__main__":
    unittest.main()
EOF_DLC
: > wcl/__init__.py
