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
RUN_ROOT = "replay-output/agentic-thematic-four-index-continuous-20260827"
WEIGHT_UNITS = 1_000_000_000_000

INDEX_SPECS = (
    (1, "generative-ai-compute-infrastructure", "01-generative-ai-compute-infrastructure"),
    (2, "energy-transition-grid-modernization", "02-energy-transition-grid-modernization"),
    (3, "critical-minerals-resource-nationalism", "03-critical-minerals-resource-nationalism"),
    (4, "defense-modernization-space-systems", "04-defense-modernization-space-systems"),
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
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def money_display(value: Any) -> str:
    return f"{Decimal(str(value)):,.2f}"


def decimal_display(value: Any, places: int) -> str:
    return f"{Decimal(str(value)):.{places}f}"


def raw_receipt(theme_dir: Path, side: str, cik: str) -> dict[str, Any]:
    packet = load(theme_dir / f"score-cache-h200-{side}" / f"{cik}.json")
    return dict(packet["receipt"])


def build_representative(
    *, theme_dir: Path, score_by_cik: dict[str, dict[str, Any]], cik: str
) -> dict[str, Any]:
    left = raw_receipt(theme_dir, "a", cik)
    right = raw_receipt(theme_dir, "b", cik)
    if left["request_sha256"] != right["request_sha256"]:
        raise ValueError(f"{theme_dir}: representative request changed")
    if left["content"].encode("utf-8") != right["content"].encode("utf-8"):
        raise ValueError(f"{theme_dir}: representative response changed")
    score = score_by_cik[cik]
    return {
        "cik": cik,
        "ticker": str(score["ticker"]),
        "transcript_available": bool(score["transcript_available"]),
        "transcript_sha256": score["transcript_sha256"],
        "request_sha256": str(left["request_sha256"]),
        "original_content_sha256": str(left["content_sha256"]),
        "replay_content_sha256": str(right["content_sha256"]),
        "byte_identical": True,
        "raw_model_output": str(left["content"]),
    }


def build_index(
    *, root: Path, position: int, slug: str, theme_id: str, proof_output_dir: Path
) -> dict[str, Any]:
    theme_dir = root / RUN_ROOT / theme_id
    rubric_packet = load(theme_dir / "rubric-h200-a.json")
    scores = load(theme_dir / "scores-h200-a.json")
    proof_path = theme_dir / "score-byte-comparison.json"
    proof = load(proof_path)
    outcome = load(theme_dir / "basket.json")
    if len(scores["scores"]) != 1_000:
        raise ValueError(f"{theme_dir}: score run is incomplete")
    proof_fields = (
        "comparison_count",
        "byte_identical_count",
        "parsed_identical_count",
        "attempt_trace_identical_count",
    )
    if any(int(proof[field]) != 1_000 for field in proof_fields):
        raise ValueError(f"{theme_dir}: replay proof is incomplete")
    if str(scores["rubric_sha256"]) != str(rubric_packet["rubric_sha256"]):
        raise ValueError(f"{theme_dir}: score run is not bound to the rubric")

    public_proof = proof_output_dir / f"agentic-index-replay-{slug}-byte-comparison.json"
    public_proof.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(proof_path, public_proof)
    score_by_cik = {str(row["cik"]): dict(row) for row in scores["scores"]}
    score_counts = Counter(int(row["score"]) for row in scores["scores"])
    transcript_count = sum(bool(row["transcript_available"]) for row in scores["scores"])
    common = {
        "position": position,
        "slug": slug,
        "basket_name": str(rubric_packet["rubric"]["basket_name"]),
        "basket_description": str(rubric_packet["rubric"]["basket_description"]),
        "rubric": rubric_packet["rubric"],
        "rubric_sha256": str(rubric_packet["rubric_sha256"]),
        "score_cutoff": 80,
        "score_distribution": {
            str(score): count for score, count in sorted(score_counts.items())
        },
        "transcript_coverage": {
            "available": transcript_count,
            "unavailable": 1_000 - transcript_count,
            "universe": 1_000,
        },
        "replay_proof": {
            "comparison_count": int(proof["comparison_count"]),
            "byte_identical_count": int(proof["byte_identical_count"]),
            "parsed_identical_count": int(proof["parsed_identical_count"]),
            "attempt_trace_identical_count": int(proof["attempt_trace_identical_count"]),
            "comparison_sha256": str(proof["comparison_sha256"]),
            "public_artifact": f"/benchmarks/{public_proof.name}",
            "public_artifact_sha256": file_sha256(public_proof),
        },
    }

    if outcome.get("status") == "rejected":
        qualifiers = [
            {
                **dict(row),
                "reasoning_confidence": int(score_by_cik[str(row["cik"])]["reasoning_confidence"]),
                "classification_verdict": str(score_by_cik[str(row["cik"])]["classification_verdict"]),
                "reasoning_block": list(score_by_cik[str(row["cik"])]["reasoning_block"]),
            }
            for row in outcome["qualifying_scores"]
        ]
        representative_cik = str(qualifiers[0]["cik"])
        return {
            **common,
            "status": "rejected",
            "constituent_count": 0,
            "constituents": [],
            "rejection": {
                "reason": str(outcome["reason"]),
                "qualifying_score_count": int(outcome["qualifying_score_count"]),
                "minimum_constituents_required_by_cap": int(
                    outcome["minimum_constituents_required_by_cap"]
                ),
                "holding_cap": str(outcome["holding_cap"]),
                "qualifying_scores": qualifiers,
                "rejection_sha256": str(outcome["rejection_sha256"]),
            },
            "representative_replay": build_representative(
                theme_dir=theme_dir,
                score_by_cik=score_by_cik,
                cik=representative_cik,
            ),
            "bindings": dict(outcome["bindings"]),
        }

    if sum(int(row["weight_units"]) for row in outcome["constituents"]) != WEIGHT_UNITS:
        raise ValueError(f"{theme_dir}: weights do not sum to {WEIGHT_UNITS}")
    if int(outcome["methodology"]["minimum_score"]) != 80:
        raise ValueError(f"{theme_dir}: expected score floor 80")
    if str(outcome["methodology"]["holding_cap"]) != "0.20":
        raise ValueError(f"{theme_dir}: expected holding cap 0.20")

    ranked = sorted(
        outcome["constituents"],
        key=lambda row: (-int(row["weight_units"]), str(row["cik"])),
    )
    constituents = []
    for rank, row in enumerate(ranked, start=1):
        constituents.append(
            {
                "rank": rank,
                "cik": str(row["cik"]),
                "ticker": str(row["ticker"]),
                "company_name": str(row["company_name"]),
                "qwen_score": int(row["score"]),
                "qwen_confidence": int(row["reasoning_confidence"]),
                "classification_verdict": str(row["classification_verdict"]),
                "counter_case": str(row["counter_case"]),
                "prior_vs_transcript_assessment": str(row["prior_vs_transcript_assessment"]),
                "qwen_reasoning_block": list(row["reasoning_block"]),
                "transcript": {
                    "available": bool(row["transcript_available"]),
                    "provider": row["transcript_provider"],
                    "fiscal_year": row["transcript_fiscal_year"],
                    "fiscal_quarter": row["transcript_fiscal_quarter"],
                    "sha256": row["transcript_sha256"],
                },
                "profitability_factor": str(row["profitability_factor"]),
                "weight": str(row["weight"]),
                "weight_percent": f"{int(row['weight_units']) / 10_000_000_000:.6f}",
                "cap_bound": bool(row["cap_bound"]),
                "weight_inputs": {
                    "market_cap_display": money_display(row["market_cap_usd"]),
                    "market_cap_root_display": money_display(row["market_cap_root"]),
                    "selected_profitability_display": money_display(row["selected_profitability"]),
                    "profitability_z_score": decimal_display(row["profitability_z_score"], 6),
                    "profitability_multiplier": decimal_display(row["profitability_multiplier"], 8),
                    "fundamental_scale_display": money_display(row["fundamental_scale"]),
                    "factor_strength": decimal_display(row["factor_strength"], 6),
                    "factor_share_percent": decimal_display(
                        Decimal(row["factor_share"]) * 100, 6
                    ),
                    "fundamental_share_percent": decimal_display(
                        Decimal(row["fundamental_share"]) * 100, 6
                    ),
                    "pre_cap_weight_percent": decimal_display(
                        Decimal(row["pre_cap_weight_decimal"]) * 100, 6
                    ),
                    "normalized_weight_units": int(row["weight_units"]),
                },
            }
        )
    representative_cik = str(ranked[0]["cik"])
    return {
        **common,
        "status": "accepted",
        "constituent_count": int(outcome["constituent_count"]),
        "cap_bound_count": int(outcome["cap_bound_count"]),
        "constituents": constituents,
        "representative_replay": build_representative(
            theme_dir=theme_dir,
            score_by_cik=score_by_cik,
            cik=representative_cik,
        ),
        "methodology": dict(outcome["methodology"]),
        "bindings": {
            **dict(outcome["bindings"]),
            "methodology_sha256": str(outcome["methodology_sha256"]),
            "final_weights_sha256": str(outcome["final_weights_sha256"]),
            "basket_sha256": str(outcome["basket_sha256"]),
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
    catalog_path = index_root / "replay-output/sec-qwen15-accounting-hybrid-suite-v1/canonical-qwen-15-baskets.json"
    catalog = load(catalog_path)
    if len(catalog["baskets"]) != 15:
        raise ValueError("the frozen thematic catalog must contain exactly 15 baskets")
    proof_output_dir = args.output.resolve().parent
    indexes = [
        build_index(
            root=index_root,
            position=position,
            slug=slug,
            theme_id=theme_id,
            proof_output_dir=proof_output_dir,
        )
        for position, slug, theme_id in INDEX_SPECS
    ]
    model_profile = load(
        index_root / RUN_ROOT / INDEX_SPECS[0][2] / "rubric-h200-a.json"
    )["model_profile"]
    stable = {
        "schema": "postfiat.agentic-index-live-samples.v2",
        "as_of": "2026-08-27T00:00:00Z",
        "claim_boundary": (
            "These artifacts prove byte-exact replay and deterministic mechanical outcomes "
            "for the listed frozen inputs. They do not prove investment merit, source truth, "
            "model-training provenance, custody, execution quality, or future performance."
        ),
        "catalog": {
            "basket_count": 15,
            "source_sha256": file_sha256(catalog_path),
            "baskets": catalog["baskets"],
        },
        "model_profile": model_profile,
        "suite": {
            "factor_runs": 4,
            "accepted_indexes": sum(index["status"] == "accepted" for index in indexes),
            "rejected_indexes": sum(index["status"] == "rejected" for index in indexes),
            "score_cutoff": 80,
            "holding_cap": "0.20",
            "methodology_sha256": "44003ac5be8cc881882676d7298389e19794f3204398f2bc31ac2225a1884a7b",
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
                "accepted": stable["suite"]["accepted_indexes"],
                "rejected": stable["suite"]["rejected_indexes"],
                "replay_comparisons": sum(
                    index["replay_proof"]["comparison_count"] for index in indexes
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
