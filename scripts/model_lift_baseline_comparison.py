#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


DEFAULT_SNAPSHOT = Path("/home/postfiat/repos/dynamic-unl-scoring/data/testnet_snapshot.json")
DEFAULT_RUN_DIR = Path(
    "/home/postfiat/repos/dynamic-unl-scoring/phase0/results/modal/"
    "qwen36-27b-fp8/2026-04-30_qwen36-27b-fp8_scoring-v2"
)
DEFAULT_PROMPT = Path("/home/postfiat/repos/dynamic-unl-scoring/prompts/scoring_v2.txt")
DEFAULT_OUTPUT_ROOT = Path("static/benchmarks")
DEFAULT_CUTOFF = 40
DEFAULT_MAX_SIZE = 20
BASELINE_WEIGHTS = {
    "consensus": 0.42,
    "reliability": 0.20,
    "software": 0.15,
    "diversity": 0.13,
    "identity": 0.10,
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def pct(value: Any) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def clamp(value: float, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, int(round(value))))


def threshold_consensus(weighted: float | None) -> int:
    if weighted is None or weighted <= 0:
        return 0
    if weighted >= 0.9995:
        return 100
    if weighted >= 0.999:
        return 98
    if weighted >= 0.995:
        return 92
    if weighted >= 0.99:
        return 82
    if weighted >= 0.98:
        return 70
    if weighted >= 0.97:
        return 60
    if weighted >= 0.95:
        return 45
    if weighted >= 0.90:
        return 25
    return 10


def common_version(validators: list[dict[str, Any]]) -> str:
    versions = [str(v.get("server_version") or "") for v in validators if v.get("server_version")]
    return Counter(versions).most_common(1)[0][0] if versions else ""


def field_counts(validators: list[dict[str, Any]], field_path: tuple[str, ...]) -> Counter:
    counter: Counter = Counter()
    for validator in validators:
        value: Any = validator
        for field in field_path:
            value = value.get(field) if isinstance(value, dict) else None
        if value not in (None, ""):
            counter[str(value)] += 1
    return counter


def deterministic_score(
    validator: dict[str, Any],
    *,
    common_server_version: str,
    country_counts: Counter,
    asn_counts: Counter,
) -> dict[str, Any]:
    one_h = pct(validator.get("agreement_1h_score"))
    day = pct(validator.get("agreement_24h_score"))
    month = pct(validator.get("agreement_30d_score"))
    present = [v for v in (one_h, day, month) if v is not None]
    weighted = None
    if present:
        weighted = (
            (one_h if one_h is not None else mean(present)) * 0.10
            + (day if day is not None else mean(present)) * 0.25
            + (month if month is not None else mean(present)) * 0.65
        )
    consensus = threshold_consensus(weighted)

    reliability = 50
    if validator.get("domain_verified") is True:
        reliability += 25
    elif validator.get("domain"):
        reliability += 15
    if validator.get("unl"):
        reliability += 15
    reliability = clamp(reliability)

    version = str(validator.get("server_version") or "")
    if not version:
        software = 30
    elif version == common_server_version:
        software = 100
    else:
        software = 70
    base_fee = validator.get("base_fee")
    if base_fee not in (None, 10):
        software -= 10
    software = clamp(software)

    country = str(((validator.get("geolocation") or {}).get("country")) or "")
    asn = str(((validator.get("asn") or {}).get("asn")) or "")
    if not country or not asn:
        diversity = 20
    else:
        diversity = 45
        if country_counts[country] == 1:
            diversity += 25
        elif country_counts[country] <= 3:
            diversity += 12
        if asn_counts[asn] == 1:
            diversity += 25
        elif asn_counts[asn] <= 3:
            diversity += 12
    diversity = clamp(diversity)

    identity_obj = validator.get("identity") or {}
    if identity_obj.get("verified") is True:
        identity = 85
    elif validator.get("domain_verified") is True:
        identity = 70
    elif validator.get("domain"):
        identity = 60
    else:
        identity = 50

    overall = clamp(sum(
        score * BASELINE_WEIGHTS[name]
        for name, score in {
            "consensus": consensus,
            "reliability": reliability,
            "software": software,
            "diversity": diversity,
            "identity": identity,
        }.items()
    ))
    return {
        "score": overall,
        "consensus": consensus,
        "reliability": reliability,
        "software": software,
        "diversity": diversity,
        "identity": identity,
        "rule_inputs": {
            "weighted_agreement": round(weighted, 6) if weighted is not None else None,
            "common_server_version": common_server_version,
            "country": country or None,
            "asn": asn or None,
            "country_count": country_counts[country] if country else None,
            "asn_count": asn_counts[asn] if asn else None,
        },
    }


