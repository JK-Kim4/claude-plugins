"""설계 문서 묶음(개요·기능 정의·도메인 정의·ERD·핵심 흐름) 공통 부품.

사용법: 프로젝트별 build.py에서
    import docset_lib as L
    L.configure(docs=[...], titles={...}, footer="...", urls_path=sys.argv[1] if len(sys.argv)>1 else None)
    L.page(key, body) / L.fig(...) / L.seq(...) / L.entity(...) / L.marker(...)
를 쓰고 HTML 파일을 쓴다. 예시는 examples/soseolbi-bookshelf-docset/build.py.
"""
import json, sys, os, html

DOCS = [("overview", "개요"), ("features", "기능 정의"), ("domain", "도메인 정의"), ("erd", "ERD"), ("sequence", "핵심 흐름")]
TITLES = {}
URLS = {}
FOOTER = ""


def configure(docs=None, titles=None, footer="", urls_path=None):
    """문서 목록·제목·바닥글을 정한다. urls_path는 게시 뒤 받은 주소 JSON({key: url})."""
    global DOCS, TITLES, FOOTER, URLS
    if docs:
        DOCS = docs
    TITLES = titles or {}
    FOOTER = footer
    URLS = json.load(open(urls_path, encoding="utf-8")) if urls_path else {}

