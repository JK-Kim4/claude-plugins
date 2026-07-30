#!/usr/bin/env python3
"""위키 조회 — 후보를 층별로 묶고 날짜를 붙여 좁힌다. 무엇을 믿을지는 LLM 이 판정한다.

    python3 recall.py <질의> [질의...]           # 어느 디렉터리에서 실행해도 된다
    python3 recall.py <질의> --root ~/other      # 위키를 직접 지정
    python3 recall.py <질의> --limit 40          # 층당 상한 (기본 12)
    python3 recall.py <질의> --json out.json     # 판정용 원자료
    python3 recall.py <질의> --lines             # 매치 줄까지

**위키 루트는 설정에서 얻는다** — `~/.config/llm-wiki/config.json` 의 `root`.
조회는 프로젝트 저장소 한가운데서 "전에 어떻게 했더라"로 불리는 일이 대부분이라,
매번 위키 경로를 알고 있어야 하면 쓰이지 않는다. 경로를 본문에 박지 않는 것과
경로를 찾을 줄 아는 것은 다른 문제다.

질의를 여러 개 주면 **전부 포함한 문서를 먼저** 올린다. 하나도 못 찾으면 알린다.

왜 grep 을 그대로 쓰지 않나 — 세 가지가 grep 으로 안 된다.

1. **원료를 훑는다.** `raw/` 는 가공 전 원본이라 인용 대상이 아닌데, 실측에서
   자격증명 패턴이 걸리는 파일이 368개였다. 여기서는 항상 제외한다.
2. **언제 기준 사실인지 안 보인다.** 문서의 절반 가까이가 날짜를 안 갖고 있고
   (실측: `projects/` 는 27% 만 보유, `sessions/`·`retrospectives/` 는 99~100%),
   날짜 없이 읽은 서술은 지금도 참인지 알 수 없다.
3. **층이 섞인다.** 같은 주제가 세션·회고·프로젝트 문서에 흩어져 있고 셋의 성격이
   다르다. 한 덩어리로 쏟아내면 무엇을 믿을지 가릴 수 없다.
"""
import os, re, sys, json, collections

HERE = os.path.dirname(os.path.abspath(__file__))
BOOTSTRAP = os.path.normpath(os.path.join(HERE, "..", "..", "wiki-bootstrap", "scripts"))
if "--bootstrap" in sys.argv:
    BOOTSTRAP = os.path.expanduser(sys.argv[sys.argv.index("--bootstrap") + 1])
sys.path.insert(0, BOOTSTRAP)
try:
    from survey import walk_md, SKIP_DIRS
except ImportError:
    sys.exit(f"wiki-bootstrap 스크립트를 찾지 못했다: {BOOTSTRAP}\n"
             f"형제 디렉터리로 설치돼 있어야 한다. 아니면 --bootstrap <경로> 로 지정한다.")

# raw/ 는 가공 전 원본이다. 인용 대상이 아니고 자격증명이 남아 있을 수 있다.
NEVER = ("raw", "node_modules")

FM_DATE = re.compile(r"^date:\s*['\"]?(\d{4}-\d{2}-\d{2})", re.M)
FM_TITLE = re.compile(r"^title:\s*['\"]?(.+?)['\"]?\s*$", re.M)
FM_TYPE = re.compile(r"^type:\s*(\S+)", re.M)
FM_PROJECT = re.compile(r"^project:\s*(\S+)", re.M)
NAME_DATE = re.compile(r"^(\d{4}-\d{2}-\d{2})")
H1 = re.compile(r"^#\s+(.+)$", re.M)

# 층마다 성격이 다르다. 이 설명은 판정용이지 순위가 아니다 — 순위는 질문에 달렸다.
LAYER_NOTE = {
    "retrospectives": "평가·교훈의 정본",
    "sessions": "그 시점의 사실 기록 — 날짜와 함께 읽는다",
    "projects": "현재 상태 — 날짜 없는 문서가 많다",
    "knowledge": "확정 지식",
    "sources": "외부 원문 (불변)",
}


def meta(path, rel, head):
    """문서의 신원 — 언제 기준이고 어느 층인지."""
    m = FM_DATE.search(head)
    date = m.group(1) if m else None
    if not date:
        m = NAME_DATE.match(os.path.basename(rel))
        date = m.group(1) if m else None
    t = FM_TITLE.search(head)
    if t:
        title = t.group(1).strip()
    else:
        h = H1.search(head)
        title = h.group(1).strip() if h else os.path.basename(rel)[:-3]
    return {"file": rel, "layer": rel.split("/")[0] if "/" in rel else "(루트)",
            "date": date, "title": title[:90],
            "type": (FM_TYPE.search(head).group(1) if FM_TYPE.search(head) else None),
            "project": (FM_PROJECT.search(head).group(1) if FM_PROJECT.search(head) else None)}


