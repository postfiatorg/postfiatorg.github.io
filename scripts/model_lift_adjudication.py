#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


DEFAULT_INPUT = Path("static/benchmarks/model-lift-baseline-20260601T154824Z")
DEFAULT_OUTPUT_ROOT = Path("static/benchmarks")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def as_float(value: str) -> float | None:
    if value == "":
        return None
    return float(value)


def as_bool(value: str) -> bool:
    return value.lower() == "true"


def allowed_reasoning_only(reasoning: str) -> bool:
    text = reasoning.lower()
    allowed_tokens = [
        "agreement",
        "consensus",
        "domain",
        "identity",
        "diversity",
        "geolocation",
        "asn",
        "country",
        "software",
        "version",
        "unl",
        "missed",
        "ledger",
        "trust",
    ]
    disallowed_tokens = [
        "operator independence",
        "entity continuity",
        "reputation outside",
        "known operator",
        "legal",
        "corporate",
        "ownership",
    ]
    if any(token in text for token in disallowed_tokens):
        return False
    return any(token in text for token in allowed_tokens)


def adjudicate(row: dict[str, str]) -> dict[str, Any]:
    model_only = as_bool(row["selected_by_model"]) and not as_bool(row["selected_by_baseline"])
    baseline_only = as_bool(row["selected_by_baseline"]) and not as_bool(row["selected_by_model"])
    agreement_30d = as_float(row["agreement_30d_score"])
    domain = row["domain"]
    verified = as_bool(row["domain_verified"]) if row["domain_verified"] else False
    country = row["country"]
    asn = row["asn"]

    if model_only:
        direction = "model-only"
        evidence_edge = "model emphasizes stronger long-window consensus despite missing public-domain accountability"
        model_supported_by_prompt_priority = True
        baseline_supported_by_prompt_priority = False
    elif baseline_only:
        direction = "baseline-only"
        evidence_edge = "deterministic baseline rewards public-domain accountability despite weaker long-window consensus"
        model_supported_by_prompt_priority = False
        baseline_supported_by_prompt_priority = True
    else:
        direction = "none"
        evidence_edge = "not a boundary disagreement"
        model_supported_by_prompt_priority = False
        baseline_supported_by_prompt_priority = False

    if country or asn:
        concentration_status = "partially adjudicable"
    else:
        concentration_status = "undecidable: snapshot has no country/asn for this validator"

    if domain:
        accountability_status = "adjudicable: domain present" + (" and verified" if verified else " but unverified")
    else:
        accountability_status = "adjudicable: no domain accountability in snapshot"

    if agreement_30d is None:
        consensus_status = "undecidable: no 30d agreement score"
    elif agreement_30d >= 0.995:
        consensus_status = "adjudicable: strong 30d consensus"
    elif agreement_30d >= 0.99:
        consensus_status = "adjudicable: acceptable but weaker 30d consensus"
    else:
        consensus_status = "adjudicable: weak 30d consensus"

    return {
        "validator_id": row["validator_id"],
        "master_key": row["master_key"],
        "direction": direction,
        "domain": domain or "-",
        "domain_verified": verified,
        "agreement_30d_score": row["agreement_30d_score"],
        "model_score": row["model_score"],
        "baseline_score": row["baseline_score"],
        "model_rank": row["model_rank"],
        "baseline_rank": row["baseline_rank"],
        "model_reasoning_allowed_fields_only": allowed_reasoning_only(row["model_reasoning"]),
        "primary_disagreement": evidence_edge,
        "consensus_status": consensus_status,
        "accountability_status": accountability_status,
        "concentration_status": concentration_status,
        "operator_independence_status": "undecidable: no operator/entity continuity fields in snapshot",
        "adjudication_class": "policy_tradeoff_from_existing_fields",
        "lift_verdict": "not_proven_without_external_label_or_policy_choice",
        "model_supported_by_prompt_priority": model_supported_by_prompt_priority,
        "baseline_supported_by_prompt_priority": baseline_supported_by_prompt_priority,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Adjudicate model/rule boundary disagreements without inventing labels.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--label", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    label = args.label or f"model-lift-adjudication-{timestamp}"
    out_dir = args.output_root / label
    out_dir.mkdir(parents=True, exist_ok=False)

    summary = read_json(args.input / "summary.json")
    comparison = read_csv(args.input / "comparison.csv")
    disagreements = [row for row in comparison if row["selection_disagreement"].lower() == "true"]
    adjudicated = [adjudicate(row) for row in disagreements]

    model_only = [row for row in adjudicated if row["direction"] == "model-only"]
    baseline_only = [row for row in adjudicated if row["direction"] == "baseline-only"]
    agreement_model_only = [float(row["agreement_30d_score"]) for row in model_only if row["agreement_30d_score"]]
    agreement_baseline_only = [float(row["agreement_30d_score"]) for row in baseline_only if row["agreement_30d_score"]]

    aggregate = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "claim_boundary": "Adjudication from existing snapshot fields only. No ground-truth labels or human committee labels are invented.",
        "source_packet": str(args.input),
        "source_packet_summary_sha256": sha256_file(args.input / "summary.json"),
        "source_packet_comparison_sha256": sha256_file(args.input / "comparison.csv"),
        "disagreement_count": len(adjudicated),
        "model_only_count": len(model_only),
        "baseline_only_count": len(baseline_only),
        "all_model_reasoning_used_allowed_fields": all(row["model_reasoning_allowed_fields_only"] for row in adjudicated),
        "model_only_avg_30d_agreement": round(mean(agreement_model_only), 6) if agreement_model_only else None,
        "baseline_only_avg_30d_agreement": round(mean(agreement_baseline_only), 6) if agreement_baseline_only else None,
        "model_advantage_proven_count": 0,
        "baseline_advantage_proven_count": 0,
        "policy_tradeoff_count": len(adjudicated),
        "undecidable_operator_independence_count": len(adjudicated),
        "main_result": (
            "The prior benchmark exposed repeatable boundary disagreement, but the existing snapshot does not prove "
            "model superiority. The disagreements reduce to a policy tradeoff: the model gives more weight to stronger "
            "30-day consensus among no-domain validators, while the deterministic baseline gives more weight to public "
            "domain accountability. Operator independence, entity continuity, and concentration lift are undecidable from "
            "these rows because country/asn/operator fields are absent for all 10 disagreements."
        ),
    }

    rubric = """# Adjudication Rubric

This packet adjudicates only what is visible in the prior model-lift benchmark
packet. It does not invent ground-truth labels, committee labels, operator
identities, or off-snapshot facts.

Categories:

- `model-only`: selected by the model top-20 set and not by the deterministic
  baseline top-20 set.
- `baseline-only`: selected by the deterministic baseline top-20 set and not by
  the model top-20 set.
- `policy_tradeoff_from_existing_fields`: the disagreement is explainable by
  different weighting of fields already present in the snapshot.
- `not_proven_without_external_label_or_policy_choice`: existing evidence shows
  divergence but does not establish which side is correct.

Allowed evidence:

- 1h, 24h, and 30d agreement scores.
- domain presence and domain verification.
- UNL status.
- server version and base fee.
- country/asn/geolocation when present.
- identity status when present.
- model reasoning text from the saved scoring output.

Forbidden evidence:

- inferred operator identity,
- inferred entity continuity,
- inferred legal or reputational facts,
- human committee preference,
- later manual labels.
"""

    write_csv(out_dir / "adjudication.csv", adjudicated)
    (out_dir / "adjudication_summary.json").write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "RUBRIC.md").write_text(rubric, encoding="utf-8")
    command_text = (
        "python3 scripts/model_lift_adjudication.py "
        f"--input {args.input} --label {label}\n"
        f"sha256sum -c {out_dir / 'SHA256SUMS.txt'}\n"
    )
    (out_dir / "COMMANDS.txt").write_text(command_text, encoding="utf-8")

    report_lines = [
        "# Model-Lift Boundary Adjudication",
        "",
        "This packet adjudicates the 10 boundary disagreements from the prior model-lift comparator without inventing labels.",
        "",
        "## Boundary",
        "",
        aggregate["claim_boundary"],
        "",
        "## Inputs",
        "",
        f"- Source packet: `{args.input}`",
        f"- Source summary SHA-256: `{aggregate['source_packet_summary_sha256']}`",
        f"- Source comparison SHA-256: `{aggregate['source_packet_comparison_sha256']}`",
        f"- Prior top-20 overlap: {summary.get('top_k_overlap')}/{summary.get('max_size')}",
        f"- Prior Jaccard: {summary.get('top_k_jaccard')}",
        "",
        "## Result",
        "",
        f"- Boundary disagreements adjudicated: {aggregate['disagreement_count']}",
        f"- Model-only cases: {aggregate['model_only_count']}",
        f"- Baseline-only cases: {aggregate['baseline_only_count']}",
        f"- Model reasoning used only allowed saved fields: {aggregate['all_model_reasoning_used_allowed_fields']}",
        f"- Model-only average 30d agreement: {aggregate['model_only_avg_30d_agreement']}",
        f"- Baseline-only average 30d agreement: {aggregate['baseline_only_avg_30d_agreement']}",
        f"- Proven model advantage from existing rows: {aggregate['model_advantage_proven_count']}",
        f"- Proven baseline advantage from existing rows: {aggregate['baseline_advantage_proven_count']}",
        f"- Policy-tradeoff cases: {aggregate['policy_tradeoff_count']}",
        "",
        "The prior benchmark exposed repeatable boundary disagreement, not model superiority. Existing fields show a clean tradeoff: model-only selections have stronger 30-day consensus and no domain accountability, while baseline-only selections have domain accountability and weaker long-window consensus. Operator independence, entity continuity, and concentration lift are undecidable from these rows because all 10 disagreement rows lack country/asn/operator-continuity fields.",
        "",
        "## Disagreement Table",
        "",
        "| Validator | Direction | Domain | 30d agreement | Model | Baseline | Adjudication |",
        "|---|---|---|---:|---:|---:|---|",
    ]
    for row in adjudicated:
        report_lines.append(
            f"| `{row['validator_id']}` | {row['direction']} | {row['domain']} | {row['agreement_30d_score']} | "
            f"{row['model_score']} | {row['baseline_score']} | {row['lift_verdict']} |"
        )
    report_lines.extend(
        [
            "",
            "## Whitepaper-Safe Claim",
            "",
            "A defensible claim from this packet is limited to: the model-lift benchmark produced repeatable, auditable boundary disagreements, and adjudication shows those disagreements are policy tradeoffs under the current snapshot rather than proven model lift. The packet strengthens the case for auditable disagreement review and richer evidence schemas; it does not prove model superiority.",
        ]
    )
    (out_dir / "REPORT.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    sha_lines = []
    for path in sorted(p for p in out_dir.rglob("*") if p.is_file() and p.name != "SHA256SUMS.txt"):
        sha_lines.append(f"{sha256_file(path)}  {path.relative_to(out_dir).as_posix()}")
    (out_dir / "SHA256SUMS.txt").write_text("\n".join(sha_lines) + "\n", encoding="utf-8")

    print(f"artifact_dir={out_dir}")
    print(json.dumps(aggregate, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
