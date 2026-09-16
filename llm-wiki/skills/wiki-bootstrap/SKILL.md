---
name: wiki-bootstrap
description: >-
  흩어진 마크다운 저장소·Obsidian vault·AI 세션 기록을 하나의 LLM wiki로 통합하거나 새 지식베이스를 세운다. "지식베이스 만들어줘", "vault 통합", "위키 구축"에 사용한다. 인터뷰 → 실측 → 복사 이관 → 검증 → 링크 통일 → git 초기화. 개별 문서 작성이나 검색에는 쓰지 않는다.
compatibility: "python3 3.8+ 와 git 만 있으면 어느 머신에서든 동작한다. 외부 패키지 의존 없음. ripgrep 이 있으면 조사 단계가 빨라지지만 필수는 아니다."
---

# wiki-bootstrap

`${CLAUDE_SKILL_DIR}`는 Claude Code가 스킬을 로드할 때 이 스킬 디렉터리의 절대 경로로 치환한다. 치환되지 않는 환경(`npx skills add`로 설치한 Codex·Gemini)에서는 이 SKILL.md가 있는 디렉터리를 뜻한다.

흩어진 마크다운을 하나의 LLM wiki로 만드는 파이프라인. Karpathy의 3계층 모델(원본은 불변, 가공물은 LLM 소유, 규약은 파일로)을 따르되 상주 서버나 특정 도구에 묶이지 않는 순수 마크다운 구조를 만든다.

**핵심 원칙: 측정하고, 복사하고, 대조한다.** 이관은 되돌리기 어렵고 문서는 사용자가 수년간 쌓은 것이다. 옮기기 전에 재고를 세고, 이동이 아니라 복사로 하고, 옮긴 뒤 숫자를 맞춘다.

## 언제 무엇을 읽나

- 인터뷰 질문과 선택지별 트레이드오프·추천 근거 → `references/interview.md`
- 이관에서 실제로 터진 함정 10가지와 처리법 → `references/pitfalls.md` (**이관 전에 반드시 읽는다**)

## 파이프라인

### 1. 재고 조사

인터뷰보다 조사가 먼저다. 숫자가 있어야 사용자가 답할 수 있다.

후보 디렉터리를 찾는다(`~/obsidian/*`, `~/Documents/*`, `~/notes`, `~/wiki`, `~/dev/*` 등 마크다운이 몰린 곳, `.obsidian/`이 있는 곳, `.git`이 있는 문서 저장소).

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/survey.py ~/obsidian/vault-a ~/notes ~/dev/kb --json before.json
```

저장소별 마크다운 수, 링크 문법 분포(wikilink vs 마크다운 링크), 프론트매터 보유율, **깨진 링크 수**가 나온다. `--json`으로 저장해 이관 후 대조에 쓴다(깨진 링크 베이스라인이 없으면 이관 후 깨짐이 내 탓인지 판별할 수 없다 — pitfalls 1).

AI 세션 기록(`~/.claude/projects/`, `~/.codex/sessions/`)도 조사 대상이다. **Claude Code는 기본 30일 보존이라** 세션을 원료로 쓸 계획이면 이관 전에 확보한다(pitfalls 6).

조사 결과를 표로 보여준다.

### 2. 인터뷰

`references/interview.md`의 질문(Q1~Q7)을 순서대로, **한 번에 하나씩**, 조사에서 나온 실측값을 붙여서 묻는다("A는 wikilink 75파일, B는 마크다운 링크 266파일입니다. 통일할까요?"). 질문마다 근거 있는 **추천을 반드시 붙이되** 다른 선택지도 진짜 선택지로 남긴다.

### 3. 구조 생성

인터뷰에서 정한 루트에 만든다. 기본 골격:

```
<root>/
├── 00-INDEX.md          단일 진입점
├── log.md               변경 이력 (턴당 한 항목)
├── .gitignore
├── knowledge/           확정 지식 — 프로젝트를 넘어 재사용되는 것
├── projects/<name>/     프로젝트별 현재 상태 (통합 대상 아님)
├── sessions/            AI 세션 기록 가공본
├── retrospectives/      회고
├── templates/           신규 문서의 출발점
└── raw/                 세션 원본 — git 제외, 인용 대상 아님
```

**내용이 있는 폴더만 만든다.** `sources/`·`notes/`는 넣을 것이 생겼을 때 만든다. "아직 확정 아님"은 디렉터리가 아니라 `status:` 프론트매터가 나른다(interview Q4).

### 4. 이관 — 이동이 아니라 복사

```bash
cp -R <원본>/. <대상>/
```

**`mv`를 쓰지 않는다**(pitfalls 7). 도구 설정(`.git`, `.obsidian`, `.ok`, `.mcp.json`, 에디터 스캐폴드)은 가져가지 않되, **`.gitignore`류 제외 규칙의 의도는 새 `.gitignore`로 옮긴다**(pitfalls 8). 저장소 내부 상대 링크가 많은 곳은 구조를 쪼개지 않고 통째로 옮긴다.

### 5. 이관 검증 — 숫자를 맞춘다

원본과 대상의 파일 수를 **항목별로** 대조해 보여준다.

```
sessions        226 → 226
retrospectives   91 → 91
projects/...    546 → 546
```

숫자가 안 맞으면 원인을 찾을 때까지 넘어가지 않는다. **차이를 정확히 설명할 수 있어야 정상이다**(pitfalls 9).

### 6. 링크 통일 (인터뷰에서 "통일"을 택했을 때만)

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/wikilink_convert.py <root>            # 건식 — 아무것도 쓰지 않음
python3 ${CLAUDE_SKILL_DIR}/scripts/wikilink_convert.py <root> --apply    # 적용
```

