#!/usr/bin/env python3
"""Validate split XRPL seed-13 packet boundaries before replay."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

HISTORICAL_PACKET_FORBIDDEN_KEYS = {
    "xrpl_vote_outcome",
    "historical_outcome",
    "source_status_context",
    "route_hint",
    "risk_class",
    "controversy_score",
    "signals",
}
ALL_PACKET_FORBIDDEN_TEXT = {
    "hold_for_challenge",
    "delay_for_fix",
    "proceed_after_review",
    "proceed",
    "reject",
}
HISTORICAL_PACKET_FORBIDDEN_TEXT = {
    "vote reversal",
    "validators revoke",
    "revoking amm support",
    "revoke-votes",
    "not-launching",
    "validator no-vote response",
    "\"status\": \"enabled\"",
    "\"status\": \"open for voting\"",
    "\"status\": \"obsolete\"",
}


def iter_keys(value: Any) -> list[str]:
    keys: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            keys.append(str(key))
            keys.extend(iter_keys(child))
    elif isinstance(value, list):
        for item in value:
            keys.extend(iter_keys(item))
    return keys


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    args = parser.parse_args(argv)

    root = args.packet.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    historical_dir = root / "historical_vote_replay"
    prospective_dir = root / "prospective_open_vote_replay"
    excluded_dir = root / "excluded_cases"

    historical_labels = load_json(historical_dir / "historical_vote_labels.json")["labels"]
    prospective_cases = load_json(prospective_dir / "prospective_vote_metadata.json")["cases"]
    excluded_cases = load_json(excluded_dir / "excluded_cases.json")["cases"]

    if len(historical_labels) != 7:
        errors.append(f"historical packet count is {len(historical_labels)}, expected 7")
    if len(prospective_cases) != 5:
        errors.append(f"prospective packet count is {len(prospective_cases)}, expected 5")
    if len(excluded_cases) != 1:
        errors.append(f"excluded packet count is {len(excluded_cases)}, expected 1")

    for packet_path in sorted((historical_dir / "amendment_packets").glob("*.json")):
        packet = load_json(packet_path)
        packet_id = packet["packet_id"]
        keys = set(iter_keys(packet))
        forbidden_keys = sorted(keys & HISTORICAL_PACKET_FORBIDDEN_KEYS)
        if forbidden_keys:
            errors.append(f"{packet_id} historical prompt contains forbidden keys: {', '.join(forbidden_keys)}")
        text = packet_path.read_text(encoding="utf-8").lower()
        for phrase in sorted(ALL_PACKET_FORBIDDEN_TEXT | HISTORICAL_PACKET_FORBIDDEN_TEXT):
            if phrase in text:
                errors.append(f"{packet_id} historical prompt contains forbidden text: {phrase}")
        label = historical_labels.get(packet_id)
        if not label:
            errors.append(f"{packet_id} missing historical label")
            continue
        if label.get("historical_replay_eligible") is not True:
            errors.append(f"{packet_id} historical label is not eligible")
        if label.get("xrpl_vote_outcome") not in {"YES", "NO"}:
            errors.append(f"{packet_id} historical label is not an XRP-native YES/NO vote")
        if packet["amendment_or_event_name"] == label["event_name"] and any(
            token in label["event_name"].lower() for token in ("reversal", "no-vote", "enabled")
        ):
            errors.append(f"{packet_id} prompt name was not neutralized: {packet['amendment_or_event_name']}")

    for packet_path in sorted((prospective_dir / "amendment_packets").glob("*.json")):
        packet = load_json(packet_path)
        packet_id = packet["packet_id"]
        keys = set(iter_keys(packet))
        forbidden_keys = sorted(keys & {"xrpl_vote_outcome", "historical_outcome", "route_hint", "risk_class"})
        if forbidden_keys:
            errors.append(f"{packet_id} prospective prompt contains forbidden keys: {', '.join(forbidden_keys)}")
        text = packet_path.read_text(encoding="utf-8").lower()
        for phrase in sorted(ALL_PACKET_FORBIDDEN_TEXT):
            if phrase in text:
                errors.append(f"{packet_id} prospective prompt contains forbidden text: {phrase}")
        meta = prospective_cases.get(packet_id)
        if not meta:
            errors.append(f"{packet_id} missing prospective metadata")
        elif meta.get("historical_replay_eligible") is not False:
            errors.append(f"{packet_id} prospective metadata is marked historical")

    report = {
        "packet": root.relative_to(REPO_ROOT).as_posix(),
        "historical_count": len(historical_labels),
        "prospective_count": len(prospective_cases),
        "excluded_count": len(excluded_cases),
        "errors": errors,
        "warnings": warnings,
        "valid": not errors,
    }
    (root / "VALIDATION.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (root / "VALIDATION.md").write_text(
        "\n".join(
            [
                "# XRPL Split Seed-13 Validation",
                "",
                f"- Historical packets: {len(historical_labels)}",
                f"- Prospective packets: {len(prospective_cases)}",
                f"- Excluded cases: {len(excluded_cases)}",
                f"- Valid: {str(not errors).lower()}",
                "",
                "## Errors",
                "",
                *([f"- {error}" for error in errors] if errors else ["- None."]),
                "",
                "## Warnings",
                "",
                *([f"- {warning}" for warning in warnings] if warnings else ["- None."]),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, sort_keys=True))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
