---
name: doc-writing
description: Procedure, plain-language rules, visual style, generators, and the review step for documents other people read — service design sets (개요 / 기능 정의 / 도메인 정의 / ERD / 핵심 흐름), analysis, comparison, plan, review, change-report, and procedure pages published as artifacts (and the same structure for Notion or docs/ reports). Load BEFORE writing or restructuring such a document, and when the user asks for a more detailed or easier version of an existing one. Triggers - "문서 만들어줘", "문서로 정리", "아티팩트", "보고서", "설계 문서", "분석 문서", "비교 문서", "상세 버전", "자세하게 문서", "html 문서", "문서 다시 써줘", "문서 다시 만들어", "도메인 문서", "공유용 문서", "기능 정의", "요구사항", "도메인 정의", "ERD", "시퀀스 다이어그램", "개요 문서", "문서 나눠서".
---

# Document Writing

The always-on rules live in `~/.claude/rules/document-writing.md` (reader/depth/type, facts, structure, sentences). This skill adds the plain-language standard, the procedure, templates, generators, diagram patterns, and the review step. For HTML artifacts the `artifact-design` guidance still applies; where they differ, this skill wins on structure, wording, and layout.

**Approved standard (2026-11-02).** The soseolbi-bookshelf document set in `examples/soseolbi-bookshelf-docset/` is the reference the user called "딱 좋다". When this skill and an older template disagree, match that set.

## Files

| File | Use |
|---|---|
| `reference/plain-language.md` | **Read first, every time.** Word swaps, sentence rules, what "no 서술" means in practice, rejected versions |
| `reference/doc-set.md` | Service design set: the five documents, what each one holds, section order, publish-and-link procedure |
| `reference/visual-style.md` | Palette (monochrome + one accent), components (cards, one-line list, pills, steps, 2×2 grid), when to use which |
| `templates/docset/docset_lib.py` | Shared CSS, document tabs, `page()`, `fig()`, sequence diagram `seq()`, ERD box `entity()`. Copy it next to the project's `build.py` |
| `examples/soseolbi-bookshelf-docset/` | Approved example: `build.py` (content), generated HTML, `urls.json` |
| `templates/overview.html` · `detailed.html` · `change-report.html` · `domain.html` · `procedure.html` | Older single-page templates for analysis, change report, procedure. Apply the plain-language and visual-style rules on top |
| `reference/diagrams.md` | Text-never-touches-a-line, comparison pair, flow lanes, grouped tree, scaled timeline |
| `reference/sources.md` | Where these rules came from |

## Default reader

Unless the user names another reader, write for **a middle or high school student with no IT background** (user decision, 2026-11-02). That reader decides everything below:

- Every visible line is one plain sentence a student understands without the line next to it.
- No developer words in visible text. Swap them (`reference/plain-language.md`). Real code names (table, column, status value) may appear only as small gray secondary text beside the plain name.
- When something needs explaining, draw it. A card row, a table, or an SVG beats a paragraph.
- Keep facts exact: numbers, limits, and rules match the source. Simplify the words, never the facts.

When the user names a technical reader (리뷰어, 구현 명세, 검토용), keep the plain-language and visual rules but allow code names in the visible line and add the detail layer (`templates/detailed.html`).

## Section names by type

Use these h2 names, in this order; delete a section with nothing true to say. Optional sections are marked (선택).

| Type | Sections |
|---|---|
| 설계 문서 묶음 | Five separate documents — see `reference/doc-set.md`. Never one long page |
| 결정·설계 (단일 결정) | 왜 바꾸나요 → 어떻게 흐르나요 (선택, 그림) → 정한 것 → 검토했던 다른 방법 (선택) → 남은 일 → 비용 (선택) |
| 변경 보고 | 무엇이 바뀌었나요 (before/after 그림) → 바뀐 것 → 쓸 때 주의할 점 (선택) → 검토했던 다른 방법 (선택) → 남은 일 |
| 도메인 설명 | 대상들의 관계 (그림) → 용어 뜻 (표) → 상태 (그림, 선택) → 꼭 지키는 규칙 |
| 절차·문제 해결 | 증상 → 원인 → 준비할 것 → 해결 순서 (번호) → 해결 확인 → 되돌리기 (선택) |

