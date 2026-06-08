# PR Review 게시 (gh api)

pr-reviewer가 분석 결과를 단일 PR Review로 게시할 때의 형식·절차다.

## 1. 코멘트 형식

각 인라인 코멘트 본문:
```
🔴 P0 [보안] <한 줄 요지>
<근거·영향. 가능하면 수정 방향>
```
- 라벨: `🔴 P0` / `🟠 P1` / `🟡 P2`
- 범주 태그: `[보안]` `[동시성]` `[로직]` `[컨벤션]`

요약 본문(Review body):
```markdown
## 리뷰 요약
| 우선순위 | 건수 |
|----------|------|
| 🔴 P0 | x |
| 🟠 P1 | y |
| 🟡 P2 | z |

<총평 1~2문장. 가장 시급한 항목 언급.>

<인라인 매핑 불가한 지적이 있으면 여기에 목록으로 기재>
```

## 2. 인라인 매핑

- diff에서 얻은 파일 경로(`path`)와 변경 라인 번호(`line`)에 코멘트를 단다.
- 추가/유지 라인은 `side=RIGHT`(기본), 삭제 라인 지적은 `side=LEFT`.
- 라인을 특정할 수 없는 지적(파일 전반·구조)은 인라인 대신 **요약 본문에 모아** 기재한다.

## 3. 제출 (단일 Review, event=COMMENT)

`gh api`로 한 번에 제출한다. `event`는 항상 `COMMENT`(승인/변경요청 자동 판정 금지).

```bash
gh api repos/{owner}/{repo}/pulls/{number}/reviews \
  -f event=COMMENT \
  -f body="<요약 본문>" \
  -F 'comments[][path]=src/foo.py' -F 'comments[][line]=42' -F 'comments[][side]=RIGHT' -F 'comments[][body]=🔴 P0 [보안] ...' \
  -F 'comments[][path]=src/bar.py' -F 'comments[][line]=10' -F 'comments[][side]=RIGHT' -F 'comments[][body]=🟠 P1 [로직] ...'
```

- `{owner}/{repo}`는 `gh repo view --json owner,name` 또는 PR URL에서 얻는다.
- 코멘트가 많으면 JSON 파일을 만들어 `--input`으로 넘겨도 된다:
  ```bash
  gh api repos/{owner}/{repo}/pulls/{number}/reviews --input review.json
  ```
  `review.json` 형식:
  ```json
  {
    "event": "COMMENT",
    "body": "<요약 본문>",
    "comments": [
      {"path": "src/foo.py", "line": 42, "side": "RIGHT", "body": "🔴 P0 [보안] ..."}
    ]
  }
  ```

## 4. 실패 처리

- 라인 번호가 diff 범위 밖이면 422 오류가 난다 → 해당 코멘트를 요약 본문으로 옮겨 재구성한다.
- 권한·인증 오류는 원인을 그대로 사용자에게 전달하고 중단한다. 임의 재시도·우회 금지.
