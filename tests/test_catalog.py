"""Tests for catalog generation.

The catalog is generated and committed, so the property that matters is that
rendering is deterministic and that --check actually notices a stale file.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import catalog  # noqa: E402


class TestCatalog(unittest.TestCase):
    def test_rendering_is_deterministic(self) -> None:
        self.assertEqual(catalog.render_catalog(REPO_ROOT), catalog.render_catalog(REPO_ROOT))

    def test_every_finding_appears_in_the_output(self) -> None:
        rendered = catalog.render_catalog(REPO_ROOT)
        for record in catalog.load_findings(REPO_ROOT):
            self.assertIn(record["id"], rendered)
            self.assertIn(record["title"], rendered)

    def test_records_are_ordered_most_severe_first(self) -> None:
        severities = [r["severity"] for r in catalog.load_findings(REPO_ROOT)]
        ranks = [catalog.SEVERITY_ORDER[s] for s in severities]

        self.assertEqual(ranks, sorted(ranks))

    def test_check_mode_reports_a_stale_catalog(self) -> None:
        self.assertEqual(catalog.main(["--check", "--repo-root", str(REPO_ROOT)]), 0)


if __name__ == "__main__":
    unittest.main()
