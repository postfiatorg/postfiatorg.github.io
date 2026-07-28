#!/usr/bin/env python3
"""Snapshot settled per-wave Opus usage from dedicated Anthropic API keys."""
from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parents[1]
HELPER_PATH = (
    Path("/home/pfrpc/repos/pfterminal-perf-probe/runs")
    / "opus5-visual-site-0123-20260727T002520Z"
    / "scripts/anthropic_billing_snapshot.py"
)
ADMIN_KEY_FILE = Path("/home/pfrpc/anthropic_admin.txt")
KEY_TO_LANE = {
    "apikey_01ETPF8aNWXS17BDVpWkzPQD": "pft",
    "apikey_01SkUWKM1VvMXAt2CR4H3Mk6": "cc",
}


def load_helper():
    spec = importlib.util.spec_from_file_location("anthropic_admin_helper", HELPER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load Anthropic helper: {HELPER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected object: {path}")
    return value


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def floor_minute(value: datetime) -> datetime:
    return value.replace(second=0, microsecond=0)


def ceil_minute(value: datetime) -> datetime:
    floored = floor_minute(value)
    return floored if value == floored else floored + timedelta(minutes=1)


def rfc3339(value: datetime) -> str:
    return value.isoformat(timespec="seconds").replace("+00:00", "Z")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--waves", nargs="+", type=int, required=True)
    args = parser.parse_args()
    helper = load_helper()
    admin_key = helper.read_key(ADMIN_KEY_FILE)
    cost_path = RUN_ROOT / "visual/opus/admin_costs.json"
    costs = load(cost_path) if cost_path.exists() else {}
    costs["_api_key_mapping"] = KEY_TO_LANE
    costs["_source"] = (
        "Anthropic Admin Usage API, one-minute buckets grouped by model and "
        "dedicated API key"
    )

    for wave in args.waves:
        records = [
            load(RUN_ROOT / f"visual/results/opus/{lane}/wave{wave}/agent_run.json")
            for lane in ("pft", "cc")
        ]
        start = floor_minute(
            min(parse_time(str(item["started_at"])) for item in records)
        )
        end = ceil_minute(
            max(parse_time(str(item["ended_at"])) for item in records)
        )
        start_text, end_text = rfc3339(start), rfc3339(end)
        params = [
            ("starting_at", start_text),
            ("ending_at", end_text),
            ("bucket_width", "1m"),
            ("limit", "1440"),
            ("group_by[]", "model"),
            ("group_by[]", "api_key_id"),
        ]
        raw = helper.admin_get(admin_key, params)
        if raw.get("_http_status") != 200:
            raise RuntimeError(
                f"Anthropic Admin API failed for wave {wave}: "
                f"HTTP {raw.get('_http_status')}"
            )
        summary = helper.summarize(
            raw, f"wave{wave}", start_text, end_text
        )
        output_dir = RUN_ROOT / "visual/opus/admin_usage"
        write_json(output_dir / f"wave{wave}.usage_raw.json", raw)
        write_json(output_dir / f"wave{wave}.summary.json", summary)
        by_lane: dict[str, float] = {}
        for item in summary["by_model_key"]:
            key_id = str(item["api_key_id"])
            lane = KEY_TO_LANE.get(key_id)
            if lane is None:
                raise RuntimeError(
                    f"unexpected Anthropic key in wave {wave}: {key_id}"
                )
            by_lane[lane] = round(
                by_lane.get(lane, 0.0) + float(item["estimated_cost_usd"]), 12
            )
        missing = sorted(set(KEY_TO_LANE.values()) - set(by_lane))
        if missing:
            raise RuntimeError(
                f"Anthropic usage is not settled for wave {wave}; missing {missing}"
            )
        costs[f"wave{wave}"] = by_lane
        write_json(cost_path, costs)
        print(
            json.dumps(
                {
                    "event": "anthropic_wave_cost_snapshot",
                    "wave": wave,
                    "requested_start": start_text,
                    "requested_end": end_text,
                    "costs": by_lane,
                },
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
