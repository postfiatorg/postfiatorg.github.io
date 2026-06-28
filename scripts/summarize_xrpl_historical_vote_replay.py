#!/usr/bin/env python3
"""Summarize historical-only XRPL seed-13 vote replay results."""

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
    labels_doc = json.loads((packet_dir / "historical_vote_labels.json").read_text(encoding="utf-8"))
    labels = labels_doc["labels"]
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
    aligned = 0
    yes_when_expected_no = 0
    no_when_expected_yes = 0
    qwen_vote_counts: Counter[str] = Counter()
    expected_vote_counts: Counter[str] = Counter()
    evidence_tier_counts: Counter[str] = Counter()
    label_basis_counts: Counter[str] = Counter()

    for packet_id, label in sorted(labels.items()):
        if label.get("historical_replay_eligible") is not True:
            raise ValueError(f"{packet_id} is not historical_replay_eligible=true")
        expected_vote = str(label["xrpl_vote_outcome"]).upper()
        if expected_vote not in VOTES:
            raise ValueError(f"{packet_id} has non-XRP vote label: {expected_vote}")

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
        is_aligned = qwen_vote == expected_vote
        aligned += int(is_aligned)
        yes_when_expected_no += int(qwen_vote == "YES" and expected_vote == "NO")
        no_when_expected_yes += int(qwen_vote == "NO" and expected_vote == "YES")
        qwen_vote_counts[qwen_vote] += 1
        expected_vote_counts[expected_vote] += 1
        evidence_tier_counts[str(label["evidence_tier"])] += 1
        label_basis_counts[str(label["label_basis"])] += 1
        first_run = runs[0].get("output_json", {}) if runs else {}
        flags = first_run.get("unscored_review_flags", {}) if isinstance(first_run, dict) else {}

        rows.append(
            {
                "packet_id": packet_id,
                "source_event_name": label["event_name"],
                "prompt_event_name": packet["amendment_or_event_name"],
                "xrpl_vote_outcome_held_out": expected_vote,
                "qwen_xrpl_vote_recommendation": qwen_vote,
                "aligned_with_historical_vote_outcome": str(is_aligned).lower(),
                "yes_when_expected_no": str(qwen_vote == "YES" and expected_vote == "NO").lower(),
                "no_when_expected_yes": str(qwen_vote == "NO" and expected_vote == "YES").lower(),
                "label_basis": label["label_basis"],
                "evidence_tier": label["evidence_tier"],
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

    csv_path = packet_dir / "historical_vote_replay.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    packet_count = len(labels)
    summary = {
        "generated_at": generated_at,
        "packet_count": packet_count,
        "total_qwen_runs": total_runs,
        "schema_valid_output_rate": round(schema_valid / total_runs, 4) if total_runs else 0,
        "endpoint_error_count": endpoint_errors,
        "fallback_used": bool(runtime_manifest.get("fallback_used")),
        "historical_vote_alignment_rate": round(aligned / packet_count, 4) if packet_count else 0,
        "yes_when_expected_no_count": yes_when_expected_no,
        "no_when_expected_yes_count": no_when_expected_yes,
        "exact_output_hash_converged_packets": exact_hash_converged,
        "parsed_vote_converged_packets": parsed_vote_converged,
        "expected_vote_counts": dict(sorted(expected_vote_counts.items())),
        "qwen_vote_counts": dict(sorted(qwen_vote_counts.items())),
        "evidence_tier_counts": dict(sorted(evidence_tier_counts.items())),
        "label_basis_counts": dict(sorted(label_basis_counts.items())),
        "scored_output_field": "xrpl_vote_recommendation",
        "allowed_scored_values": sorted(VOTES),
        "runtime_manifest": runtime_manifest,
        "eval_boundary": labels_doc["eval_boundary"],
        "selection_policy": labels_doc["selection_policy"],
        "interpretation_warning": (
            "This metric excludes open-for-voting source-default snapshots and ambiguous vote surfaces. "
            "It compares only XRP-native YES/NO outputs to historical vote outcomes."
        ),
    }
    write_json(packet_dir / "historical_vote_replay_summary.json", summary)
    write_json(packet_dir / "summary.json", summary)

    report_lines = [
        "# XRPL Historical Vote Replay Report",
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
        f"- Historical vote alignment rate: {summary['historical_vote_alignment_rate']}",
        f"- YES when held-out historical vote is NO: {yes_when_expected_no}",
        f"- NO when held-out historical vote is YES: {no_when_expected_yes}",
        f"- Runtime kind: {runtime_manifest.get('runtime_kind', 'missing')}",
        f"- Model: {runtime_manifest.get('model', 'missing')}",
        f"- Machine receipt: {runtime_manifest.get('machine_receipt_path', '')}",
        f"- Machine receipt SHA-256: {runtime_manifest.get('machine_receipt_sha256', '')}",
        "",
        "## Boundary",
        "",
        "This report is the only historical-alignment report for the split seed-13 packet.",
        "It excludes open-for-voting/default-vote snapshot rows and the ambiguous AMM post-launch row.",
        "Prompt packets exclude held-out vote outcomes, final/current source status, route labels, risk tags, raw source IDs, and raw URLs.",
        "Explicit validator advisories in source facts are retained because they are part of the public fact pattern validators saw.",
        "",
        "## Results",
        "",
        "| Event | Prompt Name | Held-Out Vote | Qwen Vote | Aligned | Basis | Evidence Tier |",
        "|---|---|---:|---:|---:|---|---:|",
    ]
    for row in rows:
        report_lines.append(
            f"| {row['source_event_name']} | {row['prompt_event_name']} | "
            f"{row['xrpl_vote_outcome_held_out']} | {row['qwen_xrpl_vote_recommendation']} | "
            f"{row['aligned_with_historical_vote_outcome']} | {row['label_basis']} | {row['evidence_tier']} |"
        )

    disagreements = [row for row in rows if row["aligned_with_historical_vote_outcome"] != "true"]
    report_lines.extend(["", "## Disagreements", ""])
    if disagreements:
        for row in disagreements:
            report_lines.append(
                f"- {row['source_event_name']}: held-out {row['xrpl_vote_outcome_held_out']}, "
                f"Qwen {row['qwen_xrpl_vote_recommendation']}."
            )
    else:
        report_lines.append("- None.")

    report_lines.extend(["", "## Basis Notes", ""])
    for row in rows:
        report_lines.append(f"- {row['source_event_name']}: {row['basis_note']}")
    (packet_dir / "REPORT.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    packet_root = write_sha256s(packet_dir)
    print(json.dumps({"packet": packet_dir.relative_to(REPO_ROOT).as_posix(), "packet_root": packet_root}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
