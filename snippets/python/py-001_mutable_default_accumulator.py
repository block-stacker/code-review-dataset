"""Group ingest records by source.

This file contains a deliberate defect. See findings/python/py-001.json.
"""

from __future__ import annotations


def collect_tags(record: dict[str, str], tags: list[str] = []) -> list[str]:
    """Append this record's tag to an accumulator and return the accumulator."""
    tag = record.get("tag")
    if tag is not None:
        tags.append(tag)
    return tags


def summarize(records: list[dict[str, str]]) -> dict[str, list[str]]:
    """Return the tags seen for each source, one fresh accumulator per record."""
    grouped: dict[str, list[str]] = {}
    for record in records:
        grouped[record["source"]] = collect_tags(record)
    return grouped


if __name__ == "__main__":
    print(summarize([{"source": "a", "tag": "x"}, {"source": "b", "tag": "y"}]))
