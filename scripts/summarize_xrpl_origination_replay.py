#!/usr/bin/env python3
"""Summarize XRPL origination replay outputs."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from xrpl_lifecycle_common import artifact_path, read_json, utc_now, write_json, write_sha256s


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def packet_lookup(root: Path) -> dict[str, dict[str, Any]]:
    out = {}
    for path in sorted((root / "packets").glob("*.json")) + sorted((root / "fork_packets").glob("*.json")):
        packet = read_json(path)
        out[packet["packet_id"]] = packet
    return out


def load_runs(root: Path) -> list[dict[str, Any]]:
    runs: list[dict[str, Any]] = []
    for path in sorted((root / "qwen_runs").glob("*/*/run_*.json")):
        run = read_json(path)
        run["_path"] = path.relative_to(root).as_posix()
        runs.append(run)
    return runs


def summarize(root: Path) -> dict[str, Any]:
    packets = packet_lookup(root)
    runs = load_runs(root)
    by_packet: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for run in runs:
        by_packet[run["packet_id"]].append(run)

    packet_rows: list[dict[str, Any]] = []
    for packet_id, packet in sorted(packets.items()):
        packet_runs = sorted(by_packet.get(packet_id, []), key=lambda run: run["run_index"])
        output_hashes = sorted({run.get("output_hash", "") for run in packet_runs})
        raw_hashes = sorted({run.get("raw_output_hash", "") for run in packet_runs})
        labels = sorted({run.get("parsed_label", "") for run in packet_runs})
        kind = "fork" if packet.get("fork_of") else "main"
        packet_rows.append(
            {
                "packet_id": packet_id,
                "packet_kind": kind,
                "xls_id": packet["amendment_identity"]["xls_id"],
                "title": packet["amendment_identity"]["title"],
                "xls_status": packet["amendment_identity"]["xls_status"],
                "mainnet_state": packet["known_status"]["mainnet_state"],
                "fork_of": packet.get("fork_of", ""),
                "fork_kind": packet.get("fork_kind", ""),
                "run_count": len(packet_runs),
                "schema_valid_count": sum(1 for run in packet_runs if run.get("schema_valid")),
                "error_count": sum(1 for run in packet_runs if run.get("error")),
                "citation_failure_count": sum(1 for run in packet_runs if not run.get("checks", {}).get("citation_valid")),
                "authority_failure_count": sum(
                    1 for run in packet_runs if run.get("checks", {}).get("authority_boundary_failures")
                ),
                "parsed_hash_count": len(output_hashes),
                "raw_hash_count": len(raw_hashes),
                "parsed_converged": len(packet_runs) > 0 and len(output_hashes) == 1,
                "raw_converged": len(packet_runs) > 0 and len(raw_hashes) == 1,
                "labels": ";".join(labels),
                "output_hashes": ";".join(output_hashes),
                "raw_output_hashes": ";".join(raw_hashes),
            }
        )

    main_rows = [row for row in packet_rows if row["packet_kind"] == "main"]
    fork_rows = [row for row in packet_rows if row["packet_kind"] == "fork"]
    fork_comparisons: list[dict[str, Any]] = []
    by_packet_row = {row["packet_id"]: row for row in packet_rows}
    for row in fork_rows:
        parent = by_packet_row.get(row["fork_of"])
        if not parent:
            continue
        fork_comparisons.append(
            {
                "fork_packet_id": row["packet_id"],
                "parent_packet_id": row["fork_of"],
                "fork_kind": row["fork_kind"],
                "parent_labels": parent["labels"],
                "fork_labels": row["labels"],
                "label_changed": parent["labels"] != row["labels"],
                "parent_output_hashes": parent["output_hashes"],
                "fork_output_hashes": row["output_hashes"],
                "output_hash_changed": parent["output_hashes"] != row["output_hashes"],
            }
        )

    run_rows = []
    for run in runs:
        packet = packets[run["packet_id"]]
        run_rows.append(
            {
                "packet_id": run["packet_id"],
                "packet_kind": run.get("packet_kind", ""),
                "xls_id": packet["amendment_identity"]["xls_id"],
                "run_index": run["run_index"],
                "schema_valid": run.get("schema_valid"),
                "parsed_label": run.get("parsed_label"),
                "output_hash": run.get("output_hash"),
                "raw_output_hash": run.get("raw_output_hash"),
                "citation_valid": run.get("checks", {}).get("citation_valid"),
                "authority_failures": ";".join(run.get("checks", {}).get("authority_boundary_failures", [])),
                "normalization_actions": ";".join(run.get("checks", {}).get("normalization_actions", [])),
                "path": run["_path"],
            }
        )

    summary = {
        "generated_at": utc_now(),
        "artifact": root.as_posix(),
        "packet_count": len([packet for packet in packets.values() if not packet.get("fork_of")]),
        "fork_packet_count": len([packet for packet in packets.values() if packet.get("fork_of")]),
        "run_count": len(runs),
        "main_run_count": sum(1 for run in runs if run.get("packet_kind") == "main"),
        "fork_run_count": sum(1 for run in runs if run.get("packet_kind") == "fork"),
        "schema_valid_count": sum(1 for run in runs if run.get("schema_valid")),
        "schema_invalid_count": sum(1 for run in runs if not run.get("schema_valid")),
        "error_count": sum(1 for run in runs if run.get("error")),
        "citation_failure_count": sum(1 for run in runs if not run.get("checks", {}).get("citation_valid")),
        "authority_failure_count": sum(1 for run in runs if run.get("checks", {}).get("authority_boundary_failures")),
        "main_packets_with_five_runs": sum(1 for row in main_rows if row["run_count"] == 5),
        "main_packets_parsed_converged": sum(1 for row in main_rows if row["parsed_converged"]),
        "main_packets_raw_converged": sum(1 for row in main_rows if row["raw_converged"]),
        "label_counts": Counter(run.get("parsed_label", "") for run in runs),
        "label_counts_main": Counter(run.get("parsed_label", "") for run in runs if run.get("packet_kind") == "main"),
        "packet_rows": packet_rows,
        "fork_comparisons": fork_comparisons,
    }
    write_json(root / "summaries" / "origination_replay_summary.json", summary)
    write_csv(root / "summaries" / "packet_convergence.csv", packet_rows)
    write_csv(root / "summaries" / "run_outputs.csv", run_rows)
    write_csv(root / "summaries" / "fork_comparisons.csv", fork_comparisons)
    with (root / "summaries" / "outputs.jsonl").open("w", encoding="utf-8") as fh:
        for run in runs:
            fh.write(json.dumps({k: v for k, v in run.items() if k != "raw_message_content"}, sort_keys=True) + "\n")

    report = [
        "# XRPL Origination Replay Summary",
        "",
        f"Generated: {summary['generated_at']}",
        "",
        "## Counts",
        "",
        f"- Main packets: {summary['packet_count']}",
        f"- Fork packets: {summary['fork_packet_count']}",
        f"- Runs: {summary['run_count']}",
        f"- Schema-valid runs: {summary['schema_valid_count']}/{summary['run_count']}",
        f"- Citation failures: {summary['citation_failure_count']}",
        f"- Authority-boundary failures: {summary['authority_failure_count']}",
        f"- Main packets with five runs: {summary['main_packets_with_five_runs']}/{summary['packet_count']}",
        f"- Main parsed-hash convergence: {summary['main_packets_parsed_converged']}/{summary['packet_count']}",
        f"- Main raw-hash convergence: {summary['main_packets_raw_converged']}/{summary['packet_count']}",
        f"- Main label counts: `{json.dumps(summary['label_counts_main'], sort_keys=True)}`",
        "",
        "## Fork Comparisons",
        "",
    ]
    for item in fork_comparisons:
        report.extend(
            [
                f"- `{item['fork_kind']}` on `{item['parent_packet_id']}`: "
                f"label_changed={item['label_changed']}, output_hash_changed={item['output_hash_changed']}",
            ]
        )
    report.extend(
        [
            "",
            "## Boundary",
            "",
            "These outputs are public work items for origination replay. They are not validator vote recommendations and do not decide whether an amendment should pass.",
            "",
            "## Files",
            "",
            "- `summaries/origination_replay_summary.json`",
            "- `summaries/packet_convergence.csv`",
            "- `summaries/run_outputs.csv`",
            "- `summaries/fork_comparisons.csv`",
            "- `summaries/outputs.jsonl`",
            "- `SHA256SUMS.txt`",
        ]
    )
    (root / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    write_sha256s(root)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", required=True)
    args = parser.parse_args(argv)
    summary = summarize(artifact_path(args.artifact))
    print(json.dumps({k: v for k, v in summary.items() if k not in {"packet_rows"}}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
