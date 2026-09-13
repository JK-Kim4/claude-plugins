#!/usr/bin/env python3
"""위키 점검 — 기계적으로 후보를 좁힌다. 판정은 LLM 이 한다.

    python3 lint.py                            # 4종 요약 (루트는 설정에서)
    python3 lint.py <위키루트>                  # 루트를 직접 지정
    python3 lint.py --check links              # 한 종만 상세
    python3 lint.py --json out.json            # LLM 이 먹을 형태
    python3 lint.py --check links --apply      # 복구 가능한 링크만 적용

위키 루트는 인자가 없으면 `~/.config/llm-wiki/config.json` 의 `root` 를 쓴다.

점검 4종 — links(깨진 링크) · orphans(고아) · pending(미결 마커) · stale(낡음).

**모순 판정은 여기 없다.** 후보를 좁히는 기계적 신호를 찾지 못했다. 식별자를 공유하는
문서 쌍으로 좁혀도 수백 쌍이 남고, 애초에 같은 커밋을 두 문서가 언급하는 건 모순이 아니라
정상 패턴이라 거짓 양성이 대부분이다. 모순은 pending 판정 중에 드러나는 것으로 둔다.

링크 파싱과 해석은 wiki-bootstrap 의 survey.py·wikilink_convert.py 를 그대로 쓴다.
여기서 다시 구현하지 않는다 — 두 벌이 되면 어느 쪽 숫자가 맞는지 알 수 없어진다.
"""
import os, re, sys, json, subprocess, collections

# --- 이웃 스킬 적재 -------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
BOOTSTRAP = os.path.normpath(os.path.join(HERE, "..", "..", "wiki-bootstrap", "scripts"))
if "--bootstrap" in sys.argv:
    BOOTSTRAP = os.path.expanduser(sys.argv[sys.argv.index("--bootstrap") + 1])
sys.path.insert(0, BOOTSTRAP)
try:
    from survey import survey, SKIP_DIRS
    from wikilink_convert import build_index, resolve, CODE
except ImportError:
    sys.exit(f"wiki-bootstrap 스크립트를 찾지 못했다: {BOOTSTRAP}\n"
             f"두 스킬이 형제 디렉터리로 설치돼 있어야 한다. "
             f"아니면 --bootstrap <경로> 로 지정한다.")

CHECKS = ("links", "orphans", "pending", "stale")

CONFIG = os.path.expanduser("~/.config/llm-wiki/config.json")


def configured_root():
    """설정에 기록된 위키 루트. wiki-bootstrap 이 구축 마지막 단계에서 남긴다."""
    try:
        with open(CONFIG, encoding="utf-8") as f:
            return json.load(f).get("root")
    except (OSError, ValueError):
        return None

# --- 고아 면제 규칙 -------------------------------------------------------
# 링크로 도달하지 않는 게 정상인 문서들. 이걸 안 빼면 고아 목록이 전체의 40% 가 되어
# 아무도 안 본다.
EXEMPT_DIR = ("sessions/", "templates/")        # 날짜·검색으로 도달하는 문서
EXEMPT_SEG = ("/_archive/", "/archive/")        # 보관물 — 안 걸리는 게 목적
EXEMPT_BASE = {"00-INDEX.md", "00-STATUS.md", "README.md", "index.md"}  # 링크의 출발지

# 원문 보존 영역. 여기 문서의 링크는 원본 저장소 기준으로 쓰인 것이라, 위키 안에서
# 같은 이름을 찾아 이어붙이면 엉뚱한 프로젝트 문서로 연결된다. 실측에서 한 프로젝트
# 원문의 ./plan/README.md 가 다른 프로젝트의 같은 이름 문서로 이어질 뻔했다.
FROZEN_DIR = ("sources/", "raw/")

# --- 미결 마커 ------------------------------------------------------------
# 세션 문서의 "어디로 이어지나" 는 좁은 어휘로 미결을 적는다. 그 하나하나가
# 지금은 참이거나 거짓인 주장이고, 그게 곧 "낡은 주장" 후보다.
SECTION = re.compile(r"^##\s*어디로 이어지나\s*?$(.*?)(?=^##\s|\Z)", re.M | re.S)
MARKER = re.compile(r"미착수|미검증|미확인|미결|미push|미푸시|미병합|미반영|미적용"
                    r"|대기 중|확인 대기|착수 전|남았다|남겼다")

