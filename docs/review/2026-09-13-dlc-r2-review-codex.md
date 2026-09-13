# [Codex 리뷰] dlc 플러그인 2라운드 — 스테이지 스킬 5개 (2026-09-13)

판정: **보완 필요(FAIL)**. 주요 산출물과 정상 CLI 흐름은 확인했지만, eval 내용 검사에 거짓 양성이 있고 분석 재호출 안내가 실제 상태 전이와 충돌한다. 기존 Fable 리뷰에서 확인된 P1을 이번 리뷰에서도 재현했다.

> 리뷰 주체: Codex 및 읽기 전용 검토 에이전트 5개. 이 보고서는 검토 결과이며 제품 수정 승인을 뜻하지 않는다. 이슈 코멘트에 기록된 기존 지적의 수정 보류 결정을 존중하여 제품 코드는 변경하지 않았다.

## 1. 범위와 방법

- 대상 커밋: `1dae4d1e6634215e2a06faec58c28c3e4135ae42`.
- 기준 커밋: `c92c91ca6a118f87575bb53a1e60c357e1a0696c`. `git diff c92c91c..1dae4d1`의 22개 파일을 대상으로 했다. 리뷰 시작 시 추적 파일의 미커밋 변경은 없었다.
- 명세: [GitHub 이슈 #2 본문](https://github.com/JK-Kim4/claude-plugins/issues/2), [실행 결과 및 수정 보류 코멘트](https://github.com/JK-Kim4/claude-plugins/issues/2#issuecomment-5650495160), [설계 문서](../design/2026-09-13-dlc-plugin-design.md)의 스킬 구성·공유 계약·2라운드 완료 조건.
- 비교 대상: 신규 스킬 5개와 `agents/openai.yaml`, 라우터·README, 공통 참조 3개, `dlc.py`, 계약 테스트, express eval 케이스.
- 방법: 명세·품질·보안·실행 QA·관련 맥락을 병렬 검토하고, 실제 파일·CLI 출력·eval 원본 자료로 지적을 대조했다. 기존 [Fable 리뷰](2026-09-13-dlc-r2-review-fable.md)는 독립 재확인 후 참고했다.
- 심각도: P1은 완료 판정의 신뢰성을 해치는 문제, P2는 지원 경로의 잘못된 동작·안내, P3는 비차단 검증·문서 정정이다. R3·R4 예정 기능은 누락 결함으로 세지 않았다.

## 2. 우선 수정할 결함

### 1. [P1] eval의 내용 검사 3개가 Read 결과만으로 통과한다

- 위치: `dlc/evals/express-requirements/case.yaml:48-55,70-75`, `docs/design/2026-09-13-dlc-plugin-design.md:147`.
- 명세: 이슈는 `requirements.md`·질문 파일을 채점하도록 요구한다. 설계는 “내용은 Write 도구 입력이 남는 trace regex로 본다”고 기록했다.
- 실제: 정규식은 trace 전체에서 `### FR1.`, `[Answer]: Looks correct`, 필수 H2 여섯 개를 찾는다. 동일 문자열이 grounding·protocol·requirements 스킬의 예시에 이미 있다.
- 재현: 남아 있는 1차 trace에서 `Read` 호출 ID 6개에 대응하는 `tool_result`만 추출했다. Write·Edit·Bash 호출 및 결과를 모두 제외한 문자열에 **현재 case.yaml의 패턴을 그대로 적용**했는데 아래 세 항목이 전부 참이었다. 참조 문서 본문만 JSON 문자열로 구성한 별도 음성 대조에서도 같은 결과였다.

  ```text
  Read results only: 6 Read calls; Write/Edit/Bash results excluded
  fr1-defined-in-trace: true
  summary-confirmed: true
  requirements-md-has-sections: true
  ```

- 영향: 파일 존재 검사는 별도로 있으므로 “파일이 전혀 없어도 전체 11/11”이라고 주장하는 것은 아니다. **파일 내용과 요약 확인을 이 세 점수로 입증할 수 없다는 문제**다. 보고된 11/11 자체가 요구사항 내용의 정확성을 증명하지 않는다.
- 수정 방향: 해당 경로의 실제 최종 파일 내용을 검사하거나, trace의 도구 종류·대상 경로·본문을 구조적으로 제한한다. Read-only 음성 대조가 실패하고 유효한 산출물 양성 대조가 통과하는지 확인한 뒤 eval을 다시 실행한다. 설계의 R4 채점 방침도 함께 정정한다.
- 기존 리뷰 관계: Fable 지적 1과 같은 결함. 코멘트의 수정 보류 결정을 확인했으며 이번에 수정하지 않았다.

### 2. [P2] 이미 승인된 분석의 재호출을 지문 일치로 오인한다

- 위치: `dlc/skills/dlc-analyze/SKILL.md:23`. 대조: `dlc.py:237-245,541-549`, `protocol.md:17`.
- 명세: 강제 시작은 “지문 일치로 건너뛴 analyze”를 다시 실행하는 예외다.
- 실제: 스킬은 `next`가 analyze가 아니면 지문이 같은 경우라고 단정한다. 하지만 `next_stage`는 이미 `done`인 단계를 지문과 관계없이 건너뛰고, `--force`는 `pending`만 허용한다.
- 재현: 임시 brownfield 프로젝트에서 analyze를 승인하고 소스를 변경한 뒤 다음을 실행했다.

  | 명령 | 종료 코드 | 실제 결과 |
  |---|---|---|
  | `next` | 0 | `requirements dlc-requirements` |
  | `check analyze` | 1 | `fingerprint 가 현재 소스와 다릅니다` |
  | `start analyze --force` | 2 | `analyze 가 이미 done 입니다.` |

- 영향: 현재 소스와 불일치하는데도 사용자에게 “현재 소스와 일치합니다”라고 안내하고 실패할 명령을 제안한다.
- 수정 방향: 상태가 pending이고 실제 지문이 일치하는 경우만 예외로 처리한다. 이미 승인되었거나 명시적으로 건너뛴 상태는 구분해서 설명하고, 현재 지원되는 새 작업 생성 경로 등을 안내한다.
- 기존 리뷰 관계: Fable 지적 3 독립 재현.

### 3. [P2] 프로파일 선택 표가 express·bugfix의 분석 단계를 빠뜨린다

- 위치: `dlc/skills/dlc-init/SKILL.md:44-46`.
- 명세: 설계의 프로파일 표와 `state-format.md:64-68`은 세 프로파일 모두 brownfield에서 analyze를 먼저 실행하도록 정의한다.
- 실제: 사용자가 프로파일을 고를 때 보는 표에서 full에만 “기존 코드가 있으면 분석이 먼저”라고 적고 express·bugfix는 요구사항부터 설명한다. 실제 brownfield express 초기화의 다음 단계는 analyze였다.
- 영향: 사용자가 선택 전에 듣는 실행 단계와 선택 후 안내가 달라진다. 코드의 라우팅 자체는 정상이다.
- 수정 방향: 표 공통 설명에 세 프로파일의 조건부 분석 단계를 명시하거나 각 행을 실제 순서와 맞춘다.
- 기존 리뷰 관계: Fable 지적 4 재확인.

## 3. 비차단 검증·문서 정정

| 심각도 | 위치 | 확인한 문제 | 권장 조치 |
|---|---|---|---|
| P3 | `dlc/skills/dlc/tests/test_dlc.py:865-893` | `unittest.main()` 뒤에 신규 계약 테스트 클래스가 있다. 직접 실행은 75건, 문서의 discovery 실행은 78건 통과하여 직접 실행에서 신규 3건이 빠진다. 이번 리뷰의 추가 발견이다 | 실행 진입점을 모든 테스트 정의 뒤로 이동. 공식 discovery 검증은 정상이며 78건 통과 주장을 부정하지 않는다 |
| P3 | 설계 문서:99, grounding.md:5-13 | 설계의 출처 태그 목록은 4종, 실제 공유 규칙은 `[code:<경로>]`를 포함한 5종이다. 설계의 열린 질문에는 추가 사실이 기록되어 있지만 규범 목록은 갱신되지 않았다 | 설계의 규범 목록도 5종으로 맞춘다. Fable 지적 2와 같으며 실행 차단은 확인되지 않아 문서 정정으로 분류 |
| P3 | 설계 문서:139, 이슈 실행 결과 코멘트 | 실행 버전을 2.1.269로 묶어 적었지만 1차 원본 JSON은 2.1.269, 2차는 2.1.270이다 | 실행별 버전 구분. 아래 원본 자료 경로 참조 |

Fable의 나머지 표현·향후 테스트 확장 제안 전체를 새 결함으로 복제하지 않았다. 특히 질문 없는 practices 경로는 공통 protocol의 “질문이 하나도 필요 없으면 파일을 만들지 않는다”는 규칙이 있으므로 별도 차단 결함으로 채택하지 않았다.

## 4. 명세 충족과 완료 증거

| 완료 조건 | 확인 결과 |
|---|---|
| 스킬 5개·openai.yaml 5개·명시 호출 설정·300줄 제한 | 충족. 실제 파일과 계약 테스트 확인 |
| 산출물 H2를 ARTIFACTS와 글자·순서 단위 비교 | 충족. analyze·intent·practices·requirements 골격 검사 통과. init은 스크립트가 state를 생성 |
| 질문 주제·출처 태그·가정 절·공통 절차 참조 | 주요 계약 충족. bugfix의 재현·기대 동작·회귀 테스트 분기 포함 |
| 라우터·README를 현재 제공 스킬과 맞춤 | 충족. 다음 라운드 스킬이 없는 상태에서 멈추는 안내 포함 |
| express eval 실행·결과 기록 | 이전 실행 원본 JSON과 코멘트 확인. 1차 10/11, 2차 11/11. 내용 검사의 타당성은 위 P1 때문에 미충족 |
| 명시 호출 발동 방식의 설계 기록 | 기록 존재. 슬래시 시작·Skill 호출 0회·사전 답변 제공 방식 명시. 이번 리뷰에서 Claude eval을 새로 실행해 발동을 검증하지는 않음 |
| brownfield 분석 생성·지문·승인·새 작업의 캐시 재사용 | 기존 산출물·승인 로그 확인. 이번 CLI QA에서 새 작업의 analyze 생략 및 강제 시작을 검증. 과거 실행의 두 번째 next 출력 원본은 미확보 |
| full에서 intent·practices 실제 승인 | 기존 Claude 실행 JSON의 성공·9턴과 산출물·승인 로그 확인. 현재 CLI로 두 산출물 검사 통과. 이번 CLI QA에서도 상태 흐름 확인 |
| 실행 중 발견한 공유 결함 수정·테스트 | analyze 질문 파일을 검사하도록 QUESTION_STAGES에 추가했고 미답변 회귀 테스트가 존재 |
| Fable 리뷰 후 P1 0건 | 원래 조건은 미충족. P1 1건을 사용자 결정으로 보류한 사실이 코멘트·리뷰에 명시됨. 보류를 해결로 간주하지 않음 |
| feat 커밋·push | 대상 feat 커밋 존재. 조회 당시 원격 브랜치는 기준 커밋이며 push는 사용자 승인 대기로 기록됨. 코드 결함으로 집계하지 않음 |

이슈 코멘트에 grader 결과 표는 있으므로 “결과가 전혀 기록되지 않았다”는 지적은 하지 않는다. 다만 원본 JSON·HTML의 첨부 링크는 없고 아래 자료는 Git 미추적 또는 임시 경로여서 다른 PC에서 원본을 재검토하기 어렵다. 원본 리포트 첨부 여부는 결과 요약 게시와 구분해야 한다.

## 5. 실행 검증과 한계

- `python3 -m unittest discover -s dlc/skills/dlc/tests`: **78건 통과**.
- `python3 dlc/skills/dlc/tests/test_dlc.py`: **75건 통과**. 신규 테스트 누락은 위 비차단 지적 참조.
- `claude plugin validate ./dlc`: **통과**.
- `python3 dlc/skills/dlc/scripts/dlc.py --help`: 종료 0, 명령·Python 요구 버전 안내 확인.
- `git diff c92c91c..1dae4d1 --check`: **통과**.
- 별도 임시 프로젝트 CLI QA: express·bugfix의 requirements 승인과 plan 안내, full의 intent·practices·requirements 승인과 design 안내, brownfield의 분석 승인·캐시 재사용·강제 시작, 잘못된 입력·미답변 거부를 확인했다. 승인 후 소스 변경·분석 재호출 경계는 위 P2로 재현됐다.
- CLI QA는 검토용 산출물을 직접 준비해 검사·전이를 실행한 것이다. **에이전트가 질문하고 산출물을 작성하는 스킬 전체 실행과 동등하지 않다.** 이번 리뷰에서는 Claude eval·헤드리스 LLM 실행을 재실행하지 않았으며 이전 자료를 대조했다.
- 보안 검토: R2 diff에서 신규 보안 차단 결함은 확인되지 않았다. scaffold의 `rm -rf docs`는 격리된 eval cwd라는 문서상 전제 아래 임시 디렉터리에서 확인했다. 일반 저장소 루트에서 직접 실행하지 않았다. 러너 자체의 격리 구현은 감사하지 않았다.

이전 실행 자료 대조:

| 자료 | 관찰 |
|---|---|
| `dlc/evals/results/2026-09-12T18-18-28-316Z/aggregate-result.json` | 1차, claudeVersion 2.1.269, overallScore 0.9090909090909091 |
| `dlc/evals/results/2026-09-13T02-44-54-597Z/aggregate-result.json` | 2차, claudeVersion 2.1.270, overallScore 1.0 |
| `/private/tmp/e-aCSA9s/out/trace.jsonl` | 현존하는 1차 trace. Read 결과만 추출한 음성 대조의 입력 |
| `/private/tmp/e-ZsICRd/out/trace.jsonl` | 2차 JSON이 가리키지만 조회 시 존재하지 않아 원 trace 재검증 불가 |
| `/private/tmp/dlc-full-run.json`, `/private/tmp/dlc-full-run/docs/dlc/260913-wiki-search/` | 성공·9턴의 기존 실행 결과 및 intent·practices 산출물·승인 로그 |
| `/private/tmp/dlc-analyze-target/docs/dlc/` | 기존 codebase.md와 분석 승인 기록. 현재 산출물 검사 통과 |

이 경로들의 영구 보존을 전제하지 않는다. 주요 재현 입력·출력과 판정 근거는 이 보고서 본문에 보존했다.

## 6. 검토 영역별 판정 기록

아래 모든 판정은 **`1dae4d1e6634215e2a06faec58c28c3e4135ae42`**에 한정한다. 제품 수정이나 새로운 커밋 이후의 통과 증거로 재사용할 수 없다.

| 영역 | 판정 | 근거 |
|---|---|---|
| 명세·제약 | FAIL | 분석 재호출 예외가 공유 계약과 불일치. 2절의 명세 인용·CLI 결과 |
| 코드 품질·지시 정확성 | FAIL | 분석 재호출·프로파일 안내 오류. 2절과 3절 |
| 실행 QA | FAIL | 정상 흐름은 통과, 분석 재호출 경계와 eval 내용 음성 대조는 실패. 5절 |
| 보안 | PASS | 신규 보안 차단 결함 미발견. 격리 cwd 전제 및 검토 한계는 5절 |
| 관련 맥락 | FAIL | 원래 P1 0 조건 미충족을 확인. 수정 보류·push 승인 대기·원본 증거 한계는 4절 |
| 런타임 감사 | FAIL | 현재 정규식으로 Read-only 거짓 양성과 CLI 상태·안내 불일치 재현. 2절의 실제 출력 |

규칙 준수 관점에서는 공유 참조 재사용·한국어·명시 호출·파일 구조의 요구를 충족했다. 명세 관점에서는 검증 장치와 분석 재호출의 보완이 필요하다. 우선순위는 eval 내용 검사의 신뢰성 확보, 분석 재호출 분기 정정, 프로파일 안내 정정 순이다. 수정·커밋·push는 이 리뷰 작업에 포함하지 않았다.

> 통합 분석과 재현 결과·반영안: [2026-09-13-dlc-r2-review-consolidated.md](2026-09-13-dlc-r2-review-consolidated.md). 이 문서의 지적 번호는 그곳의 U 번호로 대응된다.
