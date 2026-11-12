#!/usr/bin/env bash
# 정해진 KST 시각까지 기다렸다가 한 줄을 출력하고 끝난다. Bash run_in_background로 걸어 오케스트레이터를 깨운다.
# 사용: wake-at.sh <YYYY-MM-DD HH:MM> <깨울 때 할 일 한 줄>
set -euo pipefail
at=${1:?시각}; msg=${2:?할 일}
t=$(TZ=Asia/Seoul date -j -f '%Y-%m-%d %H:%M' "$at" +%s)
now=$(date +%s)
[ "$t" -gt "$now" ] || { echo "이미 지난 시각: $at"; exit 1; }
while [ "$(date +%s)" -lt "$t" ]; do /bin/sleep 30; done
echo "$(TZ=Asia/Seoul date '+%m/%d %H:%M') KST — $msg"
