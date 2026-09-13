# dlc 2라운드 리뷰 통합 분석 (2026-09-13)

이슈 #2의 리뷰 산출물이다. Fable 리뷰(`2026-09-13-dlc-r2-review-fable.md`, 지적 1~14)와 Codex 리뷰(`2026-09-13-dlc-r2-review-codex.md`, P1 1 + P2 2 + P3 3 + 완료 조건 표)를 대조하고, 모든 지적을 오케스트레이터가 커밋 `1dae4d1` 작업 트리에서 직접 재현한 뒤 수용·기각을 정했다. **사용자 지시(2026-09-13)로 이 문서는 분석과 반영안까지만 담고, 코드·스킬·설계 문서는 아직 고치지 않았다.** 반영 여부와 순서는 사용자가 정한다.

- 재현 방법: 인용된 파일·줄을 전부 다시 열어 대조. `dlc.py`를 임시 brownfield 프로젝트에서 실행해 analyze 승인 뒤 소스 변경 시나리오 재현. `python3 dlc/skills/dlc/tests/test_dlc.py`(직접)와 `python3 -m unittest discover`(문서 방식) 실행 건수 비교. 1차 eval의 남은 trace(`/private/tmp/e-aCSA9s/out/trace.jsonl`)에서 Read 도구 결과만 추출해 현재 grader 3개를 적용(음성 대조), Write 앵커 패턴을 원 trace(양성)와 Write 호출·결과를 제거한 trace(음성)에 적용. eval 결과 JSON 2개의 `claudeVersion` 확인.
- 재현 결과: 두 리뷰의 지적 **전부 재현됨**. 기각 0건. 리뷰가 놓친 결함은 없었고, 오케스트레이터가 반영안을 검증한 항목 1건(U1)을 추가했다.
- 두 리뷰가 상충하는 지적: **심각도만 다른 곳 1건**(U4, 출처 태그 목록). Codex가 채택하지 않은 Fable 지적 1건(U11, practices 갱신 모드의 질문 없는 경로)은 아래 2절에 이유를 적었다.

## 1. 지적 통합표

심각도는 두 리뷰 중 높은 쪽을 따르되, 재현 결과로 조정한 곳은 비고에 적었다. 위치의 줄 번호는 커밋 `1dae4d1` 기준.

