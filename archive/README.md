# archive — 스킬 이전 버전 보관

플러그인의 `skills/` 아래에는 **최신 버전만** 둔다. 스킬을 고쳐 이전 버전이 밀려나면, 그 이전 버전을 여기에 통째로 옮겨 보관한다. 이전 버전을 찾을 때 git 이력을 뒤지지 않고 이 디렉터리에서 바로 꺼내 쓰기 위한 것이다.

## 구조

```
archive/<스킬명>/<YYYY-MM-DD>/   교체되기 직전의 스킬 디렉터리 전체(SKILL.md·references·scripts·tests)
```

- `<YYYY-MM-DD>`는 그 버전이 **교체된 날**(교체 PR 병합일)이다. 같은 날 두 번 교체되면 `2026-09-13-2`처럼 순번을 붙인다.
- 스킬 디렉터리는 내용을 고치지 않고 그대로 옮긴다. `__pycache__` 같은 실행 산출물은 넣지 않는다.

## 보관 절차

1. 스킬을 고치는 PR에서, 수정 전에 현재 스킬 디렉터리를 `archive/<스킬명>/<교체일>/`로 복사한다.
2. 아래 목록에 한 줄 추가한다.
3. 같은 PR에서 스킬을 고치고 플러그인 버전(`plugin.json`)을 올린다.

## 목록

