# document-generator 한글 레이아웃 최적화 — 세션 핸드오프

**상태: 🟢 On Track** · _최종 갱신: 2026-07-30_ · _작업 브랜치: main (미커밋)_

## 요약

document-generator 스킬(v1.2.0 → v1.3.0)의 한글 레이아웃 깨짐을 원인 실측 → CSS·가이드 수정 → 정적 점검기 신설 → 샘플 문서로 검증까지 완료했다. 실브라우저 측정으로 가로 넘침 98/476/48px → 전 조건 0px 확인. 미응답으로 남아 있던 경쟁 스킬 조사 질문도 해소했다(아래 "조사 결론"). 변경은 커밋됐고, `samples/`는 사용자 결정으로 레포에 넣지 않았다(로컬에만 존재).

## 진행 상황

- [x] 원인 실측 — 기존 생성 문서 8개 + 한글 fixture를 Chrome(puppeteer-core + 시스템 Chrome)으로 측정. 원인 2개 확정: (1) `word-break: keep-all` 단독 + 스크롤 컨테이너 부재 → 긴 경로·`·` 연결 어절이 표를 밀어냄, (2) SVG `<text>`는 줄바꿈 없음 + `overflow: hidden` → 한글 라벨이 경고 없이 잘림
- [x] `assets/document.css` 수정 — `overflow-wrap: anywhere`(`break-word` 아님 — min-content를 낮추는 건 `anywhere`뿐), `.table-wrap` 스크롤 래퍼, 그리드 `minmax(0,1fr)`, `.badge` nowrap, `.health` flex-wrap, `@media print` 스크롤 영역 펼침 + `pre` 줄바꿈, `text-wrap: balance`, `tabular-nums`
- [x] `assets/check-layout.py` 신설 — 의존성 없는 정적 점검기. 글자폭 계수를 브라우저 실측으로 보정(오차 최대 1.7%). SVG 텍스트의 박스·viewBox 이탈, 문장형 라벨(>28자), 표 5열 초과, `.table-wrap` 누락을 잡는다. Mermaid 렌더 SVG는 검사 제외
- [x] 가이드 갱신 — `diagrams.md`(SVG엔 라벨만·한글 글자수 예산표·텍스트 x 좌표 도출·스크립트 점검), `html-output.md`(2-1 한글 레이아웃 규칙, 6절 저장 전 점검, 갱신 시 `<style>` 블록 교체 규칙), `mermaid-render.md`(6절 한글 라벨 — Mermaid는 한글 안전함을 실측 확인, 어절 공백 유지·12자 권고)
- [x] `mermaid-config.json` — fontFamily에 Malgun Gothic 추가
- [x] Mermaid 11 `role` 중복 버그 발견·수정 — 가이드의 SVG 주입 스니펫이 `role="img"`를 무조건 덧붙였는데 Mermaid 11은 이미 `role="graphics-document document"`를 넣는다 → duplicate attribute로 마크업 깨짐. `mermaid-render.md` 스니펫을 "없을 때만 붙인다"로 수정. **기존에 Mermaid 가이드로 만든 문서들은 이 중복을 갖고 있을 수 있다**
- [x] `plugin.json` 1.3.0 + `claude plugin update` 적용 + 캐시(`~/.claude/plugins/cache/jongwan-plugins/document-generator/1.3.0/`) 수동 동기화(diff -rq로 동일 확인)
- [x] 샘플 문서 생성·검증 — `samples/2026-07-30-korean-layout-verification.html`. 정적 점검 0건, 뷰포트 1440~390px + 인쇄 A4 전부 가로 넘침 0px, 스크린샷 육안 확인
- [x] evals.json에 케이스 10(한글 레이아웃) 추가 — **추가만, 실행 안 함**
- [x] 경쟁 스킬 조사 — 결과는 아래 "조사 컨텍스트" 참조
- [x] **미응답 질문 해소** — 8개 레포의 SKILL.md·references 본문을 직접 읽어 판정. 결론은 아래 "조사 결론"
- [x] 변경 커밋 — 수정 7개 + 신규 2개(`check-layout.py`, `docs/handoff/`). `samples/`는 사용자 결정으로 제외(레포에 생성물을 담는 선례를 만들지 않음)
- [ ] 기존 생성 문서 8개의 스타일 블록 교체 여부 결정
- [ ] eval 케이스 실행 방법 정리

## 🚧 Blocker / 결정 대기

