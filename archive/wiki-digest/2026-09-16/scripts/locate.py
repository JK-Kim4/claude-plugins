#!/usr/bin/env python3
"""위키 루트 해석 + 대상 세션 탐색.

스킬 본문에 경로를 박지 않기 위한 스크립트다. 루트는 설정에서, 대상 세션은
실행 위치(cwd)에서 파생한다 — 둘 다 머신에 독립적이다.

    python3 locate.py root                      # 위키 루트 해석 (없으면 탐색 결과 제안)
    python3 locate.py root --set ~/knowledge    # 설정에 기록
    python3 locate.py sessions                  # cwd 기준 대상 세션
    python3 locate.py sessions --cwd ~/repo     # 특정 프로젝트 기준
    python3 locate.py sessions --all            # 전 프로젝트
    python3 locate.py sessions --new-only       # 아직 가공 안 된 것만
    python3 locate.py collect                   # 정기 수집 대상 목록
    python3 locate.py collect --add ~/repo      # 대상 추가 (프로젝트가 늘었을 때)
"""
import json, os, re, sys, time

CONFIG = os.path.expanduser("~/.config/llm-wiki/config.json")
CLAUDE_PROJECTS = os.path.expanduser("~/.claude/projects")
CODEX_SESSIONS = os.path.expanduser("~/.codex/sessions")
INPROGRESS_MIN = 60  # 최근 N분 내 수정된 세션은 진행 중으로 보고 제외한다


# ---------- 루트 ----------

