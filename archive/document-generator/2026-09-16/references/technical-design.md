# 기술 설계/분석 문서 (Technical Design & Analysis)

기술적 결정과 그 근거를 기록하는 문서. ADR(Architecture Decision Record), 설계 문서, 기술 분석, 트러블슈팅 정리가 여기에 속한다. **독자(미래의 팀원, 리뷰어, 결정을 잊어버린 나)는 "왜 이렇게 했는가, 다른 선택지는 없었나, 무엇을 포기했나"를 알고 싶어 한다.**

이 문서의 권고는 Michael Nygard의 원조 ADR 글, MADR 템플릿, AWS Prescriptive Guidance, Google "Design Docs at Google", ThoughtWorks Technology Radar, UK GDS Way에 근거한다(하단 출처 참조).

## 핵심 원칙

- **이유(why)가 본체다.** ADR의 가장 강력한 점은 *어떻게 구현하는가*가 아니라 *왜 이 결정을 했는가*에 집중한다는 것이다. 이유가 남으면 참여하지 않았던 사람도 결정을 받아들이고, 나중에 같은 논의를 반복하거나 결정을 무심코 뒤집는 일을 막는다. (AWS)
- **고려한 대안을 반드시 적는다.** "고려한 대안"은 가장 중요한 절 중 하나로, 선택한 해법이 *왜* 최선인지를 대안들의 바람직하지 않은 트레이드오프와 대비해 보여준다. 대안 없이 결정만 적으면 신뢰가 생기지 않는다. (Google; MADR)
- **결과(consequences)는 긍정·부정·중립을 모두 적는다.** 부정적 결과를 숨기지 않는 것이 정직하고, 미래의 재검토 기준이 된다. (Nygard)
- **결정 하나당 문서 하나, 한두 페이지.** 결정이 커지면 분리한다. 미래 개발자와의 대화처럼 간결하게 쓴다. (AWS; Nygard)
- **Context는 가치중립적으로.** 배경을 적는 절에서 결론을 미리 선취하지 않는다. (Nygard)

## 구조 — ADR (Nygard 5섹션 + MADR 확장)

```markdown
# ADR-NNNN: [결정 제목 — 짧은 명사구]
**상태: Proposed**  ·  _날짜: YYYY-MM-DD_  ·  _결정자: OOO_

## 배경 / 문제 (Context)
[어떤 힘들이 작용하는가 — 기술적·조직적 제약. 가치중립적으로. 아직 결론을 내리지 않는다.]

## 고려한 대안 (Considered Options)
- **[대안 A]**: 어떤 방식인가 — 장점 / 단점
- **[대안 B]**: ... — 장점 / 단점
- **[채택안]**: ... — 장점 / 단점

## 결정 (Decision)
[무엇을 하기로 했는가. 능동태·완전한 문장으로: "우리는 ___ 한다(We will …)".]

## 결과 (Consequences)
- **긍정적:** 무엇을 얻는가
- **부정적:** 무엇을 포기/감수하는가 (반드시 적는다)
- **중립적:** 부수적으로 달라지는 것

## 검증 (Confirmation)  [선택]
[이 결정의 준수를 어떻게 확인하는가 — 코드/설계 리뷰, 자동화 테스트(예: ArchUnit) 등.]
```

### Status 라이프사이클 (출처: AWS, MADR, GDS)
`Proposed` → 리뷰 → `Accepted` 또는 `Rejected`. 나중에 더 나은 결정이 나오면 새 ADR을 만들고, **수락된 ADR은 불변(immutable)으로 두되 상태를 `Superseded by ADR-NNNN`으로 바꾼다.** 옛 ADR은 삭제하지 않고 결정 로그에 남긴다. Rejected는 거부 사유를 적어 같은 논쟁의 재발을 막는다.

## 구조 — 큰 설계 문서 (Design Doc)

ADR보다 큰 단위라면 Google design doc 골격을 쓴다: **Context and scope / Goals and Non-goals / 실제 설계 / 고려한 대안 / 횡단 관심사(보안·프라이버시·관측가능성)**. Non-goal은 "목표가 될 수도 있었지만 명시적으로 제외한 것"으로 적는다. 분량은 큰 프로젝트 10~20페이지, 점진적 개선은 1~3페이지. (Google)

## 구조 — 기술 분석 / 트러블슈팅

```markdown
# [분석 주제]

## 요약
[조사 결론을 먼저. 원인은 X였고, 권장 조치는 Y다.]

## 현상 / 질문
[무엇을 조사했는가. 어떤 증상 또는 질문에서 출발했나.]

## 조사 내용
[확인한 사실들 — 코드/로그/측정 근거와 함께. 추측과 확인된 사실을 구분한다.]

## 원인 / 결론
[조사로 도출한 결론. 근거와 함께.]

## 권장 조치
[다음에 무엇을 해야 하는가. 우선순위가 있으면 표시.]
```

## 안티패턴 (AWS가 명시)

- 잘못된 선택이 두려워 **아무 결정도 내리지 않음**.
- **근거 없이 결정** → 같은 주제가 반복 논의됨.
- 결정을 **저장소에 기록하지 않음** → 팀원이 잊거나 모름.

## 작성 팁

- **아키텍처·흐름·상태는 다이어그램으로 보강한다.** 컴포넌트 구조, 이벤트/처리 흐름, 상태 전이는 글보다 그림이 직관적이다. HTML 출력이면 `references/diagrams.md`의 인라인 SVG 방식으로(아키텍처/컴포넌트·시퀀스·상태 전이·ER) 표현한다. ASCII 아트는 쓰지 않는다.
- 결정 근거가 되는 사실(벤치마크 수치, 코드 동작, 제약)은 추측하지 말고 실제로 확인해 적는다.
- "최선", "더 좋음"은 비교 기준과 함께("쓰기 처리량 기준 2배 빠름").
- ADR/설계 문서는 위키가 아니라 **코드 저장소(version control)**에 두어 코드와 함께 버전 관리한다. 특정 앱에 영향 주는 결정은 그 앱 저장소에. (ThoughtWorks; GDS)
- 미해결로 남긴 가정은 "열린 질문" 한 줄로 남겨 미래의 재검토를 돕는다.

## 근거 출처

- Michael Nygard — Documenting Architecture Decisions (2011): https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions.html
- MADR (Markdown ADR): https://adr.github.io/madr/ · 템플릿 비교: https://adr.github.io/adr-templates/
- AWS Prescriptive Guidance — ADR process: https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html · best practices: https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/best-practices.html
- Google — Design Docs at Google: https://www.industrialempathy.com/posts/design-docs-at-google/
- ThoughtWorks Technology Radar — Lightweight ADRs: https://www.thoughtworks.com/radar/techniques/lightweight-architecture-decision-records
- UK GDS Way — Architecture decisions: https://gds-way.digital.cabinet-office.gov.uk/standards/architecture-decisions.html
