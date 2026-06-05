# 다이어그램 / 시각화 가이드 (인라인 SVG)

문서에 구조·흐름을 시각화할 때 따른다. **ASCII 아트(monospace 박스·화살표로 그린 그림)는 쓰지 않는다** — 정렬이 깨지기 쉽고 직관성이 떨어진다. 대신 **인라인 SVG를 직접 작성해 HTML에 임베드**한다. 외부 의존이 전혀 없어 자기완결 단일 파일 원칙(`html-output.md`)을 그대로 지키고, 벡터라 어떤 크기에서도 선명하다.

SVG를 손으로 그릴 때 가장 흔한 실패는 **좌표가 어긋나 박스가 겹치거나 텍스트가 삐져나오는 것**이다. 이를 막는 핵심은 좌표를 즉흥적으로 정하지 않고 **그리드 규칙**에 따라 계산하는 것이다. 아래 규칙과 보일러플레이트를 그대로 쓰면 좌표 계산이 단순해진다.

## 좌표 그리드 규칙

- 모든 다이어그램은 `<svg viewBox="0 0 W H">`로 좌표계를 고정한다. 픽셀 단위 `width/height`는 두지 않는다(반응형). 컨테이너 CSS(`figure.diagram svg { max-width:100% }`)가 크기를 맡는다.
- **표준 박스**: 폭 `160`, 높이 `52`. 텍스트는 박스 중앙(`text-anchor="middle"`, `dominant-baseline="central"`).
- **간격**: 박스 사이 수직 간격 `40`(즉 다음 행 y = 이전 y + 52 + 40 = +92), 수평 간격 `40`(다음 열 x = +160 + 40 = +200).
- 텍스트가 길면 박스 폭을 늘리지 말고 **줄바꿈**(`<tspan>`)하거나 더 짧은 라벨을 쓴다. 한 박스 1~2줄.
- `viewBox`의 W·H는 배치한 요소들의 최대 우/하단 좌표 + 여백(20)으로 잡는다.

## 공통 보일러플레이트

색은 문서 팔레트와 맞춘다: 테두리 `#d1d9e0`, 박스 배경 `#f6f8fa`, 텍스트 `#1f2328`, 선/화살표 `#59636e`, 강조 `#0969da`, 성공 `#1a7f37`/`#dafbe1`, 경고 `#cf222e`/`#ffebe9`. 글꼴은 지정하지 않으면 페이지 본문 글꼴을 상속한다(한국어 OK).

화살표는 `<defs>`의 마커를 재사용한다. SVG 1개당 한 번만 정의:

```html
<figure class="diagram">
<svg viewBox="0 0 400 300" role="img" aria-label="그림 설명">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#59636e"/>
    </marker>
  </defs>
  <!-- 박스 (표준 패턴) -->
  <g>
    <rect x="120" y="20" width="160" height="52" rx="6"
          fill="#f6f8fa" stroke="#d1d9e0"/>
    <text x="200" y="46" text-anchor="middle" dominant-baseline="central"
          font-size="14" fill="#1f2328">PipelineRunner</text>
  </g>
  <!-- 화살표 (박스 하단 → 다음 박스 상단) -->
  <line x1="200" y1="72" x2="200" y2="112" stroke="#59636e" marker-end="url(#arrow)"/>
</svg>
<figcaption>그림 1. 설명</figcaption>
</figure>
```

- **화살표 라벨**: 선 중간점 옆에 `<text>`. 배경이 겹쳐 읽기 어려우면 라벨 뒤에 흰 `<rect>`를 깔거나 선에서 살짝 띄운다.
- **DB/저장소**는 원통: `<path>`로 위 타원 + 몸통. 복잡하면 그냥 박스에 라벨 `(MySQL)`로 충분하다 — 과하게 그리지 않는다.
- **경계 그룹(BC/레이어)**: 자식 박스들을 감싸는 큰 `<rect>`를 먼저(뒤에) 그리고, 좌상단에 그룹명 `<text>`. 자식보다 먼저 그려 뒤에 깔리게 한다.

