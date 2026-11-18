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
| `document-generator` | [`document-generator/2026-11-02/`](document-generator/2026-11-02/) | document-generator 1.5.0 | #11 — 스킬을 `doc-writing`으로 교체(document-generator 2.0.0) |
| `herdr-flow`(공용 묶음) | [`herdr-flow/2026-11-18/`](herdr-flow/2026-11-18/) | herdr-flow 0.2.0 | 페르소나·체크리스트 기록 주체 변경, 진입점 SKILL.md 추가(herdr-flow 0.3.0) |
| `herdr-flow-brief` | [`herdr-flow-brief/2026-11-18/`](herdr-flow-brief/2026-11-18/) | herdr-flow 0.2.0 | 모델 대신 페르소나로 세션 기동, 하위 세션은 체크리스트에 쓰지 않음(herdr-flow 0.3.0) |
| `herdr-flow-verify` | [`herdr-flow-verify/2026-11-18/`](herdr-flow-verify/2026-11-18/) | herdr-flow 0.2.0 | 오케스트레이터가 done 기록, 약속한 후속 예약·운영 세션 화면 확인(herdr-flow 0.3.0) |
| `herdr-handoff` | [`herdr-handoff/2026-11-18/`](herdr-handoff/2026-11-18/) | herdr-flow 0.2.0 | 공용 디렉터리 설명 문구만 변경(herdr-flow 0.3.0) |

## 주의

- 여기 있는 `SKILL.md`는 마켓플레이스에 등록되지 않는다. `marketplace.json`은 플러그인 디렉터리만 가리킨다.
- `npx skills add JK-Kim4/claude-plugins`는 저장소 전체에서 `SKILL.md`를 찾는다. skills CLI 1.5.26에서는 같은 이름이 둘이어도 목록에 하나만 나오고 `--skill wiki-lint` 설치 시 플러그인 쪽 최신 버전이 설치됐다(2026-09-14 실측). 이 선택 규칙은 문서화된 계약이 아니므로 CLI 버전이 바뀌면 다시 확인한다.
