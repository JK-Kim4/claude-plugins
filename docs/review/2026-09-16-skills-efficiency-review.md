# 스킬 전수 조사 리뷰: 모델 진화에 따른 비효율 차단 사전 작업 (2026-09-16)

> 작성: Claude Fable 5.1 (Claude Code 2.1.272). 대상: 이 저장소의 플러그인 8개(마켓플레이스 등재 7 + 미등재 pr-automator), 스킬 31개, 에이전트 4개, 참조 문서 40여 개 전량.
> 목적: 2026-06~09에 작성된 스킬들이 현행 Claude Code 규격과 Claude 5 계열 모델 위에서 비효율적으로 동작하는 지점을 찾고, 개선 작업의 우선순위를 제안한다. 채택·기각은 사용자가 정한다.
> 근거 규격: code.claude.com/docs/en/skills, /plugins-reference, /plugin-evals, /sub-agents (2026-09-16 확인). 실측 명령은 2절.

## 0. 요약

전 스킬이 `claude plugin validate`를 통과하고, 스크립트 테스트(llm-wiki 138건, dlc 87건)도 전부 GREEN이다. 기능 결함은 발견하지 못했다. 비효율은 **구조** 쪽에 있다.

1. **경로 플레이스홀더를 모델이 매번 추론한다.** `<skill>`, `<skills>`, `<스킬경로>`, `<wiki-bootstrap>` 같은 자리표시자가 llm-wiki 4개·dlc 10개·document-generator 1개에 쓰인다. 현행 규격은 `${CLAUDE_SKILL_DIR}`·`${CLAUDE_PLUGIN_ROOT}` 변수를 제공한다. dlc는 본문에서 "로드하기 전에는 다른 플러그인의 설치 경로를 알 수 없다"고 스스로 적고 있다.
2. **세션마다 약 5,050 토큰이 항상 실린다**(7 플러그인 always-on 합계 6,384에서 명시 호출형 스킬 12개분을 뺀 실효치, `claude plugin details` 실측). 그중 craft가 2,492(실효 약 2,320)로 가장 크고, craft의 절반(약 1,250)은 특정 프로젝트(소설비) 전용 마케팅·PM 스킬 5개다. 이 5개는 다른 프로젝트 전용 메모리 파일·다른 저장소의 HTML 경로·이슈 번호·존재하지 않는 `ux-mockup` 스킬을 참조한다.
3. **craft 스킬 4개가 공식 마켓플레이스의 mattpocock-skills 1.2.3과 이름이 같다**(`tdd`, `diagnosing-bugs`, `triage`, `implement`). 이 머신에는 둘 다 설치돼 있어 `tdd`·`diagnosing-bugs`는 자동 트리거가 두 갈래로 갈린다. craft README의 중복 제거 안내(`~/.claude/skills` 심링크 삭제)는 이 경로를 막지 못한다.
4. **"항상 적용" 규율을 스킬로 배포한다**(`token-efficiency`). 스킬은 모델이 고를 때만 로드되므로 "항상"을 보장하지 못하고, 본문 일부는 현행 하네스와 어긋난다(Read 도구 출력 상한, 백그라운드 명령 알림, 병렬 도구 호출).
5. **내장 기능과 겹치는 스킬**: `worktree`(내장 `EnterWorktree` 도구), craft `implement`의 "충돌 시 worktree 격리"(Agent 도구 `isolation: "worktree"`), document-generator의 데이터 차트 절(내장 `dataviz` 스킬).
6. **에이전트 4종이 `model`·`effort`를 지정하지 않는다.** 부모 세션 모델(현재 Fable 5.1)을 그대로 상속한다. `design-it-twice`는 이 에이전트를 3개 이상 병렬 스폰한다.
7. **eval이 두 포맷으로 갈라져 있다.** dlc는 `claude plugin eval`용 `case.yaml`, 나머지 4개는 skill-creator용 `evals.json`. 후자는 `claude plugin eval`로 돌릴 수 없다.

우선순위(5절)로는 1·3이 P0(지금 동작을 잘못되게 하거나 비용을 매 호출 지불), 2·4·6이 P1(세션 비용·품질), 5·7과 나머지가 P2다.

## 1. 조사 범위와 방법

- 읽은 것: 31개 `SKILL.md` 전문(2,966줄), `references/`·`agents/`·`tests/` 헤더·`evals/` 전부, README 4개, `docs/review/2026-09-13-dlc-r4-improvement-proposal.md`(dlc의 알려진 잔여 17건은 여기서 재지적하지 않는다).
- 실측: `claude plugin validate .`, `claude plugin details <plugin>@jongwan-plugins`(7개 + 비교용 mattpocock-skills), python 단위 테스트 5 스위트, description 글자 수, 스킬별 최종 커밋일, 로컬 설치 목록(`~/.claude/plugins/installed_plugins.json`, `~/.claude/skills`, `~/.agents/skills`), 참조 대상 실존 여부.
- 현행 규격은 claude-code-guide 에이전트가 공식 문서에서 확인한 결과를 썼다. 문서에 없는 것은 "미문서화"로 적었다.

## 2. 실측 수치

### 2-1. 세션 상시 비용 (always-on)

