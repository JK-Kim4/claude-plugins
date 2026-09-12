#!/usr/bin/env python3
"""dlc.py 동작 고정.

    python3 -m unittest discover -s dlc/skills/dlc/tests

이 스크립트가 지키는 것은 셋이다 — 상태 파일을 에이전트가 손으로 고치지 않게
전이를 도맡는 것, 다음 스테이지를 프로파일과 워크스페이스 종류로 결정적으로
판정하는 것, 산출물의 필수 절과 ID 연속성을 승인 전에 기계적으로 검사하는 것.
"""
import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "scripts"))

import dlc as D  # noqa: E402


def run(*argv):
    """CLI 를 호출해 (exit_code, stdout, stderr) 를 돌려준다."""
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            code = D.main(list(argv))
        except SystemExit as e:  # argparse 오류
            code = e.code
    return code, out.getvalue(), err.getvalue()


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def init(self, profile="express", slug="inventory-api", desc="재고 API"):
        code, out, err = run("init", "--root", str(self.root), "--profile", profile,
                             "--slug", slug, "--description", desc)
        self.assertEqual(code, 0, err)
        return out

    def work(self):
        dirs = [p for p in (self.root / "docs" / "dlc").iterdir() if p.is_dir()]
        self.assertEqual(len(dirs), 1)
        return dirs[0]

    def write(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def make_brownfield(self):
        self.write("src/main/kotlin/App.kt", "fun main() {}\n")
        self.write("build.gradle.kts", "plugins {}\n")


# --- init -------------------------------------------------------------------

class Init(Base):
    def test_creates_work_folder_with_date_slug_and_state(self):
        self.init()
        work = self.work()
        self.assertRegex(work.name, r"^\d{6}-inventory-api$")
        state = (work / "state.md").read_text(encoding="utf-8")
        self.assertIn("profile: express", state)
        self.assertIn("depth: minimal", state)
        self.assertIn("workspace: greenfield", state)
        self.assertIn("| init | done |", state)

    def test_sets_active_cursor(self):
        self.init()
        active = (self.root / "docs" / "dlc" / "active").read_text(encoding="utf-8").strip()
        self.assertEqual(active, self.work().name)

    def test_full_profile_uses_standard_depth(self):
        self.init(profile="full")
        self.assertIn("depth: standard", (self.work() / "state.md").read_text(encoding="utf-8"))

    def test_rejects_unknown_profile(self):
        code, _, err = run("init", "--root", str(self.root), "--profile", "enterprise", "--slug", "x")
        self.assertNotEqual(code, 0)
        self.assertIn("enterprise", err)

    def test_brownfield_detected_with_stack(self):
        self.make_brownfield()
        self.init()
        state = (self.work() / "state.md").read_text(encoding="utf-8")
        self.assertIn("workspace: brownfield", state)
        self.assertIn("kotlin", state)
        self.assertIn("gradle", state)

    def test_greenfield_skips_analyze(self):
        self.init()
        state = (self.work() / "state.md").read_text(encoding="utf-8")
        self.assertIn("| analyze | skipped |", state)

    def test_docs_and_harness_dirs_do_not_make_brownfield(self):
        self.write("docs/notes.md", "# hi\n")
        self.write(".claude/settings.json", "{}\n")
        self.write("README.md", "# readme\n")
        self.init()
        self.assertIn("workspace: greenfield", (self.work() / "state.md").read_text(encoding="utf-8"))

    def test_second_init_with_same_slug_same_day_is_refused(self):
        self.init()
        code, _, err = run("init", "--root", str(self.root), "--profile", "express", "--slug", "inventory-api")
        self.assertNotEqual(code, 0)
        self.assertIn("이미", err)


# --- next / status ----------------------------------------------------------

class Next(Base):
    def test_express_greenfield_order(self):
        self.init(profile="express")
        code, out, _ = run("next", "--root", str(self.root))
        self.assertEqual(code, 0)
        self.assertIn("requirements", out)
        self.assertIn("dlc-requirements", out)

    def test_full_greenfield_starts_with_intent(self):
        self.init(profile="full")
        _, out, _ = run("next", "--root", str(self.root))
        self.assertIn("intent", out.splitlines()[0])

    def test_brownfield_starts_with_analyze(self):
        self.make_brownfield()
        self.init(profile="express")
        _, out, _ = run("next", "--root", str(self.root))
        self.assertIn("analyze", out.splitlines()[0])

    def test_analyze_skipped_when_codebase_md_fingerprint_matches(self):
        self.make_brownfield()
        self.init(profile="express")
        fp = D.workspace_fingerprint(self.root)
        self.write("docs/dlc/codebase.md", f"# 코드베이스\n<!-- fingerprint: {fp} -->\n")
        _, out, _ = run("next", "--root", str(self.root))
        self.assertIn("requirements", out.splitlines()[0])

    def test_analyze_not_skipped_when_fingerprint_stale(self):
        self.make_brownfield()
        self.init(profile="express")
        self.write("docs/dlc/codebase.md", "# 코드베이스\n<!-- fingerprint: deadbeef -->\n")
        _, out, _ = run("next", "--root", str(self.root))
        self.assertIn("analyze", out.splitlines()[0])

    def test_done_when_all_stages_finished(self):
        self.init(profile="express")
        for stage in ("requirements", "plan", "build", "verify"):
            self._force_done(stage)
        _, out, _ = run("next", "--root", str(self.root))
        self.assertEqual(out.strip(), "done")

    def test_status_lists_every_stage(self):
        self.init(profile="full")
        _, out, _ = run("status", "--root", str(self.root))
        for stage in D.STAGE_ORDER:
            self.assertIn(stage, out)

    def test_no_active_work_is_an_error(self):
        code, _, err = run("next", "--root", str(self.root))
        self.assertNotEqual(code, 0)
        self.assertIn("dlc-init", err)

    def _force_done(self, stage):
        work = self.work()
        st = D.read_state(work)
        st.stages[stage] = "done"
        D.write_state(work, st)


# --- start / approve / skip -------------------------------------------------

REQ_OK = """# 요구사항

## 의도 요약
재고를 단일 진실 원천으로 관리한다. [desc]

## 기능 요구사항
### FR1. 재고 조회 [Q1]
- FR1.1 SKU 단위 조회
### FR2. 재고 변경 [Q2]
- FR2.1 입고 반영

## 비기능 요구사항
- NFR1. 조회 p95 200ms 이하 [Q3]

## 제약
- 기존 PostgreSQL 공유 [Q4]

## 범위 밖
- 발주 자동화

## 가정과 열린 질문
None.
"""

QUESTIONS_ANSWERED = """## Q1. 주체는?
A. 사내
X. Other (please specify)

[Answer]: A

## Consolidated Summary Confirmation
- Looks correct
- Request changes

[Answer]: Looks correct
"""


class Transitions(Base):
    def setUp(self):
        super().setUp()
        self.init(profile="express")
        self.w = self.work()

    def test_start_marks_active_only_for_next_stage(self):
        code, _, err = run("start", "plan", "--root", str(self.root))
        self.assertNotEqual(code, 0)
        self.assertIn("requirements", err)
        code, _, _ = run("start", "requirements", "--root", str(self.root))
        self.assertEqual(code, 0)
        self.assertEqual(D.read_state(self.w).stages["requirements"], "active")

    def test_approve_refused_when_check_fails(self):
        run("start", "requirements", "--root", str(self.root))
        code, _, err = run("approve", "requirements", "--root", str(self.root))
        self.assertNotEqual(code, 0)
        self.assertIn("requirements.md", err)
        self.assertEqual(D.read_state(self.w).stages["requirements"], "active")

    def test_approve_advances_and_logs(self):
        run("start", "requirements", "--root", str(self.root))
        self.write(f"docs/dlc/{self.w.name}/requirements.md", REQ_OK)
        self.write(f"docs/dlc/{self.w.name}/requirements-questions.md", QUESTIONS_ANSWERED)
        code, out, err = run("approve", "requirements", "--root", str(self.root), "--note", "1차 승인")
        self.assertEqual(code, 0, err)
        self.assertEqual(D.read_state(self.w).stages["requirements"], "done")
        log = (self.w / "log.md").read_text(encoding="utf-8")
        self.assertIn("approve", log)
        self.assertIn("requirements", log)
        self.assertIn("1차 승인", log)
        _, out, _ = run("next", "--root", str(self.root))
        self.assertIn("plan", out.splitlines()[0])

    def test_skip_requires_reason_and_logs(self):
        code, _, _ = run("skip", "requirements", "--root", str(self.root))
        self.assertNotEqual(code, 0)
        code, _, _ = run("skip", "requirements", "--root", str(self.root), "--reason", "이미 문서 있음")
        self.assertEqual(code, 0)
        self.assertEqual(D.read_state(self.w).stages["requirements"], "skipped")
        self.assertIn("이미 문서 있음", (self.w / "log.md").read_text(encoding="utf-8"))

    def test_note_appends_to_log(self):
        code, _, _ = run("note", "requirements", "Q3 답변: p95 200ms", "--root", str(self.root))
        self.assertEqual(code, 0)
        self.assertIn("Q3 답변: p95 200ms", (self.w / "log.md").read_text(encoding="utf-8"))

    def test_approve_bumps_only_that_stage_timestamp(self):
        before = D.read_state(self.w)
        run("start", "requirements", "--root", str(self.root))
        after = D.read_state(self.w)
        self.assertEqual(before.updated["plan"], after.updated["plan"])
        self.assertNotEqual(before.stages["requirements"], after.stages["requirements"])

    def test_state_file_is_never_rewritten_with_unknown_status(self):
        st = D.read_state(self.w)
        st.stages["plan"] = "weird"
        with self.assertRaises(ValueError):
            D.write_state(self.w, st)


# --- check ------------------------------------------------------------------

class Check(Base):
    def setUp(self):
        super().setUp()
        self.init(profile="full")
        self.w = self.work()

    def path(self, name):
        return f"docs/dlc/{self.w.name}/{name}"

    def test_missing_artifact_reported(self):
        code, out, _ = run("check", "requirements", "--root", str(self.root))
        self.assertNotEqual(code, 0)
        self.assertIn("requirements.md", out)

    def test_missing_required_section_reported(self):
        self.write(self.path("requirements.md"), REQ_OK.replace("## 범위 밖\n- 발주 자동화\n\n", ""))
        self.write(self.path("requirements-questions.md"), QUESTIONS_ANSWERED)
        code, out, _ = run("check", "requirements", "--root", str(self.root))
        self.assertNotEqual(code, 0)
        self.assertIn("범위 밖", out)

    def test_unanswered_question_reported(self):
        self.write(self.path("requirements.md"), REQ_OK)
        self.write(self.path("requirements-questions.md"), QUESTIONS_ANSWERED.replace("[Answer]: A", "[Answer]:"))
        code, out, _ = run("check", "requirements", "--root", str(self.root))
        self.assertNotEqual(code, 0)
        self.assertIn("Q1", out)

    def test_summary_confirmation_must_be_looks_correct(self):
        self.write(self.path("requirements.md"), REQ_OK)
        self.write(self.path("requirements-questions.md"),
                   QUESTIONS_ANSWERED.replace("[Answer]: Looks correct", "[Answer]: Request changes"))
        code, out, _ = run("check", "requirements", "--root", str(self.root))
        self.assertNotEqual(code, 0)
        self.assertIn("Looks correct", out)

    def test_fr_id_gap_reported(self):
        self.write(self.path("requirements.md"), REQ_OK.replace("### FR2.", "### FR3."))
        self.write(self.path("requirements-questions.md"), QUESTIONS_ANSWERED)
        code, out, _ = run("check", "requirements", "--root", str(self.root))
        self.assertNotEqual(code, 0)
        self.assertIn("FR2", out)

    def test_assumptions_section_must_not_be_empty(self):
        self.write(self.path("requirements.md"), REQ_OK.replace("## 가정과 열린 질문\nNone.\n", "## 가정과 열린 질문\n"))
        self.write(self.path("requirements-questions.md"), QUESTIONS_ANSWERED)
        code, out, _ = run("check", "requirements", "--root", str(self.root))
        self.assertNotEqual(code, 0)
        self.assertIn("가정과 열린 질문", out)

    def test_passing_requirements(self):
        self.write(self.path("requirements.md"), REQ_OK)
        self.write(self.path("requirements-questions.md"), QUESTIONS_ANSWERED)
        code, out, _ = run("check", "requirements", "--root", str(self.root))
        self.assertEqual(code, 0, out)
        self.assertIn("OK", out)

    def test_stage_without_questions_file_passes_when_artifact_ok(self):
        # analyze/practices 는 project-level 산출물이고 질문 파일이 없을 수 있다
        self.write("docs/dlc/practices.md",
                   "# 관행\n\n## 작업 방식\ntrunk [Q1]\n\n## 테스트\ntest-after [Q2]\n\n## 배포\n수동 [Q3]\n\n"
                   "## 코드 스타일\nktlint [Q4]\n\n## 가정과 열린 질문\nNone.\n")
        code, out, _ = run("check", "practices", "--root", str(self.root))
        self.assertEqual(code, 0, out)

    def test_design_referencing_unknown_fr_reported(self):
        self.write(self.path("requirements.md"), REQ_OK)
        self.write(self.path("design.md"),
                   "# 설계\n\n## 컴포넌트\n- Inventory: FR1, FR9 [Q1]\n\n## 엔티티 소유권\n- Stock: Inventory\n\n"
                   "## 상호작용\n없음\n\n## 가정과 열린 질문\nNone.\n")
        self.write(self.path("decisions.md"), "# 결정\n\n## ADR-1 저장소 선택\n### 배경\n### 대안\n### 결정\n### 결과\n")
        self.write(self.path("units.md"),
                   "# 유닛\n\n## 유닛\n| unit | kind | depends_on | covers |\n|---|---|---|---|\n| u1-inventory | service | | FR1, FR2, NFR1 |\n\n"
                   "## 계약\n없음\n\n## 가정과 열린 질문\nNone.\n")
        self.write(self.path("design-questions.md"), QUESTIONS_ANSWERED)
        code, out, _ = run("check", "design", "--root", str(self.root))
        self.assertNotEqual(code, 0)
        self.assertIn("FR9", out)

    def test_units_must_cover_every_fr(self):
        self.write(self.path("requirements.md"), REQ_OK)
        self.write(self.path("design.md"),
                   "# 설계\n\n## 컴포넌트\n- Inventory: FR1 [Q1]\n\n## 엔티티 소유권\n- Stock: Inventory\n\n"
                   "## 상호작용\n없음\n\n## 가정과 열린 질문\nNone.\n")
        self.write(self.path("decisions.md"), "# 결정\n\n## ADR-1 저장소 선택\n### 배경\n### 대안\n### 결정\n### 결과\n")
        self.write(self.path("units.md"),
                   "# 유닛\n\n## 유닛\n| unit | kind | depends_on | covers |\n|---|---|---|---|\n| u1-inventory | service | | FR1, NFR1 |\n\n"
                   "## 계약\n없음\n\n## 가정과 열린 질문\nNone.\n")
        self.write(self.path("design-questions.md"), QUESTIONS_ANSWERED)
        code, out, _ = run("check", "design", "--root", str(self.root))
        self.assertNotEqual(code, 0)
        self.assertIn("FR2", out)

    def test_build_requires_one_file_per_unit(self):
        self.write(self.path("units.md"),
                   "# 유닛\n\n## 유닛\n| unit | kind | depends_on | covers |\n|---|---|---|---|\n| u1-inventory | service | | FR1 |\n| u2-api | service | u1-inventory | FR2 |\n\n"
                   "## 계약\n없음\n\n## 가정과 열린 질문\nNone.\n")
        self.write(self.path("build/u1-inventory.md"),
                   "# u1-inventory\n\n## 변경 파일\n- src/a.kt\n\n## 추적성\n| id | target |\n|---|---|\n| FR1 | src/a.kt |\n\n## 테스트\n통과\n\n## 가정과 열린 질문\nNone.\n")
        code, out, _ = run("check", "build", "--root", str(self.root))
        self.assertNotEqual(code, 0)
        self.assertIn("u2-api", out)


class RootOption(Base):
    """--root 는 서브명령 앞뒤 어디에 두어도 같은 프로젝트를 가리킨다 (C1)."""

    def setUp(self):
        super().setUp()
        self.elsewhere = tempfile.TemporaryDirectory()
        self.addCleanup(self.elsewhere.cleanup)
        self.prev_cwd = os.getcwd()
        os.chdir(self.elsewhere.name)
        self.addCleanup(os.chdir, self.prev_cwd)

    def test_root_before_subcommand_targets_that_root(self):
        code, _, err = run("--root", str(self.root), "init", "--profile", "express", "--slug", "demo")
        self.assertEqual(code, 0, err)
        self.assertTrue((self.root / "docs" / "dlc").exists())
        self.assertFalse((Path(self.elsewhere.name) / "docs").exists())

    def test_root_after_subcommand_targets_that_root(self):
        code, _, err = run("init", "--root", str(self.root), "--profile", "express", "--slug", "demo")
        self.assertEqual(code, 0, err)
        self.assertTrue((self.root / "docs" / "dlc").exists())
        self.assertFalse((Path(self.elsewhere.name) / "docs").exists())

    def test_root_before_subcommand_for_state_commands(self):
        run("init", "--root", str(self.root), "--profile", "express", "--slug", "demo")
        code, out, err = run("--root", str(self.root), "next")
        self.assertEqual(code, 0, err)
        self.assertIn("requirements", out)


class Fingerprint(Base):
    def test_changes_when_source_added(self):
        self.make_brownfield()
        a = D.workspace_fingerprint(self.root)
        self.write("src/main/kotlin/B.kt", "class B\n")
        b = D.workspace_fingerprint(self.root)
        self.assertNotEqual(a, b)

    def test_ignores_docs_changes(self):
        self.make_brownfield()
        a = D.workspace_fingerprint(self.root)
        self.write("docs/dlc/x.md", "x\n")
        self.assertEqual(a, D.workspace_fingerprint(self.root))


if __name__ == "__main__":
    unittest.main()
