#!/usr/bin/env python3
"""dlc — 개발 생명주기 스킬셋의 상태·검사 스크립트. python3 표준 라이브러리만 쓴다.

    python3 dlc.py init --profile express --slug inventory-api --description "재고 API"
    python3 dlc.py status
    python3 dlc.py next
    python3 dlc.py check requirements
    python3 dlc.py start|approve|skip requirements [--note ..] [--reason ..]
    python3 dlc.py start analyze --force     # 지문이 같아 건너뛴 분석을 다시 돌린다
    python3 dlc.py note requirements "결정 내용"

책임은 셋뿐이다. (1) state.md 전이를 도맡아 에이전트가 손으로 고치지 않게 한다.
(2) 다음 스테이지를 프로파일·워크스페이스 종류로 결정적으로 판정한다.
(3) 승인 전에 산출물의 필수 절·질문 답변·ID 연속성을 기계적으로 검사한다.

Python 3.9 이상. 표준 라이브러리만 쓴다.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

# --- 스테이지·프로파일 정의 --------------------------------------------------

STAGE_ORDER = ["init", "analyze", "intent", "practices", "requirements",
               "design", "plan", "build", "verify"]

SKILL_OF = {s: f"dlc-{s}" for s in STAGE_ORDER}

PROFILES = {
    "full": {"depth": "standard", "stages": STAGE_ORDER},
    "express": {"depth": "minimal",
                "stages": ["init", "analyze", "requirements", "plan", "build", "verify"]},
    "bugfix": {"depth": "minimal",
               "stages": ["init", "analyze", "requirements", "plan", "build", "verify"]},
}

STATUSES = ("pending", "active", "done", "skipped")

ASSUMPTIONS = "## 가정과 열린 질문"

# 산출물: (경로, 필수 H2 목록). 경로가 ".."로 시작하면 작업 폴더 밖(docs/dlc/) 프로젝트 공유 산출물.
ARTIFACTS = {
    "analyze": [("../codebase.md", ["## 개요", "## 구조", "## 기술 스택", "## 관례와 제약", ASSUMPTIONS])],
    "intent": [("intent.md", ["## 문제", "## 대상과 가치", "## 성공 지표", "## 범위", "## 타당성", ASSUMPTIONS])],
    "practices": [("../practices.md", ["## 작업 방식", "## 테스트", "## 배포", "## 코드 스타일", ASSUMPTIONS])],
    "requirements": [("requirements.md", ["## 의도 요약", "## 기능 요구사항", "## 비기능 요구사항",
                                          "## 제약", "## 범위 밖", ASSUMPTIONS])],
    "design": [("design.md", ["## 컴포넌트", "## 엔티티 소유권", "## 상호작용", ASSUMPTIONS]),
               ("decisions.md", []),
               ("units.md", ["## 유닛", "## 계약", ASSUMPTIONS])],
    "plan": [("plan.md", ["## 유닛 순서", "## Seam과 테스트 예산", "## 완료 정의", ASSUMPTIONS])],
    "verify": [("verify.md", ["## 테스트 결과", "## 추적성", "## 리뷰 발견", "## 판정", ASSUMPTIONS])],
}
BUILD_UNIT_SECTIONS = ["## 변경 파일", "## 추적성", "## 테스트", ASSUMPTIONS]

# 질문 파일이 있는 스테이지. 있으면 모든 [Answer]: 가 채워지고 요약 확인이 Looks correct 여야 한다.
QUESTION_STAGES = {"analyze", "intent", "practices", "requirements", "design", "plan"}

SOURCE_EXT = {
    ".kt": "kotlin", ".kts": "kotlin", ".java": "java", ".py": "python", ".ts": "typescript",
    ".tsx": "typescript", ".js": "javascript", ".jsx": "javascript", ".go": "go", ".rs": "rust",
    ".rb": "ruby", ".php": "php", ".cs": "csharp", ".swift": "swift", ".scala": "scala",
    ".c": "c", ".cc": "cpp", ".cpp": "cpp", ".h": "c", ".vue": "vue", ".dart": "dart",
}
BUILD_FILES = [
    ("build.gradle.kts", "gradle"), ("build.gradle", "gradle"), ("pom.xml", "maven"),
    ("pnpm-lock.yaml", "pnpm"), ("yarn.lock", "yarn"), ("package-lock.json", "npm"),
    ("bun.lock", "bun"), ("package.json", "npm"), ("pyproject.toml", "python"),
    ("requirements.txt", "pip"), ("go.mod", "go"), ("Cargo.toml", "cargo"),
    ("Gemfile", "bundler"), ("composer.json", "composer"), ("Makefile", "make"),
]
EXCLUDED_DIRS = {".git", "node_modules", "docs", "build", "dist", "out", "target", ".gradle",
                 ".idea", ".vscode", "venv", ".venv", "__pycache__", ".claude", ".codex",
                 ".agents", ".gemini", ".cursor", ".omc", "vendor", "coverage"}
SCAN_DEPTH = 4


# --- 워크스페이스 스캔 ---------------------------------------------------------

def source_files(root: Path):
    root = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        rel = Path(dirpath).relative_to(root)
        if len(rel.parts) >= SCAN_DEPTH:
            dirnames[:] = []
        dirnames[:] = sorted(d for d in dirnames if d not in EXCLUDED_DIRS and not d.startswith("."))
        for f in sorted(filenames):
            if Path(f).suffix in SOURCE_EXT and (Path(dirpath) / f).is_file():  # 끊어진 심링크 제외
                yield rel / f


def scan_workspace(root: Path):
    langs = {}
    for f in source_files(root):
        lang = SOURCE_EXT[f.suffix]
        langs[lang] = langs.get(lang, 0) + 1
    builds = [name for fname, name in BUILD_FILES if (root / fname).exists()]
    builds = list(dict.fromkeys(builds))
    kind = "brownfield" if langs else "greenfield"
    ranked = [k for k, _ in sorted(langs.items(), key=lambda kv: -kv[1])]
    return {"workspace": kind, "languages": ", ".join(ranked) or "-", "build": ", ".join(builds) or "-"}


def workspace_fingerprint(root: Path) -> str:
    """소스 파일의 경로와 내용을 함께 해시한다. 같은 소스면 PC 가 달라도 같은 값이 나온다."""
    h = hashlib.sha1()
    for f in source_files(root):
        h.update(str(f).encode("utf-8"))
        h.update(b"\0")
        h.update((root / f).read_bytes())
        h.update(b"\0")
    return h.hexdigest()[:12]


# --- 상태 파일 ----------------------------------------------------------------

@dataclass
class State:
    meta: dict = field(default_factory=dict)
    stages: dict = field(default_factory=dict)   # stage -> status
    notes: dict = field(default_factory=dict)    # stage -> note
    updated: dict = field(default_factory=dict)  # stage -> ISO 시각 (마지막 전이)

    def set(self, stage: str, status: str, note: str | None = None):
        self.stages[stage] = status
        self.updated[stage] = now_iso()
        if note is not None:
            self.notes[stage] = note


def dlc_root(root: Path) -> Path:
    return root / "docs" / "dlc"


WORK_NAME_RE = re.compile(r"^\d{6}-[a-z0-9][a-z0-9-]*$")


def cursor_path(root: Path) -> Path:
    """active 커서 파일. 심볼릭 링크면 읽지도 쓰지도 않는다 — 링크 너머의 파일을 덮어쓰지 않기 위해."""
    cursor = dlc_root(root) / "active"
    if cursor.is_symlink():
        raise SystemExit("docs/dlc/active 가 심볼릭 링크입니다. 일반 파일이어야 합니다.")
    return cursor


def no_active_message(root: Path) -> str:
    """커서만 없고 작업 폴더는 있을 수 있다(다른 PC 에서 클론). 그때는 새 작업을 만들라고 하지 않는다."""
    base = dlc_root(root)
    works = sorted(p.name for p in base.iterdir() if p.is_dir() and WORK_NAME_RE.match(p.name)) if base.is_dir() else []
    if not works:
        return "활성 작업이 없습니다. 먼저 dlc-init 스킬(또는 `dlc.py init`)로 작업을 만드세요."
    return ("활성 작업 커서(docs/dlc/active)가 없지만 작업 폴더가 있습니다: " + ", ".join(works)
            + "\n이어갈 작업 이름을 docs/dlc/active 에 한 줄로 쓰세요.")


def active_work(root: Path) -> Path:
    cursor = cursor_path(root)
    if not cursor.exists():
        raise SystemExit(no_active_message(root))
    name = cursor.read_text(encoding="utf-8").strip()
    if not WORK_NAME_RE.match(name):
        raise SystemExit(f"docs/dlc/active 의 내용 {name!r} 이(가) 작업 폴더 이름(<YYMMDD>-<slug>)이 아닙니다.")
    work = dlc_root(root) / name
    if work.resolve().parent != dlc_root(root).resolve():
        raise SystemExit(f"active 가 가리키는 {name} 이(가) docs/dlc/ 안의 폴더가 아닙니다.")
    if not (work / "state.md").exists():
        raise SystemExit(f"활성 작업 {name} 에 state.md 가 없습니다. dlc-init 으로 다시 만드세요.")
    return work


def read_state(work: Path) -> State:
    st = State()
    in_meta = True
    for line in (work / "state.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            in_meta = False
        m = re.match(r"^- (\w+): (.*)$", line) if in_meta else None
        if m:
            st.meta[m.group(1)] = m.group(2).strip()
            continue
        m = re.match(r"^\| (\w+) \| (\w+) \| ([^|]*)\|(.*)\|$", line)
        if m and m.group(1) in STAGE_ORDER:
            st.stages[m.group(1)] = m.group(2)
            st.updated[m.group(1)] = m.group(3).strip()
            st.notes[m.group(1)] = m.group(4).strip()
    profile = st.meta.get("profile")
    if profile not in PROFILES:
        raise SystemExit(f"state.md 의 profile 이 {profile!r} 입니다. 가능한 값: {', '.join(PROFILES)}. "
                         "파일이 손상됐으면 dlc-init 으로 다시 만드세요.")
    return st


def write_state(work: Path, st: State):
    for stage, status in st.stages.items():
        if status not in STATUSES:
            raise ValueError(f"알 수 없는 상태 {status!r} (stage={stage})")
    lines = ["# DLC State", "", "<!-- dlc.py 가 관리한다. 손으로 고치지 말고 start/approve/skip 을 쓴다. -->", ""]
    for k, v in st.meta.items():
        lines.append(f"- {k}: {v}")
    lines += ["", "## Stages", "", "| stage | status | updated | note |", "|---|---|---|---|"]
    for stage in STAGE_ORDER:
        if stage in st.stages:
            when = st.updated.get(stage) or now_iso()
            lines.append(f"| {stage} | {st.stages[stage]} | {when} | {st.notes.get(stage, '')} |")
    (work / "state.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(work: Path, stage: str, event: str, text: str = ""):
    p = work / "log.md"
    if not p.exists():
        p.write_text("# DLC Log\n\n", encoding="utf-8")
    with p.open("a", encoding="utf-8") as f:
        f.write(f"- {now_iso()} | {stage} | {event} | {text}\n")


# --- 다음 스테이지 판정 ---------------------------------------------------------

def analyze_is_current(root: Path) -> bool:
    p = dlc_root(root) / "codebase.md"
    if not p.exists():
        return False
    m = re.search(r"<!-- fingerprint: (\w+) -->", p.read_text(encoding="utf-8"))
    return bool(m and m.group(1) == workspace_fingerprint(root))


def next_stage(root: Path, st: State):
    for stage in PROFILES[st.meta["profile"]]["stages"]:
        status = st.stages.get(stage, "pending")
        if status in ("done", "skipped"):
            continue
        if stage == "analyze" and status == "pending" and analyze_is_current(root):
            continue
        return stage
    return None


# --- 검사 ----------------------------------------------------------------------

# FR1 / FR1.2 / NFR3 / NFR3.1 — (kind, top, sub|None)
ANY_ID_RE = re.compile(r"\b(NFR|FR)(\d+)(?:\.(\d+))?\b")
DEFINITION_SECTIONS = ("## 기능 요구사항", "## 비기능 요구사항")
REFERENCE_STAGES = {"design", "plan", "build", "verify"}
UNIT_ROW_RE = re.compile(r"^\|\s*(u\d+-[a-z0-9][a-z0-9-]*)\s*\|([^|]*)\|([^|]*)\|([^|]*?)\|?\s*$")
FINGERPRINT_RE = re.compile(r"<!-- fingerprint: (\w+) -->")


def h2_sections(text: str):
    return [ln.strip() for ln in text.splitlines() if ln.startswith("## ")]


def section_body(text: str, heading: str) -> str:
    lines = text.splitlines()
    out, on = [], False
    for ln in lines:
        if ln.startswith("## "):
            on = ln.strip() == heading
            continue
        if on:
            out.append(ln)
    return "\n".join(out).strip()


def check_sections(path: Path, required, problems):
    if not path.exists():
        problems.append(f"{path.name}: 파일이 없습니다")
        return None
    text = path.read_text(encoding="utf-8")
    have = set(h2_sections(text))
    for h in required:
        if h not in have:
            problems.append(f"{path.name}: 필수 절 '{h[3:]}' 이(가) 없습니다")
    if ASSUMPTIONS in required and ASSUMPTIONS in have and not section_body(text, ASSUMPTIONS):
        problems.append(f"{path.name}: '가정과 열린 질문' 절이 비어 있습니다 (없으면 None. 이라고 쓰세요)")
    return text


def question_blocks(text: str):
    """(제목, 본문) 목록. 제목은 '## ' 을 뗀 것."""
    blocks, title, body = [], None, []
    for ln in text.splitlines():
        if ln.startswith("## "):
            if title is not None:
                blocks.append((title, body))
            title, body = ln[3:].strip(), []
        else:
            body.append(ln)
    if title is not None:
        blocks.append((title, body))
    return blocks


def answer_of(body):
    """블록의 [Answer]: 값. 행이 없으면 None, 비어 있으면 ''."""
    for ln in body:
        m = re.match(r"^\[Answer\]:\s*(.*)$", ln)
        if m:
            return m.group(1).strip()
    return None


def check_questions(path: Path, problems):
    if not path.exists():
        return
    numbers, summary = [], None
    for title, body in question_blocks(path.read_text(encoding="utf-8")):
        m = re.match(r"^(Q(\d+))\b(\.?)", title)
        if m and not m.group(3):
            problems.append(f"{path.name}: {m.group(1)} 제목은 `## {m.group(1)}.` 처럼 번호 뒤에 점을 찍어야 합니다")
        if m:
            numbers.append(int(m.group(2)))
            answer = answer_of(body)
            if answer is None:
                problems.append(f"{path.name}: {m.group(1)} 에 [Answer]: 행이 없습니다")
            elif not answer:
                problems.append(f"{path.name}: {m.group(1)} 답변이 비어 있습니다")
        elif title == "Consolidated Summary Confirmation":
            summary = answer_of(body)
    missing = sorted(set(range(1, max(numbers, default=0) + 1)) - set(numbers))
    if missing:
        problems.append(f"{path.name}: 질문 번호가 비었습니다 — " + ", ".join(f"Q{n}" for n in missing))
    if summary != "Looks correct":
        problems.append(f"{path.name}: 요약 확인 답변이 정확히 'Looks correct' 여야 합니다")


def ids_in(text: str):
    """텍스트에 나오는 모든 ID 문자열 — 'FR1', 'FR1.2', 'NFR3'."""
    return {f"{k}{n}" + (f".{sub}" if sub else "") for k, n, sub in ANY_ID_RE.findall(text)}


def top_numbers(ids, kind: str):
    return {int(i[len(kind):]) for i in ids if i.startswith(kind) and "." not in i and i[len(kind):].isdigit()}


def definition_text(text: str) -> str:
    return "\n".join(section_body(text, h) for h in DEFINITION_SECTIONS)


def check_id_continuity(text: str, name: str, problems):
    ids = ids_in(definition_text(text))
    for kind in ("FR", "NFR"):
        nums = top_numbers(ids, kind)
        parents = {int(i[len(kind):].split(".")[0]) for i in ids if i.startswith(kind) and "." in i}
        orphans = sorted(parents - nums)
        if orphans:
            problems.append(f"{name}: 하위 ID 의 상위 {kind} 가 없습니다 — " + ", ".join(f"{kind}{n}" for n in orphans))
        missing = sorted(set(range(1, max(nums, default=0) + 1)) - nums)
        if missing:
            problems.append(f"{name}: {kind} 번호가 비었습니다 — " + ", ".join(f"{kind}{n}" for n in missing))


def requirement_ids(work: Path):
    """requirements.md 의 정의 절에서 뽑은 ID 집합(하위 ID 포함). 파일이 없으면 None."""
    p = work / "requirements.md"
    if not p.exists():
        return None
    return ids_in(definition_text(p.read_text(encoding="utf-8")))


def check_references(text: str, name: str, known, problems):
    if known is None:
        return
    unknown = sorted(ids_in(text) - known)
    if unknown:
        problems.append(f"{name}: requirements.md 에 없는 ID 를 참조합니다 — " + ", ".join(unknown))


def units_table(work: Path):
    p = work / "units.md"
    if not p.exists():
        return []
    rows = []
    for ln in section_body(p.read_text(encoding="utf-8"), "## 유닛").splitlines():
        m = UNIT_ROW_RE.match(ln)
        if m:
            rows.append({"unit": m.group(1), "kind": m.group(2).strip(),
                         "depends_on": m.group(3).strip(), "covers": m.group(4).strip()})
    return rows


def check_units_coverage(work: Path, known, problems):
    if known is None:
        return
    covered = set()
    for u in units_table(work):
        covered |= {i.split(".")[0] for i in ids_in(u["covers"])}  # 하위 ID 를 맡으면 상위도 덮은 것
    gaps = sorted(i for i in known - covered if "." not in i)
    if gaps:
        problems.append("units.md: 어느 유닛도 맡지 않은 요구사항 — " + ", ".join(gaps))


def check_analyze_fingerprint(root: Path, text: str, problems):
    m = FINGERPRINT_RE.search(text)
    if not m:
        problems.append("codebase.md: `<!-- fingerprint: <값> -->` 주석이 없습니다 (없으면 다음 작업마다 analyze 가 다시 뜹니다)")
    elif m.group(1) != workspace_fingerprint(root):
        problems.append(f"codebase.md: fingerprint 가 현재 소스와 다릅니다. 분석을 갱신하고 "
                        f"`<!-- fingerprint: {workspace_fingerprint(root)} -->` 로 적으세요")


def check_build(work: Path, known, problems):
    units = units_table(work)
    if not units:
        problems.append("units.md: 유닛 표를 읽을 수 없습니다 (## 유닛 절의 `| u<n>-<slug> | kind | depends_on | covers |` 행)")
    for u in units:
        path = work / "build" / f"{u['unit']}.md"
        text = check_sections(path, BUILD_UNIT_SECTIONS, problems)
        if text is not None:
            check_references(text, path.name, known, problems)


def check_stage(root: Path, work: Path, stage: str):
    problems = []
    known = requirement_ids(work)
    artifacts = list(ARTIFACTS.get(stage, []))
    if stage == "build":
        check_build(work, known, problems)
        return problems
    plan_owns_units = stage == "plan" and read_state(work).stages.get("design") in (None, "skipped")
    if plan_owns_units:
        artifacts += [a for a in ARTIFACTS["design"] if a[0] == "units.md"]
    for rel, required in artifacts:
        path = (dlc_root(root) / rel[3:]) if rel.startswith("../") else (work / rel)
        text = check_sections(path, required, problems)
        if text is None:
            continue
        if stage == "requirements":
            check_id_continuity(text, path.name, problems)
        elif stage == "analyze":
            check_analyze_fingerprint(root, text, problems)
        elif stage in REFERENCE_STAGES:
            check_references(text, path.name, known, problems)
    if stage == "design" or plan_owns_units:
        check_units_coverage(work, known, problems)
    if stage in QUESTION_STAGES:
        check_questions(work / f"{stage}-questions.md", problems)
    return problems


# --- 명령 ----------------------------------------------------------------------

def cmd_init(a):
    root = Path(a.root).resolve()
    if a.profile not in PROFILES:
        raise SystemExit(f"알 수 없는 프로파일 {a.profile!r}. 가능한 값: {', '.join(PROFILES)}")
    if not re.match(r"^[a-z0-9][a-z0-9-]*$", a.slug):
        raise SystemExit("slug 는 소문자·숫자·하이픈만 가능합니다")
    name = f"{datetime.now().strftime('%y%m%d')}-{a.slug}"
    work = dlc_root(root) / name
    if work.exists():
        raise SystemExit(f"{work.relative_to(root)} 이(가) 이미 있습니다. 다른 slug 를 쓰거나 기존 작업을 이어가세요.")
    cursor_path(root)  # 심볼릭 링크면 폴더를 만들기 전에 거부
    scan = scan_workspace(root)
    profile = PROFILES[a.profile]
    st = State()
    description = re.sub(r"\s*\n\s*", " ", a.description).strip() or "-"  # 한 줄이어야 메타 문법과 안 섞인다
    st.meta = {"profile": a.profile, "depth": profile["depth"], "description": description,
               "created": now_iso(), **scan, "fingerprint": workspace_fingerprint(root)}
    for stage in profile["stages"]:
        st.set(stage, "pending", "")
    st.set("init", "done")
    if scan["workspace"] == "greenfield":
        st.set("analyze", "skipped", "greenfield")
    work.mkdir(parents=True)
    write_state(work, st)
    cursor_path(root).write_text(name + "\n", encoding="utf-8")
    log(work, "init", "created", f"profile={a.profile} workspace={scan['workspace']}")
    print(f"작업 폴더: {work.relative_to(root)}")
    for k in ("profile", "depth", "workspace", "languages", "build"):
        print(f"- {k}: {st.meta[k]}")
    return 0


def cmd_status(a):
    root = Path(a.root).resolve()
    work = active_work(root)
    st = read_state(work)
    print(f"작업: {work.name}  ({st.meta.get('description', '-')})")
    for k in ("profile", "depth", "workspace", "languages", "build"):
        print(f"- {k}: {st.meta.get(k, '-')}")
    print()
    for stage in STAGE_ORDER:
        if stage in st.stages:
            note = f"  ({st.notes[stage]})" if st.notes.get(stage) else ""
            print(f"  {stage:13} {st.stages[stage]}{note}")
    nxt = next_stage(root, st)
    print()
    print("다음: " + (f"{nxt} → {SKILL_OF[nxt]}" if nxt else "done"))
    return 0


def cmd_next(a):
    root = Path(a.root).resolve()
    st = read_state(active_work(root))
    nxt = next_stage(root, st)
    if nxt is None:
        print("done")
    else:
        print(f"{nxt} {SKILL_OF[nxt]}")
        print(f"depth: {st.meta.get('depth')}  profile: {st.meta.get('profile')}  workspace: {st.meta.get('workspace')}")
    return 0


def cmd_check(a):
    root = Path(a.root).resolve()
    work = active_work(root)
    problems = check_stage(root, work, a.stage)
    if problems:
        print(f"check {a.stage}: {len(problems)}건")
        for p in problems:
            print(f"- {p}")
        return 1
    print(f"check {a.stage}: OK")
    return 0


def require_in_profile(st: State, stage: str):
    if stage not in st.stages:
        raise SystemExit(f"{stage} 은(는) 이 프로파일({st.meta['profile']})에 없는 스테이지입니다.")


def require_is_next(root: Path, st: State, stage: str, verb: str):
    require_in_profile(st, stage)
    nxt = next_stage(root, st)
    if nxt is None:
        raise SystemExit(f"모든 스테이지가 끝났습니다. {verb}할 스테이지가 없습니다.")
    if stage != nxt:
        raise SystemExit(f"지금 {verb}할 스테이지는 {nxt} 입니다 ({stage} 아님, 현재 {st.stages[stage]}).")


def require_forceable(st: State, stage: str):
    """--force 는 지문 일치로 건너뛴 analyze 를 다시 돌리는 용도뿐이다."""
    if stage != "analyze":
        raise SystemExit("--force 는 analyze 에만 쓸 수 있습니다 (지문이 같아 건너뛴 분석을 다시 돌릴 때).")
    require_in_profile(st, stage)
    if st.meta.get("workspace") != "brownfield":
        raise SystemExit("greenfield 작업에는 분석할 코드가 없습니다.")
    if st.stages[stage] != "pending":
        raise SystemExit(f"analyze 가 이미 {st.stages[stage]} 입니다.")


def cmd_start(a):
    root = Path(a.root).resolve()
    work = active_work(root)
    st = read_state(work)
    if a.force:
        require_forceable(st, a.stage)
    else:
        require_is_next(root, st, a.stage, "시작")
    st.set(a.stage, "active")
    write_state(work, st)
    log(work, a.stage, "start", a.note or "")
    print(f"{a.stage}: active")
    return 0


def cmd_approve(a):
    root = Path(a.root).resolve()
    work = active_work(root)
    st = read_state(work)
    require_is_next(root, st, a.stage, "승인")
    if st.stages[a.stage] != "active":
        raise SystemExit(f"{a.stage} 은(는) 아직 시작하지 않았습니다. 먼저 `dlc.py start {a.stage}` 를 실행하세요.")
    problems = check_stage(root, work, a.stage)
    if problems:
        sys.stderr.write(f"승인 거부 — check {a.stage} 실패 {len(problems)}건:\n" + "".join(f"- {p}\n" for p in problems))
        return 1
    st.set(a.stage, "done")
    write_state(work, st)
    log(work, a.stage, "approve", a.note or "")
    nxt = next_stage(root, st)
    print(f"{a.stage}: done")
    print("다음: " + (f"{nxt} → {SKILL_OF[nxt]}" if nxt else "done"))
    return 0


def cmd_skip(a):
    root = Path(a.root).resolve()
    work = active_work(root)
    st = read_state(work)
    require_in_profile(st, a.stage)
    reason = a.reason.strip()
    if not reason:
        raise SystemExit("skip 사유(--reason)가 비어 있습니다. 왜 건너뛰는지 한 줄로 적으세요.")
    if st.stages[a.stage] not in ("pending", "active"):
        raise SystemExit(f"{a.stage} 은(는) 이미 {st.stages[a.stage]} 라서 건너뛸 수 없습니다.")
    st.set(a.stage, "skipped", reason)
    write_state(work, st)
    log(work, a.stage, "skip", reason)
    print(f"{a.stage}: skipped ({reason})")
    return 0


def cmd_note(a):
    root = Path(a.root).resolve()
    work = active_work(root)
    log(work, a.stage, "note", a.text)
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="dlc.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".", help="프로젝트 루트 (기본: 현재 디렉터리)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    # 서브명령 뒤에도 --root 를 허용한다. 기본값을 SUPPRESS 로 두어 앞에서 받은 값을 덮지 않는다.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--root", default=argparse.SUPPRESS, help=argparse.SUPPRESS)

    p = sub.add_parser("init", help="작업 폴더와 state.md 생성", parents=[common])
    p.add_argument("--profile", required=True)
    p.add_argument("--slug", required=True)
    p.add_argument("--description", default="")
    p.set_defaults(fn=cmd_init)

    sub.add_parser("status", help="현재 작업과 스테이지 상태", parents=[common]).set_defaults(fn=cmd_status)
    sub.add_parser("next", help="다음 스테이지와 스킬 이름", parents=[common]).set_defaults(fn=cmd_next)

    p = sub.add_parser("check", help="스테이지 산출물 검사", parents=[common])
    p.add_argument("stage", choices=STAGE_ORDER)
    p.set_defaults(fn=cmd_check)

    p = sub.add_parser("start", help="스테이지 시작 기록", parents=[common])
    p.add_argument("stage", choices=STAGE_ORDER)
    p.add_argument("--note", default="")
    p.add_argument("--force", action="store_true", help="지문이 같아 건너뛴 analyze 를 다시 돌린다")
    p.set_defaults(fn=cmd_start)

    p = sub.add_parser("approve", help="승인 기록 (check 통과 필요)", parents=[common])
    p.add_argument("stage", choices=STAGE_ORDER)
    p.add_argument("--note", default="")
    p.set_defaults(fn=cmd_approve)

    p = sub.add_parser("skip", help="스테이지 건너뛰기 (사유 필수)", parents=[common])
    p.add_argument("stage", choices=STAGE_ORDER)
    p.add_argument("--reason", required=True)
    p.set_defaults(fn=cmd_skip)

    p = sub.add_parser("note", help="로그에 결정·메모 추가", parents=[common])
    p.add_argument("stage", choices=STAGE_ORDER)
    p.add_argument("text")
    p.set_defaults(fn=cmd_note)

    a = ap.parse_args(argv)
    try:
        return a.fn(a)
    except SystemExit as e:
        if isinstance(e.code, str):
            sys.stderr.write(e.code + "\n")
            return 2
        raise


if __name__ == "__main__":
    sys.exit(main())
