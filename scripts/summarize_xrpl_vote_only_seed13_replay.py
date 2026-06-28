#!/usr/bin/env python3
"""Summarize a vote-only blind XRPL seed-13 replay."""

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
    path.parent.mkdir(parents=True, exist_ok=True)
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
    labels_doc = json.loads((packet_dir / "vote_eval_labels.json").read_text(encoding="utf-8"))
    labels = labels_doc["labels"]
    runtime_manifest = {}
    manifest_path = packet_dir / "qwen_runtime_manifest.json"
    if manifest_path.exists():
        runtime_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    rows: list[dict[str, Any]] = []
    total_runs = 0
    schema_valid = 0
    exact_hash_converged = 0
    parsed_vote_converged = 0
    aligned = 0
    yes_when_expected_no = 0
    no_when_expected_yes = 0
    qwen_vote_counts: Counter[str] = Counter()
    expected_vote_counts: Counter[str] = Counter()
    comparison_basis_counts: Counter[str] = Counter()
    error_count = 0

    for packet_id, label in sorted(labels.items()):
        packet = json.loads((packet_dir / "amendment_packets" / f"{packet_id}.json").read_text(encoding="utf-8"))
        runs = load_runs(packet_dir, packet_id)
        total_runs += len(runs)
        schema_valid += sum(1 for run in runs if run.get("schema_valid"))
        error_count += sum(1 for run in runs if run.get("error"))
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
        expected_vote = label["xrpl_vote_outcome"]
        qwen_vote_counts[qwen_vote] += 1
        expected_vote_counts[expected_vote] += 1
        comparison_basis_counts[label["comparison_basis"]] += 1
        is_aligned = qwen_vote == expected_vote
        aligned += int(is_aligned)
        yes_when_expected_no += int(qwen_vote == "YES" and expected_vote == "NO")
        no_when_expected_yes += int(qwen_vote == "NO" and expected_vote == "YES")
        first_run = runs[0].get("output_json", {}) if runs else {}
        flags = first_run.get("unscored_review_flags", {}) if isinstance(first_run, dict) else {}
        rows.append(
            {
                "packet_id": packet_id,
                "event_name": packet["amendment_or_event_name"],
                "xrpl_vote_outcome_held_out": expected_vote,
                "qwen_xrpl_vote_recommendation": qwen_vote,
                "aligned_with_vote_outcome": str(is_aligned).lower(),
                "yes_when_expected_no": str(qwen_vote == "YES" and expected_vote == "NO").lower(),
                "no_when_expected_yes": str(qwen_vote == "NO" and expected_vote == "YES").lower(),
                "comparison_basis": label["comparison_basis"],
                "basis_note": label["basis_note"],
                "source_status_held_out": label["source_status_held_out"],
                "source_reported_default_vote": label["source_reported_default_vote"],
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

    with (packet_dir / "vote_only_replay.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    packet_count = len(labels)
    source_default_snapshot_rows = sum(
        1 for row in rows if row["comparison_basis"] == "source_default_vote_snapshot_open_for_voting"
    )
    summary = {
        "generated_at": generated_at,
        "packet_count": packet_count,
        "total_qwen_runs": total_runs,
        "schema_valid_output_rate": round(schema_valid / total_runs, 4) if total_runs else 0,
        "endpoint_error_count": error_count,
        "fallback_used": bool(runtime_manifest.get("fallback_used")),
        "vote_alignment_rate": round(aligned / packet_count, 4) if packet_count else 0,
        "yes_when_expected_no_count": yes_when_expected_no,
        "no_when_expected_yes_count": no_when_expected_yes,
        "exact_output_hash_converged_packets": exact_hash_converged,
        "parsed_vote_converged_packets": parsed_vote_converged,
        "expected_vote_counts": dict(sorted(expected_vote_counts.items())),
        "qwen_vote_counts": dict(sorted(qwen_vote_counts.items())),
        "comparison_basis_counts": dict(sorted(comparison_basis_counts.items())),
        "source_default_snapshot_rows": source_default_snapshot_rows,
        "scored_output_field": "xrpl_vote_recommendation",
        "allowed_scored_values": sorted(VOTES),
        "runtime_manifest": runtime_manifest,
        "eval_boundary": labels_doc["eval_boundary"],
        "selection_policy": labels_doc["selection_policy"],
        "interpretation_warning": (
            "Alignment compares only XRP-native YES/NO values. Rows with comparison_basis="
            "source_default_vote_snapshot_open_for_voting are not completed mainnet-history labels; "
            "they use the source default-vote snapshot because the source row was still open for voting."
        ),
    }
    write_json(packet_dir / "vote_replay_summary.json", summary)
    write_json(packet_dir / "summary.json", summary)

    report_lines = [
        "# XRPL Vote-Only Seed-13 Replay Report",
        "",
        f"Generated: {generated_at}",
        "",
        "## Summary",
        "",
        f"- Packets: {packet_count}",
        f"- Qwen runs: {total_runs}",
        f"- Scored output field: `xrpl_vote_recommendation`",
        "- Allowed scored values: `YES`, `NO`",
        f"- Schema-valid output rate: {summary['schema_valid_output_rate']}",
        f"- Endpoint errors: {error_count}",
        f"- Offline fallback used: {summary['fallback_used']}",
        f"- Exact-output-hash converged packets: {exact_hash_converged}",
        f"- Parsed-vote converged packets: {parsed_vote_converged}",
        f"- Vote alignment rate: {summary['vote_alignment_rate']}",
        f"- YES when held-out vote outcome is NO: {yes_when_expected_no}",
        f"- NO when held-out vote outcome is YES: {no_when_expected_yes}",
        f"- Source-default snapshot rows, not completed mainnet-history rows: {source_default_snapshot_rows}",
        f"- Runtime kind: {runtime_manifest.get('runtime_kind', 'missing')}",
        f"- Model: {runtime_manifest.get('model', 'missing')}",
        f"- Machine receipt: {runtime_manifest.get('machine_receipt_path', '')}",
        f"- Machine receipt SHA-256: {runtime_manifest.get('machine_receipt_sha256', '')}",
        "",
        "## Boundary",
        "",
        "This run removes `HOLD_FOR_CHALLENGE` from the scored comparison layer.",
        "Prompt packets exclude held-out vote outcomes and final/current source status when it would reveal the label.",
        "Prompt packets retain source-backed descriptions, source default votes, and explicit validator advisories.",
        "Unscored review flags are recorded but are not used for alignment.",
        "",
        "## Results",
        "",
        "| Event | Held-Out XRP Vote | Qwen XRP Vote | Aligned | Basis | Source Status Held Out | Source Default Vote |",
        "|---|---:|---:|---:|---|---:|---:|",
    ]
    for row in rows:
        report_lines.append(
            f"| {row['event_name']} | {row['xrpl_vote_outcome_held_out']} | "
            f"{row['qwen_xrpl_vote_recommendation']} | {row['aligned_with_vote_outcome']} | "
            f"{row['comparison_basis']} | {row['source_status_held_out']} | "
            f"{row['source_reported_default_vote']} |"
        )
    report_lines.extend(
        [
            "",
            "## Basis Notes",
            "",
        ]
    )
    for row in rows:
        report_lines.append(f"- {row['event_name']}: {row['basis_note']}")
    (packet_dir / "REPORT.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    packet_root = write_sha256s(packet_dir)
    print(json.dumps({"packet": packet_dir.relative_to(REPO_ROOT).as_posix(), "packet_root": packet_root}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
