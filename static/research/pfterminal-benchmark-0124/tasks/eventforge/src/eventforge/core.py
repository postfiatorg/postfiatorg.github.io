"""EventForge ledger replay implementation.

The benchmark starts with deliberately incomplete code. Implement the contract in
../../task_prompt.md.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def replay_events(lines: Iterable[str], as_of: str | None = None) -> dict[str, Any]:
    """Replay JSONL ledger events.

    This stub only exists so imports work before the benchmark agent starts.
    Replace it with a correct implementation.
    """

    return {"accounts": {}, "applied_event_ids": [], "diagnostics": []}


def monthly_report(lines: Iterable[str], month: str) -> dict[str, Any]:
    """Return a monthly posted-balance report.

    This stub only exists so imports work before the benchmark agent starts.
    Replace it with a correct implementation.
    """

    return {"month": month, "accounts": {}, "diagnostics": []}
