"""Summarize parsed configuration rows.

This file contains a deliberate defect. See findings/python/py-002.json.
"""

from __future__ import annotations

from collections.abc import Iterator


def parse_rows(lines: list[str]) -> Iterator[dict[str, str]]:
    """Parse `name=value` lines lazily, so large files are not held in memory."""
    for line in lines:
        name, _, value = line.partition("=")
        yield {"name": name.strip(), "value": value.strip()}


def report(rows: Iterator[dict[str, str]]) -> str:
    """Describe how many rows were parsed and which ones had no value."""
    total = sum(1 for _ in rows)
    empty = [row["name"] for row in rows if not row["value"]]
    return f"{total} rows, {len(empty)} empty: {sorted(empty)}"


if __name__ == "__main__":
    print(report(parse_rows(["host=localhost", "port=", "debug=true"])))
