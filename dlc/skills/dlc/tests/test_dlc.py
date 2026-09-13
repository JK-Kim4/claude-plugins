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

    def test_no_active_work_lists_existing_work_folders(self):
        # 다른 PC 에서 클론하면 작업 폴더는 있는데 커서만 없다 (F3). 새 작업을 만들라고 하면 안 된다
        self.init(slug="carried-over")
        (self.root / "docs" / "dlc" / "active").unlink()
        code, _, err = run("status", "--root", str(self.root))
        self.assertNotEqual(code, 0)
        self.assertIn("carried-over", err)
        self.assertNotIn("dlc-init", err)

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


class TransitionGuards(Base):
    """approve·skip 은 순서와 상태를 본다. 손상된 state.md 와 조작된 active 커서는 거부한다 (G1)."""

    def setUp(self):
        super().setUp()
        self.init(profile="express")
        self.w = self.work()

    def approve_ready(self, stage):
        if stage == "requirements":
            self.write(f"docs/dlc/{self.w.name}/requirements.md", REQ_OK)
            self.write(f"docs/dlc/{self.w.name}/requirements-questions.md", QUESTIONS_ANSWERED)

    def test_approve_refuses_stage_that_is_not_next(self):
        self.write(f"docs/dlc/{self.w.name}/plan.md",
                   "## 유닛 순서\nx\n\n## Seam과 테스트 예산\nx\n\n## 완료 정의\nx\n\n## 가정과 열린 질문\nNone.\n")
        code, _, err = run("approve", "plan", "--root", str(self.root))
        self.assertNotEqual(code, 0)
        self.assertIn("requirements", err)
        self.assertEqual(D.read_state(self.w).stages["plan"], "pending")

    def test_approve_requires_start_first(self):
        self.approve_ready("requirements")
        code, _, err = run("approve", "requirements", "--root", str(self.root))
        self.assertNotEqual(code, 0)
        self.assertIn("start", err)
        self.assertEqual(D.read_state(self.w).stages["requirements"], "pending")

    def test_approve_refuses_skipped_stage(self):
        code, _, err = run("approve", "analyze", "--root", str(self.root))
        self.assertNotEqual(code, 0)
        self.assertIn("skipped", err)

    def test_stage_outside_profile_is_named_in_message(self):
        for cmd in ("approve", "start"):
            code, _, err = run(cmd, "design", "--root", str(self.root))
            self.assertNotEqual(code, 0)
            self.assertIn("에 없는 스테이지", err)
            self.assertNotIn("None", err)

    def test_start_after_completion_says_done(self):
        for stage in ("requirements", "plan", "build", "verify"):
            st = D.read_state(self.w); st.stages[stage] = "done"; D.write_state(self.w, st)
        code, _, err = run("start", "verify", "--root", str(self.root))
        self.assertNotEqual(code, 0)
        self.assertIn("끝났습니다", err)
        self.assertNotIn("None", err)

    def test_skip_refuses_done_stage(self):
        run("start", "requirements", "--root", str(self.root))
        self.approve_ready("requirements")
        code, _, err = run("approve", "requirements", "--root", str(self.root))
        self.assertEqual(code, 0, err)
        code, _, err = run("skip", "requirements", "--root", str(self.root), "--reason", "undo")
        self.assertNotEqual(code, 0)
        self.assertEqual(D.read_state(self.w).stages["requirements"], "done")

    def test_skip_refuses_blank_reason(self):
        for reason in ("", "   "):
            code, _, err = run("skip", "requirements", "--root", str(self.root), "--reason", reason)
            self.assertNotEqual(code, 0, reason)
            self.assertIn("사유", err)
        self.assertEqual(D.read_state(self.w).stages["requirements"], "pending")

    def test_state_without_profile_is_reported_not_traceback(self):
        p = self.w / "state.md"
        p.write_text(p.read_text(encoding="utf-8").replace("- profile: express\n", ""), encoding="utf-8")
        code, _, err = run("next", "--root", str(self.root))
        self.assertEqual(code, 2)
        self.assertIn("profile", err)

    def test_state_with_unknown_profile_is_reported_not_traceback(self):
        p = self.w / "state.md"
        p.write_text(p.read_text(encoding="utf-8").replace("- profile: express", "- profile: enterprise"), encoding="utf-8")
        code, _, err = run("next", "--root", str(self.root))
        self.assertEqual(code, 2)
        self.assertIn("enterprise", err)

    def test_active_with_path_outside_docs_dlc_is_refused(self):
        other = tempfile.TemporaryDirectory()
        self.addCleanup(other.cleanup)
        run("init", "--root", other.name, "--profile", "express", "--slug", "victim")
        victim = [p for p in (Path(other.name) / "docs" / "dlc").iterdir() if p.is_dir()][0]
        for bad in (str(victim), f"../../{victim.name}", "../active"):
            self.write("docs/dlc/active", bad + "\n")
            code, _, err = run("start", "requirements", "--root", str(self.root))
            self.assertNotEqual(code, 0, bad)
            self.assertIn("active", err)
        self.assertEqual(D.read_state(victim).stages["requirements"], "pending")

    def test_active_symlink_is_refused_by_read_and_init(self):
        victim = Path(self.tmp.name) / "victim.txt"
        victim.write_text("precious\n", encoding="utf-8")
        cursor = self.root / "docs" / "dlc" / "active"
        cursor.unlink()
        os.symlink(victim, cursor)
        code, _, err = run("status", "--root", str(self.root))
        self.assertNotEqual(code, 0)
        self.assertIn("심볼릭", err)
        code, _, err = run("init", "--root", str(self.root), "--profile", "express", "--slug", "second")
        self.assertNotEqual(code, 0)
        self.assertEqual(victim.read_text(encoding="utf-8"), "precious\n")

    def test_note_with_pipe_round_trips(self):
        run("start", "requirements", "--root", str(self.root))
        self.approve_ready("requirements")
        code, _, err = run("approve", "requirements", "--root", str(self.root), "--note", "a | b")
        self.assertEqual(code, 0, err)
        st = D.read_state(self.w)
        st.set("plan", "active", "p | q")
        D.write_state(self.w, st)
        self.assertEqual(D.read_state(self.w).notes["plan"], "p | q")
        self.assertEqual(D.read_state(self.w).stages["build"], "pending")


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


