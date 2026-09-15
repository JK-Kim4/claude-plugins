# 회의록 (Meeting Notes)

회의의 논의·결정·할 일을 기록하는 문서. 스프린트 회의, 설계 논의, 킥오프, 정례 미팅 정리가 여기에 속한다. **독자(참석자, 불참한 이해관계자, 나중의 나)는 "무엇이 결정됐고, 왜 그렇게 됐고, 누가 무엇을 언제까지 하나"를 알고 싶어 한다.**

이 문서의 권고는 Atlassian의 회의록 가이드(Inside Atlassian, The Workstream)와 Confluence 회의록 템플릿에 근거한다(하단 출처 참조).

## 핵심 원칙

- **결정과 액션 아이템이 본체다.** 논의 내용은 결정의 맥락을 주는 보조 정보다. 발언을 전부 받아 적은 속기록은 정작 결정과 할 일을 묻어버린다. (Atlassian)
- **결정은 "왜"와 함께 기록한다.** 결정만 적고 근거를 빼면 나중에 모호해지고 같은 논의가 반복된다. "무엇이 결정됐고 — 왜"까지가 한 단위다. (Atlassian — "documenting what was decided, and why, removes ambiguity down the line")
- **액션 아이템에는 담당자와 기한을 반드시 단다.** 소유자와 기한이 없는 할 일은 멈춘다. 회의가 끝난 뒤 일이 굴러가게 하는 것이 회의록의 존재 이유다. (Atlassian)
- **회의 직후 공유한다.** 기억이 선명할 때 확정하고, 불참한 이해관계자가 따라잡을 수 있게 한 곳에 공유한다.

## 구조

```markdown
# [회의명] — YYYY-MM-DD

**참석:** OOO, OOO  ·  **불참(공유):** OOO  ·  _기록: OOO_

## 결정 사항
- **[결정 내용]** — 근거/이유 한 줄
- **[결정 내용]** — ...

## 액션 아이템
- [ ] [할 일] (담당: OOO, 기한: YYYY-MM-DD)
- [ ] [할 일] (담당: OOO, 기한: YYYY-MM-DD)

## 논의 내용
[안건별로 짧게 — 결정에 이르게 된 맥락, 제기된 우려, 검토한 선택지.
 결정에 이르지 못한 논의는 "보류/추가 논의 필요"를 명시.]

### [안건 1]
- 핵심 논점과 오간 의견 요약

## 다음 회의 / 보류 안건  [있다면]
- [다음에 다룰 것, 일정]
```

## 변형

- **정례 회의(주간 등)**: 맨 위에 **"이전 액션 아이템 리뷰"** 섹션을 두고 지난 회의 할 일의 완료 여부부터 체크한다. 회의록을 회의마다 새 파일로 흩뿌리지 말고 한 문서/한 공간에 누적해 추적이 이어지게 한다. (Atlassian)
- **결정 중심 회의(설계 리뷰 등)**: 결정 사항이 아키텍처 결정이면 회의록 요약과 별도로 ADR(`technical-design.md`)로도 남길지 확인한다 — 회의록은 시점 기록이고 ADR은 결정 로그다.
- **킥오프**: 목표/비목표(Non-goals), 역할 분담, 마일스톤 합의를 결정 사항 섹션에 담는다.

## 안티패턴 (출처에서 경고하는 것)

- **속기록** — 발언 전부를 시간순으로 받아 적기. 읽는 사람은 대화를 재생하고 싶은 게 아니라 결과를 알고 싶다. (Atlassian)
- **담당·기한 없는 액션 아이템** — "~하기로 함"으로 끝나는 할 일은 아무도 하지 않는다. (Atlassian)
- **결정만 있고 이유가 없음** — 몇 주 뒤 "왜 이렇게 하기로 했지?"로 같은 회의가 반복된다.
- **회의록이 여러 곳에 분산** — 지난 액션 아이템을 찾을 수 없으면 추적이 무의미해진다. 한 곳에 모은다. (Atlassian)

## 작성 팁

- 대화 기록이나 메모에서 정리할 때는 **확정된 결정**과 **아이디어/제안 수준**을 구분한다. 결정 아닌 것을 결정 사항에 넣으면 문서가 신뢰를 잃는다.
- 참석자가 아닌 사람이 읽어도 이해되도록 약어·맥락은 한 줄 보충한다.
- 액션 아이템은 이슈 트래커를 쓰는 팀이면 `#이슈번호`로 연결한다.
- 날짜는 절대 날짜(YYYY-MM-DD)로. "다음 주까지"는 다음 주가 되면 알 수 없다.

## 근거 출처

- Inside Atlassian — How to take truly useful meeting notes: https://www.atlassian.com/blog/productivity/meeting-notes
- Atlassian Workstream — Meeting notes & agendas: https://www.atlassian.com/work-management/project-collaboration/team-meetings/meeting-notes-agendas
- Confluence — Meeting notes template: https://www.atlassian.com/software/confluence/templates/meeting-notes