- **eval 실행 불가**: 이 레포는 `evals.json` 형식인데 `claude plugin eval`은 `evals/**/case.yaml` 또는 `prompt.md + graders/*.md`를 읽는다 → 형식 변환을 할지, 수동 검증으로 둘지 결정 필요 (담당: 사용자)
- **기존 문서 8개**: 결함이 둘인데 대상 파일이 같으므로 **한 번의 결정으로 함께 처리한다**. (1) CSS는 생성 시점 임베드라 자동으로 안 고쳐진다 → 갱신 모드로 `<style>` 교체, (2) Mermaid 가이드로 만든 문서는 `role` 중복 속성을 갖고 있을 수 있다 → `check-layout.py`가 "SVG 파싱 실패"로 잡아낸다. 먼저 8개에 `check-layout.py`를 돌려 실제 영향 범위를 확인한 뒤 교체 여부를 정하는 편이 싸다. 대상: `~/Documents/features/flow_api-gap-analysis-2026-06-23.html`, `~/Desktop/settlement-lab/interview-report.html`, `~/Desktop/workspaces/write-note/docs/community-epic-workbook.html`, `~/Desktop/abtest-nplus1-interview-prep/lessons/0001-abtest-nplus1-interview.html` 외 4개 (담당: 사용자)

## 다음 단계

1. 위 Blocker 2건(eval 형식 변환 / 기존 문서 8개)에 대한 사용자 결정
2. (선택) 조사 결론이 지목한 3개 갭 중 도입할 것 선택 — 특히 Reader Testing

## 조사 결론 (2026-07-30, 각 레포 파일 본문 직접 확인)

**질문**: 조사한 스킬들 중 "이해도를 높이기 위한 문서 작성 규칙·템플릿"을 포함한 것이 있는가?
**답**: 있다. 직접 해당 3개, 장르 한정 1개, 시각화 규칙만 2개, 해당 없음 2개.

| 레포 | 판정 | 근거 파일 · 내용 |
|---|---|---|
| YurunChen/repo-docs-skills | **직접 해당** | `docs/WRITING.md`(15분 이해 기준, 소크라테스 질문 7개 표 — 문서에 노출 금지, "약한 중심→나은 중심" 치환표), `docs/QUALITY_RULES.md`(Confirmed/Inferred/Planned/Unknown 증거 등급 — 신뢰도와 출처를 직교로 분리), `docs/PAGE_RULES.md`(Navigation Scent — 링크 라벨에 파일명·"여기" 금지, 독자 숙련도별 진입점) |
| anthropics/skills · doc-coauthoring | **직접 해당** | `skills/doc-coauthoring/SKILL.md` Stage 3 Reader Testing — 컨텍스트 없는 fresh Claude에 문서 본문만 주고 독자 질문 5~10개 + 모호/전제지식/모순 점검을 시켜, 틀린 지점을 갭으로 잡아 되돌아간다. 종료 조건은 Reader Claude가 일관되게 맞출 때 |
| anthropics/skills · internal-comms | **직접 해당** | `skills/internal-comms/SKILL.md` — 유형별 가이드라인을 `examples/`에 분리하는 구조가 우리 `references/`와 동일. 규칙 본문은 특정 회사 내부 포맷이라 이식 가치는 낮음 |
| Imbad0202/academic-research-skills | 장르 한정 | `academic-paper/references/` 29종(`academic_writing_style.md`, `writing_quality_check.md`, `writing_judgment_framework.md` 등) + `templates/` 11종(IMRaD·문헌고찰·정책브리프…). 학술 논문 장르 고정 |
| haidang1810/md2html | 시각화만 | `SKILL.md` + `components.md` 스니펫 카탈로그 + `template.html`. 목표는 이해도지만 규칙은 시각 컴포넌트 선택에 한정. 8개 언어 UI 라벨 표에 한국어 포함 |
| nicobailon/visual-explainer | 시각화만 | `plugins/visual-explainer/SKILL.md`의 "내용 유형 → 기본 표현" 매핑표·참조 라우팅표. 무엇을 쓰는지가 아니라 무엇으로 그리는지 |
| bitjaru/styleseed | 해당 없음 | UI 디자인 시스템 주입. 문서 작성 아님 |
| comsky/remy-skill-recipes | 해당 없음 | `skills/_template/*.md`는 **SKILL.md 작성** 템플릿이지 문서 작성 템플릿이 아님. 단 `skills/cjk-text-wrap-audit/`가 같은 한글 깨짐 문제를 다룬다 — 접근은 보완적(그쪽은 런타임 CSS cascade·컴포넌트 override 추적, 우리는 생성 시점 정적 좌표 계산) |

**우리 스킬에 없는 것 3가지**

| 없는 것 | 출처 | 우리 현황 |
|---|---|---|
| Reader Testing | doc-coauthoring Stage 3 | `check-layout.py`는 레이아웃만 검증한다. "독자가 이해했는가"는 검증하지 않는다 |
| 증거 등급 표기 체계 | repo-docs-skills `QUALITY_RULES.md` | SKILL.md 4단계에 "추측과 사실을 구분한다" 원칙만 있고 표기 규약이 없다 |
| Navigation Scent | repo-docs-skills `PAGE_RULES.md` | 단일 파일 출력이라 영향이 작다 |