# --- 산출물 계약 (G2) --------------------------------------------------------

UNITS_OK = """# 유닛

## 유닛
| unit | kind | depends_on | covers |
|---|---|---|---|
| u1-api | service | | FR1, FR2, NFR1 |

## 계약
| endpoint | method | path | owner |
|---|---|---|---|
| get-stock | GET | /stock | u1-api |

## 가정과 열린 질문
None.
"""

PLAN_OK = """## 유닛 순서
1. u1-api — FR1.1, FR2

## Seam과 테스트 예산
없음

## 완료 정의
테스트 GREEN

## 가정과 열린 질문
None.
"""

BUILD_OK = """# u1-api

## 변경 파일
- src/a.kt

## 추적성
| id | target |
|---|---|
| FR1.1 | src/a.kt |

## 테스트
통과

## 가정과 열린 질문
None.
"""

VERIFY_OK = """## 테스트 결과
전부 통과

## 추적성
FR1, FR2, NFR1 확인

## 리뷰 발견
없음

## 판정
승인

## 가정과 열린 질문
None.
"""


class Contracts(Base):
    def setUp(self):
        super().setUp()
        self.init(profile="full")
        self.w = self.work()
        self.write(self.path("requirements.md"), REQ_OK)

    def path(self, name):
        return f"docs/dlc/{self.w.name}/{name}"

    def check(self, stage):
        return run("check", stage, "--root", str(self.root))

    def test_contract_table_in_units_md_is_not_a_unit(self):
        self.write(self.path("units.md"), UNITS_OK)
        self.assertEqual([u["unit"] for u in D.units_table(self.w)], ["u1-api"])
        self.write(self.path("build/u1-api.md"), BUILD_OK)
        code, out, _ = self.check("build")
        self.assertEqual(code, 0, out)

    def test_fr_mentioned_outside_definition_sections_is_neither_defined_nor_a_gap(self):
        self.write(self.path("requirements.md"), REQ_OK.replace("- 발주 자동화", "- 발주 자동화 (FR7 후보였으나 제외)"))
        self.write(self.path("requirements-questions.md"), QUESTIONS_ANSWERED)
        code, out, _ = self.check("requirements")
        self.assertEqual(code, 0, out)
        self.write(self.path("plan.md"), PLAN_OK.replace("FR2", "FR7"))
        self.write(self.path("plan-questions.md"), QUESTIONS_ANSWERED)
        code, out, _ = self.check("plan")
        self.assertNotEqual(code, 0)
        self.assertIn("FR7", out)

    def test_unknown_sub_id_reference_reported(self):
        self.write(self.path("plan-questions.md"), QUESTIONS_ANSWERED)
        for bad in ("FR1.9", "FR999.1"):
            self.write(self.path("plan.md"), PLAN_OK.replace("FR1.1", bad))
            code, out, _ = self.check("plan")
            self.assertNotEqual(code, 0, bad)
            self.assertIn(bad, out)
        self.write(self.path("plan.md"), PLAN_OK)
        code, out, _ = self.check("plan")
        self.assertEqual(code, 0, out)

    def test_build_unit_file_references_are_checked(self):
        self.write(self.path("units.md"), UNITS_OK)
        self.write(self.path("build/u1-api.md"), BUILD_OK.replace("FR1.1", "FR999"))
        code, out, _ = self.check("build")
        self.assertNotEqual(code, 0)
        self.assertIn("FR999", out)
        self.assertIn("u1-api.md", out)

    def test_verify_references_are_checked(self):
        self.write(self.path("verify.md"), VERIFY_OK)
        code, out, _ = self.check("verify")
        self.assertEqual(code, 0, out)
        self.write(self.path("verify.md"), VERIFY_OK.replace("NFR1", "NFR9"))
        code, out, _ = self.check("verify")
        self.assertNotEqual(code, 0)
        self.assertIn("NFR9", out)

    def test_analyze_requires_current_fingerprint_in_codebase_md(self):
        self.make_brownfield()
        body = "## 개요\nx\n\n## 구조\nx\n\n## 기술 스택\nx\n\n## 관례와 제약\nx\n\n## 가정과 열린 질문\nNone.\n"
        self.write("docs/dlc/codebase.md", body)
        code, out, _ = self.check("analyze")
        self.assertNotEqual(code, 0)
        self.assertIn("fingerprint", out)
        self.write("docs/dlc/codebase.md", "<!-- fingerprint: deadbeef -->\n" + body)
        code, out, _ = self.check("analyze")
        self.assertNotEqual(code, 0)
        self.write("docs/dlc/codebase.md", f"<!-- fingerprint: {D.workspace_fingerprint(self.root)} -->\n" + body)
        code, out, _ = self.check("analyze")
        self.assertEqual(code, 0, out)

    def test_question_without_answer_line_reported(self):
        self.write(self.path("requirements-questions.md"),
                   "## Q1. 주체는?\nA. 사내\nX. Other (please specify)\n\n"
                   "## Consolidated Summary Confirmation\n- Looks correct\n\n[Answer]: Looks correct\n")
        code, out, _ = self.check("requirements")
        self.assertNotEqual(code, 0)
        self.assertIn("Q1", out)

    def test_question_numbers_must_be_continuous(self):
        self.write(self.path("requirements-questions.md"),
                   "## Q1. a\nA. x\n\n[Answer]: A\n\n## Q3. b\nA. x\n\n[Answer]: A\n\n"
                   "## Consolidated Summary Confirmation\n- Looks correct\n\n[Answer]: Looks correct\n")
        code, out, _ = self.check("requirements")
        self.assertNotEqual(code, 0)
        self.assertIn("Q2", out)

    def test_empty_summary_answer_is_reported_once(self):
        self.write(self.path("requirements-questions.md"), QUESTIONS_ANSWERED.replace("[Answer]: Looks correct", "[Answer]:"))
        code, out, _ = self.check("requirements")
        self.assertNotEqual(code, 0)
        self.assertEqual(out.count("Consolidated Summary Confirmation") + out.count("요약 확인"), 1, out)


