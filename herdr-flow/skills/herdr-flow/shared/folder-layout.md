# 작업 폴더 구조

여러 날 이어진 오케스트레이션 작업에서 굳어진 구조다.

## 위치

- 사용자 메모리·`CLAUDE.md`에 작업 폴더 위치 규칙이 있으면 그것을 따른다.
- 없으면 오케스트레이터 cwd 아래 `docs/work/<YYMMDD>-<티켓>-<주제>/`. 티켓이 없으면 `docs/work/<YYMMDD>-<주제>/`. 처음 한 번 사용자에게 위치를 확인한다.
- **작업 단위는 티켓이 있으면 티켓, 없으면 주제 하나다.** 같은 티켓의 단계(stage0, stage1 …)는 폴더를 따로 만들지 않고 그 폴더 안의 하위 폴더나 `plan.md`의 단계 표로 둔다. 만들기 전에 같은 티켓·주제 폴더가 이미 있는지 `ls docs/work`로 본다.
- 백업은 용량·시크릿 때문에 `docs` 밖 `backups/<같은 작업 폴더 이름>/`에 둔다.
- git 저장소 작업 트리(커밋 대상) 안에는 만들지 않는다. 코드 작업은 저장소별 별도 `git worktree`로.

## 구성

| 경로 | 쓰는 쪽 | 내용 |
|---|---|---|
| `plan.md` | 오케스트레이터(사용자와 대화로) | **필수.** 무엇을 어디까지: 의도·완료 기준, 배경·제약, 범위(다루지 않을 것 포함), 단계, 검증 방법. 지금 참인 것만 쓴다. 틀: `templates/plan.md` |
| `decisions.md` | 오케스트레이터 | **필수.** 왜 그렇게 했나: 결정 한 건 = 문제·옵션·선택·근거·사용자 원문, 출처·영향 태그. 쌓기만 하고 번호를 다시 매기지 않는다. 틀: `templates/decisions.md` |
| `HANDOFF.md` | 오케스트레이터 | 인계 문서 겸 현재 상태 진입점. 인계마다 다시 쓴다(틀은 `herdr-handoff`). 계획·결정은 복사하지 않고 `plan.md`·`decisions.md`를 가리킨다. 시작용 뼈대: `templates/HANDOFF.md` |
| `notes/<YYYY-MM-DD>-orchN-인계-orchM.md` | 오케스트레이터 | 지난 인계 문서. 새로 쓰기 전에 옮긴다 |
| `briefs/<단계 ID>-<짧은 이름>.md` | 오케스트레이터 | 지시서 한 장 = 하위 세션 한 일. 공통 규칙은 `briefs/<묶음>-공통-규칙.md` |
| `results/<단계 ID>.md` (+ `.diff`) | 하위 세션 | 결과 파일 |
| `reports/INBOX.md` | 하위 세션(덧붙이기만) | 보고 한 줄씩. 첫 줄 `# INBOX` |
| `reports/<YYMMDD>-<주제>.<ext>` | 오케스트레이터 | 사람과 HTML로 소통한 문서 아카이브(요구사항 명확화·설계 논의·결과 공유). `INBOX.md`와 같은 폴더에 두고 이름으로 구분한다. 거기서 나온 결정은 `decisions.md` 근거 칸에 링크한다 |
| `design/` | 설계 단계 | 설계 과정 산출물(intake·clarify·design·confirm·log 등). 설계가 확정되면 결론은 `plan.md`·`decisions.md`로 올리고 `plan.md`의 「관련 문서」에서 링크한다 |
| `backups/<작업 폴더 이름>/<YYMMDD>-<일>/` (`docs` 밖) | 하위 세션 | 바꾸기 전 원본(설정 JSON, 대상 목록) |
| `checklist/` | `work-checklist` 스킬 | `checklist.json`, `checklist.html`, 게시 URL |
| `design-review/` | 설계 토론(`herdr-flow-debate`) | `BRIEF.md`(토론 지시서), `orch-rN.md`·`<상대>-rN.md`(라운드), `consensus.md`(합의), `BRIEF-edit*.md`·`edit-report*.md`(정본 반영), `BRIEF-codex*.md`·`codex-review*.md`(외부 리뷰), `INBOX.md`(토론 세션 보고) |

## 새로 만들 때

```bash
D=<작업 폴더>; T=<skills>/herdr-flow/shared/templates
mkdir -p "$D"/{briefs,results,reports,notes}
[ -f "$D/reports/INBOX.md" ] || printf '# INBOX\n\n' > "$D/reports/INBOX.md"
for f in plan.md decisions.md; do [ -f "$D/$f" ] || cp "$T/$f" "$D/$f"; done
```

- 백업 폴더는 `backups/<작업 폴더 이름>/`을 처음 백업할 때 `docs` 밖에 만든다. 작업 폴더 안에 `backups/`를 만들지 않는다.
- `HANDOFF.md`는 처음 인계할 때 `herdr-handoff`가 만든다. 미리 만들지 않는다.
- 만든 직후 `plan.md`를 사용자와 대화로 채운다. 갈림길은 선택지를 골라 가며 정하고, 정한 결정은 `decisions.md`에 D-1부터 쌓는다. 채우기 전에 지시서(`briefs/`)를 쓰지 않는다.
