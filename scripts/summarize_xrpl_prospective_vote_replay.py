#!/usr/bin/env python3
"""Summarize prospective/open-vote XRPL seed-13 replay results."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
VOTES = {"YES", "NO"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_sha256s(packet_dir: Path) -> str:
    rows = []
    for path in sorted(packet_dir.rglob("*")):
        if not path.is_file() or path.name == "SHA256SUMS.txt":
            continue
        rows.append(f"{sha_file(path)}  {path.relative_to(packet_dir).as_posix()}\n")
    sums = "".join(rows)
    (packet_dir / "SHA256SUMS.txt").write_text(sums, encoding="utf-8")
    return hashlib.sha256(sums.encode("utf-8")).hexdigest()


def load_runs(packet_dir: Path, packet_id: str) -> list[dict[str, Any]]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((packet_dir / "qwen_runs" / packet_id).glob("run_*.json"))
    ]


def majority(values: list[str]) -> str:
    if not values:
        return "NOT_RUN"
    return Counter(values).most_common(1)[0][0]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    args = parser.parse_args(argv)

    packet_dir = args.packet.resolve()
    generated_at = utc_now()
    metadata_doc = json.loads((packet_dir / "prospective_vote_metadata.json").read_text(encoding="utf-8"))
    cases = metadata_doc["cases"]
    runtime_manifest = {}
    manifest_path = packet_dir / "qwen_runtime_manifest.json"
    if manifest_path.exists():
        runtime_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    rows: list[dict[str, Any]] = []
    total_runs = 0
    schema_valid = 0
    endpoint_errors = 0
    exact_hash_converged = 0
    parsed_vote_converged = 0
    default_vote_match = 0
    qwen_vote_counts: Counter[str] = Counter()
    source_default_vote_counts: Counter[str] = Counter()
    review_flag_counts: Counter[str] = Counter()

    for packet_id, meta in sorted(cases.items()):
        if meta.get("historical_replay_eligible") is not False:
            raise ValueError(f"{packet_id} should not be historical_replay_eligible=true")
        packet = json.loads((packet_dir / "amendment_packets" / f"{packet_id}.json").read_text(encoding="utf-8"))
        runs = load_runs(packet_dir, packet_id)
        total_runs += len(runs)
        schema_valid += sum(1 for run in runs if run.get("schema_valid"))
        endpoint_errors += sum(1 for run in runs if run.get("error"))
        output_hashes = [run.get("output_hash") for run in runs]
        votes = [
            str(run.get("output_json", {}).get("xrpl_vote_recommendation", "NOT_RUN")).upper()
            for run in runs
        ]
        if output_hashes and len(set(output_hashes)) == 1:
            exact_hash_converged += 1
        if votes and len(set(votes)) == 1:
            parsed_vote_converged += 1

        qwen_vote = majority(votes)
        source_default_vote = str(meta["source_reported_default_vote"]).upper()
        is_default_match = source_default_vote in VOTES and qwen_vote == source_default_vote
        default_vote_match += int(is_default_match)
        qwen_vote_counts[qwen_vote] += 1
        source_default_vote_counts[source_default_vote] += 1
        first_run = runs[0].get("output_json", {}) if runs else {}
        flags = first_run.get("unscored_review_flags", {}) if isinstance(first_run, dict) else {}
        for flag, value in sorted(flags.items()):
            review_flag_counts[flag] += int(bool(value))

        rows.append(
            {
                "packet_id": packet_id,
                "event_name": meta["event_name"],
                "qwen_xrpl_vote_recommendation": qwen_vote,
                "source_reported_default_vote": source_default_vote,
                "matches_source_default_vote_snapshot": str(is_default_match).lower(),
                "source_status_snapshot": meta["source_status"],
                "basis_note": meta["basis_note"],
                "needs_public_review_unscored": str(bool(flags.get("needs_public_review", False))).lower(),
                "bug_or_fix_sequence_unscored": str(bool(flags.get("bug_or_fix_sequence", False))).lower(),
                "asset_control_or_compliance_unscored": str(bool(flags.get("asset_control_or_compliance", False))).lower(),
                "source_default_vote_used_unscored": str(bool(flags.get("source_default_vote_used", False))).lower(),
                "exact_output_hash_converged": str(bool(output_hashes and len(set(output_hashes)) == 1)).lower(),
                "parsed_vote_converged": str(bool(votes and len(set(votes)) == 1)).lower(),
                "run_count": len(runs),
                "first_source_fact": packet["source_facts"][0]["quote_or_summary"],
            }
        )

    with (packet_dir / "prospective_vote_replay.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    packet_count = len(cases)
    summary = {
        "generated_at": generated_at,
        "packet_count": packet_count,
        "total_qwen_runs": total_runs,
        "schema_valid_output_rate": round(schema_valid / total_runs, 4) if total_runs else 0,
        "endpoint_error_count": endpoint_errors,
        "fallback_used": bool(runtime_manifest.get("fallback_used")),
        "exact_output_hash_converged_packets": exact_hash_converged,
        "parsed_vote_converged_packets": parsed_vote_converged,
        "qwen_vote_counts": dict(sorted(qwen_vote_counts.items())),
        "source_default_vote_counts": dict(sorted(source_default_vote_counts.items())),
        "source_default_vote_snapshot_match_count": default_vote_match,
        "source_default_vote_snapshot_match_rate": round(default_vote_match / packet_count, 4) if packet_count else 0,
        "review_flag_counts": dict(sorted(review_flag_counts.items())),
        "scored_output_field": "xrpl_vote_recommendation",
        "allowed_scored_values": sorted(VOTES),
        "runtime_manifest": runtime_manifest,
        "eval_boundary": metadata_doc["eval_boundary"],
        "interpretation_warning": (
            "This is not historical vote alignment. It summarizes recommendations for open-for-voting "
            "source snapshots and whether they match source-code default-vote metadata."
        ),
    }
    write_json(packet_dir / "prospective_vote_replay_summary.json", summary)
    write_json(packet_dir / "summary.json", summary)

    report_lines = [
        "# XRPL Prospective Open-Vote Replay Report",
        "",
        f"Generated: {generated_at}",
        "",
        "## Summary",
        "",
        f"- Packets: {packet_count}",
        f"- Qwen runs: {total_runs}",
        "- Scored output field: `xrpl_vote_recommendation`",
        "- Allowed scored values: `YES`, `NO`",
        f"- Schema-valid output rate: {summary['schema_valid_output_rate']}",
        f"- Endpoint errors: {endpoint_errors}",
        f"- Offline fallback used: {summary['fallback_used']}",
        f"- Exact-output-hash converged packets: {exact_hash_converged}",
        f"- Parsed-vote converged packets: {parsed_vote_converged}",
        f"- Source-default snapshot match rate: {summary['source_default_vote_snapshot_match_rate']}",
        f"- Runtime kind: {runtime_manifest.get('runtime_kind', 'missing')}",
        f"- Model: {runtime_manifest.get('model', 'missing')}",
        f"- Machine receipt: {runtime_manifest.get('machine_receipt_path', '')}",
        f"- Machine receipt SHA-256: {runtime_manifest.get('machine_receipt_sha256', '')}",
        "",
        "## Boundary",
        "",
        "These rows were open for voting in the source snapshot and are not historical labels.",
        "The source-default snapshot match rate is not historical alignment and should not be reported as such.",
        "Prompt packets may include `Open for Voting` source status because the task is prospective recommendation, not held-out replay.",
        "",
        "## Results",
        "",
        "| Event | Qwen Vote | Source Default Vote | Default Match | Source Status |",
        "|---|---:|---:|---:|---|",
    ]
    for row in rows:
        report_lines.append(
            f"| {row['event_name']} | {row['qwen_xrpl_vote_recommendation']} | "
            f"{row['source_reported_default_vote']} | {row['matches_source_default_vote_snapshot']} | "
            f"{row['source_status_snapshot']} |"
        )
    report_lines.extend(["", "## Basis Notes", ""])
    for row in rows:
        report_lines.append(f"- {row['event_name']}: {row['basis_note']}")
    (packet_dir / "REPORT.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    packet_root = write_sha256s(packet_dir)
    print(json.dumps({"packet": packet_dir.relative_to(REPO_ROOT).as_posix(), "packet_root": packet_root}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