class ExpressContract(Base):
    """design 이 없는 프로파일에서는 plan 이 units.md 를 만든다 (C2, 결정 A)."""

    def setUp(self):
        super().setUp()
        self.init(profile="express")
        self.w = self.work()

    def path(self, name):
        return f"docs/dlc/{self.w.name}/{name}"

    def test_check_plan_requires_units_md_when_profile_has_no_design(self):
        self.write(self.path("requirements.md"), REQ_OK)
        self.write(self.path("plan.md"), PLAN_OK)
        self.write(self.path("plan-questions.md"), QUESTIONS_ANSWERED)
        code, out, _ = run("check", "plan", "--root", str(self.root))
        self.assertNotEqual(code, 0)
        self.assertIn("units.md", out)
        self.write(self.path("units.md"), UNITS_OK.replace("FR1, FR2, NFR1", "FR1, NFR1"))
        code, out, _ = run("check", "plan", "--root", str(self.root))
        self.assertNotEqual(code, 0)
        self.assertIn("FR2", out)

    def test_express_runs_to_completion(self):
        def approve(stage, *files):
            for name, text in files:
                self.write(self.path(name), text)
            code, _, err = run("start", stage, "--root", str(self.root))
            self.assertEqual(code, 0, err)
            code, _, err = run("approve", stage, "--root", str(self.root))
            self.assertEqual(code, 0, err)

        approve("requirements", ("requirements.md", REQ_OK), ("requirements-questions.md", QUESTIONS_ANSWERED))
        approve("plan", ("plan.md", PLAN_OK), ("units.md", UNITS_OK), ("plan-questions.md", QUESTIONS_ANSWERED))
        approve("build", ("build/u1-api.md", BUILD_OK))
        approve("verify", ("verify.md", VERIFY_OK))
        _, out, _ = run("next", "--root", str(self.root))
        self.assertEqual(out.strip(), "done")


