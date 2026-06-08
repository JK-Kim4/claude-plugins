# HTML 출력 가이드

사용자가 문서를 **HTML 형태**로 요청했을 때(또는 스타일·디자인이 입혀진 문서를 원할 때) 따른다. 핵심은 두 가지다: **내용·구조는 문서 종류의 템플릿을 그대로 따르고, 형식만 HTML로 입힌다.** 그리고 **문서 종류에 맞는 시각적 컴포넌트**를 적용해 목적이 한눈에 드러나게 한다.

## 1. 먼저 종류별 템플릿을 읽는다

HTML은 표현 형식일 뿐이다. *무엇을 담을지*는 여전히 해당 문서 종류의 템플릿(`work-report.md` / `progress-tracking.md` / `technical-design.md` / `onboarding-guide.md`)이 정한다. 그 파일을 먼저 읽고 섹션 구조·원칙·안티패턴을 따른 뒤, 아래 규칙으로 HTML을 입힌다.

## 2. 자기완결 단일 HTML 파일로 출력한다

공유·열람 시 파일 하나만 열면 바로 보이도록, **외부 의존성이 없는 단일 `.html` 파일**로 만든다.

- `assets/document.css`의 **내용을 읽어 `<head>`의 `<style>` 태그 안에 그대로 임베드**한다. 외부 CSS 링크나 CDN(폰트·JS 라이브러리 포함)은 쓰지 않는다 — 오프라인에서도 깨지지 않아야 한다.
- `<html lang="ko">`, `<meta charset="utf-8">`, `<meta name="viewport" ...>`를 포함한다.
- JavaScript는 기본적으로 넣지 않는다. 꼭 필요하면(예: 목차 토글) 외부 의존 없는 짧은 인라인 스크립트만.
- 기본 골격:

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>[문서 제목]</title>
  <style>
  /* assets/document.css 내용을 여기에 그대로 붙여넣는다 */
  </style>
</head>
<body>
  <!-- 문서 본문 -->
</body>
</html>
```

## 3. 문서 종류별 컴포넌트 적용

`document.css`가 제공하는 클래스를 종류에 맞게 쓴다. 모든 요소를 다 쓰려 하지 말고, 해당 문서에 실제로 필요한 것만.

### 작업 보고서
- 제목 아래 `<p class="doc-meta">`에 날짜·작성자.
- 요약은 `<div class="summary">`로 상단 강조.
- **Breaking Change는 `<div class="callout callout-warning">`**(빨강)으로 눈에 띄게. 주의사항은 `callout-caution`(노랑).
- 검증 결과의 통과/미확인은 `<span class="badge badge-green">통과</span>` / `badge-neutral`로.

### 진행/추적
- 문서 상단에 **RAG 헬스 헤더**를 크게:
  ```html
  <div class="health health-amber"><span class="dot">🟡</span> At Risk — PG사 API 키 발급 대기로 결제 연동 지연</div>
  ```
  (green/amber/red 중 현실에 맞게. `health-green`/`health-amber`/`health-red`)
- 체크리스트는 `<ul class="checklist">` + `<li class="done|todo|blocked">`.
- 상태 표를 쓸 때 상태 셀에 `badge-green`/`badge-amber`/`badge-red` 배지.
- Blocker는 `<div class="callout callout-caution">`로 강조하고 담당·기한을 함께.

### 기술 설계 / ADR
- 제목 아래 `doc-meta`에 상태 배지: `<span class="badge badge-amber">Proposed</span>` (Accepted=green, Rejected/Superseded=red/neutral).
- **고려한 대안의 장단점, Consequences의 긍정/부정은 `<div class="proscons">`**(좌 `.pros` 초록 / 우 `.cons` 빨강)로 시각 대비.
- 결정(Decision)은 `summary` 박스로 도드라지게 해도 좋다.

### 온보딩 / 가이드
- 섹션이 많으면 상단에 `<nav class="toc">` 목차(앵커 링크).
- 단계는 `<ol>`로, 각 단계의 기대 결과는 `<div class="expected">이게 보이면 성공</div>`.
- 명령어는 `<pre><code>` 코드 블록. 언어가 분명하면 그대로 텍스트로 두되 가독성 위해 들여쓰기 유지.

## 4. 다이어그램 / 시각화

구조·흐름·상태·데이터 관계를 그림으로 보여줄 때는 **ASCII 아트(monospace 박스·화살표)를 쓰지 않는다.** 대신 `references/diagrams.md`를 읽고 그 규칙을 따른다 — **인라인 SVG를 직접 작성**해 `<figure class="diagram">`에 임베드한다(외부 의존 없음, 자기완결 유지). 그리드 좌표 규칙과 보일러플레이트를 따르면 박스·화살표가 어긋나지 않는다. 아키텍처/컴포넌트, 시퀀스/흐름, 상태 전이, ER 4종 패턴이 있다. 특히 **기술 설계/ADR 문서**는 아키텍처 구조와 핵심 흐름을 다이어그램으로 보강할 때 직관성이 크게 오른다.

## 5. 공통 원칙 유지

- Markdown 기본 출력과 마찬가지로 빈 섹션은 넣지 않고, 요약을 위에 두고, 추측과 사실을 구분한다.
- 파일은 의미 있는 이름(`kebab-case.html`)으로 저장하고 경로를 알려준다.
- 색·배지는 **의미를 전달할 때만** 쓴다. 장식 목적의 과한 색은 오히려 정보를 가린다(특히 진행/추적의 RAG는 현실을 반영해야지 보기 좋으라고 green을 주지 않는다).

## 6. 다른 형식 요청 시

- **PDF**: 먼저 위 방식으로 자기완결 HTML을 만든 뒤, 사용자에게 "브라우저에서 인쇄→PDF 저장" 또는 변환 도구 사용을 안내한다. CSS에 `@media print`가 포함돼 인쇄 시에도 레이아웃이 유지된다. 변환 도구(예: wkhtmltopdf 등) 사용은 환경에 설치돼 있는지 확인 후에만.
- 그 외 형식은 사용자의 명시를 따르되, 불확실하면 짧게 확인한다.
