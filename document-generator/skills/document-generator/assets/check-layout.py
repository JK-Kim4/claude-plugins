#!/usr/bin/env python3
"""생성한 HTML 문서의 한글 레이아웃 넘침을 정적으로 점검한다 (의존성 없음).

    python3 <스킬경로>/assets/check-layout.py report.html

한글 글자는 폭이 영문의 약 1.7배라, 영문 기준으로 잡은 SVG 박스·표 열은 한글을 넣으면
넘친다. SVG 밖으로 나간 텍스트는 경고 없이 잘려 사라지므로 눈으로는 놓치기 쉽다.
이 스크립트는 그 넘침을 좌표로 계산해 잡아낸다.
발견 사항이 있으면 종료코드 1.
"""
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path


def tag_of(el):
    """인라인 SVG 는 xmlns 가 없고 렌더된 SVG 는 있다 — 둘 다 로컬 태그명으로 본다."""
    return el.tag.split("}")[-1]


def text_width(s, font_size):
    """근사 렌더 폭(px). 계수는 document.css 폰트 스택에서 실측해 보정한 값(오차 2% 안)."""
    total = 0.0
    for ch in s:
        if ch == " ":
            total += 0.27
        elif unicodedata.east_asian_width(ch) in ("W", "F"):
            total += 0.87  # 한글·한자·가나
        elif ch.isdigit():
            total += 0.60
        elif ch.isupper():
            total += 0.67
        elif ch in "/-.,:;'\"|!()[]":
            total += 0.33
        else:
            total += 0.52
    return total * font_size


def check_svgs(html, findings):
    for raw in re.findall(r"<svg\b.*?</svg>", html, re.S):
        try:
            svg = ET.fromstring(raw)
        except ET.ParseError as e:
            findings.append(f"SVG 파싱 실패 — 태그가 닫히지 않았을 수 있다: {e}")
            continue
        # Mermaid 렌더 산출물은 실측 레이아웃이라 검사 대상이 아니다
        if any(tag_of(e) == "style" or (tag_of(e) == "g" and (e.get("class") or "").startswith("node"))
               for e in svg.iter()):
            continue
        vb = (svg.get("viewBox") or "").split()
        if len(vb) != 4:
            findings.append("SVG 에 viewBox 가 없다 — 반응형 크기 조절이 되지 않는다")
            continue
        vx, vw = float(vb[0]), float(vb[2])

        for group in [svg] + [e for e in svg.iter() if tag_of(e) == "g"]:
            rects = [r for r in group if tag_of(r) == "rect" and r.get("width")]
            for t in [c for c in group if tag_of(c) == "text"]:
                fs = float(t.get("font-size", 14))
                anchor = t.get("text-anchor", "start")
                # tspan 은 줄바꿈이다 — 합쳐 재면 실제보다 넓게 나온다. 줄별로 재고 가장 넓은 줄을 쓴다
                spans = [c for c in t if tag_of(c) == "tspan"]
                lines = [(" ".join("".join(s.itertext()).split()), float(s.get("x", t.get("x", 0)))) for s in spans]
                if not spans:
                    lines = [(" ".join("".join(t.itertext()).split()), float(t.get("x", 0)))]
                lines = [(txt, lx) for txt, lx in lines if txt]
                if not lines:
                    continue

                widest = max(lines, key=lambda ln: text_width(ln[0], fs))
                label, x = widest
                w = text_width(label, fs)
                x0 = x - w / 2 if anchor == "middle" else (x - w if anchor == "end" else x)
                x1 = x0 + w

                short = label[:30] + ("…" if len(label) > 30 else "")
                if len(label) > 28:
                    findings.append(
                        f'SVG 텍스트가 한 줄에 문장을 담았다 ({len(label)}자) — figcaption/본문으로 옮긴다: "{short}"'
                    )
                if x0 < vx - 0.5 or x1 > vx + vw + 0.5:
                    findings.append(
                        f'SVG 텍스트가 viewBox 를 벗어나 잘린다: "{short}" '
                        f"(텍스트 {x0:.0f}~{x1:.0f}px, viewBox {vx:.0f}~{vx + vw:.0f}px)"
                    )
                for r in rects:
                    rx, rw = float(r.get("x", 0)), float(r.get("width"))
                    ry, rh = float(r.get("y", 0)), float(r.get("height", 0))
                    y = float(t.get("y", 0))
                    # 기준점이 박스 안에 있는 텍스트만 그 박스 소속으로 본다
                    # (차트의 축·값 라벨은 막대 밖에 두는 것이 정상이다)
                    if not (ry - 2 <= y <= ry + rh + 2 and rx <= x <= rx + rw):
                        continue
                    if x0 < rx - 0.5 or x1 > rx + rw + 0.5:
                        findings.append(
                            f'SVG 텍스트가 박스를 벗어난다: "{short}" '
                            f"(텍스트 {x0:.0f}~{x1:.0f}px, 박스 {rx:.0f}~{rx + rw:.0f}px, "
                            f"{fs:.0f}px 한글 최대 {int((rw - 16) / fs)}자)"
                        )


def check_tables(html, findings):
    for i, table in enumerate(re.findall(r"<table\b.*?</table>", html, re.S), 1):
        rows = re.findall(r"<tr\b.*?</tr>", table, re.S)
        cols = max((len(re.findall(r"<t[hd]\b", r)) for r in rows), default=0)
        if cols > 4:
            findings.append(f"표 {i}: 열이 {cols}개 — 한글 표는 4열 이하로 줄이고 긴 서술은 표 밖으로 뺀다")

    wrapped = len(re.findall(r'class="[^"]*table-wrap', html))
    total = len(re.findall(r"<table\b", html))
    if total > wrapped:
        findings.append(f'표 {total}개 중 {total - wrapped}개가 <div class="table-wrap"> 로 감싸이지 않았다')


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    html = Path(sys.argv[1]).read_text()
    findings = []
    check_svgs(html, findings)
    check_tables(html, findings)

    if not findings:
        print("레이아웃 점검 통과 — 넘침 없음")
        return 0
    print(f"발견 {len(findings)}건:")
    for f in findings:
        print(f"  - {f}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
