#!/usr/bin/env python3
"""lint.py 동작 고정.

    python3 -m unittest discover -s wiki-lint/tests

wiki-bootstrap 이 형제 디렉터리에 있어야 한다 — lint.py 가 거기서 링크 파싱을 가져온다.
가장 중요한 것은 두 가지다: 불변 영역을 자동 수정하지 않는 것과,
미결 마커를 불릿 단위로 뽑는 것. 둘 다 실사용에서 사고가 났던 지점이다.
"""
import os, sys, subprocess, tempfile, textwrap, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(os.path.dirname(HERE), "scripts")
sys.path.insert(0, SCRIPTS)

import lint as L
from survey import survey
from wikilink_convert import build_index


def tree(root, files):
    for rel, body in files.items():
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(textwrap.dedent(body).lstrip("\n"))


def section(body):
    return "## 이 세션은 무엇이었나\n\n요약\n\n## 어디로 이어지나\n\n" + textwrap.dedent(body).lstrip("\n")


class Exemption(unittest.TestCase):
    def test_archive_segments_are_frozen(self):
        self.assertTrue(L.in_archive("p/_archive/x.md"))
        self.assertTrue(L.in_archive("p/archive/x.md"))
        self.assertFalse(L.in_archive("p/plan-v8.5-archive/x.md"))  # 이름이 끝만 같은 디렉터리

    def test_orphan_exemptions(self):
        for rel in ("sessions/a.md", "templates/t.md", "p/_archive/x.md",
                    "p/00-INDEX.md", "p/README.md", "p/00-STATUS.md"):
            self.assertTrue(L.exempt(rel), rel)
        self.assertFalse(L.exempt("projects/some-project/notes/a.md"))


