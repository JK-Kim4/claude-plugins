# 진행/추적 문서 (Progress & Tracking)

진행 상황을 추적하고 다음 할 일을 관리하는 문서. 작업 체크리스트, 프로젝트 진행 현황, 상태 리포트, 이슈/마일스톤 추적이 여기에 속한다. **독자(나중의 나 또는 팀)는 "무엇이 끝났고, 무엇이 남았고, 지금 막힌 게 뭔가"를 한눈에 보고 싶어 한다.**

이 문서의 권고는 Atlassian/Jira의 RAG(상태등) 가이드, Asana·Tempo·Plane의 status report 모범 사례, GitHub task list 문서에 근거한다(하단 출처 참조).

## 핵심 원칙

- **상단에 health 지표를 고정한다.** 문서 맨 위에 RAG(Red-Amber-Green, 신호등) 한 줄: **🟢 On Track / 🟡 At Risk / 🔴 Off Track**. 가장 널리 쓰이는 상태 표기다. (Atlassian; Asana; Tempo)
- **지표는 낙관이 아니라 현실을 반영한다.** "On Track"인데 리스크 섹션이 차 있으면 모순이고, 이 모순은 어떤 지연보다 빠르게 신뢰를 무너뜨린다. 색을 적기 전에 리스크 섹션과 충돌하지 않는지 점검한다. (Plane)
- **스캔 가능해야 한다.** 줄글이 아니라 체크박스·표로. 상태를 한눈에 훑을 수 있어야 한다.
- **살아있는 문서다.** 정해진 주기(cadence)로 갱신되는 것을 전제로, 갱신하기 쉽게 만든다.

## 구조

```markdown
# [작업/프로젝트명] 진행 현황
**상태: 🟡 At Risk**  ·  _최종 갱신: YYYY-MM-DD_  ·  _다음 갱신: YYYY-MM-DD_

## 요약
[2~3문장. 현재 단계와 가장 중요한 한 가지(주로 막힌 것).]

## 진행 상황
- [x] 완료된 항목
- [ ] 진행 중 항목  #이슈번호
- [ ] 대기 항목

## 🚧 Blocker / 의존성
[단순 나열이 아니라 "누가 · 무엇을 · 언제까지"로. 미해소 시 일정 영향까지.]
- **[항목]**: 무엇에 막혔나 → 필요한 액션(담당: OOO, 기한: YYYY-MM-DD)

## 다음 단계
- [할 일] (담당: OOO, 기한: YYYY-MM-DD)
```

여러 작업의 상태/담당/기한을 함께 볼 때는 표가 낫다:

```markdown
| 항목 | 상태 | 담당 | 비고 |
|------|------|------|------|
| 인증 모듈 | 🟢 완료 | | |
| 결제 연동 | 🔴 막힘 | 김OO | PG사 API 키 발급 대기 (3/10 요청) |
| 배포 자동화 | ⬜ 대기 | | 인증 완료 후 착수 |
```

상태 표기는 일관되게: `🟢 완료/On Track` · `🟡 진행 중/At Risk` · `🔴 막힘/Off Track` · `⬜ 대기`.

## 변형

- **마일스톤 추적**: 항목을 마일스톤별로 묶고 목표 날짜를 단다.
- **이슈/버그 추적**: 표에 `심각도`, `발견일` 컬럼을 추가한다.

## 안티패턴 (출처에서 경고하는 것)

- **owner 없는 리스크/blocker 나열** — 소유자가 없으면 추적이 무의미해진다. (Plane)
- **blocker를 "문제 진술"로만 적기** — "SSL 인증서 없음"이 아니라 "SSL 인증서 발급 대기 → 매니저가 IT에 에스컬레이션 필요"처럼 *액션*으로. (Asana; Tempo)
- **맥락 없는 raw 데이터 나열** — 지표만 던지지 말고 분석을 곁들인다. (Plane)
- **불규칙한 갱신 / 습관적 green** — 근거 없이 계속 green을 주면 RAG가 형식적으로 변질되고, 갱신이 불규칙하면 지표가 stale해진다.
- **과도한 길이** — 2페이지 이내, 결과에 영향을 주는 정보에 집중. (Plane; Tempo)

## 작성 팁

- 기존 추적 문서가 있으면 새로 만들지 말고 거기에 갱신한다(사용자에게 확인). 한 곳에 누적해 audit trail을 만든다. (Plane)
- 체크리스트는 GitHub task list 문법(`- [ ]` / `- [x]`)으로 쓰고, 가능하면 `#이슈번호`를 연결한다 — 이슈가 닫히면 자동 체크되고 제목이 표시된다. (GitHub Docs)
- 완료 항목을 지우지 말고 체크 표시로 남긴다. 너무 길어지면 맨 아래 "완료됨" 섹션으로 접는다.
- 날짜는 상대 표현("어제", "다음 주") 대신 절대 날짜(YYYY-MM-DD)로.
- **같은 blocker가 연속 갱신에 반복 등장하면 에스컬레이션 신호**다 — 표식을 남기고 위로 올린다.

## 근거 출처

- Atlassian Support — RAG/traffic light health status in Jira: https://support.atlassian.com/jira/kb/how-to-create-health-status-indicator-fields-like-rag-or-traffic-light-in-jira-and-advanced-roadmaps/
- Asana — How Project Status Reports Work: https://asana.com/resources/how-project-status-reports
- Tempo — The art of writing status reports: https://www.tempo.io/blog/status-report
- Plane — Project status report: https://plane.so/blog/project-status-report-how-to-write-one-and-what-to-include
- GitHub Docs — About tasklists: https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/about-tasklists
