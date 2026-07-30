#!/usr/bin/env python3
"""재생성 전후를 대조해 사라진 고유명사를 찾는다.

서사형으로 다듬는 과정에서 커밋 해시·PR 번호·클래스명 같은 식별자가 일반명사로
치환되는 실수가 잦다. 의미는 남지만 "어느 테이블인지" 다시 찾아야 하는 문서가 되어
원본을 열지 않아도 되게 하려던 목적이 무너진다.

    python3 lost_identifiers.py <새문서> <백업문서>      # 한 건 — 잃은 식별자와 원문 맥락
    python3 lost_identifiers.py --scan <새디렉터리> <백업디렉터리>   # 전수 — 보존율 순 목록

--scan 으로 대상을 좁히고, 건별로 돌려 나온 맥락 문장을 보며 문서에 다시 심는다.
기계적으로 끼워 넣지 말 것 — 문장 안 제자리에 들어가야 읽힌다.
"""
import os, re, sys

# 되찾아야 할 것: 다시 찾는 데 비용이 드는 고유 식별자.
# 일반 영단어를 걸러내려고 각 패턴을 좁게 잡았다.
IDENT = re.compile(
    r"\b[0-9a-f]{7,40}\b"                                        # 커밋 해시
    r"|(?<![\w/])#\d{2,5}\b"                                     # PR·이슈 번호
    r"|`[^`]{2,80}\.(?:kt|java|ts|tsx|js|py|sql|yml|yaml|md|sh|json|toml)`"  # 파일
    r"|\b[A-Z][A-Za-z]{3,}(?:Service|Controller|Repository|Test|Config|Port|Adapter|Response|Request|Entity|Handler|Publisher|Listener)\b"
    r"|\bV\d{1,4}\b"                                             # 마이그레이션 버전 (V45·V001 둘 다)
    r"|\b(?:feature|fix|hotfix|release|chore|refactor)/[\w./가-힣_-]+"        # 브랜치
    r"|\b[a-z][a-z0-9]*(?:_[a-z0-9]+){1,4}\b"                    # snake_case 테이블·컬럼
)


def idents(text):
    return {m.group(0) for m in IDENT.finditer(text)}


def context_of(text, token, width=110):
    """식별자가 등장한 문장을 돌려준다 — 어디에 다시 심을지 판단하는 근거."""
    out = []
    for m in re.finditer(re.escape(token), text):
        s = text.rfind("\n", 0, m.start()) + 1
        e = text.find("\n", m.end())
        line = text[s: e if e != -1 else len(text)].strip()
        line = re.sub(r"\s+", " ", line)
        if len(line) > width * 2:
            line = line[: width * 2] + " …"
        if line not in out:
            out.append(line)
        if len(out) >= 2:
            break
    return out


def compare(new_path, old_path):
    new = open(new_path, encoding="utf-8").read()
    old = open(old_path, encoding="utf-8").read()
    ni, oi = idents(new), idents(old)
    return old, new, oi, ni, oi - ni


def main():
    if "--scan" in sys.argv:
        i = sys.argv.index("--scan")
        newdir, olddir = sys.argv[i + 1], sys.argv[i + 2]
        rows = []
        for fn in sorted(os.listdir(os.path.expanduser(newdir))):
            if not fn.endswith(".md"):
                continue
            np = os.path.join(os.path.expanduser(newdir), fn)
            op = os.path.join(os.path.expanduser(olddir), fn)
            if not os.path.isfile(op):
                continue
            _, _, oi, ni, lost = compare(np, op)
            if len(oi) >= 5:
                rows.append((len(ni & oi) / len(oi), fn, len(oi), len(lost)))
        rows.sort()
        print(f"대조 {len(rows)}건 (식별자 5개 이상)")
        for r, fn, tot, lost in rows:
            flag = "  ← 보정 필요" if r < 0.3 else ""
            print(f"  {r*100:3.0f}%  {fn:<52} {tot:3d}개 중 {lost:3d}개 소실{flag}")
        need = [r for r in rows if r[0] < 0.3]
        print(f"\n보정 대상(보존율 30% 미만): {len(need)}건")
        return

    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    new_path, old_path = sys.argv[1], sys.argv[2]
    old, new, oi, ni, lost = compare(new_path, old_path)
    print(f"# {os.path.basename(new_path)}")
    print(f"# 식별자 {len(oi)} → {len(ni & oi)} 보존, {len(lost)} 소실\n")
    if not lost:
        print("소실 없음.")
        return
    for tok in sorted(lost):
        print(f"[{tok}]")
        for line in context_of(old, tok):
            print(f"    {line}")
        print()


if __name__ == "__main__":
    main()
