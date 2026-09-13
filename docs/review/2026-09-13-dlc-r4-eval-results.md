# [Eval] dlc 플러그인 4라운드 — `claude plugin eval` 스킬 완성도 평가 (2026-09-13)

> 평가 주체: 오케스트레이터(Claude Fable 5.1)가 `claude plugin eval` 러너로 실행하고 trace를 읽어 정리했다. 채점은 러너의 결정적 grader(regex·file_exists)이며 LLM 채점은 쓰지 않았다. 점수는 "grader가 본 행위"의 통과율이고, 5절이 grader가 보지 못한 것을 따로 적는다.

## 1. 범위와 방법

- 대상: 브랜치 `feature/dlc-plugin` HEAD `860be02`(R4 커밋 3개 + Opus 리뷰 기록)의 `dlc/` 플러그인. eval 케이스 8개(`dlc/evals/<case>/case.yaml`, 픽스처 `scaffold.sh`).
- 실행: `dlc/evals/run.sh -j 2 --keep-temp` = `claude plugin eval ./dlc --runs 1 --ablation none --scaffold --allow-tools Bash Write Edit --trust-plugin --no-publish --threshold 1.0`. Claude Code 2.1.270, 2026-09-13 19:05 KST, 324초, 약 $4.15. `run.sh`가 `~/.docker`의 심링크 디렉터리 2개를 실행 동안 옮기고 되돌렸다(끝난 뒤 심링크 30개 복원 확인).
- 케이스 설계: 단일 프롬프트라 질문 답·요약 확인·승인을 프롬프트에 사전 제공한다(설계 §8 R2 결정). 라우터 안내 모드 3건은 사전 답이 없거나 한 줄(커서 선택)이다. `router-all-gate-waits`만 승인 답을 주지 않아 게이트 대기 자체를 본다.
- 판정 자료: 러너 JSON(`aggregate-result.json`, `results/2026-09-13T10-04-00-450Z/`는 gitignore), `--keep-temp`로 남은 trace 8개. 러너가 에이전트 cwd를 `sealed`로 봉인해 산출물 파일은 사후 열 수 없고, 파일 내용은 trace의 Write 도구 입력으로 확인했다.
- 같은 날 앞선 실행 2회(1차 전체, grader 수정 뒤 3건 재실행)를 3절에서 비교한다. 1차 실패 3건의 원인과 수정은 설계 §8 R4·Opus 리뷰(`2026-09-13-dlc-r4-review-opus.md` 지적 1~3)에 있다.

## 2. 결과 — 최종 실행

| 케이스 | 대상 | turns | 비용 | 시간 | grader | 점수 |
|---|---|---|---|---|---|---|
| `router-guide-empty` | 라우터 안내 모드 — 작업 없음 | 4 | $0.18 | 14초 | 4/4 | 1.0 |
| `router-guide-next` | 라우터 안내 모드 — 다음 스킬 안내 | 2 | $0.15 | 10초 | 4/4 | 1.0 |
| `router-no-cursor` | 라우터 — 커서 없음, 기존 작업 나열 후 커서 기록 | 7 | $0.21 | 19초 | 5/5 | 1.0 |
| `router-all-gate-waits` | 라우터 `--all` — 승인 게이트 대기(침묵≠승인) | 15 | $0.68 | 112초 | 6/6 | 1.0 |
| `express-requirements` | express init→requirements 승인 + "여기까지" 중단 | 17 | $0.80 | 122초 | 11/11 | 1.0 |
| `requirements-vague-followup` | requirements — 모호어 후속 질문 | 17 | $0.70 | 114초 | 6/6 | 1.0 |
| `bugfix-requirements` | bugfix init→requirements 승인 | 15 | $0.72 | 104초 | 9/9 | 1.0 |
| `plan-supplies-units` | plan — units.md 공급, 유닛 집합·실행 명령 검사 | 18 | $0.71 | 108초 | 9/9 | 1.0 |

8 케이스 전부 1.0, grader 54개 전부 통과, `--threshold 1.0` 종료 코드 0. `claude plugin validate ./dlc` 통과, `python3 -m unittest discover -s dlc/skills/dlc/tests` 87건 GREEN.

## 3. 실행 간 비교