LINK = re.compile(r"(\[[^\]]*\]\()(?!https?://|mailto:|#)([^)#\s]+\.md)([^)]*\))")
BULLET = re.compile(r"^\s*([-*+]|\d+\.)\s+")


def in_archive(rel):
    return any(s in "/" + rel for s in EXEMPT_SEG)


def exempt(rel):
    return (rel.startswith(EXEMPT_DIR)
            or in_archive(rel)
            or os.path.basename(rel) in EXEMPT_BASE)


# --- 점검 ------------------------------------------------------------------

def check_links(root, g, by_base, all_rel, all_set):
    """깨진 링크를 복구 가능성으로 가른다 — 세는 것과 고칠 수 있는 것은 다르다.

    아카이브와 원문 보존 영역에서 출발하는 링크는 절대 고치지 않는다. 얼려둔 스냅샷의
    내부 링크가 깨져 보이는 건 스냅샷이 옛 구조를 그대로 담고 있기 때문이고, 그걸 현행
    문서로 갈아끼우면 스냅샷이 스냅샷이 아니게 된다. 실측에서 '복구 가능' 후보의 9/10 이
    이 경우였다.
    """
    out = {"fixable": [], "ambiguous": [], "absent": [], "frozen": []}
    for src, target in g["broken"]:
        if in_archive(src) or src.startswith(FROZEN_DIR):
            out["frozen"].append({"from": src, "to": target})
            continue
        r = resolve(target, src, by_base, all_rel, all_set)
        if isinstance(r, str):
            srcdir = os.path.dirname(src)
            new = os.path.relpath(os.path.join(root, r), os.path.join(root, srcdir) if srcdir else root)
            if not new.startswith("."):
                new = "./" + new
            out["fixable"].append({"from": src, "to": target, "new": new})
        elif isinstance(r, tuple):
            # 후보가 '현행 문서'와 '아카이브 안의 그 사본' 뿐이면 모호하지 않다.
            # 살아 있는 문서를 가리키는 게 의도다 — 아카이브는 링크의 목적지가 아니다.
            live = [c for c in r[1] if not in_archive(c)]
            if len(live) == 1:
                srcdir = os.path.dirname(src)
                new = os.path.relpath(os.path.join(root, live[0]),
                                      os.path.join(root, srcdir) if srcdir else root)
                out["fixable"].append({"from": src, "to": target,
                                       "new": new if new.startswith(".") else "./" + new})
            else:
                out["ambiguous"].append({"from": src, "to": target, "candidates": r[1][:6]})
        else:
            out["absent"].append({"from": src, "to": target})
    return out


def check_orphans(g):
    """피참조 0건. 면제 규칙을 적용하고 디렉터리별로 묶는다 —
    개별 200행이 아니라 '어느 디렉터리가 자기 문서를 색인하지 않는가' 가 발견이다."""
    inbound = collections.Counter(dst for _, dst in g["edges"])
    orph = [f for f in g["files"] if inbound[f] == 0]
    kept = [o for o in orph if not exempt(o)]
    by_dir = collections.defaultdict(list)
    for o in kept:
        by_dir[os.path.dirname(o) or "(루트)"].append(o)
    return {"total": len(orph), "exempted": len(orph) - len(kept),
            "items": kept,
            "by_dir": sorted(((d, v) for d, v in by_dir.items()),
                             key=lambda x: -len(x[1]))}


def check_pending(root, files):
    """세션 문서가 스스로 적어둔 미결. 원본 저장소·코드로 참·거짓을 판정할 대상."""
    items = []
    for rel in files:
        try:
            text = open(os.path.join(root, rel), encoding="utf-8").read()
        except OSError:
            continue
        m = SECTION.search(text)
        if not m:
            continue
        start = text[:m.start(1)].count("\n") + 1
        # 마커가 걸린 줄만 뽑으면 안 된다. 미결 항목은 여러 줄짜리 불릿으로 적히고
        # 주어가 첫 줄에 있는 경우가 많아서, 마커 줄만 보면 "무엇이 미결인지"가
        # 통째로 빠진다 — 실측에서 164개 중 34개가 불릿 첫 줄이 아니었고,
        # 그 때문에 판정 가능한 항목을 판정 불가로 넘기는 일이 실제로 생겼다.
        blocks, cur = [], None
        for i, line in enumerate(m.group(1).splitlines()):
            if not line.strip():
                if cur:
                    blocks.append(cur)
                cur = None
            elif BULLET.match(line):
                if cur:
                    blocks.append(cur)
                cur = [start + i, [line]]
            elif cur:
                cur[1].append(line)
            else:
                cur = [start + i, [line]]
        if cur:
            blocks.append(cur)
        for ln, ls in blocks:
            body = re.sub(r"\s+", " ", " ".join(l.strip() for l in ls)).strip()
            hits = MARKER.findall(body)
            if hits:
                items.append({"file": rel, "line": ln, "markers": sorted(set(hits)),
                              "text": body[:400]})
    return {"docs": len({i["file"] for i in items}), "items": items}