class RereviewFindings(Base):
    """재리뷰(N2~N7)에서 나온 경계 케이스."""

    def path(self, name):
        return f"docs/dlc/{self.work().name}/{name}"

    def test_unit_covering_only_sub_ids_counts_as_covering_parent(self):  # N2
        self.init(profile="express")
        self.write(self.path("requirements.md"), REQ_OK)
        self.write(self.path("plan.md"), PLAN_OK)
        self.write(self.path("plan-questions.md"), QUESTIONS_ANSWERED)
        self.write(self.path("units.md"), UNITS_OK.replace("FR1, FR2, NFR1", "FR1.1, FR2.1, NFR1"))
        code, out, _ = run("check", "plan", "--root", str(self.root))
        self.assertEqual(code, 0, out)

    def test_broken_symlink_in_source_tree_does_not_crash(self):  # N3
        self.make_brownfield()
        os.symlink(self.root / "nowhere.py", self.root / "dead.py")
        code, _, err = run("init", "--root", str(self.root), "--profile", "express", "--slug", "demo")
        self.assertEqual(code, 0, err)
        code, _, err = run("status", "--root", str(self.root))
        self.assertEqual(code, 0, err)

    def test_skipped_design_hands_units_md_to_plan(self):  # N5
        self.init(profile="full")
        for stage in ("intent", "practices", "requirements", "design"):
            code, _, err = run("skip", stage, "--root", str(self.root), "--reason", "테스트")
            self.assertEqual(code, 0, err)
        self.write(self.path("plan.md"), PLAN_OK)
        self.write(self.path("plan-questions.md"), QUESTIONS_ANSWERED)
        code, out, _ = run("check", "plan", "--root", str(self.root))
        self.assertNotEqual(code, 0)
        self.assertIn("units.md", out)

    def test_question_heading_without_dot_is_reported(self):  # N6
        self.init(profile="full")
        self.write(self.path("requirements.md"), REQ_OK)
        self.write(self.path("requirements-questions.md"),
                   "## Q1 주체는?\nA. 사내\n\n## Consolidated Summary Confirmation\n- Looks correct\n\n[Answer]: Looks correct\n")
        code, out, _ = run("check", "requirements", "--root", str(self.root))
        self.assertNotEqual(code, 0)
        self.assertIn("Q1", out)

    def test_unit_row_without_trailing_pipe_is_read(self):  # N7
        self.init(profile="express")
        self.write(self.path("units.md"), UNITS_OK.replace("| u1-api | service | | FR1, FR2, NFR1 |", "| u1-api | service | | FR1, FR2, NFR1"))
        self.assertEqual([u["unit"] for u in D.units_table(self.work())], ["u1-api"])

    def test_analyze_fingerprint_mismatch_message_shows_expected_value(self):  # N4
        self.make_brownfield()
        self.init(profile="express")
        self.write("docs/dlc/codebase.md", "<!-- fingerprint: deadbeef -->\n## 개요\nx\n\n## 구조\nx\n\n## 기술 스택\nx\n\n## 관례와 제약\nx\n\n## 가정과 열린 질문\nNone.\n")
        code, out, _ = run("check", "analyze", "--root", str(self.root))
        self.assertNotEqual(code, 0)
        self.assertIn(D.workspace_fingerprint(self.root), out)


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

    def test_changes_when_source_content_changes_with_same_path(self):
        self.write("app.py", "print(1)\n")
        a = D.workspace_fingerprint(self.root)
        self.write("app.py", "class NewService: pass\n")
        self.assertNotEqual(a, D.workspace_fingerprint(self.root))


