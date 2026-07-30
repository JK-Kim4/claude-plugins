#!/usr/bin/env python3
"""세션 원본을 위키의 raw/ 로 수집한다.

왜 필요한가 — Claude Code 는 `~/.claude/projects/` 의 세션을 기본 30일 후 지운다.
가공하고 싶어졌을 때는 이미 없을 수 있으므로, 관심 있는 프로젝트는 미리 지켜둔다.

    python3 collect.py               # 설정의 collect 목록을 수집
    python3 collect.py --dry-run     # 무엇이 복사될지만 표시
    python3 collect.py --file <경로> # 특정 파일 하나만 (digest 직전 확보용)
    python3 collect.py --auto-add    # 세션이 쌓인 새 프로젝트를 목록에 자동 등록
    python3 collect.py --auto-add --min-sessions 5   # 임계 조정 (기본 3)

cron/launchd 에 걸어 정기 실행해도 된다. 이미 수집한 원본은 건너뛴다.
원본은 복사만 하고 옮기지 않는다 — 옮기면 Claude Code 의 세션 재개가 깨진다.
"""
import json, os, re, shutil, sys, time

CONFIG = os.path.expanduser("~/.config/llm-wiki/config.json")
CLAUDE_PROJECTS = os.path.expanduser("~/.claude/projects")
CODEX_SESSIONS = os.path.expanduser("~/.codex/sessions")
INPROGRESS_MIN = 60

SKIP_NAME = re.compile(r"^(agent-|journal)")


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


def raw_dirs(cfg):
    root = cfg.get("root")
    if not root or not os.path.isdir(root):
        print("위키 루트를 찾을 수 없다. locate.py root --set <경로> 로 먼저 지정할 것.",
              file=sys.stderr)
        sys.exit(3)
    raw = os.path.join(root, cfg.get("raw", "raw"))
    c, x = os.path.join(raw, "claude"), os.path.join(raw, "codex")
    os.makedirs(c, exist_ok=True)
    os.makedirs(x, exist_ok=True)
    return c, x


def slug_for(path):
    return re.sub(r"[/_]", "-", os.path.abspath(os.path.expanduser(path)))


def matches(project_dir, target_slug):
    """세션 디렉터리가 이 대상에 속하는가.

    단순 startswith 는 하위 프로젝트까지 삼킨다 — `~/workspaces` 를 등록하면
    `~/workspaces/my_app` 세션까지 전부 딸려온다. 워크트리 디렉터리만 `--` 로
    이어붙으므로(`...my-app--claude-worktrees-foo`) 그 경계로 정확히 가른다.
    """
    return project_dir == target_slug or project_dir.startswith(target_slug + "--")


def already_have(dest_dir, uuid8):
    return any(uuid8 in fn for fn in os.listdir(dest_dir))


def origin_name(project_dir, target=None):
    """세션 디렉터리명 → 읽기 좋은 프로젝트 이름.

    슬러그는 홈 경로가 통째로 들어가 길다. 사용자명 자체에 하이픈이 들어갈 수 있어
    (`some-user` 같은 계정) 정규식으로 앞부분을 자르면 어긋난다 — 실제로 그 버그를
    겪었다. 대상 경로의 슬러그와 문자열 대조해 떼어내는 편이 안전하다.
    """
    if target:
        base = os.path.basename(target.rstrip("/"))
        tslug = slug_for(target)
        if project_dir.startswith(tslug):
            wt = project_dir[len(tslug):].lstrip("-")
            wt = re.sub(r"^claude-worktrees-", "", wt)
            return f"{base}-{wt}" if wt else base
        return base
    # 대상을 모를 때는 홈 슬러그만 떼어낸다
    home_slug = slug_for("~") + "-"
    return project_dir[len(home_slug):] if project_dir.startswith(home_slug) else project_dir


def copy_claude(src, dest_dir, dry, target=None):
    """raw/claude/YYYY-MM-DD-<프로젝트>-<uuid8>.jsonl 로 담는다."""
    uuid8 = os.path.basename(src)[:8]
    if already_have(dest_dir, uuid8):
        return None
    d = time.strftime("%Y-%m-%d", time.localtime(os.path.getmtime(src)))
    origin = origin_name(os.path.basename(os.path.dirname(src)), target) or "unknown"
    name = f"{d}-{origin}-{uuid8}.jsonl"
    if not dry:
        shutil.copy2(src, os.path.join(dest_dir, name))
    return name


def copy_codex(src, dest_dir, dry):
    name = os.path.basename(src)
    if os.path.exists(os.path.join(dest_dir, name)):
        return None
    if not dry:
        shutil.copy2(src, os.path.join(dest_dir, name))
    return name


def claude_cwd(path):
    """세션 파일에 기록된 작업 경로. 슬러그를 역산할 필요가 없다.

    디렉터리명(`-Users-...-my-app`)은 `/` 와 `_` 를 모두 `-` 로 바꾼 것이라
    되돌릴 수 없다 — `my-app` 이 `my_app` 인지 `my-app` 인지 알 수 없다.
    파일 안의 `cwd` 는 원본 경로 그대로라 이 문제가 없다.
    워크트리 세션에서도 `cwd` 는 저장소 루트를 가리킨다(작업 위치는 relocatedCwd).
    """
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for _ in range(40):
                line = f.readline()
                if not line:
                    break
                try:
                    o = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if o.get("cwd"):
                    return o["cwd"]
    except OSError:
        pass
    return None


