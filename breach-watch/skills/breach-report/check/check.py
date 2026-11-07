#!/usr/bin/env python3
"""breach-report 점검. 사용: python3 -I check.py <report.html>
0건이어야 사용자에게 넘긴다. 숫자가 원본 보고서와 맞는지, 말이 정말 쉬운지는 사람이 본다."""
import re
import sys
from html.parser import HTMLParser

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

# 칸별 한 줄 길이 상한(글자 수). 넘으면 둘로 나누거나 개발자용 칸으로 옮긴다.
LIMITS = {"signal": 50, "points": 60, "good": 60, "ask": 90, "node": 26, "c-title": 34}

# 개발자용 칸·용어 풀이 밖에서 쓰면 안 되는 말. 쉬운 말 표(reference/plain-words.md)로 바꾼다.
# 한글이 바로 붙어도("MFA가") 잡히게 \b 대신 영숫자 경계를 쓴다.
JARGON = re.compile(
    r"(?<![A-Za-z0-9])(IDOR|BOLA|JWT|CSP|MFA|2FA|RLS|OAuth|CVE-\d|SSO|XSS|IAM|egress|lockfile|postinstall|"
    r"Swagger|springdoc|FAIL|PARTIAL|MANUAL|PASS|N/A|critical|high|medium)(?![A-Za-z0-9])"
    r"|엔드포인트|하드코딩|크리덴셜|인가(?![가-힣])|플래그"
)
SECRET = re.compile(r"AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{30,}|sk-(proj-|ant-)?[A-Za-z0-9_-]{20,}|"
                    r"AIza[0-9A-Za-z_-]{35}|-----BEGIN [A-Z ]*PRIVATE KEY-----|xox[baprs]-[A-Za-z0-9-]{10,}")
PLACEHOLDER = re.compile(r"\{[^{}<>\n]{1,40}\}")


class Node:
    def __init__(self, tag, attrs, parent, line):
        self.tag, self.attrs, self.parent, self.line = tag, dict(attrs), parent, line
        self.children, self.parts = [], []

    @property
    def classes(self):
        return (self.attrs.get("class") or "").split()

    def text(self):
        out = []
        for p in self.parts:
            out.append(p.text() if isinstance(p, Node) else p)
        return "".join(out)

    def walk(self):
        yield self
        for c in self.children:
            yield from c.walk()

    def inside(self, pred):
        n = self.parent
        while n is not None:
            if pred(n):
                return True
            n = n.parent
        return False


class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("root", [], None, 0)
        self.cur = self.root
        self.comments = []

    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs, self.cur, self.getpos()[0])
        self.cur.children.append(n)
        self.cur.parts.append(n)
        if tag not in VOID:
            self.cur = n

    def handle_endtag(self, tag):
        n = self.cur
        while n is not None and n.tag != tag:
            n = n.parent
        if n is not None and n.parent is not None:
            self.cur = n.parent

    def handle_data(self, data):
        self.cur.parts.append(data)

    def handle_comment(self, data):
        self.comments.append(data)


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def exempt(n):
    """개발자용 칸·용어 풀이·각주·용어 표시·style 안은 쉬운 말 규칙을 적용하지 않는다."""
    def p(x):
        c = x.classes
        return (x.tag in ("details", "footer", "style", "title", "head", "small", "dl")
                and (x.tag != "details" or "dev" in c)) or "term" in c or "gloss" in c
    return p(n) or n.inside(p)


