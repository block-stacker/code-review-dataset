"""Issue and check expiry of short-lived tokens.

This file contains a deliberate defect. See findings/python/py-004.json.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone


def issue_token(ttl: timedelta) -> dict[str, datetime]:
    """Issue a token expiring `ttl` from now.

    The timestamp is stored without a tzinfo because the storage layer's
    column is a naive TIMESTAMP. The value itself is UTC.
    """
    expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + ttl
    return {"expires_at": expires_at}


def is_expired(token: dict[str, datetime]) -> bool:
    """Return True once the token's expiry has passed."""
    return token["expires_at"] <= datetime.now()


if __name__ == "__main__":
    token = issue_token(timedelta(hours=1))
    print("stored expires_at:", token["expires_at"])
    print("compared against :", datetime.now())
    print("expired?", is_expired(token))
