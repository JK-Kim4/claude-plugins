# agent-workflow

에이전트가 **무엇을 만드느냐**가 아니라 **어떻게 일하느냐**를 다루는 스킬 묶음.

| 스킬 | 역할 |
|---|---|
| `worktree` | 최신 `origin/develop` 기준으로 격리 Git worktree 를 만들고 이후 작업 경로를 거기로 고정한다. |

`worktree` 는 **사용자가 명시적으로 호출했을 때만** 동작한다 — 일반적인 코드 변경
요청만으로 자동으로 워크트리를 만들지 않는다. 격리는 유용하지만 사용자가 예상하지
못한 경로 이동은 혼란을 만든다.

`token-efficiency` 스킬(도구 출력 토큰 절약 규율)은 0.2.0에서 제거했다. 스킬은 모델이
고를 때만 로드돼 "모든 작업에 적용"을 보장하지 못하므로, 같은 내용을 사용자 글로벌 룰
(`~/.claude/rules/shared/token-efficiency.md`)로 옮겼다. 이전 본문은 `archive/token-efficiency/`.
