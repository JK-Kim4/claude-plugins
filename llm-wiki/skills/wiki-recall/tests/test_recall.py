#!/usr/bin/env python3
"""recall.py 동작 고정.

    python3 -m unittest discover -s wiki-recall/tests

가장 중요한 둘은 `raw/` 를 절대 훑지 않는 것과, 문서의 날짜를 정확히 뽑는 것이다.
전자는 자격증명이 걸릴 수 있어서고, 후자는 "이 서술을 지금도 믿을 수 있나"의
유일한 단서라서다.
"""
import os, sys, json, tempfile, textwrap, subprocess, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(os.path.dirname(HERE), "scripts")
sys.path.insert(0, SCRIPTS)

import recall as R


def tree(root, files):
    for rel, body in files.items():
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(textwrap.dedent(body).lstrip("\n"))


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def find(self, files, *terms, lines=False):
        tree(self.root, files)
        return R.search(self.root, list(terms), lines)


class RawIsNeverRead(Base):
    """가공 전 원본은 인용 대상이 아니고 자격증명이 남아 있을 수 있다."""

    def test_raw_directory_is_excluded(self):
        hits = self.find({"raw/dump.md": "비밀번호 password 어쩌고\n",
                          "sessions/s.md": "password 를 다룬 세션\n"}, "password")
        self.assertEqual([h["file"] for h in hits], ["sessions/s.md"])

    def test_node_modules_is_excluded(self):
        hits = self.find({"node_modules/p/readme.md": "쿼리\n", "a.md": "쿼리\n"}, "쿼리")
        self.assertEqual([h["file"] for h in hits], ["a.md"])


class DateExtraction(Base):
    def test_frontmatter_date_wins(self):
        hits = self.find({"sessions/2026-01-01-x.md":
                          "---\ndate: 2026-07-30\n---\n쿼리\n"}, "쿼리")
        self.assertEqual(hits[0]["date"], "2026-07-30")

    def test_falls_back_to_filename_date(self):
        hits = self.find({"sessions/2026-07-24-x.md": "쿼리\n"}, "쿼리")
        self.assertEqual(hits[0]["date"], "2026-07-24")

    def test_quoted_frontmatter_date_is_parsed(self):
        hits = self.find({"a.md": "---\ndate: '2026-07-30'\n---\n쿼리\n"}, "쿼리")
        self.assertEqual(hits[0]["date"], "2026-07-30")

    def test_undated_document_is_marked_not_guessed(self):
        # 날짜를 지어내면 안 된다 — 없다는 사실 자체가 판정 신호다.
        hits = self.find({"projects/p/status.md": "쿼리\n"}, "쿼리")
        self.assertIsNone(hits[0]["date"])


class Metadata(Base):
    def test_title_from_frontmatter(self):
        hits = self.find({"a.md": "---\ntitle: 제목이다\n---\n쿼리\n"}, "쿼리")
        self.assertEqual(hits[0]["title"], "제목이다")

    def test_title_falls_back_to_h1(self):
        hits = self.find({"a.md": "# 헤딩이다\n\n쿼리\n"}, "쿼리")
        self.assertEqual(hits[0]["title"], "헤딩이다")

    def test_title_falls_back_to_filename_last(self):
        hits = self.find({"b.md": "제목 없이 쿼리\n"}, "쿼리")
        self.assertEqual(hits[0]["title"], "b")

    def test_layer_is_the_top_directory(self):
        hits = self.find({"retrospectives/r.md": "쿼리\n", "root.md": "쿼리\n"}, "쿼리")
        layers = {h["file"]: h["layer"] for h in hits}
        self.assertEqual(layers["retrospectives/r.md"], "retrospectives")
        self.assertEqual(layers["root.md"], "(루트)")