CSS = r"""
:root{
  --paper:#ffffff;--surface:#ffffff;--ink:#141414;--muted:#666666;--rule:#e3e3e3;--line:#9b9b9b;
  --well:#f4f4f4;--accent:#e8590c;--accent-soft:#fff0e6;--sun:#3d3d3d;--sun-soft:#e7e7e7;
  --sky:#3d3d3d;--sky-soft:#f1f1f1;--rose:#141414;--rose-soft:#e3e3e3;
  --f-body:"IBM Plex Sans KR","Apple SD Gothic Neo","Malgun Gothic",system-ui,sans-serif;
  --f-mono:"JetBrains Mono",ui-monospace,Menlo,monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --paper:#0f0f0f;--surface:#181818;--ink:#f0f0f0;--muted:#a3a3a3;--rule:#2f2f2f;--line:#6f6f6f;
  --well:#222222;--accent:#ff8a3d;--accent-soft:#3a2414;--sun:#d0d0d0;--sun-soft:#2e2e2e;
  --sky:#d0d0d0;--sky-soft:#262626;--rose:#f0f0f0;--rose-soft:#333333;color-scheme:dark}}
:root[data-theme="dark"]{
  --paper:#0f0f0f;--surface:#181818;--ink:#f0f0f0;--muted:#a3a3a3;--rule:#2f2f2f;--line:#6f6f6f;
  --well:#222222;--accent:#ff8a3d;--accent-soft:#3a2414;--sun:#d0d0d0;--sun-soft:#2e2e2e;
  --sky:#d0d0d0;--sky-soft:#262626;--rose:#f0f0f0;--rose-soft:#333333;color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--paper);color:var(--ink);font:16px/1.7 var(--f-body);word-break:keep-all;overflow-wrap:break-word;
  padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
.page{max-width:920px;margin:0 auto;padding-block:20px 96px}
nav.docs{display:flex;flex-wrap:wrap;gap:6px;padding-bottom:14px;border-bottom:1px solid var(--rule);margin-bottom:28px}
nav.docs a,nav.docs span{font-size:14px;padding:5px 12px;border-radius:999px;text-decoration:none;color:var(--muted);border:1px solid var(--rule);background:var(--surface)}
nav.docs span{color:var(--paper);background:var(--ink);border-color:var(--ink);font-weight:600}
nav.docs a:hover{color:var(--accent);border-color:var(--accent)}
.eyebrow{font-size:13px;color:var(--muted);margin:0}
h1{font-size:1.9rem;line-height:1.3;margin:4px 0 10px;text-wrap:balance}
.lead{font-size:1.12rem;margin:0 0 6px}
.basis{font-size:13px;color:var(--muted);margin:0 0 8px}
h2{font-size:1.3rem;margin:48px 0 12px;padding-bottom:6px;border-bottom:1px solid var(--rule);text-wrap:balance}
h3{font-size:1.05rem;margin:28px 0 8px}
p{margin:8px 0}
a{color:var(--accent);text-underline-offset:2px}
a:focus-visible,summary:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:3px}
code{font-family:var(--f-mono);font-size:.84em;background:var(--well);padding:.05em .35em;border-radius:4px;white-space:nowrap}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin:14px 0}
.card{background:var(--surface);border:1px solid var(--rule);border-radius:10px;padding:14px 16px}
.card .k{font-size:12.5px;color:var(--muted);font-weight:600;letter-spacing:.03em}
.card .v{font-size:1.02rem;font-weight:600;margin-top:4px}
.card .d{font-size:14px;color:var(--muted);margin-top:4px}
ul.one{list-style:none;padding:0;margin:12px 0;display:grid;gap:8px}
ul.one li{background:var(--surface);border:1px solid var(--rule);border-radius:8px;padding:10px 14px}
ul.one li b{color:var(--accent)}
.two{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.box-yes,.box-no{border-radius:10px;padding:12px 16px}
.box-yes{background:var(--accent-soft)}.box-no{background:var(--well)}
.box-yes h3,.box-no h3{margin:0 0 6px;font-size:1rem}
.box-yes ul,.box-no ul{margin:0;padding-left:1.1em}
.table-wrap{overflow-x:auto;margin:12px 0}
table{border-collapse:collapse;width:100%;font-size:15px;line-height:1.55}
th,td{border:1px solid var(--rule);padding:8px 10px;text-align:left;vertical-align:top}
th{background:var(--well);font-weight:600;white-space:nowrap}
td.n{white-space:nowrap;color:var(--muted);font-variant-numeric:tabular-nums}
td.name{white-space:nowrap;font-weight:600}
td .ex{display:block;font-size:13px;color:var(--muted);margin-top:2px}
.pill{display:inline-block;font-size:12px;font-weight:600;padding:1px 9px;border-radius:999px;white-space:nowrap}
.pill.g{background:var(--accent-soft);color:var(--accent)}
.pill.y{background:var(--sun-soft);color:var(--sun)}
.pill.b{background:var(--sky-soft);color:var(--sky)}
.pill.r{background:var(--rose-soft);color:var(--rose)}
.pill.m{background:var(--well);color:var(--muted)}
.pill.k{background:var(--ink);color:var(--paper)}
figure{margin:16px 0;padding:14px;background:var(--surface);border:1px solid var(--rule);border-radius:10px}
.svg-wrap{overflow-x:auto}
figure svg{display:block;width:100%;height:auto}
figcaption{font-size:14px;color:var(--muted);margin-top:8px}
.swipe{display:none;font-size:12.5px;color:var(--muted);margin:0 0 6px}
svg text{font-family:var(--f-body)}
svg .box{fill:var(--surface);stroke:var(--line);stroke-width:1.3}
svg .box.g{fill:var(--accent-soft);stroke:var(--accent)}
svg .box.y{fill:var(--sun-soft);stroke:var(--sun)}
svg .box.b{fill:var(--sky-soft);stroke:var(--sky)}
svg .box.r{fill:var(--rose-soft);stroke:var(--rose)}
svg .box.m{fill:var(--well);stroke:var(--line);stroke-dasharray:5 4}
svg .zone{fill:none;stroke:var(--rule);stroke-width:1.2;stroke-dasharray:6 5}
svg .t{fill:var(--ink);font-size:14px;font-weight:600}
svg .s{fill:var(--muted);font-size:12px}
svg .lbl{fill:var(--ink);font-size:12.5px}
svg .lbl.m{fill:var(--muted)}
svg .zt{fill:var(--muted);font-size:12px;font-weight:600}
svg .card-n{fill:var(--accent);font-size:12px;font-weight:700}
svg .edge{stroke:var(--line);stroke-width:1.5;fill:none}
svg .edge.dash{stroke-dasharray:5 4}
svg .life{stroke:var(--rule);stroke-width:1.5;stroke-dasharray:4 4}
svg .head{fill:var(--line)}
svg .row{fill:var(--ink);font-size:12.5px}
svg .rowc{fill:var(--muted);font-size:11px;font-family:var(--f-mono)}
svg .hdr{fill:var(--accent-soft);stroke:none}
svg .hdr.b{fill:var(--sky-soft)}
svg .hdr.y{fill:var(--sun-soft)}
svg .hdr.m{fill:var(--well)}
svg .sep{stroke:var(--sun);stroke-width:1.2;stroke-dasharray:3 4}
svg .sept{fill:var(--sun);font-size:12px;font-weight:600}
svg .num{fill:var(--accent)}
svg .numt{fill:var(--paper);font-size:11px;font-weight:700}
svg .card1{fill:var(--accent);font-size:11.5px;font-weight:700}
.steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;margin:14px 0}
.step{border-radius:10px;padding:10px 12px;background:var(--surface);border:1px solid var(--rule)}
.step .no{font-size:12px;color:var(--muted);font-weight:600}
.step .nm{font-weight:600;margin-top:2px}
.step .st{margin-top:6px}
.step.done{background:var(--well);border-color:var(--ink)}
.step.now{background:var(--accent-soft);border-color:var(--accent)}
.legend{display:flex;flex-wrap:wrap;gap:10px 18px;font-size:13.5px;color:var(--muted);margin:6px 0 2px}
.legend i{display:inline-block;width:14px;height:14px;border-radius:4px;vertical-align:-2px;margin-right:5px}
details{margin:8px 0}
summary{cursor:pointer;color:var(--accent);font-weight:500;font-size:14.5px}
details .body{margin-top:6px;padding:10px 14px;background:var(--well);border-radius:8px;font-size:14.5px}
.words{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:8px;margin:12px 0}
.word{background:var(--surface);border:1px solid var(--rule);border-radius:8px;padding:10px 14px;font-size:14.5px}
.word b{display:block;font-size:15px}
.grid4{display:grid;grid-template-columns:auto 1fr 1fr;gap:6px;margin:12px 0;font-size:14.5px}
.grid4 div{padding:10px 12px;border-radius:8px;background:var(--surface);border:1px solid var(--rule)}
.grid4 .h{background:var(--well);font-weight:600;border-color:transparent}
.grid4 .ok{background:var(--accent-soft);border-color:var(--accent);font-weight:600}
.grid4 .no{color:var(--muted)}
.foot{margin-top:56px;padding-top:12px;border-top:1px solid var(--rule);font-size:13px;color:var(--muted)}
@media (max-width:700px){
  h1{font-size:1.6rem}
  .two{grid-template-columns:1fr}
  .swipe{display:block}
  figure svg.wide{min-width:620px}
  .table-wrap table{min-width:540px}
}
@media (prefers-reduced-motion:no-preference){html{scroll-behavior:smooth}}
"""