def rank_rows(rows: list[dict[str, Any]], score_key: str) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda row: (-int(row[score_key]), str(row["master_key"])))


def select(rows: list[dict[str, Any]], score_key: str, cutoff: int, max_size: int) -> list[str]:
    return [
        row["master_key"]
        for row in rank_rows([r for r in rows if int(r[score_key]) >= cutoff], score_key)[:max_size]
    ]


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2 or len(xs) != len(ys):
        return None
    xbar = mean(xs)
    ybar = mean(ys)
    numerator = sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys))
    xden = math.sqrt(sum((x - xbar) ** 2 for x in xs))
    yden = math.sqrt(sum((y - ybar) ** 2 for y in ys))
    if not xden or not yden:
        return None
    return numerator / (xden * yden)


def ranks(values: dict[str, float]) -> dict[str, int]:
    ordered = sorted(values.items(), key=lambda item: (-item[1], item[0]))
    return {key: idx + 1 for idx, (key, _) in enumerate(ordered)}


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare saved model validator scores against a deterministic rule baseline.")
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--prompt", type=Path, default=DEFAULT_PROMPT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--label", default=None)
    parser.add_argument("--cutoff", type=int, default=DEFAULT_CUTOFF)
    parser.add_argument("--max-size", type=int, default=DEFAULT_MAX_SIZE)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    generated_at = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    label = args.label or f"model-lift-baseline-{generated_at}"
    out_dir = args.output_root / label
    source_dir = out_dir / "source"
    out_dir.mkdir(parents=True, exist_ok=False)
    source_dir.mkdir()

    snapshot = load_json(args.snapshot)
    validators = list(snapshot["validators"])
    run_paths = sorted(args.run_dir.glob("run_*.json"))
    if not validators or not run_paths:
        raise SystemExit("missing validators or model run files")

    runs = [load_json(path) for path in run_paths]
    id_map = runs[0]["validator_id_map"]
    by_master = {validator["master_key"]: validator for validator in validators}

    model_by_master: dict[str, list[dict[str, Any]]] = {master: [] for master in by_master}
    for run in runs:
        if run["validator_id_map"] != id_map:
            raise SystemExit("validator_id_map changed across runs")
        if not run.get("complete_result"):
            raise SystemExit(f"incomplete model result: run {run.get('run')}")
        for validator_id, master_key in id_map.items():
            model_by_master[master_key].append(run["scores_by_validator_id"][validator_id])

    common_server_version = common_version(validators)
    country_counts = field_counts(validators, ("geolocation", "country"))
    asn_counts = field_counts(validators, ("asn", "asn"))

    rows: list[dict[str, Any]] = []
    model_scores_json: dict[str, Any] = {}
    baseline_scores_json: dict[str, Any] = {}
    for validator_id, master_key in id_map.items():
        validator = by_master[master_key]
        model_scores = model_by_master[master_key]
        unique_model_score_hashes = sorted({canonical_hash(score) for score in model_scores})
        first_model = model_scores[0]
        baseline = deterministic_score(
            validator,
            common_server_version=common_server_version,
            country_counts=country_counts,
            asn_counts=asn_counts,
        )
        row = {
            "validator_id": validator_id,
            "master_key": master_key,
            "domain": validator.get("domain") or "",
            "model_score": int(first_model["score"]),
            "baseline_score": int(baseline["score"]),
            "score_delta_model_minus_baseline": int(first_model["score"]) - int(baseline["score"]),
            "model_consensus": int(first_model["consensus"]),
            "baseline_consensus": int(baseline["consensus"]),
            "model_reliability": int(first_model["reliability"]),
            "baseline_reliability": int(baseline["reliability"]),
            "model_software": int(first_model["software"]),
            "baseline_software": int(baseline["software"]),
            "model_diversity": int(first_model["diversity"]),
            "baseline_diversity": int(baseline["diversity"]),
            "model_identity": int(first_model["identity"]),
            "baseline_identity": int(baseline["identity"]),
            "model_reasoning": first_model.get("reasoning", ""),
            "agreement_1h_score": validator.get("agreement_1h_score"),
            "agreement_24h_score": validator.get("agreement_24h_score"),
            "agreement_30d_score": validator.get("agreement_30d_score"),
            "domain_verified": validator.get("domain_verified"),
            "unl": validator.get("unl"),
            "server_version": validator.get("server_version"),
            "country": ((validator.get("geolocation") or {}).get("country")) or "",
            "asn": ((validator.get("asn") or {}).get("asn")) or "",
            "model_output_identical_across_runs": len(unique_model_score_hashes) == 1,
        }
        rows.append(row)
        model_scores_json[master_key] = {
            "validator_id": validator_id,
            "scores": model_scores,
            "unique_score_object_hashes": unique_model_score_hashes,
        }
        baseline_scores_json[master_key] = {"validator_id": validator_id, **baseline}

    model_selected = select(rows, "model_score", args.cutoff, args.max_size)
    baseline_selected = select(rows, "baseline_score", args.cutoff, args.max_size)
    model_set = set(model_selected)
    baseline_set = set(baseline_selected)
    model_rank = ranks({row["master_key"]: row["model_score"] for row in rows})
    baseline_rank = ranks({row["master_key"]: row["baseline_score"] for row in rows})
    comparison_rows: list[dict[str, Any]] = []
    for row in rows:
        master = row["master_key"]
        comparison_rows.append(
            {
                **row,
                "model_rank": model_rank[master],
                "baseline_rank": baseline_rank[master],
                "rank_delta_model_minus_baseline": model_rank[master] - baseline_rank[master],
                "selected_by_model": master in model_set,
                "selected_by_baseline": master in baseline_set,
                "selection_disagreement": (master in model_set) != (master in baseline_set),
            }
        )

    score_pairs = [(float(row["model_score"]), float(row["baseline_score"])) for row in rows]
    rank_pairs = [(float(model_rank[row["master_key"]]), float(baseline_rank[row["master_key"]])) for row in rows]
    abs_diffs = [abs(a - b) for a, b in score_pairs]
    disagreements = [row for row in comparison_rows if row["selection_disagreement"]]
    largest_deltas = sorted(comparison_rows, key=lambda row: abs(int(row["score_delta_model_minus_baseline"])), reverse=True)[:10]

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "claim_boundary": "Comparator audit only. No ground-truth labels are invented and no accuracy claim is made.",
        "deterministic_baseline_boundary": (
            "The deterministic baseline is an operator-authored heuristic comparator "
            "derived from the scoring_v2 dimensions. The prompt explicitly leaves the "
            "overall score to model judgment, so these numeric weights are disclosed "
            "comparison rules, not protocol truth or hidden labels."
        ),
        "deterministic_baseline_weights": BASELINE_WEIGHTS,
        "source_snapshot": str(args.snapshot),
        "source_prompt": str(args.prompt),
        "source_model_run_dir": str(args.run_dir),
        "validator_count": len(rows),
        "model_run_count": len(run_paths),
        "all_model_score_objects_identical_across_runs": all(row["model_output_identical_across_runs"] for row in rows),
        "cutoff": args.cutoff,
        "max_size": args.max_size,
        "top_k_overlap": len(model_set & baseline_set),
        "top_k_jaccard": round(len(model_set & baseline_set) / len(model_set | baseline_set), 4) if model_set | baseline_set else None,
        "model_only_selected_count": len(model_set - baseline_set),
        "baseline_only_selected_count": len(baseline_set - model_set),
        "pearson_score_correlation": round(pearson([p[0] for p in score_pairs], [p[1] for p in score_pairs]) or 0, 4),
        "spearman_rank_correlation": round(pearson([p[0] for p in rank_pairs], [p[1] for p in rank_pairs]) or 0, 4),
        "mean_absolute_score_delta": round(mean(abs_diffs), 2),
        "max_absolute_score_delta": max(abs_diffs),
        "selection_disagreements": [
            {
                "validator_id": row["validator_id"],
                "master_key": row["master_key"],
                "domain": row["domain"],
                "model_score": row["model_score"],
                "baseline_score": row["baseline_score"],
                "model_rank": row["model_rank"],
                "baseline_rank": row["baseline_rank"],
                "selected_by_model": row["selected_by_model"],
                "selected_by_baseline": row["selected_by_baseline"],
                "model_reasoning": row["model_reasoning"],
            }
            for row in disagreements
        ],
        "largest_score_deltas": [
            {
                "validator_id": row["validator_id"],
                "master_key": row["master_key"],
                "domain": row["domain"],
                "model_score": row["model_score"],
                "baseline_score": row["baseline_score"],
                "delta": row["score_delta_model_minus_baseline"],
                "model_reasoning": row["model_reasoning"],
            }
            for row in largest_deltas
        ],
    }

    shutil.copy2(args.snapshot, source_dir / args.snapshot.name)
    if args.prompt.exists():
        shutil.copy2(args.prompt, source_dir / args.prompt.name)
    for path in run_paths:
        shutil.copy2(path, source_dir / path.name)

    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "model_scores.json").write_text(json.dumps(model_scores_json, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "deterministic_baseline_scores.json").write_text(json.dumps(baseline_scores_json, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(out_dir / "comparison.csv", comparison_rows)

    report = [
        "# Model-Lift Baseline Comparison",
        "",
        "This packet compares saved Qwen3.6 scoring_v2 outputs against a deterministic rule baseline over the same frozen PFT testnet snapshot.",
        "",
        "## Boundary",
        "",
        "This is a comparator audit, not an accuracy benchmark. It invents no ground-truth labels. The deterministic baseline is an operator-authored heuristic derived from the public scoring_v2 dimensions. The prompt explicitly says the overall score is model judgment rather than a mechanical average, so the numeric baseline weights below are disclosed comparison rules, not protocol truth or hidden labels.",
        "",
        "## Inputs",
        "",
        f"- Snapshot: `{args.snapshot}`",
        f"- Scoring prompt: `{args.prompt}`",
        f"- Model run directory: `{args.run_dir}`",
        f"- Validators: {len(rows)}",
        f"- Model runs: {len(run_paths)}",
        f"- Cutoff/max size: {args.cutoff}/{args.max_size}",
        f"- Baseline weights: {json.dumps(BASELINE_WEIGHTS, sort_keys=True)}",
        "",
        "## Results",
        "",
        f"- Model outputs identical across all saved runs: {summary['all_model_score_objects_identical_across_runs']}",
        f"- Top-{args.max_size} overlap: {summary['top_k_overlap']}/{args.max_size}",
        f"- Top-k Jaccard: {summary['top_k_jaccard']}",
        f"- Model-only selections: {summary['model_only_selected_count']}",
        f"- Baseline-only selections: {summary['baseline_only_selected_count']}",
        f"- Pearson score correlation: {summary['pearson_score_correlation']}",
        f"- Spearman rank correlation: {summary['spearman_rank_correlation']}",
        f"- Mean absolute score delta: {summary['mean_absolute_score_delta']}",
        "",
        "## Selection Disagreements",
        "",
    ]
    if disagreements:
        report.append("| Validator | Domain | Model | Baseline | Model rank | Baseline rank | Direction |")
        report.append("|---|---|---:|---:|---:|---:|---|")
        for row in disagreements:
            direction = "model-only" if row["selected_by_model"] else "baseline-only"
            report.append(
                f"| `{row['validator_id']}` | {row['domain'] or '-'} | {row['model_score']} | {row['baseline_score']} | "
                f"{row['model_rank']} | {row['baseline_rank']} | {direction} |"
            )
    else:
        report.append("No selection disagreements at the configured cutoff/max-size.")
    report.extend(
        [
            "",
            "## Integration Note",
            "",
            "A defensible whitepaper sentence from this packet is limited to: the project ran a deterministic-rule comparator over the same frozen scoring_v2 snapshot and recorded overlap/disagreement metrics. It should not be phrased as proof that the model is correct or that the comparator is ground truth.",
        ]
    )
    (out_dir / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    sha_lines = []
    for path in sorted(p for p in out_dir.rglob("*") if p.is_file() and p.name != "SHA256SUMS.txt"):
        sha_lines.append(f"{sha256_file(path)}  {path.relative_to(out_dir).as_posix()}")
    (out_dir / "SHA256SUMS.txt").write_text("\n".join(sha_lines) + "\n", encoding="utf-8")

    print(f"artifact_dir={out_dir}")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
