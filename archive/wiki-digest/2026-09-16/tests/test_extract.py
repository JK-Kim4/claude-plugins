#!/usr/bin/env python3
"""extract.py 동작 고정.

    python3 -m unittest discover -s wiki-digest/tests

원본 JSONL 은 수십 MB 라 통째로 읽으면 컨텍스트가 망가진다. 그래서 이 스크립트가
무엇을 버리고 무엇을 남기는지가 곧 세션 문서의 품질이다 — 특히 시스템 주입을
사용자 발화로 착각하지 않는 것과, 도구 판별이 메타데이터에 밀리지 않는 것.
"""
import os, sys, json, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "scripts"))

import extract as E


def jsonl(objs):
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        for o in objs:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
    return path


class Detect(unittest.TestCase):
    def tearDown(self):
        if getattr(self, "path", None):
            os.unlink(self.path)

    def test_claude_by_conversation_type(self):
        self.path = jsonl([{"type": "user", "message": {"content": "안녕"}}])
        self.assertEqual(E.detect(self.path), "claude")

    def test_codex_by_event_type(self):
        self.path = jsonl([{"type": "session_meta"}])
        self.assertEqual(E.detect(self.path), "codex")

    def test_claude_recognised_behind_metadata_lines(self):
        # 대화 항목이 수십 줄 뒤에 처음 나오는 세션이 실제로 있다.
        self.path = jsonl([{"type": "file-history-snapshot"}] * 30
                          + [{"type": "user", "message": {"content": "x"}}])
        self.assertEqual(E.detect(self.path), "claude")

    def test_unknown_when_nothing_matches(self):
        self.path = jsonl([{"type": "무엇"} for _ in range(60)])
        self.assertEqual(E.detect(self.path), "unknown")

    def test_broken_json_lines_are_skipped(self):
        fd, self.path = tempfile.mkstemp(suffix=".jsonl")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("{깨진 줄\n\n")
            f.write(json.dumps({"type": "user", "message": {"content": "x"}}) + "\n")
        self.assertEqual(E.detect(self.path), "claude")


class TextOf(unittest.TestCase):
    def test_plain_string(self):
        self.assertEqual(E._text_of("본문"), "본문")

    def test_joins_text_blocks_only(self):
        blocks = [{"type": "text", "text": "하나"},
                  {"type": "tool_use", "text": "버릴 것"},
                  {"type": "output_text", "text": "둘"}]
        self.assertEqual(E._text_of(blocks), "하나\n둘")

    def test_unexpected_shape_returns_empty(self):
        self.assertEqual(E._text_of({"type": "text"}), "")


class ParseClaude(unittest.TestCase):
    def tearDown(self):
        os.unlink(self.path)

    def test_drops_system_injections_masquerading_as_user_turns(self):
        self.path = jsonl([
            {"type": "user", "message": {"content": "진짜 요청"}},
            {"type": "user", "message": {"content": "<command-name>/compact</command-name>"}},
            {"type": "user", "message": {"content": "<system-reminder>무시</system-reminder>"}},
            {"type": "user", "message": {"content": "Caveat: 이건 도구가 넣은 것"}},
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "응답"}]}},
        ])
        users, assists = E.parse_claude(self.path)
        self.assertEqual(users, ["진짜 요청"])
        self.assertEqual(assists, ["응답"])

    def test_empty_assistant_turns_are_dropped(self):
        self.path = jsonl([{"type": "assistant", "message": {"content": [
            {"type": "tool_use", "text": "도구만"}]}}])
        self.assertEqual(E.parse_claude(self.path), ([], []))


class ParseCodex(unittest.TestCase):
    def tearDown(self):
        os.unlink(self.path)

    def test_splits_user_and_agent_messages(self):
        self.path = jsonl([
            {"type": "event_msg", "payload": {"type": "user_message", "message": "요청"}},
            {"type": "event_msg", "payload": {"type": "agent_message", "message": "응답"}},
            {"type": "response_item", "payload": {"type": "user_message", "message": "무시"}},
        ])
        self.assertEqual(E.parse_codex(self.path), (["요청"], ["응답"]))


class CodexCwd(unittest.TestCase):
    def tearDown(self):
        os.unlink(self.path)

    def test_reads_cwd_from_leading_meta(self):
        self.path = jsonl([{"type": "session_meta", "payload": {"cwd": "/repo"}}])
        self.assertEqual(E.codex_cwd(self.path), "/repo")

    def test_stops_at_first_non_meta_line(self):
        self.path = jsonl([{"type": "event_msg", "payload": {}},
                           {"type": "session_meta", "payload": {"cwd": "/repo"}}])
        self.assertIsNone(E.codex_cwd(self.path))


class Sample(unittest.TestCase):
    def test_everything_fits_under_budget(self):
        items = ["a" * 10] * 3
        self.assertEqual(E.sample(items, 1000), items)

    def test_keeps_head_and_tail_with_a_gap_marker(self):
        items = [f"{i}" * 10 for i in range(10)]
        out = E.sample(items, 45)
        self.assertIn("…", out)
        self.assertEqual(out[0], items[0])
        self.assertEqual(out[-1], items[-1])

    def test_budget_is_never_exceeded_by_content(self):
        items = [f"{i}" * 10 for i in range(10)]
        out = E.sample(items, 45)
        self.assertLessEqual(sum(len(s) for s in out if s != "…"), 45)


class Ident(unittest.TestCase):
    def test_picks_up_hashes_branches_and_versions(self):
        found = {m.group(0) for m in E.IDENT.finditer(
            "커밋 a1b2c3d 와 feature/foo-bar 그리고 V42 를 남겼다")}
        self.assertEqual(found, {"a1b2c3d", "feature/foo-bar", "V42"})


if __name__ == "__main__":
    unittest.main()
