#!/usr/bin/env python3
"""Validate XRPL origination replay packets and optional Qwen outputs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from build_xrpl_origination_replay_packets import ALLOWED_LABELS, NON_FINAL_STATUSES, packet_hash
from xrpl_lifecycle_common import artifact_path, read_json, sha_json, write_json


REQUIRED_NON_CLAIMS = {
    "This is not a validator vote recommendation.",
    "This does not decide whether the amendment should pass.",
}

FORBIDDEN_AUTHORITY_PATTERNS = [
    re.compile(r"\bvalidators?\s+should\s+vote\b", re.I),
    re.compile(r"\bvote\s+(yes|no)\b", re.I),
    re.compile(r"\b(?:the\s+)?(?:amendment|proposal|xls-\d{4})\s+(?:should|must)\s+be\s+(adopted|enabled|passed)\b", re.I),
    re.compile(r"\b(?:should|must)\s+be\s+(adopted|enabled|passed)\b(?!\s+before\b)", re.I),
    re.compile(r"\bthe\s+model\s+decides\b", re.I),
]


def json_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def packet_errors(path: Path, packet: dict[str, Any], *, expect_fork: bool) -> list[str]:
    errors: list[str] = []
    if packet.get("packet_hash") != packet_hash(packet):
        errors.append(f"{path}: packet_hash mismatch")
    if packet.get("allowed_output_labels") != ALLOWED_LABELS:
        errors.append(f"{path}: allowed_output_labels mismatch")
    for field in [
        "packet_id",
        "schema_version",
        "decision_question",
        "amendment_identity",
        "known_status",
        "source_list",
        "source_facts",
        "missing_evidence",
        "omission_log",
        "packet_hash",
    ]:
        if field not in packet:
            errors.append(f"{path}: missing {field}")
    source_ids = [source.get("source_id") for source in packet.get("source_list", [])]
    if len(source_ids) != len(set(source_ids)):
        errors.append(f"{path}: duplicate source_id in source_list")
    fact_ids = [fact.get("source_id") for fact in packet.get("source_facts", [])]
    missing_fact_sources = sorted(set(fact_ids) - set(source_ids))
    if missing_fact_sources:
        errors.append(f"{path}: source_facts cite missing source ids {missing_fact_sources}")
    xls_status = str(packet.get("amendment_identity", {}).get("xls_status", "")).upper()
    if not expect_fork and xls_status not in NON_FINAL_STATUSES:
        errors.append(f"{path}: main packet is not non-final, got {xls_status}")
    if expect_fork:
        if not packet.get("fork_of"):
            errors.append(f"{path}: fork packet missing fork_of")
        if not packet.get("fork_kind"):
            errors.append(f"{path}: fork packet missing fork_kind")
    return errors


def output_errors(run_path: Path, run: dict[str, Any], packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    output = run.get("output_json") or {}
    if run.get("output_hash") != sha_json(output):
        errors.append(f"{run_path}: output_hash mismatch")
    label = str(output.get("work_item_label", "")).strip().upper()
    if label not in ALLOWED_LABELS:
        errors.append(f"{run_path}: invalid work_item_label {label!r}")
    source_ids = {source.get("source_id") for source in packet.get("source_list", [])}
    citations = output.get("source_citations")
    if not isinstance(citations, list) or not citations:
        errors.append(f"{run_path}: source_citations missing or empty")
    else:
        bad = sorted({str(item) for item in citations if str(item) not in source_ids})
        if bad:
            errors.append(f"{run_path}: citations reference missing source ids {bad}")
    non_claims = {str(item) for item in output.get("non_claims", []) if isinstance(item, str)}
    missing = sorted(REQUIRED_NON_CLAIMS - non_claims)
    if missing:
        errors.append(f"{run_path}: missing required non_claims {missing}")
    text = json_text(output)
    for pattern in FORBIDDEN_AUTHORITY_PATTERNS:
        if pattern.search(text):
            errors.append(f"{run_path}: authority-boundary failure pattern {pattern.pattern}")
    return errors


def validate_artifact(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    packet_paths = sorted((root / "packets").glob("*.json"))
    fork_paths = sorted((root / "fork_packets").glob("*.json"))
    if len(packet_paths) != 27:
        errors.append(f"expected 27 main packets, found {len(packet_paths)}")
    if len(fork_paths) != 3:
        errors.append(f"expected 3 fork packets, found {len(fork_paths)}")
    packets: dict[str, dict[str, Any]] = {}
    for path in packet_paths:
        packet = read_json(path)
        packets[packet.get("packet_id", path.stem)] = packet
        errors.extend(packet_errors(path, packet, expect_fork=False))
    for path in fork_paths:
        packet = read_json(path)
        packets[packet.get("packet_id", path.stem)] = packet
        errors.extend(packet_errors(path, packet, expect_fork=True))
        parent = packet.get("fork_of")
        if parent not in packets:
            errors.append(f"{path}: fork parent {parent!r} not found")
        elif packet.get("packet_hash") == packets[parent].get("packet_hash"):
            errors.append(f"{path}: fork hash did not change from parent")

    run_errors = 0
    run_count = 0
    for run_path in sorted((root / "qwen_runs").glob("*/*/run_*.json")):
        run_count += 1
        run = read_json(run_path)
        packet_id = run.get("packet_id")
        packet = packets.get(packet_id)
        if not packet:
            errors.append(f"{run_path}: packet {packet_id!r} not found")
            run_errors += 1
            continue
        errs = output_errors(run_path, run, packet)
        run_errors += len(errs)
        errors.extend(errs)

    report = {
        "artifact": root.as_posix(),
        "valid": not errors,
        "packet_count": len(packet_paths),
        "fork_packet_count": len(fork_paths),
        "run_count": run_count,
        "run_error_count": run_errors,
        "error_count": len(errors),
        "errors": errors[:200],
    }
    write_json(root / "validation_report.json", report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", required=True)
    args = parser.parse_args(argv)
    report = validate_artifact(artifact_path(args.artifact))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
