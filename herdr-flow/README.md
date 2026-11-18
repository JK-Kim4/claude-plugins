# herdr-flow

Herdr 터미널 멀티플렉서 위에서 여러 Claude Code 세션으로 일하는 방식을 스킬로 묶었다. 사람은 체크리스트로 진척을 보고 승인할 때만 개입하고, 오케스트레이터 세션이 목표·분석·설계·계획과 지시·대조를 맡고, 구현·조사·배포는 하위 세션이 한다. 하위 세션과 서브에이전트는 일 종류마다 정해 둔 **페르소나**(모델)로 띄운다.

```
/plugin marketplace add JK-Kim4/claude-plugins
/plugin install herdr-flow@jongwan-plugins
```

전제: Herdr 패널 안(`HERDR_ENV=1`), `jq`, `python3`, macOS 기준 `date -j`. yolo 기동은 `cc` alias(`claude --dangerously-skip-permissions`)를 쓴다. herdr 명령은 Claude Code 샌드박스 안에서 소켓이 막히므로 샌드박스 밖에서 실행한다. 페르소나 세션(`cc --agent herdr-flow:<페르소나>`)은 이 플러그인이 설치돼 있어야 뜬다. 외부 리뷰(Codex)는 `codex` CLI와 `~/.codex/models_cache.json`이 있어야 한다.

## 흐름

```
herdr-flow(진입점) → herdr-flow-plan(계획) ─┬→ herdr-flow-debate(설계 토론, 필요할 때)
                                          └→ herdr-flow-brief(지시) → herdr-flow-verify(대조)
                                                     ↑                     │
                                                     └── herdr-flow-gate(실행 승인) ←┘
                                          … 단계가 모두 끝나면 → herdr-flow-close(마무리)
컨텍스트가 차면 언제든 herdr-handoff(인계)
```

## 스킬

| 스킬 | 하는 일 | 언제 |
|---|---|---|
| `herdr-flow` | 진입점. 작업 폴더를 찾거나 양식으로 만들고, 인계 문서·계획·결정·INBOX·체크리스트·하위 세션 상태로 현황을 한 화면에 보고, 다음 한 걸음과 쓸 스킬을 제안 | "작업 이어서", "어디까지 했지", "herdr-flow로 시작" |
| `herdr-flow-plan` | 전제를 원천에서 확인 → 한 질문씩 인터뷰 → `plan.md`(범위·단계·검증) 채우기, 묶음마다 페르소나·검증 위치·승인 단계, 결정은 사용자 원문으로 `decisions.md`, 계획 승인 | "계획 세워줘", "단계 나눠줘" |
| `herdr-flow-brief` | 지시서 작성(고정 절 + 합의 대조 + 새 의존 점검) → 페르소나로 새 탭 세션 기동 → 첫 지시 → 체크리스트 `start` | "하위 세션 만들어서 맡겨", "지시서 써서" |
| `herdr-flow-verify` | INBOX 감시를 한 번 걸고, 새 보고 줄을 분류해 결과 파일과 원천으로 직접 대조 → 오케스트레이터가 체크리스트 `done`·`block` → 확인 범위를 붙여 보고 | 보고 알림, "결과 대조해", "어디까지 됐어" |
| `herdr-flow-gate` | 되돌리기 어려운 일 앞에서 준비 결과 대조 → 승인 질문 하나(무엇·범위·되돌리기·영향) → 지목한 승인 원문 기록 → 지시서 수정 → 「실행」 한 줄 전달 | 「준비 끝」 보고, "머지해", "배포해" |
| `herdr-flow-debate` | 토론 지시서 → 설계 토론 상대(Fable) 독립 1라운드 → 교차 라운드 → 합의안·직접 확인 → 사용자 결정 → 문서 담당이 정본 반영 → Codex 외부 리뷰 → 지적을 직접 대조해 받아들일 것만 반영 | "둘이 논의해서 제일 좋은 설계", "codex 리뷰" |
| `herdr-flow-close` | 미완료 단계 계산·완료 기준 재확인 → 하위 세션·감시 정리 → `plan.md` 「끝」·인계 문서 마지막 상태 → 범위 밖 발견 보고 | "마무리하자", "세션 정리" |
| `herdr-handoff` | 인계 문서(사용자 지적 원문 절·하위 세션 표 포함)를 쓰고 새 탭에 yolo 세션을 띄워 요약 대조 후 넘김. 오케스트레이터면 하위 세션에 새 이름 알림 | `/herdr-flow:herdr-handoff`로 직접 호출 |

## 페르소나 — 일 종류마다 정해 둔 모델

`agents/`의 정의 하나를 두 곳에서 쓴다. 새 탭 세션은 `scripts/spawn.sh <이름> <페르소나>`(= `cc --agent herdr-flow:<페르소나>`), 오케스트레이터 안의 서브에이전트는 Agent 도구 `subagent_type: "herdr-flow:<페르소나>"`. 추론 강도는 정의에 적지 않아 사용자 설정을 따른다.

