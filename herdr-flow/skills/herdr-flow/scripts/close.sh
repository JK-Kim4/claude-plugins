#!/usr/bin/env bash
# 일을 마친 하위 세션의 탭을 닫는다. 넘긴 저장소(작업 트리)에 커밋 안 된 변경이나 push 안 된 커밋이 있으면 닫지 않는다.
# 사용: close.sh <이름> [작업 트리 경로 ...]
set -euo pipefail

[ "${HERDR_ENV:-}" = 1 ] || { echo "herdr_env=0"; exit 1; }
name=${1:?이름}; shift || true

info=$(herdr agent get "$name")
tab=$(jq -r '.result.agent.tab_id' <<<"$info")
status=$(jq -r '.result.agent.agent_status' <<<"$info")
[ "$tab" = "${HERDR_TAB_ID:-}" ] && { echo "자기 탭은 닫지 않는다"; exit 1; }
[ "$status" = working ] && { echo "$name 작업 중(working) — 닫지 않음"; exit 1; }

dirty=0
for repo in "$@"; do
  s=$(git -C "$repo" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
  up=$(git -C "$repo" rev-list --count '@{u}..HEAD' 2>/dev/null || echo "upstream 없음")
  echo "$repo: 변경 $s줄, push 안 된 커밋 $up"
  { [ "$s" != 0 ] || [ "$up" != 0 ]; } && dirty=1
done
[ "$dirty" = 0 ] || { echo "정리 안 된 작업 트리가 있어 닫지 않음 — 확인 후 다시"; exit 1; }

herdr tab close "$tab" >/dev/null
echo "closed=$name tab=$tab"