| # | Fable | Codex | 심각도 | 위치 | 결함 | 재현 결과 | 비고 |
|---|---|---|---|---|---|---|---|
| U1 | 1 | P1-1 | **P1** | `dlc/evals/express-requirements/case.yaml:48-55, 70-75`, 설계 §8 "파일 내용 채점" 행 | trace 대상 regex grader 3개(`fr1-defined-in-trace`, `summary-confirmed`, `requirements-md-has-sections`)가 참조 문서(protocol.md·grounding.md·dlc-requirements/SKILL.md)의 Read 결과에도 매치돼 requirements.md를 쓰지 않아도 통과한다 | **재현.** 1차 trace의 Read 결과(6건)만 모은 문자열에 현재 패턴 3개 적용 → 셋 모두 참 | 파일 존재는 `file_exists` 3개가 따로 보므로 "파일 없이 11/11"은 아니다. 문제는 내용·요약 확인을 이 점수로 입증할 수 없다는 것. 설계 §8이 이 방식을 R4 기준으로 확정해 두어 그대로 두면 suite 전체에 번진다. 반영안은 3-1 |
| U2 | 3 | P2-2 | P2 | `dlc/skills/dlc-analyze/SKILL.md:23` | `next`가 analyze를 안 가리키면 "지문 일치로 건너뛴 경우"라 단정한다. 같은 작업에서 analyze가 이미 `done`이고 그 뒤 소스가 바뀐 경우에도 `next`는 analyze를 건너뛴다(`next_stage`는 done을 무조건 건너뜀). 이때 스킬은 "현재 소스와 일치합니다"라는 거짓 문장을 내고, 이어 제안하는 `start analyze --force`는 `pending`만 허용해 거부된다 | **재현.** analyze 승인 → 소스 변경 → `next`=requirements, `check analyze`=지문 불일치(exit 1), `start analyze --force`="analyze 가 이미 done 입니다."(exit 2) | 반영안은 3-2 |
| U3 | 4 | P2-3 | P2 | `dlc/skills/dlc-init/SKILL.md:44-47` | 사용자에게 보이는 프로파일 표에서 `full` 행만 "기존 코드가 있으면 분석이 먼저"라 적고 `express`·`bugfix` 행은 요구사항부터 시작한다고 설명한다. 세 프로파일 모두 brownfield면 analyze가 먼저다(state-format.md:64-68, dlc.py:38-39) | **재현.** 표 본문 대조 | 표 아래 한 줄 "세 프로파일 모두 기존 코드가 있으면 분석(analyze)이 먼저 끼어든다" 추가가 가장 작다 |
| U4 | 2 | P3-2 | P2 | 설계 문서 §5 "출처 태그" 문단(:99) vs `grounding.md:5-13` | 설계는 태그 4종, grounding.md는 R2에서 `[code:<경로>]`를 더해 5종. 설계 §9 열린 질문에는 추가 사실이 있지만 규범 문단은 안 고쳤다 | **재현.** 두 문단 대조 | Fable P2·Codex P3. 실행을 막지는 않지만 설계 문서가 규칙의 원천이라 P2로 둔다. 설계 §5에 `[code:<경로>]` 한 줄 추가 |
| U5 | 5 | — | P2 | `dlc/skills/dlc-init/SKILL.md:37` | 스캔 결과가 사용자 인식과 다를 때 알려 주는 제외 목록이 `docs`·`build`·`dist`·`node_modules`·점 폴더만이다. 실제 `EXCLUDED_DIRS`(dlc.py:79-81)에는 `out`·`target`·`vendor`·`venv`·`coverage` 등이 더 있어 그 아래에 소스가 있는 프로젝트의 greenfield 오판을 이 문장으로 설명할 수 없다 | **재현.** 목록 대조 | "등"을 붙이고 정확한 목록은 `dlc.py`의 `EXCLUDED_DIRS`를 가리키는 편이 목록 복제보다 안전하다 |
| U6 | — | P3-1 | P3 | `dlc/skills/dlc/tests/test_dlc.py:865-866` | `if __name__ == "__main__": unittest.main()`이 파일 중간(865행)에 있고 R2 계약 테스트 클래스(893행~)가 그 뒤에 온다. 파일을 직접 실행하면 신규 3건이 빠진다 | **재현.** 직접 실행 75건, discover 78건 | 문서의 공식 검증 명령(discover)은 정상. 진입점을 파일 끝으로 옮긴다 |
| U7 | — | P3-3 | P3 | 설계 §8 첫 문장(:139), 이슈 #2 코멘트 | "Claude Code 2.1.269"로 묶어 적었지만 1차는 2.1.269, 2차는 2.1.270에서 실행됐다(두 실행 사이에 CLI가 자동 갱신됨) | **재현.** `express-r2-run1.json` 2.1.269 / `express-r2-run2.json` 2.1.270, 현재 CLI 2.1.270 | 실행별 버전을 나눠 적는다 |
| U8 | 6 | — | P3 | `dlc/skills/dlc-analyze/SKILL.md:42` | analyze만 depth 수를 "상한"이라 부른다. protocol.md:20은 "기준", 설계 §8은 "기준은 상한이 아니다" | 대조 확인 | "대개 0~2개다. depth 기준(protocol.md)보다 적어도 된다"로 |
| U9 | 7 | — | P3 | `dlc/skills/dlc-analyze/SKILL.md:89` | 한 문장 안에서 "기존 행을 지우지 않고"와 "사라진 모듈은 행을 지우고"가 충돌 | 대조 확인 | "바뀐 행만 고치고 나머지는 보존한다. 저장소에서 사라진 모듈의 행만 지우되 …"로 |
| U10 | 8 | — | P3 | `dlc/skills/dlc-analyze/SKILL.md:93` | 완료 기준이 질문 파일 검사를 빠뜨렸다. R2에서 `QUESTION_STAGES`에 analyze가 들어가 `check analyze`가 `analyze-questions.md`의 답변·`Looks correct`도 본다 | dlc.py:64 확인 | "질문 파일이 있으면 모든 답변과 `Looks correct`" 추가 |
| U11 | 10 | (미채택) | P3 | `dlc/skills/dlc-practices/SKILL.md:21, 47, 92` | 갱신 모드에서 바꿀 항목이 없을 때의 경로가 없고, 완료 기준 92행은 질문 파일이 항상 있는 것처럼 적었다 | 대조 확인 | Codex는 protocol.md:20 "질문이 하나도 필요 없으면 파일을 만들지 않는다"가 이미 있어 차단 결함으로 안 봤다. 수용하되 P3. 2절 참조 |
| U12 | 9 | — | P3 | `dlc/skills/dlc-intent/SKILL.md:23, 36` | intent는 full 전용이고 full은 standard만이라 "minimal이면 1~4번만 묻는다" 분기는 도달 불가 | 대조 확인 | 지우거나 "(현재 프로파일 구성에서는 나오지 않는다)" 표시. YAGNI |
| U13 | 11 | — | P3 | `case.yaml:13` vs 설계 §8 vs 이슈 #2 완료 조건 | 허용 도구 기록이 세 곳에서 다르다: case.yaml `allowed_tools` 6개 / 설계 `--allow-tools Bash Write Edit` / 이슈 `--allow-tools Bash` | 대조 확인 | 모순이 아니라 층이 다르다. `allowed_tools`는 모델에 보이는 도구 목록, `--allow-tools`는 그중 게이트 도구(Bash·Write·Edit)에 대한 운영자 허가다. Read·Glob·Grep은 게이트가 아니라 허가 불필요. 이 관계를 설계 §8에 한 줄 적고 이슈 표기는 실제 값으로 |
| U14 | 12 | — | P3 | 설계 §4 표 `dlc-requirements` 행(:56) | 산출물 설명에 "스토리"가 있지만 골격·`ARTIFACTS`에 스토리 절은 없고 "의도 요약"은 표에 없다 | dlc.py:53-54 대조 | "(의도 요약, FR/NFR ID, 제약, 범위 밖, 가정)"으로 정정 |
| U15 | 13 | — | P3 | `dlc/skills/dlc-init/SKILL.md:38` | "`next` 출력의 첫 단어의 스킬"이 모호. 첫 줄은 `<stage> dlc-<stage>`라 스킬 이름은 둘째 단어 | dlc.py:509 대조 | "첫 줄 `<stage> dlc-<stage>`의 스킬 이름을"로 |
| U16 | 14 | — | P3 (R3 메모) | `test_dlc.py:871-908` | `skeleton_h2s`가 `ARTIFACTS` 키만 순회해 (a) `build/<unit>.md`(`BUILD_UNIT_SECTIONS`)는 검사 대상이 아니고 (b) `decisions.md`는 필수 절 `[]`이라 dlc-design에 빈 골격 블록이 없으면 `assertIsNotNone`에서 실패한다 | dlc.py:56, 61 대조 | R3 착수 시 함께 고친다. R2 스킬에는 영향 없음 |

