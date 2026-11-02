# Visual style

Approved 2026-11-02: **monochrome + one accent**. The earlier muted teal on off-white was rejected as "애매한 색".

## Palette (tokens in `templates/docset/docset_lib.py`)

| Token | Light | Dark | Use |
|---|---|---|---|
| `--paper` / `--surface` | `#ffffff` | `#0f0f0f` / `#181818` | Page and cards. Pure white / near-black |
| `--ink` | `#141414` | `#f0f0f0` | Text, 완료 state, current tab |
| `--muted` | `#666666` | `#a3a3a3` | Secondary text, code names, captions |
| `--rule` / `--line` | `#e3e3e3` / `#9b9b9b` | `#2f2f2f` / `#6f6f6f` | Borders / diagram lines |
| `--well` | `#f4f4f4` | `#222222` | Gray fills (나중에 하는 것, 대기) |
| `--accent` | `#e8590c` | `#ff8a3d` | **The only color.** New parts, 지금 하는 단계, 정해야 할 일, links, step numbers, cardinality labels |
| `--accent-soft` | `#fff0e6` | `#3a2414` | Fill behind accent items |
| `--sun*`, `--sky*`, `--rose*` | gray steps | gray steps | Kept as names for compatibility; all map to grays |

Rules:
- Accent marks *what to look at*, never decoration. If more than a quarter of a screen is orange, remove some.
- 완료 is black (outline or black pill), not green. 지금 is orange.
- Never mention a color the palette no longer has in captions ("노란 상자"). Captions name what is drawn: "주황 상자", "회색 상자".
- Every color is a token with a dark value; check one page in dark mode before publishing.

## Typography

IBM Plex Sans KR (body, headings) and JetBrains Mono (code names), from Google Fonts with system fallbacks. `word-break: keep-all` so Korean never breaks mid-word.

## Components and when to use them

| Need | Use |
|---|---|
| 3–5 facts at a glance | `.cards` (k = question, v = short answer, d = one sentence) |
| Reasons, rules, remaining work | `ul.one` (bold lead phrase in accent + one sentence, or a pill + one sentence) |
| A vs B lists | `.two` |
| Progress | `.steps` with pills |
| Two yes/no conditions | `.grid4` |
| Items sharing columns | table; first column bold and non-wrapping |
| How parts connect / order / states | SVG in `figure`, claim sentence above, "how to read" caption below |

Layout: single column, max width 920 px, tab bar at top, footer at bottom. On phones, tables keep a 540 px minimum and scroll inside their box; SVGs keep 620 px and show the "옆으로 밀어서 보세요" hint. The page itself never scrolls sideways.