class AnalyzeRerun(Base):
    """지문이 같아 next 가 건너뛴 analyze 를 사용자가 명시 호출로 다시 돌린다 (F6)."""

    def test_force_starts_analyze_even_when_fingerprint_matches(self):
        self.make_brownfield()
        self.init(profile="express")
        self.write("docs/dlc/codebase.md", f"<!-- fingerprint: {D.workspace_fingerprint(self.root)} -->\n")
        code, _, err = run("start", "analyze", "--root", str(self.root))
        self.assertNotEqual(code, 0)
        code, _, err = run("start", "analyze", "--root", str(self.root), "--force")
        self.assertEqual(code, 0, err)
        self.assertEqual(D.read_state(self.work()).stages["analyze"], "active")
        _, out, _ = run("next", "--root", str(self.root))
        self.assertIn("analyze", out.splitlines()[0])

    def test_force_is_refused_for_other_stages(self):
        self.init(profile="express")
        code, _, err = run("start", "plan", "--root", str(self.root), "--force")
        self.assertNotEqual(code, 0)
        self.assertIn("--force", err)
        self.assertEqual(D.read_state(self.work()).stages["plan"], "pending")

    def test_force_is_refused_on_greenfield(self):
        self.init(profile="express")
        code, _, err = run("start", "analyze", "--root", str(self.root), "--force")
        self.assertNotEqual(code, 0)
        self.assertEqual(D.read_state(self.work()).stages["analyze"], "skipped")


