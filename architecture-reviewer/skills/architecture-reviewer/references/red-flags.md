# Red Flags 카탈로그 (Ousterhout)

루브릭 5번 축에서 적용하는 구조적 악취 신호. 각 항목은 "정의 + 신호"다.

| Red flag | 정의 / 신호 |
|----------|-------------|
| **Shallow module** | 인터페이스가 기능 대비 복잡 — 추상화로 복잡도를 숨기지 못함. |
| **Information leakage** | 같은 설계 결정/지식이 둘 이상의 모듈에 노출됨. |
| **Temporal decomposition** | 지식이 아니라 실행 순서로 모듈을 분해해 지식이 중복됨. |
| **Overexposure** | 인터페이스가 드물게 쓰이는 내부 세부를 사용자에게 강제로 노출. |
| **Pass-through method** | 의미를 더하지 않고 다른 메서드로 호출만 위임. |
| **Repetition** | 같은 코드/지식 조각이 반복됨(누수의 신호). |
| **Special-general mixture** | 범용 메커니즘에 특수 케이스가 섞여 들어감. |
| **Conjoined methods** | 둘을 같이 봐야만 이해/수정되는 메서드 쌍. |
| **Comment repeats code** | 주석이 코드를 그대로 옮길 뿐 — 추상화·"왜"가 없음. |
| **Hard to pick name** | 이름 짓기가 어려움 = 책임이 불명확하거나 과다. |
| **Hard to describe** | 인터페이스를 짧게 설명하기 어려움 = 인터페이스가 깊지 않음. |
| **Nonobvious code** | 영리한 트릭·암묵 전제로 가독성을 희생. |

## 사용
- 발견한 red flag는 이름을 명시하고(예: "pass-through method"), 위치와 함께 지적한다.
- red flag 자체가 곧 P0는 아니다 — 영향도 × 개선비용으로 우선순위를 별도 판단한다(SKILL.md §우선순위).
