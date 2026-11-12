# 작업 폴더 구조

여러 날 이어진 오케스트레이션 작업에서 굳어진 구조다.

## 위치

- 사용자 메모리·`CLAUDE.md`에 작업 폴더 위치 규칙이 있으면 그것을 따른다.
- 없으면 오케스트레이터 cwd 아래 `docs/_work/<YYMMDD>-<slug>/`. 처음 한 번 사용자에게 위치를 확인한다.
- git 저장소 작업 트리(커밋 대상) 안에는 만들지 않는다. 코드 작업은 저장소별 별도 `git worktree`로.

## 구성

| 경로 | 쓰는 쪽 | 내용 |
|---|---|---|
| `HANDOFF.md` | 오케스트레이터 | 인계 문서 겸 현재 상태 진입점. 인계마다 다시 쓴다(틀은 `herdr-handoff`) |
| `notes/<YYYY-MM-DD>-orchN-인계-orchM.md` | 오케스트레이터 | 지난 인계 문서. 새로 쓰기 전에 옮긴다 |
| `briefs/<단계 ID>-<짧은 이름>.md` | 오케스트레이터 | 지시서 한 장 = 하위 세션 한 일. 공통 규칙은 `briefs/<묶음>-공통-규칙.md` |
| `results/<단계 ID>.md` (+ `.diff`) | 하위 세션 | 결과 파일 |
| `reports/INBOX.md` | 하위 세션(덧붙이기만) | 보고 한 줄씩. 첫 줄 `# INBOX` |
| `backups/<YYMMDD>-<일>/` | 하위 세션 | 바꾸기 전 원본(설정 JSON, 대상 목록) |
| `checklist/` | `work-checklist` 스킬 | `checklist.json`, `checklist.html`, 게시 URL |
| `design-review/` | 설계 토론 | `BRIEF*.md`, `orch-rN.md`, `<상대>-rN.md`, `consensus.md`, `codex-review.md`, `INBOX.md` |

## 새로 만들 때

```bash
D=<작업 폴더>; mkdir -p "$D"/{briefs,results,reports,notes,backups}; [ -f "$D/reports/INBOX.md" ] || printf '# INBOX\n\n' > "$D/reports/INBOX.md"
```
