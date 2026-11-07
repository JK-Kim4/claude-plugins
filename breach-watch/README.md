# breach-watch

최근 실제로 뚫린 경로로 우리 시스템을 점검하는 스킬 2종. 국내·해외 해킹 사고(AI가 관여한 공격 포함)를 근본 원인별로 분류한 **버전 관리 카탈로그**가 중심이다.

python3 3.9+ 만 있으면 동작한다. 외부 패키지 의존 없음.

```
/plugin marketplace add JK-Kim4/claude-plugins
/plugin install breach-watch@jongwan-plugins
```

## 두 스킬

| 스킬 | 하는 일 | 언제 |
|---|---|---|
| `breach-audit` | 카탈로그로 현재 프로젝트를 **읽기 전용** 점검하고 보고서를 남긴다 | "최근 해킹 사례 기준으로 점검해줘", "쿠팡 같은 사고 우리도 당할 수 있어?" |
| `breach-update` | 마지막 조사일 이후 사고를 조사해 사건·점검 항목을 추가하고 버전을 올린다 | "해킹 사례 카탈로그 업데이트", "이번 달 침해 사고 반영해줘" |

## 카탈로그

`skills/breach-audit/catalog/`

| 파일 | 내용 |
|---|---|
| `catalog.json` | 버전, 조사 기준일, 카테고리 12개 |
| `incidents.json` | 사건. 공격 경로, 근본 원인, AI 관여 수준(confirmed·reported·none-reported)과 근거, 출처 |
| `checks.json` | 점검 항목. 근거 사건, 확인 방법, 통과 기준, 조치, 스캔 신호, 추가된 버전 |
| `CHECKLIST.md` | 사람이 읽는 목록(생성물) |
| `CHANGELOG.md` | 버전별 추가 내역, 조사 경향, 보류 사건 |

1.0.0(2026-11-07): 사건 85건(국내 21, 해외 64), 점검 57개.

## 설계에서 지킨 것

**사건 없는 점검 항목은 넣지 않는다.** 모든 점검 항목은 실제 사고 하나 이상과 이어진다. "있으면 좋은 보안 습관" 목록이 되는 순간 우선순위가 사라진다.

**AI 관여는 근거로만 표시한다.** 조사해 보면 AI가 관여한 공격도 들어온 곳은 노출 관리 포트·기본 자격증명·하드코딩 비밀·미패치 서버였다. AI는 옛 구멍을 찾는 비용을 낮췄다. 그래서 점검 항목 대부분은 기본 통제이고, AI 고유 항목(프롬프트 인젝션, MCP, 코딩 에이전트 권한, CI 안의 에이전트)은 따로 묶었다.

**버전으로 증분 점검을 한다.** 항목마다 `added_in`·`updated_in`이 있고, 점검 보고서는 맨 위에 사용한 카탈로그 버전을 남긴다. 다음 점검은 `--since <그 버전>`으로 새로 들어오거나 바뀐 항목만 보고, 지난 FAIL을 재확인한다.

**스크립트는 좁히고, 판정은 에이전트가 한다.** `catalog.py scan`은 "여기를 읽어라" 후보만 준다. 신호가 없다고 통과로 치지 않는다.

**운영 시스템을 건드리지 않는다.** 점검은 저장소와 로컬 읽기 전용 명령으로만 한다. 스캔·퍼징·익스플로잇은 하지 않고, 운영 확인이 필요한 것은 질문(MANUAL)으로 남긴다.

## 버전 관리

| 올림 | 언제 |
|---|---|
| major | 점검 항목·카테고리 id 변경·삭제, 판정 기준 반전 → 다음 점검은 전체 |
| minor | 사건·점검·카테고리 추가, 확인 방법·통과 기준 강화 |
| patch | 오탈자, 출처 보강, 스캔 신호 개선 |

새 항목은 `added_in: "next"`로 쓰고 `catalog.py bump minor`가 버전으로 바꾸며 CHANGELOG와 CHECKLIST를 갱신한다. 카탈로그 갱신은 데이터 변경이라 `archive/` 보관 대상이 아니다.

**어디에 쓰나.**

- 이 저장소 안에서 돌리면 번들 카탈로그를 직접 고친다. 끝나면 `plugin.json` 버전을 올리고 PR.
- 설치본에서 돌리면 `catalog.py init-local`로 `~/.claude/breach-watch/catalog`(git 저장소)를 만들어 거기서 갱신하고 커밋·태그(`catalog-vX.Y.Z`)한다. 플러그인 갱신으로 번들이 더 새로워지면 `catalog.py sync`로 병합한다.
- `BREACH_WATCH_CATALOG` 환경변수로 팀 공용 카탈로그 경로를 지정할 수 있다.

정기 갱신은 `/schedule`로 매월 breach-update를 돌리는 루틴을 만들면 된다.

## 테스트

```bash
python3 -m unittest discover -s breach-watch/skills/breach-audit/tests
python3 breach-watch/skills/breach-audit/scripts/catalog.py validate
```
