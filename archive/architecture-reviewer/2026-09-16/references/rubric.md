# 아키텍처 평가 루브릭 (7축)

architecture-reviewer가 진단/검증 시 따르는 축이다. 각 축은 "무엇을 보는가 +
점검 질문"으로 구성된다. 근거는 `sources.md`.

## 1. 복잡도 (Complexity = 의존성 + 불명료함)
복잡도의 3증상으로 본다.
- **Change amplification**: 작은 변경이 여러 곳 수정을 유발하는가?
- **Cognitive load**: 안전하게 바꾸려면 얼마나 많이 알아야 하는가?
- **Unknown unknowns**: 무엇을 바꿔야 하는지조차 드러나지 않는가?
점검: 한 가지 정책 변경(예: 통화 추가)이 몇 개 파일을 건드리는가?

## 2. 모듈 깊이 (Deep vs Shallow)
좋은 모듈은 **작은 인터페이스 + 큰 기능**(deep). 인터페이스가 기능 대비 복잡하면 shallow.
점검: 인터페이스가 숨기는 복잡도가 인터페이스 자체 비용보다 큰가? 호출자가 내부 세부(재시도·분기·키)를 떠안는가?

## 3. 정보 은닉 / 누수
설계 결정이 모듈 경계 안에 갇혀 있는가.
- **Information leakage**: 같은 지식(포맷·provider 상태값 등)이 여러 모듈에 노출되는가?
- **Temporal decomposition**: 지식이 아니라 실행 순서로 모듈을 쪼갰는가?
점검: 한 모듈의 구현 세부(라이브러리 타입·문자열)가 다른 모듈에 등장하는가?

## 4. 결합도 · 응집도 · SoC
- **결합도**: 모듈 간 의존이 적고 느슨한가? 의존 방향이 구체가 아닌 추상을 향하는가?
- **응집도**: 한 모듈이 한 가지 책임에 집중하는가?
- **SoC**: 관심사가 분리돼 있는가(오케스트레이션 vs 인프라 vs 도메인)?
점검: 한 클래스가 repository·외부 API·도메인 규칙을 동시에 떠안는가?

## 5. Red Flags
`red-flags.md`의 카탈로그를 적용한다(pass-through method, special-general mixture,
repetition, conjoined methods, comment-repeats-code, hard-to-name 등).

## 6. 경계 · 언어 (DDD-lite)
- **Ubiquitous language**: 같은 개념에 같은 용어를 일관되게 쓰는가?
- **Bounded context**: 용어·모델 경계가 명확한가(같은 단어가 맥락마다 의미가 다르면 경계를 분리)?
점검: `cart`/`order`/`purchase`처럼 같은 개념이 여러 이름으로 흩어져 있는가?

## 7. 테스트 용이성
"good codebases are easy to test" — 테스트 난이도를 설계 품질의 프록시로 본다.
점검: 단위 테스트가 네트워크·DB·시계 같은 외부에 직접 묶여 있는가(경계/포트 부재)?

## 적용 지침
- 모든 축을 항상 다 채우지 않아도 된다. 대상에 해당하는 축에 집중하고, 해당 없으면 "해당 없음"으로 둔다.
- 각 축의 지적은 위치(파일·라인)와 함께, 확실치 않으면 "가능성"으로 명시한다.
