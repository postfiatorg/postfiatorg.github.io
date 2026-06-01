#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import hashlib
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_SOURCE_ROOT = Path("/home/postfiat/repos/postfiatl1v2")
DEFAULT_OUTPUT_ROOT = Path("static/benchmarks")

SOURCE_FILES = {
    "llm_redteam_readme": "docs/governance/ai_governance_llm_redteam/README.md",
    "live_benchmark_readme": "docs/governance/ai_governance_live_benchmark/README.md",
    "llm_generation_summary": "reports/ai-governance-llm-redteam/generate/20260530T132633Z/summary.json",
    "llm_generated_packets": "reports/ai-governance-llm-redteam/generate/20260530T132633Z/packets.json",
    "llm_exact_selector_baseline": "reports/ai-governance-llm-redteam/rubric/20260530T132656Z/rubric_outputs.json",
    "llm_residual_fail_score": "reports/ai-governance-llm-redteam/score/20260530T133006Z/summary.json",
    "llm_residual_pass_score": "reports/ai-governance-llm-redteam/score/20260530T134334Z/summary.json",
    "llm_residual_pass_score_md": "reports/ai-governance-llm-redteam/score/20260530T134334Z/summary.md",
    "llm_qwen_run_summary": (
        "reports/ai-governance-llm-redteam/qwen/"
        "20260530T134103Z-vast-h200-38568893-llm-redteam-output-contract/summary.json"
    ),
    "live_hardened_score": "reports/ai-governance-live-benchmark-hardened/score/20260530T134707Z/summary.json",
    "live_hardened_score_md": "reports/ai-governance-live-benchmark-hardened/score/20260530T134707Z/summary.md",
    "live_hardened_qwen_run_summary": (
        "reports/ai-governance-live-benchmark-hardened/qwen/"
        "20260530T134334Z-vast-h200-38568893-live-output-contract/summary.json"
    ),
    "redteam_comparison": "reports/ai-governance-redteam/20260530T033500Z/summary.json",
    "redteam_comparison_md": "reports/ai-governance-redteam/20260530T033500Z/summary.md",
    "cross_machine_matrix": "reports/ai-governance-live-benchmark/matrix/20260530T010142Z/matrix_report.json",
    "live_packet_corpus": "docs/governance/ai_governance_live_benchmark/packets.json",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def fraction_numerator(value: str) -> int:
    return int(str(value).split("/", 1)[0])


def fraction_denominator(value: str) -> int:
    return int(str(value).split("/", 1)[1])


def count_exact_selector_live_admits(rubric: Mapping[str, Any]) -> dict[str, int]:
    outputs = list(rubric["outputs"])
    admits = [row for row in outputs if row.get("route") == "admit"]
    positive_admits = [row for row in admits if row.get("positive_live_effect") is True]
    expected_challenges = [row for row in outputs if row.get("committee_route") == "hold-for-challenge"]
    return {
        "packet_count": len(outputs),
        "admit_count": len(admits),
        "positive_live_admit_count": len(positive_admits),
        "expected_challenge_count": len(expected_challenges),
    }


def path_totals(path: Mapping[str, Any]) -> dict[str, Any]:
    families = path["by_family"]
    packet_count = sum(int(row["count"]) for row in families.values())
    matches = sum(int(row["matches"]) for row in families.values())
    challenge_capture = sum(int(row["challenge_capture"]) for row in families.values())
    challenge_expected = sum(int(row["challenge_expected"]) for row in families.values())
    false_positive_live_admits = sum(int(row["false_positive_live_admits"]) for row in families.values())
    review_minutes = sum(int(row["review_minutes"]) for row in families.values())
    return {
        "packet_count": packet_count,
        "route_fraction": f"{matches}/{packet_count}",
        "challenge_capture_fraction": f"{challenge_capture}/{challenge_expected}",
        "false_positive_live_admits": false_positive_live_admits,
        "review_minutes": review_minutes,
        "review_hours": round(review_minutes / 60, 2),
    }


def extract_iteration_note(readme: str) -> dict[str, Any]:
    first = re.search(r"admitted `(?P<count>\d+)/80` adversarial packets", readme)
    second = re.search(r"reduced unsafe admits to `(?P<count>\d+)/80`", readme)
    return {
        "first_generated_redteam_unsafe_admits": first.group("count") + "/80" if first else None,
        "second_redteam_unsafe_admits": second.group("count") + "/80" if second else None,
        "note_source": "docs/governance/ai_governance_llm_redteam/README.md",
    }


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_sha256s(out_dir: Path) -> None:
    rows = []
    for path in sorted(p for p in out_dir.rglob("*") if p.is_file() and p.name != "SHA256SUMS.txt"):
        rows.append(f"{sha256_file(path)}  {path.relative_to(out_dir).as_posix()}")
    (out_dir / "SHA256SUMS.txt").write_text("\n".join(rows) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Package the AI-governance residual-gate evidence into a public challenge benchmark."
    )
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--label", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    label = args.label or f"ai-governance-evidence-challenge-{timestamp}"
    out_dir = args.output_root / label
    source_out = out_dir / "source"
    out_dir.mkdir(parents=True, exist_ok=False)
    source_out.mkdir()

    sources: dict[str, dict[str, Any]] = {}
    loaded: dict[str, Any] = {}
    for key, rel in SOURCE_FILES.items():
        src = args.source_root / rel
        if not src.exists():
            raise SystemExit(f"missing source file: {src}")
        dest = source_out / f"{key}{src.suffix}"
        shutil.copy2(src, dest)
        sources[key] = {
            "source_path": rel,
            "copied_to": dest.relative_to(out_dir).as_posix(),
            "sha256": sha256_file(src),
            "bytes": src.stat().st_size,
        }
        if src.suffix == ".json":
            loaded[key] = load_json(src)
        elif src.suffix == ".md":
            loaded[key] = src.read_text(encoding="utf-8")

    llm_generation = loaded["llm_generation_summary"]
    llm_score = loaded["llm_residual_pass_score"]
    llm_fail_score = loaded["llm_residual_fail_score"]
    live_score = loaded["live_hardened_score"]
    comparison = loaded["redteam_comparison"]
    matrix = loaded["cross_machine_matrix"]
    exact_selector_counts = count_exact_selector_live_admits(loaded["llm_exact_selector_baseline"])
    iteration_note = extract_iteration_note(str(loaded["llm_redteam_readme"]))

    production_path_key = "production exact-selector plus replayed model residual gate"
    safe_path_key = "safe deterministic rubric v2"
    production_totals = path_totals(comparison["paths"][production_path_key])
    safe_totals = path_totals(comparison["paths"][safe_path_key])

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "claim_boundary": (
            "Evidence-packet challenge benchmark. It measures the residual gate after deterministic exact checks "
            "have already passed: a pinned model profile converts adversarial or ambiguous evidence packets into "
            "typed challenge routes while preserving the zero-positive-authority safety boundary."
        ),
        "source_repository": str(args.source_root),
        "llm_redteam": {
            "attacker_model": llm_generation["attacker_model"],
            "packet_count": llm_generation["packet_count"],
            "packet_set_root": llm_score["packet_set_root"],
            "generated_packet_set_root": llm_generation["packet_set_root"],
            "families": llm_generation["families"],
            "exact_selector_baseline": exact_selector_counts,
            "iteration_note": iteration_note,
            "failed_residual_run": llm_fail_score["production_acceptance"],
            "final_residual_run": llm_score["production_acceptance"],
            "by_family": llm_score["results"][0]["by_family"],
            "report_root": llm_score["report_root"],
        },
        "original_corpus_no_regression": {
            "packet_count": 240,
            "packet_set_root": live_score["packet_set_root"],
            "production_acceptance": live_score["production_acceptance"],
            "by_family": live_score["results"][0]["by_family"],
            "report_root": live_score["report_root"],
        },
        "safe_deterministic_comparison": {
            "cost_model": comparison["cost_model"],
            "safe_deterministic": safe_totals,
            "production": production_totals,
            "marginal_value": comparison["marginal_value"],
            "partition_seed": comparison["partition_seed"],
            "partition_metrics": comparison["partition_metrics"],
            "report_root": comparison["report_root"],
        },
        "cross_machine_replay": {
            "hardware_classes": comparison["cross_machine"]["hardware_classes"],
            "route_convergence": comparison["cross_machine"]["route_convergence"],
            "parsed_output_root_convergence": comparison["cross_machine"]["parsed_output_root_convergence"],
            "raw_output_root_convergence": comparison["cross_machine"]["raw_output_root_convergence"],
            "response_logprob_root_convergence": comparison["cross_machine"]["response_logprob_root_convergence"],
            "matrix_report_root": comparison["cross_machine"]["matrix_report_root"],
            "matrix_cross_machine": matrix["cross_machine"],
        },
        "whitepaper_safe_sentence": (
            "In an attacker-generated 80-packet residual-governance corpus whose exact fields passed the selector, "
            "the exact-selector baseline emitted admit for 80/80 packets, while the hardened negative-authority "
            "model routed 80/80 to typed challenge with zero false-positive live admits and schema-valid replay; "
            "on the original 240-packet corpus the same profile preserved zero false-positive live admits, captured "
            "64/72 typed challenge cases, and saved 20.4 first-pass review hours versus a safe deterministic fallback."
        ),
        "claim_discipline": [
            "Model output is evidence triage, with correctness still routed through typed challenge review.",
            "The model has negative authority only; it cannot select validators or create positive live authority.",
            "H100/H200 replay is same-vendor profile evidence, not a cross-vendor convergence claim.",
            "The review-hour result uses the declared cost fixture, not calendar-measured committee throughput.",
        ],
    }

    write_json(out_dir / "challenge_summary.json", summary)
    write_json(out_dir / "SOURCE_HASHES.json", sources)
    (out_dir / "COMMANDS.txt").write_text(
        "python3 scripts/ai_governance_evidence_challenge.py "
        f"--source-root {args.source_root} --label {label}\n"
        f"cd {out_dir} && sha256sum -c SHA256SUMS.txt\n",
        encoding="utf-8",
    )

    family_rows = [
        "| family | packets | route | challenge capture | false positives |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for family, row in llm_score["results"][0]["by_family"].items():
        family_rows.append(
            f"| `{family}` | {row['count']} | `{row['route_fraction']}` | "
            f"`{row['challenge_capture_fraction']}` | {row['false_positive']} |"
        )

    split_rows = [
        "| partition | packets | production challenges | safe deterministic challenges | production false-positive admits | review hours saved |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, row in comparison["partition_metrics"].items():
        split_rows.append(
            f"| `{name}` | {row['packet_count']} | `{row['production']['challenge_capture_fraction']}` | "
            f"`{row['safe_deterministic']['challenge_capture_fraction']}` | "
            f"{row['production']['false_positive_live_admits']} | {row['marginal_value']['review_hours_saved']} |"
        )

    source_rows = [
        "| key | source | sha256 |",
        "| --- | --- | --- |",
    ]
    for key, row in sources.items():
        source_rows.append(f"| `{key}` | `{row['source_path']}` | `{row['sha256']}` |")

    report = [
        "# AI Governance Evidence-Packet Challenge",
        "",
        "This packet packages the existing AI-governance red-team, original-corpus replay, and deterministic-fallback comparison into one auditable benchmark artifact.",
        "",
        "## Boundary",
        "",
        summary["claim_boundary"],
        "",
        "The useful question is whether a model with negative authority catches residual evidence risks after exact gates have already passed, without gaining the power to admit, vote, or change consensus thresholds.",
        "",
        "## Red-Team Result",
        "",
        f"- Attacker model: `{llm_generation['attacker_model']}`",
        f"- Adversarial packets: `{llm_generation['packet_count']}`",
        f"- Exact-selector baseline admits with positive live effect: `{exact_selector_counts['positive_live_admit_count']}/{exact_selector_counts['packet_count']}`",
        f"- First generated-red-team unsafe admits from README iteration note: `{iteration_note['first_generated_redteam_unsafe_admits']}`",
        f"- Second residual run unsafe admits: `{llm_fail_score['production_acceptance']['false_positive_live_effect']}/80`",
        f"- Final residual run false-positive live admits: `{llm_score['production_acceptance']['false_positive_live_effect']}`",
        f"- Final residual route: `{llm_score['production_acceptance']['route_fraction']}`",
        f"- Final residual challenge capture: `{llm_score['production_acceptance']['challenge_capture_fraction']}`",
        f"- Final parse/schema: `{llm_score['production_acceptance']['parse_ok_fraction']}` / `{llm_score['production_acceptance']['schema_valid_fraction']}`",
        f"- Final deterministic packets: `{llm_score['production_acceptance']['deterministic_packet_fraction']}`",
        "",
        "\n".join(family_rows),
        "",
        "## Original-Corpus No-Regression",
        "",
        "The same hardened residual prompt was rerun against the original 240-packet live benchmark corpus.",
        "",
        f"- Production acceptance: `{live_score['production_acceptance']['status']}`",
        f"- False-positive live admits: `{live_score['production_acceptance']['false_positive_live_effect']}`",
        f"- Route: `{live_score['production_acceptance']['route_fraction']}`",
        f"- Challenge capture: `{live_score['production_acceptance']['challenge_capture_fraction']}`",
        f"- Parse/schema/determinism: `{live_score['production_acceptance']['parse_ok_fraction']}` / `{live_score['production_acceptance']['schema_valid_fraction']}` / `{live_score['production_acceptance']['deterministic_packet_fraction']}`",
        "",
        "## Deterministic Fallback Comparison",
        "",
        "The safe deterministic rubric preserves safety by routing residual ambiguity to untyped committee review. The model-assisted production path keeps the same zero-false-positive live-admit invariant, but adds typed challenge triage.",
        "",
        "| path | route | false-positive admits | challenge capture | review hours |",
        "| --- | ---: | ---: | ---: | ---: |",
        f"| safe deterministic rubric v2 | `{safe_totals['route_fraction']}` | {safe_totals['false_positive_live_admits']} | `{safe_totals['challenge_capture_fraction']}` | {safe_totals['review_hours']} |",
        f"| exact selector + residual model | `{production_totals['route_fraction']}` | {production_totals['false_positive_live_admits']} | `{production_totals['challenge_capture_fraction']}` | {production_totals['review_hours']} |",
        "",
        f"- Challenge-capture lift: `{comparison['marginal_value']['challenge_capture_lift']}`",
        f"- Review minutes saved under declared cost fixture: `{comparison['marginal_value']['review_minutes_saved']}`",
        f"- Review hours saved under declared cost fixture: `{comparison['marginal_value']['review_hours_saved']}`",
        "",
        "## Hash-Split Holdouts",
        "",
        "\n".join(split_rows),
        "",
        "## Replay Evidence",
        "",
        f"- Hardware classes: `{', '.join(comparison['cross_machine']['hardware_classes'])}`",
        f"- Route convergence: `{comparison['cross_machine']['route_convergence']}`",
        f"- Parsed-output root convergence: `{comparison['cross_machine']['parsed_output_root_convergence']}`",
        f"- Raw-output root convergence: `{comparison['cross_machine']['raw_output_root_convergence']}`",
        f"- Response-logprob root convergence: `{comparison['cross_machine']['response_logprob_root_convergence']}`",
        f"- Matrix report root: `{comparison['cross_machine']['matrix_report_root']}`",
        "",
        "## Whitepaper-Safe Sentence",
        "",
        summary["whitepaper_safe_sentence"],
        "",
        "## Claim Discipline",
        "",
        "\n".join(f"- {item}" for item in summary["claim_discipline"]),
        "",
        "## Source Hashes",
        "",
        "\n".join(source_rows),
    ]
    (out_dir / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    write_sha256s(out_dir)

    print(f"artifact_dir={out_dir}")
    print(json.dumps(summary["whitepaper_safe_sentence"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
