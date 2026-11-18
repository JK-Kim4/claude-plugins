#!/usr/bin/env bash
# 하위 세션을 새 탭에 띄우고 이름을 붙인다. 지시는 보내지 않는다(send.sh로 보낸다).
# 사용: spawn.sh <이름> <페르소나 또는 모델> [워크스페이스 ID] [cwd]
#   페르소나: implementer|investigator|operator|writer|debater|clerk|watcher → cc --agent herdr-flow:<페르소나>
#             reviewer → Codex, 모델 목록에서 가장 새로운 astra
#   모델 직접 지정(사용자가 모델을 고른 때만): claude|fable|sonnet|codex
#   워크스페이스를 비우면 이 세션($HERDR_PANE_ID)의 워크스페이스, cwd를 비우면 이 세션 패널의 cwd.
# Herdr 소켓은 샌드박스 안에서 막히므로 샌드박스 밖에서 실행한다.
set -euo pipefail

[ "${HERDR_ENV:-}" = 1 ] || { echo "herdr_env=0 (Herdr 패널 밖)"; exit 1; }
name=${1:?이름}; kind=${2:?페르소나 또는 모델}
ws=${3:-${HERDR_PANE_ID%%:*}}
here=$(cd "$(dirname "$0")" && pwd)

personas="implementer investigator operator writer debater clerk watcher"
case " $personas reviewer claude fable sonnet codex " in
  *" $kind "*) ;;
  *) echo "페르소나: $personas reviewer / 모델 직접 지정: claude fable sonnet codex"; exit 1 ;;
esac

# Codex는 고정 ID를 쓰지 않고 띄울 때마다 가장 새로운 astra를 고른다.
codex_model=""
if [ "$kind" = reviewer ] || [ "$kind" = codex ]; then
  codex_model=$("$here/latest-codex-model.sh" astra) || { echo "astra 모델을 찾지 못함 — ~/.codex/models_cache.json 확인"; exit 1; }
fi

[[ "$name" =~ ^[a-z][a-z0-9_-]{0,31}$ ]] || { echo "이름 형식 오류: [a-z][a-z0-9_-]{0,31}"; exit 1; }
if herdr agent list | jq -e --arg n "$name" '.result.agents[] | select(.name == $n)' >/dev/null; then
  echo "이미 있는 이름: $name (다음 번호나 b·c 접미사를 쓴다)"; exit 1
fi

cwd=${4:-$(herdr pane current --current | jq -r '.result.pane.foreground_cwd // .result.pane.cwd')}
res=$(herdr tab create --workspace "$ws" --cwd "$cwd" --label "$name")
pane=$(jq -r '.result.root_pane.pane_id' <<<"$res")
tab=$(jq -r '.result.tab.tab_id // .result.root_pane.tab_id // empty' <<<"$res")

case "$kind" in
  claude) herdr pane run "$pane" "cc" >/dev/null ;;
  fable)  herdr pane run "$pane" "cc --model claude-fable-5-2" >/dev/null ;;
  sonnet) herdr pane run "$pane" "cc --model sonnet" >/dev/null ;;
  reviewer|codex)
    herdr agent start "$name" --kind codex --pane "$pane" --timeout 60000 -- -m "$codex_model" --dangerously-bypass-approvals-and-sandbox >/dev/null ;;
  *) herdr pane run "$pane" "cc --agent herdr-flow:$kind" >/dev/null ;;
esac

# 에이전트가 잡힐 때까지(최대 60초) 기다린 뒤 이름을 붙인다.
for _ in $(seq 1 30); do herdr agent get "$pane" >/dev/null 2>&1 && break; /bin/sleep 2; done
case "$kind" in reviewer|codex) ;; *) herdr agent rename "$pane" "$name" >/dev/null ;; esac
if ! herdr agent wait "$name" --until idle --timeout 60000 >/dev/null 2>&1; then
  echo "idle 대기 실패 — 화면 확인(확인 화면에 임의로 답하지 않는다):"
  herdr pane read "$pane" --source visible --lines 30 | grep -v '^\s*$' | tail -12
  exit 2
fi
echo "name=$name pane=$pane tab=${tab:-미확인} kind=$kind${codex_model:+ model=$codex_model} ws=$ws"