`claude plugin details` 추정치. "always-on"은 스킬 description 등 매 세션 시스템 프롬프트에 실리는 몫, "on-invoke"는 스킬이 발동할 때 본문이 로드되는 몫이다.

| 플러그인 | 컴포넌트 | always-on | on-invoke 최대 |
|---|---|---|---|
| craft | 스킬 11 + 에이전트 4 | ~2,492 | diagnosing-bugs ~3.9k |
| llm-wiki | 스킬 4 | ~1,275 | wiki-recall ~4.4k |
| dlc | 스킬 10 | ~1,161 | dlc-build ~4.3k |
| document-generator | 스킬 1 | ~475 | ~5.5k |
| architecture-reviewer | 스킬 1 | ~380 | ~1.6k |
| pr-reviewer | 스킬 1 | ~326 | ~3k |
| agent-workflow | 스킬 2 | ~275 | token-efficiency ~2.9k |
| 합계 | 31 + 4 | **~6,384** | |
| (비교) mattpocock-skills 1.2.3 | 스킬 25 | ~1,622 | |

- craft 15 컴포넌트의 always-on이 mattpocock 25 스킬보다 크다. 컴포넌트당 평균 166 대 65 토큰이다. 원인은 둘이다. (a) 한국어 description은 같은 뜻의 영어보다 토큰 수가 많다. (b) 트리거 문구를 6~15개씩 나열한다.
- dlc 10개와 craft `triage`·`implement`는 `disable-model-invocation: true`다. 공식 문서(skills § Control who invokes a skill)에 따르면 이 스킬들은 description도 컨텍스트에 실리지 않는다. `plugin details`의 추정치는 이를 구분하지 않으므로, 실효 always-on은 6,384에서 dlc 1,161과 craft 170을 뺀 **약 5,050**이다. dlc는 사실상 세션 비용이 0이다.
- Codex CLI 실측(dlc README)에서 이미 "Skill descriptions were shortened to fit the skills context budget" 경고가 관찰됐다. Claude Code는 description 1개당 1,536자 상한을 두며 총예산은 문서화돼 있지 않다.

### 2-2. description 길이와 본문 길이

description 상한 1,536자를 넘는 스킬은 없다. 긴 순서:

| 스킬 | description 글자 | 본문 줄 | 최종 커밋 |
|---|---|---|---|
| document-generator | 488 | 103 (1,529단어) | 2026-08-20 |
| wiki-bootstrap | 390 | 184 | 2026-07-30 |
| architecture-reviewer | 384 | 75 | 2026-06-08 |
| token-efficiency | 366 | 100 | 2026-07-30 |
| wiki-lint | 309 | 131 | 2026-09-13 |
| pr-reviewer | 300 | 117 | 2026-07-17 |
| pr-automator | 284 | 132 | 2026-06-08 |
| wiki-digest | 280 | 191 | 2026-07-30 |

본문 500줄 권장 상한을 넘는 스킬은 없다. 다만 on-invoke 4k 이상인 스킬(document-generator, wiki-recall, wiki-digest, wiki-bootstrap, dlc-build, dlc-verify, dlc-plan)은 4-절에서 개별로 본다.

### 2-3. 검증 결과

- `claude plugin validate .`: 통과.
- 단위 테스트: wiki-bootstrap 26, wiki-digest 41, wiki-lint 24, wiki-recall 47(합 138, README는 137로 표기), dlc 87. 전부 OK (Python 3.14.6).
- dlc eval: 최종 실행 8/8 (2026-09-13 기록).

## 3. 현행 규격 대비 갭 (플러그인 횡단)

### G1. 스킬 경로 플레이스홀더 [P0]

- **현황**: llm-wiki 4개(`<skill>`, `<wiki-bootstrap>`), dlc 10개(`<skills>/dlc/scripts/dlc.py`), document-generator(`<스킬경로>/assets/check-layout.py`)가 자리표시자를 쓴다. dlc는 protocol.md에 "`<skills>`는 스킬이 로드될 때 보인 스킬 디렉터리의 부모다"라는 해석 규칙까지 둔다.
- **규격**: SKILL.md 본문에서 `${CLAUDE_SKILL_DIR}`(그 스킬 디렉터리), `${CLAUDE_PLUGIN_ROOT}`(플러그인 루트), `${CLAUDE_PROJECT_DIR}`를 쓸 수 있다. 공식 문서(skills § Available string substitutions)는 이 변수를 **스킬 마크다운 본문 로드 시점에 실제 경로로 치환**하며, 플러그인 스킬에서도 동일하게 동작하고, `${CLAUDE_PLUGIN_ROOT}`는 "플러그인의 스킬들 사이에 공유되는 리소스"를 가리키는 용도로 명시돼 있다.
- **비용**: 매 호출마다 모델이 경로를 추론한다. dlc eval 5회 중 3회에서 에이전트가 `dlc.py` 소스를 grep해 규칙을 확인했다는 기록(r4 제안 I9)이 있고, 경로 추론도 같은 부류의 턴 낭비다. 추론이 틀리면 스크립트를 못 찾고 "수동 체크리스트" 폴백으로 빠진다.
- **제안**: Claude Code 경로는 변수로 바꾼다. 형제 스킬은 `${CLAUDE_PLUGIN_ROOT}/skills/dlc/scripts/dlc.py`. Codex·Gemini 이식성은 "변수가 치환되지 않은 환경에서는 `<skills>` 규칙을 따른다" 한 줄로 유지한다.
- **주의**: `npx skills add`로 설치한 Codex·Gemini 환경에서는 변수가 치환되지 않고 문자열 그대로 남는다. 그 환경용 해석 규칙(`<skills>` = 스킬 디렉터리의 부모)은 protocol.md에 한 줄로 유지한다.

