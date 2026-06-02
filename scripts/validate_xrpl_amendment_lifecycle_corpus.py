#!/usr/bin/env python3
"""Validate XRPL amendment lifecycle replay corpus and blind packets."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from xrpl_lifecycle_common import LANES, artifact_path, read_json, write_json


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def walk_values(value: Any) -> list[str]:
    if isinstance(value, dict):
        out: list[str] = []
        for key, item in value.items():
            if key in {"allowed_labels", "held_out_fields"}:
                continue
            out.extend(walk_values(item))
        return out
    if isinstance(value, list):
        out = []
        for item in value:
            out.extend(walk_values(item))
        return out
    if isinstance(value, str):
        return [value]
    return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--min-selected", type=int, default=60)
    parser.add_argument("--min-terminal-yes", type=int, default=40)
    parser.add_argument("--min-nonterminal-state", type=int, default=10)
    parser.add_argument("--min-sensitive-triage", type=int, default=10)
    parser.add_argument("--allow-missing-h200-receipt", action="store_true")
    args = parser.parse_args(argv)

    root = artifact_path(args.artifact)
    corpus_dir = root / "corpus"
    errors: list[str] = []
    warnings: list[str] = []

    events = read_json(corpus_dir / "lifecycle_events.json")
    selected = read_json(corpus_dir / "corpus_selection.json")
    universe = read_json(corpus_dir / "amendment_universe.json")
    state_receipts = read_json(corpus_dir / "state_receipts.json")
    source_receipts = read_json(corpus_dir / "source_receipts.json")

    selected_ids = {event["event_id"] for event in selected}
    selected_events = [event for event in events if event["event_id"] in selected_ids]
    selected_by_id = {event["event_id"]: event for event in selected_events}
    event_by_id = {event["event_id"]: event for event in events}

    if len(selected) < args.min_selected:
        fail(errors, f"selected lifecycle rows < {args.min_selected}: {len(selected)}")
    terminal_yes = sum(1 for event in selected if event["terminal_outcome"] == "YES")
    if terminal_yes < args.min_terminal_yes:
        fail(errors, f"terminal YES rows < {args.min_terminal_yes}: {terminal_yes}")
    nonterminal_state = sum(
        1
        for event in selected
        if event["terminal_outcome"] == "NONE"
        and event["vote_state_label"] in {"NO_MAJORITY", "MAJORITY_ACTIVE", "MAJORITY_LOST", "UNKNOWN"}
    )
    if nonterminal_state < args.min_nonterminal_state:
        fail(errors, f"nonterminal vote-state rows < {args.min_nonterminal_state}: {nonterminal_state}")
    triage_sensitive = sum(1 for event in selected if event["triage_policy_label"] != "PROCEED")
    if triage_sensitive < args.min_sensitive_triage:
        fail(errors, f"governance-sensitive triage rows < {args.min_sensitive_triage}: {triage_sensitive}")

    receipt_errors = [sid for sid, receipt in source_receipts.items() if not receipt.get("sha256") or not receipt.get("bytes")]
    if receipt_errors:
        fail(errors, f"source receipts missing bytes/hash: {receipt_errors}")

    if not args.allow_missing_h200_receipt and not (root / "vast_lifecycle" / "machine_receipt.json").exists():
        fail(errors, "H200 runtime manifest missing vast_lifecycle/machine_receipt.json")

    ledger_count = int(state_receipts.get("validated_amendment_count", 0))
    enabled_universe = [row for row in universe if row.get("current_enabled")]
    if ledger_count and len(enabled_universe) != ledger_count:
        warnings.append(f"universe enabled count {len(enabled_universe)} differs from ledger Amendments count {ledger_count}")

    for row in universe:
        if row.get("current_enabled") and not row.get("amendment_id"):
            fail(errors, f"enabled universe row missing amendment_id: {row.get('name')}")
        if not row.get("current_enabled") and row.get("source_default_vote") == "NO":
            pass

    for event in selected:
        if event["terminal_outcome"] == "NO" and event["vote_state_label"] == "NO_MAJORITY":
            fail(errors, f"non-enabled below-threshold event labeled terminal NO: {event['event_id']}")
        if event["terminal_outcome"] == "YES" and event["vote_state_label"] != "ENABLED":
            fail(errors, f"terminal YES without ENABLED state: {event['event_id']}")
        if event["terminal_outcome"] == "NONE" and "vote_outcome" in event["eligible_metrics"]:
            fail(errors, f"NONE terminal event eligible for vote_outcome: {event['event_id']}")

    packet_counts: dict[str, int] = {}
    label_counts: dict[str, Counter[str]] = {}
    for lane in LANES:
        labels_path = root / "labels" / f"{lane}_labels.json"
        labels = read_json(labels_path)
        packet_paths = sorted((root / "packets" / lane).glob("*.json"))
        packet_counts[lane] = len(packet_paths)
        label_counts[lane] = Counter(item["expected_label"] for item in labels.values())
        if len(packet_paths) != len(labels):
            fail(errors, f"{lane}: packet count {len(packet_paths)} != label count {len(labels)}")
        for packet_path in packet_paths:
            packet = read_json(packet_path)
            pid = packet["packet_id"]
            identity_text = f"{packet.get('packet_id', '')} {packet.get('event_id', '')}".upper()
            for forbidden_identity in ("ENABLED", "VETOED", "RETIRED", "MAJORITY", "OBSOLETE"):
                if forbidden_identity in identity_text:
                    fail(errors, f"{lane}: packet identity leaks status term {forbidden_identity}: {pid}")
            if pid not in labels:
                fail(errors, f"{lane}: missing label for {pid}")
                continue
            expected = labels[pid]["expected_label"]
            true_event_id = labels[pid].get("event_id", packet.get("event_id", ""))
            event = event_by_id.get(true_event_id)
            if not event:
                fail(errors, f"{lane}: packet event not found: {packet['event_id']} -> {true_event_id}")
                continue
            packet_text_values = walk_values(packet)
            combined_text = "\n".join(packet_text_values).upper()
            if "terminal_outcome" in packet or "vote_state_label" in packet or "triage_policy_label" in packet:
                fail(errors, f"{lane}: scored label field leaked into packet root: {pid}")
            if "event_type" in packet.get("input_context", {}) or "event_time" in packet.get("input_context", {}):
                fail(errors, f"{lane}: event_type/event_time leaked into packet input_context: {pid}")
            if lane == "vote_outcome":
                if "HOLD_FOR_CHALLENGE" in combined_text:
                    fail(errors, f"vote_outcome packet mentions HOLD_FOR_CHALLENGE: {pid}")
                if expected == "YES" and "ENABLED_ON" in combined_text:
                    fail(errors, f"vote_outcome terminal YES packet leaks enabled_on: {pid}")
                if event["terminal_outcome"] == "NONE":
                    fail(errors, f"vote_outcome packet built for nonterminal event: {pid}")
            if lane == "default_vote":
                fact_text = "\n".join(
                    str(item.get("claim", ""))
                    for item in packet.get("input_context", {}).get("source_facts", [])
                    if isinstance(item, dict)
                ).upper()
                if "DEFAULT VOTE (LATEST STABLE RELEASE)" in fact_text or "SOURCE_DEFAULT_VOTE" in fact_text:
                    fail(errors, f"default_vote packet leaks source default vote fact: {pid}")
            if lane == "triage":
                fact_text = "\n".join(
                    str(item.get("claim", ""))
                    for item in packet.get("input_context", {}).get("source_facts", [])
                    if isinstance(item, dict)
                ).upper()
                for forbidden_current_state in ("VALIDATED LEDGER AMENDMENTS OBJECT CURRENTLY CONTAINS", "ENABLED_ON=", "ENABLED_IN_LEDGER="):
                    if forbidden_current_state in fact_text:
                        fail(errors, f"triage packet leaks current enabled-state fact: {pid}")
            if lane != "triage" and event["triage_policy_label"] == expected:
                warnings.append(f"{lane}: expected equals triage label by string coincidence for {pid}")

    validation = {
        "artifact": str(root),
        "selected_rows": len(selected),
        "event_counts": dict(Counter(event["event_type"] for event in selected)),
        "terminal_counts": dict(Counter(event["terminal_outcome"] for event in selected)),
        "vote_state_counts": dict(Counter(event["vote_state_label"] for event in selected)),
        "triage_counts": dict(Counter(event["triage_policy_label"] for event in selected)),
        "packet_counts": packet_counts,
        "label_counts": {lane: dict(counter) for lane, counter in label_counts.items()},
        "errors": errors,
        "warnings": warnings,
        "valid": not errors,
    }
    write_json(root / "corpus" / "validation_report.json", validation)
    print(json.dumps(validation, indent=2, sort_keys=True))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