def auto_add(cfg, min_sessions, dry):
    """세션이 임계 이상 쌓인 프로젝트를 수집 목록에 자동 등록한다.

    명시적 등록에만 기대면 새 프로젝트를 잊고, 30일 보존 정책이 지나면 되살릴 수
    없다. 매일 도는 수집이 스스로 발견하는 편이 안전하다. 임계를 두는 이유는
    한두 번 열어본 디렉터리까지 전부 보존하면 용량만 늘기 때문이다.
    """
    if not os.path.isdir(CLAUDE_PROJECTS):
        return []
    counts = {}
    for d in sorted(os.listdir(CLAUDE_PROJECTS)):
        pdir = os.path.join(CLAUDE_PROJECTS, d)
        if not os.path.isdir(pdir):
            continue
        files = [f for f in os.listdir(pdir) if f.endswith(".jsonl") and not SKIP_NAME.match(f)]
        if not files:
            continue
        cwd = claude_cwd(os.path.join(pdir, files[0]))
        if not cwd or not os.path.isdir(cwd):
            continue
        # 워크트리는 루트 프로젝트로 합산된다 — 수집은 접두어로 함께 잡히므로
        counts[cwd] = counts.get(cwd, 0) + len(files)

    # 컨테이너 디렉터리는 등록하지 않는다. `~/workspaces` 처럼 안에 프로젝트가 여럿
    # 들어 있는 곳을 등록하면 Codex 쪽 경로 매칭이 하위를 전부 흡수해 사실상 전량
    # 수집이 된다. 다른 후보의 조상이면 그 자신은 프로젝트가 아니라 담는 그릇이다.
    others = set(counts)
    containers = {c for c in counts
                  if any(o != c and o.startswith(c + os.sep) for o in others)}

    have = {os.path.abspath(os.path.expanduser(t)) for t in cfg.get("collect", [])}
    added = []
    for cwd, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        if n < min_sessions or cwd in have or cwd in containers:
            continue
        if any(cwd.startswith(h + os.sep) for h in have):
            continue                                   # 이미 상위 경로가 등록돼 있다
        added.append((cwd, n))
    if added and not dry:
        cfg["collect"] = sorted(have | {c for c, _ in added})
        save_config(cfg)
    return added


def codex_cwd(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for _ in range(3):
                line = f.readline()
                if not line:
                    break
                try:
                    o = json.loads(line)
                except json.JSONDecodeError:
                    continue
                cwd = (o.get("payload") or {}).get("cwd") or o.get("cwd")
                if cwd:
                    return cwd
    except OSError:
        pass
    return None


def main():
    dry = "--dry-run" in sys.argv
    cfg = load_config()
    cdir, xdir = raw_dirs(cfg)
    now = time.time()
    copied = []

    if "--file" in sys.argv:
        src = os.path.abspath(os.path.expanduser(sys.argv[sys.argv.index("--file") + 1]))
        if not os.path.isfile(src):
            print(f"파일 없음: {src}", file=sys.stderr); sys.exit(1)
        n = (copy_codex(src, xdir, dry) if "rollout-" in os.path.basename(src)
             else copy_claude(src, cdir, dry))
        print(f"{'[건식] ' if dry else ''}{n or '이미 있음 — 건너뜀'}")
        return

    if "--auto-add" in sys.argv:
        m = 3
        if "--min-sessions" in sys.argv:
            m = int(sys.argv[sys.argv.index("--min-sessions") + 1])
        added = auto_add(cfg, m, dry)
        for cwd, n in added:
            print(f"{'[건식] ' if dry else ''}자동 등록: {cwd}  (세션 {n}개)")
        if added and not dry:
            cfg = load_config()

    targets = [os.path.abspath(os.path.expanduser(t)) for t in cfg.get("collect", [])]
    if not targets:
        print("정기 수집 대상이 없다. locate.py collect --add <경로> 로 추가하거나 "
              "--auto-add 로 자동 등록할 것.")
        return

    prefixes = [slug_for(t) for t in targets]

    if os.path.isdir(CLAUDE_PROJECTS):
        for d in sorted(os.listdir(CLAUDE_PROJECTS)):
            matched = next((t for t, p in zip(targets, prefixes) if matches(d, p)), None)
            if not matched:
                continue
            pdir = os.path.join(CLAUDE_PROJECTS, d)
            if not os.path.isdir(pdir):
                continue
            for fn in sorted(os.listdir(pdir)):
                if not fn.endswith(".jsonl") or SKIP_NAME.match(fn):
                    continue
                src = os.path.join(pdir, fn)
                if (now - os.path.getmtime(src)) / 60 < INPROGRESS_MIN:
                    continue                                  # 진행 중 — 기록이 미완이다
                n = copy_claude(src, cdir, dry, matched)
                if n:
                    copied.append(("claude", n))

    if os.path.isdir(CODEX_SESSIONS):
        for dp, _, fns in os.walk(CODEX_SESSIONS):
            for fn in sorted(fns):
                if not fn.endswith(".jsonl"):
                    continue
                src = os.path.join(dp, fn)
                if (now - os.path.getmtime(src)) / 60 < INPROGRESS_MIN:
                    continue
                cwd = codex_cwd(src)                          # 경로가 날짜별이라 내용을 봐야 한다
                if not cwd or not any(cwd.startswith(t) for t in targets):
                    continue
                n = copy_codex(src, xdir, dry)
                if n:
                    copied.append(("codex", n))

    head = "[건식] " if dry else ""
    print(f"{head}수집 {len(copied)}건  (대상 {len(targets)}개 프로젝트)")
    for kind, n in copied[:30]:
        print(f"  {kind}: {n}")
    if len(copied) > 30:
        print(f"  … 외 {len(copied)-30}건")


if __name__ == "__main__":
    main()