def check(path):
    html = open(path, encoding="utf-8").read()
    t = Tree()
    t.feed(html)
    errs = []

    if not any("breach-report" in c and "source:" in c and "catalog_version:" in c for c in t.comments):
        errs.append("메타 주석 <!-- breach-report source: … catalog_version: … --> 이 없다")
    # 코드 안의 {id} 같은 경로 변수는 자리표시가 아니다.
    bare = re.sub(r"<style>.*?</style>|<code>.*?</code>", "", html, flags=re.S)
    for m in PLACEHOLDER.finditer(bare):
        errs.append(f"자리표시가 남았다: {m.group(0)}")
    if SECRET.search(html):
        errs.append("비밀값처럼 보이는 문자열이 있다. 앞 6자만 남기고 지운다")

    nodes = list(t.root.walk())
    cards = [n for n in nodes if n.tag == "section" and "card" in n.classes]
    ids = {n.attrs.get("id") for n in nodes if n.attrs.get("id")}

    # 한 줄 길이
    for n in nodes:
        if exempt(n):
            continue
        key = None
        if n.tag == "li" and n.inside(lambda x: x.tag in ("ul", "ol") and (set(x.classes) & {"signal", "points", "ask"})):
            key = next(k for k in ("signal", "points", "ask") if n.inside(lambda x, k=k: k in x.classes))
        elif n.tag == "li" and n.inside(lambda x: "good" in x.classes):
            key = "good"
        elif "node" in n.classes:
            key = "node"
        elif "c-title" in n.classes:
            key = "c-title"
        if key:
            txt = norm(n.text())
            if "node" == key:
                txt = norm(re.sub(r"^(누가|구멍|피해|막음|입구|결과)", "", txt))
            if len(txt) > LIMITS[key]:
                errs.append(f"{n.line}행 .{key} {len(txt)}자 > {LIMITS[key]}자: {txt[:40]}…")

    # 긴 문단 금지
    for n in nodes:
        if n.tag == "p" and not exempt(n) and len(norm(n.text())) > 80:
            errs.append(f"{n.line}행 문단이 80자를 넘는다. 한 줄 bullet로 나눈다")

    # 낯선 말·코드 이름
    for n in nodes:
        if exempt(n) or n.tag in ("style", "script"):
            continue
        own = "".join(p for p in n.parts if isinstance(p, str))
        m = JARGON.search(own)
        if m:
            errs.append(f"{n.line}행 낯선 말 '{m.group(0)}' — 쉬운 말로 바꾸거나 <span class=\"term\">로 감싼다")
        if n.tag == "code":
            errs.append(f"{n.line}행 코드 이름은 개발자용 근거 칸(details.dev)이나 footer에만 쓴다")

    # 카드 구성
    for c in cards:
        cid = c.attrs.get("id", "?")
        sub = list(c.walk())
        flows = [x for x in sub if "flow" in x.classes]
        if not flows:
            errs.append(f"카드 #{cid}: 공격 흐름 그림(.flow)이 없다")
        for f in flows:
            if sum("node" in x.classes for x in f.walk()) < 3:
                errs.append(f"카드 #{cid}: 흐름 그림은 단계가 3개 이상이어야 한다(누가 → 구멍 → 피해)")
        lists = [x for x in sub if x.tag == "ul" and "points" in x.classes]
        if len(lists) < 2 or not any("fix" in x.classes for x in lists):
            errs.append(f"카드 #{cid}: '무슨 일이 생기나요'와 '이렇게 막아요'(.points.fix) 두 목록이 필요하다")
        if not any(x.tag == "details" and "dev" in x.classes for x in sub):
            errs.append(f"카드 #{cid}: 개발자용 근거(details.dev)가 없다")

    # 지도
    if cards and not any("map" in n.classes for n in nodes):
        errs.append("서비스 지도(.map)가 없다")
    for n in nodes:
        if "m-hit" in n.classes:
            href = (n.attrs.get("href") or "").lstrip("#")
            if href not in ids:
                errs.append(f"{n.line}행 지도 번호가 없는 카드를 가리킨다: #{href}")
    hit_targets = {(n.attrs.get("href") or "").lstrip("#") for n in nodes if "m-hit" in n.classes}
    for c in cards:
        if "c-red" in c.classes and c.attrs.get("id") not in hit_targets:
            errs.append(f"카드 #{c.attrs.get('id')}: 빨간 카드는 서비스 지도에 번호(.m-hit)로 표시한다")

    return errs


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    errs = check(sys.argv[1])
    for e in errs:
        print(f"- {e}")
    print(f"{len(errs)}건")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