Headings are plain questions or short noun phrases a student would say ("어떻게 생겼나요", "지금 어디까지 왔나요"), not jargon ("아키텍처", "흐름 개요").

## Procedure

1. **Reader, type, split.** Default reader per above. Decide the type; a service or system design is always the five-document set. Say reader and type in one line in the reply.
2. **Core question and sources.** Write down the questions each document answers and the sources (design doc on the integration branch, ADRs, tracking issue, PR list). The picture or table that answers each core question goes near the top.
3. **Verify state now.** Status, progress, and dates come from the source of truth checked today (issues, PRs, deployed config), not from an older doc. Use the integration branch (e.g. `develop`), not `main`, when the repo promotes in batches. Unmerged changes are shown as "검토 중", never as fact. Compare the tracking doc with the issue; when they differ, the issue wins and you say so in the reply.
4. **Separate scope.** Out-of-scope findings stay out of the documents; list them in the reply.
5. **Write content in a generator.** Copy `templates/docset/docset_lib.py` and start `build.py` from the example. Content lives in Python lists (rows, steps, entities) so every document shares one style and the tab links can be filled after publishing.
6. **Plain-language pass while writing** (`reference/plain-language.md`): one sentence per visible line, swap list applied, no meta-discourse, no translated-English phrasing, numbers with units.
7. **Diagrams.** Use the generators: `seq()` for 핵심 흐름, `entity()` for ERD, hand SVG for overview/관계/상태. Each diagram answers one question, has a one-sentence claim above it, and a caption that explains how to read it. Fix every `[warn] label too wide` the generator prints (raise `col`).
8. **Render and look.** Build, then screenshot every page full-length with Playwright (`require('playwright')`, or headless Chrome on the Mac) and screenshot **each `<figure>` on its own**. Check: line touching text, clipped note box at the left/right edge, overlapping boxes, cramped `1`/`N` labels, Korean breaking mid-word, empty first screen. Check one page in dark mode. Fix and rebuild before publishing.
9. **Fresh-context review** (shared documents). A subagent that has not seen the conversation gets: this SKILL.md path, `reference/plain-language.md`, reader/type line, and the HTML paths. It returns, per finding, the quoted element, the rule it breaks, and a rewrite. Fix or consciously reject each finding and say which you rejected and why.
10. **Publish and link.** Publish each document as its own artifact, write the returned URLs to `urls.json`, rebuild with `python3 -I build.py urls.json`, and republish the same file paths so the tabs link to each other.
11. **Clean up only on request.** When the user says to discard an earlier version, delete that artifact after the new ones are live. Never delete on your own initiative.
12. **Reply.** The links (one per line or a small table), what changed from the previous version, stale facts found, and anything you could not verify. Keep it short.

## Blocks

Classes are in `templates/docset/docset_lib.py`. Usage rules in `reference/visual-style.md`.

| Block | When |
|---|---|
| `.lead` | One sentence under the h1: what this document is about |
| `.cards` | 3–5 facts that answer "누가 / 무엇을 / 어디서 / 언제" or a reading legend ("그림 읽는 법") |
| `ul.one` | One-line items; a bold lead phrase in accent color is allowed for "why" lists |
| `.two` (`.box-yes` / `.box-no`) | 이번에 하는 것 vs 나중에 하는 것 |
| `.steps` | Progress through stages; `done` = black outline, `now` = accent |
| pills `.k .g .m .r` | 완료 · 지금/정해야 함 · 대기 · 조건 대기 |
| `.grid4` | 2×2 condition grid ("링크 켜짐 × 공개 표시") |
| `figure` + `.swipe` | Every SVG; `.swipe` shows "옆으로 밀어서 보세요" on phones |
| `.words` | 2–4 terms the reader truly needs, one line each, at the end of 개요 |
| footer `.foot` | `기준일 · 근거 · Claude Code로 작성했습니다.` — replaces the 이 문서에 대해 box for the default reader |

