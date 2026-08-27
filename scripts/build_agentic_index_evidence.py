#!/usr/bin/env python3
"""Build the public evidence packet used by the agentic-indexing article."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from collections import Counter
from decimal import Decimal
from pathlib import Path
from typing import Any


SITE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INDEX_ROOT = SITE_ROOT.parent / "navstrategies-sec-index-replay"
WEIGHT_UNITS = 1_000_000_000_000

INDEX_SPECS = (
    {
        "position": 1,
        "slug": "generative-ai-compute-infrastructure",
        "score_dir": "replay-output/sec-qwen15-accounting-hybrid-suite-v1/scores/01-generative-ai-compute-infrastructure",
        "basket": "replay-output/sec-accounting-hybrid-ai-score75-repaired-v3/basket.json",
    },
    {
        "position": 2,
        "slug": "energy-transition-grid-modernization",
        "score_dir": "replay-output/sec-transcript-supplemented-energy-transition-v2",
        "basket": "replay-output/sec-accounting-hybrid-energy-transition-score75-repaired-v3/basket.json",
    },
    {
        "position": 3,
        "slug": "critical-minerals-resource-nationalism",
        "score_dir": "replay-output/sec-qwen15-accounting-hybrid-suite-v1/scores/03-critical-minerals-resource-nationalism",
        "basket": "replay-output/sec-accounting-hybrid-critical-minerals-score75-repaired-v3/basket.json",
    },
    {
        "position": 4,
        "slug": "defense-modernization-space-systems",
        "score_dir": "replay-output/sec-qwen15-accounting-hybrid-suite-v1/scores/04-defense-modernization-space-systems",
        "basket": "replay-output/sec-accounting-hybrid-defense-score75-repaired-v1/basket.json",
    },
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def money_display(value: Any) -> str:
    return f"{Decimal(str(value)):,.2f}"


def decimal_display(value: Any, places: int) -> str:
    return f"{Decimal(str(value)):.{places}f}"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return value


def receipt_for(score_dir: Path, cik: str, labels: tuple[str, str]) -> dict[str, Any]:
    matches: list[dict[str, Any]] = []
    for label in labels:
        packet = load(score_dir / label)
        matches.extend(
            dict(row) for row in packet["request_receipts"] if str(row["cik"]) == cik
        )
    if len(matches) != 1:
        raise ValueError(f"{score_dir}: expected one receipt for CIK {cik}, found {len(matches)}")
    return matches[0]


def build_index(
    *, root: Path, spec: dict[str, Any], proof_output_dir: Path
) -> dict[str, Any]:
    score_dir = root / spec["score_dir"]
    basket_path = root / spec["basket"]
    score_run = load(score_dir / "merged-scores.json")
    proof_path = score_dir / "byte-comparison.json"
    proof = load(proof_path)
    basket = load(basket_path)

    if len(score_run["scores"]) != 1_000:
        raise ValueError(f"{score_dir}: score run is not a 1,000-company run")
    if (
        proof["comparison_count"] != 1_000
        or proof["byte_identical_count"] != 1_000
        or proof["parsed_identical_count"] != 1_000
    ):
        raise ValueError(f"{score_dir}: replay proof is incomplete")
    if sum(int(row["weight_units"]) for row in basket["constituents"]) != WEIGHT_UNITS:
        raise ValueError(f"{basket_path}: weights do not sum to {WEIGHT_UNITS}")
    if basket["methodology"]["minimum_qwen_score"] != 75:
        raise ValueError(f"{basket_path}: expected the score-75 methodology")

    theme = score_run["theme"]
    ranked = sorted(
        basket["constituents"],
        key=lambda row: (-int(row["weight_units"]), str(row["cik"])),
    )
    score_by_cik = {str(row["cik"]): row for row in score_run["scores"]}
    if basket["score_run_sha256"] != score_run["run_sha256"]:
        raise ValueError(f"{basket_path}: basket is not bound to the score run")
    if basket["score_vector_sha256"] != score_run["score_vector_sha256"]:
        raise ValueError(f"{basket_path}: basket is not bound to the score vector")

    top = ranked[0]
    cik = str(top["cik"])
    original = receipt_for(
        score_dir,
        cik,
        ("h200-a-original.json", "h200-b-original.json"),
    )
    replay = receipt_for(
        score_dir,
        cik,
        ("h200-a-replay.json", "h200-b-replay.json"),
    )
    if original["request_sha256"] != replay["request_sha256"]:
        raise ValueError(f"{score_dir}: representative request changed")
    if original["content"].encode("utf-8") != replay["content"].encode("utf-8"):
        raise ValueError(f"{score_dir}: representative response is not byte-identical")

    public_proof = proof_output_dir / f"agentic-index-replay-{spec['slug']}-byte-comparison.json"
    public_proof.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(proof_path, public_proof)

    score_counts = Counter(int(row["score"]) for row in score_run["scores"])
    transcript_count = sum(bool(row["transcript_available"]) for row in score_run["scores"])
    constituents = []
    for rank, row in enumerate(ranked, start=1):
        constituent_cik = str(row["cik"])
        score_row = score_by_cik[constituent_cik]
        reasoning = [str(paragraph) for paragraph in row["qwen_reasoning_block"]]
        if reasoning != [str(paragraph) for paragraph in score_row["reasoning_block"]]:
            raise ValueError(f"{basket_path}: reasoning mismatch for CIK {constituent_cik}")
        if int(row["qwen_score"]) != int(score_row["score"]):
            raise ValueError(f"{basket_path}: score mismatch for CIK {constituent_cik}")
        constituents.append(
            {
                "rank": rank,
                "cik": constituent_cik,
                "ticker": str(row["ticker"]),
                "company_name": str(row["company_name"]),
                "qwen_score": int(row["qwen_score"]),
                "qwen_confidence": int(row["qwen_confidence"]),
                "qwen_reasoning_block": reasoning,
                "transcript": {
                    "available": bool(score_row["transcript_available"]),
                    "provider": score_row["transcript_provider"],
                    "fiscal_year": score_row["transcript_fiscal_year"],
                    "fiscal_quarter": score_row["transcript_fiscal_quarter"],
                    "sha256": score_row["transcript_sha256"],
                },
                "accounting_regime": str(row["accounting_regime"]),
                "profitability_factor": str(row["profitability_factor"]),
                "weight": str(row["weight"]),
                "weight_percent": f"{int(row['weight_units']) / 10_000_000_000:.6f}",
                "weight_inputs": {
                    "ttm_revenue_display": money_display(row["ttm_revenue"]),
                    "selected_profitability_display": money_display(row["selected_profitability"]),
                    "profitability_z_score": decimal_display(row["profitability_z_score"], 6),
                    "profitability_multiplier": decimal_display(row["profitability_multiplier"], 8),
                    "adjusted_scale_display": money_display(row["adjusted_scale"]),
                    "score_multiplier": decimal_display(
                        Decimal(int(row["qwen_score"])) / Decimal(100), 2
                    ),
                    "raw_weight_display": money_display(row["raw_weight_decimal"]),
                    "normalized_weight_units": int(row["weight_units"]),
                },
            }
        )
    representative_score = score_by_cik[cik]
    return {
        "position": int(spec["position"]),
        "slug": str(spec["slug"]),
        "basket_name": str(theme["basket_name"]),
        "basket_description": str(theme["basket_description"]),
        "scoring_heuristic": dict(theme["scoring_heuristic"]),
        "constituent_count": int(basket["constituent_count"]),
        "score_cutoff": 75,
        "score_distribution": {
            str(score): score_counts.get(score, 0) for score in (0, 25, 50, 75, 100)
        },
        "transcript_coverage": {
            "available": transcript_count,
            "unavailable": 1_000 - transcript_count,
            "universe": 1_000,
        },
        "constituents": constituents,
        "replay_proof": {
            "comparison_count": int(proof["comparison_count"]),
            "byte_identical_count": int(proof["byte_identical_count"]),
            "parsed_identical_count": int(proof["parsed_identical_count"]),
            "comparison_sha256": str(proof["comparison_sha256"]),
            "public_artifact": f"/benchmarks/{public_proof.name}",
            "public_artifact_sha256": file_sha256(public_proof),
        },
        "representative_replay": {
            "cik": cik,
            "ticker": str(top["ticker"]),
            "company_name": str(top["company_name"]),
            "transcript_available": bool(representative_score["transcript_available"]),
            "transcript_sha256": representative_score["transcript_sha256"],
            "request_sha256": str(original["request_sha256"]),
            "original_content_sha256": str(original["content_sha256"]),
            "replay_content_sha256": str(replay["content_sha256"]),
            "byte_identical": True,
            "raw_model_output": str(original["content"]),
        },
        "bindings": {
            "universe_manifest_sha256": str(basket["universe_manifest_sha256"]),
            "theme_sha256": str(score_run["theme_sha256"]),
            "model_profile_sha256": str(score_run["model_profile_sha256"]),
            "score_run_sha256": str(score_run["run_sha256"]),
            "score_vector_sha256": str(score_run["score_vector_sha256"]),
            "accounting_run_sha256": str(basket["accounting_run_sha256"]),
            "accounting_ruleset_sha256": str(basket["accounting_ruleset_sha256"]),
            "fcf_run_sha256": str(basket["fcf_run_sha256"]),
            "net_income_run_sha256": str(basket["net_income_run_sha256"]),
            "methodology_sha256": str(basket["methodology_sha256"]),
            "final_weights_sha256": str(basket["final_weights_sha256"]),
            "basket_sha256": str(basket["basket_sha256"]),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index-root", type=Path, default=DEFAULT_INDEX_ROOT)
    parser.add_argument(
        "--output",
        type=Path,
        default=SITE_ROOT / "static/benchmarks/agentic-index-live-samples-20260827.json",
    )
    args = parser.parse_args()

    index_root = args.index_root.resolve()
    catalog_path = (
        index_root
        / "replay-output/sec-qwen15-accounting-hybrid-suite-v1/canonical-qwen-15-baskets.json"
    )
    catalog = load(catalog_path)
    if len(catalog["baskets"]) != 15:
        raise ValueError("the frozen thematic catalog must contain exactly 15 baskets")

    proof_output_dir = args.output.resolve().parent
    indexes = [
        build_index(root=index_root, spec=spec, proof_output_dir=proof_output_dir)
        for spec in INDEX_SPECS
    ]
    model_profile = load(
        index_root / INDEX_SPECS[0]["score_dir"] / "merged-scores.json"
    )["model_profile"]
    stable = {
        "schema": "postfiat.agentic-index-live-samples.v1",
        "as_of": "2026-08-27T00:00:00Z",
        "claim_boundary": (
            "These artifacts prove byte-exact replay and deterministic mechanical weighting "
            "for the listed frozen inputs. They do not prove investment merit, source truth, "
            "model-training provenance, custody, execution quality, or future performance."
        ),
        "catalog": {
            "basket_count": 15,
            "source_sha256": file_sha256(catalog_path),
            "baskets": catalog["baskets"],
        },
        "model_profile": model_profile,
        "fundamental_backtest": {
            "source_commit": "d4d6b4f13d4725e637e2b17fe8e859815f7d5486",
            "source_report": (
                "https://github.com/postfiatorg/navstrategies/blob/"
                "d4d6b4f13d4725e637e2b17fe8e859815f7d5486/research/pre_catalyst/"
                "data_exploration/sec_10q_size_proxy/open_sec_fundamental_index_research_report.md"
            ),
            "period": "1998-03-17 through 2026-08-24",
            "observations": 7_154,
            "candidate": {
                "cagr_percent": "10.92",
                "return_to_volatility": "0.644",
                "volatility_percent": "18.91",
                "maximum_drawdown_percent": "-55.05",
                "correlation_to_spy": "0.949",
            },
            "spy": {
                "cagr_percent": "8.98",
                "return_to_volatility": "0.542",
                "volatility_percent": "19.37",
                "maximum_drawdown_percent": "-55.20",
            },
            "uncertainty": {
                "candidate_minus_spy_annualized_mean_percent": "1.68",
                "newey_west_t_statistic": "1.59",
                "confidence_interval_95_percent": ["-0.40", "3.76"],
                "five_factor_intercept_annualized_percent": "0.64",
                "five_factor_intercept_t_statistic": "0.91",
            },
            "frozen_rule": {
                "selection_count": 500,
                "retention_rank": 750,
                "rebalance_cutoffs": ["March 16", "May 15", "August 14", "November 14"],
                "adjusted_scale": "TTM revenue * exp(0.03 * selected profitability population z-score)",
                "operating_company_profitability": "TTM free cash flow",
                "financial_and_utility_profitability": "TTM net income",
                "holding_cap": None,
                "winsorization": None,
            },
        },
        "indexes": indexes,
    }
    payload = {**stable, "evidence_sha256": canonical_sha256(stable)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_bytes(payload) + b"\n")
    print(
        json.dumps(
            {
                "output": str(args.output.resolve()),
                "evidence_sha256": payload["evidence_sha256"],
                "index_count": len(indexes),
                "replay_comparisons": sum(
                    index["replay_proof"]["comparison_count"] for index in indexes
                ),
                "byte_identical": sum(
                    index["replay_proof"]["byte_identical_count"] for index in indexes
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
