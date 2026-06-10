#!/usr/bin/env python3
"""Refresh the homepage's build-time data snapshots from the live public APIs.

Writes:
  static/benchmarks/live-testnet-validator-stats.json
      Validator summary computed from the live VHS API with the same rules the
      homepage JS uses (revoked validators excluded, 24h agreement >= 0.999,
      30d agreement >= 0.99, ledger = max current_index). This file is both
      the JS fallback payload and the source for the statically rendered
      validator card.
  data/task_feed_snapshot.json
      The most recent public Task Node feed items, rendered statically into
      the homepage at build time and live-refreshed by JS in the browser.

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
FEED_URL = "https://pftasks-api.fly.dev/activity/public-feed?limit=24"
STATS_PATH = REPO / "static" / "benchmarks" / "live-testnet-validator-stats.json"
FEED_PATH = REPO / "data" / "task_feed_snapshot.json"
FEED_ITEMS = 8


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


def display_time(iso: str) -> str:
    # Always include the year: undated or year-less timestamps next to a
    # dated whitepaper read as inconsistent to careful reviewers.
    try:
        stamp = dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError:
        return "UTC"
    return stamp.strftime("%b %-d, %Y, %H:%M UTC")


def diversify_by_actor(raw_items: list, limit: int, per_actor: int = 2) -> list:
    """Prefer a mix of contributors over a single node's burst of activity."""
    picked: list = []
    counts: dict[str, int] = {}
    deferred: list = []
    for item in raw_items:
        actor = str(item.get("actor") or "node")
        if counts.get(actor, 0) < per_actor:
            picked.append(item)
            counts[actor] = counts.get(actor, 0) + 1
        else:
            deferred.append(item)
        if len(picked) >= limit:
            return picked
    return (picked + deferred)[:limit]


def build_feed_snapshot(payload: dict, now_iso: str) -> dict:
    items = []
    for item in diversify_by_actor(payload.get("items", []), FEED_ITEMS):
        title = (item.get("title") or item.get("summary") or "Task Node update").strip()
        summary = (item.get("summary") or "").strip()
        if title.endswith("...") and summary:
            title = summary
        items.append(
            {
                "category": str(item.get("category") or item.get("type") or "network")
                .replace("_", " ")
                .strip(),
                "timestamp": item.get("timestamp") or "",
                "display_time": display_time(item.get("timestamp") or ""),
                "title": title[:132],
                "summary": summary[:150],
                "actor": (item.get("actor") or "node").strip(),
                "tickers": [str(t).lstrip("$") for t in (item.get("tickers") or [])][:4],
                "links": [
                    {
                        "label": (link.get("label") or "PFTL proof").strip(),
                        "url": link.get("url") or "",
                    }
                    for link in (item.get("links") or [])
                    if str(link.get("url") or "").startswith("https://")
                ][:2],
            }
        )
    return {
        "generated_at": now_iso,
        "generated_at_display": display_time(now_iso),
        "source": FEED_URL,
        "items": items,
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

    feed = build_feed_snapshot(fetch_json(FEED_URL), now_iso)
    FEED_PATH.parent.mkdir(parents=True, exist_ok=True)
    FEED_PATH.write_text(json.dumps(feed, indent=2) + "\n", encoding="utf-8")
    print(f"task feed: {len(feed['items'])} items -> {FEED_PATH.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
