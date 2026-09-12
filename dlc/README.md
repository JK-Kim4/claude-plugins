# dlc

AI-DLC(awslabs/aidlc-workflows) 방법론을 **에이전트 종속 없이** 쓰는 명시 호출형 생명주기 스킬셋. Claude Code, Codex CLI, Gemini CLI에서 같은 `SKILL.md`가 동작한다.

설계 기록: `docs/design/2026-09-13-dlc-plugin-design.md`

## 구성

| 스킬 | 역할 | 산출물 |
|---|---|---|
| `dlc` | 라우터. 상태를 보이고 다음 스킬을 안내하거나 `--all`로 전체 진행 | — |
| `dlc-init` | 작업 폴더 생성, 저장소 스캔, 프로파일 선택 | `state.md` |
| `dlc-analyze` | 기존 코드베이스 분석 (brownfield일 때만) | `docs/dlc/codebase.md` |
| `dlc-intent` | 착수 전 검토: 문제, 대상, 성공 지표, 범위, 타당성 | `intent.md` |
| `dlc-practices` | 팀 관행 확정: 작업 방식, 테스트, 배포, 코드 스타일 | `docs/dlc/practices.md` |
| `dlc-requirements` | 6차원 질문, FR/NFR ID 요구사항서 | `requirements.md` |
| `dlc-design` | 컴포넌트 경계, 엔티티 소유권, ADR, 유닛 분해, 계약 | `design.md`, `decisions.md`, `units.md` |
| `dlc-plan` | 유닛 순서, seam, 테스트 예산, 완료 정의 | `plan.md` |
| `dlc-build` | 유닛별 구현, 요구사항→파일 추적 | 코드, `build/<unit>.md` |
| `dlc-verify` | 전체 테스트, 추적성 검사, 리뷰 발견, 판정 | `verify.md` |

스테이지 스킬은 2·3라운드에서 추가된다. 현재 저장소에는 라우터 `dlc`와 공유 스파인만 있다.

프로파일: `full`(9단계 전부, 질문 5~8개), `express`(init·analyze·requirements·plan·build·verify, 질문 2~4개), `bugfix`(express와 같은 단계, 결함 재현·회귀 중심).

## 동작 원리

- 산출물과 진행 상태는 프로젝트 저장소의 `docs/dlc/<YYMMDD>-<slug>/`에 남는다. 커밋 대상이라 세션·에이전트·PC가 바뀌어도 이어간다.
- `dlc/scripts/dlc.py`(python3 표준 라이브러리만)가 상태 전이, 다음 단계 판정, 산출물 필수 절·ID 검사를 맡는다. 에이전트는 `state.md`를 손으로 고치지 않는다.
- 질문은 A~E + `X. Other` 선택지와 `[Answer]:` 태그가 있는 파일로 주고받는다. 특정 도구의 질문 UI에 의존하지 않는다.
- 스테이지마다 승인 게이트가 있다. 침묵은 승인이 아니다.

## 설치

### Claude Code

```
/plugin marketplace add JK-Kim4/claude-plugins
/plugin install dlc@jongwan-plugins
```

호출: `/dlc:dlc`, `/dlc:dlc-requirements` 등. 모든 스킬이 `disable-model-invocation: true`라 이름을 쳐야만 실행된다.

### Codex CLI, Gemini CLI, Cursor

```
npx skills add JK-Kim4/claude-plugins --skill dlc
```

`--skill`은 정확한 스킬 이름만 받는다(와일드카드 불가). 스테이지 스킬이 추가되는 2·3라운드부터는 `--skill dlc --skill dlc-init ...`처럼 이름을 전부 나열한다. 스킬이 `.agents/skills/<name>/`에 형제 디렉터리로 복사된다. 스테이지 스킬은 `../dlc/scripts/dlc.py`로 라우터 스킬의 스크립트를 찾으므로 **`dlc` 라우터는 항상 함께 설치**한다.

호출: Codex `$dlc-requirements`, Gemini CLI `/dlc-requirements`. Codex는 각 스킬의 `agents/openai.yaml`이 자동 발동을 막는다. Gemini CLI는 그 설정이 없어 description을 사람용 한 줄로만 둔다.

## 요구 환경

python3 3.9 이상. 외부 패키지 없음.

## 검증

```bash
python3 -m unittest discover -s dlc/skills/dlc/tests
claude plugin validate ./dlc
```