### G2. 스킬 이름 충돌 [P0]

- **현황**: craft의 `tdd`, `diagnosing-bugs`, `triage`, `implement`가 공식 마켓플레이스 `mattpocock-skills@claude-plugins-official` 1.2.3의 같은 이름 스킬과 공존한다. 이 머신에는 두 플러그인이 모두 설치돼 있고, 현재 세션의 스킬 목록에 `mattpocock-skills:tdd`와 `craft:tdd`가 나란히 있다.
- **영향**: `tdd`·`diagnosing-bugs`는 자동 호출형이라 "TDD로"라는 말에 어느 쪽이 발동할지 모델 판단에 맡겨진다. 두 description이 모두 예산을 먹는다. `triage`·`implement`는 명시 호출형이라 description은 컨텍스트에 실리지 않고, 사용자가 `/craft:triage`로 구분할 수 있지만 슬래시 목록에 둘 다 보인다.
- **craft README의 안내**("`~/.claude/skills`에서 심링크 4개 삭제")는 개인 스킬 경로만 다루고, 플러그인으로 설치된 upstream은 막지 못한다. 실제로 심링크는 이미 삭제돼 있는데 충돌은 남아 있다.
- **제안** (택일, 7절 결정 사항 1):
  - (a) craft 포크 4개의 이름을 바꾼다(예: `tdd-kr`, `diagnose`). 다른 스킬·에이전트·dlc가 `craft:tdd` 이름으로 참조하므로 참조 7곳을 함께 고친다.
  - (b) README에 "mattpocock-skills 플러그인을 설치했다면 `claude plugin disable` 하거나 두 스킬 중 하나를 쓰기로 정한다"를 적고, craft description에 upstream과의 차이(한국어·에이전트 위임·비용 규율)를 한 줄로 넣어 모델이 구분하게 한다.
  - (c) 포크를 버리고 upstream + craft 에이전트 4종만 남긴다. 한국어 본문·검증 위임 경로를 잃는다.

### G3. 프로젝트 전용 스킬이 공용 플러그인에 실려 있다 [P1]

- **현황**: `marketing-strategy`, `pm-breakdown`, `prd-ticket-writing`, `retention-playbook`, `acquisition-playbook`(2026-08-19 추가)는 소설비 서비스 전용이다. 근거:
  - 메모리 위키링크 `[[oci-db-readonly-access]]`, `[[ga4-tracking-prod-env-only]]`, `[[pr-closes-keyword-develop]]`는 `~/.claude/projects/-Users-jongwan-air-Desktop-workspaces-write-note/memory/`에만 존재한다. 다른 프로젝트·다른 머신에서는 해석 불가.
  - `ux-mockup` 스킬을 Skill 도구로 로드하라고 하지만 이 머신 어디에도 없다.
  - `docs/research/2026-08-19-*.html`, 이슈 `#144~#155`, `gh auth switch -u JK-Kim4`, "§10·§19-5·§35·§40"(출처 문서 미상), 테이블명 `documents.updated_at`·`work_sessions` 등 다른 저장소의 사실이 본문에 박혀 있다.
- **비용**: always-on 약 1,250 토큰(craft의 절반)을 모든 세션이 지불한다. 마케팅과 무관한 코드 세션에서도 "리텐션", "온보딩", "PRD" 같은 단어에 트리거 후보가 된다.
- **사용자 자신의 원칙과 충돌**: 메모리 `skill-authoring-universality`("스킬은 항상 범용으로, 머신 경로 하드코딩 금지").
- **제안**: 소설비 저장소(write-note)의 `.claude/skills/`로 옮긴다. 범용으로 남길 가치가 있는 것은 `prd-ticket-writing` 1~4절(PRD·유저 스토리·수용 기준·우선순위 프레임워크)뿐이며, 이 저장소 전용 5절을 떼면 범용 스킬이 된다. `retention-playbook`·`acquisition-playbook`의 원본 프레임워크 부분도 소설비 수치를 떼면 범용이지만, 지금 본문은 수치와 결합돼 있어 분리 작업이 필요하다.

### G4. description 예산: 한국어 밀도와 트리거 문구 나열 [P1]

- **현황**: 2-1절. document-generator description 하나가 488자(~480 토큰)로 mattpocock 스킬 7개분이다. "정리해줘/보고서/문서로 남겨줘/요약해줘/체크리스트/…" 15개 문구를 나열한다.
- **모델 변화**: 트리거 문구 나열은 이전 세대 모델이 짧은 description으로는 발동을 놓치던 시기의 패턴이다. Claude 5 계열은 "무엇을 하는가 + 언제 쓰는가" 두 문장으로 충분히 구분한다(공식 문서 권장 형태). 다만 이것은 규격 문서의 권장이지 모델별 성능 수치가 문서화된 것은 아니다.
- **제안**: description을 "역할 1문장 + 사용 시점 1문장 + 제외 1구절"로 줄인다. 목표는 스킬당 200자 이하. 예상 절감은 always-on 기준 30~40%(약 2,000 토큰/세션). 줄인 뒤 `claude plugin eval`로 발동률을 확인한다(G8).

