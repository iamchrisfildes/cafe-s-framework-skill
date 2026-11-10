import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from check_context import check_text, main


def checks(text):
    return [(finding.check, finding.line) for finding in check_text("doc.md", text)]


class PlanningNotes(unittest.TestCase):
    def test_flags_common_planning_notes(self):
        text = "Run the tests.\nTBD: choose a database.\nAdd the commands later.\nOwner to be confirmed.\n"
        self.assertEqual(checks(text), [("planning-note", 2), ("planning-note", 3), ("planning-note", 4)])

    def test_ignores_words_that_only_contain_the_letters(self):
        self.assertEqual(checks("The tbdata column holds the payload.\n"), [])


class StatusConflicts(unittest.TestCase):
    def test_flags_a_draft_status_and_an_approved_status(self):
        text = "Status: Approved by the owner.\n\nBody.\n\nThis is not yet approved; do not implement.\n"
        found = checks(text)
        self.assertIn(("status-conflict", 1), found)
        self.assertIn(("status-conflict", 5), found)

    def test_flags_a_stale_before_approval_line_under_an_approved_status(self):
        text = "Status: Approved.\n\nDo not implement before this specification is approved.\n"
        self.assertEqual([c for c in checks(text) if c[0] == "status-conflict"], [("status-conflict", 1), ("status-conflict", 3)])

    def test_a_single_consistent_status_is_fine(self):
        self.assertEqual(checks("Status: Approved by the owner on 2026-11-10.\n"), [])

    def test_two_draft_lines_are_not_a_conflict(self):
        self.assertEqual(checks("Status: Draft\n\n**Status:** draft for review\n"), [])


class EnvironmentTerms(unittest.TestCase):
    def test_flags_an_environment_word_with_no_value(self):
        self.assertEqual(checks("Turn on verbose logging in local development.\n"), [("environment-term", 1)])

    def test_an_exact_value_on_the_line_settles_it(self):
        self.assertEqual(checks("Turn on verbose logging when the environment is `Development`.\n"), [])

    def test_ignores_code_blocks(self):
        self.assertEqual(checks("```\nrun locally\n```\n"), [])


class ProhibitionOnly(unittest.TestCase):
    def test_flags_a_rule_with_no_alternative(self):
        self.assertEqual(checks("Never edit the generated files.\nThe build is fast.\n"), [("prohibition-only", 1)])

    def test_an_alternative_in_the_same_sentence_is_fine(self):
        self.assertEqual(checks("Never edit the generated files; regenerate them instead.\n"), [])

    def test_an_alternative_in_the_next_sentence_is_fine(self):
        self.assertEqual(checks("Do not push to main. Open a PR to develop instead.\n"), [])


class CleanDocument(unittest.TestCase):
    def test_a_clean_document_has_no_hints(self):
        text = (
            "# Release checklist\n\n"
            "Goal: publish version 1.4.0 to the `prod-eu` cluster.\n\n"
            "1. Run `make test` and confirm it passes.\n"
            "2. Tag the commit `v1.4.0`.\n"
            "3. You are done when the deploy job shows `succeeded`.\n"
        )
        self.assertEqual(checks(text), [])


class CommandLine(unittest.TestCase):
    def test_prints_hints_with_locations_and_exits_zero(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as handle:
            handle.write("TODO: write this.\n")
            path = handle.name
        try:
            output = io.StringIO()
            with redirect_stdout(output):
                code = main([path])
            self.assertEqual(code, 0)
            self.assertIn(f"Location: {path}:1", output.getvalue())
            self.assertIn("Check: planning-note", output.getvalue())
        finally:
            os.unlink(path)

    def test_a_missing_file_is_a_usage_error(self):
        self.assertEqual(main(["/nonexistent/file.md"]), 2)


if __name__ == "__main__":
    unittest.main()