def search(root, terms, want_lines=False):
    lowered = [t.lower() for t in terms]
    hits = []
    for path in walk_md(root):
        rel = os.path.relpath(path, root)
        if rel.split("/")[0] in NEVER:
            continue
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                text = f.read()
        except OSError:
            continue
        low = text.lower()
        counts = [low.count(t) for t in lowered]
        if not any(counts):
            continue
        d = meta(path, rel, text[:900])
        d["matched"] = sum(1 for c in counts if c)
        d["hits"] = sum(counts)
        if want_lines:
            out = []
            for line in text.splitlines():
                ll = line.lower()
                if any(t in ll for t in lowered):
                    out.append(re.sub(r"\s+", " ", line).strip()[:200])
                if len(out) >= 3:
                    break
            d["lines"] = out
        hits.append(d)
    # 질의어를 많이 포함한 순 → 매치 밀도 순 → 최신 순(날짜 없으면 뒤).
    #
    # **날짜를 관련도보다 앞세우지 않는다.** 날짜는 "이 서술을 지금도 믿을 수 있나"를
    # 가리는 정보지 "어느 문서가 답인가"를 고르는 기준이 아니다. 최신 순으로 세우면
    # 질의어를 스치듯 한 번 언급한 최근 문서가 27번 다룬 정본 위로 올라간다.
    hits.sort(key=lambda h: (-h["matched"], -h["hits"],
                             h["date"] is None, _neg(h["date"] or "")))
    return hits


def _neg(date):
    """최신이 먼저 오도록 날짜를 뒤집는다 (문자열 정렬용)."""
    return "".join(chr(ord("9") - int(c)) if c.isdigit() else c for c in date)


def group(hits):
    by = collections.OrderedDict()
    for h in hits:
        by.setdefault(h["layer"], []).append(h)
    return by


def report(root, terms, hits, limit, want_lines):
    print(f"{os.path.basename(root)} — {' + '.join(terms)} → 문서 {len(hits)}건 (raw/ 제외)")
    if not hits:
        print("\n걸린 문서가 없다. 질의어를 줄이거나 다른 표현을 쓴다 —\n"
              "위키는 한국어 서사라 영어 용어로는 안 걸릴 수 있다.")
        return
    if len(terms) > 1:
        full = sum(1 for h in hits if h["matched"] == len(terms))
        print(f"  질의어 전부 포함: {full}건 / 일부만: {len(hits) - full}건")
    for layer, items in group(hits).items():
        note = LAYER_NOTE.get(layer, "")
        undated = sum(1 for h in items if not h["date"])
        tail = f" · 날짜 없음 {undated}건" if undated else ""
        print(f"\n[{layer}] {len(items)}건{' — ' + note if note else ''}{tail}")
        for h in items[:limit]:
            d = h["date"] or "  날짜없음  "
            print(f"  {d}  ×{h['hits']:<3} {h['title']}")
            print(f"              {h['file']}")
            for line in h.get("lines", []):
                print(f"                · {line}")
        if len(items) > limit:
            print(f"  … 외 {len(items) - limit}건 (--limit 로 늘린다)")


CONFIG = os.path.expanduser("~/.config/llm-wiki/config.json")


def configured_root():
    """설정에 기록된 위키 루트. wiki-bootstrap 이 구축 마지막 단계에서 남긴다."""
    try:
        with open(CONFIG, encoding="utf-8") as f:
            return json.load(f).get("root")
    except (OSError, ValueError):
        return None


def main():
    argv, args, opts = sys.argv[1:], [], {}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--json", "--limit", "--bootstrap", "--root"):
            opts[a] = argv[i + 1] if i + 1 < len(argv) else None
            i += 2
        elif a.startswith("--"):
            opts[a] = True
            i += 1
        else:
            args.append(a)
            i += 1
    if not args:
        print(__doc__)
        sys.exit(1)

    root = opts.get("--root") or configured_root()
    if not root:
        sys.exit(f"위키 루트를 모른다. {CONFIG} 에 root 가 없고 --root 도 안 줬다.\n"
                 f"wiki-bootstrap 으로 구축했다면 거기서 기록됐어야 한다.")
    root = os.path.abspath(os.path.expanduser(root))
    if not os.path.isdir(root):
        sys.exit(f"위키 루트가 없다: {root}")
    terms = args
    limit = int(opts.get("--limit") or 12)
    want_lines = bool(opts.get("--lines"))

    hits = search(root, terms, want_lines)
    report(root, terms, hits, limit, want_lines)

    if opts.get("--json"):
        with open(opts["--json"], "w", encoding="utf-8") as f:
            json.dump({"terms": terms, "hits": hits}, f, ensure_ascii=False, indent=1)
        print(f"\n저장: {opts['--json']}")


if __name__ == "__main__":
    main()
