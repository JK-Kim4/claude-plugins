#!/bin/bash
# eval 러너의 cwd 에 픽스처를 만든다. 형식은 dlc.py 가 쓰는 state.md/log.md 와 같다.
set -e
rm -rf docs
W=docs/dlc/260913-inventory-lookup
mkdir -p "$W"
printf '260913-inventory-lookup\n' > docs/dlc/active
cat > "$W/state.md" <<'EOF'
# DLC State

<!-- dlc.py 가 관리한다. 손으로 고치지 말고 start/approve/skip 을 쓴다. -->

- profile: express
- depth: minimal
- description: 창고 관리자가 SKU 로 현재 재고 수량을 조회하는 사내 API
- created: 2026-09-13T02:10:00Z
- workspace: greenfield
- languages: -
- build: -
- fingerprint: da39a3ee5e6b

## Stages

| stage | status | updated | note |
|---|---|---|---|
| init | done | 2026-09-13T02:10:00Z |  |
| analyze | skipped | 2026-09-13T02:10:00Z | greenfield |
| requirements | pending | 2026-09-13T02:10:00Z |  |
| plan | pending | 2026-09-13T02:10:00Z |  |
| build | pending | 2026-09-13T02:10:00Z |  |
| verify | pending | 2026-09-13T02:10:00Z |  |
EOF
cat > "$W/log.md" <<'EOF'
# DLC Log

- 2026-09-13T02:10:00Z | init | created | profile=express workspace=greenfield
EOF
