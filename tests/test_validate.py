"""Tests for the dataset validator.

These exercise the rejection paths. A validator that accepts everything
passes just as cleanly on a correct dataset as a real one does, so the
cases that matter are the ones that must fail.

Run with:  python3 -m unittest discover -s tests
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import validate  # noqa: E402  (import follows the sys.path change above)


def a_valid_record(**overrides: Any) -> dict[str, Any]:
    """Build a record that passes, so each test can break exactly one thing."""
    record: dict[str, Any] = {
        "id": "py-001",
        "language": "python",
        "snippet": "snippets/python/py-001_example.py",
        "title": "Example defect used only by the test suite",
        "category": "correctness",
        "severity": "high",
        "defect_lines": [1],
        "explanation": (
            "A placeholder explanation that is long enough to clear the schema's "
            "minimum length, because the schema deliberately rejects short "
            "explanations as unreviewed placeholders."
        ),
        "trigger": "Calling the function twice with the same argument.",
        "observed": "Returns a stale value.",
        "expected": "Returns a freshly computed value.",
        "fix": "return compute(value)",
        "fix_rationale": (
            "Recomputing is correct here because the cache was never the point "
            "of the function."
        ),
        "distractors": [],
        "references": [],
        "annotator": "block-stacker",
        "annotated_on": "2026-09-09",
    }
    record.update(overrides)
    return record


class ValidatorTestCase(unittest.TestCase):
    """Base class providing a throwaway repository on disk for each test."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

        (self.root / "schema").mkdir()
        shutil.copy(
            REPO_ROOT / "schema" / "finding.schema.json",
            self.root / "schema" / "finding.schema.json",
        )
        for language in ("python", "typescript"):
            (self.root / "findings" / language).mkdir(parents=True)
            (self.root / "snippets" / language).mkdir(parents=True)

    def write_snippet(self, relative: str, lines: int = 5) -> None:
        path = self.root / relative
        path.write_text("\n".join(f"line {n}" for n in range(1, lines + 1)), encoding="utf-8")

    def write_record(self, language: str, name: str, record: Any) -> None:
        path = self.root / "findings" / language / name
        text = record if isinstance(record, str) else json.dumps(record, indent=2)
        path.write_text(text, encoding="utf-8")

    def messages(self) -> str:
        return "\n".join(str(problem) for problem in validate.validate_all(self.root))


class TestAcceptsValidRecords(ValidatorTestCase):
    def test_a_consistent_record_produces_no_problems(self) -> None:
        self.write_snippet("snippets/python/py-001_example.py")
        self.write_record("python", "py-001.json", a_valid_record())

        self.assertEqual(validate.validate_all(self.root), [])

    def test_an_empty_dataset_is_reported_rather_than_silently_passing(self) -> None:
        self.assertIn("no finding records found", self.messages())


class TestSchemaViolations(ValidatorTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.write_snippet("snippets/python/py-001_example.py")

    def test_missing_required_field_is_rejected(self) -> None:
        record = a_valid_record()
        del record["trigger"]
        self.write_record("python", "py-001.json", record)

        self.assertIn("trigger", self.messages())

    def test_unknown_field_is_rejected_rather_than_ignored(self) -> None:
        self.write_record("python", "py-001.json", a_valid_record(sevrity="high"))

        self.assertIn("sevrity", self.messages())

    def test_severity_outside_the_enum_is_rejected(self) -> None:
        self.write_record("python", "py-001.json", a_valid_record(severity="showstopper"))

        self.assertIn("severity", self.messages())

    def test_placeholder_explanation_is_rejected_for_being_too_short(self) -> None:
        self.write_record("python", "py-001.json", a_valid_record(explanation="It is wrong."))

        self.assertIn("explanation", self.messages())

    def test_malformed_json_names_the_file_it_came_from(self) -> None:
        self.write_record("python", "py-001.json", "{not json")

        self.assertIn("py-001.json", self.messages())


class TestCrossFileConsistency(ValidatorTestCase):
    def test_id_must_match_the_filename(self) -> None:
        self.write_snippet("snippets/python/py-002_example.py")
        self.write_record(
            "python",
            "py-002.json",
            a_valid_record(id="py-001", snippet="snippets/python/py-002_example.py"),
        )

        self.assertIn("does not match filename stem", self.messages())

    def test_language_must_match_the_directory(self) -> None:
        self.write_snippet("snippets/python/py-001_example.py")
        self.write_record("typescript", "py-001.json", a_valid_record())

        self.assertIn("filed under", self.messages())

    def test_missing_snippet_is_reported(self) -> None:
        self.write_record("python", "py-001.json", a_valid_record())

        self.assertIn("snippet not found", self.messages())

    def test_snippet_filename_must_carry_the_id_as_a_prefix(self) -> None:
        self.write_snippet("snippets/python/unrelated_name.py")
        self.write_record(
            "python", "py-001.json", a_valid_record(snippet="snippets/python/unrelated_name.py")
        )

        self.assertIn("is not prefixed with id", self.messages())

    def test_defect_line_past_the_end_of_the_snippet_is_reported(self) -> None:
        self.write_snippet("snippets/python/py-001_example.py", lines=5)
        self.write_record("python", "py-001.json", a_valid_record(defect_lines=[3, 99]))

        message = self.messages()
        self.assertIn("cites line 99", message)
        self.assertNotIn("cites line 3", message)

    def test_the_same_id_cannot_be_used_in_two_languages(self) -> None:
        self.write_snippet("snippets/python/py-001_example.py")
        self.write_snippet("snippets/typescript/py-001_example.ts")
        self.write_record("python", "py-001.json", a_valid_record())
        self.write_record(
            "typescript",
            "py-001.json",
            a_valid_record(language="typescript", snippet="snippets/typescript/py-001_example.ts"),
        )

        self.assertIn("already used by", self.messages())


class TestReportsEveryProblem(ValidatorTestCase):
    def test_one_record_with_several_faults_reports_all_of_them(self) -> None:
        self.write_snippet("snippets/python/py-001_example.py")
        record = a_valid_record(severity="showstopper", category="vibes")
        del record["expected"]
        self.write_record("python", "py-001.json", record)

        problems = validate.validate_all(self.root)
        self.assertGreaterEqual(len(problems), 3)


if __name__ == "__main__":
    unittest.main()
