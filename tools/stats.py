"""Report what the dataset actually contains.

A hand-built dataset drifts toward whatever its author finds easiest to write,
and the drift is invisible from inside. This prints the composition so the gaps
are visible: which categories are empty, whether one language is carrying the
severity distribution, and how long the prose fields have grown.
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent

SEVERITIES = ["critical", "high", "medium", "low"]
PROSE_FIELDS = ["explanation", "trigger", "fix_rationale"]


def load_findings(repo_root: Path) -> list[dict[str, Any]]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((repo_root / "findings").rglob("*.json"))
    ]


def schema_categories(repo_root: Path) -> list[str]:
    """Read the category vocabulary from the schema, so the two cannot disagree."""
    schema = json.loads((repo_root / "schema" / "finding.schema.json").read_text(encoding="utf-8"))
    categories = schema["properties"]["category"]["enum"]
    return list(categories)


def _bar(count: int, width: int = 24) -> str:
    return "#" * min(count, width)


def _table(title: str, counts: Counter[str], keys: list[str]) -> str:
    lines = [title, "-" * len(title)]
    width = max((len(k) for k in keys), default=0)
    for key in keys:
        count = counts.get(key, 0)
        marker = "" if count else "   (none yet)"
        lines.append(f"  {key.ljust(width)}  {count:>3}  {_bar(count)}{marker}")
    return "\n".join(lines)


def report(repo_root: Path = REPO_ROOT) -> str:
    records = load_findings(repo_root)
    if not records:
        return "No findings."

    languages = Counter(r["language"] for r in records)
    severities = Counter(r["severity"] for r in records)
    categories = Counter(r["category"] for r in records)

    sections = [
        f"{len(records)} findings",
        "",
        _table("By language", languages, sorted(languages)),
        "",
        _table("By severity", severities, SEVERITIES),
        "",
        _table("By category", categories, schema_categories(repo_root)),
        "",
        "Prose length (characters)",
        "-------------------------",
    ]

    width = max(len(f) for f in PROSE_FIELDS)
    for field in PROSE_FIELDS:
        lengths = [len(r[field]) for r in records]
        sections.append(
            f"  {field.ljust(width)}  median {int(statistics.median(lengths)):>4}"
            f"   min {min(lengths):>4}   max {max(lengths):>4}"
        )

    without_distractors = [r["id"] for r in records if not r.get("distractors")]
    sections += ["", "Records with no distractors recorded"]
    sections.append("  " + (", ".join(without_distractors) if without_distractors else "none"))

    return "\n".join(sections)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    print(report(args.repo_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