### G5. "항상 적용" 규율을 스킬로 배포 [P1]

- **현황**: `agent-workflow/token-efficiency`. description이 "TRIGGER on any computer use whatsoever"이고 README는 "도구를 쓰는 모든 작업에 적용된다"고 쓴다.
- **문제**: 스킬은 모델이 관련 있다고 판단해 Skill 도구로 로드할 때만 본문이 들어온다. "항상"은 보장되지 않고, 로드되면 매번 2.9k 토큰이 든다. 반면 사용자 글로벌 `~/.claude/rules/shared/long-running-bash.md`·`subagent-delegation-cost.md`가 같은 주제를 이미 항상 로드한다.
- **낡은 서술**: "Read 한 번에 100K+ 토큰이 들어올 수 있다"(현행 하네스는 도구 출력 상한을 두고 초과분을 파일로 내린다), "md5로 폴링하라"(백그라운드 명령 완료 알림과 Monitor 도구가 있다), "`&&`로 묶어 왕복을 줄여라"(독립 도구 호출은 한 응답에서 병렬 실행된다), "출력 토큰이 2~5배 비싸다"(모델별 수치 미확인).
- **제안**: 스킬을 폐기하고 내용을 `~/.claude/rules/shared/token-efficiency.md`(또는 기존 long-running-bash.md 병합)로 옮긴다. 남길 가치가 있는 것은 구조화 질의 도구(jq/yq/rg/ast-grep) 우선, git `--stat` 먼저, 색상·verbose 억제 정도이며 30줄이면 된다. 플러그인에는 `worktree`만 남거나(G6 참조) 플러그인 자체를 정리한다.

### G6. 내장 기능과의 중복 [P2]

| 스킬 | 내장 기능 | 차이 | 판단 |
|---|---|---|---|
| `worktree` | `EnterWorktree` 도구 | 내장은 `.claude/worktrees/` 아래, 기준은 `worktree.baseRef` 설정(fresh=origin/기본 브랜치). 스킬은 `.worktrees/` 아래, 기준 `origin/develop` 고정, 충돌 검사·검증 절차 포함 | develop 기반 워크플로우(git-workflow 룰)가 필요하면 스킬이 여전히 유효. 단 `disable-model-invocation: true`가 없어 "명시 호출 시만"을 산문으로만 강제한다. 프론트매터로 박는다 |
| craft `implement` "충돌 시 worktree 격리" | Agent 도구 `isolation: "worktree"` | 스킬이 방법을 안 적음 | 한 줄로 `isolation: "worktree"` 지정 |
| document-generator `diagrams.md` 5절(데이터 차트) | 내장 `dataviz` 스킬 | 내장은 팔레트·접근성·차트 형식 일반론, 스킬은 한글 폭·SVG 좌표 규칙 | 겹치지만 대체는 아님. 차트 요청 시 dataviz 병행 로드를 언급할지 선택 |
| `design-it-twice`·`test-audit`의 병렬 스폰 + 취합 | Workflow 도구(`parallel`/`pipeline`) | Workflow는 사용자 명시 opt-in 필요 | 스킬이 의존할 수 없음. 현행 유지 |

### G7. 에이전트 frontmatter에 model·effort 없음 [P1]

- **현황**: craft `agents/*.md` 4개는 `name`, `description`, `tools`만 둔다(`tdd-implementer`는 `tools`도 없음). 규격상 `model`, `effort`, `maxTurns`, `isolation`, `memory`, `background`를 지정할 수 있다.
- **영향**: 부모 세션이 Fable 5.1이면 `interface-designer` 3~4개 병렬, `code-reviewer` 모듈별 병렬(test-audit)이 전부 최상위 모델로 돈다. 사용자 룰(multi-round-implementation.md)은 구현 에이전트를 sonnet으로 돌리는 것을 전제한다.
- **제안**: `tdd-implementer`·`verifier`(실행 위주) `model: sonnet`, `interface-designer`·`code-reviewer`(판단 위주) 상속 유지 또는 `opus`. `maxTurns`로 verifier의 재현 루프 폭주를 막는다(long-running-bash 룰의 "tool_uses 50회 cap"을 frontmatter로). 근거 없는 수치는 넣지 않고, 실제 dispatch 몇 건의 토큰·턴 기록을 본 뒤 정한다.

### G8. eval 포맷 두 벌 [P2]

- **현황**: `dlc/evals/*/case.yaml`(+scaffold.sh)은 `claude plugin eval` 포맷이고 실제로 8/8 실행 기록이 있다. `architecture-reviewer`·`document-generator`·`pr-reviewer`·`pr-automator`의 `evals/evals.json`은 skill-creator 플러그인 포맷이라 `claude plugin eval`이 읽지 않는다.
- **제안**: G4의 description 축소 효과를 재려면 발동 테스트가 필요하다. 네 플러그인의 evals.json 중 발동 판정 케이스(예: architecture-reviewer id 0·1·2, document-generator 0·8·9)를 `case.yaml`로 옮긴다. `--ablation with-without`로 "플러그인 유무 점수 차"를 얻을 수 있다.

