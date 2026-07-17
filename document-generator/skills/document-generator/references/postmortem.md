# 장애 보고서 (Incident Postmortem)

장애·사고의 영향, 원인, 대응 과정, 재발 방지책을 기록하는 문서. 서비스 장애 회고, 인시던트 리포트, 데이터 사고 정리가 여기에 속한다. **독자(팀 전체, 미래의 대응자, 경영진)는 "무슨 일이 얼마나 크게 일어났고, 왜 일어났고, 재발을 어떻게 막나"를 알고 싶어 한다.**

이 문서의 권고는 Google SRE Book/Workbook의 Postmortem Culture 챕터와 예시 포스트모템, Atlassian Incident Management Handbook에 근거한다(하단 출처 참조).

## 핵심 원칙

- **Blameless — 사람이 아니라 시스템을 본다.** 모든 관련자가 당시 가진 정보 안에서 선의로 행동했다고 전제한다. 비난이 들어가는 순간 사람들은 사실을 숨기고, 다음 장애는 더 늦게 보고된다. 포스트모템은 처벌이 아니라 조직 전체의 학습 기회다. (Google SRE; Atlassian)
- **"휴먼 에러"는 근본 원인이 아니다.** 사람의 실수로 끝내지 말고 "왜 시스템이 그 실수를 허용/증폭했는가"까지 파고든다. Five Whys 등으로 인과 사슬을 근본 원인까지 따라간다. (Atlassian; Google SRE)
- **액션 아이템 없는 포스트모템은 무의미하다.** 모든 재발 방지책에 담당자·기한·우선순위를 달고 이슈 트래커에 등록해 추적한다. "더 조심한다"류의 비구조적 대책은 대책이 아니다. (Google SRE; Atlassian)
- **타임라인은 사실대로.** 탐지가 늦었으면 늦었다고, 첫 대응이 잘못 짚었으면 그렇다고 적는다. 미화된 타임라인은 탐지·대응 개선 기회를 없앤다.
- **잘된 점과 운도 기록한다.** 잘 동작한 방어선은 강화 대상이고, "운이 좋았던 점"은 다음번에 운이 없을 때의 취약점 목록이다. (Google SRE 예시 포스트모템의 What went well / What went wrong / Where we got lucky)

## 구조 (Google SRE 템플릿 기반)

```markdown
# [장애 제목] Postmortem
**상태: Draft**  ·  _발생일: YYYY-MM-DD_  ·  _작성: OOO_  ·  _리뷰: OOO_

## 요약
[한 문단: 무엇이 얼마 동안 어떤 영향을 냈고, 원인은 무엇이었으며, 어떻게 복구했는가.]

## 영향 (Impact)
[사용자 관점 영향 — 누구에게, 얼마 동안, 어느 규모로. 수치로:
 영향 시간, 실패율/에러 수, 영향받은 사용자·요청·금액.]

## 근본 원인 및 기여 요인 (Root Causes & Trigger)
[근본 원인 — 시스템/프로세스 관점. 트리거(방아쇠)와 구분해 적는다.
 기여 요인이 여럿이면 나열한다.]

## 타임라인
| 시각 (KST) | 이벤트 |
|-----------|--------|
| HH:MM | [배포/변경 등 시작점] |
| HH:MM | 🔔 탐지 — [무엇으로 탐지했나: 알림/모니터링/사용자 신고] |
| HH:MM | [대응 조치, 에스컬레이션] |
| HH:MM | [완화(mitigation) 시점] |
| HH:MM | ✅ 복구 확인 |

## 잘된 점 / 아쉬운 점 / 운이 좋았던 점
- **잘된 점:** [동작한 방어선 — 알림, 롤백 절차 등]
- **아쉬운 점:** [탐지 지연, 문서 부재, 잘못 짚은 초기 대응 등]
- **운이 좋았던 점:** [우연히 피해가 작았던 요인 — 다음엔 없다고 가정]

## 재발 방지 액션 아이템
| 액션 | 유형 | 담당 | 기한 | 우선순위 |
|------|------|------|------|----------|
| [근본 원인 제거] | 예방 | OOO | YYYY-MM-DD | P0 |
| [탐지 시간 단축] | 탐지 | OOO | YYYY-MM-DD | P1 |
| [영향 축소] | 완화 | OOO | YYYY-MM-DD | P2 |
```

액션 유형은 세 겹의 방어로 나눠 생각한다: **예방**(재발 자체를 막기) / **탐지**(더 빨리 알기) / **완화**(같은 일이 나도 영향 줄이기). 예방책만 있는 포스트모템은 같은 부류의 다른 장애에 무방비다.

## 안티패턴 (출처에서 경고하는 것)

- **이름 지목·비난** — "OOO가 실수로 배포했다"가 아니라 "리뷰 없이 배포 가능한 파이프라인이 잘못된 설정을 통과시켰다"로. 사람 이름은 역할로 치환한다. (Google SRE; Atlassian)
- **근본 원인을 "휴먼 에러"로 종결** — 인과 사슬을 끝까지 따라가지 않은 것. (Atlassian Five Whys)
- **담당·기한 없는 액션 아이템** — 추적되지 않는 재발 방지책은 재발로 돌아온다. (Google SRE)
- **포스트모템 미공유** — 쓰고 서랍에 넣으면 조직 학습이 없다. 팀/조직에 공유하고 리뷰받는다. (Google SRE)
- **심각한 장애인데 포스트모템 생략** — 어떤 조건(심각도, 지속시간, 데이터 영향)이면 반드시 쓴다는 기준을 두는 것이 이상적이다. (Google SRE; Atlassian은 severity 2 이상 필수)

## 작성 팁

- 타임라인은 추측하지 말고 실제 기록(알림 시각, 배포 로그, 채팅 타임스탬프, 그래프)에서 재구성한다. 시각이 불확실하면 "약 HH:MM경"으로 표시한다.
- 영향 수치(에러율, 영향 사용자 수)는 가능한 한 측정해서 적고, 측정 불가면 추정임을 명시한다.
- 상태는 `Draft` → 리뷰 → `Final`. 리뷰 전 공유본임을 밝힌다.
- 대외 공유용(고객 공지)과 내부용은 목적이 다르다 — 이 템플릿은 내부 학습용이다. 대외용이 필요하면 별도로 만든다.

## 근거 출처

- Google SRE Book — Postmortem Culture: Learning from Failure: https://sre.google/sre-book/postmortem-culture/
- Google SRE Book — Example Postmortem: https://sre.google/sre-book/example-postmortem/
- Google SRE Workbook — Postmortem Culture: https://sre.google/workbook/postmortem-culture/
- Atlassian — How to run a blameless postmortem: https://www.atlassian.com/incident-management/postmortem/blameless
- Atlassian Incident Management Handbook — Postmortems: https://www.atlassian.com/incident-management/handbook/postmortems
