# [Fable 리뷰] dlc 플러그인 1라운드 (2026-09-13)

> 리뷰 주체: Claude Fable 5.1 서브에이전트(craft:code-reviewer 페르소나). 사람이 아닌 모델 리뷰이며, 채택·기각 판단은 아래 "조치 계획"에서 오케스트레이터가 내렸다.

- 대상: 브랜치 `feature/dlc-plugin`, 커밋 `f0852a6` — 설계 문서, 라우터 SKILL.md, references 3종, dlc.py, test_dlc.py, 메타 파일 4종
- 리뷰어: craft:code-reviewer 페르소나, 모델 Claude Fable 5.1 (읽기 전용 서브에이전트)
- 리뷰 축: 설계 대 구현 정합성 / dlc.py 논리 결함 / 스킬 문서 품질 / 이식성 / 테스트 품질
- 테스트 상태: unittest 36건 GREEN (0.09초)
- 재현 표기 (a)~(j)는 리뷰어가 스크립트로 직접 재현한 시나리오

## 요약

| 축 | 건수 | 항목 |
|---|---|---|
| 설계 문서와 구현이 어긋난 항목 | 4 | 1, 6, 7, 13 |
| 논리 결함 | 8 | 1, 2, 4, 5, 8, 9, 10, 11 |
| 문서 품질 지적 | 4 | 3, 12, 13, 14 |

1번과 13번은 두 축에 걸쳐 중복 집계. 총 15건, 기각 항목 없음(오케스트레이터 판단).

**2라운드 전에 반드시 고칠 것 3개**: 1번(approve 순서 강제), 2번(유닛 표를 `## 유닛` 절로 한정), 3번(active 없을 때 기존 작업 폴더 나열).

## P1 — 반드시 고침

### 1. approve가 스테이지 순서를 강제하지 않는다

`dlc.py:437`

```python
if st.stages.get(a.stage) not in ("active", "pending"):
    raise SystemExit(...)
problems = check_stage(root, work, a.stage)
```

pending이면 `next`와 무관하게 승인된다. 재현 (a): express에서 requirements가 pending인 채로 `approve plan`이 exit 0, 상태가 `plan: done`, 다음이 requirements로 되돌아간다. 설계 §6 "라우팅 판단을 코드에 둔다"와 protocol.md 2·10단계(start 후 approve)가 코드에서 보장되지 않는다.

제안: `cmd_start`처럼 `a.stage != next_stage(...)`이면 거부하고, `active` 상태만 승인 대상으로 좁힌다.

### 2. units_table이 units.md의 모든 표를 유닛으로 읽는다

`dlc.py:305-307`

```python
for ln in p.read_text(encoding="utf-8").splitlines():
    m = re.match(r"^\|\s*([a-z0-9][a-z0-9-]*)\s*\|([^|]*)\|([^|]*)\|([^|]*)\|", ln)
    if m and m.group(1) not in ("unit", "---"):
```

재현 (e): `## 계약` 절의 `| endpoint | method | path | owner |` 표가 있으면 유닛이 `['u1-api', 'endpoint', 'get-stock']`로 잡힌다. build 검사가 `build/endpoint.md`를 요구하고, design 커버리지 집계도 오염된다. state-format.md:87은 유닛 표를 네 열로 정의하지만 절 위치를 한정하지 않는다.

제안: `section_body(text, "## 유닛")`만 파싱하고 grounding.md:25의 `u<n>-<slug>` 패턴을 정규식에 반영한다.

### 3. 라우터 안내 모드가 "active 없음"을 "작업 없음"으로 단정한다

`SKILL.md:40`

```
1. `dlc.py status`를 실행한다. 활성 작업이 없다는 오류가 나오면 사용자에게 "아직 작업이 없습니다. `dlc-init`을 먼저 부르세요"라고 전하고 끝낸다.
```

state-format.md:7은 `active`를 "사용자별 커서라 .gitignore에 넣어도 된다"고 한다. 다른 PC에서 클론하면 `docs/dlc/<작업>/`은 있는데 `active`만 없어서 에이전트가 새 작업을 만들라고 안내한다. 설계 §1 "PC가 바뀌어도 이어간다"가 깨진다.

제안: 오류 시 `docs/dlc/` 하위 폴더를 먼저 나열하고 있으면 "다른 작업으로 바꾸기" 절로 보낸다.

## P2 — 적극 고려

### 4. ID 연속성 검사가 requirements.md 전문을 대상으로 한다

`dlc.py:266-277`

```python
nums = ids_in(text, kind)
...
missing = sorted(set(range(1, max(nums) + 1)) - nums)
```

재현 (c): `## 범위 밖`에 "FR7 후보였으나 제외"라고 쓰면 FR3~FR6이 비었다고 오탐한다. 반대로 가정 절의 언급이 진짜 빈 번호를 가릴 수도 있다.

제안: `## 기능 요구사항`·`## 비기능 요구사항` 절 본문만 정의 집합으로 삼는다.

### 5. fingerprint가 파일 경로 목록만 해시한다

`dlc.py:106-111`

```python
for f in source_files(root):
    h.update(str(f).encode("utf-8"))
```

재현 (h): 파일 내용을 바꿔도 지문이 같아 codebase.md가 현행으로 판정된다. state-format.md:57 "fingerprint가 현재 소스와 같으면"은 실제 동작보다 강하게 읽힌다.

제안: 크기나 mtime을 섞거나, 문서에 "파일 목록 지문"이라고 명시한다.

### 6. 지문이 일치하면 analyze를 다시 돌릴 방법이 없다

`dlc.py:202`, `dlc.py:424`

```python
if stage == "analyze" and status == "pending" and analyze_is_current(root):
    continue
```

