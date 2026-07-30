#!/usr/bin/env python3
"""wikilink_convert.py 동작 고정.

핵심은 `resolve()` 다 — 여기서 임의로 하나를 고르면 조용히 틀린 링크가 생기고
사용자는 몇 달 뒤에 발견한다. 그래서 "모호는 모호로 남는다"를 못박아 둔다.
"""
import os, sys, tempfile, textwrap, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "scripts"))

import wikilink_convert as W


def tree(root, rels):
    for rel in rels:
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8").close()


class SubOutsideCode(unittest.TestCase):
    def test_leaves_examples_in_code_alone(self):
        text = "진짜 [[a]] 와 `[[b]]` 와\n```\n[[c]]\n```\n"
        out = W.sub_outside_code(text, lambda m: "<X>")
        self.assertIn("<X>", out)
        self.assertIn("`[[b]]`", out)
        self.assertIn("[[c]]", out)


class BuildIndex(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_skips_backup_and_state_dirs(self):
        # 백업본이 색인에 들어가면 본문 링크가 조용히 사본을 가리킨다.
        tree(self.tmp.name, ["live.md", ".digest/live.md", ".lint/live.md", "raw/live.md"])
        by_base, all_rel, _ = W.build_index(self.tmp.name)
        self.assertEqual(all_rel, ["live.md"])
        self.assertEqual(by_base["live"], ["live.md"])


class Resolve(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def idx(self, rels):
        tree(self.root, rels)
        return W.build_index(self.root)

    def test_relative_target_resolves_against_source(self):
        by_base, all_rel, all_set = self.idx(["docs/a.md", "docs/sub/b.md"])
        self.assertEqual(W.resolve("../a", "docs/sub/b.md", by_base, all_rel, all_set),
                         "docs/a.md")

    def test_path_target_matches_by_suffix(self):
        by_base, all_rel, all_set = self.idx(["p/adrs/ADR-1.md", "start.md"])
        self.assertEqual(W.resolve("adrs/ADR-1", "start.md", by_base, all_rel, all_set),
                         "p/adrs/ADR-1.md")

    def test_bare_name_matches_unique_file(self):
        by_base, all_rel, all_set = self.idx(["deep/x/target.md", "start.md"])
        self.assertEqual(W.resolve("target", "start.md", by_base, all_rel, all_set),
                         "deep/x/target.md")

    def test_same_directory_wins_over_far_namesake(self):
        by_base, all_rel, all_set = self.idx(["a/dup.md", "b/dup.md", "a/start.md"])
        self.assertEqual(W.resolve("dup", "a/start.md", by_base, all_rel, all_set), "a/dup.md")

    def test_ambiguous_stays_ambiguous(self):
        by_base, all_rel, all_set = self.idx(["a/dup.md", "b/dup.md", "c/start.md"])
        got = W.resolve("dup", "c/start.md", by_base, all_rel, all_set)
        self.assertIsInstance(got, tuple)
        self.assertEqual(got[0], "AMBIG")
        self.assertEqual(sorted(got[1]), ["a/dup.md", "b/dup.md"])

    def test_missing_target_returns_none(self):
        by_base, all_rel, all_set = self.idx(["start.md"])
        self.assertIsNone(W.resolve("없는것", "start.md", by_base, all_rel, all_set))

    def test_md_suffix_on_target_is_tolerated(self):
        by_base, all_rel, all_set = self.idx(["x.md", "start.md"])
        self.assertEqual(W.resolve("x.md", "start.md", by_base, all_rel, all_set), "x.md")


class Pattern(unittest.TestCase):
    def test_captures_alias_and_heading(self):
        m = W.PAT.search("[[대상#헤딩|보이는 이름]]")
        self.assertEqual(m.group(1), "대상")
        self.assertEqual(m.group(2), "#헤딩")
        self.assertEqual(m.group(4), "보이는 이름")


if __name__ == "__main__":
    unittest.main()
