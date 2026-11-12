#!/usr/bin/env bash
# 핸드오프에 필요한 Herdr 상태를 한 번에 모은다. 읽기만 하고 아무것도 바꾸지 않는다.
# Claude Code 샌드박스 안에서는 Herdr 소켓이 막혀 "Operation not permitted"가 난다.
# 그때는 이 스크립트를 샌드박스 밖에서 다시 실행한다.
set -euo pipefail

if [ "${HERDR_ENV:-}" != 1 ]; then
  echo "herdr_env=0 (Herdr 패널 밖이라 핸드오프를 진행하지 않는다)"
  exit 1
fi

current=$(herdr pane current --current)
layout=$(herdr pane layout --pane "$HERDR_PANE_ID")
agents=$(herdr agent list)

session_id=$(jq -r '.result.pane.agent_session.value // empty' <<<"$current")
width=$(jq -r --arg p "$HERDR_PANE_ID" '.result.layout.panes[] | select(.pane_id == $p) | .rect.width' <<<"$layout")
height=$(jq -r --arg p "$HERDR_PANE_ID" '.result.layout.panes[] | select(.pane_id == $p) | .rect.height' <<<"$layout")
pane_count=$(jq -r '.result.layout.panes | length' <<<"$layout")

# 반으로 나눠도 Claude Code가 80칸 이상을 쓰도록 160칸을 기준으로 삼는다.
if [ "${width:-0}" -ge 160 ]; then direction=right; else direction=down; fi

transcript=""
if [ -n "$session_id" ]; then
  transcript=$(ls "$HOME"/.claude/projects/*/"$session_id".jsonl 2>/dev/null | head -1 || true)
fi

echo "pane_id=$HERDR_PANE_ID"
echo "tab_id=$HERDR_TAB_ID"
echo "cwd=$(jq -r '.result.pane.foreground_cwd // .result.pane.cwd' <<<"$current")"
echo "pane_size=${width}x${height} (탭 안 패널 ${pane_count}개)"
echo "split_direction=$direction"
echo "current_agent_name=$(jq -r --arg p "$HERDR_PANE_ID" '.result.agents[] | select(.pane_id == $p) | .name // "(없음)"' <<<"$agents")"
echo "taken_names=$(jq -r '[.result.agents[].name // empty] | join(",")' <<<"$agents")"
echo "session_id=${session_id:-(못 찾음)}"
echo "transcript=${transcript:-(못 찾음)}"
echo "now=$(date '+%Y-%m-%d %H:%M')"
