#!/usr/bin/env bash
# 하위 세션에 지시를 보낸다. 본문은 표준 입력으로 받는다(따옴표 깨짐 방지).
# 사용: send.sh <이름> <<'EOF' ... EOF
# 보낸 뒤 10초 안에 working이 안 되면 Enter를 한 번만 더 누른다. 같은 지시를 다시 보내지 않는다.
set -euo pipefail

[ "${HERDR_ENV:-}" = 1 ] || { echo "herdr_env=0"; exit 1; }
name=${1:?이름}
text=$(cat)
[ -n "$text" ] || { echo "보낼 본문이 비었음"; exit 1; }

herdr agent prompt "$name" "$text" >/dev/null
for _ in 1 2 3 4 5; do
  st=$(herdr agent get "$name" | jq -r '.result.agent.agent_status')
  [ "$st" = working ] && { echo "sent=$name status=working at=$(date '+%H:%M:%S')"; exit 0; }
  /bin/sleep 2
done
herdr agent send-keys "$name" enter >/dev/null
/bin/sleep 3
st=$(herdr agent get "$name" | jq -r '.result.agent.agent_status')
echo "sent=$name status=$st at=$(date '+%H:%M:%S') (Enter 한 번 더 누름)"
[ "$st" = working ] || echo "아직 working 아님 — herdr pane read로 입력 줄을 확인할 것(다시 보내지 말 것)"
