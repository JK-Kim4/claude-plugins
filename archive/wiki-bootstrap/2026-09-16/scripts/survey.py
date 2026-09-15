#!/usr/bin/env python3
"""마크다운 저장소 재고 조사.

이관 전에 원본들에 대해, 이관 후에 대상에 대해 돌린다.
깨진 링크 수가 특히 중요하다 — 이 베이스라인이 없으면 이관 후에
"내가 깨뜨린 것"과 "원래 깨져 있던 것"을 구분할 수 없다.

    python3 survey.py ~/vault-a ~/notes            # 표로 출력
    python3 survey.py ~/vault-a --json before.json # 저장해서 나중에 대조
"""
import os, re, sys, json, collections

# 백업·작업 디렉터리는 세지 않는다. 사본 안의 상대 링크는 원래 위치를 기준으로
# 쓰인 것이라 새 위치에서 깨진 것처럼 보이고, 그러면 "이관이 링크를 깨뜨렸나"라는
# 판단이 오염된다.
SKIP_DIRS = {".git", ".obsidian", ".ok", "node_modules", ".venv", "__pycache__",
             ".digest", ".lint", ".backup", ".trash"}

WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
# 로컬 .md 링크 전부 — 상대(./ ../), 루트상대(dir/foo.md), 맨이름(foo.md).
# 외부 URL·mailto·순수 앵커만 뺀다. ./ ../ 만 잡으면 깨진 링크 수는 맞아도
# 링크 그래프에 구멍이 나고, 고아 판정이 그 그래프를 먹는다.
MDLINK = re.compile(r"\[[^\]]*\]\((?!https?://|mailto:|#)([^)#\s]+\.md)")
FENCE = re.compile(r"```.*?```", re.S)
# 이중 백틱을 먼저 본다. ``[`a.md`](a.md)`` 처럼 안에 백틱이 든 예시는 단일 백틱
# 패턴으로는 반쪽만 벗겨져, 문서에 적은 링크 *예시*가 실제 깨진 링크로 잡힌다.
INLINE_CODE = re.compile(r"``[^\n]*?``|`[^`\n]*`")


def strip_code(text):
    """코드 블록·인라인 코드를 지운다 — 예시로 적힌 링크를 실제 링크로 세지 않기 위해."""
    return INLINE_CODE.sub("", FENCE.sub("", text))


def walk_md(root):
    for dp, dn, fns in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for fn in sorted(fns):
            if fn.endswith((".md", ".mdx")):
                yield os.path.join(dp, fn)


def survey(root, edges=False):
    root = os.path.abspath(os.path.expanduser(root))
    r = {
        "root": root, "md_files": 0,
        "wikilink_files": 0, "wikilink_count": 0,
        "mdlink_files": 0, "mdlink_count": 0,
        "frontmatter_files": 0,
        "links_ok": 0, "links_broken": 0,
        "broken_samples": [],
    }
    if edges:
        # 해석된 링크 전량 (출발, 도착) — 고아 판정용. 기본으로는 모으지 않는다.
        r["edges"], r["broken"], r["files"] = [], [], []
    if not os.path.isdir(root):
        r["error"] = "디렉터리 없음"
        return r

    for path in walk_md(root):
        r["md_files"] += 1
        try:
            with open(path, encoding="utf-8") as fh:
                raw = fh.read()
        except (UnicodeDecodeError, OSError):
            continue

        if raw.startswith("---"):
            r["frontmatter_files"] += 1

        text = strip_code(raw)
        rel = os.path.relpath(path, root)
        dp = os.path.dirname(path)
        if edges:
            r["files"].append(rel)

        wl = WIKILINK.findall(text)
        if wl:
            r["wikilink_files"] += 1
            r["wikilink_count"] += len(wl)

        ml = MDLINK.findall(text)
        if ml:
            r["mdlink_files"] += 1
            r["mdlink_count"] += len(ml)
        for target in ml:
            dest = os.path.normpath(os.path.join(dp, target))
            if os.path.exists(dest):
                r["links_ok"] += 1
                if edges:
                    r["edges"].append([rel, os.path.relpath(dest, root)])
            else:
                r["links_broken"] += 1
                if len(r["broken_samples"]) < 10:
                    r["broken_samples"].append({"from": rel, "to": target})
                if edges:
                    r["broken"].append([rel, target])
    return r


def main():
    # 값을 받는 플래그의 값이 저장소 인자로 새어 들어가지 않게 직접 훑는다.
    argv, args, opts = sys.argv[1:], [], {}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--json", "--graph"):
            opts[a] = argv[i + 1] if i + 1 < len(argv) else None
            i += 2
        elif a.startswith("--"):
            i += 1
        else:
            args.append(a)
            i += 1
    json_out, graph_out = opts.get("--json"), opts.get("--graph")
    if not args:
        print(__doc__)
        sys.exit(1)

    results = [survey(a, edges=bool(graph_out)) for a in args]

    w = max(len(os.path.basename(r["root"]) or r["root"]) for r in results) + 2
    print(f"{'저장소':<{w}} {'md':>6} {'wiki링크':>9} {'md링크':>8} {'프론트':>8} {'해석':>7} {'깨짐':>7}")
    print("-" * (w + 50))
    tot = collections.Counter()
    for r in results:
        name = os.path.basename(r["root"]) or r["root"]
        if r.get("error"):
            print(f"{name:<{w}} {r['error']}")
            continue
        fm = f"{r['frontmatter_files']}/{r['md_files']}"
        print(f"{name:<{w}} {r['md_files']:>6} "
              f"{r['wikilink_count']:>4}({r['wikilink_files']:>3}f) "
              f"{r['mdlink_count']:>4}({r['mdlink_files']:>2}f) "
              f"{fm:>8} {r['links_ok']:>7} {r['links_broken']:>7}")
        for k in ("md_files", "wikilink_count", "mdlink_count", "links_ok", "links_broken"):
            tot[k] += r[k]
    if len(results) > 1:
        print("-" * (w + 50))
        print(f"{'합계':<{w}} {tot['md_files']:>6} {tot['wikilink_count']:>9} "
              f"{tot['mdlink_count']:>8} {'':>8} {tot['links_ok']:>7} {tot['links_broken']:>7}")

    broken = [b for r in results for b in r.get("broken_samples", [])]
    if broken:
        print("\n깨진 링크 예시:")
        for b in broken[:8]:
            print(f"  {b['from']} → {b['to']}")

    if graph_out:
        with open(graph_out, "w", encoding="utf-8") as f:
            json.dump({"results": results}, f, ensure_ascii=False)
        print(f"\n링크 그래프 저장: {graph_out}")
    if json_out:
        slim = [{k: v for k, v in r.items() if k not in ("edges", "broken", "files")}
                for r in results]
        with open(json_out, "w", encoding="utf-8") as f:
            json.dump({"results": slim, "totals": dict(tot)}, f, ensure_ascii=False, indent=2)
        print(f"\n저장: {json_out}")


if __name__ == "__main__":
    main()
