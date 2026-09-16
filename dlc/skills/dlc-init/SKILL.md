---
name: dlc-init
description: 개발 생명주기 작업을 시작한다. 프로파일(full·express·bugfix)과 작업 이름·설명을 확인받아 작업 폴더와 state.md를 만들고 저장소 스캔 결과를 보인다.
disable-model-invocation: true
metadata:
  author: JK-Kim4
  version: "0.1.0"
---

# dlc-init — 작업 시작

생명주기의 첫 스테이지다. 작업 폴더 `docs/dlc/<YYMMDD>-<slug>/`와 `state.md`를 만들고, 저장소를 스캔해 기존 코드가 있는지(brownfield) 없는지(greenfield)를 기록한다. 질문 파일과 승인 게이트가 없는 유일한 스테이지다. `dlc.py init`이 init을 곧바로 done으로 기록한다.

공통 절차는 [../dlc/references/protocol.md](../dlc/references/protocol.md), 상태 형식은 [../dlc/references/state-format.md](../dlc/references/state-format.md)에 있다. 스크립트 위치 `${CLAUDE_PLUGIN_ROOT}/skills/dlc/scripts/dlc.py`의 뜻은 protocol.md의 "스크립트 위치" 절을 따른다. 아래는 이 단계에서만 다른 것이다.

## 읽을 것

앞 단계가 없다. 대신 다음을 확인한다.

- `docs/dlc/active`와 `docs/dlc/<YYMMDD>-<slug>/` 폴더가 이미 있는지. 있으면 새 작업을 만들기 전에 사용자에게 "기존 작업 `<이름>`(설명: …)을 이어갈지, 새 작업을 만들지"를 묻는다. 이어가면 `dlc-init`을 끝내고 라우터 `dlc`를 안내한다.
- 호출 인자. 사용자가 `dlc-init express inventory-api 재고 조회 API` 처럼 붙였으면 그 값을 쓰고, 빠진 것만 묻는다.

## 순서

1. **프로파일 확인.** 인자에 없으면 채팅으로 묻는다. 선택지는 이름만 던지지 않고 아래 표의 "무엇이 달라지는가"를 함께 보인다. 사용자가 고르기 전에 임의로 정하지 않는다.
2. **slug와 설명 확인.** slug는 소문자·숫자·하이픈만(`inventory-api`). 설명은 한 문장이며 이것이 뒤 단계 산출물의 `[desc]` 출처가 된다. 사용자의 말을 고쳐 쓰지 않고 그대로 넣는다. 사용자가 slug를 안 정했으면 설명에서 후보를 하나 제안하고 확인받는다.
3. **실행.** 프로젝트 루트에서:

   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/skills/dlc/scripts/dlc.py init --profile <profile> --slug <slug> --description "<설명>"
   ```

   "이미 있습니다" 오류면 같은 날 같은 slug가 있다는 뜻이다. 다른 slug를 받거나 기존 작업을 이어간다.
4. **스캔 결과 설명.** 출력의 `workspace`·`languages`·`build`를 한 줄씩 풀어 전한다.
   - `brownfield`: 소스 파일이 발견됐다. 다음 단계는 `dlc-analyze`(코드베이스 분석)다. 단, `docs/dlc/codebase.md`가 이미 있고 지문이 같으면 자동으로 건너뛴다.
   - `greenfield`: 소스 파일이 없다. analyze는 `skipped`로 기록됐고 프로파일의 다음 단계로 간다.
   - 결과가 사용자 인식과 다르면(코드가 있는데 greenfield 등) 스캔 규칙을 알린다: 깊이 4까지만 보고, `docs`·`build`·`dist`·`out`·`target`·`node_modules`·`vendor`·`venv`·`coverage` 등과 점으로 시작하는 폴더는 제외한다(정확한 목록은 `dlc.py`의 `EXCLUDED_DIRS`). 스캔은 참고 정보라 잘못돼도 진행은 막지 않는다.
5. **다음 안내.** `python3 ${CLAUDE_PLUGIN_ROOT}/skills/dlc/scripts/dlc.py next`를 실행해 출력 첫 줄 `<stage> dlc-<stage>`의 스킬 이름을 이 에이전트의 호출 표기로 안내한다(예: "다음은 코드베이스 분석입니다. `/dlc:dlc-analyze`를 부르세요"). 다음 스킬을 대신 실행하지 않는다.

## 프로파일 설명 (사용자에게 보이는 문구)

| 프로파일 | 돌리는 단계 | 질문 수 | 이런 때 |
|---|---|---|---|
| `full` | 착수 전 검토(intent) → 팀 관행(practices) → 요구사항 → 설계 → 계획 → 구현 → 검증. 기존 코드가 있으면 분석이 먼저 | 단계당 5~8개 | 새 기능이나 새 프로젝트. 왜 만드는지부터 확인해야 할 때 |
| `express` | 요구사항 → 계획 → 구현 → 검증. 착수 전 검토·팀 관행·설계를 건너뛰고 계획 단계에서 유닛 표를 함께 만든다 | 단계당 2~4개 | 요구가 이미 명확한 작은 기능 |
| `bugfix` | express와 같은 단계. 요구사항 질문이 재현 조건·기대 동작·회귀 테스트 중심 | 단계당 2~4개 | 알려진 결함 수정 |

세 프로파일 모두 기존 코드가 있으면(brownfield) 분석(analyze)이 첫 단계로 끼어든다. `codebase.md`가 이미 있고 지문이 같으면 건너뛴다.

프로파일은 나중에 바꿀 수 없다. 바꾸려면 새 작업을 만든다.

## 산출물

`docs/dlc/<YYMMDD>-<slug>/state.md`와 `log.md`, 그리고 커서 `docs/dlc/active`. 모두 `dlc.py init`이 쓴다. 이 스킬이 직접 쓰는 파일은 없다. 스크립트가 없는 환경(폴백)에서는 state-format.md의 예시대로 `state.md`를 손으로 만들고 `active`에 폴더 이름을 적는다. 이때 fingerprint 행은 비워 둔다(analyze가 지문 검사를 못 하므로 사용자에게 알린다).

## 완료 기준

- `dlc.py init`이 0으로 끝나고 작업 폴더 경로를 출력했다.
- `dlc.py next`가 프로파일의 다음 스테이지를 가리킨다.
- 사용자가 프로파일·slug·설명을 직접 확정했다. 셋 중 하나라도 에이전트가 추측으로 채우지 않았다.

## 출력 언어

사용자 대면 출력은 한국어. 코드, 식별자, 경로, 명령은 원문 유지.
