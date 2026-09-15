# 커밋 컨벤션 & PR 본문 템플릿

이 파일은 pr-automator 스킬이 커밋 메시지와 PR 본문을 만들 때 참고하는 카탈로그다.

## 1. 커밋 컨벤션 카탈로그

### conventional-commits (범용 기본값)

형식: `<type>(<scope 선택>): <subject>`

| type | 언제 |
|------|------|
| feat | 새 기능 |
| fix | 버그 수정 |
| docs | 문서만 변경 |
| refactor | 동작 변화 없는 구조 개선 |
| test | 테스트 추가/수정 |
| chore | 빌드·설정·잡일 |
| perf | 성능 개선 |
| style | 포맷팅(동작 무관) |

규칙:
- subject 는 명령형 현재시제, 마침표 없음, 50자 내외 권장
- 본문이 필요하면 빈 줄 뒤에 "무엇을·왜" 설명
- breaking change 는 본문에 `BREAKING CHANGE:` 명시
- subject 언어는 설정의 `language`를 따른다(기본 한국어). type 키워드는 영문 유지.

예: `feat: 사용자 프로필 이미지 업로드 추가`

### inferred (히스토리 추론)

기존 커밋 히스토리에서 패턴을 읽어 따른다. 확인 순서:
1. `git log --oneline -30` 으로 최근 메시지 확인
2. `type:` 접두사 비율이 높으면 conventional-commits 로 간주
3. 접두사 없이 자유 서술이 다수면 그 톤·언어·길이를 모방
4. 이모지·이슈번호(`[#123]`)·대문자 시작 등 반복되는 규칙이 있으면 따른다

## 2. PR 본문 템플릿: summary-changes-test

언어는 설정의 `language`(기본 한국어). 코드·식별자·명령어는 원문 유지.

```markdown
## 요약
<무엇을, 왜 변경했는지 1~2문장>

## 주요 변경점
- <변경 항목 1>
- <변경 항목 2>

## 테스트
- <검증 방법 또는 실행 결과. 해당 없으면 "별도 테스트 없음(문서/설정 변경)" 등으로 명시>
```

작성 지침:
- "주요 변경점"은 diff/커밋 로그에서 실제 바뀐 것만 적는다. 추측·과장 금지.
- 검증하지 않은 것을 검증했다고 쓰지 않는다. 안 돌렸으면 안 돌렸다고 적는다.
- PR 제목은 커밋 컨벤션과 같은 톤. conventional-commits면 `<type>: <subject>` 형태.

## 출처(권고 근거)

- Conventional Commits 1.0.0 — https://www.conventionalcommits.org
- GitHub Docs, "About pull requests" / PR 본문 모범 사례
