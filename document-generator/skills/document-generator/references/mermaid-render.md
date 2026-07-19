# Mermaid 정적 렌더 가이드

구조·관계 다이어그램을 **Mermaid 문법으로 기술하고, 생성 시점에 정적 SVG로 렌더해 문서에 인라인 임베드**하는 방법. 좌표를 손으로 계산하지 않으므로 박스 겹침·화살표 어긋남·텍스트 삐져나옴이 원천적으로 없다.

**핵심: 렌더는 생성 시점에 한 번만 한다.** 완성된 문서에는 SVG만 남고 JavaScript도 CDN 링크도 없다 — `html-output.md`의 자기완결 불변식이 그대로 유지되고, 오프라인·인쇄·장기 보관에서 깨지지 않는다. **문서에 Mermaid CDN 스크립트를 넣지 않는다.**

## 1. 어느 쪽을 쓸 것인가

| 표현 대상 | 방식 |
|---|---|
| 아키텍처·컴포넌트 구조, 시퀀스/흐름, 상태 전이, ER | **Mermaid** — 자동 레이아웃이 정확하다 |
| 데이터 차트(막대·선) | **hand-SVG** (`diagrams.md` 5번) — Mermaid의 xychart 은 미성숙하고 값 라벨 제어가 어렵다 |
| Before/After 비교 쌍 | **hand-SVG** (`diagrams.md` 6번) — 두 그림의 축척을 강제로 맞춰야 하는데 자동 레이아웃은 그걸 보장하지 않는다 |
| 툴체인을 쓸 수 없는 환경 | **hand-SVG** — 아래 5절 폴백 |

**Mermaid는 정확할 뿐 아니라 싸다.** 같은 그림 하나를 표현하는 데 Mermaid 소스는 약 100자인 반면 hand-SVG는 약 1,400자로 **13배 이상** 든다. graph 형태 그림을 손으로 그리는 것은 정확도와 비용을 동시에 잃는 선택이다. 다만 이 이점은 렌더 산출물을 직접 옮겨 적지 않을 때만 유지된다 — 3절을 반드시 따른다.

## 2. 렌더 절차

다이어그램을 `.mmd` 파일로 쓰고 `mermaid-cli`로 SVG를 만든다. 설정은 `assets/mermaid-config.json`을 그대로 쓴다.

```bash
npx -y @mermaid-js/mermaid-cli \
  -i diagram.mmd -o diagram.svg \
  -c <스킬경로>/assets/mermaid-config.json \
  --svgId dg-fig-1 \
  -b transparent
```

**세 옵션 모두 필수다.** 하나라도 빠지면 아래 결함이 생긴다.

- `-c .../mermaid-config.json` — 없으면 (a) 라벨이 `foreignObject`(SVG 안의 HTML)로 나와 **인쇄·PDF에서 빈칸으로 렌더**되고 (b) 색이 문서 팔레트와 어긋나 그림만 따로 노는 인상을 준다.
- `--svgId dg-fig-N` — **그림마다 다른 값**을 준다. 생략하면 모든 SVG가 `id="my-svg"`로 나오고 내부 스타일이 그 id로 스코프돼, 한 문서에 그림이 둘 이상이면 **서로 스타일을 덮어써 뒤쪽 그림이 깨진다.**
- `-b transparent` — `figure.diagram` 배경 위에 자연스럽게 얹힌다.

## 3. 임베드 — SVG를 절대 직접 옮겨 적지 않는다

**렌더된 SVG를 읽거나 타이핑하지 않는다. 스크립트로 파일에서 파일로 끼워 넣는다.**

렌더 결과는 그림 하나가 15KB 안팎(약 5,000토큰)이다. 이걸 Read 로 열거나 Write 로 옮겨 적으면 Mermaid 소스(약 30토큰)를 쓰는 것보다 **150배 비싸진다** — Mermaid를 쓰는 이유가 통째로 사라진다. 네가 직접 쓰는 것은 `.mmd` 소스와 HTML 본문뿐이고, SVG 본문은 네 컨텍스트를 거치지 않는다.

HTML 본문에는 자리표시자만 두고:

```html
<figure class="diagram">
  <!--SVG:fig1-->
  <figcaption>그림 1. 인증 요청 처리 구조</figcaption>
</figure>
```

스크립트로 치환한다:

```python
import re
from pathlib import Path
html = Path("report.html").read_text()
for tag, svg_path in [("fig1", "fig1.svg"), ("fig2", "fig2.svg")]:
    svg = re.sub(r'^<\?xml[^>]*\?>', '', Path(svg_path).read_text()).strip()
    svg = svg.replace('<svg ', f'<svg role="img" aria-label="그림 {tag} 설명" ', 1)
    html = html.replace(f"<!--SVG:{tag}-->", svg)
Path("report.html").write_text(html)
```

`role="img"`와 `aria-label`은 Mermaid가 넣지 않으므로 위처럼 치환 시점에 붙인다.

## 3-1. 검증

검증도 파일을 읽지 말고 `grep -c`로 센다 — 출력이 숫자뿐이라 컨텍스트를 먹지 않는다.

**임베드 전 4가지를 확인한다** — 하나라도 어긋나면 설정이 반영되지 않은 것이다:

```bash
grep -c foreignObject diagram.svg   # 0 이어야 한다 (1 이상이면 인쇄에서 깨진다)
grep -c "<text"       diagram.svg   # 1 이상이어야 한다 (라벨이 텍스트로 존재)
grep -c "<script"     diagram.svg   # 0 이어야 한다
grep -oE "id=\"dg-fig-[0-9]+\"" diagram.svg   # 지정한 고유 id 가 나와야 한다
```

라벨 텍스트가 실제로 보존됐는지 볼 때는 `grep "서비스 A"` 처럼 연속 문자열로 찾지 않는다 — Mermaid는 라벨을 `<tspan>`으로 쪼개므로 공백을 포함한 패턴은 매칭에 실패한다. 태그를 제거한 뒤 확인하거나 브라우저로 직접 연다.

## 4. 새 머신에서 — 이미 있는 Chrome을 재사용한다

`mermaid-cli`는 렌더에 브라우저를 쓴다. 기본 동작은 puppeteer 전용 Chromium(약 1.1GB)을 새로 내려받는 것이라, 처음 쓰는 머신에서 비용이 크다. **시스템에 Chrome이나 Edge가 이미 있으면 그걸 가리켜 다운로드를 통째로 건너뛴다.**

`puppeteer.json`을 만들고 `-p`로 넘긴다:

```json
{ "executablePath": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" }
```

```bash
npx -y @mermaid-js/mermaid-cli -i diagram.mmd -o diagram.svg \
  -c <스킬경로>/assets/mermaid-config.json -p puppeteer.json \
  --svgId dg-fig-1 -b transparent
```

경로는 OS마다 다르다 — macOS는 위 경로, Windows는 `C:\Program Files\Google\Chrome\Application\chrome.exe`, Linux는 `which google-chrome`/`which chromium`으로 확인한다. 브라우저가 없으면 이 절을 건너뛰고 기본 동작(자동 다운로드)을 쓰되, **용량과 시간이 든다는 점을 사용자에게 먼저 알리고 진행 여부를 확인한다.**

## 5. 툴체인을 쓸 수 없을 때 (폴백)

다음 경우에는 무리해서 설치하지 말고 `diagrams.md`의 hand-SVG 방식으로 그린다.

- 오프라인이거나 설치가 실패하는 환경
- 브라우저도 없고 사용자가 대용량 다운로드를 원치 않는 경우
- 박스 3~4개짜리 단순한 그림 — 손으로 그려도 어긋날 여지가 적다

폴백했다고 사용자에게 굳이 알릴 필요는 없다. 문서 하나 만들자고 수백 MB를 조용히 받지 않는다.

**폴백해도 문서는 깨지지 않는다** — hand-SVG 역시 자기완결 인라인 SVG다. 툴체인 유무는 *그림의 정확도*에만 영향을 주지 *문서의 이식성*에는 영향을 주지 않는다. 그래서 이식성을 이유로 Mermaid CDN 스크립트를 문서에 넣는 선택은 하지 않는다 — 작성 편의를 얻는 대신 **모든 열람자에게 네트워크 의존을 영구히 떠넘기는** 거래이기 때문이다.

## 6. 작성 원칙

Mermaid를 쓴다고 해서 `diagrams.md`의 원칙이 면제되지 않는다. 그대로 적용한다.

- **하나의 다이어그램은 하나의 메시지.** 노드가 ~8개를 넘으면 나눈다 — 자동 레이아웃이 배치를 해준다고 해서 복잡한 그림이 읽히는 것은 아니다.
- **그림을 이해하는 데 설명 문단이 필요하면, 문단 말고 그림을 다시 그린다.**
- 관례가 아닌 시각 규칙(점선=비동기 등)을 썼으면 범례를 단다.
- 라벨은 짧게. 자동 레이아웃은 긴 라벨을 만나면 그림 전체를 옆으로 늘린다.
