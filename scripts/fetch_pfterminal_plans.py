#!/usr/bin/env python3
"""Refresh data/pfterminal_plans.json from the live PfTerminal plan gateway.

The /terminal/ page renders plan prices server-side from this file so the numbers
exist in static HTML for non-executing agents. Never hand-edit the prices; run
this script instead.

    python3 scripts/fetch_pfterminal_plans.py

Exits non-zero without touching the file if the gateway is unreachable or the
payload does not look like a plan catalogue, so a bad fetch cannot publish a
wrong price.
"""

from __future__ import annotations

import datetime as dt
import json
import pathlib
import sys
import urllib.request

SOURCE = "https://pfterminal-plan-gateway.fly.dev/v1/plans"
OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "pfterminal_plans.json"
REQUIRED_PLAN_KEYS = {"id", "priceUsdc", "termMonths", "weeklyTokenLimit", "monthlyTokenLimit"}


def main() -> int:
    try:
        with urllib.request.urlopen(SOURCE, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"plan catalogue fetch failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    plans = payload.get("plans")
    if not isinstance(plans, list) or not plans:
        print("plan catalogue payload had no plans; refusing to write", file=sys.stderr)
        return 1
    for plan in plans:
        missing = REQUIRED_PLAN_KEYS - set(plan)
        if missing:
            print(f"plan {plan.get('id')!r} missing {sorted(missing)}; refusing to write", file=sys.stderr)
            return 1

    payload["source"] = SOURCE
    payload["fetched_at_utc"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT} with {len(plans)} plans: "
          + ", ".join(f"{p['id']}={p['priceUsdc']} USDC" for p in plans))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
