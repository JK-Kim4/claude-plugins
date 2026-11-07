#!/usr/bin/env python3
"""breach-watch 카탈로그 스크립트. 사건(incidents)·점검 항목(checks)·버전을 다룬다.

    python3 catalog.py where                      # 지금 쓰는 카탈로그와 모드
    python3 catalog.py validate                   # 스키마·참조·버전 검사 (갱신 후 0건이어야 한다)
    python3 catalog.py stats                      # 카테고리별·AI 관여별 수
    python3 catalog.py profile [--root .]         # 대상 프로젝트의 스택 태그 추정
    python3 catalog.py list-checks [--since 1.0.0] [--tags node,aws] [--category X] [--format md|json]
    python3 catalog.py scan [--root .] [--tags ...] [--since ...]   # 점검 항목 신호(파일·패턴) 후보 수집
    python3 catalog.py bump minor --note "2026-12 정기 조사"         # "next" 를 새 버전으로 확정
    python3 catalog.py render                     # CHECKLIST.md 재생성
    python3 catalog.py init-local                 # 사용자 카탈로그(~/.claude/breach-watch/catalog) 생성
    python3 catalog.py sync [--prefer local|bundled]                # 번들 카탈로그를 사용자 카탈로그로 병합

책임은 셋이다. (1) 카탈로그가 깨지지 않게 기계 검사한다. (2) 버전을 결정적으로 올리고
"어느 버전에 무엇이 들어왔는지"를 항목마다 남긴다. (3) 점검할 후보를 좁혀 준다.
점검 판정(취약한가)은 하지 않는다. 그건 스킬을 실행하는 에이전트가 근거를 읽고 한다.

Python 3.9 이상. 표준 라이브러리만 쓴다.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUNDLED = HERE.parent / "catalog"
LOCAL = Path(os.path.expanduser("~/.claude/breach-watch/catalog"))
ENV = "BREACH_WATCH_CATALOG"

FILES = ("catalog.json", "incidents.json", "checks.json")
SEVERITIES = ("critical", "high", "medium", "low")
METHODS = ("code", "config", "infra", "process")
AI_LEVELS = ("confirmed", "reported", "none-reported")
CONFIDENCE = ("high", "medium", "low")
STATUSES = ("active", "deprecated")
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
DATE = re.compile(r"^\d{4}-\d{2}(-\d{2})?$")
NEXT = "next"  # 아직 릴리스하지 않은 항목의 added_in/updated_in. bump 가 버전으로 바꾼다.

# 스캔에서 건너뛸 디렉터리. 의존성·빌드 산출물을 뒤지면 신호가 잡음에 묻힌다.
SKIP_DIRS = {".git", "node_modules", "vendor", "dist", "build", ".next", ".venv", "venv",
             "__pycache__", ".tox", "target", ".gradle", ".idea", "coverage", ".terraform"}
MAX_FILE_BYTES = 1_000_000
# 패턴 스캔에서 뺄 파일. lockfile 의 해시 문자열이 패턴에 우연히 걸려 잡음만 늘린다.
LOCKFILES = {"package-lock.json", "pnpm-lock.yaml", "yarn.lock", "poetry.lock", "uv.lock",
             "Cargo.lock", "Gemfile.lock", "composer.lock", "go.sum"}
TEST_PATH = re.compile(r"(^|/)(test|tests|__tests__|spec|fixtures?|testdata)(/|$)|\.(test|spec)\.[a-z]+$|Test\.(kt|java)$|_test\.(go|py)$")
MAX_HITS_PER_CHECK = 15


# --- 카탈로그 위치 -----------------------------------------------------------

def in_source_repo() -> bool:
    """번들 카탈로그가 플러그인 원본 저장소(마켓플레이스 checkout) 안에 있으면 True.

    설치본(~/.claude/plugins/...)은 플러그인 갱신 때 덮어써지므로 직접 고치면 안 된다.
    """
    if "/.claude/plugins/" in str(BUNDLED):
        return False
    for parent in BUNDLED.parents:
        if (parent / ".claude-plugin" / "marketplace.json").exists():
            return True
    return False


def active_dir() -> tuple[Path, str]:
    env = os.environ.get(ENV)
    if env:
        return Path(env).expanduser().resolve(), "env"
    if LOCAL.exists():
        return LOCAL, "local"
    return BUNDLED, "source" if in_source_repo() else "bundled-readonly"


def load(d: Path) -> dict:
    out = {}
    for name in FILES:
        p = d / name
        if not p.exists():
            sys.exit(f"카탈로그 파일 없음: {p}")
        out[name.split(".")[0]] = json.loads(p.read_text(encoding="utf-8"))
    return out


def save(d: Path, cat: dict) -> None:
    for key in ("catalog", "incidents", "checks"):
        text = json.dumps(cat[key], ensure_ascii=False, indent=2) + "\n"
        (d / f"{key}.json").write_text(text, encoding="utf-8")


def vtuple(v: str) -> tuple[int, int, int]:
    if v == NEXT:
        return (10**9, 0, 0)
    a, b, c = v.split(".")
    return int(a), int(b), int(c)


# --- 명령 ---------------------------------------------------------------------

def cmd_where(_args) -> int:
    d, mode = active_dir()
    cat = load(d)["catalog"]
    print(f"active: {d}")
    print(f"mode: {mode}")
    print(f"version: {cat['version']}  released: {cat['released']}  researched_through: {cat['researched_through']}")
    if d != BUNDLED and BUNDLED.exists():
        b = load(BUNDLED)["catalog"]
        print(f"bundled: {BUNDLED}  version: {b['version']}")
        if b["researched_through"] > cat["researched_through"]:
            print("note: 번들 카탈로그가 더 최근까지 조사됐다. `sync`로 병합을 검토한다.")
    print({
        "env": "writable: 환경변수가 가리키는 카탈로그",
        "local": "writable: 사용자 카탈로그. 갱신 후 이 폴더에서 git commit",
        "source": "writable: 플러그인 원본 저장소. 갱신 후 plugin.json 버전도 올리고 PR",
        "bundled-readonly": "read-only: 설치본. 갱신하려면 먼저 `init-local`",
    }[mode])
    return 0


def validate(cat: dict) -> tuple[list[str], list[str]]:
    errs, warns = [], []
    meta, incidents, checks = cat["catalog"], cat["incidents"], cat["checks"]

    for k in ("schema", "version", "released", "researched_through", "categories"):
        if k not in meta:
            errs.append(f"catalog.json: '{k}' 없음")
    if not SEMVER.match(str(meta.get("version", ""))):
        errs.append(f"catalog.json: version '{meta.get('version')}' 이 semver가 아님")
    cur = meta.get("version", "0.0.0")

    cats = {c["id"] for c in meta.get("categories", [])}
    if len(cats) != len(meta.get("categories", [])):
        errs.append("catalog.json: 카테고리 id 중복")

    inc_ids = set()
    for i in incidents:
        iid = i.get("id", "?")
        if iid in inc_ids:
            errs.append(f"incident {iid}: id 중복")
        inc_ids.add(iid)
        for k in ("id", "date", "region", "org", "sector", "summary", "attack_vector",
                  "root_causes", "categories", "ai_involvement", "sources", "confidence", "added_in"):
            if k not in i:
                errs.append(f"incident {iid}: '{k}' 없음")
        if not DATE.match(str(i.get("date", ""))):
            errs.append(f"incident {iid}: date '{i.get('date')}' 형식 오류(YYYY-MM 또는 YYYY-MM-DD)")
        if i.get("region") not in ("KR", "global"):
            errs.append(f"incident {iid}: region 은 KR|global")
        ai = i.get("ai_involvement", {})
        if not isinstance(ai, dict) or ai.get("level") not in AI_LEVELS or not ai.get("basis"):
            errs.append(f"incident {iid}: ai_involvement 는 {{level: {'|'.join(AI_LEVELS)}, basis: 근거}}")
        if i.get("confidence") not in CONFIDENCE:
            errs.append(f"incident {iid}: confidence 값 오류")
        srcs = i.get("sources", [])
        if not srcs or any(not s.get("url", "").startswith("http") for s in srcs):
            errs.append(f"incident {iid}: sources 에 url 이 있는 출처가 1개 이상 필요")
        for c in i.get("categories", []):
            if c not in cats:
                errs.append(f"incident {iid}: 없는 카테고리 '{c}'")
        _check_version(f"incident {iid}", i.get("added_in"), cur, errs)
        if "updated_in" in i:
            _check_version(f"incident {iid}", i["updated_in"], cur, errs)

    chk_ids, linked = set(), set()
    for c in checks:
        cid = c.get("id", "?")
        if cid in chk_ids:
            errs.append(f"check {cid}: id 중복")
        chk_ids.add(cid)
        for k in ("id", "category", "title", "severity", "method", "applies_to", "why",
                  "how_to_check", "pass_criteria", "remediation", "incidents", "added_in", "status"):
            if k not in c:
                errs.append(f"check {cid}: '{k}' 없음")
        if c.get("category") not in cats:
            errs.append(f"check {cid}: 없는 카테고리 '{c.get('category')}'")
        if not str(cid).startswith(f"{c.get('category')}/"):
            errs.append(f"check {cid}: id 는 '<category>/<slug>' 형식")
        if c.get("severity") not in SEVERITIES:
            errs.append(f"check {cid}: severity 값 오류")
        if c.get("method") not in METHODS:
            errs.append(f"check {cid}: method 값 오류")
        if c.get("status") not in STATUSES:
            errs.append(f"check {cid}: status 값 오류")
        if c.get("status") == "deprecated" and not c.get("deprecated_reason"):
            errs.append(f"check {cid}: deprecated 면 deprecated_reason 필요")
        for iid in c.get("incidents", []):
            if iid not in inc_ids:
                errs.append(f"check {cid}: 없는 사건 '{iid}'")
            linked.add(iid)
        if not c.get("incidents"):
            warns.append(f"check {cid}: 근거 사건이 없다(사건 기반 카탈로그 원칙)")
        for p in c.get("signals", {}).get("patterns", []):
            try:
                re.compile(p)
            except re.error as e:
                errs.append(f"check {cid}: 잘못된 정규식 {p!r} ({e})")
        _check_version(f"check {cid}", c.get("added_in"), cur, errs)
        if "updated_in" in c:
            _check_version(f"check {cid}", c["updated_in"], cur, errs)

    for iid in inc_ids - linked:
        warns.append(f"incident {iid}: 어떤 점검 항목도 이 사건을 참조하지 않는다")
    for cat_id in cats:
        if not any(c.get("category") == cat_id for c in checks):
            warns.append(f"category {cat_id}: 점검 항목이 없다")
    return errs, warns


def _check_version(where: str, v, cur: str, errs: list[str]) -> None:
    if v == NEXT:
        return
    if not v or not SEMVER.match(str(v)):
        errs.append(f"{where}: 버전 '{v}' 형식 오류(semver 또는 'next')")
    elif vtuple(v) > vtuple(cur):
        errs.append(f"{where}: 버전 {v} 가 카탈로그 버전 {cur} 보다 크다")


def cmd_validate(_args) -> int:
    d, _ = active_dir()
    errs, warns = validate(load(d))
    for w in warns:
        print(f"WARN  {w}")
    for e in errs:
        print(f"ERROR {e}")
    pending = _pending(load(d))
    if pending:
        print(f"INFO  릴리스 대기('next') 항목 {pending}건. 끝나면 `bump`.")
    print(f"{len(errs)} error(s), {len(warns)} warning(s)")
    return 1 if errs else 0


def _pending(cat: dict) -> int:
    n = 0
    for item in cat["incidents"] + cat["checks"]:
        n += item.get("added_in") == NEXT or item.get("updated_in") == NEXT
    return n


def cmd_stats(_args) -> int:
    cat = load(active_dir()[0])
    meta = cat["catalog"]
    print(f"catalog {meta['version']} · 사건 {len(cat['incidents'])} · 점검 {len(cat['checks'])}")
    print("\n카테고리                         사건  점검(active)")
    for c in meta["categories"]:
        ni = sum(c["id"] in i["categories"] for i in cat["incidents"])
        nc = sum(k["category"] == c["id"] and k["status"] == "active" for k in cat["checks"])
        print(f"  {c['id']:<30} {ni:>4}  {nc:>4}")
    print("\nAI 관여")
    for lv in AI_LEVELS:
        print(f"  {lv:<14} {sum(i['ai_involvement']['level'] == lv for i in cat['incidents'])}")
    print("\n지역")
    for r in ("KR", "global"):
        print(f"  {r:<14} {sum(i['region'] == r for i in cat['incidents'])}")
    return 0


# --- 대상 프로젝트 프로필 -----------------------------------------------------

# (태그, 판단 근거) — 파일 존재 또는 매니페스트 내용으로 판정한다.
PROFILE_FILES = {
    "node": ["package.json"],
    "python": ["pyproject.toml", "requirements*.txt", "Pipfile", "setup.py", "poetry.lock"],
    "java": ["pom.xml", "build.gradle", "build.gradle.kts"],
    "go": ["go.mod"],
    "ruby": ["Gemfile"],
    "php": ["composer.json"],
    "docker": ["Dockerfile", "docker-compose*.yml", "compose*.yaml"],
    "k8s": ["**/kustomization.yaml", "**/Chart.yaml"],
    "terraform": ["**/*.tf"],
    "github-actions": [".github/workflows/*.yml", ".github/workflows/*.yaml"],
    "gitlab-ci": [".gitlab-ci.yml"],
    "firebase": ["firebase.json", "firestore.rules", "database.rules.json"],
    "supabase": ["supabase/config.toml"],
    "mcp": [".mcp.json", "mcp.json", ".cursor/mcp.json", ".vscode/mcp.json"],
    "ai-agent-config": [".claude/settings.json", "CLAUDE.md", "AGENTS.md", ".cursorrules"],
}
# 매니페스트 안에 이 문자열이 있으면 태그를 붙인다.
PROFILE_DEPS = {
    "llm-app": ["openai", "anthropic", "@anthropic-ai", "langchain", "llama-index", "llama_index",
                "@ai-sdk", "\"ai\":", "google-generativeai", "@google/genai", "litellm", "transformers"],
    "mcp": ["@modelcontextprotocol", "modelcontextprotocol", "fastmcp", "mcp["],
    "web": ["express", "next", "react", "vue", "django", "flask", "fastapi", "spring-boot",
            "nestjs", "rails", "laravel", "koa", "hono", "svelte"],
    "aws": ["aws-sdk", "@aws-sdk", "boto3", "aws-cdk", "serverless"],
    "gcp": ["@google-cloud", "google-cloud-"],
    "firebase": ["firebase"],
    "supabase": ["@supabase", "supabase"],
    "crypto": ["ethers", "web3", "@solana", "viem", "wagmi", "bitcoinjs"],
}
# 매니페스트에 SDK 가 없어도 HTTP 로 직접 부르는 경우(Kotlin·Go 등)를 코드에서 찾는다.
PROFILE_CODE = {
    "llm-app": re.compile(r"generativelanguage\.googleapis\.com|api\.openai\.com|api\.anthropic\.com|"
                          r"x-goog-api-key|workers-ai|/ai/run/@cf/|bedrock-runtime|openrouter\.ai"),
}
CODE_EXT = {".kt", ".java", ".go", ".rb", ".php", ".cs", ".py", ".ts", ".js", ".rs", ".scala", ".yml", ".yaml"}
MANIFESTS = ["package.json", "pyproject.toml", "requirements.txt", "Pipfile", "pom.xml",
             "build.gradle", "build.gradle.kts", "go.mod", "Gemfile", "composer.json"]


def _walk(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            yield Path(dirpath) / f


def _rel_files(root: Path) -> list[str]:
    # 이 스킬 자신(카탈로그·스크립트)은 신호 패턴을 글자 그대로 담고 있어 스캔에서 뺀다.
    own = HERE.parent
    return [str(p.relative_to(root)) for p in _walk(root) if own not in p.parents]


def _matches(rel: str, glob: str) -> bool:
    if glob.startswith("**/"):
        return fnmatch.fnmatch(rel, glob) or fnmatch.fnmatch(Path(rel).name, glob[3:])
    return fnmatch.fnmatch(rel, glob)


def detect_profile(root: Path) -> dict[str, list[str]]:
    files = _rel_files(root)
    tags: dict[str, list[str]] = {}
    for tag, globs in PROFILE_FILES.items():
        # 모노레포(frontend/package.json, backend/build.gradle.kts)도 잡히게 파일명만으로도 맞춘다.
        hit = next((f for f in files for g in globs
                    if _matches(f, g) or ("/" not in g and fnmatch.fnmatch(Path(f).name, g))), None)
        if hit:
            tags.setdefault(tag, []).append(hit)
    manifests = [f for f in files if Path(f).name in MANIFESTS]
    for m in manifests[:50]:
        try:
            text = (root / m).read_text(encoding="utf-8", errors="ignore").lower()
        except OSError:
            continue
        for tag, needles in PROFILE_DEPS.items():
            if any(n.lower() in text for n in needles):
                tags.setdefault(tag, []).append(m)
    for tag, rx in PROFILE_CODE.items():
        if tag in tags:
            continue
        for f in files:
            if Path(f).suffix not in CODE_EXT or TEST_PATH.search(f):
                continue
            try:
                if rx.search((root / f).read_text(encoding="utf-8", errors="ignore")[:MAX_FILE_BYTES]):
                    tags.setdefault(tag, []).append(f)
                    break
            except OSError:
                continue
    tags.setdefault("any", ["(항상)"])
    return {k: sorted(set(v))[:3] for k, v in sorted(tags.items())}


def cmd_profile(args) -> int:
    prof = detect_profile(Path(args.root).resolve())
    for tag, ev in prof.items():
        print(f"{tag:<16} {', '.join(ev)}")
    print("\ntags=" + ",".join(prof))
    return 0


# --- 점검 항목 조회·스캔 ------------------------------------------------------

def select_checks(cat: dict, since: str | None, tags: list[str] | None,
                  category: str | None, include_deprecated: bool = False) -> list[dict]:
    out = []
    for c in cat["checks"]:
        if c["status"] != "active" and not include_deprecated:
            continue
        if category and c["category"] != category:
            continue
        if tags is not None:
            applies = set(c["applies_to"])
            if "any" not in applies and not applies & set(tags):
                continue
        if since:
            changed = c.get("updated_in", c["added_in"])
            newest = max(vtuple(c["added_in"]), vtuple(changed))
            if newest <= vtuple(since):
                continue
        out.append(c)
    order = {s: i for i, s in enumerate(SEVERITIES)}
    return sorted(out, key=lambda c: (order[c["severity"]], c["id"]))


def _tags_arg(args) -> list[str] | None:
    if args.tags == "auto":
        return list(detect_profile(Path(args.root).resolve()))
    return [t.strip() for t in args.tags.split(",")] if args.tags else None


def cmd_list_checks(args) -> int:
    cat = load(active_dir()[0])
    checks = select_checks(cat, args.since, _tags_arg(args), args.category, args.include_deprecated)
    if args.format == "json":
        print(json.dumps(checks, ensure_ascii=False, indent=2))
        return 0
    inc = {i["id"]: i for i in cat["incidents"]}
    print(f"# catalog {cat['catalog']['version']} · {len(checks)} checks"
          + (f" (since {args.since})" if args.since else ""))
    for c in checks:
        refs = ", ".join(f"{i} ({inc[i]['org']})" for i in c["incidents"] if i in inc)
        print(f"\n## [{c['severity']}] {c['id']} — {c['title']}  ({c['method']}, applies: {','.join(c['applies_to'])})")
        print(f"why: {c['why']}")
        print("check:")
        for s in c["how_to_check"]:
            print(f"  - {s}")
        print(f"pass: {c['pass_criteria']}")
        print(f"fix: {c['remediation']}")
        print(f"incidents: {refs}")
    return 0


def cmd_scan(args) -> int:
    """점검 항목의 signals(파일 glob·정규식)로 후보 위치를 모은다. 판정이 아니라 '여기를 읽어라'."""
    root = Path(args.root).resolve()
    cat = load(active_dir()[0])
    checks = [c for c in select_checks(cat, args.since, _tags_arg(args), args.category)
              if c.get("signals")]
    files = _rel_files(root)
    result = []
    for c in checks:
        sig = c["signals"]
        file_hits = sorted({f for f in files for g in sig.get("files", []) if _matches(f, g)})
        pat_hits = []
        pats = [re.compile(p) for p in sig.get("patterns", [])]
        scope = sig.get("pattern_files") or ["*"]
        if pats:
            for f in files:
                if Path(f).name in LOCKFILES:
                    continue
                if not args.include_tests and TEST_PATH.search(f):
                    continue
                if not any(_matches(f, g) or fnmatch.fnmatch(Path(f).name, g) for g in scope):
                    continue
                p = root / f
                try:
                    if p.stat().st_size > MAX_FILE_BYTES:
                        continue
                    lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
                except OSError:
                    continue
                for n, line in enumerate(lines, 1):
                    if any(rx.search(line) for rx in pats):
                        # 비밀값이 출력에 그대로 실리지 않게 줄 내용은 자르고 가린다.
                        pat_hits.append(f"{f}:{n}: {_redact(line.strip())[:140]}")
                        if len(pat_hits) >= MAX_HITS_PER_CHECK:
                            break
                if len(pat_hits) >= MAX_HITS_PER_CHECK:
                    break
        result.append({"id": c["id"], "severity": c["severity"],
                       "files": file_hits[:MAX_HITS_PER_CHECK], "patterns": pat_hits})
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    for r in result:
        if not r["files"] and not r["patterns"]:
            continue
        print(f"\n## {r['id']} [{r['severity']}]")
        for f in r["files"]:
            print(f"  file  {f}")
        for h in r["patterns"]:
            print(f"  match {h}")
    quiet = [r["id"] for r in result if not r["files"] and not r["patterns"]]
    if quiet:
        print(f"\n# 신호 없음 {len(quiet)}건 (신호 없음 ≠ 안전. 해당 항목은 how_to_check 대로 직접 본다)")
        for q in quiet:
            print(f"  {q}")
    return 0


# 영문과 숫자가 섞인 20자 이상 토큰만 비밀 후보로 보고 앞 6자만 남긴다.
# 긴 낱말(--dangerously-skip-permissions 등)까지 가리면 판정할 근거가 사라진다.
_TOKEN = re.compile(r"[A-Za-z0-9_\-+/=]{20,}")


def _redact(s: str) -> str:
    def cut(m):
        t = m.group(0)
        if re.search(r"\d", t) and re.search(r"[A-Za-z]", t):
            return t[:6] + "…"
        return t
    return _TOKEN.sub(cut, s)


# --- 버전 ---------------------------------------------------------------------

def cmd_bump(args) -> int:
    d, mode = active_dir()
    if mode == "bundled-readonly":
        sys.exit("설치본은 고치지 않는다. 먼저 `init-local`.")
    cat = load(d)
    errs, _ = validate(cat)
    if errs:
        sys.exit(f"validate 오류 {len(errs)}건. 먼저 고친다.")
    pending = _pending(cat)
    if args.level == "patch" and pending:
        sys.exit(f"'next' 항목 {pending}건이 있다. 사건·점검 추가·기준 변경은 minor 이상.")
    if not pending and not args.allow_empty:
        sys.exit("릴리스할 'next' 항목이 없다. 문구·출처만 고쳤으면 `bump patch --allow-empty`.")
    ma, mi, pa = vtuple(cat["catalog"]["version"])
    new = {"major": f"{ma + 1}.0.0", "minor": f"{ma}.{mi + 1}.0", "patch": f"{ma}.{mi}.{pa + 1}"}[args.level]
    added_i, added_c, updated_c = [], [], []
    for i in cat["incidents"]:
        if i.get("added_in") == NEXT:
            i["added_in"] = new
            added_i.append(i["id"])
        if i.get("updated_in") == NEXT:
            i["updated_in"] = new
    for c in cat["checks"]:
        if c.get("added_in") == NEXT:
            c["added_in"] = new
            added_c.append(c["id"])
        if c.get("updated_in") == NEXT:
            c["updated_in"] = new
            if c["id"] not in added_c:
                updated_c.append(c["id"])
    today = date.today().isoformat()
    cat["catalog"]["version"] = new
    cat["catalog"]["released"] = today
    if args.researched_through:
        cat["catalog"]["researched_through"] = args.researched_through
    save(d, cat)
    _prepend_changelog(d, new, today, args.note, added_i, added_c, updated_c)
    render(d, cat)
    print(f"{new}  사건 +{len(added_i)} · 점검 +{len(added_c)} · 점검 수정 {len(updated_c)}")
    return 0


def _prepend_changelog(d: Path, ver: str, today: str, note: str,
                       inc: list[str], add: list[str], upd: list[str]) -> None:
    p = d / "CHANGELOG.md"
    head = "# 카탈로그 변경 이력\n\n버전 규칙은 SKILL.md '버전 규칙' 참고. 최신이 위.\n"
    body = p.read_text(encoding="utf-8") if p.exists() else head
    if body.startswith(head):
        body = body[len(head):]
    lines = [f"\n## {ver} — {today}\n", f"\n{note}\n" if note else ""]
    for label, ids in (("사건 추가", inc), ("점검 추가", add), ("점검 수정", upd)):
        if ids:
            lines.append(f"\n- {label} {len(ids)}: " + ", ".join(f"`{x}`" for x in ids) + "\n")
    p.write_text(head + "".join(lines) + body, encoding="utf-8")


# --- 사람이 읽는 목록 ---------------------------------------------------------

def render(d: Path, cat: dict | None = None) -> Path:
    cat = cat or load(d)
    meta = cat["catalog"]
    inc = {i["id"]: i for i in cat["incidents"]}
    out = [f"# 점검 목록 (catalog {meta['version']})\n",
           f"\n이 파일은 `catalog.py render`가 checks.json·incidents.json에서 만든다. 직접 고치지 않는다.\n",
           f"\n- 릴리스: {meta['released']} · 조사 기준일: {meta['researched_through']}"
           f" · 사건 {len(cat['incidents'])}건 · 점검 {sum(c['status'] == 'active' for c in cat['checks'])}건\n"]
    for c in meta["categories"]:
        items = [k for k in cat["checks"] if k["category"] == c["id"] and k["status"] == "active"]
        incs = [i for i in cat["incidents"] if c["id"] in i["categories"]]
        out.append(f"\n## {c['name']} (`{c['id']}`)\n\n{c['description']}\n")
        if incs:
            out.append("\n사건: " + ", ".join(f"{i['org']}({i['date'][:7]})" for i in incs) + "\n")
        out.append("\n| 심각도 | 점검 | 방식 | 근거 사건 | 추가 |\n|---|---|---|---|---|\n")
        for k in sorted(items, key=lambda x: SEVERITIES.index(x["severity"])):
            refs = ", ".join(inc[i]["org"] for i in k["incidents"] if i in inc)
            out.append(f"| {k['severity']} | `{k['id']}` {k['title']} | {k['method']} | {refs} | {k['added_in']} |\n")
    dep = [k for k in cat["checks"] if k["status"] == "deprecated"]
    if dep:
        out.append("\n## 폐기된 점검\n\n")
        for k in dep:
            out.append(f"- `{k['id']}` {k['title']} — {k['deprecated_reason']}\n")
    p = d / "CHECKLIST.md"
    p.write_text("".join(out), encoding="utf-8")
    return p


def cmd_render(_args) -> int:
    print(render(active_dir()[0]))
    return 0


# --- 사용자 카탈로그 ----------------------------------------------------------

def cmd_init_local(_args) -> int:
    if LOCAL.exists():
        print(f"이미 있음: {LOCAL}")
        return 0
    LOCAL.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(BUNDLED, LOCAL)
    if shutil.which("git"):
        subprocess.run(["git", "init", "-q"], cwd=LOCAL, check=False)
        subprocess.run(["git", "add", "-A"], cwd=LOCAL, check=False)
        ver = load(LOCAL)["catalog"]["version"]
        subprocess.run(["git", "commit", "-q", "-m", f"catalog {ver}: 번들 카탈로그에서 시작"],
                       cwd=LOCAL, check=False)
    print(f"생성: {LOCAL} (번들 {load(LOCAL)['catalog']['version']}에서 복사)")
    return 0


def cmd_sync(args) -> int:
    """번들 → 사용자 카탈로그 병합. id 기준. 사용자 쪽에만 있는 항목은 그대로 둔다."""
    if not LOCAL.exists():
        sys.exit("사용자 카탈로그가 없다. `init-local` 먼저.")
    b, l = load(BUNDLED), load(LOCAL)
    added, conflicts = [], []
    for key in ("incidents", "checks"):
        lidx = {x["id"]: n for n, x in enumerate(l[key])}
        for item in b[key]:
            if item["id"] not in lidx:
                new = dict(item)
                new["added_in"] = NEXT
                l[key].append(new)
                added.append(item["id"])
            elif l[key][lidx[item["id"]]] != item:
                conflicts.append(item["id"])
                if args.prefer == "bundled":
                    new = dict(item)
                    new["updated_in"] = NEXT
                    l[key][lidx[item["id"]]] = new
    lcats = {c["id"] for c in l["catalog"]["categories"]}
    for c in b["catalog"]["categories"]:
        if c["id"] not in lcats:
            l["catalog"]["categories"].append(c)
            added.append(f"category:{c['id']}")
    if b["catalog"]["researched_through"] > l["catalog"]["researched_through"]:
        l["catalog"]["researched_through"] = b["catalog"]["researched_through"]
    save(LOCAL, l)
    print(f"추가 {len(added)}: {', '.join(added) or '-'}")
    print(f"충돌 {len(conflicts)} (prefer={args.prefer}): {', '.join(conflicts) or '-'}")
    if added or (conflicts and args.prefer == "bundled"):
        print("다음: validate → bump minor --note '번들 x.y.z 병합'")
    return 0


# --- main ---------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="catalog.py", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("where").set_defaults(fn=cmd_where)
    sub.add_parser("validate").set_defaults(fn=cmd_validate)
    sub.add_parser("stats").set_defaults(fn=cmd_stats)
    p = sub.add_parser("profile")
    p.add_argument("--root", default=".")
    p.set_defaults(fn=cmd_profile)
    for name, fn in (("list-checks", cmd_list_checks), ("scan", cmd_scan)):
        p = sub.add_parser(name)
        p.add_argument("--root", default=".")
        p.add_argument("--since", help="이 카탈로그 버전 이후 추가·수정된 항목만")
        p.add_argument("--tags", help="쉼표 구분 스택 태그, 또는 auto(profile 결과)")
        p.add_argument("--category")
        p.add_argument("--format", choices=("md", "json"), default="md")
        if name == "list-checks":
            p.add_argument("--include-deprecated", action="store_true")
        else:
            p.add_argument("--include-tests", action="store_true",
                           help="테스트 경로도 패턴 스캔(기본은 제외. 테스트 속 실제 비밀은 gitleaks 로 따로 본다)")
        p.set_defaults(fn=fn)
    p = sub.add_parser("bump")
    p.add_argument("level", choices=("major", "minor", "patch"))
    p.add_argument("--note", default="")
    p.add_argument("--researched-through", help="이번 조사가 덮은 마지막 날짜 YYYY-MM-DD")
    p.add_argument("--allow-empty", action="store_true")
    p.set_defaults(fn=cmd_bump)
    sub.add_parser("render").set_defaults(fn=cmd_render)
    sub.add_parser("init-local").set_defaults(fn=cmd_init_local)
    p = sub.add_parser("sync")
    p.add_argument("--prefer", choices=("local", "bundled"), default="local")
    p.set_defaults(fn=cmd_sync)
    args = ap.parse_args(argv)
    if getattr(args, "since", None) and not SEMVER.match(args.since):
        sys.exit("--since 는 semver(예: 1.0.0)")
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
