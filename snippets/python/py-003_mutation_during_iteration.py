"""Drop expired sessions from an in-memory registry.

This file contains a deliberate defect. See findings/python/py-003.json.
"""

from __future__ import annotations


def prune_expired(sessions: list[dict[str, int]], now: int) -> int:
    """Remove every session whose deadline has passed, returning the count removed."""
    removed = 0
    for session in sessions:
        if session["expires_at"] <= now:
            sessions.remove(session)
            removed += 1
    return removed


if __name__ == "__main__":
    registry = [
        {"id": 1, "expires_at": 10},
        {"id": 2, "expires_at": 10},
        {"id": 3, "expires_at": 10},
        {"id": 4, "expires_at": 99},
    ]
    count = prune_expired(registry, now=50)
    print(f"removed {count}, still registered: {[s['id'] for s in registry]}")
