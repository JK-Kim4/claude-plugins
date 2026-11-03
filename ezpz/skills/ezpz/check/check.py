#!/usr/bin/env python3
"""ezpz 그림책 점검. 사용: python3 -I check.py <book.html>
0건이어야 게시한다. 사람이 볼 것(숫자가 원천과 맞나, 용어가 쉬운가)은 잡지 못한다."""
import re
import sys
from html.parser import HTMLParser

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
SENT_END = re.compile(r"(다|요|까)[.?!]")

# 컴포넌트별로 허용하는 수식 클래스. 다른 컴포넌트 이름이 끼면 스타일이 섞인다(2026-11-03 칩에 seat를 붙여 큰 네모로 그려짐)
MODIFIERS = {
    "chip": re.compile(r"^ch-[a-z0-9-]+$"),
    "verdict": re.compile(r"^(ok|ask|bad)$"),
    "fstep": re.compile(r"^fs-[a-z0-9-]+$"),
    "msg": re.compile(r"^msg-[a-z0-9-]+$"),
    "win-row": re.compile(r"^win-[a-z0-9-]+$"),
    "seat": re.compile(r"^[tro]$"),
    "card": re.compile(r"^(me|full|ghost)$"),
    "bitem": re.compile(r"^(ask-c|bad-c)$"),
}


class Node:
    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.parent = tag, dict(attrs), parent
        self.children, self.text = [], []
        self.line = 0

    @property
    def classes(self):
        return (self.attrs.get("class") or "").split()

    def all_text(self):
        out = list(self.text)
        for c in self.children:
            out.append(c.all_text())
        return "".join(out)

    def walk(self):
        yield self
        for c in self.children:
            yield from c.walk()

    def ancestors(self):
        p = self.parent
        while p is not None:
            yield p
            p = p.parent


class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("root", [], None)
        self.cur = self.root
        self.in_style = False

    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs, self.cur)
        n.line = self.getpos()[0]
        self.cur.children.append(n)
        if tag == "style":
            self.in_style = True
        if tag not in VOID:
            self.cur = n

    def handle_endtag(self, tag):
        if tag == "style":
            self.in_style = False
        n = self.cur
        while n is not None and n.tag != tag:
            n = n.parent
        if n is not None and n.parent is not None:
            self.cur = n.parent

    def handle_data(self, data):
        if not self.in_style:
            self.cur.text.append(data)


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def main(path):
    src = open(path, encoding="utf-8").read()
    p = P()
    p.feed(src)
    nodes = list(p.root.walk())
    issues = []

    def add(n, msg):
        issues.append(f"{n.line if n else 0}: {msg}")

    ids = {n.attrs.get("id") for n in nodes if n.attrs.get("id")}

    # 1. 개발팀 참고: li마다 라벨 하나·값 하나, 값에 여러 정보 금지
    for n in nodes:
        if n.tag == "li" and any("dev" in a.classes for a in n.ancestors()):
            ks = [c for c in n.children if "k" in c.classes]
            vs = [c for c in n.children if "v" in c.classes]
            if len(ks) != 1 or len(vs) != 1:
                add(n, f"개발팀 참고 항목은 라벨(.k) 1개·값(.v) 1개여야 함: {norm(n.all_text())[:60]}")
                continue
            v = norm(vs[0].all_text())
            if " · " in v or " / " in v or len(v) > 90:
                add(n, f"개발팀 참고 값에 정보가 여러 개로 보임(한 줄 한 정보): {v[:60]}")

    # 2. 칸 격자: 칸 수 = aria-label의 첫 수, 상자 제목의 (… N) 수와도 같게
    for n in nodes:
        if "seats" in n.classes:
            cnt = sum(1 for c in n.children if "seat" in c.classes)
            label = n.attrs.get("aria-label", "")
            m = re.search(r"(\d+)\s*(자리|칸|개|건|명)\s*중", label)
            if not m:
                add(n, f"칸 격자에 'N칸 중 …' 형식 aria-label이 없음: {label[:40]}")
            elif int(m.group(1)) != cnt:
                add(n, f"칸 격자 칸 수 {cnt} ≠ aria-label {m.group(1)}")
            box = n.parent
            cap = next((c for c in box.children if "cap" in c.classes), None) if box else None
            if cap:
                cm = re.search(r"(?:정원|전체|총)\s*(\d+)", cap.all_text())
                if cm and int(cm.group(1)) != cnt:
                    add(n, f"칸 격자 칸 수 {cnt} ≠ 제목의 수 {cm.group(1)}")

    # 3. 수식 클래스 충돌
    for n in nodes:
        cls = n.classes
        for base, ok in MODIFIERS.items():
            if base in cls:
                for c in cls:
                    if c != base and not ok.match(c):
                        add(n, f".{base}에 허용되지 않은 수식 클래스 .{c}(컴포넌트 접두사를 쓸 것)")

    # 4. 장면 문장: .lines p 하나에 한 문장
    for n in nodes:
        if n.tag == "p" and n.parent is not None and "lines" in n.parent.classes:
            t = norm(n.all_text())
            if len(SENT_END.findall(t)) > 1:
                add(n, f"이야기 한 줄에 문장이 둘 이상: {t[:60]}")

    # 5. 앵커 연결
    for n in nodes:
        href = n.attrs.get("href", "")
        if href.startswith("#") and href[1:] not in ids:
            add(n, f"없는 앵커로 연결: {href}")

    # 6. 필수 부품
    text_all = norm(p.root.all_text())
    if not any("cover" in n.classes for n in nodes):
        add(None, "표지(.cover)가 없음")
    if not any("brief" in n.classes for n in nodes):
        add(None, "표지에 '지금 확인이 필요한 N가지'(.brief)가 없음 — 확인할 것이 정말 없으면 이 줄은 무시")
    stamp = next((n for n in nodes if "stamp" in n.classes), None)
    if not stamp or not re.search(r"\d{4}-\d{2}-\d{2}", stamp.all_text()):
        add(stamp, "표지 도장(.stamp)에 YYYY-MM-DD 기준 시각이 없음")
    if not any(n.tag == "details" and "src" in n.classes for n in nodes):
        add(None, "맨 끝 '숫자와 근거'(details.src)가 없음")
    if "이 문서에 대해" in text_all:
        add(None, "'이 문서에 대해' 상자는 doc-writing 형식 — 그림책에는 표지 도장만 둔다")
    # 틀의 자리표시는 한글이 든 {…}. 코드의 {productId} 같은 영문 경로 변수는 잡지 않는다
    ph = re.search(r"\{[^{}<>]{0,40}[가-힣][^{}<>]{0,40}\}", text_all)
    if ph:
        add(None, "틀의 {자리표시}가 남아 있음: " + ph.group(0))

    # 7. 판정 알약 문구는 짧게
    for n in nodes:
        if "verdict" in n.classes and len(norm(n.all_text())) > 40:
            add(n, f"판정 알약이 김(40자 이하): {norm(n.all_text())}")

    for i in issues:
        print(i)
    print(f"ezpz check: {len(issues)}건")
    return 1 if issues else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
