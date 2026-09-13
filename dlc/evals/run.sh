#!/bin/bash
# dlc eval suite 실행기.
#
# `claude plugin eval` 은 Bash 를 허용하는 케이스에서 ~/.docker 안에 심볼릭 링크가 있으면 샌드박스가 실행을 거부한다
# ("the Docker credential store … holds a symbolic link inside it"). Docker Desktop 이 만드는 `cli-plugins/` 와
# `bin/lib/` 가 그 링크다. DOCKER_CONFIG 를 바꿔도 우회되지 않는다(R4 확인). 이 스크립트는 두 디렉터리를 실행 동안
# /tmp 로 옮기고, 정상 종료·오류·SIGTERM 어느 경우에도 trap 으로 되돌린다. 실행 중에는 `docker compose` 같은 CLI
# 플러그인 서브커맨드가 잠시 동작하지 않는다.
#
# 사용: dlc/evals/run.sh [claude plugin eval 추가 인자...]
#   예: dlc/evals/run.sh                       # 8 케이스 전부, runs 1, ablation 없음
#       dlc/evals/run.sh --case router-*       # 라우터 케이스만
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN="$(dirname "$HERE")"
STASH="$(mktemp -d /tmp/dlc-eval-docker-stash.XXXXXX)"
MOVED=()
restore() {
  for d in "${MOVED[@]}"; do mv "$STASH/$(basename "$d")" "$d"; done
  rmdir "$STASH" 2>/dev/null
}
trap restore EXIT
for d in "$HOME/.docker/cli-plugins" "$HOME/.docker/bin/lib"; do
  if [ -d "$d" ] && [ -n "$(find "$d" -maxdepth 1 -type l | head -1)" ]; then mv "$d" "$STASH/"; MOVED+=("$d"); fi
done
echo "docker symlink dirs moved: ${#MOVED[@]}"
claude plugin eval "$PLUGIN" --runs 1 --ablation none --scaffold --allow-tools Bash Write Edit --trust-plugin --no-publish --threshold 1.0 "$@"
