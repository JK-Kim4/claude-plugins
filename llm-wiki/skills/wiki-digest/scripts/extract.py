#!/usr/bin/env python3
"""세션 JSONL에서 요약에 필요한 것만 뽑는다.

원본은 수 MB 라 통째로 읽으면 컨텍스트가 망가진다. 이 스크립트가 그 규율을
강제한다 — 출력은 항상 상한이 걸려 있고, 도구 호출 원문은 버린다.

    python3 extract.py <session.jsonl>
    python3 extract.py <session.jsonl> --max-chars 30000
    python3 extract.py <session.jsonl> --meta-only     # 판별용 메타만

Claude Code 와 Codex 는 스키마가 완전히 다르다. 첫 줄을 보고 자동 판별한다.
"""
import json, os, re, sys

# 사용자 발화로 위장한 시스템 주입 — 세션의 실제 요청이 아니므로 버린다.
NOISE = re.compile(
    r"^\s*(<command-|<local-command|<task-notification|<system-reminder|"
    r"Caveat:|# AGENTS\.md instructions|<INSTRUCTIONS>)"
)

IDENT = re.compile(
    r"\b([0-9a-f]{7,40})\b"                      # 커밋 해시
    r"|\b((?:feature|fix|hotfix|release)/[\w./-]+)"  # 브랜치
    r"|\b(V\d{1,3})\b"                           # Flyway 버전 등
)


def read_lines(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue


CODEX_TYPES = {"session_meta", "response_item", "event_msg", "turn_context"}
# 대화 항목(user/assistant)은 파일 앞부분에 없을 수 있다 — 실제로 메타데이터가
# 수십 줄 먼저 오는 세션이 있다. Claude Code 고유의 메타 타입도 판별 근거로 쓴다.
CLAUDE_TYPES = {"user", "assistant", "summary", "last-prompt", "permission-mode",
                "mode", "ai-title", "attachment", "file-history-snapshot"}


def detect(path):
    """claude | codex | unknown"""
    for i, obj in enumerate(read_lines(path)):
        t = obj.get("type")
        if t in CODEX_TYPES:
            return "codex"
        if t in CLAUDE_TYPES:
            return "claude"
        if i > 50:
            break
    return "unknown"


def _text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            b.get("text", "") for b in content
            if isinstance(b, dict) and b.get("type") in ("text", "input_text", "output_text")
        )
    return ""


def parse_claude(path):
    users, assists = [], []
    for obj in read_lines(path):
        t = obj.get("type")
        if t == "user":
            s = _text_of((obj.get("message") or {}).get("content"))
            if s and not NOISE.match(s):
                users.append(s.strip())
        elif t == "assistant":
            s = _text_of((obj.get("message") or {}).get("content"))
            if s.strip():
                assists.append(s.strip())
    return users, assists


def parse_codex(path):
    """event_msg 쪽이 순수 텍스트라 response_item 보다 깨끗하다."""
    users, assists = [], []
    for obj in read_lines(path):
        if obj.get("type") != "event_msg":
            continue
        p = obj.get("payload") or {}
        msg = (p.get("message") or "").strip()
        if not msg or NOISE.match(msg):
            continue
        if p.get("type") == "user_message":
            users.append(msg)
        elif p.get("type") == "agent_message":
            assists.append(msg)
    return users, assists


def codex_cwd(path):
    for obj in read_lines(path):
        p = obj.get("payload") or {}
        cwd = p.get("cwd") or obj.get("cwd")
        if cwd:
            return cwd
        if obj.get("type") not in ("session_meta", "turn_context"):
            break
    return None


def sample(items, budget):
    """앞뒤 위주로 담는다 — 세션의 시작(요청)과 끝(결말)이 가장 정보가 많다.

    **뒤쪽 몫을 먼저 떼어 둔다.** 앞에서부터 예산을 다 쓰면 결말이 통째로 사라지는데,
    그러면 "무엇을 남겼나 / 어디로 이어지나"를 쓸 근거가 없어진다. 실제로 그렇게
    잘린 문서가 나왔다(SKILL.md 의 재생성 주의 참고).
    """
    if sum(len(s) for s in items) <= budget:
        return list(items)
    head, used = [], 0
    for s in items:
        if used + len(s) > budget // 2:      # 앞은 예산의 절반까지만
            break
        head.append(s); used += len(s)
    tail = []
    for s in reversed(items[len(head):]):
        if used + len(s) > budget:
            break
        tail.append(s); used += len(s)
    return head + ["…"] + list(reversed(tail))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__); sys.exit(1)
    path = os.path.expanduser(args[0])
    if not os.path.isfile(path):
        print(f"파일 없음: {path}"); sys.exit(1)

    max_chars = 40000
    if "--max-chars" in sys.argv:
        i = sys.argv.index("--max-chars")
        if i + 1 < len(sys.argv):
            max_chars = int(sys.argv[i + 1])

    tool = detect(path)
    size = os.path.getsize(path)
    print(f"# 원본: {path}")
    print(f"# 도구: {tool}   크기: {size/1024/1024:.1f}MB")
    if tool == "codex":
        cwd = codex_cwd(path)
        if cwd:
            print(f"# cwd: {cwd}")

    if "--meta-only" in sys.argv:
        return

    if tool == "claude":
        users, assists = parse_claude(path)
    elif tool == "codex":
        users, assists = parse_codex(path)
    else:
        print("# 알 수 없는 스키마 — 수동 확인 필요"); sys.exit(2)

    print(f"# 사용자 발화 {len(users)}건 / 어시스턴트 응답 {len(assists)}건\n")

    # 사용자 발화가 세션의 뼈대다 — 예산의 절반 이상을 준다.
    print("## 사용자 발화")
    for s in sample(users, int(max_chars * 0.55)):
        print(f"\n---\n{s}")

    print("\n\n## 어시스턴트 응답 (표본)")
    for s in sample(assists, int(max_chars * 0.35)):
        print(f"\n---\n{s[:2000]}")

    idents = set()
    for s in users + assists:
        for m in IDENT.finditer(s):
            idents.add(next(g for g in m.groups() if g))
    if idents:
        print("\n\n## 식별자 후보 (커밋·브랜치·버전)")
        print(", ".join(sorted(idents)[:40]))


if __name__ == "__main__":
    main()