`next`가 건너뛰고 `start analyze`는 "지금 시작할 스테이지는 requirements"로 거부된다. 사용자가 `dlc-analyze`를 명시 호출해도 protocol.md:17 1단계에서 멈춘다. 설계 §1 "단계별 스킬을 따로 쓸 수 있다"와 마찰한다.

제안: `start --force`를 두거나 protocol에 "codebase.md를 지운 뒤 호출"을 명시한다.

### 7. 하위 ID 참조는 검사하지 않는다

`dlc.py:288-297`

```python
def top_ids(text: str):
    return {f"{k}{n}" for k in ID_RE for n in ids_in(text, k)}
```

재현 (i): plan.md가 존재하지 않는 `FR1.9`를 참조해도 `check plan: OK`. grounding.md:27 "존재하지 않는 ID 참조를 잡는다"와 어긋난다.

제안: requirements에서 `SUB_ID_RE`로 하위 ID 집합도 모아 대조한다.

### 8. state.md에 profile이 없으면 traceback

`dlc.py:198` `PROFILES[st.meta["profile"]]`. 재현 (g): `KeyError: 'profile'`.

제안: SystemExit 메시지로 감싼다.

### 9. skip이 done을 되돌린다

`dlc.py:456-458`. 재현 (d5): `skip verify --reason undo`로 승인된 스테이지가 skipped가 된다. 승인 이력이 사라진다.

제안: pending/active만 허용한다.

## P3 — 웬만하면

### 10. 오류 메시지에 None 노출

`dlc.py:425`, `dlc.py:438`. 재현 (d2) "현재 None", (d4) "지금 시작할 스테이지는 None 입니다". 프로파일 밖 스테이지와 완료 후를 별도 문장으로 낸다.

### 11. 질문 번호 연속성 미검사

protocol.md:50 "번호는 1부터 연속이다"를 `check_questions`(dlc.py:244-259)가 보지 않는다. 재현 (f): Q1, Q3만 있어도 통과. 같은 재현에서 빈 요약 답변이 두 건으로 중복 보고된다.

### 12. 스크립트 경로 표기가 세 가지

`SKILL.md:14` `<이 스킬 디렉터리>/scripts/dlc.py`, `protocol.md:10` `<skills>/dlc/scripts/dlc.py`, llm-wiki 선례 `<skill>/scripts/...`. 에이전트가 실제 경로를 어디서 얻는지 한 줄이 없다. 하나로 통일하고 "스킬이 로드될 때 보인 디렉터리"를 명시한다.

### 13. 설계 문서와 구현의 사소한 불일치

설계 §6 검증 명령이 `dlc/tests`인데 실제는 `dlc/skills/dlc/tests`. §6 명령 표에 `note`가 없으나 protocol.md:26이 쓴다. state-format.md 필수 절 표에 decisions.md가 없는데 `dlc.py:51`은 존재만 검사한다. 세 곳 모두 문서를 코드에 맞춘다.

### 14. 안내 모드와 상태만 보기의 중복

`SKILL.md:38-42`와 `SKILL.md:51-53`. 둘 다 `dlc.py status` 출력을 그대로 보이고, 차이는 안내 모드가 덧붙이는 "다음 스킬 한 줄 안내"뿐이다. Pocock의 중복 금지 원칙상 "상태만 보기" 절을 없애거나 안내 모드 안의 선택지로 접는다.

## P4 — 선택

### 15. 작업 폴더 날짜와 created 시각의 기준이 다르다

`dlc.py:352` `datetime.now().strftime('%y%m%d')`는 로컬 시간, `dlc.py:176` `now_iso()`는 UTC. 자정 근처에 폴더 이름의 날짜와 state.md의 created 날짜가 하루 어긋날 수 있다. 둘 다 UTC로 맞추거나 폴더 이름 기준을 문서에 적는다.

## 이식성

Claude 전용 도구(AskUserQuestion, Task, hooks)를 부르는 문장은 SKILL.md·references 어디에도 없다. 질문·승인이 파일과 채팅으로만 처리되는 점은 설계 §1 비목표에 부합한다. `../dlc/scripts/dlc.py` 상대 경로는 설계 §9에서 copy 설치를 확인했고, README가 "라우터를 항상 함께 설치"를 명시한다. 남는 위험은 12번의 경로 표기 불일치뿐이다. `disable-model-invocation` 프론트매터를 Codex·Gemini가 어떻게 다루는지는 저장소 안에 확인 근거가 없어 지적하지 않는다.

## 테스트 품질

CLI를 `run()`으로 호출해 종료 코드·출력·파일 상태를 보는 행위 검증이라 구현 결합은 낮다. `_force_done`이 `read_state`/`write_state`를 직접 쓰는 것은 허용 범위다. 빠진 행위(모두 재현으로 확인됨):

- 순서를 어긴 approve (1번, 재현 a)
- skipped 스테이지 approve, 프로파일 밖 스테이지 approve/start (재현 d1, d2, d4)
- `|`가 든 note의 왕복 — 재현 (b)에서는 정상이지만 테스트가 없다
- 후속 질문 번호 연속성 (11번, 재현 f)
- 계약 표가 함께 있는 units.md (2번, 재현 e)
- 하위 ID 참조 (7번, 재현 i)
- `check verify`와 `check analyze`(`../codebase.md` 경로 분기)는 한 건도 없다
- state.md에 profile이 없는 손상 파일 (8번, 재현 g)

## 조치 계획 (오케스트레이터)

15건 전부 타당하다고 판단해 기각 항목은 없다. 2라운드(스테이지 스킬 작성) 전에 15건을 모두 고치고 빠진 테스트 8개를 추가한 뒤 같은 리뷰어에게 재검토를 받는다. 조치 결과는 이 문서 아래에 추가한다.
