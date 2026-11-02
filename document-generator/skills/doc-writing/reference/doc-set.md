# Service design set

A design for a service or system is **five separate artifacts**, never one long page. Each has the same tab bar at the top (`docset_lib.nav`) and the same footer. Approved example: `examples/soseolbi-bookshelf-docset/`.

Every document opens with: `문서 n / 5` eyebrow → h1 `(서비스 이름) (문서 이름)` → one-sentence `.lead`.

## 1. 개요

Answers: 이게 뭔가요? 어떻게 생겼나요? 어디까지 왔나요?

| Section | Content | Form |
|---|---|---|
| (top) | 누가 쓰나요 / 무엇을 하나요 / 정보는 어디서 / 언제 쓸 수 있나요 | 4 cards |
| 어떻게 생겼나요 | People → existing screens → new programs → storage → outside providers. Dashed zone around "이번에 새로 만드는 부분", new programs in accent | hand SVG |
| 왜 (따로) 만드나요 | 3 reasons, bold lead phrase + one sentence | `ul.one` |
| 이번에 하는 것과 나중에 하는 것 | Two lists | `.two` |
| 지금 어디까지 왔나요 | Stages in plain names ("뼈대 만들기", "책 찾기"), status pill each | `.steps` + legend |
| 남아 있는 일 | One line each with a pill: 정해야 함 / 공개 조건 / 기다리는 중 / 나중에 확인 | `ul.one` |
| 이 문서에서 쓰는 말 | 2–4 words the reader truly needs | `.words` |

## 2. 기능 정의

Answers: 누가 무엇을 할 수 있나요?

| Section | Content | Form |
|---|---|---|
| (top) | One card per actor with feature count | `.cards` |
| 기능 목록 | Grouped by actor (회원 / 링크를 받은 사람 / 관리자 / 다른 서비스(자동) / 자동 프로그램). Columns: 번호(F1…) · 기능 · 할 수 있는 일 · 지켜야 할 약속 | table per actor with a pill heading |
| (rule that needs explaining) | e.g. search behavior by input length — three boxes side by side with ✔/✘ examples | hand SVG |
| 모든 기능이 지키는 약속 | Cross-cutting rules (privacy, deletion, data source, who builds the screen), bold lead + one sentence | `ul.one` |

Feature names are verbs a student would use: 책 찾기, 서재에 담기, 링크 새로 만들기.

## 3. 도메인 정의

Answers: 어떤 것들이 있고, 서로 어떻게 이어지나요?

| Section | Content | Form |
|---|---|---|
| 대상들의 관계 | Concept map with edge labels "여러 개 / 하나 / 또는 / 들어 있음"; data sources as side boxes | hand SVG |
| 용어 뜻 | 이름 · 뜻 (one sentence) · 예시·참고 (a real example: a real book title and ISBN) | table |
| (상태) | State diagram, pill-shaped boxes, code value in gray under the plain name | hand SVG |
| 누가 ~를 볼 수 있나요 | Two-condition rule as a 2×2 grid | `.grid4` |
| 꼭 지키는 규칙 | Invariants, one line each | `ul.one` |

## 4. ERD

Answers: 정보를 어떤 표에 나눠 담고, 표끼리 어떻게 이어지나요?

| Section | Content | Form |
|---|---|---|
| 그림 읽는 법 | 상자 = 표 / 상자 안 줄 = 칸 / 🔑 고유 번호 / 🔗 다른 표를 가리킴 / 1 · N | 5 cards |
| (core area) | Main tables only, key columns only. Plain name bold + code name gray in the header; each row plain label left, code name right | `entity()` SVG |
| (secondary area) | e.g. collection/log tables, separate figure | `entity()` SVG |
| 표 전체 목록 | 표 · 실제 이름 · 무엇을 담나 (one line) | table |
| (folded) | What was left out of the picture; where the exact schema lives; pending schema changes | `<details>` |

ERD drawing rules:
- A table owned by another service is a dashed gray box ("회원 (소설비에 있음)"); its links are dashed lines, and the caption says why.
- Header tint groups tables (accent = this area's main tables, gray-dark = logs/collection, light gray = standalone). Say the grouping in the caption.
- Cardinality is the text `1`, `N`, `0~1` in accent at each end, at least 14 px from the box edge and from each other; leave ≥ 30 px vertical gap between stacked boxes that carry labels.
- Route lines orthogonally (H/V) when a curve would pass close to another box; go around the outside of the drawing rather than through a column of boxes.

## 5. 핵심 흐름

Answers: 중요한 일이 어떤 순서로 처리되나요?

| Section | Content | Form |
|---|---|---|
| (top) | 그림 읽는 법: 위에서 아래로 / 실선 = 부탁 / 점선 = 답 | 3 cards |
| (list) | Links to each flow | `ul.one` |
| n. (flow name) | One sentence → `seq()` diagram → 1–2 "기억할 점" lines | per flow |

Pick 4–6 flows a user or operator would notice: the main user action, something that happens later in the background, a public/no-login path, deletion/withdrawal, the scheduled job, an admin action.

Sequence drawing rules (`seq()`):
- Participants: plain name + gray role ("새로 만듦", "원래 웹사이트"). New programs are accent boxes (keys `api`, `worker`; adjust in `seq()` if names differ).
- Messages are numbered; labels are a short request or answer in quotes-free plain words ("“한강” 검색", "찾은 책 목록").
- `note` = work done in place (gray box). Span a note across two participants when its text is longer than one column; a one-participant note at the first or last column clips otherwise.
- `sep` = "이어서" / "나중에" divider.
- Raise `col` until no `[warn] label too wide` remains.
- No time axis unless durations were measured.

## Publish and link

1. `python3 -I build.py` → five HTML files.
2. Screenshot each page and each figure; fix; rebuild.
3. Publish five artifacts (icons: book, list, map, table, flow).
4. Save `{"overview": url, "features": url, "domain": url, "erd": url, "sequence": url}` to `urls.json`.
5. `python3 -I build.py urls.json` and republish the same five file paths.
6. Open the 개요 artifact for the user when they ask to see it; the tabs reach the rest.