### G9. 프로그레시브 디스클로저 훼손 [P2]

- **document-generator**: SKILL.md가 `sentence-style.md` 핵심 5항목, `diagrams.md`·`mermaid-render.md`·`html-output.md`의 다이어그램 분기 규칙을 본문에 다시 요약한다. 결과적으로 SKILL.md(5.5k) + 참조 2~3개(각 2~5k)가 함께 로드된다. 본문의 요약을 지우고 "어느 경우 어느 파일"의 표만 남기면 on-invoke가 줄어든다. 갱신 모드 규칙과 유형 표는 본문에 남긴다.
- **llm-wiki 4개**: 본문의 상당 부분이 근거 서사("실측에서 226개 중 224개…", "19회·48KB로 15~35배")다. 사람에게는 설득력이 있지만 매 호출 로드된다. Claude 5 계열에 규율을 지키게 하는 데 실측 일화가 필요한지는 문서화된 근거가 없다. 절차만 남기고 근거는 README·`references/`로 옮기면 스킬당 1.5~2k 절감이 예상된다. 스크립트 테스트는 그대로다.
- **dlc**: 스테이지 스킬마다 protocol.md(70줄)·grounding.md(46줄)·state-format.md(91줄)를 읽는다. 라우터 `--all`은 한 세션에서 스테이지 파일을 차례로 읽어 누적된다. 상태가 디스크(`docs/dlc/`)에 있어 스테이지를 `context: fork`로 격리하면 컨텍스트를 아낄 수 있으나, 승인 게이트가 사용자 대화를 요구하므로 격리 실행과 맞지 않는다. 현행 유지가 맞다. 대신 세 참조 파일 중 stage마다 정말 필요한 절만 링크하도록 좁힌다.

### G10. 반복 문구 [P2]

- craft 6개 스킬의 "(폴백) 서브에이전트 스폰을 지원하지 않는 환경(Codex 등)…" 단락과 dlc 10개의 "로드 방법은 에이전트마다 다르다…" 단락은 이식성을 위한 것이지만 Claude Code에서는 매 호출 죽은 텍스트다. 각 플러그인의 `references/portability.md` 하나로 모으고 스킬 본문에는 한 줄 포인터만 둔다.
- "출력 언어" 절이 31개 중 25개에 있다. 사용자 글로벌 CLAUDE.md §0이 이미 한국어를 강제한다. 이식성 때문에 남긴다면 한 줄이면 된다.
- Pn 룰(P1~P5) 표가 4곳(pr-reviewer SKILL·review-criteria·craft code-reviewer·dlc-verify)에 있다. 플러그인 간 공유는 불가하므로 pr-reviewer 안의 2벌만 1벌로 줄인다.

### G11. 미등재·위험 스킬 [P2]

- `pr-automator`: 마켓플레이스에서 빠져 설치 불가인데 소스가 남아 있다(README도 그렇게 적음). 4단계가 `git add -A`를 쓴다. 사용자 보안 룰(`.env` 커밋 금지)과 충돌할 수 있는 패턴이다. 복원할 계획이 없으면 `archive/`로 옮기거나 삭제한다. 복원한다면 `git status --porcelain` 목록을 보여주고 명시 경로로 add한다.
- `samples/`가 untracked 상태로 남아 있다(`git status`). 커밋 대상인지 `.gitignore` 대상인지 정한다.

### G12. archive/ 정책 [P2]

- 스킬을 고칠 때마다 이전 버전을 `archive/<스킬>/<날짜>/`에 통째로 복사한다. git 이력과 중복이고, README 스스로 `npx skills add`가 같은 이름을 둘 발견하는 문제를 적어 두었다. G4·G9로 다수 스킬을 고치면 archive가 급증한다. git tag(`llm-wiki-0.2.4` 등)로 대체하는 것을 검토한다.

## 4. 플러그인별 상세

### 4-1. document-generator (1.5.0)

- 강점: 유형별 1차 출처 기반 템플릿, 한글 레이아웃 점검 스크립트, Notion 사고 사례 축적. 참조 문서의 품질이 높다.
- 지적: G4(description 488자), G9(본문이 참조를 재요약), `<스킬경로>`(G1). `mermaid-render.md`의 "SVG를 절대 옮겨 적지 않는다"는 토큰 규율은 여전히 유효하고 좋은 예다.
- 제안: description 200자 이하, 본문에서 문장 규칙·다이어그램 분기 요약 삭제(참조 표만), `check-layout.py` 경로를 `${CLAUDE_SKILL_DIR}/assets/check-layout.py`로. evals.json 발동 케이스 3~4건을 case.yaml로.

### 4-2. pr-reviewer (1.1.0)

- 강점: 절차가 명확하고 실패 처리(422)까지 적혀 있다. `craft:code-reviewer` 위임과 인라인 폴백이 분리돼 있다.
- 지적: Pn 표 2벌(G10). `.claude/pr-reviewer.json` 인터뷰는 레포당 1회라 적정. 내장 `code-review` 스킬·`ReportFindings` 도구와 역할이 다르므로(GitHub 게시) 중복 아님.
- 제안: 표 1벌로. description에서 트리거 문구 5개 중 2개만 남긴다.

