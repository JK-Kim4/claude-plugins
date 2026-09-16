---
name: wiki-digest
description: >-
  Claude Code·Codex 세션 기록(JSONL)을 읽을 수 있는 위키 문서로 가공한다. "이 세션 정리해줘", "세션 아카이브", "세션 일괄 가공"에 사용한다. 프로젝트 안에서 부르면 그 프로젝트 세션, 위키 안에서 부르면 전체가 대상이다. 회고 작성이나 외부 문서 수집에는 쓰지 않는다.
compatibility: "python3 3.8+ 만 있으면 어느 머신에서든 동작한다. 외부 패키지 의존 없음. 위키 루트는 최초 실행 시 확보해 ~/.config/llm-wiki/config.json 에 기록한다."
---

# wiki-digest

`${CLAUDE_SKILL_DIR}`는 Claude Code가 스킬을 로드할 때 이 스킬 디렉터리의 절대 경로로 치환한다. 치환되지 않는 환경(`npx skills add`로 설치한 Codex·Gemini)에서는 이 SKILL.md가 있는 디렉터리를 뜻한다. `${CLAUDE_PLUGIN_ROOT}/skills/wiki-bootstrap`은 같은 플러그인의 형제 스킬 wiki-bootstrap 디렉터리다.

AI 세션 원본(JSONL)을 사람이 읽는 위키 문서로 가공한다. **JSONL만 다룬다.** 회고 작성, 외부 자료 수집, 코드 저장소 문서 편입은 범위 밖이다.

- 문서 규격(프론트매터·5섹션·작성 규칙) → `references/document-shape.md`
- 각 규칙이 왜 이렇게 정해졌는지(실측 근거) → `references/rationale.md`

## 전제 둘

- **진행 중 세션은 가공하지 않는다.** 최근 60분 내 수정된 파일과 지금 이 세션이 해당한다. 탐색 스크립트가 걸러내지만, 사용자가 지목하면 확인하고 알린다.
- **원본은 이동하지 않고 복사만 한다.** Claude Code는 `~/.claude/projects/`의 파일로 세션 재개를 지원한다.

## 1. 위키 루트 확보

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/locate.py root
```

경로가 나오면 그대로 쓴다. 종료 코드 3이면 설정이 없는 것이고 후보가 함께 나온다. **사용자에게 확인받고** 기록한다:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/locate.py root --set <경로>
```

## 1-b. 수집 대상 관리

Claude Code는 세션을 기본 30일 후 지우므로, 나중에 가공할 세션은 미리 `raw/`로 지켜둔다. 전량 보존은 용량이 계속 늘어 관심 있는 프로젝트만 고른다.

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/locate.py collect                    # 현재 목록
python3 ${CLAUDE_SKILL_DIR}/scripts/locate.py collect --add ~/repo       # 프로젝트 추가
python3 ${CLAUDE_SKILL_DIR}/scripts/collect.py --dry-run                 # 무엇이 복사될지
python3 ${CLAUDE_SKILL_DIR}/scripts/collect.py                           # 수집 실행
python3 ${CLAUDE_SKILL_DIR}/scripts/collect.py --file <원본 경로>         # 목록에 없는 세션 하나만 확보
```

**새 프로젝트 자동 등록**: 사람이 기억해 등록하는 방식은 새므로 수집이 발견하게 한다. 세션 파일의 `cwd`를 읽어 세션이 임계 이상인 디렉터리를 등록하고, 안에 프로젝트가 여럿 든 컨테이너 디렉터리(`~/workspaces` 등)는 제외한다. cron/launchd에 걸어두면 사람이 아무것도 안 해도 며칠 안에 잡힌다.

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/collect.py --auto-add                    # 세션 3개 이상이면 등록
python3 ${CLAUDE_SKILL_DIR}/scripts/collect.py --auto-add --min-sessions 5   # 임계 조정
```

