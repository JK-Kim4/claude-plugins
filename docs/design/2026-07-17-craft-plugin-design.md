# craft 플러그인 설계 (2026-07-17)

개발 파이프라인 6단계를 단계별로 논의해 확정한 페르소나 sub agent + 스킬 세트의 설계 기록.

## 핵심 설계 결정

1. **하이브리드 구조**: 스킬 단일 관리(Matt Pocock 방식)를 척추로 유지하고, 페르소나는 **비대화형 + 격리 이득이 실재하는 역할에만** 추출한다. 근거: sub agent는 실행 중 사용자에게 질문할 수 없으므로 인터뷰형 규율(grilling, domain-modeling, qa)은 구조적으로 페르소나 부적합.
2. **중복 금지**: 같은 규칙을 스킬과 페르소나 양쪽에 두지 않는다. 페르소나 = 역할의 성격·판단 기준·도구 권한, 스킬 = 절차·산출물 형식. 스킬은 페르소나를 스폰으로 참조만 한다.
3. **선택적 포크(fork-on-write)**: 바인딩하거나 개선할 Matt 스킬만 포크한다. 포크 파일 상단에 upstream·포크 시점 기록. 포크한 스킬의 원본 심링크는 `~/.claude/skills/`에서 제거해 트리거 충돌을 막는다.
4. **한국 현업 관행 반영**: 규모 있는 설문·기업 공식 기술블로그 1차 자료 기준 (`docs/research/2026-07-17-korean-it-practices.md`). 주요 반영: Pn 룰(P1~P5, 뱅크샐러드 원문), 테크 스펙 5섹션(ADR은 옵션), 테스트 비용 규율의 1차 근거(우아한형제들·토스), PR 크기 가드(300~1,000줄), 질문형·제안형 코멘트 톤, blameless+5 Whys.

## 단계별 판정 요약

| 단계 | 페르소나 추출 | 포크 | 비고 |
|---|---|---|---|
| 1 요구사항·계획 | verifier (주장 검증) | triage | 인터뷰 규율(grilling 등)은 스킬 유지 |
| 2 설계·도메인 모델링 | interface-designer | design-it-twice (참조 문서→독립 스킬 승격) | codebase-design 본체는 어휘 허브라 포크 안 함 |
| 3 구현 | tdd-implementer | tdd, implement | 테스트 비용 규율 4항목 신설: 최저 충분 레벨 / 행위당 1테스트 / 통합테스트 예산 / 커버리지는 지표. 리팩토링은 실행 않고 보고 |
| 4 검증·디버깅 | (verifier로 통합 — 옵션 A) | diagnosing-bugs | Phase 1~2 위임, Phase 3~6은 메인 세션(가설 랭킹 사용자 체크포인트 유지) |
| 5 리뷰 | code-reviewer (smell 12종 내장) | 없음 (pr-reviewer는 repo 소유라 직접 수정) | Spec 축은 내장 지식이 없어 페르소나화 안 함 |
| 6 지식화·핸드오프 | 없음 | 없음 | 원료가 대화 컨텍스트라 구조적 부적합. 기존 to-wiki·obsidian-vault·document-generator 담당 |

- 신규 스킬 `test-audit`: 기존 스위트를 TDD 규율로 소급 진단(레벨 분류→병렬 진단→중복 행위 분석→정리 제안). code-reviewer 페르소나 재사용, 분석만 하고 실행 안 함.
- 이름 `craft`: dev-flow는 회사 프로젝트명(flow)과 충돌해 기각.

## 배포·운영

- 마켓플레이스: 이 repo (`JK-Kim4/claude-plugins`, 로컬 `~/doc-gen-plugin`). 다른 PC: `/plugin marketplace add JK-Kim4/claude-plugins` → `/plugin install craft@jongwan-plugins`.
- 설치 후 정리: `~/.claude/skills/`에서 `triage`, `diagnosing-bugs`, `tdd`, `implement` 심링크 제거.
- 페르소나 참조명: `craft:verifier` 등 (플러그인 네임스페이스).
- 추후 후보(이번 범위 제외): KPT 회고 스킬, blameless 포스트모템 템플릿(document-generator 쪽), 환경 맵 질의 규칙, to-prd/to-issues 한국화, code-review(로컬 diff) 포크.