### 4-3. architecture-reviewer (1.0.0)

- 강점: 짧고(75줄) 참조가 얇다. 모드 판별이 명확하다.
- 지적: `sources.md`는 런타임에 읽을 필요가 없는데 본문이 "따른다"로 묶어 둔다. description 384자.
- 제안: sources.md를 rubric.md 하단으로 합치고 본문에서 링크 제거. description 축소.

### 4-4. craft (0.2.0)

- 강점: 에이전트 4종의 규율(반증 우선, 근거 인용, seam 없으면 중단, 재현 실패 정직 보고)이 명확하고 짧다. 스킬과 페르소나의 책임 분리 원칙이 지켜진다.
- 지적: G2(이름 충돌), G3(프로젝트 전용 5개), G7(model/effort), G10(폴백 반복), `implement`의 worktree 격리(G6). `diagnosing-bugs`가 핸드오프하는 `/improve-codebase-architecture`·`/grilling`·`/domain-modeling`은 mattpocock-skills 플러그인에 있어 유효하지만, 플러그인 한정 이름(`mattpocock-skills:grilling`)이 아닌 개인 스킬 이름으로 적혀 있어 환경에 따라 해석이 갈린다.
- 제안: 5절 P0·P1 항목. 추가로 `tdd/mocking.md`·`tests.md`·`triage/AGENT-BRIEF.md`·`OUT-OF-SCOPE.md`는 upstream verbatim 영문 복사본인데, Codex 사용자 이식성을 위해 남긴다면 유지하고 아니면 upstream 참조로 대체 가능(사용자 결정 4).

### 4-5. llm-wiki (0.2.4)

- 강점: 스크립트가 후보를 좁히고 판정만 모델이 하는 구조, 138건 회귀 테스트, 불변 영역·신호 없음 처리 원칙. `compatibility` 프론트매터는 현행 규격에 있는 정식 키다.
- 지적: G1(`<skill>` 9곳, `<wiki-bootstrap>` 1곳), G9(서사 비중), description 4개 합계 약 1,230자. README 테스트 수 137 대 실측 138.
- 제안: 경로 변수화, 본문을 절차 중심으로 40~50% 축소(근거는 references/로), description 200자 이하.

### 4-6. agent-workflow (0.1.0)

- 지적: G5(token-efficiency 전체), G6(worktree ↔ EnterWorktree), `worktree`에 `disable-model-invocation: true` 부재.
- 제안: token-efficiency는 룰 파일로 이관 후 삭제. worktree는 프론트매터 보강 후 유지하거나, `EnterWorktree` + `worktree.baseRef` 설정으로 develop 기반이 가능한지 확인한 뒤 대체. 후자는 미확인이라 실측이 필요하다.

### 4-7. dlc (0.1.0)

- 강점: 전 스킬 명시 호출형, 상태·검사를 스크립트에 위임, 출처 태그로 지어낸 요구사항 차단, eval 8건. 4라운드 리뷰를 거쳐 알려진 잔여가 문서화돼 있다.
- 지적: G1(`<skills>` 전 스테이지), G9(참조 3개 전량 로드), G10(로드 방법 단락 반복). 질문 파일 방식은 이식성 때문이지만 Claude Code에서는 `AskUserQuestion`이 사용자 룰(금지 3: 선택지를 풀어 쓴다)에 더 맞는다. protocol.md 5단계 (a)에 "Claude Code에서는 AskUserQuestion으로 묻고 답을 파일에 기록한다"를 명시하면 된다.
- 제안: r4 제안서(I1~I17)와 합쳐 한 라운드로 처리. 이 리뷰에서 새로 더한 것은 G1·G9·G10과 AskUserQuestion 명시뿐이다.

### 4-8. pr-automator (미등재)

- 3절 G11 참조. 결정 사항 5.

## 5. 우선순위 제안

| 우선순위 | 항목 | 이유 | 비용 | 검증 |
|---|---|---|---|---|
| P0 | G1 경로 변수화 (llm-wiki·dlc·document-generator) | 매 호출 추론 비용 + 오추론 시 폴백 | 문서 편집 15파일, 스크립트 무변경 | 각 스킬 1회 호출해 스크립트 실행 확인. dlc는 eval 8건 재실행 |
| P0 | G2 이름 충돌 해소 | 자동 트리거 분기 | 결정 1 + 이름 변경 시 참조 7곳 | 세션 스킬 목록에서 중복 소멸 확인 |
| P1 | G3 마케팅 5종 이관 | always-on 절반 절감, 범용성 원칙 | 파일 이동 + write-note 저장소 커밋 | `claude plugin details craft` always-on 재측정 |
| P1 | G4 description 축소 (전 스킬) | 세션당 약 2,000 토큰 | 31파일 문구 편집 | plugin details 재측정 + case.yaml 발동 eval |
| P1 | G5 token-efficiency 룰 이관 | 보장 안 되는 "항상" + 낡은 서술 | 룰 파일 1개 신설, 스킬 삭제 | 없음 |
| P1 | G7 에이전트 model/effort/maxTurns | 병렬 스폰 비용 | 4파일 프론트매터 | dispatch 2~3건 토큰 기록 비교 |
| P2 | G9 본문 축소 (document-generator·llm-wiki·dlc) | on-invoke 30~40% | 편집 + 검토 | plugin details on-invoke 재측정, 테스트·eval 유지 |
| P2 | G8 evals.json → case.yaml | 축소 효과 측정 수단 | 케이스 10건 내외 작성, 실행 비용 케이스당 $0.2~0.9 | eval 통과 |
| P2 | G6·G10·G11·G12 | 정리 | 소 | 없음 |