def check_stale(root, files):
    """마지막 수정일. 이관 직후에는 전부 같은 날이라 신호가 없다 —
    없으면 없다고 보고한다. 몇 달 지나면 같은 코드가 진짜 신호를 낸다."""
    ts = {}
    try:
        out = subprocess.run(["git", "-C", root, "log", "--format=%at", "--name-only"],
                             capture_output=True, text=True, timeout=60)
        cur = None
        for line in out.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.isdigit() and len(line) == 10:
                cur = int(line)
            elif cur and line not in ts:      # log 는 최신순 — 첫 등장이 최종 수정
                ts[line] = cur
    except (OSError, subprocess.SubprocessError):
        pass
    known = {f: ts[f] for f in files if f in ts}
    # 이력 전체가 낡음 기준(180일)보다 짧으면 낡은 문서를 가려낼 수가 없다.
    # 없는 신호를 있는 척 내놓지 않는다 — 몇 달 뒤 같은 코드가 진짜 신호를 낸다.
    span = (max(known.values()) - min(known.values())) if len(known) >= 2 else 0
    if span < 30 * 86400:
        return {"signal": False, "items": [],
                "reason": f"git 이력 전체가 {span // 86400}일치라 낡음을 가릴 수 없다"}
    newest = max(known.values())
    items = sorted(({"file": f, "days": (newest - t) // 86400} for f, t in known.items()),
                   key=lambda x: -x["days"])
    return {"signal": True, "items": [i for i in items if i["days"] >= 180][:60]}


# --- 링크 적용 --------------------------------------------------------------

def apply_links(root, fixable):
    """복구 가능으로 판정된 것만 고친다. 실제로 바꾼 수를 돌려준다 —
    후보 수를 그대로 보고하면 조용히 안 고쳐진 게 섞인다.

    코드 영역은 잘라내지 않고 위치로 거른다. 잘라내면 [`경로`](경로) 처럼 표시
    문자열이 백틱으로 감싸인 링크에서 여는 대괄호와 괄호가 다른 조각으로 갈라져
    매칭 자체가 실패한다.
    """
    per_file = collections.defaultdict(dict)
    for f in fixable:
        per_file[f["from"]][f["to"]] = f["new"]
    changed = replaced = 0
    for rel, mapping in per_file.items():
        path = os.path.join(root, rel)
        text = open(path, encoding="utf-8").read()
        spans = [m.span() for m in CODE.finditer(text)]
        stat = [0]

        def repl(m):
            if any(a <= m.start() < b for a, b in spans):
                return m.group(0)                      # 코드 안의 예시
            new = mapping.get(m.group(2))
            if not new:
                return m.group(0)
            stat[0] += 1
            # 표시 문자열이 경로 그 자체면 같이 고친다 —
            # 안 그러면 보이는 경로와 가리키는 경로가 갈라진다.
            return m.group(1).replace(m.group(2), new) + new + m.group(3)

        new_text = LINK.sub(repl, text)
        if new_text != text:
            open(path, "w", encoding="utf-8").write(new_text)
            changed += 1
            replaced += stat[0]
    return changed, replaced


# --- 출력 --------------------------------------------------------------------

def report(res, which):
    if "links" in which:
        L = res["links"]
        print(f"\n[깨진 링크] {sum(len(v) for v in L.values())}건")
        print(f"  복구 가능 {len(L['fixable'])} · 모호 {len(L['ambiguous'])} · "
              f"대상 없음 {len(L['absent'])} · 불변 영역 {len(L['frozen'])}")
        if which == ("links",):
            for f in L["fixable"][:40]:
                print(f"  고침  {f['from']}\n          {f['to']}  →  {f['new']}")
            for a in L["ambiguous"][:20]:
                print(f"  모호  {a['from']}\n          {a['to']}  →  {', '.join(a['candidates'][:4])}")
            print(f"\n  대상 없음 {len(L['absent'])}건은 고칠 게 아니라 "
                  f"'여기에 문서가 있어야 한다'는 정보다. 지우지 않는다.")

    if "orphans" in which:
        O = res["orphans"]
        print(f"\n[고아 문서] {len(O['items'])}건 (면제 {O['exempted']}건 제외, 총 {O['total']})")
        for d, v in O["by_dir"][:12]:
            print(f"  {len(v):>4}  {d}/")
        if which == ("orphans",):
            for d, v in O["by_dir"]:
                print(f"\n  {d}/ — {len(v)}건")
                for o in v[:8]:
                    print(f"      {os.path.basename(o)}")
                if len(v) > 8:
                    print(f"      … 외 {len(v)-8}건")

    if "pending" in which:
        P = res["pending"]
        print(f"\n[미결 마커] {len(P['items'])}개 지점 / 문서 {P['docs']}건")
        if which == ("pending",):
            cur = None
            for i in P["items"]:
                if i["file"] != cur:
                    cur = i["file"]
                    print(f"\n  {cur}")
                print(f"    :{i['line']}  {i['text']}")
        else:
            c = collections.Counter(m for i in P["items"] for m in i["markers"])
            print("  " + " · ".join(f"{k} {v}" for k, v in c.most_common(6)))

    if "stale" in which:
        S = res["stale"]
        if not S["signal"]:
            print(f"\n[낡은 문서] 신호 없음 — {S['reason']}")
        else:
            print(f"\n[낡은 문서] 180일 이상 손 안 댄 문서 {len(S['items'])}건")
            for i in S["items"][:20] if which == ("stale",) else S["items"][:5]:
                print(f"  {i['days']:>5}일  {i['file']}")


def main():
    argv, args, opts = sys.argv[1:], [], {}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--json", "--check", "--bootstrap"):
            opts[a] = argv[i + 1] if i + 1 < len(argv) else None
            i += 2
        elif a.startswith("--"):
            opts[a] = True
            i += 1
        else:
            args.append(a)
            i += 1
    # 루트를 안 주면 설정에서 얻는다 — 위키 밖에서 불려도 동작해야 한다.
    root = args[0] if args else configured_root()
    if not root:
        sys.exit(f"위키 루트를 모른다. {CONFIG} 에 root 가 없고 인자도 안 줬다.\n"
                 f"wiki-bootstrap 으로 구축했다면 거기서 기록됐어야 한다.")
    root = os.path.abspath(os.path.expanduser(root))
    if not os.path.isdir(root):
        sys.exit(f"위키 루트가 없다: {root}")
    which = (opts["--check"],) if opts.get("--check") else CHECKS
    for w in which:
        if w not in CHECKS:
            sys.exit(f"모르는 점검: {w} (가능: {', '.join(CHECKS)})")

    g = survey(root, edges=True)
    by_base, all_rel, all_set = build_index(root)
    res = {}
    if "links" in which:
        res["links"] = check_links(root, g, by_base, all_rel, all_set)
    if "orphans" in which:
        res["orphans"] = check_orphans(g)
    if "pending" in which:
        res["pending"] = check_pending(root, g["files"])
    if "stale" in which:
        res["stale"] = check_stale(root, g["files"])

    print(f"{os.path.basename(root)} — 마크다운 {len(g['files'])}건 점검")
    report(res, which)

    if opts.get("--apply"):
        if "links" not in res:
            sys.exit("\n--apply 는 --check links 와 함께 쓴다.")
        nf, nl = apply_links(root, res["links"]["fixable"])
        print(f"\n적용 — 파일 {nf}개에서 링크 {nl}건 수정.")
        print("survey.py 로 깨진 링크가 줄었는지 확인할 것.")
    elif "links" in res and res["links"]["fixable"]:
        print(f"\n확인 후 --check links --apply 로 {len(res['links']['fixable'])}건을 적용한다.")

    if opts.get("--json"):
        with open(opts["--json"], "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=1)
        print(f"\n저장: {opts['--json']}")


if __name__ == "__main__":
    main()