## 2. 한쪽만 잡은 결함과 이유

- **Codex만 잡은 것(U6, U7).** Codex는 검증 명령을 두 방식으로 실행하고 결과 JSON의 메타데이터까지 열었다. Fable은 문서의 공식 명령(discover)만 실행해 진입점 위치를 못 봤고, 버전은 설계 문서 서술을 그대로 받았다.
- **Fable만 잡은 것(U5, U8~U16).** Fable은 스킬 프로즈를 문장 단위로 코드와 대조했고 Codex는 CLI 실행 QA 중심이라 실행을 막지 않는 표현·중복·모호함은 새 결함으로 세지 않았다고 명시했다. Codex가 U11을 채택하지 않은 이유는 protocol.md의 일반 규칙이 그 경로를 덮는다는 것인데, 스킬 완료 기준(92행)이 "질문 파일의 모든 답변"을 무조건으로 적어 일반 규칙과 어긋나는 문장은 남으므로 P3로 수용한다.
- **둘이 같이 잡은 것(U1~U4).** 계약 위반과 잘못된 안내다. 독립 재현이 둘 다 있어 확신도가 가장 높다.

## 3. 설계 결정이 필요한 항목

### 3-1. eval 내용 grader를 무엇에 앵커링하는가 (U1)

| 선택지 | 내용 | 장점 | 단점 |
|---|---|---|---|
| **A (권장)** | Write 도구 입력에 앵커링. `requirements\.md","content":"` 뒤에 JSON 문자열 안에서만 움직이는 `(?:[^"\\]\|\\.)*?`로 필수 절 여섯 개·`### FR1\.`을 잇고, 요약 확인은 `requirements-questions\.md","content":"` 뒤에 `\[Answer\]: Looks correct`를 요구 | **검증됨.** 1차 trace에서 앵커 리터럴은 Write의 tool_use 레코드와 그 tool_result(입력을 되돌려 줌)에만 있고 Read 결과에는 없다. 원 trace 매치(양성), Write 호출·결과를 모두 뺀 trace 불매치(진짜 음성) 확인. case.yaml만 고치면 된다 | Write 대신 Bash heredoc으로 파일을 쓰면 놓친다(현재 스킬은 Write를 쓰지만 보장은 아님). trace 직렬화 형식(`"file_path"` 뒤 `"content"` 순서)에 의존 |
| B | 참조 문서에 없는 문자열을 요구(사전 답변 고유 표현 "창고가 0개", `[Q5]` 이상) | 형식 의존 없음 | 프롬프트 픽스처에 결합돼 케이스마다 다시 짜야 한다. "참조 문서에 없음"을 매번 확인해야 함 |
| C | 최종 파일 내용을 직접 검사 | 가장 정확 | 러너의 `regex` `{source: file, path}`가 glob을 안 받고 작업 폴더 이름에 날짜가 있어 지금은 불가. 러너가 glob을 지원하면 그때 전환 |

