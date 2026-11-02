# Plain language

Approved 2026-11-02 on the soseolbi-bookshelf document set. The user's words:

> 서술하는 형식은 최대한 지양하고 새로운 단어 표현이나 외국어를 직역한 표현은 사용하지 말고 최대한 간단하고 공감대 있는 언어로 표현해줘. 서술하는 대신 간결하게 한 문장으로 표현할 수 있으면 좋고, 서술이 필요한 지점이라 판단되면 최대한 보조도구인 시각화 자료를 활용해서 설명해줘. 독자가 중고등학생이고 IT 분야에 전문 지식이 없다고 가정.

## Sentence rules

1. **One sentence per visible line.** A card body, list item, or table cell is one sentence or one short phrase.
2. **합니다체.** Short, ending in -ㅂ니다/-습니다. Headings may be questions in -나요 ("어떻게 생겼나요").
3. **No 서술.** No paragraph that walks through reasoning. If two or more sentences are needed to explain, use a picture, a table, or a card row instead.
4. **No meta-discourse.** Drop "이 절에서는", "아래는 ~입니다", "~에 대한 답입니다", "정리하면".
5. **No coined words, no translated English.** If a student would not say it, swap it. Use words people already share: 부탁, 답, 줄, 목록, 표, 칸, 묶음, 기록, 자동.
6. **Numbers stay exact, with units.** "약 586만 권", "최대 5,000자", "5분마다". A rough comparison must still be true ("천 배 넘게", not "수천 배" when the ratio is about 1,300–2,000).
7. **Code names only as gray secondary text.** `shelf_items` sits next to "서재 항목", never alone in a visible line.
8. **One word per idea.** Once 작업 조각 is chosen for chunk, never write chunk or 청크 in the same set.

## Swap list

Add to this list whenever a new project brings new jargon. Left: do not use in visible text. Right: use.

| 쓰지 않음 | 쓰는 말 |
|---|---|
| API 서버, 백엔드 | (서비스이름) 서버 — 처음 한 번 "요청을 받아 처리하는 프로그램" |
| DB, 데이터베이스 | 저장소 — 처음 한 번 "기록을 표 모양으로 보관하는 곳(흔히 DB)" |
| worker, 배치, 크론, 스케줄러 | 자동 수집 프로그램 / 정해진 때 자동으로 도는 일 |
| chunk | 작업 조각 |
| run | 수집 실행 / 한 번 돌린 기록 |
| queue, 큐, enqueue | 대기 줄 / 줄에 추가 |
| upsert, 적재, 동기화 | 넣기 · 고치기 / 받아 오기 |
| backfill | 처음 한 번 전부 받기 |
| resweep, 재순회 | 매달 다시 확인하기 |
| enrichment, 보강 | 표지·소개 채우기 |
| endpoint, 엔드포인트 | 기능 / 창구 |
| request / response | 부탁 / 답 |
| 인증, 토큰 | 로그인 / 로그인 표시 |
| 인가, 권한 체크 | 할 수 있는 사람인지 확인 |
| handle, 핸들 | 공개 링크 글자 |
| PK / FK | 🔑 고유 번호 / 🔗 다른 표를 가리킴 |
| 1:N, 카디널리티 | 하나와 여러 개 (`1` · `N` 표시) |
| 엔티티, 테이블, 컬럼 | 표, 칸 |
| 상태 전이 | 상태 바꾸기 |
| 게이트, 블로커 | 조건 / 기다리는 것 |
| 리뷰 중, PR | 검토 중 (PR 번호는 바닥글이나 접힌 곳에만) |
| 이용 조건, 약관 | 사용 허락 |
| 운영 노출, 출시 | 공개하기 |
| 외부 API, 소스 | 바깥 정보 제공처 |
| 무작위 토큰 | 긴 무작위 글자 |
| p95, 지연 | "1초 안에 끝나는지" |
| 멱등 | (말하지 않는다. 필요하면 "여러 번 불러도 결과가 같습니다") |

## Approved lines (examples)

- 소설비 회원이 읽은 책, 읽는 중인 책, 읽고 싶은 책을 기록하는 기능입니다.
- 책 정보가 너무 큽니다. 책 586만 권의 정보가 지금 소설비 저장소 전체보다 천 배 넘게 큽니다.
- 공개 링크를 새로 만들면 예전 링크로는 더 이상 볼 수 없습니다.
- 회원이 직접 연 책이 새 책보다 먼저 채워집니다.
- 물어보기 전에 횟수부터 적어 두어서 하루 한도를 넘지 않습니다.

## Rejected versions (same project, do not repeat)

| Version | What it was | Why it was rejected |
|---|---|---|
| v1 (2026-10-29) | `design.md` converted to HTML as-is with a sticky TOC | 원문 전사. 독자·구조 없이 길기만 함 |
| v2 (2026-10-29) | One page, 결정·설계 type, 이 문서에 대해 box, glossary, 상세 divider, ADR-heavy tables | "내가 원하는 형식이 아님": 한 문서에 다 몰아넣음, 개발자 용어, 서술이 많음 |
| v3 colors (2026-11-02) | Muted teal accent on off-white | "애매한 색" → monochrome + one orange accent |
| v3 (2026-11-02) | Five documents, student reader, plain words, generator-built SVGs, monochrome + orange | **Approved** ("딱 좋다") |
