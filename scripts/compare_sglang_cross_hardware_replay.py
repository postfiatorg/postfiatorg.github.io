#!/usr/bin/env python3
"""Compare SGLang/MLX replay profiles for cross-hardware evidence packets."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from xrpl_lifecycle_common import LANES, artifact_path, read_json, sha_json, utc_now, write_json, write_sha256s


LABEL_FIELDS = {
    "vote_outcome": "xrpl_vote_recommendation",
    "vote_state": "vote_state",
    "default_vote": "source_default_vote",
    "triage": "route",
}


def stable_profile_acceptance_hash(runtime_manifest: dict[str, Any]) -> str:
    """Hash only the fields that define an accepted replay profile.

    Existing lifecycle artifacts include `generated_at`, endpoint, and local
    machine-receipt path in the runtime manifest. Those are useful provenance,
    but they should not make two otherwise identical profile runs incomparable.
    """
    summary = dict(runtime_manifest.get("machine_receipt_summary") or {})
    stable = {
        "runtime_kind": runtime_manifest.get("runtime_kind"),
        "model": runtime_manifest.get("model"),
        "machine_receipt_sha256": runtime_manifest.get("machine_receipt_sha256"),
        "machine_receipt_summary": summary,
        "temperature": runtime_manifest.get("temperature"),
        "top_p": runtime_manifest.get("top_p"),
        "response_format": runtime_manifest.get("response_format"),
        "chat_template_kwargs": runtime_manifest.get("chat_template_kwargs"),
        "separate_reasoning": runtime_manifest.get("separate_reasoning"),
    }
    return sha_json(stable)


def raw_hash(run: dict[str, Any]) -> str:
    return hashlib.sha256(str(run.get("raw_message_content") or "").encode("utf-8")).hexdigest()


def cited_fact_ids(run: dict[str, Any]) -> list[str]:
    output = run.get("output_json") or {}
    ids: list[str] = []
    for item in output.get("cited_facts") or []:
        if isinstance(item, dict) and item.get("fact_id"):
            ids.append(str(item["fact_id"]))
    return sorted(set(ids))


def source_fact_set_hash(ids: list[str]) -> str:
    return sha_json(ids)


def load_run(root: Path, lane: str, packet_id: str, run_index: int = 1) -> dict[str, Any] | None:
    path = root / "qwen_runs" / lane / packet_id / f"run_{run_index:03d}.json"
    if not path.exists():
        return None
    return read_json(path)


def drift_class(row: dict[str, Any]) -> str:
    if not row["packet_hash_match"] or not row["prompt_hash_match"]:
        return "invalid_input_mismatch"
    if not row["schema_valid_a"] or not row["schema_valid_b"]:
        return "schema_invalid"
    if row["raw_output_hash_match"] and row["parsed_output_hash_match"]:
        return "exact_raw_and_parsed_match"
    if row["parsed_output_hash_match"]:
        return "raw_text_drift_only"
    if row["route_label_match"] and row["source_fact_set_match"]:
        return "parsed_shape_drift_route_and_facts_stable"
    if row["route_label_match"]:
        return "source_fact_drift_route_stable"
    return "governance_relevant_route_drift"


def compare_roots(
    *,
    artifact: Path,
    name: str,
    root_a: Path,
    root_b: Path,
    profile_a: str,
    profile_b: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    runtime_a = read_json(root_a / "qwen_runs" / "runtime_manifest.json")
    runtime_b = read_json(root_b / "qwen_runs" / "runtime_manifest.json")
    profile_hash_a = stable_profile_acceptance_hash(runtime_a)
    profile_hash_b = stable_profile_acceptance_hash(runtime_b)
    rows: list[dict[str, Any]] = []

    for lane in LANES:
        labels = read_json(root_a / "labels" / f"{lane}_labels.json")
        for packet_id in sorted(labels):
            run_a = load_run(root_a, lane, packet_id)
            run_b = load_run(root_b, lane, packet_id)
            if not run_a or not run_b:
                rows.append(
                    {
                        "comparison": name,
                        "lane": lane,
                        "packet_id": packet_id,
                        "profile_a": profile_a,
                        "profile_b": profile_b,
                        "profile_acceptance_hash_a": profile_hash_a,
                        "profile_acceptance_hash_b": profile_hash_b,
                        "profile_acceptance_hash_match": profile_hash_a == profile_hash_b,
                        "missing_run_a": run_a is None,
                        "missing_run_b": run_b is None,
                        "drift_class": "missing_run",
                    }
                )
                continue

            facts_a = cited_fact_ids(run_a)
            facts_b = cited_fact_ids(run_b)
            label_a = str(run_a.get("parsed_label") or "")
            label_b = str(run_b.get("parsed_label") or "")
            unsafe_a = lane == "triage" and label_a == "PROCEED" and labels[packet_id]["expected_label"] in {
                "HOLD_FOR_CHALLENGE",
                "DELAY_FOR_FIX",
                "REJECT",
            }
            unsafe_b = lane == "triage" and label_b == "PROCEED" and labels[packet_id]["expected_label"] in {
                "HOLD_FOR_CHALLENGE",
                "DELAY_FOR_FIX",
                "REJECT",
            }
            row = {
                "comparison": name,
                "lane": lane,
                "packet_id": packet_id,
                "event_id": run_a.get("event_id") or run_b.get("event_id"),
                "profile_a": profile_a,
                "profile_b": profile_b,
                "profile_acceptance_hash_a": profile_hash_a,
                "profile_acceptance_hash_b": profile_hash_b,
                "profile_acceptance_hash_match": profile_hash_a == profile_hash_b,
                "packet_hash_a": run_a.get("packet_hash"),
                "packet_hash_b": run_b.get("packet_hash"),
                "packet_hash_match": run_a.get("packet_hash") == run_b.get("packet_hash"),
                "prompt_hash_a": run_a.get("prompt_hash"),
                "prompt_hash_b": run_b.get("prompt_hash"),
                "prompt_hash_match": run_a.get("prompt_hash") == run_b.get("prompt_hash"),
                "raw_output_hash_a": raw_hash(run_a),
                "raw_output_hash_b": raw_hash(run_b),
                "raw_output_hash_match": raw_hash(run_a) == raw_hash(run_b),
                "parsed_output_hash_a": run_a.get("output_hash"),
                "parsed_output_hash_b": run_b.get("output_hash"),
                "parsed_output_hash_match": run_a.get("output_hash") == run_b.get("output_hash"),
                "route_label_a": label_a,
                "route_label_b": label_b,
                "route_label_match": label_a == label_b,
                "source_fact_ids_a": ",".join(facts_a),
                "source_fact_ids_b": ",".join(facts_b),
                "source_fact_set_hash_a": source_fact_set_hash(facts_a),
                "source_fact_set_hash_b": source_fact_set_hash(facts_b),
                "source_fact_set_match": facts_a == facts_b,
                "schema_valid_a": bool(run_a.get("schema_valid")),
                "schema_valid_b": bool(run_b.get("schema_valid")),
                "unsafe_proceed_a": unsafe_a,
                "unsafe_proceed_b": unsafe_b,
                "unsafe_proceed_delta": unsafe_a != unsafe_b,
            }
            row["drift_class"] = drift_class(row)
            rows.append(row)

    counts = Counter(row["drift_class"] for row in rows)
    by_lane: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        by_lane[row["lane"]][row["drift_class"]] += 1
    summary = {
        "comparison": name,
        "generated_at": utc_now(),
        "profile_a": profile_a,
        "profile_b": profile_b,
        "root_a": root_a.as_posix(),
        "root_b": root_b.as_posix(),
        "profile_acceptance_hash_a": profile_hash_a,
        "profile_acceptance_hash_b": profile_hash_b,
        "profile_acceptance_hash_match": profile_hash_a == profile_hash_b,
        "row_count": len(rows),
        "drift_class_counts": dict(counts),
        "drift_class_counts_by_lane": {lane: dict(counts) for lane, counts in by_lane.items()},
        "packet_hash_mismatches": sum(1 for row in rows if not row.get("packet_hash_match")),
        "prompt_hash_mismatches": sum(1 for row in rows if not row.get("prompt_hash_match")),
        "schema_invalid_rows": sum(1 for row in rows if not row.get("schema_valid_a") or not row.get("schema_valid_b")),
        "route_label_mismatches": sum(1 for row in rows if not row.get("route_label_match")),
        "source_fact_set_mismatches": sum(1 for row in rows if not row.get("source_fact_set_match")),
        "unsafe_proceed_deltas": sum(1 for row in rows if row.get("unsafe_proceed_delta")),
    }
    return rows, summary


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_readme(root: Path, summaries: list[dict[str, Any]]) -> None:
    lines = [
        "# SGLang Cross-Hardware Replay Evidence",
        "",
        f"Generated: {utc_now()}",
        "",
        "This packet compares profile-addressed replay outputs. It separates machine/profile acceptance hashes, packet/prompt hashes, raw output hashes, parsed output hashes, route labels, cited source facts, and unsafe-proceed deltas.",
        "",
        "## Comparisons",
        "",
    ]
    for summary in summaries:
        lines.extend(
            [
                f"### {summary['comparison']}",
                "",
                f"- Profile A: `{summary['profile_a']}`",
                f"- Profile B: `{summary['profile_b']}`",
                f"- Rows: {summary['row_count']}",
                f"- Profile acceptance hash match: `{summary['profile_acceptance_hash_match']}`",
                f"- Packet hash mismatches: {summary['packet_hash_mismatches']}",
                f"- Prompt hash mismatches: {summary['prompt_hash_mismatches']}",
                f"- Schema-invalid rows: {summary['schema_invalid_rows']}",
                f"- Route-label mismatches: {summary['route_label_mismatches']}",
                f"- Source-fact-set mismatches: {summary['source_fact_set_mismatches']}",
                f"- Unsafe-proceed deltas: {summary['unsafe_proceed_deltas']}",
                f"- Drift classes: `{json.dumps(summary['drift_class_counts'], sort_keys=True)}`",
                "",
            ]
        )
    root.joinpath("README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--selected-source", default="static/benchmarks/xrpl-amendment-lifecycle-replay-20260602T142703Z")
    parser.add_argument("--heldout-source", default="static/benchmarks/xrpl-amendment-lifecycle-heldout-20260602T182517Z")
    args = parser.parse_args(argv)

    root = artifact_path(args.artifact)
    selected_source = artifact_path(args.selected_source)
    heldout_source = artifact_path(args.heldout_source)

    candidate_comparisons = [
        (
            "h200_repeatability_selected",
            selected_source,
            root / "profiles" / "h200_sglang_repeat_selected",
            "h200_sglang_initial_selected",
            "h200_sglang_repeat_selected",
        ),
        (
            "h200_repeatability_heldout",
            heldout_source,
            root / "profiles" / "h200_sglang_repeat_heldout",
            "h200_sglang_initial_heldout",
            "h200_sglang_repeat_heldout",
        ),
        (
            "h200_repeat_vs_h100nvl_heldout",
            root / "profiles" / "h200_sglang_repeat_heldout",
            root / "profiles" / "h100nvl_sglang_heldout",
            "h200_sglang_repeat_heldout",
            "h100nvl_sglang_heldout",
        ),
        (
            "h100nvl_selected_clean_repeat",
            root / "profiles" / "h100nvl_selected_a",
            root / "profiles" / "h100nvl_selected_b",
            "h100nvl_selected_a",
            "h100nvl_selected_b",
        ),
        (
            "h100nvl_heldout_clean_repeat",
            root / "profiles" / "h100nvl_heldout_a",
            root / "profiles" / "h100nvl_heldout_b",
            "h100nvl_heldout_a",
            "h100nvl_heldout_b",
        ),
        (
            "h100nvl_vs_second_cuda_heldout",
            root / "profiles" / "h100nvl_heldout_a",
            root / "profiles" / "second_cuda_heldout",
            "h100nvl_heldout_a",
            "second_cuda_heldout",
        ),
    ]
    comparisons = [
        item
        for item in candidate_comparisons
        if (item[1] / "qwen_runs" / "runtime_manifest.json").exists()
        and (item[2] / "qwen_runs" / "runtime_manifest.json").exists()
    ]
    all_rows: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    for name, root_a, root_b, profile_a, profile_b in comparisons:
        rows, summary = compare_roots(
            artifact=root,
            name=name,
            root_a=root_a,
            root_b=root_b,
            profile_a=profile_a,
            profile_b=profile_b,
        )
        write_csv(root / "comparisons" / f"{name}.csv", rows)
        write_json(root / "comparisons" / f"{name}_summary.json", summary)
        all_rows.extend(rows)
        summaries.append(summary)

    combined = {
        "generated_at": utc_now(),
        "artifact": root.as_posix(),
        "comparisons": summaries,
        "combined_drift_class_counts": dict(Counter(row["drift_class"] for row in all_rows)),
        "combined_rows": len(all_rows),
        "combined_route_label_mismatches": sum(1 for row in all_rows if not row.get("route_label_match")),
        "combined_unsafe_proceed_deltas": sum(1 for row in all_rows if row.get("unsafe_proceed_delta")),
    }
    write_csv(root / "comparisons" / "combined_comparison.csv", all_rows)
    write_json(root / "comparisons" / "combined_summary.json", combined)
    write_readme(root, summaries)
    combined["sha256s_hash"] = write_sha256s(root)
    write_json(root / "comparisons" / "combined_summary.json", combined)
    print(json.dumps(combined, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
