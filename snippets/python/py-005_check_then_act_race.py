"""Register each job exactly once, from any number of worker threads.

This file contains a deliberate defect. See findings/python/py-005.json.
"""

from __future__ import annotations

import threading
import time

_jobs: dict[str, str] = {}
_submitted: list[str] = []


def _prepare(payload: str) -> str:
    """Stand in for the network round trip that normalizes a payload."""
    time.sleep(0.01)
    return payload.upper()


def register(job_id: str, payload: str) -> bool:
    """Register a job idempotently. Returns True if this caller created it."""
    if job_id in _jobs:
        return False
    prepared = _prepare(payload)
    _jobs[job_id] = prepared
    _submitted.append(prepared)
    return True


if __name__ == "__main__":
    workers = [
        threading.Thread(target=register, args=("job-1", f"payload-{n}")) for n in range(50)
    ]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join()
    print(f"one job id, submitted {len(_submitted)} time(s)")