def load_config():
    if os.path.isfile(CONFIG):
        try:
            return json.load(open(CONFIG, encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {}


def save_config(cfg):
    os.makedirs(os.path.dirname(CONFIG), exist_ok=True)
    json.dump(cfg, open(CONFIG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def looks_like_wiki(d):
    return os.path.isfile(os.path.join(d, "00-INDEX.md")) and os.path.isdir(os.path.join(d, "raw"))


def discover():
    """설정이 없을 때 후보를 찾는다. 확정은 사용자가 한다."""
    home = os.path.expanduser("~")
    hits = []
    for name in ("knowledge", "wiki", "kb", "notes", "vault", "obsidian", "Documents", "dev"):
        base = os.path.join(home, name)
        if not os.path.isdir(base):
            continue
        if looks_like_wiki(base):
            hits.append(base)
        else:
            try:
                for sub in sorted(os.listdir(base)):
                    p = os.path.join(base, sub)
                    if os.path.isdir(p) and looks_like_wiki(p):
                        hits.append(p)
            except OSError:
                pass
    return hits


def cmd_root(argv):
    if "--set" in argv:
        i = argv.index("--set")
        root = os.path.abspath(os.path.expanduser(argv[i + 1]))
        cfg = load_config()
        cfg.update({"root": root, "raw": cfg.get("raw", "raw"),
                    "sessions": cfg.get("sessions", "sessions")})
        save_config(cfg)
        print(f"기록: {CONFIG}\nroot = {root}")
        if not looks_like_wiki(root):
            print("경고: 00-INDEX.md 또는 raw/ 가 없다. 경로를 확인할 것.")
        return

    cfg = load_config()
    if cfg.get("root") and os.path.isdir(cfg["root"]):
        print(cfg["root"])
        return
    hits = discover()
    if hits:
        print("설정 없음. 후보:", file=sys.stderr)
        for h in hits:
            print(f"  {h}", file=sys.stderr)
        print("확정하려면: locate.py root --set <경로>", file=sys.stderr)
    else:
        print("설정도 후보도 없음. 사용자에게 위키 루트를 묻고 --set 으로 기록할 것.",
              file=sys.stderr)
    sys.exit(3)


# ---------- 세션 ----------

def slug_for(cwd):
    """Claude Code 의 프로젝트 디렉터리명 규칙: 경로의 / 와 _ 를 모두 - 로.

    정방향 전용이다. 슬러그에서 경로를 되돌리려 하면 안 된다 —
    my-app 이 my_app 인지 my-app 인지 구분할 수 없다.
    """
    return re.sub(r"[/_]", "-", os.path.abspath(os.path.expanduser(cwd)))


def digested_sources(root, cfg):
    """이미 가공된 세션의 원본 경로 집합 — frontmatter 의 session_file 을 읽는다."""
    sdir = os.path.join(root, cfg.get("sessions", "sessions"))
    done = set()
    if not os.path.isdir(sdir):
        return done
    for fn in os.listdir(sdir):
        if not fn.endswith(".md"):
            continue
        try:
            with open(os.path.join(sdir, fn), encoding="utf-8") as f:
                for _ in range(30):
                    line = f.readline()
                    if not line or line.startswith("## "):
                        break
                    if line.startswith("session_file:"):
                        done.add(os.path.basename(line.split(":", 1)[1].strip().strip("\"'")))
                        break
        except OSError:
            continue
    return done


def claude_sessions(prefix=None):
    """prefix 는 대상 프로젝트의 슬러그. 워크트리(`슬러그--...`)는 포함하되
    하위 프로젝트(`슬러그-이름`)는 삼키지 않는다 — 구분자가 `--` 인 점을 이용한다."""
    out = []
    if not os.path.isdir(CLAUDE_PROJECTS):
        return out
    for d in sorted(os.listdir(CLAUDE_PROJECTS)):
        if prefix and not (d == prefix or d.startswith(prefix + "--")):
            continue
        pdir = os.path.join(CLAUDE_PROJECTS, d)
        if not os.path.isdir(pdir):
            continue
        for fn in sorted(os.listdir(pdir)):
            if fn.endswith(".jsonl") and not fn.startswith("agent-"):
                out.append((os.path.join(pdir, fn), d))
    return out


def codex_sessions(cwd_filter=None):
    out = []
    if not os.path.isdir(CODEX_SESSIONS):
        return out
    for dp, dn, fns in os.walk(CODEX_SESSIONS):
        for fn in sorted(fns):
            if not fn.endswith(".jsonl"):
                continue
            p = os.path.join(dp, fn)
            if cwd_filter:
                # codex 는 경로가 날짜별이라 cwd 를 파일 안에서 확인해야 한다
                found = None
                try:
                    with open(p, encoding="utf-8", errors="replace") as f:
                        for _ in range(3):
                            line = f.readline()
                            if not line:
                                break
                            try:
                                o = json.loads(line)
                            except json.JSONDecodeError:
                                continue
                            found = (o.get("payload") or {}).get("cwd") or o.get("cwd")
                            if found:
                                break
                except OSError:
                    continue
                if not found or not found.startswith(cwd_filter):
                    continue
            out.append((p, "codex"))
    return out


def cmd_sessions(argv):
    cfg = load_config()
    root = cfg.get("root")
    now = time.time()

    scope_all = "--all" in argv
    cwd = os.getcwd()
    if "--cwd" in argv:
        cwd = os.path.expanduser(argv[argv.index("--cwd") + 1])
    cwd = os.path.abspath(cwd)

    # 위키 안이나 홈에서 실행하면 특정 프로젝트를 겨냥한 게 아니므로 전체로 본다
    if root and (cwd == root or cwd.startswith(root + os.sep)):
        scope_all = True
    if cwd == os.path.expanduser("~"):
        scope_all = True

    if scope_all:
        items = claude_sessions() + codex_sessions()
        scope = "전체"
    else:
        items = claude_sessions(prefix=slug_for(cwd)) + codex_sessions(cwd_filter=cwd)
        scope = cwd

    done = digested_sources(root, cfg) if (root and "--new-only" in argv) else set()

    rows = []
    for path, origin in items:
        try:
            st = os.stat(path)
        except OSError:
            continue
        age_min = (now - st.st_mtime) / 60
        if age_min < INPROGRESS_MIN:
            continue                      # 진행 중 — 기록이 미완이다
        if done and os.path.basename(path) in done:
            continue
        rows.append((st.st_mtime, path, origin, st.st_size))

    rows.sort(reverse=True)
    print(f"# 범위: {scope}   대상 {len(rows)}건"
          + ("   (미가공분만)" if "--new-only" in argv else ""))
    for mt, path, origin, size in rows:
        d = time.strftime("%Y-%m-%d", time.localtime(mt))
        print(f"{d}\t{size/1024/1024:6.1f}MB\t{origin}\t{path}")


def cmd_collect(argv):
    """정기 수집 대상 프로젝트 목록.

    탐색(sessions)은 목록이 필요 없다 — cwd 로 파생하거나 전체를 훑으면 된다.
    수집이 목록을 요구하는 이유는 보존 정책 때문이다: Claude Code 는 세션을 30일 후
    지우므로, 나중에 가공하고 싶어질 것을 미리 지켜둬야 한다. 전량 보존은 수백 MB 가
    계속 쌓이므로 관심 있는 것만 고른다.
    """
    cfg = load_config()
    targets = cfg.get("collect", [])

    def norm(p):
        return os.path.abspath(os.path.expanduser(p))

    if "--add" in argv:
        p = norm(argv[argv.index("--add") + 1])
        if not os.path.isdir(p):
            print(f"경고: 디렉터리가 없다 — {p}", file=sys.stderr)
        if p not in targets:
            targets.append(p)
            cfg["collect"] = sorted(targets)
            save_config(cfg)
            print(f"추가: {p}")
        else:
            print(f"이미 있음: {p}")
    elif "--remove" in argv:
        p = norm(argv[argv.index("--remove") + 1])
        if p in targets:
            targets.remove(p)
            cfg["collect"] = targets
            save_config(cfg)
            print(f"제거: {p}")
        else:
            print(f"목록에 없음: {p}")
    else:
        if not targets:
            print("# 정기 수집 대상 없음 — digest 요청 시 그 자리에서 복사한다.")
            print("# 보존이 필요하면: locate.py collect --add <프로젝트 경로>")
        for t in targets:
            mark = "" if os.path.isdir(t) else "  (경로 없음)"
            print(f"{t}{mark}")


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    cmd, argv = sys.argv[1], sys.argv[2:]
    if cmd == "root":
        cmd_root(argv)
    elif cmd == "sessions":
        cmd_sessions(argv)
    elif cmd == "collect":
        cmd_collect(argv)
    else:
        print(__doc__); sys.exit(1)


if __name__ == "__main__":
    main()
