#!/usr/bin/env python3
"""lost_identifiers.py 동작 고정.

이 스크립트가 느슨하면 재생성이 커밋 해시·PR 번호를 일반명사로 바꾼 것을 놓친다.
반대로 너무 넓으면 일반 영단어까지 "잃은 식별자"로 올려 지표가 못 쓰게 된다.
경계를 여기서 못박는다.
"""
import os, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "scripts"))

import lost_identifiers as LI


class IdentPattern(unittest.TestCase):
    def test_catches_the_kinds_worth_restoring(self):
        text = ("커밋 `a1b2c3d` 와 8ed601f, PR #123, 마이그레이션 V63, "
                "브랜치 feature/foo-bar, 파일 `Service.kt`, "
                "클래스 PaymentService, 테이블 idempotency_keys")
        got = LI.idents(text)
        for want in ("a1b2c3d", "8ed601f", "#123", "V63", "feature/foo-bar",
                     "`Service.kt`", "PaymentService", "idempotency_keys"):
            self.assertIn(want, got, want)

    def test_ignores_issue_number_inside_a_url_path(self):
        # (?<![\w/]) 가드 — 링크 경로의 #123 은 이슈 참조가 아니다.
        self.assertNotIn("#123", LI.idents("https://x/issues/#123"))

    def test_short_hex_is_not_a_commit(self):
        self.assertNotIn("abc123", LI.idents("abc123 은 6자리라 해시가 아니다"))

    def test_plain_capitalised_word_is_not_a_class(self):
        # 접미사 화이트리스트가 없으면 일반 영단어가 전부 식별자가 된다.
        self.assertNotIn("Session", LI.idents("Session 은 일반 명사다"))

    def test_single_word_is_not_snake_case(self):
        self.assertNotIn("keys", LI.idents("keys 하나로는 테이블명이 아니다"))


class ContextOf(unittest.TestCase):
    def test_returns_the_whole_line_the_token_sits_in(self):
        text = "앞줄\n커밋 a1b2c3d 로 고쳤다\n뒷줄"
        self.assertEqual(LI.context_of(text, "a1b2c3d"), ["커밋 a1b2c3d 로 고쳤다"])

    def test_collapses_whitespace_and_caps_at_two_lines(self):
        text = "\n".join(f"{i} 줄에 a1b2c3d" for i in range(5))
        self.assertEqual(len(LI.context_of(text, "a1b2c3d")), 2)

    def test_missing_token_yields_nothing(self):
        self.assertEqual(LI.context_of("본문", "없는것"), [])


class Compare(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, body):
        p = os.path.join(self.tmp.name, name)
        with open(p, "w", encoding="utf-8") as f:
            f.write(body)
        return p

    def test_reports_only_identifiers_the_new_version_dropped(self):
        old = self.write("old.md", "커밋 a1b2c3d 와 PR #123 을 다뤘다")
        new = self.write("new.md", "커밋 a1b2c3d 와 그 이슈를 다뤘다")
        _, _, oi, ni, lost = LI.compare(new, old)
        self.assertEqual(lost, {"#123"})
        self.assertIn("a1b2c3d", ni & oi)

    def test_added_identifiers_do_not_count_as_lost(self):
        old = self.write("old.md", "커밋 a1b2c3d")
        new = self.write("new.md", "커밋 a1b2c3d 와 새로 붙인 V63")
        _, _, _, _, lost = LI.compare(new, old)
        self.assertEqual(lost, set())


if __name__ == "__main__":
    unittest.main()