class Ranking(Base):
    def test_documents_with_every_term_come_first(self):
        hits = self.find({"both.md": "신고 임계\n", "one.md": "신고 신고 신고 신고\n"},
                         "신고", "임계")
        self.assertEqual(hits[0]["file"], "both.md")
        self.assertEqual(hits[0]["matched"], 2)

    def test_density_beats_recency(self):
        # 최신 순으로 세우면 스치듯 언급한 문서가 정본 위로 올라간다.
        hits = self.find({"sessions/2026-07-30-thin.md": "신고\n",
                          "sessions/2026-07-01-thick.md": "신고 " * 20}, "신고")
        self.assertEqual(hits[0]["file"], "sessions/2026-07-01-thick.md")

    def test_recency_breaks_ties_at_equal_density(self):
        hits = self.find({"sessions/2026-07-01-old.md": "신고\n",
                          "sessions/2026-07-30-new.md": "신고\n"}, "신고")
        self.assertEqual(hits[0]["file"], "sessions/2026-07-30-new.md")

    def test_undated_documents_sink_below_dated_ones(self):
        hits = self.find({"projects/p/undated.md": "신고\n",
                          "sessions/2026-01-01-dated.md": "신고\n"}, "신고")
        self.assertEqual(hits[-1]["file"], "projects/p/undated.md")


class Matching(Base):
    def test_search_is_case_insensitive(self):
        self.assertEqual(len(self.find({"a.md": "IME 조합\n"}, "ime")), 1)

    def test_counts_every_occurrence(self):
        hits = self.find({"a.md": "신고 신고 신고\n"}, "신고")
        self.assertEqual(hits[0]["hits"], 3)

    def test_no_match_yields_empty(self):
        self.assertEqual(self.find({"a.md": "본문\n"}, "없는말"), [])

    def test_lines_are_returned_only_when_asked(self):
        files = {"a.md": "앞줄\n여기 신고 가 있다\n뒷줄\n"}
        self.assertNotIn("lines", self.find(files, "신고")[0])
        self.assertEqual(self.find(files, "신고", lines=True)[0]["lines"],
                         ["여기 신고 가 있다"])

    def test_line_capture_stops_at_three(self):
        hits = self.find({"a.md": "\n".join(["신고"] * 10)}, "신고", lines=True)
        self.assertEqual(len(hits[0]["lines"]), 3)


class ReadingCost(Base):
    """스킬의 이득은 읽을 문서를 줄이는 데서 나온다 — 크기를 안 보여주면 그게 무너진다."""

    def test_size_is_reported(self):
        hits = self.find({"a.md": "신고\n"}, "신고")
        self.assertEqual(hits[0]["bytes"], len("신고\n".encode()))

    def test_heavy_document_is_flagged_in_output(self):
        tree(self.root, {"projects/p/big.md": "신고\n" + "가" * R.HEAVY})
        out = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS, "recall.py"), "신고", "--root", self.root],
            capture_output=True, text=True, timeout=60).stdout
        self.assertIn("⚠무거움", out)
        self.assertIn("--lines 로 매치 줄만 먼저 본다", out)

    def test_no_warning_when_everything_is_small(self):
        tree(self.root, {"a.md": "신고\n"})
        out = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS, "recall.py"), "신고", "--root", self.root],
            capture_output=True, text=True, timeout=60).stdout
        self.assertNotIn("⚠", out)


class ProjectScope(Base):
    """조회는 대개 프로젝트 저장소 안에서 불린다 — 그때 위키 전체 최신이 답인 경우는 드물다."""

    def test_common_path_names_are_not_projects(self):
        got = R.cwd_scope("/Users/x/Desktop/workspaces/my-app")
        self.assertIn("my-app", got)
        for junk in ("users", "desktop", "workspaces", "x"):
            if junk != "x":
                self.assertNotIn(junk, got)

    def test_worktree_still_finds_the_repo_name(self):
        got = R.cwd_scope("/Users/x/workspaces/my-app/.worktrees/130-feature")
        self.assertIn("my-app", got)

    def test_project_comes_from_frontmatter(self):
        hits = self.find({"sessions/a.md": "---\nproject: my-app\n---\n신고\n"}, "신고")
        self.assertEqual(hits[0]["project"], "my-app")

    def test_project_falls_back_to_projects_directory(self):
        hits = self.find({"projects/my-app/status.md": "신고\n"}, "신고")
        self.assertEqual(hits[0]["project"], "my-app")

    def test_in_scope_documents_rank_first_even_when_weaker(self):
        tree(self.root, {"sessions/2026-07-01-mine.md": "---\nproject: my-app\n---\n신고\n",
                         "sessions/2026-07-30-other.md": "---\nproject: other\n---\n" + "신고 " * 20})
        hits = R.search(self.root, ["신고"], scope={"my-app"})
        self.assertEqual(hits[0]["file"], "sessions/2026-07-01-mine.md")
        self.assertTrue(hits[0]["in_scope"])

    def test_out_of_scope_is_kept_not_filtered(self):
        # 위키를 하나로 합친 이유가 프로젝트를 가로지르는 조회다. 하드 필터는 그걸 되돌린다.
        tree(self.root, {"sessions/a.md": "---\nproject: my-app\n---\n신고\n",
                         "sessions/b.md": "---\nproject: other\n---\n신고\n"})
        hits = R.search(self.root, ["신고"], scope={"my-app"})
        self.assertEqual(len(hits), 2)
        self.assertFalse(hits[1]["in_scope"])

    def test_no_scope_means_nothing_is_privileged(self):
        tree(self.root, {"sessions/a.md": "---\nproject: my-app\n---\n신고\n"})
        self.assertFalse(R.search(self.root, ["신고"], scope=None)[0]["in_scope"])