## 조사 컨텍스트 (2026-07-30 GitHub API 실측)

별 수는 `gh api repos/...`로 직접 조회한 조회 시점 값. 아래 표는 최초 조사 시점 값이고, 같은 날 재조회에서 8개 중 5개가 소폭 상향했다(165,104→165,125 / 82,598→82,628 / 40,118→40,133 / 9,359→9,360 / 427→428). 자연스러운 스타 증가이며 레포 존재·규모·순위는 그대로다 — 후보 목록은 유효하다. 이후 재조회에서도 이 정도 드리프트는 정상이니 표가 낡았다는 신호로 읽지 말 것.

| 별 | 레포 | 성격 |
|---|---|---|
| 165,104 | anthropics/skills | 공식. document-skills(docx·pdf·pptx·xlsx) 포함 |
| 82,598 | nexu-io/open-design | 에이전트를 디자이너로 |
| 40,118 | Imbad0202/academic-research-skills | 연구→작성→리뷰→수정 파이프라인 |
| 9,359 | nicobailon/visual-explainer | 자기완결 HTML 설명 페이지. 생성 후 검증 없음(README 기준) |
| 854 | bitjaru/styleseed | 에이전트에 고정된 디자인 판단 주입 |
| 427 | YurunChen/repo-docs-skills | 진행 로그·핸드오프 문서 유지 — 우리 갱신 모드와 겹침 |
| 410 | haidang1810/md2html | md→디자인된 HTML. 한국어 포함 8개 언어, Mermaid는 CDN 기본 |
| 12 | comsky/remy-skill-recipes | "engineering-grade SKILL.md recipes" — 작성 규칙 후보 |

- GitHub 코드 검색: SKILL.md 내 `word-break: keep-all` 177건 / `overflow-wrap` 1,632건 / `table-wrap` 384건 — 한글 레이아웃을 다루는 스킬은 이미 여럿 있다
- `awesome-*` 목록(ComposioHQ 71k 등)의 별 수는 목록 인기이지 스킬 자체가 아님

## ⚠️ 배포 시 함정 (2026-07-30 실측)

1. **이 레포는 머신이 둘이다.** 회사 머신(`zimssa-jwkim@zimssa.com`)이 같은 origin에 푸시한다. 실제로 v1.3.0은 fetch 없이 v1.2.0 위에 쌓여, 원격의 `95346d3 v1.2.1`(긴 코드 토큰 오버플로우 CSS)을 모른 채 작업했다 — 그대로 밀었으면 그 수정이 사라졌다. **작업 시작 전 `git fetch` 필수.** v1.2.1은 rebase로 통합했고 `code`·`th,td`의 `overflow-wrap: anywhere`, `word-break: break-word`가 모두 살아 있음을 확인했다.
2. **`claude plugin update`는 버전 번호만 비교한다.** 레포 내용을 바꿔도 `plugin.json`의 버전이 그대로면 "already at the latest version"만 출력하고 캐시를 재복사하지 않는다. 캐시(`~/.claude/plugins/cache/jongwan-plugins/document-generator/<버전>/`)는 심링크가 아니라 복사본이다. → 같은 버전에서 내용만 고쳤으면 **파일을 직접 복사하거나 버전을 올려야** 반영된다. `diff -rq`로 확인하는 습관이 필요하다.
3. **마켓플레이스 소스가 GitHub이 아니라 로컬 디렉터리다** (`known_marketplaces.json`: `"source": "directory", "path": "/Users/jongwan-air/doc-gen-plugin"`). 이 머신에서는 push가 플러그인 동작에 아무 영향이 없다. push는 원격 백업과 타 머신용이다.

## 참고 — 재현·검증 도구 위치

- **영속(레포)**: `document-generator/skills/document-generator/assets/check-layout.py` — `python3 <스킬경로>/assets/check-layout.py <html>` 로 실행, 발견 0건이 통과
- **휘발(세션 scratchpad, 다음 세션엔 없을 수 있음)**: 실브라우저 측정 스크립트 `measure.js`(puppeteer-core `~/.npm/_npx/1a4eb60c8f6b0f89/node_modules/puppeteer-core` + 시스템 Chrome, `documentElement.scrollWidth − clientWidth` 측정 + SVG getBBox 검사)와 before/after fixture. 필요하면 이 요약대로 재작성 가능
- 폭 계수(한글 0.87em / 숫자 0.60 / 대문자 0.67 / 경로 구두점 0.33 / 소문자 0.52)는 macOS 폰트 스택 실측 — 타 OS 미검증. 가이드 예산표는 보수적 1.0em을 쓰는 비대칭이 의도된 설계
