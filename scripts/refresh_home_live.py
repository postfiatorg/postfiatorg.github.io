#!/usr/bin/env python3
"""Refresh the homepage's build-time data snapshots from the live public APIs.

Writes:
  static/benchmarks/live-testnet-validator-stats.json
      Validator summary computed from the live VHS API with the same rules the
      homepage JS uses (revoked validators excluded, 24h agreement >= 0.999,
      30d agreement >= 0.99, ledger = max current_index). This file is both
      the JS fallback payload and the source for the statically rendered
      validator card.

Run before a deploy (or on a schedule) to keep the no-JS view current:
  python3 scripts/refresh_home_live.py
"""

from __future__ import annotations

import datetime as dt
import json
import pathlib
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[1]
VHS_URL = "https://vhs.testnet.postfiat.org/v1/network/validators/test"
STATS_PATH = REPO / "static" / "benchmarks" / "live-testnet-validator-stats.json"


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def agreement_score(validator: dict, key: str) -> float:
    try:
        return float((validator.get(key) or {}).get("score") or 0.0)
    except (TypeError, ValueError):
        return 0.0


def build_validator_stats(payload: dict, now_iso: str) -> dict:
    validators = [v for v in payload.get("validators", []) if not v.get("revoked")]
    total = len(validators)
    strong24 = sum(1 for v in validators if agreement_score(v, "agreement_24h") >= 0.999)
    strong30 = sum(1 for v in validators if agreement_score(v, "agreement_30day") >= 0.99)

    def mean(key: str) -> float:
        scores = [agreement_score(v, key) for v in validators]
        return sum(scores) / len(scores) if scores else 0.0

    return {
        "generated_at": now_iso,
        "source_name": "Live VHS snapshot",
        "source_url": VHS_URL,
        "validator_count": total,
        "publishing_domain_count": sum(
            1 for v in validators if str(v.get("domain") or "").strip()
        ),
        "verified_domain_count": sum(1 for v in validators if v.get("domain_verified")),
        "latest_ledger_index": max(
            (int(v.get("current_index") or 0) for v in validators), default=0
        ),
        "agreement_24h": {
            "threshold": 0.999,
            "threshold_label": "99.9%+",
            "count": strong24,
            "ratio": (strong24 / total) if total else 0.0,
            "mean_score": mean("agreement_24h"),
        },
        "agreement_30day": {
            "threshold": 0.99,
            "threshold_label": "99%+",
            "count": strong30,
            "ratio": (strong30 / total) if total else 0.0,
            "mean_score": mean("agreement_30day"),
        },
    }


def main() -> int:
    now_iso = (
        dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds")
    ).replace("+00:00", "Z")

    stats = build_validator_stats(fetch_json(VHS_URL), now_iso)
    STATS_PATH.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    print(
        f"validator stats: {stats['validator_count']} validators, "
        f"{stats['publishing_domain_count']} domains, "
        f"ledger {stats['latest_ledger_index']:,} -> {STATS_PATH.relative_to(REPO)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