| 스킬 | 보관 디렉터리 | 플러그인·버전 | 교체한 변경 |
|---|---|---|---|
| `wiki-lint` | [`wiki-lint/2026-09-13/`](wiki-lint/2026-09-13/) | llm-wiki 0.2.1 | #6 — 깨진 링크에 「외부(위키 밖)」 분류 추가(llm-wiki 0.2.4) |
| `marketing-strategy` | [`marketing-strategy/2026-09-16/`](marketing-strategy/2026-09-16/) | craft 0.2.0 | 소설비 전용 스킬을 프로젝트 저장소(soseolbi `.claude/skills/`)로 이관하며 craft에서 제거(craft 0.3.0) |
| `pm-breakdown` | [`pm-breakdown/2026-09-16/`](pm-breakdown/2026-09-16/) | craft 0.2.0 | 소설비 전용 스킬을 프로젝트 저장소(soseolbi `.claude/skills/`)로 이관하며 craft에서 제거(craft 0.3.0) |
| `prd-ticket-writing` | [`prd-ticket-writing/2026-09-16/`](prd-ticket-writing/2026-09-16/) | craft 0.2.0 | 소설비 전용 스킬을 프로젝트 저장소(soseolbi `.claude/skills/`)로 이관하며 craft에서 제거(craft 0.3.0) |
| `retention-playbook` | [`retention-playbook/2026-09-16/`](retention-playbook/2026-09-16/) | craft 0.2.0 | 소설비 전용 스킬을 프로젝트 저장소(soseolbi `.claude/skills/`)로 이관하며 craft에서 제거(craft 0.3.0) |
| `tdd` | [`tdd/2026-09-16/`](tdd/2026-09-16/) | craft 0.2.0 | 공식 mattpocock-skills 플러그인과의 이름 충돌 해소를 위해 `test-first`으로 개명(craft 0.3.0) |
| `diagnosing-bugs` | [`diagnosing-bugs/2026-09-16/`](diagnosing-bugs/2026-09-16/) | craft 0.2.0 | 공식 mattpocock-skills 플러그인과의 이름 충돌 해소를 위해 `diagnose`으로 개명(craft 0.3.0) |
| `triage` | [`triage/2026-09-16/`](triage/2026-09-16/) | craft 0.2.0 | 공식 mattpocock-skills 플러그인과의 이름 충돌 해소를 위해 `issue-triage`으로 개명(craft 0.3.0) |
| `implement` | [`implement/2026-09-16/`](implement/2026-09-16/) | craft 0.2.0 | 공식 mattpocock-skills 플러그인과의 이름 충돌 해소를 위해 `implement-spec`으로 개명(craft 0.3.0) |
| `acquisition-playbook` | [`acquisition-playbook/2026-09-16/`](acquisition-playbook/2026-09-16/) | craft 0.2.0 | 소설비 전용 스킬을 프로젝트 저장소(soseolbi `.claude/skills/`)로 이관하며 craft에서 제거(craft 0.3.0) |
| `token-efficiency` | [`token-efficiency/2026-09-16/`](token-efficiency/2026-09-16/) | agent-workflow 0.1.0 | "항상 적용" 규율을 스킬로는 보장할 수 없어 사용자 글로벌 룰(`~/.claude/rules/shared/token-efficiency.md`)로 이관하고 제거(agent-workflow 0.2.0) |
| `pr-automator` | [`pr-automator/2026-09-16/`](pr-automator/2026-09-16/) | pr-automator 1.0.0 (미등재) | 마켓플레이스에서 빠진 뒤 설치 불가 상태로 남아 있던 플러그인을 삭제. `git add -A` 커밋 절차도 보안 룰과 맞지 않았다 |
| `pr-reviewer` | [`pr-reviewer/2026-09-16/`](pr-reviewer/2026-09-16/) | pr-reviewer 1.1.0 | pr-automator 삭제에 따라 description·3단계의 pr-automator 언급 제거(pr-reviewer 1.1.1) |
| `wiki-bootstrap` | [`wiki-bootstrap/2026-09-16/`](wiki-bootstrap/2026-09-16/) | llm-wiki 0.2.4 | 스크립트 경로 자리표시자 `<skill>`를 `${CLAUDE_SKILL_DIR}`로(llm-wiki 0.2.5) |
| `wiki-digest` | [`wiki-digest/2026-09-16/`](wiki-digest/2026-09-16/) | llm-wiki 0.2.4 | 스크립트 경로 자리표시자 `<skill>`를 `${CLAUDE_SKILL_DIR}`로(llm-wiki 0.2.5) |
| `wiki-lint` | [`wiki-lint/2026-09-16/`](wiki-lint/2026-09-16/) | llm-wiki 0.2.4 | 스크립트 경로 자리표시자 `<skill>`를 `${CLAUDE_SKILL_DIR}`로(llm-wiki 0.2.5) |
| `wiki-recall` | [`wiki-recall/2026-09-16/`](wiki-recall/2026-09-16/) | llm-wiki 0.2.4 | 스크립트 경로 자리표시자 `<skill>`를 `${CLAUDE_SKILL_DIR}`로(llm-wiki 0.2.5) |
| `dlc` | [`dlc/2026-09-16/`](dlc/2026-09-16/) | dlc 0.1.0 | 스크립트 경로 `<skills>/dlc/scripts/dlc.py`를 `${CLAUDE_PLUGIN_ROOT}/skills/dlc/scripts/dlc.py`로(dlc 0.1.1). dlc-plan·dlc-build는 craft 개명 참조 갱신 포함 |
| `dlc-init` | [`dlc-init/2026-09-16/`](dlc-init/2026-09-16/) | dlc 0.1.0 | 스크립트 경로 `<skills>/dlc/scripts/dlc.py`를 `${CLAUDE_PLUGIN_ROOT}/skills/dlc/scripts/dlc.py`로(dlc 0.1.1). dlc-plan·dlc-build는 craft 개명 참조 갱신 포함 |
| `dlc-analyze` | [`dlc-analyze/2026-09-16/`](dlc-analyze/2026-09-16/) | dlc 0.1.0 | 스크립트 경로 `<skills>/dlc/scripts/dlc.py`를 `${CLAUDE_PLUGIN_ROOT}/skills/dlc/scripts/dlc.py`로(dlc 0.1.1). dlc-plan·dlc-build는 craft 개명 참조 갱신 포함 |
| `dlc-intent` | [`dlc-intent/2026-09-16/`](dlc-intent/2026-09-16/) | dlc 0.1.0 | 스크립트 경로 `<skills>/dlc/scripts/dlc.py`를 `${CLAUDE_PLUGIN_ROOT}/skills/dlc/scripts/dlc.py`로(dlc 0.1.1). dlc-plan·dlc-build는 craft 개명 참조 갱신 포함 |
| `dlc-practices` | [`dlc-practices/2026-09-16/`](dlc-practices/2026-09-16/) | dlc 0.1.0 | 스크립트 경로 `<skills>/dlc/scripts/dlc.py`를 `${CLAUDE_PLUGIN_ROOT}/skills/dlc/scripts/dlc.py`로(dlc 0.1.1). dlc-plan·dlc-build는 craft 개명 참조 갱신 포함 |
| `dlc-requirements` | [`dlc-requirements/2026-09-16/`](dlc-requirements/2026-09-16/) | dlc 0.1.0 | 스크립트 경로 `<skills>/dlc/scripts/dlc.py`를 `${CLAUDE_PLUGIN_ROOT}/skills/dlc/scripts/dlc.py`로(dlc 0.1.1). dlc-plan·dlc-build는 craft 개명 참조 갱신 포함 |
| `dlc-design` | [`dlc-design/2026-09-16/`](dlc-design/2026-09-16/) | dlc 0.1.0 | 스크립트 경로 `<skills>/dlc/scripts/dlc.py`를 `${CLAUDE_PLUGIN_ROOT}/skills/dlc/scripts/dlc.py`로(dlc 0.1.1). dlc-plan·dlc-build는 craft 개명 참조 갱신 포함 |
| `dlc-plan` | [`dlc-plan/2026-09-16/`](dlc-plan/2026-09-16/) | dlc 0.1.0 | 스크립트 경로 `<skills>/dlc/scripts/dlc.py`를 `${CLAUDE_PLUGIN_ROOT}/skills/dlc/scripts/dlc.py`로(dlc 0.1.1). dlc-plan·dlc-build는 craft 개명 참조 갱신 포함 |
| `dlc-build` | [`dlc-build/2026-09-16/`](dlc-build/2026-09-16/) | dlc 0.1.0 | 스크립트 경로 `<skills>/dlc/scripts/dlc.py`를 `${CLAUDE_PLUGIN_ROOT}/skills/dlc/scripts/dlc.py`로(dlc 0.1.1). dlc-plan·dlc-build는 craft 개명 참조 갱신 포함 |
| `dlc-verify` | [`dlc-verify/2026-09-16/`](dlc-verify/2026-09-16/) | dlc 0.1.0 | 스크립트 경로 `<skills>/dlc/scripts/dlc.py`를 `${CLAUDE_PLUGIN_ROOT}/skills/dlc/scripts/dlc.py`로(dlc 0.1.1). dlc-plan·dlc-build는 craft 개명 참조 갱신 포함 |
| `document-generator` | [`document-generator/2026-09-16/`](document-generator/2026-09-16/) | document-generator 1.5.0 | `<스킬경로>`·상대 `assets/` 경로를 `${CLAUDE_SKILL_DIR}`로(document-generator 1.5.1) |

## 주의

- 여기 있는 `SKILL.md`는 마켓플레이스에 등록되지 않는다. `marketplace.json`은 플러그인 디렉터리만 가리킨다.
- `npx skills add JK-Kim4/claude-plugins`는 저장소 전체에서 `SKILL.md`를 찾는다. skills CLI 1.5.26에서는 같은 이름이 둘이어도 목록에 하나만 나오고 `--skill wiki-lint` 설치 시 플러그인 쪽 최신 버전이 설치됐다(2026-09-14 실측). 이 선택 규칙은 문서화된 계약이 아니므로 CLI 버전이 바뀌면 다시 확인한다.