| 케이스 | 1차 (18:07) | 재실행 (18:2x, 3건) | 최종 (19:05) |
|---|---|---|---|
| `router-guide-empty` | 3턴 / $0.16 / 3/4 | 4턴 / $0.15 / 4/4 | 4턴 / $0.18 / 4/4 |
| `router-guide-next` | 4턴 / $0.17 / 4/4 | — | 2턴 / $0.15 / 4/4 |
| `router-no-cursor` | 6턴 / $0.22 / 5/5 | — | 7턴 / $0.21 / 5/5 |
| `router-all-gate-waits` | 13턴 / $0.62 / 5/6 | 13턴 / $0.64 / 6/6 | 15턴 / $0.68 / 6/6 |
| `express-requirements` | 18턴 / $0.88 / 11/11 | — | 17턴 / $0.80 / 11/11 |
| `requirements-vague-followup` | 14턴 / $0.67 / 6/6 | — | 17턴 / $0.70 / 6/6 |
| `bugfix-requirements` | 16턴 / $0.76 / 9/9 | — | 15턴 / $0.72 / 9/9 |
| `plan-supplies-units` | 23턴 / $0.93 / 8/9 | 15턴 / $0.69 / 6/9 | 18턴 / $0.71 / 9/9 |

- 1차 5/8 → 최종 8/8. 달라진 것은 grader 3개(부정 패턴 2개 좁힘, units.md 앵커의 JSON 통과 구간 보완)뿐이고 스킬·스크립트는 세 실행 사이에 바뀌지 않았다. 즉 1차의 실패 3건은 전부 채점기 결함이었고, 스킬 행위는 세 실행에서 같은 결과를 냈다.
- 턴 수는 실행마다 ±2~5 흔들린다(예: `plan-supplies-units` 23 → 15(한도 중단) → 18, `router-guide-next` 4 → 2). 비용은 케이스당 $0.15~$0.93, 전체 $4.1~4.4. 라우터 안내 모드 3건은 합쳐 $0.5 안이다.
- 재실행의 `plan-supplies-units`는 Claude 계정 세션 한도로 plan.md 작성 직후 끊겼던 건이다(Opus 리뷰 지적 3). 최종 실행에서 `check plan: OK` → `approve plan` → `status`까지 끝나 R4 잔여 (1)이 닫혔다.

## 4. 케이스별 행위 관찰 (trace)

| 케이스 | 도구 순서 (요약) | 산출물·질문 | 특이점 |
|---|---|---|---|
| `router-guide-empty` | `status` → `status` → `ls docs/dlc` | 없음 | 4턴. dlc.py 오류 문구를 그대로 인용한 뒤 "아직 작업이 없습니다. `/dlc:dlc-init`을 먼저 부르세요"로 끝. init 실행 없음 |
| `router-guide-next` | `status` 1회 | 없음 | 2턴. status 출력 전체를 코드 블록으로 보이고 "다음은 요구사항 분석입니다. `/dlc:dlc-requirements`를 부르세요" 한 줄. 스킬 명세의 최소 경로 그대로 |
| `router-no-cursor` | `ls` → `status`(오류: 작업 폴더 목록) → `ls -a docs/dlc` → Write `active` → `status` | `docs/dlc/active` | 7턴. 사전 동의대로 커서를 쓰고 status를 다시 보였다. `dlc.py init` 없음 |
| `router-all-gate-waits` | Read protocol·state-format → `next` → Read grounding·dlc-requirements SKILL·state·log → `start requirements` → Grep·Read `dlc.py` → Write 질문·requirements → `check requirements` | Q4(기능·시나리오·기술·품질), FR1·FR2·NFR1~3, 출처 태그 29 | 15턴. check OK 뒤 protocol 10단계 (a)~(d)를 표로 보이고 "승인 / 수정 요청"을 물은 채 종료. `approve` 미실행, `start plan` 미실행 |
| `express-requirements` | `next` → Read 라우터 SKILL·protocol → `init --profile express` → `next` → Read dlc-requirements SKILL·grounding → `start requirements` → Bash `grep`/`sed`로 `dlc.py`의 `cmd_check`·`check_questions` 읽기 → Write 질문·requirements → `check` → `approve` → `status` | Q5(기능·시나리오·기술·품질·비기능), FR1~3·NFR1, 출처 태그 34 | 17턴. 질문 5개는 minimal 기준(2~4)을 넘었다 — 사용자가 주제 5개를 줬기 때문이며 R2 관찰과 같다. `start plan` 없음("여기까지" 준수) |
| `requirements-vague-followup` | Read protocol·grounding·state·log → `next` → `start requirements` → Bash `sed`로 `dlc.py` 검사 로직 읽기 → Write 질문·requirements → `check` → `approve` | Q4 + 후속 Q5 "(Q4 후속) '적당히'가 구체적으로 어느 수준·범위를 뜻합니까?", FR1·NFR1, 출처 태그 26 | 17턴. Q4 답을 `X - 적당히 테스트되면 된다.`로 그대로 기록한 뒤 Q5를 추가하고 `X - 통합 테스트 2건 … test_stock_200 … test_stock_404`를 기록. 최종 보고에 "답변 검사에서 걸린 것"과 남은 가정 4건을 명시 |
| `bugfix-requirements` | `next` → Read protocol·state-format·grounding·라우터 SKILL → `init --profile bugfix` → `next; status` → Read dlc-requirements SKILL → `start requirements` → Write 질문·requirements → `check` → `approve; status` | Q4(재현 조건 / 기대·실제 / 영향 범위 / 회귀 테스트), FR1·FR2·NFR1, 출처 태그 36 | 15턴. bugfix 주제 1~4를 순서대로 물었고 5(근본 원인 가설)는 "주어지지 않아 묻지 않고 가정 절로" — 스킬 문장("없으면 묻지 않는다") 준수. 요구사항 골격도 bugfix 지침대로(FR1 기대 동작, FR2 회귀 테스트, NFR1 데이터 정합성) |
| `plan-supplies-units` | `ls`/`find` → Read protocol·grounding·state·requirements·질문·log → `next` → `start plan` → Bash `grep`로 `dlc.py`의 plan 검사 읽기 → Write plan-questions·units·plan → `check plan` → `approve plan` → `status` | Q4(유닛 분해·seam·테스트 수준과 실행 명령·완료 정의), units.md 유닛 2행(`u1-stock-query`·`u2-stock-endpoint`), plan.md 유닛 순서 2행 + `실행 명령:` 줄, 출처 태그 6+16 | 18턴. R4에 추가된 `check plan` 검사(유닛 집합 일치·실행 명령)를 첫 시도에 통과. approve 출력 "다음: build → dlc-build"를 그대로 전하고 멈춤 |

