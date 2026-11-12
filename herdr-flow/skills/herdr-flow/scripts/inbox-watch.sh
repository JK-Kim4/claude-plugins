#!/usr/bin/env bash
# 하위 세션 보고 파일(INBOX.md)에 새 줄이 생길 때마다 한 줄씩 내보낸다.
# Monitor 도구로 한 번만 건다(10분짜리 until 루프를 다시 거는 방식은 쓰지 않는다).
# 사용: inbox-watch.sh <INBOX.md 절대 경로>
set -euo pipefail
f=${1:?INBOX 경로}
[ -f "$f" ] || { echo "없음: $f"; exit 1; }
# 보고 줄은 「- YYYY-MM-DD HH:MM KST [세션] …」 형식. 앞 600자만 내보내고 나머지는 파일에서 읽는다.
# cut은 파이프에서 버퍼링해 줄이 늦게 나오므로 awk로 줄마다 내보낸다.
tail -n 0 -F "$f" | awk '/^- /{ print substr($0, 1, 600); fflush() }'