## 유형별 패턴

문서 종류·표현 대상에 맞춰 고른다.

### 1. 아키텍처 / 컴포넌트 구조
박스를 **세로로 쌓고(레이어)** 화살표로 의존을 잇는다. BC/레이어 경계는 감싸는 `<rect>` + 그룹명. 위→아래 데이터 흐름이 자연스럽다.
- 행마다 y를 +92씩 증가시켜 겹침을 막는다.
- 외부 시스템은 경계 밖에, 내부 컴포넌트는 경계 `<rect>` 안에 배치.

### 2. 시퀀스 / 흐름
참여자(participant)를 **상단에 가로로 나열**하고 각자 아래로 생명선(점선 `<line stroke-dasharray="4 4">`)을 내린다. 상호작용은 생명선 사이 **가로 화살표 + 위에 라벨**, 시간순으로 y를 +44씩 내린다.
```html
<!-- 생명선 -->
<line x1="80" y1="60" x2="80" y2="280" stroke="#d1d9e0" stroke-dasharray="4 4"/>
<!-- 단계: A → B -->
<line x1="80" y1="100" x2="240" y2="100" stroke="#59636e" marker-end="url(#arrow)"/>
<text x="160" y="92" text-anchor="middle" font-size="13" fill="#1f2328">runCycle()</text>
```
- 트랜잭션 경계·분기 조건은 옅은 배경 `<rect fill="#fff8c5">` + 라벨(노트)로 표시.

### 3. 상태 전이도
상태를 **둥근 박스**(rx=20), 시작/종료는 작은 원(`<circle>`). 전이는 화살표 + **조건 라벨**(왜 전이하는가). 상태 수가 적으면 가로로, 많으면 세로로 흐르게 배치한다.

### 4. ER / 데이터 모델
엔티티를 **테이블 박스**로: 헤더 `<rect>`(엔티티명) + 그 아래 컬럼 행들. 관계는 박스 사이 선 + cardinality 라벨(`1`, `N`, `||`, `o{`). 핵심 컬럼(PK/FK/UK)만 적고 전체 컬럼은 본문 표로 보완한다.
```html
<g>
  <rect x="40" y="40" width="180" height="24" rx="6" fill="#0969da"/>
  <text x="130" y="52" text-anchor="middle" dominant-baseline="central"
        font-size="13" fill="#fff">matching_instance</text>
  <rect x="40" y="64" width="180" height="60" fill="#f6f8fa" stroke="#d1d9e0"/>
  <text x="52" y="80" font-size="12" fill="#1f2328">matching_id (PK)</text>
  <text x="52" y="100" font-size="12" fill="#1f2328">correlation_id (UK)</text>
  <text x="52" y="118" font-size="12" fill="#1f2328">status</text>
</g>
```

## 원칙

- **하나의 다이어그램은 하나의 메시지.** 전부 한 그림에 넣지 말고 관심사별로 나눈다(전체 구조 1장 + 핵심 흐름 1장). 한 SVG에 박스가 ~8개를 넘으면 분리를 검토한다.
- **다이어그램은 본문을 보완한다.** 그림으로 구조를 한눈에 주고, 세부(컬럼·파라미터·예외)는 표·본문으로 받친다.
- **그린 뒤 좌표를 점검한다.** 박스가 겹치지 않는지, 텍스트가 박스를 벗어나지 않는지, 화살표가 박스 경계에 닿는지 viewBox 범위와 함께 확인한다. 불안하면 박스 수를 줄이고 간격을 넓힌다.
- 접근성: `<svg>`에 `role="img"`와 `aria-label`(또는 `<title>`)로 설명을 단다.
- `figure.diagram` 컨테이너 + `figcaption`(그림 번호·제목)으로 감싸 본문에서 참조할 수 있게 한다.
- **너무 복잡해 SVG로 정확히 그리기 어렵다면**, 무리하게 그리다 깨뜨리지 말고 구조를 표로 표현하거나 사용자에게 분할을 제안한다. 깨진 그림보다 정확한 표가 낫다.