작업 순서 제안: G2 결정 → G3 이관 → G1·G4·G7 한 라운드(스킬 파일을 한 번만 건드리도록) → G8 eval 작성 → G9 축소를 eval로 검증 → 나머지. archive/ 정책(G12)은 첫 라운드 전에 정하는 편이 좋다. 그렇지 않으면 첫 라운드에서 archive가 20개 이상 생긴다.

## 6. 하지 않기로 한 것과 이유

- dlc 스테이지의 `context: fork` 격리: 승인 게이트가 사용자 대화를 요구하므로 격리 실행과 충돌한다.
- design-it-twice·test-audit의 Workflow 도구 전환: Workflow는 사용자 명시 opt-in이 필요해 스킬이 전제할 수 없다.
- "Claude 5는 지시를 덜 반복해도 된다"는 이유로 규율 문장을 일괄 삭제: 모델별 프롬프트 설계 변화는 문서화돼 있지 않다(가이드 확인). 축소는 토큰 근거로만 하고 효과는 eval로 잰다.
- dlc r4 제안서의 17건 재지적: 이미 문서화돼 있다.

## 7. 사용자 결정이 필요한 것

1. **craft 포크 4개의 이름 충돌을 어떻게 풀 것인가.** (a) 이름을 바꾼다: `tdd`·`diagnosing-bugs`·`triage`·`implement`를 다른 이름으로 하고 이 저장소 안의 참조 7곳을 고친다. 이후 "TDD로"라고 하면 upstream이 뜨고 craft 것은 새 이름으로만 뜬다. (b) README와 description으로 구분한다: 이름은 그대로 두고 설치 안내에 "mattpocock-skills를 함께 쓰면 disable하라"를 적는다. 사용자가 관리해야 한다. (c) 포크를 버린다: upstream 스킬 + craft 에이전트만 남긴다. 한국어 본문과 verifier 위임 경로를 잃는다.
2. **마케팅·PM 스킬 5개를 소설비 저장소로 옮길 것인가.** 옮기면 craft always-on이 약 절반으로 줄고 다른 프로젝트 세션에서 사라진다. 이 저장소에서는 `prd-ticket-writing`의 범용 절(1~4절)만 남길 수 있다. 옮기지 않으면 지금처럼 모든 세션이 비용을 내고, 존재하지 않는 `ux-mockup`·메모리 링크는 어쨌든 고쳐야 한다.
3. **token-efficiency를 스킬에서 글로벌 룰로 옮길 것인가.** 옮기면 모든 세션에 30줄 정도가 항상 실리고 스킬 로드(2.9k)가 사라진다. 그대로 두면 "항상 적용"은 보장되지 않는다.
4. **craft의 영문 verbatim 참조 4개(mocking.md, tests.md, AGENT-BRIEF.md, OUT-OF-SCOPE.md)를 유지할 것인가.** Codex 등 다른 에이전트로 `npx skills add` 설치하는 사용자가 있으면 유지가 맞다. Claude Code 전용이면 upstream 플러그인의 같은 파일을 가리키고 삭제할 수 있다.
5. **pr-automator를 살릴 것인가.** 살리면 마켓플레이스 재등재 + `git add -A` 수정이 필요하다. 아니면 archive/ 이동 또는 삭제.
6. **archive/ 정책을 git tag로 바꿀 것인가.** 바꾸면 이번 개선 라운드에서 archive 디렉터리가 늘지 않는다. 유지하면 스킬 20개 이상이 archive에 복사된다.

## 8. 진행 기록 (2026-09-16, 브랜치 `feature/skills-efficiency-r1`)

사용자 결정: 1 개명 / 2 이관 후 소설비 저장소 커밋·push / 3 글로벌 룰로 / 4 유지 / 5 삭제 / 6 archive 복사 방식 유지. 후속 범위는 G1 경로 변수화까지.

| 커밋 | 내용 | 결정·항목 |
|---|---|---|
| 053419c | craft 0.3.0: 마케팅·PM 스킬 5종 제거. 소설비 저장소 `chore/import-marketing-skills`(2baf924c, push 완료)로 이관 | 결정 2, G3 |
| 49c3ffd | craft 0.3.0: `tdd→test-first`, `diagnosing-bugs→diagnose`, `triage→issue-triage`, `implement→implement-spec`. 참조 갱신(craft·루트 README, marketplace, test-audit, dlc-plan·dlc-build). dlc 0.1.1 | 결정 1, G2 |
| 0e82ff7 | agent-workflow 0.2.0: token-efficiency 제거, `~/.claude/rules/shared/token-efficiency.md`로 이관(낡은 조항 제거) | 결정 3, G5 |
| 20fe9a0 | pr-automator 삭제, pr-reviewer 1.1.1(pr-automator 언급 제거) | 결정 5, G11 |
| f6b3e56 | `<skill>`·`<skills>`·`<스킬경로>` → `${CLAUDE_SKILL_DIR}`·`${CLAUDE_PLUGIN_ROOT}`. llm-wiki 0.2.5, dlc 0.1.1, document-generator 1.5.1 | G1 |