HEAD = """<title>{title}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap">
<style>{css}</style>
"""


def nav(cur):
    out = ['<nav class="docs" aria-label="문서 목록">']
    for key, name in DOCS:
        if key == cur:
            out.append(f"<span>{name}</span>")
        elif key in URLS:
            out.append(f'<a href="{URLS[key]}">{name}</a>')
        else:
            out.append(f'<a href="#" aria-disabled="true">{name}</a>')
    out.append("</nav>")
    return "".join(out)


def page(key, body):
    return (HEAD.format(title=TITLES[key], css=CSS)
            + '<div class="page">' + nav(key) + body
            + f'<p class="foot">{FOOTER}</p></div>')


def marker(mid):
    return (f'<defs><marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path class="head" d="M0,0 L10,5 L0,10 z"/></marker></defs>')


def esc(s):
    return html.escape(s, quote=False)


def tw(s, size=12.5):
    """대략적인 글자 폭(px)."""
    w = 0
    for ch in s:
        w += size * (1.0 if ord(ch) > 0x2E80 else 0.58)
    return w


# ---------------------------------------------------------------- 순서 그림
def seq(mid, parts, steps, aria, col=168):
    n = len(parts)
    left = 86
    W = left * 2 + (n - 1) * col
    xs = {k: left + i * col for i, (k, _, _) in enumerate(parts)}
    out = []
    y = 92
    num = 0
    body = []
    for st in steps:
        kind = st[0]
        if kind in ("call", "reply"):
            _, a, b, label = st
            num += 1
            xa, xb = xs[a], xs[b]
            d = 1 if xb > xa else -1
            x1, x2 = xa + 4 * d, xb - 4 * d
            cls = "edge" if kind == "call" else "edge dash"
            body.append(f'<path class="{cls}" d="M{x1} {y} H{x2}" marker-end="url(#{mid})"/>')
            mx = (xa + xb) / 2
            text = f"{label}"
            need = tw(text) + 34
            if need > abs(xb - xa) - 6:
                print(f"[warn] {mid}: label too wide '{label}' {need:.0f}>{abs(xb-xa)}", file=sys.stderr)
            body.append(f'<circle class="num" cx="{mx - tw(text)/2 - 12:.1f}" cy="{y-13}" r="8.5"/>'
                        f'<text class="numt" x="{mx - tw(text)/2 - 12:.1f}" y="{y-9}" text-anchor="middle">{num}</text>')
            lc = "lbl" if kind == "call" else "lbl m"
            body.append(f'<text class="{lc}" x="{mx + 0:.1f}" y="{y-8}" text-anchor="middle">{esc(text)}</text>')
            y += 50
        elif kind == "note":
            _, a, b, text = st
            xa, xb = sorted([xs[a], xs[b]])
            w = max(xb - xa + 120, tw(text, 12.5) + 28)
            cx = (xa + xb) / 2
            body.append(f'<rect class="box y" x="{cx - w/2:.1f}" y="{y-22}" width="{w:.1f}" height="30" rx="6"/>'
                        f'<text class="lbl" x="{cx:.1f}" y="{y-2}" text-anchor="middle">{esc(text)}</text>')
            y += 46
        elif kind == "sep":
            _, text = st
            body.append(f'<path class="sep" d="M10 {y-10} H{W-10}"/>'
                        f'<rect x="{W/2 - tw(text,12)/2 - 10:.1f}" y="{y-22}" width="{tw(text,12)+20:.1f}" height="22" rx="11" style="fill:var(--surface)"/>'
                        f'<text class="sept" x="{W/2}" y="{y-6}" text-anchor="middle">{esc(text)}</text>')
            y += 40
    H = y + 6
    out.append(f'<svg class="wide" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(aria)}">{marker(mid)}')
    for k, name, sub in parts:
        x = xs[k]
        out.append(f'<path class="life" d="M{x} 58 V{H-4}"/>')
    for k, name, sub in parts:
        x = xs[k]
        bw = max(140, tw(name, 14) + 24)
        out.append(f'<rect class="box {"g" if k in ("api","worker") else ""}" x="{x-bw/2:.1f}" y="8" width="{bw:.1f}" height="50" rx="8"/>'
                   f'<text class="t" x="{x}" y="30" text-anchor="middle">{esc(name)}</text>'
                   f'<text class="s" x="{x}" y="48" text-anchor="middle">{esc(sub)}</text>')
    out.extend(body)
    out.append("</svg>")
    return "".join(out)


