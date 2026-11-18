#!/usr/bin/env bash
# Codex 모델 목록(~/.codex/models_cache.json)에서 이름이 gpt-<버전>-<계열>인 것 중 버전이 가장 높은 것을 출력한다.
# 사용: latest-codex-model.sh [계열=astra]   예) latest-codex-model.sh astra → gpt-6.2-astra
# 읽기만 한다. 목록에 없으면 1로 끝난다(다른 계열로 대신 고르지 않는다).
set -euo pipefail
family=${1:-astra}
cache=${CODEX_MODELS_CACHE:-$HOME/.codex/models_cache.json}
[ -f "$cache" ] || { echo "없음: $cache" >&2; exit 1; }
python3 -I - "$cache" "$family" <<'EOF'
import json, re, sys
path, family = sys.argv[1], sys.argv[2]
d = json.load(open(path))
models = d.get("models", d) if isinstance(d, dict) else d
pat = re.compile(r"^gpt-(\d+(?:\.\d+)*)-" + re.escape(family) + r"$")
found = []
for m in models:
    slug = (m.get("slug") or m.get("id") or "") if isinstance(m, dict) else str(m)
    hit = pat.match(slug)
    if hit:
        found.append((tuple(int(x) for x in hit.group(1).split(".")), slug))
if not found:
    sys.exit(1)
print(max(found)[1])
EOF
