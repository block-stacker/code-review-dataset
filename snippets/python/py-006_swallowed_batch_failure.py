"""Import a batch of records, tolerating individual bad rows.

This file contains a deliberate defect. See findings/python/py-006.json.
"""

from __future__ import annotations

from typing import Any


def _parse(raw: str) -> dict[str, str]:
    """Parse one `name=value` record, rejecting records with no name."""
    name, _, value = raw.partition("=")
    if not name.strip():
        raise ValueError(f"missing name in {raw!r}")
    return {"name": name.strip(), "value": value.strip()}


def import_batch(raw_records: list[str]) -> dict[str, Any]:
    """Import every record, skipping ones that fail to parse."""
    imported: list[dict[str, str]] = []
    try:
        for raw in raw_records:
            imported.append(_parse(raw))
    except Exception:
        pass
    return {"ok": True, "imported": len(imported), "total": len(raw_records)}


if __name__ == "__main__":
    print(import_batch(["host=localhost", "=orphaned", "port=8080"]))
