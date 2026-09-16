#!/usr/bin/env python3
"""locate.py · collect.py 의 경로 규칙 고정.

수집 대상을 고르는 규칙이라, 틀리면 남의 프로젝트 세션을 통째로 빨아들이거나
(컨테이너 디렉터리 문제) 정작 필요한 세션을 놓친다. 슬러그는 정방향 전용이고
역산하면 안 된다는 것도 여기서 못박는다.
"""
import os, sys, json, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "scripts"))

import locate as LO
import collect as CO


class Slug(unittest.TestCase):
    def test_slashes_and_underscores_both_become_dashes(self):
        self.assertEqual(LO.slug_for("/Users/x/workspaces/my_app"),
                         "-Users-x-workspaces-my-app")

    def test_collect_and_locate_agree(self):
        for p in ("/a/b_c", "/a/b-c", "/tmp/x_y_z"):
            self.assertEqual(LO.slug_for(p), CO.slug_for(p))

    def test_slug_is_not_reversible(self):
        # my_app 과 my-app 이 같은 슬러그로 접힌다 — 역산 금지의 근거다.
        self.assertEqual(LO.slug_for("/a/my_app"), LO.slug_for("/a/my-app"))


class Matches(unittest.TestCase):
    """컨테이너 디렉터리를 등록해도 하위 프로젝트를 삼키지 않아야 한다."""

    def setUp(self):
        self.target = CO.slug_for("/Users/x/workspaces/my_app")

    def test_exact_project_matches(self):
        self.assertTrue(CO.matches(self.target, self.target))

    def test_worktree_of_the_project_matches(self):
        self.assertTrue(CO.matches(self.target + "--claude-worktrees-foo", self.target))

    def test_sibling_project_does_not_match(self):
        other = CO.slug_for("/Users/x/workspaces/my_app_extra")
        self.assertFalse(CO.matches(other, self.target))

    def test_child_project_of_a_container_does_not_match(self):
        container = CO.slug_for("/Users/x/workspaces")
        child = CO.slug_for("/Users/x/workspaces/my_app")
        self.assertFalse(CO.matches(child, container))


class AlreadyHave(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        open(os.path.join(self.tmp.name, "2026-07-30-main-abc12345.jsonl"), "w").close()

    def tearDown(self):
        self.tmp.cleanup()

    def test_finds_existing_uuid_prefix(self):
        self.assertTrue(CO.already_have(self.tmp.name, "abc12345"))

    def test_reports_missing_uuid(self):
        self.assertFalse(CO.already_have(self.tmp.name, "ffffffff"))


class ClaudeCwd(unittest.TestCase):
    def tearDown(self):
        os.unlink(self.path)

    def write(self, lines):
        fd, self.path = tempfile.mkstemp(suffix=".jsonl")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            for o in lines:
                f.write(json.dumps(o) + "\n")

    def test_reads_cwd_from_the_session_file(self):
        self.write([{"type": "user"}, {"type": "user", "cwd": "/Users/x/repo"}])
        self.assertEqual(CO.claude_cwd(self.path), "/Users/x/repo")

    def test_gives_up_after_the_head_of_the_file(self):
        self.write([{"type": "user"}] * 60 + [{"cwd": "/Users/x/repo"}])
        self.assertIsNone(CO.claude_cwd(self.path))

    def test_broken_lines_do_not_abort_the_scan(self):
        fd, self.path = tempfile.mkstemp(suffix=".jsonl")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("{깨진\n")
            f.write(json.dumps({"cwd": "/Users/x/repo"}) + "\n")
        self.assertEqual(CO.claude_cwd(self.path), "/Users/x/repo")


class LooksLikeWiki(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_needs_both_index_and_raw(self):
        d = self.tmp.name
        self.assertFalse(LO.looks_like_wiki(d))
        open(os.path.join(d, "00-INDEX.md"), "w").close()
        self.assertFalse(LO.looks_like_wiki(d))
        os.makedirs(os.path.join(d, "raw"))
        self.assertTrue(LO.looks_like_wiki(d))


class SkipName(unittest.TestCase):
    def test_subagent_and_journal_files_are_skipped(self):
        self.assertTrue(CO.SKIP_NAME.match("agent-abc123"))
        self.assertTrue(CO.SKIP_NAME.match("journal-2026"))
        self.assertIsNone(CO.SKIP_NAME.match("2026-07-30-main-abc.jsonl"))


if __name__ == "__main__":
    unittest.main()