## 5. 완성도 평가

**증명된 것 (grader + trace).**

- 명시 호출 발동: 8 케이스 모두 프롬프트 첫 줄의 슬래시 명령으로 스킬이 발동해 `dlc.py`를 첫 도구 호출 안에서 실행했다. 안내 모드 두 케이스는 각각 4턴·2턴으로 스킬 본문의 최소 경로를 그대로 밟았다.
- 라우터 3분기: 작업 없음(안내 후 종료, init 대행 없음), 커서 있음(status + 다음 스킬 안내, 다음 스킬 대행 없음), 커서 없음(작업 나열 → 커서 기록 → status)이 각각 명세대로 나왔다.
- 승인 게이트: 승인 답이 없는 케이스에서 에이전트는 `check` 통과 뒤 (a)~(d)를 보이고 멈췄다. `approve`도 다음 스테이지 `start`도 없다 — protocol.md "침묵을 승인으로 치지 않는다"가 실행에서 지켜졌다. 사전 승인이 있는 4 케이스에서는 "여기까지"에서 멈춰 다음 스테이지를 시작하지 않았다.
- 질문 파일 규율: 다섯 케이스 모두 `## Q<n>.` 번호 연속, `[Answer]:` 행, `Consolidated Summary Confirmation` = `Looks correct`. 모호어("적당히")를 그대로 기록하고 후속 질문 `Q<n+1>`을 붙이는 protocol 6단계가 실제로 돌았다. bugfix는 질문 주제 전환과 골격 지침을 둘 다 따랐다.
- 산출물 검사: 다섯 스테이지 실행 모두 `dlc.py check`를 첫 시도에 통과했다(재시도 0). 출처 태그가 requirements.md에 26~36개, plan.md에 16개 붙었고 가정 절은 매번 채워졌다. R4에 새로 들어간 `check plan` 규칙(유닛 집합·실행 명령)을 에이전트가 별도 안내 없이 충족했다.

**grader가 보지 못한 것 — 이 점수가 말하지 않는 것.**

