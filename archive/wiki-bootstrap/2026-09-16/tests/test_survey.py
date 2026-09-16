#!/usr/bin/env python3
"""survey.py 동작 고정.

    python3 -m unittest discover -s wiki-bootstrap/tests

여기 있는 테스트 중 셋은 실사용에서 터진 버그의 회귀 방지다 —
루트상대 링크가 그래프에서 빠지던 것, 이중 백틱 예시가 실제 링크로 세지던 것,
그리고 --json 의 값이 저장소 인자로 새던 것.
"""
import os, sys, json, tempfile, textwrap, subprocess, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(os.path.dirname(HERE), "scripts")
sys.path.insert(0, SCRIPTS)

import survey as S


def tree(root, files):
    """{상대경로: 내용} 으로 파일 트리를 만든다."""
    for rel, body in files.items():
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(textwrap.dedent(body).lstrip("\n"))


class StripCode(unittest.TestCase):
    def test_removes_fenced_block(self):
        self.assertNotIn("hidden", S.strip_code("before\n```\nhidden\n```\nafter"))

    def test_removes_single_backtick_span(self):
        self.assertNotIn("hidden", S.strip_code("a `hidden` b"))

    def test_removes_double_backtick_span_containing_backticks(self):
        # 회귀: 링크 문법을 설명하려고 적은 예시가 실제 링크로 집계됐다.
        text = "설명 ``[`../a.md`](../a.md)`` 끝"
        self.assertEqual(S.MDLINK.findall(S.strip_code(text)), [])

    def test_keeps_real_link_outside_code(self):
        text = "진짜 [x](./real.md) 와 `[y](./fake.md)`"
        self.assertEqual(S.MDLINK.findall(S.strip_code(text)), ["./real.md"])


class LinkPattern(unittest.TestCase):
    def test_matches_every_local_form(self):
        # 회귀: ./ ../ 만 잡으면 깨진 링크 수는 맞아도 링크 그래프에 구멍이 난다.
        text = ("[a](./same.md) [b](../up.md) [c](dir/deep.md) [d](bare.md)")
        self.assertEqual(S.MDLINK.findall(text),
                         ["./same.md", "../up.md", "dir/deep.md", "bare.md"])

    def test_skips_external_and_anchor(self):
        text = "[a](https://x.com/a.md) [b](http://x/a.md) [c](mailto:a@b.md) [d](#head)"
        self.assertEqual(S.MDLINK.findall(text), [])

    def test_strips_anchor_from_target(self):
        self.assertEqual(S.MDLINK.findall("[a](./x.md#sec)"), ["./x.md"])


class Survey(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_counts_files_frontmatter_and_links(self):
        tree(self.root, {
            "a.md": "---\ntitle: A\n---\n[to b](./b.md) [dead](./nope.md)\n",
            "b.md": "본문만 있고 프론트매터 없음\n",
        })
        r = S.survey(self.root)
        self.assertEqual(r["md_files"], 2)
        self.assertEqual(r["frontmatter_files"], 1)
        self.assertEqual(r["links_ok"], 1)
        self.assertEqual(r["links_broken"], 1)

    def test_root_relative_link_counts_as_resolved(self):
        tree(self.root, {"a.md": "[b](sub/b.md)\n", "sub/b.md": "x\n"})
        r = S.survey(self.root)
        self.assertEqual((r["links_ok"], r["links_broken"]), (1, 0))

    def test_skips_working_directories(self):
        tree(self.root, {
            "keep.md": "x\n",
            ".digest/backup.md": "x\n",
            ".lint/state.md": "x\n",
            "node_modules/pkg/readme.md": "x\n",
        })
        self.assertEqual(S.survey(self.root)["md_files"], 1)

    def test_edges_are_off_by_default(self):
        tree(self.root, {"a.md": "[b](./b.md)\n", "b.md": "x\n"})
        self.assertNotIn("edges", S.survey(self.root))

    def test_edges_carry_resolved_pairs_and_file_list(self):
        tree(self.root, {"a.md": "[b](./b.md) [x](./gone.md)\n", "b.md": "x\n"})
        r = S.survey(self.root, edges=True)
        self.assertEqual(r["edges"], [["a.md", "b.md"]])
        self.assertEqual(r["broken"], [["a.md", "./gone.md"]])
        self.assertEqual(sorted(r["files"]), ["a.md", "b.md"])

    def test_missing_root_reports_error(self):
        r = S.survey(os.path.join(self.root, "없는곳"))
        self.assertIn("error", r)


class Cli(unittest.TestCase):
    """플래그 값이 저장소 인자로 새면 조용히 '디렉터리 없음' 행이 늘어난다."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        tree(self.root, {"a.md": "[b](./b.md)\n", "b.md": "x\n"})

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *args):
        return subprocess.run([sys.executable, os.path.join(SCRIPTS, "survey.py"), *args],
                              capture_output=True, text=True, timeout=60)

    def test_json_value_is_not_treated_as_a_repo(self):
        out = os.path.join(self.root, "out.json")
        r = self.run_cli(self.root, "--json", out)
        self.assertNotIn("디렉터리 없음", r.stdout)
        with open(out, encoding="utf-8") as f:
            self.assertEqual(len(json.load(f)["results"]), 1)

    def test_json_payload_stays_slim(self):
        out = os.path.join(self.root, "out.json")
        self.run_cli(self.root, "--json", out)
        with open(out, encoding="utf-8") as f:
            row = json.load(f)["results"][0]
        for heavy in ("edges", "broken", "files"):
            self.assertNotIn(heavy, row)

    def test_graph_flag_emits_edges(self):
        out = os.path.join(self.root, "g.json")
        self.run_cli(self.root, "--graph", out)
        with open(out, encoding="utf-8") as f:
            row = json.load(f)["results"][0]
        self.assertEqual(row["edges"], [["a.md", "b.md"]])


if __name__ == "__main__":
    unittest.main()
