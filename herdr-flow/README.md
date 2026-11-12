# herdr-flow

Herdr 터미널 멀티플렉서 위에서 여러 Claude Code 세션으로 일하는 방식을 스킬로 묶었다. 사람은 체크리스트로 진척을 보고 승인할 때만 개입하고, 오케스트레이터 세션이 목표·분석·설계·계획과 지시·대조를 맡고, 구현·조사·배포는 하위 세션이 한다.

```
/plugin marketplace add JK-Kim4/claude-plugins
/plugin install herdr-flow@jongwan-plugins
```

전제: Herdr 패널 안(`HERDR_ENV=1`), `jq`, `python3`, macOS 기준 `date -j`. yolo 기동은 `cc` alias(`claude --dangerously-skip-permissions`)를 쓴다. herdr 명령은 Claude Code 샌드박스 안에서 소켓이 막히므로 샌드박스 밖에서 실행한다.

## 구성

| 스킬 | 하는 일 | 언제 |
|---|---|---|
| `herdr-flow-brief` | 지시서 작성(고정 절 + 합의 대조 + 새 의존 점검) → 컨텍스트 확인 → 새 탭에 세션 기동(claude·fable·sonnet·codex) → 첫 지시 → 체크리스트 기록 | "하위 세션 만들어서 맡겨", "지시서 써서" |
| `herdr-flow-verify` | INBOX 감시를 한 번 걸고, 새 보고 줄을 분류해 결과 파일과 원천(코드·git·클라우드·k8s·읽기 전용 DB·로그)으로 직접 대조 → 체크리스트 기록 → 확인 범위를 붙여 사용자에게 보고 | 보고 알림이 왔을 때, "결과 대조해", "어디까지 됐어" |
| `herdr-handoff` | 인계 문서(사용자 지적 원문 절·하위 세션 표 포함)를 쓰고 새 탭에 yolo 세션을 띄워 요약 대조 후 넘김. 오케스트레이터면 하위 세션에 새 이름 알림 | `/herdr-flow:herdr-handoff`로 직접 호출 |

공용 묶음 `skills/herdr-flow/`(SKILL.md 없음):

| 파일 | 내용 |
|---|---|
| `shared/rules.md` | 역할, 세션(새 탭·yolo·이름), 컨텍스트 기준(새 일 50%·하위 60%·오케스트레이터 70%), INBOX 보고, 체크리스트 기록, 직접 대조, 결정·승인(한 메시지에 하나), 지시서, 말투 |
| `shared/folder-layout.md` | 작업 폴더 구성(HANDOFF·briefs·results·reports/INBOX·notes·backups·checklist·design-review) |
| `scripts/spawn.sh` | 새 탭 + 모델별 기동 + 이름 붙이기 + 준비 대기 |
| `scripts/send.sh` | 지시 전송, working 확인, 안 먹으면 Enter 한 번 |
| `scripts/ctx.sh` | 세션별 컨텍스트 %(세션 기록 jsonl 마지막 usage / 1M) |
| `scripts/inbox-watch.sh` | INBOX 새 보고 줄만 내보내기(Monitor용) |
| `scripts/wake-at.sh` | 정해진 KST 시각에 깨우기(백그라운드 Bash용) |
| `scripts/close.sh` | 작업 트리 확인 후 하위 세션 탭 닫기 |

## 설계에서 지킨 것

**보고는 파일 한 줄로만 받는다.** 하위 세션이 herdr로 오케스트레이터에게 직접 보고하면 사용자가 그 탭에 치는 입력과 섞인다. 하위 세션은 `reports/INBOX.md`에 한 줄을 덧붙이고, 오케스트레이터는 감시를 한 번 걸어 받는다. 화면 끝을 grep하거나 idle을 폴링하면 보고를 놓친다.

**하위 세션 보고는 주장이다.** 오케스트레이터 일의 대부분은 지시가 아니라 대조다. 보고가 인용한 줄 하나를 열어 보는 것은 대조가 아니고, 양쪽(이전·이후, 부르는 쪽·받는 쪽), 실행 구조, 연결이 살아 있는지, 배포된 값, 운영 데이터까지 같은 폭으로 본다.

**승인은 하나씩, 원문으로.** 승인 질문 옆에 대기 항목을 늘어놓으면 사용자는 승인한 줄 안다. 지시서는 준비(읽기·백업·PR 생성)와 실행(운영 쓰기·머지)을 나눠, 실행 승인이 한 줄 전달로 끝나게 한다.

**컨텍스트가 차기 전에 넘긴다.** 찬 세션은 지시를 놓친다. 인계 문서 1절에 사용자가 지적한 말을 원문으로 쌓아 다음 세션이 같은 실수를 하지 않게 한다.

## 남은 것

진입점(현황 보고·폴더 생성), 계획(인터뷰·묶음 계획·결정 기록), 승인 게이트, 설계 토론(다른 모델과 라운드 토론 → 외부 리뷰), 마무리 스킬은 다음 버전에서.