## 2. 대상 세션 찾기

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/locate.py sessions              # 실행 위치 기준
python3 ${CLAUDE_SKILL_DIR}/scripts/locate.py sessions --new-only   # 아직 가공 안 된 것만
python3 ${CLAUDE_SKILL_DIR}/scripts/locate.py sessions --cwd <경로> # 특정 프로젝트
```

**실행 위치가 곧 대상 지정이다.** 프로젝트 저장소 안이면 그 프로젝트 세션(워크트리 포함), 위키 안이나 홈이면 전체. 대상이 여럿이면 목록을 보여주고 확인받는다 — 최근 것 하나를 임의로 고르지 않는다.

## 3. 추출 — 파일을 통째로 읽지 않는다

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/extract.py <파일> --max-chars 40000
```

원본은 수십 MB다. 스크립트가 도구(Claude/Codex)를 판별해 사용자 발화 전량 + 어시스턴트 응답 표본 + 식별자 후보(커밋 해시·브랜치)만 낸다. `--max-chars`는 예산이지 상한이 아니다 — 아주 긴 세션은 두 번 나누기보다 예산을 늘려 한 번에 본다.

**건너뛸지는 발화 수가 아니라 내용으로 판단한다.** 남길 게 없는 세션("계속"·"ok"만 오간 것)은 문서를 만들지 말고 건너뛴 사실만 보고한다.

## 4. 회고 대조

```bash
rg -l '<트랙 키워드>' <위키루트>/retrospectives
```

- 회고 **있음** → "결정과 교훈"은 회고 링크로 위임하고 세션 고유 사실만 남긴다.
- **없음** → 결정·교훈을 세션 문서에 직접 적는다.

평가와 교훈의 정본은 회고다. 같은 내용을 두 문서에 복제하지 않는다.

## 5. 문서 작성

`references/document-shape.md`의 규격대로 쓴다. 프론트매터에 `session_file`을 반드시 남기고, 본문은 5섹션 서사형, 전사에서 확인된 사실만, 고유명사(커밋 해시·브랜치·테이블명·파일 경로·사람 이름)는 그대로, 45줄 내외. 같은 세션 문서가 이미 있으면 새로 만들지 않고 갱신한다.

## 6. 검증

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/wiki-bootstrap/scripts/survey.py <위키루트>
```

깨진 링크가 늘지 않았는지 본다. 늘었다면 대개 `raw/` 경로에 링크를 걸었거나 없는 회고를 참조한 것이다.

## 일괄 가공 (수십~수백 건)

한 세션에 끝나지 않으므로 **재개 가능하게** 만든다. 상태는 대화가 아니라 디스크, 위키 루트의 `.digest/`에 둔다:

```
<위키루트>/.digest/
├── README.md               지금 무슨 작업이 진행 중이고 어떻게 이어받는지 (반드시 쓴다)
├── worklist.tsv            대상 전체 — 상태 ⇥ 문서경로 ⇥ 원본경로
└── <원본 백업>/            착수 전 문서 전량 사본
```

- 시작 전에 `.digest/README.md`가 이미 있는지 본다. 있으면 진행 중인 배치이므로 그 규약을 따른다.
- 진행 여부는 기록보다 **실제 문서**로 판정한다. 매번 문서를 열어 규격 충족 여부로 잔여를 다시 센다.
- 5~10건씩 끊어 처리하고 묶음마다 보고한다. 전량을 조용히 돌리지 않는다.
- **이미 문서가 있는 세션을 재생성할 때는 기존 문서를 함께 읽고 합친다.** 원본에서는 발화 원문을, 기존 문서에서는 결론과 미해결 목록을 가져온다. 덮어쓰기 전에 기존 문서를 백업한다.

## 테스트

```bash
python3 -m unittest discover -s ${CLAUDE_SKILL_DIR}/tests
```

**스크립트를 고치면 여기부터 돌린다.**

## 마무리

만든 문서 경로와 건너뛴 세션(이유와 함께)을 보고한다. 위키 루트에 `log.md`가 있으면 이번 턴 항목을 하나 추가한다 — 파일당이 아니라 턴당 하나다.