A를 권장한다. A로 바꾼 뒤 설계 §8 "파일 내용 채점" 행을 "trace에는 Read 결과도 남으므로 Write 입력 앵커가 필요하다"로 정정하고, eval을 1회 재실행해 11/11을 다시 받는다(R4 suite의 기준이 되므로 재실행은 생략하지 않는다).

### 3-2. 승인된 analyze 뒤 소스가 바뀌었을 때의 경로 (U2)

| 선택지 | 내용 | 장점 | 단점 |
|---|---|---|---|
| **A (권장)** | 스킬 분기만 추가. `state.md`의 analyze가 `pending`이고 지문이 같으면 지금 문장대로, `done`이면 "이 작업에서는 analyze가 이미 승인됐다. codebase.md를 갱신하려면 새 작업을 만들면 지문 불일치로 analyze가 다시 뜬다"고 안내하고 끝낸다 | 코드 변경 없음. R1에서 확정한 "`--force`는 pending 한정" 계약을 지킨다 | 같은 작업 안에서 codebase.md를 갱신할 길은 없다 |
| B | `--force`가 `done`도 받아 다시 `active`로 되돌린다 | 같은 작업에서 갱신 가능 | done→active 역전이가 생겨 상태 모델(넷뿐)의 단순함이 깨진다. `require_forceable`·테스트·state-format.md·protocol.md:17을 모두 고쳐야 함 |

A를 권장한다. 뒤 단계가 codebase.md를 `[practice]`로 인용하는데 그 근거를 같은 작업 도중에 바꾸는 것은 오히려 위험하다.

### 3-3. 결정 없이 고칠 수 있는 것

U3~U15는 문장 수정 또는 진입점 이동이며 선택지가 없다. U16은 R3 착수 항목.

## 4. 개선 목표

### G1. 검증 장치가 산출물 내용을 실제로 입증한다

- **왜**: eval 점수가 R2 완료 조건이자 R4 suite의 기준이다. 참조 문서 Read만으로 통과하는 grader는 완료 판정을 거짓으로 만든다.
- **속한 지적**: U1, U7, U13
- **동작 결정**: 3-1 A. 설계 §8 "파일 내용 채점" 행 정정, 실행 버전을 1차 2.1.269 / 2차 2.1.270으로 분리, `allowed_tools`(모델 도구 목록)와 `--allow-tools`(게이트 도구 운영자 허가)의 관계 한 줄 추가. 이슈 #2 완료 조건의 `--allow-tools Bash`는 실제 값 `Bash Write Edit`로 코멘트에 정정.
- **완료 확인**: 1차 trace의 Read 결과만 모은 문자열에 새 패턴 3개 적용 → 셋 모두 거짓. eval 재실행 11/11. 재실행 결과 JSON을 이슈 코멘트에 요약.

### G2. 스킬 안내가 코드의 실제 전이와 일치한다

- **왜**: 스킬 프로즈가 곧 실행 절차다. 거부될 명령을 제안하거나 실제와 다른 단계 순서를 보이면 사용자가 잘못된 선택을 한다.
- **속한 지적**: U2, U3, U5, U15
- **동작 결정**: 3-2 A. init 프로파일 표 아래 조건부 analyze 한 줄. 스캔 제외 목록은 `EXCLUDED_DIRS`를 가리킴. `next` 출력의 스킬 이름 위치 명시.
- **완료 확인**: analyze 승인 → 소스 변경 → `dlc-analyze` 재호출 시나리오를 스킬 문장대로 따라가면 거부되는 명령을 만나지 않는다(수동 대조). brownfield에서 express를 고른 사용자가 표에서 analyze를 미리 본다.

### G3. 문서와 코드가 일치한다

