#!/usr/bin/env python3
"""wikilink [[대상]] → 마크다운 경로 링크 변환.

기본은 건식 실행이라 아무것도 쓰지 않는다. 먼저 돌려서 해석 결과를 확인하고,
미해결이 이관 때문인지 원래 없던 대상인지 판별한 뒤에 --apply 한다.

    python3 wikilink_convert.py ~/knowledge
    python3 wikilink_convert.py ~/knowledge --apply

해석 규칙 (순서대로):
  0. ./ 나 ../ 로 시작하면 링크한 문서 기준 상대경로로 먼저 푼다
  1. 경로 형태(/ 포함)면 전체 경로 목록에서 접미사 매칭
  2. 파일명 매칭 — 후보가 여럿이면 같은 디렉터리 → 같은 최상위 트리 순으로 좁힌다

하나로 정해지지 않으면 모호로 분류하고 원본을 유지한다. 임의로 고르면
조용히 틀린 링크가 생기고 사용자는 몇 달 뒤에 발견한다.
"""
import os, re, sys, collections

# 작업 상태·백업 디렉터리를 빼지 않으면 백업본이 링크 대상 후보로 잡힌다 —
# 본문 링크가 조용히 사본을 가리키게 된다.
SKIP_DIRS = {".git", ".obsidian", ".ok", "node_modules", ".venv", "__pycache__", "raw",
             ".digest", ".lint", ".backup", ".trash"}

# [[대상]] / [[대상|별칭]] / [[대상#헤딩]]
PAT = re.compile(r"\[\[([^\]|#]+)(#[^\]|]+)?(\|([^\]]+))?\]\]")

# 코드 펜스와 인라인 코드 — 안에 든 [[예시]] 는 실제 링크가 아니므로 건드리지 않는다.
# 위키 문법을 설명하는 문서에서 예시가 조용히 변환되는 사고를 막는다.
CODE = re.compile(r"(```.*?```|~~~.*?~~~|`[^`\n]*`)", re.S)


def sub_outside_code(text, repl):
    """코드 영역은 그대로 두고 나머지에만 치환을 적용한다."""
    return "".join(
        part if i % 2 else PAT.sub(repl, part)
        for i, part in enumerate(CODE.split(text))
    )


def build_index(root):
    by_base = collections.defaultdict(list)
    all_rel = []
    for dp, dn, fns in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for fn in fns:
            if not fn.endswith(".md"):
                continue
            rel = os.path.relpath(os.path.join(dp, fn), root)
            all_rel.append(rel)
            by_base[fn[:-3]].append(rel)
    return by_base, all_rel, set(all_rel)


def resolve(target, src_rel, by_base, all_rel, all_set):
    """→ 상대경로(str) | ("AMBIG", 후보들) | None"""
    t = target.strip()
    if t.endswith(".md"):
        t = t[:-3]
    srcdir = os.path.dirname(src_rel)

    # 0) 상대경로 형태는 소스 기준으로 먼저 푼다.
    #    이걸 안 하면 ../foo/bar 가 접미사 매칭에서 무조건 실패한다.
    if t.startswith("./") or t.startswith("../"):
        cand = os.path.normpath(os.path.join(srcdir, t)) + ".md"
        if cand in all_set:
            return cand
        t = t.lstrip("./")

    t = t.strip("/")

    # 1) 경로 형태 → 접미사 매칭
    if "/" in t:
        cands = [r for r in all_rel if r[:-3].endswith(t)]
        if len(cands) == 1:
            return cands[0]
        if len(cands) > 1:
            top = srcdir.split("/")[0] if srcdir else ""
            near = [c for c in cands if c.split("/")[0] == top]
            return near[0] if len(near) == 1 else ("AMBIG", cands)
        return None

    # 2) 파일명 매칭
    cands = by_base.get(t, [])
    if len(cands) == 1:
        return cands[0]
    if len(cands) > 1:
        same = [c for c in cands if os.path.dirname(c) == srcdir]
        if len(same) == 1:
            return same[0]
        top = srcdir.split("/")[0] if srcdir else ""
        near = [c for c in cands if c.split("/")[0] == top]
        if len(near) == 1:
            return near[0]
        return ("AMBIG", cands)
    return None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(1)
    root = os.path.abspath(os.path.expanduser(args[0]))
    apply_ = "--apply" in sys.argv

    by_base, all_rel, all_set = build_index(root)
    stats = collections.Counter()
    unresolved, ambiguous = [], []
    changed = 0

    for src_rel in sorted(all_rel):
        path = os.path.join(root, src_rel)
        text = open(path, encoding="utf-8").read()
        if "[[" not in text:
            continue
        srcdir = os.path.dirname(src_rel)

        def repl(m):
            target, heading, _, alias = m.groups()
            r = resolve(target, src_rel, by_base, all_rel, all_set)
            label = alias or target.strip()
            if r is None:
                stats["unresolved"] += 1
                unresolved.append(target.strip())
                return m.group(0)
            if isinstance(r, tuple):
                stats["ambiguous"] += 1
                ambiguous.append((src_rel, target.strip(), r[1]))
                return m.group(0)
            base = os.path.join(root, srcdir) if srcdir else root
            relp = os.path.relpath(os.path.join(root, r), base)
            if not relp.startswith("."):
                relp = "./" + relp
            stats["ok"] += 1
            return f"[{label}]({relp}{heading or ''})"

        new = sub_outside_code(text, repl)
        if new != text:
            changed += 1
            if apply_:
                open(path, "w", encoding="utf-8").write(new)

    print(f"{'적용' if apply_ else '건식 실행'} — 대상 파일 {changed}개")
    print(f"  변환 성공   : {stats['ok']}")
    print(f"  모호(보류)  : {stats['ambiguous']}")
    print(f"  미해결(보류): {stats['unresolved']}")

    if ambiguous:
        print("\n[모호] 같은 이름 파일이 여럿 — 원본 유지")
        for s, t, c in ambiguous[:15]:
            print(f"  {s}\n    [[{t}]] → {', '.join(c[:4])}")
    if unresolved:
        print("\n[미해결] 대상 파일 없음 — 원본 유지")
        print("  이관 누락인지 원래 없던 대상인지 원본 저장소에서 확인할 것.")
        for t, n in collections.Counter(unresolved).most_common(20):
            print(f"  [[{t}]]  ×{n}")
    if not apply_ and stats["ok"]:
        print("\n확인 후 --apply 로 적용한다.")


if __name__ == "__main__":
    main()