| 일 종류 | 페르소나 | 모델 |
|---|---|---|
| 구현(코드 수정·테스트·PR) | `implementer` | Opus |
| 조사·대조(읽기 전용) | `investigator` | Opus |
| 배포·운영 실행 | `operator` | Opus |
| 문서 작성·수정 | `writer` | Opus (Fable은 사용자가 지정할 때만) |
| 설계 토론 상대 | `debater` | Fable |
| 기계적 작업(재생성·재게시, 대기, 행 수 대조) | `clerk` | Sonnet |
| 운영 감시 회차 | `watcher` | Sonnet |
| 외부 리뷰 | `reviewer` | Codex, 띄울 때마다 가장 새로운 astra(`scripts/latest-codex-model.sh`) |

입력 대부분이 캐시 읽기인 Claude Code 세션에서는 같은 토큰 양이면 Fable이 Opus의 약 1.5배, Sonnet이 약 0.5배다(API 단가 기준). 토큰을 많이 쓰는 문서 작업을 Opus에 두는 이유다. 사용자가 모델을 지정하면 `spawn.sh <이름> <claude|fable|sonnet|codex>`로 그대로 띄운다.

## 공용 묶음 `skills/herdr-flow/`

진입점 `SKILL.md`와 함께 다른 스킬이 쓰는 규칙·양식·스크립트를 담는다.

| 파일 | 내용 |
|---|---|
| `shared/rules.md` | 역할, 세션(새 탭·yolo·이름·페르소나), 컨텍스트 기준(새 일 50%·하위 60%·오케스트레이터 70%), INBOX 보고, 체크리스트 기록(오케스트레이터만), 직접 대조, 결정·승인(한 메시지에 하나), 지시서, 말투 |
| `shared/folder-layout.md` | 작업 폴더 구성(plan·decisions·HANDOFF·briefs·results·reports/INBOX·notes·design·checklist·design-review, 백업은 docs 밖) |
| `shared/templates/` | `plan.md`(의도·범위·단계(페르소나 칸)·검증), `decisions.md`(쌓기만 함), `HANDOFF.md`(상태 한 장) |
| `scripts/spawn.sh` | 새 탭 + 페르소나·모델별 기동 + 이름 붙이기 + 준비 대기 |
| `scripts/latest-codex-model.sh` | Codex 모델 목록에서 계열(astra 등)의 가장 높은 버전 고르기 |
| `scripts/send.sh` | 지시 전송, working 확인, 안 먹으면 Enter 한 번 |
| `scripts/ctx.sh` | 세션별 컨텍스트 %(세션 기록 jsonl 마지막 usage / 1M) |
| `scripts/inbox-watch.sh` | INBOX 새 보고 줄만 내보내기(Monitor용) |
| `scripts/wake-at.sh` | 정해진 KST 시각에 깨우기(백그라운드 Bash용) |
| `scripts/close.sh` | 작업 트리 확인 후 하위 세션 탭 닫기 |

## 설계에서 지킨 것

**보고는 파일 한 줄로만 받는다.** 하위 세션이 herdr로 오케스트레이터에게 직접 보고하면 사용자가 그 탭에 치는 입력과 섞인다. 하위 세션은 `reports/INBOX.md`에 단계 시작·끝·막힘마다 한 줄을 덧붙이고, 오케스트레이터는 감시를 한 번 걸어 받는다.

**체크리스트는 오케스트레이터만 쓴다.** 하위 세션이 쓰게 하면 없는 단계 ID, 막힘 뒤 빠진 완료, 늦은 시작이 섞여 「끝」 보고 때 단계가 남는다. 오케스트레이터가 지시 때 `start`, 대조한 턴에 `done`, 「끝」 전에 단계별 마지막 상태를 계산한다.

**하위 세션 보고는 주장이다.** 오케스트레이터 일의 대부분은 지시가 아니라 대조다. 양쪽(이전·이후, 부르는 쪽·받는 쪽), 실행 구조, 연결이 살아 있는지, 배포된 값, 운영 데이터까지 같은 폭으로 본다.

**승인은 하나씩, 원문으로.** 승인 질문 옆에 대기 항목을 늘어놓으면 사용자는 승인한 줄 안다. 지시서는 준비와 실행을 나눠, 실행 승인이 한 줄 전달로 끝나게 한다.

**모델은 일 종류로 고른다.** 판단이 거의 없는 대기·대조·재게시에 비싼 모델을 붙잡아 두지 않고, 토큰을 많이 쓰는 일에 가장 비싼 모델을 기본으로 두지 않는다.

**약속한 후속은 같은 턴에 예약한다.** 「끝나면 대조하겠다」고 말만 하면 아무도 깨우지 않는다.

**컨텍스트가 차기 전에 넘긴다.** 찬 세션은 지시를 놓친다. 인계 문서 1절에 사용자가 지적한 말을 원문으로 쌓아 다음 세션이 같은 실수를 하지 않게 한다.
