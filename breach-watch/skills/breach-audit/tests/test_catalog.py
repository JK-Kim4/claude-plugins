"""catalog.py 테스트. 번들 카탈로그를 임시 폴더로 복사해 BREACH_WATCH_CATALOG로 가리킨다.

    python3 -m unittest discover -s breach-watch/skills/breach-audit/tests
"""
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import catalog  # noqa: E402

BUNDLED = HERE.parent / "catalog"


def run(*argv) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            code = catalog.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
            buf.write(str(e.code))
    return code, buf.getvalue()


class CatalogTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.cat = self.tmp / "catalog"
        shutil.copytree(BUNDLED, self.cat)
        os.environ[catalog.ENV] = str(self.cat)

    def tearDown(self):
        os.environ.pop(catalog.ENV, None)
        shutil.rmtree(self.tmp)

    def _load(self, name):
        return json.loads((self.cat / name).read_text(encoding="utf-8"))

    def _dump(self, name, data):
        (self.cat / name).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def test_bundled_catalog_is_valid(self):
        code, out = run("validate")
        self.assertEqual(code, 0, out)

    def test_validate_catches_dangling_incident_ref(self):
        checks = self._load("checks.json")
        checks[0]["incidents"].append("1999-01-nope")
        self._dump("checks.json", checks)
        code, out = run("validate")
        self.assertEqual(code, 1)
        self.assertIn("1999-01-nope", out)

    def test_bump_minor_resolves_next_and_writes_changelog(self):
        checks = self._load("checks.json")
        new = dict(checks[0], id=checks[0]["category"] + "/test-new", added_in="next")
        checks.append(new)
        self._dump("checks.json", checks)
        before = self._load("catalog.json")["version"]
        code, out = run("bump", "minor", "--note", "테스트")
        self.assertEqual(code, 0, out)
        ma, mi, _ = catalog.vtuple(before)
        after = f"{ma}.{mi + 1}.0"
        self.assertEqual(self._load("catalog.json")["version"], after)
        added = [c for c in self._load("checks.json") if c["id"].endswith("/test-new")][0]
        self.assertEqual(added["added_in"], after)
        self.assertIn(f"## {after}", (self.cat / "CHANGELOG.md").read_text(encoding="utf-8"))

    def test_patch_bump_refuses_pending_items(self):
        checks = self._load("checks.json")
        checks[0]["updated_in"] = "next"
        self._dump("checks.json", checks)
        code, _ = run("bump", "patch")
        self.assertNotEqual(code, 0)

    def test_since_returns_only_newer_items(self):
        checks = self._load("checks.json")
        checks[0]["updated_in"] = "next"
        self._dump("checks.json", checks)
        run("bump", "minor")
        ver = self._load("catalog.json")["version"]
        ma, mi, _ = catalog.vtuple(ver)
        cat = catalog.load(self.cat)
        picked = catalog.select_checks(cat, f"{ma}.{mi - 1}.0", None, None)
        self.assertEqual([c["id"] for c in picked], [checks[0]["id"]])

    def test_profile_and_scan_on_sample_project(self):
        proj = self.tmp / "proj"
        (proj / ".github" / "workflows").mkdir(parents=True)
        (proj / "package.json").write_text('{"dependencies": {"express": "^4", "openai": "^4"}}')
        (proj / ".github" / "workflows" / "ci.yml").write_text(
            "on: pull_request_target\njobs:\n  a:\n    steps:\n      - uses: actions/checkout@v4\n")
        (proj / "firestore.rules").write_text("allow read, write: if true;")
        tags = catalog.detect_profile(proj)
        for t in ("node", "web", "llm-app", "github-actions", "firebase", "any"):
            self.assertIn(t, tags)
        code, out = run("scan", "--root", str(proj), "--tags", "auto")
        self.assertEqual(code, 0, out)
        self.assertIn("firestore.rules", out)


    def test_monorepo_profile_and_scan_noise_filters(self):
        proj = self.tmp / "mono"
        (proj / "frontend").mkdir(parents=True)
        (proj / "backend" / "src" / "main").mkdir(parents=True)
        (proj / "backend" / "src" / "test").mkdir(parents=True)
        (proj / "frontend" / "package.json").write_text('{"dependencies": {"next": "15"}}')
        (proj / "frontend" / "pnpm-lock.yaml").write_text("resolution: {integrity: sha512-xxdifyxx}\n")
        (proj / "backend" / "build.gradle.kts").write_text("plugins {}")
        (proj / "backend" / "src" / "main" / "Gemini.kt").write_text('val u = "https://generativelanguage.googleapis.com/v1"')
        (proj / "backend" / "src" / "test" / "AuthTest.kt").write_text('val password = "Strong!Pass12345"')
        tags = catalog.detect_profile(proj)
        for t in ("node", "java", "llm-app"):
            self.assertIn(t, tags)
        code, out = run("scan", "--root", str(proj), "--tags", "auto")
        self.assertEqual(code, 0, out)
        self.assertNotIn("pnpm-lock.yaml:", out)
        self.assertNotIn("AuthTest.kt", out)
        _, out = run("scan", "--root", str(proj), "--tags", "auto", "--include-tests")
        self.assertIn("AuthTest.kt", out)


if __name__ == "__main__":
    unittest.main()