class Description(Base):
    """자유 텍스트 description 이 state.md 메타 문법과 섞이지 않는다 (C9)."""

    def test_multiline_description_is_flattened_and_kept(self):
        self.init(desc="첫 줄\n- profile: unknown\n둘째 줄")
        code, out, err = run("status", "--root", str(self.root))
        self.assertEqual(code, 0, err)
        self.assertIn("첫 줄 - profile: unknown 둘째 줄", out.splitlines()[0])
        self.assertEqual(D.read_state(self.work()).meta["profile"], "express")

    def test_meta_after_stages_table_is_ignored(self):
        self.init()
        p = self.work() / "state.md"
        p.write_text(p.read_text(encoding="utf-8") + "\n- profile: enterprise\n", encoding="utf-8")
        self.assertEqual(D.read_state(self.work()).meta["profile"], "express")


if __name__ == "__main__":
    unittest.main()


# --- 스테이지 스킬 계약 (R2) --------------------------------------------------

SKILLS_DIR = Path(HERE).parent.parent  # dlc/skills/


def skeleton_h2s(skill_md: str, artifact: str):
    """SKILL.md 의 '### <artifact>' 소절 다음 첫 fenced block 안의 H2 목록. 소절이 없으면 None."""
    lines = skill_md.splitlines()
    try:
        start = lines.index(f"### {artifact}")
    except ValueError:
        return None
    h2s, in_fence = [], False
    for ln in lines[start + 1:]:
        if ln.startswith("```"):
            if in_fence:
                return h2s
            in_fence = True
            continue
        if in_fence and ln.startswith("## "):
            h2s.append(ln.strip())
    return None


class StageSkillContracts(Base):
    def test_skill_skeleton_h2_matches_artifacts(self):
        """스킬 본문의 산출물 골격 H2 가 dlc.py ARTIFACTS 와 글자 단위로 같다 (순서 포함)."""
        checked = 0
        for stage, artifacts in D.ARTIFACTS.items():
            skill = SKILLS_DIR / f"dlc-{stage}" / "SKILL.md"
            if not skill.exists():
                continue  # 아직 없는 스테이지 스킬 (R3)
            text = skill.read_text(encoding="utf-8")
            for rel, required in artifacts:
                name = rel.split("/")[-1]
                got = skeleton_h2s(text, name)
                self.assertIsNotNone(got, f"dlc-{stage}/SKILL.md 에 '### {name}' 골격 블록이 없습니다")
                self.assertEqual(got, required, f"dlc-{stage}/SKILL.md 의 {name} 골격 H2 가 ARTIFACTS 와 다릅니다")
                checked += 1
        self.assertGreaterEqual(checked, 4, "R2 스킬 4개(analyze·intent·practices·requirements)의 골격이 검사돼야 합니다")

    def test_every_stage_skill_is_explicit_invocation_only(self):
        for d in sorted(SKILLS_DIR.glob("dlc-*")):
            text = (d / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("disable-model-invocation: true", text, d.name)
            self.assertIn("allow_implicit_invocation: false", (d / "agents" / "openai.yaml").read_text(encoding="utf-8"), d.name)
            self.assertLessEqual(len(text.splitlines()), 300, f"{d.name}/SKILL.md 가 300줄을 넘습니다")

    def test_analyze_questions_file_is_checked_when_present(self):
        self.make_brownfield()
        self.init()
        work = self.work()
        fp = D.workspace_fingerprint(self.root)
        self.write("docs/dlc/codebase.md", f"# 코드베이스 분석\n\n<!-- fingerprint: {fp} -->\n\n## 개요\nx\n## 구조\nx\n"
                   "## 기술 스택\nx\n## 관례와 제약\nx\n## 가정과 열린 질문\nNone.\n")
        self.write(f"docs/dlc/{work.name}/analyze-questions.md",
                   "## Q1. legacy/ 는 폐기 예정입니까?\nA. 예\nX. Other\n\n[Answer]:\n\n"
                   "## Consolidated Summary Confirmation\n- x\n\n[Answer]: Looks correct\n")
        code, out, _ = run("check", "--root", str(self.root), "analyze")
        self.assertEqual(code, 1)
        self.assertIn("Q1 답변이 비어 있습니다", out)