class Grouping(Base):
    def test_groups_preserve_ranked_order(self):
        hits = self.find({"sessions/2026-07-30-a.md": "신고 " * 5,
                          "projects/p/b.md": "신고\n",
                          "sessions/2026-07-29-c.md": "신고 " * 3}, "신고")
        g = R.group(hits)
        self.assertEqual(list(g)[0], "sessions")
        self.assertEqual(len(g["sessions"]), 2)


class Cli(Base):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, os.path.join(SCRIPTS, "recall.py"), *args],
                              capture_output=True, text=True, timeout=60)

    def test_reports_zero_hits_with_guidance(self):
        tree(self.root, {"a.md": "본문\n"})
        out = self.run_cli("없는말", "--root", self.root).stdout
        self.assertIn("0건", out)
        self.assertIn("질의어를 줄이거나", out)

    def test_json_holds_metadata_for_judgement(self):
        tree(self.root, {"sessions/2026-07-30-a.md": "---\ntitle: 제목\n---\n신고\n"})
        out = os.path.join(self.root, "out.json")
        self.run_cli("신고", "--root", self.root, "--json", out)
        with open(out, encoding="utf-8") as f:
            d = json.load(f)
        self.assertEqual(d["terms"], ["신고"])
        self.assertEqual(d["hits"][0]["date"], "2026-07-30")
        self.assertEqual(d["hits"][0]["layer"], "sessions")

    def test_root_comes_from_config_when_not_given(self):
        """조회는 프로젝트 저장소 한가운데서 불린다 — 매번 위키 경로를 알 순 없다."""
        tree(self.root, {"a.md": "신고\n"})
        cfg = os.path.join(self.root, ".config", "llm-wiki")
        os.makedirs(cfg)
        with open(os.path.join(cfg, "config.json"), "w", encoding="utf-8") as f:
            json.dump({"root": self.root}, f)
        env = dict(os.environ, HOME=self.root)
        r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "recall.py"), "신고"],
                           capture_output=True, text=True, timeout=60, env=env)
        self.assertIn("문서 1건", r.stdout)

    def test_missing_root_fails_loudly(self):
        env = dict(os.environ, HOME=os.path.join(self.root, "빈홈"))
        r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "recall.py"), "신고"],
                           capture_output=True, text=True, timeout=60, env=env)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("위키 루트를 모른다", r.stderr)

    def test_all_flag_disables_project_priority(self):
        tree(self.root, {"sessions/a.md": "---\nproject: 빈홈\n---\n신고\n"})
        out = self.run_cli("신고", "--root", self.root, "--all").stdout
        self.assertNotIn("우선", out)

    def test_explicit_project_is_reported(self):
        tree(self.root, {"sessions/a.md": "---\nproject: my-app\n---\n신고\n"})
        out = self.run_cli("신고", "--root", self.root, "--project", "my-app").stdout
        self.assertIn("my-app 우선", out)

    def test_flag_value_is_not_treated_as_a_query_term(self):
        tree(self.root, {"a.md": "신고\n"})
        out = self.run_cli("신고", "--root", self.root, "--limit", "5").stdout
        self.assertIn("신고 → 문서 1건", out)


if __name__ == "__main__":
    unittest.main()