**반드시 건식 실행부터.** 결과의 미해결 항목은 이관 때문인지 원래 없던 대상인지 원본 저장소에서 확인한다. 원래 없던 링크는 지우지 않는다(pitfalls 10). 변환기는 이름 매칭이 여럿이면 같은 디렉터리 → 같은 최상위 트리 순으로 좁히고, 그래도 못 정하면 모호로 남긴다(pitfalls 4·5).

### 7. 링크 건전성 대조

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/survey.py <root> --json after.json
```

이관 전 원본들의 깨진 링크 합계와 비교한다. **늘지 않았으면 성공이다** — 0이 목표가 아니다. 늘었다면 디렉터리 개명(pitfalls 2)·트리 깊이 변화(pitfalls 3)를 먼저 의심한다.

### 8. 진입점과 git

`00-INDEX.md`에 구조 표, 프로젝트 목록, **규약**(링크 문법, 불변 영역, `status:` 사용법, 로그 규칙, 검색 방법)을 쓴다. 다음 에이전트가 읽을 유일한 계약이다.

`.gitignore`에 대용량 원본 디렉터리를 **먼저** 넣고 `git init` → 첫 커밋. 커밋 메시지에 검증 수치를 남긴다.

### 9. 루트 위치 기록

이후 스킬(wiki-digest·wiki-lint·wiki-recall)이 위키를 찾을 수 있게 표준 위치에 기록한다. 경로는 머신마다 다르므로 **여기에만** 두고 스킬 본문에는 넣지 않는다.

```bash
mkdir -p ~/.config/llm-wiki
cat > ~/.config/llm-wiki/config.json <<EOF
{ "root": "<절대경로>", "raw": "raw", "sessions": "sessions" }
EOF
```

## 테스트

```bash
python3 -m unittest discover -s ${CLAUDE_SKILL_DIR}/tests
```

**스크립트를 고치면 여기부터 돌린다.** 상당수가 실사용 회귀 방지 테스트다.

## 마무리

무엇이 만들어졌고 무엇이 아직 없는지 알린다. 세션 가공·점검은 다른 스킬의 범위다. 원본 저장소는 지우지 않는다 — 며칠 써보고 사용자가 판단한다.