class Pending(unittest.TestCase):
    """마커가 걸린 한 줄만 뽑으면 '무엇이 미결인지'가 통째로 빠진다."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def run_check(self, body):
        tree(self.root, {"sessions/s.md": section(body)})
        return L.check_pending(self.root, ["sessions/s.md"])["items"]

    def test_subject_on_first_line_survives(self):
        items = self.run_check("""
            - **`056-oci-image-storage` 가 origin 에 push 되지 않았다**(커밋 `634ac4d`)
              — 유실 위험이 미결이다.
            """)
        self.assertEqual(len(items), 1)
        self.assertIn("056-oci-image-storage", items[0]["text"])
        self.assertIn("634ac4d", items[0]["text"])

    def test_one_item_per_bullet_not_per_line(self):
        items = self.run_check("""
            - 첫 줄은 배경이다
              그리고 이것은 미착수다
              또한 이것도 미검증이다
            """)
        self.assertEqual(len(items), 1)
        self.assertEqual(sorted(items[0]["markers"]), ["미검증", "미착수"])

    def test_separate_bullets_stay_separate(self):
        items = self.run_check("""
            - 하나는 미착수다
            - 둘은 미검증이다
            """)
        self.assertEqual(len(items), 2)

    def test_numbered_list_is_a_bullet_too(self):
        self.assertEqual(len(self.run_check("1. 워크트리가 develop 에 미병합이다.\n")), 1)

    def test_bullet_without_marker_is_dropped(self):
        items = self.run_check("""
            - 마커 없는 평범한 문장
            - 이건 미결이다
            """)
        self.assertEqual(len(items), 1)

    def test_document_without_the_section_is_skipped(self):
        tree(self.root, {"sessions/s.md": "## 다른 절\n\n미착수다\n"})
        self.assertEqual(L.check_pending(self.root, ["sessions/s.md"])["items"], [])

    def test_line_number_points_at_the_bullet_head(self):
        items = self.run_check("- 배경\n  이것은 미결이다\n")
        with open(os.path.join(self.root, "sessions/s.md"), encoding="utf-8") as f:
            lines = f.read().splitlines()
        self.assertTrue(lines[items[0]["line"] - 1].lstrip().startswith("- 배경"))


class Links(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def classify(self, files):
        tree(self.root, files)
        g = survey(self.root, edges=True)
        by_base, all_rel, all_set = build_index(self.root)
        return L.check_links(self.root, g, by_base, all_rel, all_set)

    def test_unique_target_is_fixable(self):
        out = self.classify({"a/start.md": "[x](./target.md)\n", "b/target.md": "x\n"})
        self.assertEqual(len(out["fixable"]), 1)
        self.assertEqual(out["fixable"][0]["new"], "../b/target.md")

    def test_missing_target_is_absent_not_fixable(self):
        out = self.classify({"a.md": "[x](../../outside/spec.md)\n"})
        self.assertEqual(len(out["absent"]), 1)
        self.assertEqual(out["fixable"], [])

    def test_links_from_archive_are_never_touched(self):
        out = self.classify({"p/_archive/snap/a.md": "[x](../live.md)\n", "p/live.md": "x\n"})
        self.assertEqual(len(out["frozen"]), 1)
        self.assertEqual(out["fixable"], [])

    def test_links_from_sources_are_never_touched(self):
        # sources/ 원문의 링크는 원본 저장소 기준이라 위키 안에서 이으면 남남이 된다.
        out = self.classify({"sources/doc.md": "[x](./plan/README.md)\n",
                             "projects/other/plan/README.md": "x\n"})
        self.assertEqual(len(out["frozen"]), 1)
        self.assertEqual(out["fixable"], [])

    def test_live_copy_beats_archived_copy(self):
        # 실제 사례의 모양 — 출발지가 한 단계 깊어 ../adrs/ 가 빗나간다.
        # 디렉터리 이름이 "-archive" 로 끝날 뿐 불변 영역은 아니다.
        out = self.classify({
            "p/roadmap/plan-v8.5-archive/start.md": "[x](../adrs/A.md)\n",
            "p/adrs/A.md": "live\n",
            "p/_archive/snap/adrs/A.md": "frozen\n",
        })
        self.assertEqual(out["ambiguous"], [])
        self.assertEqual(len(out["fixable"]), 1)
        self.assertNotIn("_archive", out["fixable"][0]["new"])

    def test_two_live_candidates_stay_ambiguous(self):
        out = self.classify({"c/start.md": "[x](../dup.md)\n",
                             "a/dup.md": "x\n", "b/dup.md": "x\n"})
        self.assertEqual(len(out["ambiguous"]), 1)
        self.assertEqual(out["fixable"], [])


class ApplyLinks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def body(self):
        with open(os.path.join(self.root, "a.md"), encoding="utf-8") as f:
            return f.read()

    def test_rewrites_target(self):
        tree(self.root, {"a.md": "[x](./old.md)\n"})
        n_files, n_links = L.apply_links(self.root, [{"from": "a.md", "to": "./old.md",
                                                      "new": "./new.md"}])
        self.assertEqual((n_files, n_links), (1, 1))
        self.assertIn("[x](./new.md)", self.body())

    def test_backtick_label_is_rewritten_too(self):
        # 회귀: CODE.split 방식은 여는 대괄호와 괄호를 다른 조각으로 갈라 매칭을 놓쳤다.
        tree(self.root, {"a.md": "1. [`../spec/R.md`](../spec/R.md) — 설명\n"})
        _, n = L.apply_links(self.root, [{"from": "a.md", "to": "../spec/R.md",
                                          "new": "../../spec/R.md"}])
        self.assertEqual(n, 1)
        self.assertIn("[`../../spec/R.md`](../../spec/R.md)", self.body())

    def test_example_inside_code_fence_is_left_alone(self):
        tree(self.root, {"a.md": "```\n[x](./old.md)\n```\n"})
        n_files, n_links = L.apply_links(self.root, [{"from": "a.md", "to": "./old.md",
                                                      "new": "./new.md"}])
        self.assertEqual((n_files, n_links), (0, 0))
        self.assertIn("./old.md", self.body())

    def test_reports_actual_replacements_not_candidate_count(self):
        tree(self.root, {"a.md": "[x](./old.md) [y](./old.md)\n"})
        _, n = L.apply_links(self.root, [{"from": "a.md", "to": "./old.md", "new": "./new.md"}])
        self.assertEqual(n, 2)


class Orphans(unittest.TestCase):
    def test_groups_by_directory_and_reports_exempt_count(self):
        g = {"files": ["projects/p/진행기록/a.md", "projects/p/진행기록/b.md",
                       "sessions/s.md", "projects/p/00-INDEX.md", "projects/p/live.md"],
             "edges": [["projects/p/00-INDEX.md", "projects/p/live.md"]]}
        out = L.check_orphans(g)
        self.assertEqual(out["total"], 4)          # live.md 만 피참조가 있다
        self.assertEqual(out["exempted"], 2)       # sessions/ 와 00-INDEX.md
        self.assertEqual(out["by_dir"][0][0], "projects/p/진행기록")
        self.assertEqual(len(out["by_dir"][0][1]), 2)


class Stale(unittest.TestCase):
    """이력이 낡음 기준보다 짧으면 없는 신호를 만들어내지 않는다."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args, when=None):
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
                   GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        if when:
            env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = when
        subprocess.run(["git", "-C", self.root, *args], check=True, env=env,
                       capture_output=True)

    def commit(self, rel, when):
        tree(self.root, {rel: "x\n"})
        self.git("add", "-A")
        self.git("commit", "-m", rel, when=when)

    def test_no_signal_when_history_is_shorter_than_the_window(self):
        self.git("init", "-q")
        self.commit("a.md", "2026-07-30T10:00:00+09:00")
        self.commit("b.md", "2026-07-30T11:00:00+09:00")
        out = L.check_stale(self.root, ["a.md", "b.md"])
        self.assertFalse(out["signal"])
        self.assertEqual(out["items"], [])
        self.assertIn("낡음", out["reason"])

    def test_reports_old_files_once_history_is_long_enough(self):
        self.git("init", "-q")
        self.commit("old.md", "2025-01-01T10:00:00+09:00")
        self.commit("new.md", "2026-07-30T10:00:00+09:00")
        out = L.check_stale(self.root, ["old.md", "new.md"])
        self.assertTrue(out["signal"])
        self.assertEqual([i["file"] for i in out["items"]], ["old.md"])
        self.assertGreater(out["items"][0]["days"], 500)

    def test_no_git_means_no_signal(self):
        tree(self.root, {"a.md": "x\n"})
        self.assertFalse(L.check_stale(self.root, ["a.md"])["signal"])


if __name__ == "__main__":
    unittest.main()
