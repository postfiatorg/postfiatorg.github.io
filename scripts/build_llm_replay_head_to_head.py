#!/usr/bin/env python3
"""Build a head-to-head evidence packet for LLM governance replay."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROUTE_SEVERITY = {
    "PROCEED": 0,
    "HOLD_FOR_CHALLENGE": 1,
    "DELAY_FOR_FIX": 2,
    "REJECT": 3,
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    packet = repo / "static/benchmarks/xrpl-amendment-governance-replay-20260601T204407Z"
    out = repo / "docs/evidence/llm-governance-replay-head-to-head-20260601T231200Z"
    out.mkdir(parents=True, exist_ok=True)

    source_files = {
        "summary": packet / "summary.json",
        "attention_cost_model": packet / "attention_cost_model.json",
        "deterministic_baseline": packet / "deterministic_baseline.json",
        "counterfactual": packet / "vote_replay_hash_counterfactual.csv",
        "packet_sha256s": packet / "SHA256SUMS.txt",
        "runtime_manifest": packet / "qwen_runtime_manifest.json",
    }
    summary = json.loads(source_files["summary"].read_text(encoding="utf-8"))
    cost = json.loads(source_files["attention_cost_model"].read_text(encoding="utf-8"))
    baseline = json.loads(source_files["deterministic_baseline"].read_text(encoding="utf-8"))
    rows: list[dict[str, str]] = []
    with source_files["counterfactual"].open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    comparison_rows: list[dict[str, object]] = []
    disagreements: list[dict[str, object]] = []
    qwen_wins: list[dict[str, object]] = []
    rule_wins: list[dict[str, object]] = []
    for row in rows:
        deterministic_route = row["deterministic_route"]
        qwen_route = row["qwen_replay_route"]
        historical_route = row["historical_route"]
        deterministic_severity = ROUTE_SEVERITY[deterministic_route]
        qwen_severity = ROUTE_SEVERITY[qwen_route]
        historical_severity = ROUTE_SEVERITY[historical_route]
        delta = qwen_severity - deterministic_severity
        out_row = {
            "packet_id": row["packet_id"],
            "amendment_or_event": row["amendment_or_event"],
            "historical_route": historical_route,
            "deterministic_route": deterministic_route,
            "qwen_replay_route": qwen_route,
            "replay_default_vote": row["replay_default_vote"],
            "deterministic_severity": deterministic_severity,
            "qwen_severity": qwen_severity,
            "historical_severity": historical_severity,
            "qwen_vs_rule_delta": delta,
            "same_route": str(deterministic_route == qwen_route).lower(),
            "same_historical_alignment": str(
                deterministic_route == historical_route and qwen_route == historical_route
            ).lower(),
            "unsafe_proceed": row["unsafe_proceed"],
        }
        comparison_rows.append(out_row)
        if deterministic_route != qwen_route:
            disagreements.append(out_row)
        if abs(qwen_severity - historical_severity) < abs(deterministic_severity - historical_severity):
            qwen_wins.append(out_row)
        elif abs(deterministic_severity - historical_severity) < abs(qwen_severity - historical_severity):
            rule_wins.append(out_row)

    deterministic_counts = Counter(row["deterministic_route"] for row in rows)
    qwen_counts = Counter(row["qwen_replay_route"] for row in rows)
    historical_counts = Counter(row["historical_route"] for row in rows)
    exact_sequence_match = [
        row["deterministic_route"] for row in rows
    ] == [row["qwen_replay_route"] for row in rows]
    cutoff_counts_identical = dict(deterministic_counts) == dict(qwen_counts)

    deterministic_hours = float(cost["deterministic_alert"]["hours"])
    qwen_hours = float(cost["qwen_replay_default"]["hours"])
    committee_hours = float(cost["standing_committee"]["hours"])
    attention_lift_vs_deterministic = 1.0 - qwen_hours / deterministic_hours
    attention_lift_vs_committee = 1.0 - qwen_hours / committee_hours

    source_hashes = {name: sha256(path) for name, path in source_files.items()}
    packet_root = sha256(source_files["packet_sha256s"])

    measurement = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source_packet": str(packet.relative_to(repo)),
        "source_packet_sha256s_sha256": packet_root,
        "source_hashes": source_hashes,
        "contested_method": "Qwen/Qwen3.6-27B-FP8 deterministic SGLang replay-default route",
        "simpler_baseline": baseline["rule_engine_version"],
        "input_corpus": {
            "packet_count": len(rows),
            "qwen_runs": int(summary["total_qwen_runs"]),
            "runs_per_packet": int(summary["runtime_manifest"]["runs_per_packet"]),
            "machine_receipt_sha256": summary["runtime_manifest"]["machine_receipt_sha256"],
        },
        "route_comparison": {
            "qwen_vs_rule_disagreement_count": len(disagreements),
            "qwen_vs_rule_disagreement_rate": len(disagreements) / max(1, len(rows)),
            "exact_ordinal_sequence_match": exact_sequence_match,
            "cutoff_distribution_match": cutoff_counts_identical,
            "historical_route_counts": dict(sorted(historical_counts.items())),
            "deterministic_route_counts": dict(sorted(deterministic_counts.items())),
            "qwen_route_counts": dict(sorted(qwen_counts.items())),
            "qwen_wins_vs_rule_count": len(qwen_wins),
            "rule_wins_vs_qwen_count": len(rule_wins),
            "unsafe_proceed_count": int(summary["unsafe_proceed_count"]),
        },
        "attention_comparison": {
            "standing_committee_hours": committee_hours,
            "deterministic_alert_hours": deterministic_hours,
            "qwen_replay_default_hours": qwen_hours,
            "attention_reduction_vs_deterministic_alert": round(attention_lift_vs_deterministic, 4),
            "attention_reduction_vs_standing_committee": round(attention_lift_vs_committee, 4),
        },
        "safe_sentence": (
            "On the 13-packet XRPL amendment replay corpus, Qwen added no route-choice "
            "lift over the deterministic rule floor (0/13 disagreements), while the "
            "replay-default process reduced modeled review hours by 81.03% versus a "
            "deterministic alert that every validator reviews."
        ),
        "claim_not_supported": (
            "This packet does not show that Qwen is more accurate or more discriminating "
            "than the deterministic rule engine on route choice."
        ),
    }

    comparison_path = out / "comparison.csv"
    with comparison_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(comparison_rows[0].keys()))
        writer.writeheader()
        writer.writerows(comparison_rows)

    write_json(out / "summary.json", measurement)
    write_json(
        out / "decision.json",
        {
            "decision": "MEASURED_PROCESS_LIFT_NO_ROUTE_LIFT",
            "safe_sentence": measurement["safe_sentence"],
            "claim_not_supported": measurement["claim_not_supported"],
        },
    )

    report = f"""# LLM Governance Replay Head-To-Head

