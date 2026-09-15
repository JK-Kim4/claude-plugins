# 작업 보고서 (Work Report)

완료했거나 진행한 작업을 독자에게 보고하는 문서. PR 설명, 변경 요약, 작업 완료 리포트, changelog가 여기에 속한다. **독자는 "무슨 일이 됐고, 왜 했고, 결과가 무엇이며, 내가 알아야 할 게 있나"를 알고 싶어 한다.**

이 문서의 권고는 Google의 코드 리뷰 가이드(Writing good CL descriptions), Conventional Commits, Keep a Changelog, GitHub PR 가이드, cbea.ms의 커밋 메시지 규칙에 근거한다(하단 출처 참조).

## 핵심 원칙

- **결론부터, 그리고 "왜"를 먼저.** 소스 코드는 *무엇*을 하는지는 보여줘도 *왜* 존재하는지는 못 보여준다 — 그래서 보고서의 본체는 "왜/목적"이다. "무엇을 바꿨나(what)"는 그 다음, "어떻게(how)"는 코드가 말하므로 적지 않는다. (Google CL descriptions; cbea.ms 규칙 7)
- **제목은 명령형 완전 문장으로.** "적용하면 이 작업이 ___ 한다"가 완성되도록 쓴다(예: "세션 인증을 JWT로 전환한다"). "버그 수정", "코드 이동", "1단계" 같은 모호한 제목은 정보가 없어 금지. (Google; cbea.ms 규칙 5)
- **검증 상태를 정직하게.** 통과했으면 통과했다고, 못 돌려봤으면 미확인이라고 쓴다.
- **한 보고서는 한 가지를.** 변경이 한두 가지 무관한 일을 섞고 있으면 보고서(그리고 가능하면 변경 자체)를 나눈다. 거대한 변경 묶음은 읽는 사람을 압도한다. (Google small CLs)

## 구조

```markdown
# [명령형 제목 — 무엇을 하는 변경인가]

## 요약
- 왜: 이 작업이 필요했던 이유/배경 (가장 먼저)
- 무엇을: 한두 문장으로 무슨 작업을 했는지
- 결과: 끝난 상태와 핵심 효과

## 변경 내용
[중요한 것부터. 파일 단위가 아니라 의미 단위로 묶는다. 가능하면 Conventional Commits
 타입으로 분류: feat / fix / refactor / perf / docs / test / chore]
- **[변경 항목]**: 무엇을 바꿨고 왜 그렇게 했는지 (how는 생략)

## 검증
[어떻게 동작을 확인했는가. 정직하게.]
- 통과한 테스트 / 직접 확인한 동작
- 미확인 항목 (있다면 명시)

## ⚠️ Breaking Change  [해당 시에만]
[기존 동작 중 무엇이 깨지는가. 업그레이드 시 무엇을 해야 하는가. 깨짐은 "고통스러울 만큼 명확히".]

## 영향 및 후속 작업
- 영향받는 부분 / 후속으로 필요한 작업
- 관련 이슈: Closes #123  [있다면]
```

## 변형

- **PR 설명**: 목적을 맨 앞에 두고, 변경 개요와 관련 이슈 링크(`Closes #...`)를 포함한다. 변경이 여러 파일에 걸치면 **리뷰어를 위한 리뷰 순서 안내**를 한 줄 단다("auth.ts → login.ts 순으로 보면 됩니다"). (GitHub PR 가이드)
- **Changelog**: Keep a Changelog의 6개 카테고리로 그룹화한다 — **Added / Changed / Deprecated / Removed / Fixed / Security**. 버전별 날짜는 ISO 8601(YYYY-MM-DD), 최신 버전이 위. **커밋 로그를 그대로 붙여넣지 않는다**(노이즈). (Keep a Changelog 1.1.0)
- **주간 보고**: `## 변경 내용`을 "완료 / 진행 중 / 다음 계획"으로 나눈다.
- **본인 기록용**: 요약을 줄이고, 나중의 내가 헷갈릴 결정의 이유를 더 남긴다.

## 안티패턴 (출처에서 명시적으로 경고하는 것)

- 모호한 한 단어/한 구절 제목("Fix bug", "코드 이동", "1단계"). (Google)
- 커밋 로그 diff를 그대로 보고서/changelog로 사용 — "노이즈로 가득 차 있다". (Keep a Changelog)
- 변경의 일부만 기록 — "변경 누락은 changelog가 없는 것만큼 위험할 수 있다". (Keep a Changelog)
- "how"를 장황하게 서술 — 코드가 이미 보여준다. 본문은 what/why에. (cbea.ms)

## 작성 팁

- 숫자를 쓴다("3개 파일", "테스트 18개 통과", "응답 시간 절반"). 막연한 형용사보다 구체적 수치가 신뢰를 준다.
- 검증 섹션에는 "본인이 직접 빌드·테스트했는가"를 반영한다. 제출 전 본인 검증은 GitHub·Google 가이드가 공통으로 권하는 기본 절차다.

## 근거 출처

- Google eng-practices — Writing good CL descriptions: https://google.github.io/eng-practices/review/developer/cl-descriptions.html
- Google eng-practices — Small CLs: https://google.github.io/eng-practices/review/developer/small-cls.html
- Conventional Commits v1.0.0: https://www.conventionalcommits.org/en/v1.0.0/
- Keep a Changelog 1.1.0: https://keepachangelog.com/en/1.1.0/
- GitHub Docs — Helping others review your changes: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/getting-started/helping-others-review-your-changes
- cbea.ms — How to Write a Git Commit Message: https://cbea.ms/git-commit/
