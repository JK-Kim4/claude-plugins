---
name: dlc
description: 개발 생명주기(착수 전 검토 → 요구사항 → 설계 → 계획 → 구현 → 검증) 스킬셋의 라우터. 현재 작업의 상태를 보이고 다음에 부를 dlc-* 스킬을 안내하거나, "전부 진행"이면 남은 단계를 순서대로 승인 게이트를 두고 진행한다.
disable-model-invocation: true
metadata:
  author: JK-Kim4
  version: "0.1.0"
---

# dlc — 생명주기 라우터

`dlc-*` 스테이지 스킬 아홉 개의 입구다. 사용자가 이름을 쳐서 부를 때만 실행된다.

공통 절차는 [references/protocol.md](references/protocol.md), 상태·산출물 형식은 [references/state-format.md](references/state-format.md), 출처 규칙은 [references/grounding.md](references/grounding.md)에 있다. 스크립트는 `<skills>/dlc/scripts/dlc.py`이며 항상 프로젝트 루트에서 `python3 <skills>/dlc/scripts/dlc.py <명령>`으로 실행한다. `<skills>`는 이 스킬이 로드될 때 보인 스킬 디렉터리(`dlc/`)의 부모다. Claude Code 플러그인이면 `<plugin>/skills`, `npx skills add`로 설치했으면 `.agents/skills`.

## 스테이지와 스킬

| 순서 | 스테이지 | 스킬 | 하는 일 |
|---|---|---|---|
| 1 | init | dlc-init | 작업 폴더 생성, 저장소 스캔, 프로파일 선택 |
| 2 | analyze | dlc-analyze | 기존 코드베이스 분석 (기존 코드가 있을 때만) |
| 3 | intent | dlc-intent | 왜 만드는가, 누구를 위한 것인가, 성공 지표, 범위, 타당성 |
| 4 | practices | dlc-practices | 브랜치·테스트·배포·코드 스타일 관행 확정 |
| 5 | requirements | dlc-requirements | 6차원 빈 곳 질문, FR/NFR ID 요구사항서 |
| 6 | design | dlc-design | 컴포넌트 경계, 엔티티 소유권, ADR, 유닛 분해, 계약 |
| 7 | plan | dlc-plan | 유닛 순서, seam, 테스트 예산, 완료 정의 |
| 8 | build | dlc-build | 유닛별 구현, 요구사항→파일 추적 |
| 9 | verify | dlc-verify | 전체 테스트, 추적성 검사, 리뷰 발견, 판정 |

프로파일이 어느 스테이지를 돌리는지는 state-format.md에 있다.

## 호출

- `/dlc:dlc` (Claude Code), `$dlc` (Codex), `/dlc` (Gemini CLI). 인자 없이 부르면 **안내 모드**.
- 인자에 `--all` 또는 "전부 진행"이 있으면 **전체 진행 모드**.
- 인자에 `status`가 있으면 안내 모드에서 다음 스킬 안내 문장만 생략한다.

## 안내 모드

1. `dlc.py status`를 실행한다. 오류가 나오면 메시지를 그대로 보인다. 메시지가 작업 폴더 목록을 나열하면(커서만 없는 경우, 다른 PC에서 클론했을 때 흔하다) "다른 작업으로 바꾸기" 절로 간다. 작업 폴더가 하나도 없다고 하면 "아직 작업이 없습니다. `dlc-init`을 먼저 부르세요"라고 전하고 끝낸다.
2. 출력을 그대로 보인 뒤, "다음:" 줄의 스킬 이름을 이 에이전트의 호출 표기로 바꿔 한 줄로 안내한다. 예: "다음은 요구사항 분석입니다. `/dlc:dlc-requirements`를 부르세요." 인자가 `status`였으면 이 안내 문장은 생략한다.
3. 끝낸다. 다음 스킬을 대신 실행하지 않는다.

## 전체 진행 모드

1. `dlc.py next`를 실행한다. `done`이면 완료를 알리고 끝낸다. "활성 작업이 없습니다"라고 하면 `../dlc-init/SKILL.md`를 읽고 그 절차부터 수행한다(인자에 프로파일·slug·설명이 있으면 그것을 쓰고, 없는 것만 묻는다). 작업 폴더 목록이 나열되면 "다른 작업으로 바꾸기" 절로 간다.
2. 출력된 스테이지의 스킬 파일 `../dlc-<stage>/SKILL.md`를 읽고 그 절차를 이 세션에서 그대로 수행한다. 그 파일이 없으면 그렇게 알리고 `dlc.py status`를 보인 뒤 끝낸다. 절차를 지어내 진행하지 않는다. protocol.md의 승인 게이트는 그대로 유효하다. 스테이지마다 멈춰 승인을 받는다. build처럼 질문 파일이 없는 스테이지도 승인 게이트는 있다.
3. 승인이 기록되면 1로 돌아간다. 사용자가 "여기까지"라고 하면 멈추고 `dlc.py status`를 보인다.
4. 한 스테이지에서 받은 "알아서 진행해"는 그 스테이지에만 적용한다. 다음 스테이지는 다시 묻는다.

## 다른 작업으로 바꾸기

사용자가 다른 작업을 이어가고 싶어 하거나 커서만 없을 때, `docs/dlc/` 아래 작업 폴더 목록을 보이고 고르게 한 뒤, 고른 이름을 `docs/dlc/active`에 한 줄로 쓴다. 이것이 `active` 파일을 직접 쓰는 유일한 경우다. 하나뿐이면 그 이름을 확인만 받고 쓴다.

## 출력 언어

사용자 대면 출력과 산출물은 한국어로 쓴다. 코드, 식별자, 경로, 명령은 원문 유지.
