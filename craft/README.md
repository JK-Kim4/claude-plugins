# craft

개발 파이프라인 단계별 **페르소나 sub agent 4종**과 이를 오케스트레이션하는 **스킬 세트**.

설계 원칙: 절차·판단 기준은 스킬에, 비대화형 실행 역할의 성격·도구 권한은 페르소나에 둔다(중복 금지). Matt Pocock 엔지니어링 스킬 팩에서 바인딩·개선이 필요한 스킬만 선택적으로 포크했다(fork-on-write). 포크 파일 상단에 upstream·포크 시점을 기록한다.

## 페르소나 (agents/)

| 페르소나 | 역할 | 도구 | 스폰하는 스킬 |
|---|---|---|---|
| `verifier` | 주장 검증·버그 재현·루프 구축·최소화 | 읽기+실행+스크래치 쓰기 | triage, diagnosing-bugs |
| `interface-designer` | deep module 인터페이스 대안 설계 | 읽기 전용 | design-it-twice |
| `tdd-implementer` | 합의된 seam에서 red-green 구현 | 전체 | implement, tdd |
| `code-reviewer` | 근거 인용 리뷰 (Fowler smell 12종 + Pn 룰 내장) | 읽기 전용 | test-audit, pr-reviewer(플러그인) |

## 스킬 (skills/)

- `triage` — 포크. 주장 검증 단계를 verifier에 위임
- `diagnosing-bugs` — 포크. Phase 1~2(루프·재현·최소화)를 verifier에 위임 가능, Phase 6 blameless+5 Whys
- `design-it-twice` — codebase-design의 참조 문서를 독립 스킬로 승격. interface-designer 병렬 스폰, 착지는 테크 스펙 5섹션
- `tdd` — 포크. 테스트 비용 규율 4항목(최저 충분 레벨·행위당 1테스트·통합테스트 예산·커버리지는 지표) 추가
- `implement` — 포크. seam·예산 게이트 후 tdd-implementer 스폰 오케스트레이션
- `test-audit` — 신규. 기존 테스트 스위트를 TDD 규율로 진단, 정리 대상(삭제/병합/레벨 하강) 제안

## 설치

### Claude Code (플러그인 — 페르소나 agent 포함, 권장)

```
/plugin marketplace add JK-Kim4/claude-plugins   # 이 repo를 마켓플레이스로 등록 (최초 1회)
/plugin install craft@jongwan-plugins
```

설치 후 포크 원본과의 트리거 충돌을 막으려면 `~/.claude/skills/`에서 다음 심링크를 제거한다: `triage`, `diagnosing-bugs`, `tdd`, `implement`. (codebase-design은 포크하지 않았으므로 유지 — design-it-twice가 어휘 원본으로 참조한다.)

### Codex 등 다른 에이전트 (skills CLI — 스킬만, 에이전트 선택 설치)

```
npx skills add JK-Kim4/claude-plugins
```

실행하면 repo에서 발견된 스킬 목록과 설치 대상 에이전트(Codex, Cursor, Gemini CLI 등)를 인터랙티브하게 고를 수 있다. **Claude Code는 대상에서 제외**할 것 — Claude는 위 플러그인 설치와 중복된다.

제약: 페르소나 agent(`agents/`)는 Claude Code 전용이다. 다른 에이전트에서는 각 스킬의 *(폴백)* 문구에 따라 같은 규율을 현재 세션에서 인라인 적용한다. 스폰 지시(`craft:verifier` 등)는 Claude Code에서만 동작한다.

## 참고 문서

- 설계 배경·단계별 원칙 논의: `docs/design/2026-07-17-craft-plugin-design.md`
- 한국 IT 현업 관행 조사(포크 고도화 근거): `docs/research/2026-07-17-korean-it-practices.md`