def fig(svg, caption, swipe=True):
    sw = '<p class="swipe">그림을 옆으로 밀어서 보세요 →</p>' if swipe else ""
    return f'<figure>{sw}<div class="svg-wrap">{svg}</div><figcaption>{caption}</figcaption></figure>'


# ---------------------------------------------------------------- ERD 그림
def entity(x, y, w, title, code, rows, tone=""):
    h = 44 + 22 * len(rows) + 8
    o = [f'<rect class="box" x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/>',
         f'<path class="hdr {tone}" d="M{x+1} {y+8} a7 7 0 0 1 7 -7 H{x+w-8} a7 7 0 0 1 7 7 V{y+40} H{x+1} Z"/>',
         f'<text class="t" x="{x+12}" y="{y+20}">{esc(title)}</text>',
         f'<text class="rowc" x="{x+12}" y="{y+35}">{esc(code)}</text>']
    for i, (key, label, c) in enumerate(rows):
        ry = y + 44 + 22 * i + 15
        prefix = {"pk": "🔑 ", "fk": "🔗 ", "": ""}[key]
        o.append(f'<text class="row" x="{x+12}" y="{ry}">{prefix}{esc(label)}</text>')
        o.append(f'<text class="rowc" x="{x+w-10}" y="{ry}" text-anchor="end">{esc(c)}</text>')
    return "".join(o), h


def card_lbl(x, y, t, anchor="middle"):
    return f'<text class="card1" x="{x}" y="{y}" text-anchor="{anchor}">{t}</text>'

