#!/usr/bin/env bash
# 하위 세션을 새 탭에 띄우고 이름을 붙인다. 지시는 보내지 않는다(send.sh로 보낸다).
# 사용: spawn.sh <이름> <모델: claude|fable|sonnet|codex> [워크스페이스 ID] [cwd]
#   워크스페이스를 비우면 이 세션($HERDR_PANE_ID)의 워크스페이스, cwd를 비우면 이 세션 패널의 cwd.
# Herdr 소켓은 샌드박스 안에서 막히므로 샌드박스 밖에서 실행한다.
set -euo pipefail

[ "${HERDR_ENV:-}" = 1 ] || { echo "herdr_env=0 (Herdr 패널 밖)"; exit 1; }
name=${1:?이름}; model=${2:?모델}
ws=${3:-${HERDR_PANE_ID%%:*}}
cwd=${4:-$(herdr pane current --current | jq -r '.result.pane.foreground_cwd // .result.pane.cwd')}

[[ "$name" =~ ^[a-z][a-z0-9_-]{0,31}$ ]] || { echo "이름 형식 오류: [a-z][a-z0-9_-]{0,31}"; exit 1; }
if herdr agent list | jq -e --arg n "$name" '.result.agents[] | select(.name == $n)' >/dev/null; then
  echo "이미 있는 이름: $name (다음 번호나 b·c 접미사를 쓴다)"; exit 1
fi

res=$(herdr tab create --workspace "$ws" --cwd "$cwd" --label "$name")
pane=$(jq -r '.result.root_pane.pane_id' <<<"$res")
tab=$(jq -r '.result.tab.tab_id // .result.root_pane.tab_id // empty' <<<"$res")

case "$model" in
  claude) herdr pane run "$pane" "cc" >/dev/null ;;
  fable)  herdr pane run "$pane" "cc --model claude-fable-5-2" >/dev/null ;;
  sonnet) herdr pane run "$pane" "cc --model sonnet" >/dev/null ;;
  codex)  herdr agent start "$name" --kind codex --pane "$pane" --timeout 60000 -- --dangerously-bypass-approvals-and-sandbox >/dev/null ;;
  *) echo "모델은 claude|fable|sonnet|codex"; exit 1 ;;
esac

# 에이전트가 잡힐 때까지(최대 60초) 기다린 뒤 이름을 붙인다.
for _ in $(seq 1 30); do herdr agent get "$pane" >/dev/null 2>&1 && break; /bin/sleep 2; done
[ "$model" = codex ] || herdr agent rename "$pane" "$name" >/dev/null
if ! herdr agent wait "$name" --until idle --timeout 60000 >/dev/null 2>&1; then
  echo "idle 대기 실패 — 화면 확인(확인 화면에 임의로 답하지 않는다):"
  herdr pane read "$pane" --source visible --lines 30 | grep -v '^\s*$' | tail -12
  exit 2
fi
echo "name=$name pane=$pane tab=${tab:-미확인} model=$model ws=$ws"