Generated: {measurement['generated_at']}

## Question

Does the Qwen replay route beat a simpler deterministic rule floor on the same
13 XRPL amendment packets?

## Answer

No route-choice lift was measured. Qwen and the deterministic rule floor selected
the same route on all 13 packets.

The measured advantage in this packet is process cost, not route discrimination:
the replay-default workflow is modeled at {qwen_hours:.2f} review hours versus
{deterministic_hours:.2f} hours for a deterministic alert that every validator
reviews, a {attention_lift_vs_deterministic:.2%} reduction. Against a standing
committee model, the reduction is {attention_lift_vs_committee:.2%}.

## Inputs

- Source packet: `{measurement['source_packet']}`
- Source packet SHA256SUMS hash: `{packet_root}`
- Contested method: {measurement['contested_method']}
- Simpler baseline: `{measurement['simpler_baseline']}`
- Packets: {len(rows)}
- Qwen outputs: {summary['total_qwen_runs']}
- Runs per packet: {summary['runtime_manifest']['runs_per_packet']}
- Machine receipt SHA-256: `{summary['runtime_manifest']['machine_receipt_sha256']}`

## Measurements

| Measurement | Value |
|---|---:|
| Qwen-vs-rule disagreements | {len(disagreements)} / {len(rows)} |
| Qwen wins versus rule, judged by distance to historical label | {len(qwen_wins)} |
| Rule wins versus Qwen, judged by distance to historical label | {len(rule_wins)} |
| Exact ordinal route sequence match | {str(exact_sequence_match).lower()} |
| Route distribution match | {str(cutoff_counts_identical).lower()} |
| Unsafe `PROCEED` events | {summary['unsafe_proceed_count']} |
| Standing committee review hours | {committee_hours:.2f} |
| Deterministic alert review hours | {deterministic_hours:.2f} |
| Qwen replay-default review hours | {qwen_hours:.2f} |
| Attention reduction vs deterministic alert | {attention_lift_vs_deterministic:.2%} |
| Attention reduction vs standing committee | {attention_lift_vs_committee:.2%} |

## Route Distributions

| Route | Historical | Deterministic baseline | Qwen replay |
|---|---:|---:|---:|
"""
    for route in sorted(ROUTE_SEVERITY, key=ROUTE_SEVERITY.get):
        report += (
            f"| {route} | {historical_counts.get(route, 0)} | "
            f"{deterministic_counts.get(route, 0)} | {qwen_counts.get(route, 0)} |\n"
        )
    report += f"""
## Safe Integration Sentence

{measurement['safe_sentence']}

## Claim This Packet Does Not Support

{measurement['claim_not_supported']}

## Files

- `comparison.csv`: per-packet head-to-head comparison.
- `summary.json`: machine-readable metrics and source hashes.
- `decision.json`: integration decision and safe/unsafe claims.
- `SOURCE_HASHES.json`: hashes of the upstream packet files used.
- `COMMANDS.txt`: reproduction commands.
- `SHA256SUMS.txt`: hashes for this evidence packet.
"""
    (out / "REPORT.md").write_text(report, encoding="utf-8")
    write_json(out / "SOURCE_HASHES.json", source_hashes)
    (out / "COMMANDS.txt").write_text(
        "\n".join(
            [
                "python3 scripts/build_llm_replay_head_to_head.py",
                f"cd {out.relative_to(repo)} && sha256sum -c SHA256SUMS.txt",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    sums = []
    for path in sorted(out.iterdir()):
        if path.name == "SHA256SUMS.txt" or not path.is_file():
            continue
        sums.append(f"{sha256(path)}  {path.name}\n")
    (out / "SHA256SUMS.txt").write_text("".join(sums), encoding="utf-8")
    print(out.relative_to(repo))
    print(f"decision={json.loads((out / 'decision.json').read_text())['decision']}")
    print(f"safe_sentence={measurement['safe_sentence']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