검증: `claude plugin validate .` 통과, llm-wiki 138건·dlc 87건 OK. 이전 버전은 전부 `archive/<스킬>/2026-09-16/`(28건). 남은 항목(G4 description 축소, G7 에이전트 model, G8 eval 포맷 통일, G9 본문 축소, G6·G10·G12)은 다음 라운드.

## 9. 2라운드 진행 기록 (2026-09-16, 같은 브랜치)

사용자 지시: gh 활성 계정은 JK-Kim4로 유지, 리뷰의 나머지 P0·P1·P2 항목 진행.

| 커밋 | 내용 | 항목 |
|---|---|---|
| 49c1c0e | craft `verifier`·`tdd-implementer`에 `model: sonnet`, `maxTurns: 50`(글로벌 룰의 tool_uses 50 cap과 정합). worktree description에 내장 EnterWorktree(기본 브랜치·`.claude/worktrees/`)와의 차이 명시 | G7, G6 |
| 5ac013f | description 축소 11개(document-generator 488→180자, wiki-bootstrap 390→177, architecture-reviewer 384→199 등). craft "(폴백)" 단락 6곳 한 문장으로. implement-spec 병렬 스폰 시 `isolation: "worktree"` | G4, G10, G6 |
| fe32cdb | SKILL.md 본문 축소 — llm-wiki 4종 실측 근거를 `references/rationale.md`로 분리(단어 수 1,189→775 / 1,182→777 / 1,063→733 / 1,324→739), document-generator 참조 재요약 제거(1,529→898) | G9 |
| (아래) | `claude plugin eval`용 case.yaml 7건 신설(architecture-reviewer 3, document-generator 3, pr-reviewer 1)과 루트 `evals-run.sh`. 기존 `evals.json`(skill-creator 포맷)은 그대로 둔다 | G8 |

G6의 worktree 항목은 리뷰 권고(`disable-model-invocation: true`)를 **적용하지 않았다.** 내장 EnterWorktree는 `worktree.baseRef`가 기본 브랜치 또는 로컬 HEAD뿐이라 origin/develop 기준 흐름을 대체하지 못한다. 플래그를 켜면 "워크트리 만들어줘"에 모델이 이 스킬을 못 고르고 EnterWorktree로 가서 기준 브랜치가 틀린다. 리뷰의 해당 권고는 이 사실로 정정한다.

하지 않은 것: dlc 스테이지 본문 축소(G9의 dlc 항목)는 참조 3개가 이미 절별로 나뉘어 있어 이득이 작아 보류. dlc r4 잔여 17건은 사용자 결정(I8·I14)이 걸려 있어 다음 라운드.

### 9-1. eval 실측 (2026-09-16, `claude plugin eval`, 총 $4.90)

| 플러그인 | 케이스 | 결과 | 비고 |
|---|---|---|---|
| pr-reviewer | no-pr-id | 3/3 통과 | 첫 실행은 부정 패턴 `gh pr diff`가 스킬 본문 예시에 걸려 거짓 실패 → 실행 형태(`gh pr diff [0-9#h]`)로 교체 |
| architecture-reviewer | diagnose-mode, direction-mode | 각 6/6 통과 | 픽스처 식별자(`StripeGateway` 등)와 `last_message`로 앵커 |
| architecture-reviewer | no-target | **0/5 실행 통과** | 발동·"리포트 없음"은 통과. 소스 Read 0~4회, 질문 표현이 실행마다 다름. 스킬 문장 강화(1.0.1) 후에도 불안정. 사용자 결정 필요(아래) |
| document-generator | readme, postmortem, progress-update | 통과 | postmortem은 `target: files`가 동작하지 않아 저장 경로를 프롬프트로 고정하고 파일 본문 채점으로 교체. `file_exists`는 에이전트가 만든 파일에만 통과 |

채점기 설계 규약(케이스 파일 주석에도 적음): 응답은 `last_message`, 산출물은 `source: file` 본문, 발동은 `tool_used: Skill` + `input_match`, trace에는 인자가 채워진 실행 형태만. 스킬 본문·참조 문서·프롬프트가 trace에 실리므로 그 안의 문자열은 양성·부정 앵커 어느 쪽으로도 쓰지 않는다.

**남은 결정(no-target)**: (a) "대상 없으면 파일을 읽지 않는다"를 지키게 할 것인가 — 그러면 SKILL.md에 절차를 더 박거나(예: `ls`만 허용) 채점기를 유지하고 스킬을 더 고친다. (b) 작은 저장소에서 한두 파일을 들여다보고 묻는 것을 허용할 것인가 — 그러면 `no-source-scan`을 빼고 "리포트 없이 묻는다"만 잰다. 어느 쪽이든 `asks-which-target`의 질문 표현 패턴은 실행 3회의 실제 문장을 모아 넓힌다.