The full **이 문서에 대해** box (상태 → 확인 범위 → 리뷰 지점 → 작성), **warning box**, **KPI tiles**, and `추정` tags remain for technical readers and change reports; for the default reader, put the as-of date and sources in the footer and say "아직 바뀔 수 있습니다" inline where it matters.

## One line per item, explanation folded

Applies to every type: list items, table rows, cards, questions, checklist entries. (2026-10-29: "문항은 그것만 읽어도 이해되게, 최대한 단순하고 한 문장으로 … 서술이 필요한 내용을 문서에 그대로 쓰지말고 드롭다운 같은 거로 숨겨서 직관적으로 이해할 수 있게")

- **Each item reads alone.** It names who, what situation, and what scope. Never lean on a heading, the previous item, or 그/이/해당/위.
- **One sentence, as plain as possible.** No internal notation (file paths, issue numbers, ids, 「템플릿 X절」) in the visible line; put them in the footer or a `<details>`.
- **Explanation goes in a picture first, a dropdown second.** If a reader needs more than one sentence, first try a card row, table, or SVG. Only background that no picture can carry goes into `<details>`.
- **Check before publishing:** read each visible line alone. If it needs another line, rewrite it; if it runs past one sentence, split or move the rest.

## Comparison tables

1. Write the reader's choosing question first, in plain words.
2. One column per sub-question; a short value per cell, the condition in a `.why`/`.ex` line under it.
3. Highlight the subject row; state the conclusion in one sentence above the table.
4. Verify every cell.

## Writing to Notion

Same rules, same section names and order by type; only the rendering changes. Use the Notion API (`NOTION_TOKEN` in `~/.claude/trevari-agent-docs/.env`, `Notion-Version: 2022-06-28`; read with `curl --compressed` to a file). Never overwrite a page the user did not ask to replace — create a new page next to it (same parent) when rewriting. A design set becomes five sibling pages under one parent, each linking the others at the top.

| HTML block | Notion block |
|---|---|
| h1 | page title (no h1 block in the body) |
| h2 / h3 | `heading_2` / `heading_3` with the fixed section names |
| `.lead` | first paragraph |
| `.cards` | `column_list` of callouts, or a 2-column `table` |
| footer / 이 문서에 대해 | gray `callout`, one line |
| `<details>` | `toggle`, title naming its contents |
| tables | `table` with header row; subject row's first cell in bold |
| SVG diagram | render to PNG with headless Chrome, upload via `/v1/file_uploads`, `image` block with the caption as the claim |
| commands | `code` block (language `bash`) inside the step's toggle |

A diagram image cannot be edited in Notion. Keep the SVG source next to the page's other evidence and say in the footer where it is.

### Density (Notion only)

Notion has no letter- or line-spacing control, so density is set by the text itself. The approved default is `examples/notion-default-density.md` (attack-IP check, v3, 2026-10-22). Tools: `notion/dump.py <page_id> <out_dir>`, `notion/publish.py <parent_id> <title> <file.md> [--dry]` (run with `python3 -I`; the Notion call needs the sandbox off).

- Length about the same as the source (rewrites) or a few screens (new pages).
- One sentence per line; a paragraph is 1–2 sentences.
- Cells are one short phrase, no line breaks inside a cell.
- An empty paragraph between blocks and a divider between h2 sections.
- Sources, check times, and 미확인 lists go in one toggle at the end.
- Rejected on both sides (2026-10-22): v1 at 1.5× the source with 100–138-character paragraphs was "글자가 다닥다닥"; v2 at 0.4× with label-only cells was "너무 생략".

## Overview → Detailed

For a technical reader, keep the overview block on top; add `templates/detailed.html` pieces under a `상세` divider. Detail sections add what the overview lacks and never restate its tables. For the default reader, do not add a detail layer — split into separate documents instead.
