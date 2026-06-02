#!/usr/bin/env python3
"""Run deterministic baseline rules for XRPL amendment lifecycle replay lanes."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from xrpl_lifecycle_common import LANES, artifact_path, read_json, sha_json, write_json, write_sha256s


def packet_text(packet: dict[str, Any]) -> str:
    return json.dumps(packet.get("input_context", {}), sort_keys=True).lower()


def baseline_vote_outcome(packet: dict[str, Any]) -> tuple[str, list[str]]:
    text = packet_text(packet)
    rules = []
    if "advised to vote no" in text or "disabled" in text or "obsolete" in text or "unauthorized" in text:
        rules.append("explicit_no_advisory_or_obsolete")
        return "NO", rules
    if "bug" in text and ("not enabled" in text or "pre-activation" in text):
        rules.append("pre_activation_bug")
        return "NO", rules
    rules.append("enabled_amendment_prior")
    return "YES", rules


def baseline_vote_state(packet: dict[str, Any]) -> tuple[str, list[str]]:
    text = packet_text(packet)
    rules = []
    if "validated ledger amendments object currently contains" in text:
        rules.append("ledger_amendments_object_membership")
        return "ENABLED", rules
    if "obsolete" in text or "disabled" in text or "advised to vote no" in text:
        rules.append("obsolete_or_no_advisory")
        return "VETOED_OR_RETIRED", rules
    if "majority lost" in text or "pre-activation bug handling" in text:
        rules.append("majority_lost_or_bug_surface")
        return "MAJORITY_LOST", rules
    if "support count" in text and "threshold" in text:
        rules.append("below_or_at_threshold_vote_count")
        return "NO_MAJORITY", rules
    rules.append("insufficient_state_evidence")
    return "UNKNOWN", rules


def baseline_default_vote(packet: dict[str, Any]) -> tuple[str, list[str]]:
    text = packet_text(packet)
    rules = []
    if any(term in text for term in ("clawback", "amm", "batch", "permission", "credential", "vault", "lending", "mpt", "token escrow", "confidential")):
        rules.append("risk_surface_default_no_prior")
        return "NO", rules
    if any(term in text for term in ("fix", "cleanup", "invariant", "quality", "dry offer")):
        rules.append("fix_or_cleanup_default_yes_prior")
        return "YES", rules
    rules.append("unknown_default_vote")
    return "UNKNOWN", rules


def baseline_triage(packet: dict[str, Any]) -> tuple[str, list[str]]:
    text = packet_text(packet)
    rules = []
    if "advised to vote no" in text or "unauthorized" in text or "drain" in text:
        rules.append("explicit_no_or_critical_vulnerability")
        return "REJECT", rules
    if any(term in text for term in ("bug", "vulnerability", "discrepanc", "crash", "liveness")):
        rules.append("known_bug_or_liveness_risk")
        return "DELAY_FOR_FIX", rules
    if any(term in text for term in ("clawback", "permission", "credential", "lending", "vault", "amm", "mpt", "escrow", "issuer", "privacy", "compliance", "bridge")):
        rules.append("financial_or_compliance_review_surface")
        return "HOLD_FOR_CHALLENGE", rules
    rules.append("routine_or_cleanup_surface")
    return "PROCEED", rules


BASELINE_BY_LANE = {
    "vote_outcome": baseline_vote_outcome,
    "vote_state": baseline_vote_state,
    "default_vote": baseline_default_vote,
    "triage": baseline_triage,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", required=True)
    args = parser.parse_args(argv)
    root = artifact_path(args.artifact)
    baseline_root = root / "baseline"
    baseline_root.mkdir(parents=True, exist_ok=True)

    all_results: dict[str, dict[str, Any]] = {}
    rows: list[dict[str, Any]] = []
    for lane in LANES:
        labels = read_json(root / "labels" / f"{lane}_labels.json")
        lane_results: dict[str, Any] = {}
        for packet_path in sorted((root / "packets" / lane).glob("*.json")):
            packet = read_json(packet_path)
            label, rules = BASELINE_BY_LANE[lane](packet)
            expected = labels[packet["packet_id"]]["expected_label"]
            result = {
                "packet_id": packet["packet_id"],
                "event_id": packet["event_id"],
                "lane": lane,
                "predicted_label": label,
                "expected_label": expected,
                "aligned": label == expected,
                "triggered_rules": rules,
                "packet_hash": packet["packet_hash"],
            }
            result["result_hash"] = sha_json(result)
            lane_results[packet["packet_id"]] = result
            rows.append(result)
        all_results[lane] = lane_results

    write_json(baseline_root / "deterministic_baseline.json", all_results)
    with (baseline_root / "deterministic_baseline.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "packet_id",
                "event_id",
                "lane",
                "predicted_label",
                "expected_label",
                "aligned",
                "triggered_rules",
                "packet_hash",
                "result_hash",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        for row in rows:
            out = dict(row)
            out["triggered_rules"] = ",".join(row["triggered_rules"])
            writer.writerow(out)

    summary = {}
    for lane, lane_results in all_results.items():
        values = list(lane_results.values())
        summary[lane] = {
            "packet_count": len(values),
            "aligned_count": sum(1 for item in values if item["aligned"]),
            "alignment_rate": round(sum(1 for item in values if item["aligned"]) / len(values), 4) if values else 0,
        }
    write_json(baseline_root / "deterministic_baseline_summary.json", summary)
    write_sha256s(root)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