- 안내 문장의 유무는 grader에 없다(Opus 리뷰 지적 1). 이번 실행에서는 trace로 두 라우터 케이스가 실제 안내 문장을 낸 것을 눈으로 확인했지만, 채점기는 `dlc.py init`·`start` 부재만 봤다. 지적 1의 조치(안내 문장 grader 복원)가 들어가면 자동으로 잡힌다.
- 발동 지표 `dlc\.py (init|next|…)`는 스킬 파일 Read와 구분되지 않는다(지적 2). 이번 실행에서는 8 케이스 모두 실제 실행이 있어 문제가 되지 않았지만, 지표 자체의 증명력은 `dlc.py` 출력 grader(`작업 폴더:`, `requirements: done`, `check plan: OK`)에 있다.
- 사전 답변의 한계: 답을 미리 주는 케이스는 "사용자와의 다중 턴 대화"를 재현하지 않는다. `bugfix-requirements`는 프롬프트가 bugfix 주제 순서대로 답을 주므로 질문 주제 전환의 독립 증거로는 약하다(지적 6). 독립 증거는 Codex 실측(`$dlc-requirements`만으로 재현·영향·회귀 질문 생성)이다.
- 산출물 품질은 "필수 절·ID·태그·커버리지"까지만 기계로 본다. 내용의 타당성(예: `router-all-gate-waits`가 SSO 인증·읽기 전용 접근·통합 테스트 2건을 NFR1~3으로 올린 것 — 같은 답변을 `express-requirements`는 제약·수용 기준으로 두고 NFR은 p95 하나만 뒀다)은 실행마다 다르고 grader가 판정하지 않는다. 이것은 스킬 문장의 분류 지침("품질 차원 → 수용 기준", "기술 차원 → 제약")이 있어도 에이전트가 다르게 배치할 수 있음을 보인다.

**관찰 — 개선 후보 (결함이 아닌 신호).**

1. 에이전트 5회 중 3회(express·vague·plan)가 `dlc.py` 소스를 `grep`·`sed`로 읽어 `check`가 무엇을 보는지 확인했다. protocol.md·스킬 완료 기준에 검사 목록이 있는데도 소스를 본 것은, 문서의 검사 설명이 "무엇이 실패하는가"를 충분히 구체적으로 말하지 않는다는 신호다. state-format.md의 검사 문단을 항목별 표로 바꾸면 줄어들 수 있다.
2. 질문 선택지가 사전 답변에 맞춰 만들어진다(`express-requirements` 답 5개 전부 `A`). 사전 답변 방식의 부산물이며 실제 대화에서는 나타나지 않는다. eval의 측정 범위 한계로 기록한다.
3. NFR 분류의 실행 간 편차(위 4번째 항목). 스킬의 여섯 차원 표에 "제약·완료 기준은 NFR이 아니다" 한 줄을 두면 흔들림이 줄 것이다. R5 후보.
4. 질문 수가 minimal 기준(2~4)을 넘는 것은 사용자가 준 주제 수에 비례한다(express 5). 기준이 상한이 아님은 R2에 기록됐다.

## 6. 미측정 영역

- design·build·verify 스테이지는 eval 케이스가 없다. 헤드리스 실측(R3 express 완주·full design, R4 build 재개)으로만 확인됐다. build는 실제 코드 생성이 필요해 케이스당 $2~4로 비싸고 산출물이 픽스처 코드에 의존한다 — 만들려면 R3 `wcl` 픽스처를 scaffold로 옮기는 방식이 후보다.
- 실제 사용자 다중 턴(질문 → 답 → 후속 → 요약 → 승인)은 러너가 지원하지 않는다. Codex `exec resume` 경로가 다중 턴 실측이며 답변 이후 턴이 계정 한도로 남아 있다(설계 §8 R4 잔여 (2)).
- Codex·Gemini에서의 eval은 없다(러너가 Claude Code 전용). 두 에이전트는 설치·발동·질문 생성까지 수동 실측이다.
- ablation(플러그인 없이 같은 프롬프트) 비교는 `--ablation none`으로 끄고 돌렸다. 명시 호출 스킬은 플러그인 없이는 슬래시 명령 자체가 없어 비교가 성립하지 않는다.

## 7. 결론

eval이 보는 범위 — 라우터 3분기, `--all` 게이트, requirements(express·모호어·bugfix), plan(units.md 공급) — 에서 스킬은 명세대로 동작하며 세 실행에 걸쳐 결과가 흔들리지 않았다. 1차의 실패는 전부 채점기 결함이었고 스킬 수정 없이 8/8에 도달했다. 남은 약점은 채점기의 증명력(안내 문장·발동 지표)과 사전 답변 방식의 측정 한계이며, 스킬 자체의 개선 후보는 검사 설명의 구체성과 NFR 분류 지침 두 가지다. design·build·verify는 eval 밖이고 헤드리스 실측 기록이 그 자리를 대신한다.
