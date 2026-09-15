#!/bin/bash
# 플러그인 eval 실행기(dlc/evals/run.sh와 같은 Docker 심링크 우회). 사용: ./evals-run.sh <plugin-dir> [claude plugin eval 추가 인자...]
set -u
PLUGIN="$1"; shift
STASH="$(mktemp -d /tmp/plugin-eval-docker-stash.XXXXXX)"; MOVED=()
restore() { for d in "${MOVED[@]:-}"; do [ -n "$d" ] && mv "$STASH/$(basename "$d")" "$d"; done; rmdir "$STASH" 2>/dev/null; }
trap restore EXIT
for d in "$HOME/.docker/cli-plugins" "$HOME/.docker/bin/lib"; do
  if [ -d "$d" ] && [ -n "$(find "$d" -maxdepth 1 -type l | head -1)" ]; then mv "$d" "$STASH/"; MOVED+=("$d"); fi
done
claude plugin eval "$PLUGIN" --runs 1 --ablation none --scaffold --allow-tools Bash Write Edit --trust-plugin --no-publish --threshold 1.0 "$@"
