#!/usr/bin/env bash
# Herdr 세션들의 컨텍스트 사용량을 잰다. 읽기만 한다.
# 사용: ctx.sh [이름 접두사]   예) ctx.sh proj-
# 값 = 세션 기록 jsonl의 마지막 응답 usage(input + cache_read + cache_creation) / 1,000,000.
# 1M 토큰 창 기준이다. 창 크기가 다른 모델은 토큰 수로 판단한다. codex 세션은 잴 수 없다.
set -euo pipefail

[ "${HERDR_ENV:-}" = 1 ] || { echo "herdr_env=0"; exit 1; }
prefix=${1:-}
herdr agent list | jq -r --arg p "$prefix" \
  '.result.agents[] | select((.name // "") | startswith($p)) | [(.name // "(이름없음)"), .pane_id, .agent_status, (.agent_session.value // "")] | @tsv' |
while IFS=$'\t' read -r name pane status sid; do
  f=""
  [ -n "$sid" ] && f=$(ls "$HOME"/.claude/projects/*/"$sid".jsonl 2>/dev/null | head -1 || true)
  if [ -z "$f" ]; then printf '%-20s %-8s %-8s 측정 불가(기록 없음)\n' "$name" "$pane" "$status"; continue; fi
  python3 - "$f" "$name" "$pane" "$status" <<'EOF'
import json, sys
f, name, pane, status = sys.argv[1:]
last = None
for line in open(f, errors="ignore"):
    try: d = json.loads(line)
    except Exception: continue
    m = d.get("message") or {}
    if d.get("type") == "assistant" and m.get("usage") and not d.get("isSidechain"):
        last = (m.get("model", "?"), m["usage"])
if not last:
    print(f"{name:20} {pane:8} {status:8} 측정 불가(응답 없음)"); sys.exit()
model, u = last
tok = u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
pct = tok / 1_000_000 * 100
flag = "  ← 70% 초과: 인계" if pct >= 70 else "  ← 60% 초과: 하위 세션이면 인계" if pct >= 60 else "  ← 50% 초과: 새 일은 새 세션" if pct >= 50 else ""
print(f"{name:20} {pane:8} {status:8} {pct:4.0f}% ({tok:,} 토큰, {model}){flag}")
EOF
done