- **왜**: 규칙의 원천(설계 문서·grounding.md)이 서로 다르면 어느 쪽을 따를지 에이전트마다 갈린다.
- **속한 지적**: U4, U8, U9, U10, U11, U12, U14
- **동작 결정**: 설계 §5 태그 5종, §4 requirements 행 정정. analyze의 "상한"→"기준", 갱신 모드 문장 재서술, 완료 기준에 질문 파일 조건부 추가. practices 갱신 모드의 "바꿀 것 없으면 질문 파일 없이 check→승인" 한 줄, 완료 기준 "질문 파일이 있으면". intent의 minimal 분기 제거.
- **완료 확인**: 문서 grep — 설계 §5에 `[code:<경로>]` 있음, analyze:42에 "상한" 없음, intent에 "minimal이면 1~4번" 없음. `StageSkillContracts` GREEN 유지(골격 H2는 건드리지 않음).

### G4. 테스트 진입점이 모든 테스트를 실행한다

- **속한 지적**: U6
- **동작 결정**: `if __name__ == "__main__": unittest.main()`을 파일 끝으로.
- **완료 확인**: `python3 dlc/skills/dlc/tests/test_dlc.py`와 discover 모두 78건.

### 실행 순서와 커밋 (반영이 결정되면)

1. G4 → G3 → G2 (코드·문서, 자식 프로세스 불필요) → `fix(dlc)` 커밋 1개.
2. G1 (case.yaml + 설계 §8) → eval 재실행 1회 → `fix(dlc)` 또는 `test(dlc)` 커밋 1개. 재실행 전 `~/.docker` 심볼릭 링크 우회(설계 §8)를 다시 적용해야 한다.
3. 이 문서에 "조치 결과" 절 추가, 이슈 #2 코멘트로 재실행 결과 게시.

## 5. 범위 밖 메모

- **원본 증거의 보존.** eval 결과 JSON·HTML은 `.gitignore`(`*/evals/results/`) 대상이고 trace는 `/private/tmp`에 있어 다른 PC에서 재검토할 수 없다(Codex 4절). 2차 trace는 이미 없다. 이슈 코멘트의 grader 표가 유일한 영구 기록이다. R4에서 결과 JSON을 이슈에 첨부하는 절차를 정한다.
- **P1 0건 조건.** 이슈 #2 완료 조건 "Fable 리뷰 후 P1 0건"은 현재 미충족이다(P1 1건 보류). 보류는 해결이 아니다(Codex 4절). U1 반영 후에만 충족으로 표기한다.
- **push.** 원격 `feature/dlc-plugin`은 기준 커밋 `c92c91c`에 있고 `1dae4d1`은 로컬에만 있다. 사용자 승인 대기.
- **R3 메모.** U16(테스트 파서 범위), 그리고 Codex가 언급한 "에이전트가 질문하고 산출물을 쓰는 스킬 전체 실행"은 CLI QA로 대체할 수 없다는 한계 — R3의 design·plan·build·verify 실행 검증도 eval 또는 헤드리스 실행으로 한다.

## 조치 결과 (2026-09-13)

사용자 결정: 3-1 A(Write 입력 앵커), 3-2 A(스킬 분기만 추가). U1~U15 전부 반영, U16은 R3 착수 항목으로 남김.

| 목표 | 지적 | 커밋 | 확인 |
|---|---|---|---|
| G4 테스트 진입점 | U6 | `e939a4d` | `python3 dlc/skills/dlc/tests/test_dlc.py` 78건, discover 78건 |
| G3 문서·코드 일치 | U4, U8, U9, U10, U11, U12, U14 | `e939a4d` | 설계 §5 태그 5종·§4 requirements 행 정정. analyze에 "상한" 0건, intent에 "minimal이면 1~4번" 0건(grep). `StageSkillContracts` GREEN |
| G2 스킬 안내 = 코드 전이 | U2, U3, U5, U15 | `e939a4d` | dlc-analyze:23-26 pending/done/skipped 분기, done이면 `--force` 미제안. dlc-init 표 아래 조건부 analyze 한 줄, 스캔 제외 목록은 `EXCLUDED_DIRS` 참조, `next` 첫 줄의 스킬 이름 위치 명시 |
| G1 검증 장치 | U1, U7, U13 | 다음 커밋 | case.yaml 내용 grader 3개 → Write 입력 앵커 2개(`requirements-md-written-with-sections-and-fr1`, `questions-md-written-with-summary-confirmed`), 총 10개. 1차 trace에서 양성 매치·Write 제거 시 불매치 확인 뒤 3차 실행: 2.1.270, 18턴, $0.80, **10/10**. 설계 §8에 실행별 버전(1차 2.1.269 / 2차·3차 2.1.270), `allowed_tools`와 `--allow-tools`의 관계, "파일 내용 채점" 행 정정 |

이슈 #2 완료 조건 "Fable 리뷰 후 P1 0건"은 이 조치로 충족됐다. push는 사용자 승인 대기.
