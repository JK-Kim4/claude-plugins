# 온보딩/가이드 문서 (Onboarding & Guide)

사용법이나 절차를 안내하는 문서. README, 셋업 가이드, how-to 가이드, 사용법 안내가 여기에 속한다. **독자는 이 분야를 잘 모르는 사람이고, "내가 이걸 따라서 성공할 수 있나"가 유일한 성공 기준이다.**

이 문서의 권고는 Diátaxis 문서 프레임워크, Make a README, Write the Docs, Google developer documentation style guide에 근거한다(하단 출처 참조).

## 핵심 원칙

- **목적이 다른 문서를 섞지 않는다 (Diátaxis).** 문서에는 네 종류가 있다 — **튜토리얼**(학습), **how-to 가이드**(작업 수행), **레퍼런스**(정보 조회), **설명**(이해). 한 페이지에 이들을 섞는 것이 문서 문제의 가장 큰 원인이다. 특히 튜토리얼(처음 배우는 사람용, 선택지 없이 한 길로)과 how-to(이미 할 줄 아는 사람용, 분기 가능)를 혼동하는 것이 가장 흔한 실수다.
- **독자는 모른다고 가정한다.** 전제 조건(도구·버전·환경·권한)을 *동작보다 먼저* 명시한다. (Google; Make a README)
- **빠른 성공을 먼저.** 설치는 기본 케이스 한두 줄로, 상세·예외는 링크로 분리한다. 완전성보다 실용성 — how-to에 모든 옵션을 욱여넣지 말고 레퍼런스로 링크한다. (Write the Docs; Diátaxis)
- **매 단계에 기대 결과를 붙인다.** "이렇게 하면 이런 출력이 보인다"를 동작과 같은 문단에 적어, 독자가 자기 진행을 스스로 확인하게 한다. (Google; Diátaxis)

## 구조 — README

```markdown
# [프로젝트/도구 이름]

[한두 문장: 이게 무엇을 하는가. 낯선 용어에는 링크.]

## 요구 사항 (Requirements)
[필요한 도구·버전·OS. 예: Python 3.10+]

## 설치 (Installation)
[복사 가능한 기본 명령 한두 줄. 상세/개발 셋업은 링크로 분리.]
\`\`\`bash
pip install logparser
\`\`\`

## 사용법 (Usage)
[가장 흔한 시나리오를 끝까지. 명령어는 문법 강조 코드 블록으로, 가능하면 기대 출력까지.]
\`\`\`bash
logparser app.log --format json
\`\`\`
→ 파싱된 로그가 JSON으로 출력된다. (옵션: --format 은 json|csv, 기본 json)

## 자주 묻는 문제 (선택)
- **[증상]**: 원인 → 해결책
```

긴 README에는 목차를 둔다. 그 외 권장 섹션(필요 시): Support, Contributing, License, Project Status.

## 구조 — How-to 가이드

제목을 **달성할 목표**로 짓는다("성능 모니터링을 연동하는 방법" ○ / "성능 모니터링" ✗). 이미 어느 정도 아는 사용자를 가정하므로 선행 지식은 가정해도 된다.

```markdown
# [무엇을 하는 방법]

[목표 한 줄: 이 가이드를 끝내면 무엇을 할 수 있게 되는가.]

## 전제 조건
[시작 전 갖춰야 할 것 — 동작보다 먼저.]

## 단계
1. **[단계 제목]** — (위치/맥락 먼저) 무엇을 하는지
   \`\`\`bash
   실행할 명령
   \`\`\`
   → 기대 결과 (이게 보이면 성공)
2. **[단계 제목]** — ...

## 확인
[제대로 됐는지 확인하는 방법.]

## 문제 해결
- **[증상]**: 해결책
```

절차 작성 규칙(Google): 단계는 번호 + 명령형 동사로 시작, **위치/조건을 먼저 말하고 동작을 나중에**("In Settings, click Save" 식), 결과는 동작과 같은 문단에. 단일 단계면 번호 대신 불릿, 선택 단계는 "선택:"으로 표기.

## 안티패턴 (출처에서 경고하는 것)

- **튜토리얼과 how-to 혼동** — 가장 흔하고 해로운 실수. 학습용과 작업용은 분리한다. (Diátaxis)
- **레퍼런스에 지시·설명 섞기** — 레퍼런스는 중립적 사실만, 나머지는 링크. (Diátaxis)
- **부정확한 문서 방치** — "틀린 문서는 없는 문서보다 나쁘다." 오래된 내용은 적극 갱신/제거. (Write the Docs)
- **FAQ를 1차 문서로** — 금세 낡고 무관한 내용이 쌓인다. 정보를 적절한 유형으로 배치한다. (Write the Docs)
- **전제 개념을 뒤에 두기** — 선행 개념을 먼저 다루도록 순서를 잡는다(Cumulative). (Write the Docs)

## 작성 팁

- 명령어와 경로는 추측하지 말고 실제 프로젝트에서 확인해 적는다. 틀린 명령어 한 줄이 가이드 전체의 신뢰를 깎는다.
- 모든 기능을 설명하려 하지 않는다. 처음 필요한 것에 집중하고 심화는 링크로 미룬다.

## 근거 출처

- Diátaxis — Start here: https://diataxis.fr/start-here/ · Tutorials vs how-to: https://diataxis.fr/tutorials-how-to/ · How-to guides: https://diataxis.fr/how-to-guides/ · Reference: https://diataxis.fr/reference/ · Tutorials: https://diataxis.fr/tutorials/
- Make a README: https://www.makeareadme.com/
- Write the Docs — Beginner's guide to docs: https://www.writethedocs.org/guide/writing/beginners-guide-to-docs/ · Docs principles: https://www.writethedocs.org/guide/writing/docs-principles/
- Google developer style guide — Procedures: https://developers.google.com/style/procedures
