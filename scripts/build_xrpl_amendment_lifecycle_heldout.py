#!/usr/bin/env python3
"""Build the held-out XRPL amendment lifecycle replay artifact from a frozen split."""

from __future__ import annotations

import argparse
import copy
import csv
import json
import shutil
from collections import Counter
from pathlib import Path
from typing import Any

from build_xrpl_amendment_lifecycle_corpus import write_packets
from run_qwen_xrpl_amendment_lifecycle_replay import build_prompt
from xrpl_lifecycle_common import LANES, artifact_path, read_json, sha_text, utc_now, write_json, write_sha256s


GENERATED_DIRS = ("packets", "labels", "baseline", "qwen_runs", "summaries", "reports", "prompt_audit")


def rel_artifact(path: Path) -> str:
    try:
        return path.relative_to(path.parents[2]).as_posix()
    except ValueError:
        return str(path)


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def scrub_for_leak_scan(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: scrub_for_leak_scan(item)
            for key, item in value.items()
            if key not in {"allowed_labels", "held_out_fields"}
        }
    if isinstance(value, list):
        return [scrub_for_leak_scan(item) for item in value]
    return value


def packet_fact_text(packet: dict[str, Any]) -> str:
    facts = packet.get("input_context", {}).get("source_facts", [])
    return "\n".join(str(item.get("claim", "")) for item in facts if isinstance(item, dict)).upper()


def write_prompt_audit(root: Path, labels: dict[str, dict[str, Any]]) -> None:
    audit_dir = root / "prompt_audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    warnings: list[str] = []
    prompt_rows: list[dict[str, str]] = []
    prompt_hash_counts: Counter[str] = Counter()

    for lane in LANES:
        for packet_path in sorted((root / "packets" / lane).glob("*.json")):
            packet = read_json(packet_path)
            packet_id = packet["packet_id"]
            prompt = build_prompt(packet)
            prompt_hash = sha_text(prompt)
            prompt_hash_counts[prompt_hash] += 1
            prompt_rows.append(
                {
                    "lane": lane,
                    "packet_id": packet_id,
                    "packet_hash": packet["packet_hash"],
                    "prompt_hash": prompt_hash,
                }
            )
            if "Required JSON schema:" not in prompt or "Allowed labels:" not in prompt:
                errors.append(f"{lane} {packet_id}: prompt missing schema or allowed labels")
            if "Allowed labels define the output schema only" not in prompt:
                errors.append(f"{lane} {packet_id}: prompt missing anti-label-order instruction")
            if "Use only the packet facts by fact_id" not in prompt:
                errors.append(f"{lane} {packet_id}: prompt missing packet-facts-only instruction")

            scrubbed_text = json.dumps(scrub_for_leak_scan(packet), sort_keys=True).upper()
            for forbidden_field in ("TERMINAL_OUTCOME", "VOTE_STATE_LABEL", "SOURCE_DEFAULT_VOTE", "TRIAGE_POLICY_LABEL"):
                if forbidden_field in scrubbed_text:
                    errors.append(f"{lane} {packet_id}: held-out label field leaked into packet body")
            if lane == "vote_outcome":
                for triage_label in ("HOLD_FOR_CHALLENGE", "DELAY_FOR_FIX"):
                    if triage_label in scrubbed_text:
                        errors.append(f"{lane} {packet_id}: triage label leaked into vote_outcome packet")
                fact_text = packet_fact_text(packet)
                for current_state_marker in (
                    "VALIDATED LEDGER AMENDMENTS OBJECT CURRENTLY CONTAINS",
                    "ENABLED_ON=",
                    "ENABLED_IN_LEDGER=",
                ):
                    if current_state_marker in fact_text:
                        errors.append(f"{lane} {packet_id}: current enabled-state fact leaked into vote_outcome")
            if lane == "triage":
                fact_text = packet_fact_text(packet)
                for current_state_marker in (
                    "VALIDATED LEDGER AMENDMENTS OBJECT CURRENTLY CONTAINS",
                    "ENABLED_ON=",
                    "ENABLED_IN_LEDGER=",
                ):
                    if current_state_marker in fact_text:
                        errors.append(f"{lane} {packet_id}: current enabled-state fact leaked into triage")
            if packet_id not in labels[lane]:
                errors.append(f"{lane} {packet_id}: missing label entry")

    write_json(
        audit_dir / "prompt_audit.json",
        {
            "generated_at": utc_now(),
            "valid": not errors,
            "errors": errors,
            "warnings": warnings,
            "prompt_count": len(prompt_rows),
            "unique_prompt_hash_count": len(prompt_hash_counts),
            "prompt_hash_counts": dict(prompt_hash_counts),
            "prompt_rows": prompt_rows,
            "design_notes": [
                "Allowed labels are included so the classifier knows the valid output vocabulary.",
                "Expected label values are stored only under labels/ and are not present in packet input_context.",
                "The prompt explicitly forbids using label order, case ids, event ids, held_out_fields names, outside knowledge, or real-world memory as evidence.",
                "vote_outcome and triage packets exclude current enabled-state facts; vote_state packets include them by design.",
                "triage is a conservative policy-conformance lane, not an XRP validator vote lane.",
            ],
        },
    )
    write_csv(audit_dir / "prompt_hashes.csv", prompt_rows, ["lane", "packet_id", "packet_hash", "prompt_hash"])
    lines = [
        "# Prompt Design Audit",
        "",
        f"Generated: {utc_now()}",
        "",
        f"- Valid: {not errors}",
        f"- Prompt count: {len(prompt_rows)}",
        f"- Unique prompt hashes: {len(prompt_hash_counts)}",
        "",
        "## Design Position",
        "",
        "- Allowed labels are provided as output choices only.",
        "- Expected labels are kept in `labels/` and not placed in packet facts.",
        "- The prompt forbids outside knowledge, packet identity, label order, case numbering, and `held_out_fields` names as evidence.",
        "- `vote_outcome` and `triage` packets exclude current enabled-state facts.",
        "- `vote_state` packets intentionally include current or dated state facts.",
        "- `triage` remains a frozen conservative policy-conformance lane, not an XRP vote replay lane.",
        "",
        "## Errors",
        "",
    ]
    lines.extend([f"- {item}" for item in errors] or ["- None"])
    lines.extend(["", "## Warnings", ""])
    lines.extend([f"- {item}" for item in warnings] or ["- None"])
    (audit_dir / "PROMPT_AUDIT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_readme(root: Path, source_root: Path, selected: list[dict[str, Any]], labels: dict[str, dict[str, Any]]) -> None:
    lane_counts = {lane: len(values) for lane, values in labels.items()}
    terminal_counts = dict(Counter(event["terminal_outcome"] for event in selected))
    triage_counts = dict(Counter(event["triage_policy_label"] for event in selected))
    lines = [
        "# XRPL Amendment Lifecycle Held-Out Replay",
        "",
        f"Generated: {utc_now()}",
        "",
        f"Source artifact: `{source_root}`",
        "",
        "This artifact contains lifecycle rows where `selected == false` in the source artifact.",
        "It is a held-out validation set for the existing packet format and lane prompts.",
        "",
        "## Counts",
        "",
        f"- Held-out lifecycle rows: {len(selected)}",
        f"- Terminal outcome labels: {terminal_counts}",
        f"- Triage labels: {triage_counts}",
        f"- Lane packet counts: {lane_counts}",
        "",
        "## Claim Boundary",
        "",
        "`default_vote` is diagnostic only. `triage` is policy conformance. The clean historical lanes are `vote_outcome` and `vote_state`.",
    ]
    (root / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-artifact", required=True)
    parser.add_argument("--artifact", required=True)
    args = parser.parse_args(argv)

    source_root = artifact_path(args.source_artifact)
    root = artifact_path(args.artifact)
    root.mkdir(parents=True, exist_ok=True)

    for dirname in GENERATED_DIRS:
        path = root / dirname
        if path.exists():
            shutil.rmtree(path)

    source_corpus = source_root / "corpus"
    corpus_dir = root / "corpus"
    if corpus_dir.exists():
        shutil.rmtree(corpus_dir)
    shutil.copytree(source_corpus, corpus_dir)

    source_vast = source_root / "vast_lifecycle"
    if source_vast.exists():
        target_vast = root / "vast_lifecycle"
        if target_vast.exists():
            shutil.rmtree(target_vast)
        shutil.copytree(source_vast, target_vast)

    source_events = read_json(source_corpus / "lifecycle_events.json")
    events = copy.deepcopy(source_events)
    heldout_ids = {event["event_id"] for event in source_events if not event.get("selected")}
    for event in events:
        source_selected = bool(event.get("selected"))
        event["source_artifact_selected"] = source_selected
        event["source_artifact"] = str(source_root)
        event["selected"] = event["event_id"] in heldout_ids
        event.pop("case_id", None)
    selected = [event for event in events if event["selected"]]
    if len(selected) != 47:
        raise SystemExit(f"expected 47 held-out events from source split, found {len(selected)}")

    labels = write_packets(root, selected)
    write_prompt_audit(root, labels)

    write_json(corpus_dir / "lifecycle_events.json", events)
    write_json(corpus_dir / "corpus_selection.json", selected)
    write_json(
        corpus_dir / "heldout_manifest.json",
        {
            "generated_at": utc_now(),
            "source_artifact": str(source_root),
            "source_artifact_sha256s": read_json(source_root / "summaries" / "combined_summary.json").get("sha256s_hash", ""),
            "selection_rule": "event.selected == false in source artifact lifecycle_events.json",
            "heldout_count": len(selected),
            "lane_counts": {lane: len(values) for lane, values in labels.items()},
            "terminal_counts": dict(Counter(event["terminal_outcome"] for event in selected)),
            "vote_state_counts": dict(Counter(event["vote_state_label"] for event in selected)),
            "triage_counts": dict(Counter(event["triage_policy_label"] for event in selected)),
        },
    )
    write_csv(
        corpus_dir / "lifecycle_events.csv",
        [
            {
                "event_id": event["event_id"],
                "amendment_name": event["amendment_name"],
                "event_type": event["event_type"],
                "terminal_outcome": event["terminal_outcome"],
                "vote_state_label": event["vote_state_label"],
                "source_default_vote": event["source_default_vote"],
                "triage_policy_label": event["triage_policy_label"],
                "eligible_metrics": ",".join(event["eligible_metrics"]),
                "selected": event["selected"],
                "source_artifact_selected": event["source_artifact_selected"],
            }
            for event in events
        ],
        [
            "event_id",
            "amendment_name",
            "event_type",
            "terminal_outcome",
            "vote_state_label",
            "source_default_vote",
            "triage_policy_label",
            "eligible_metrics",
            "selected",
            "source_artifact_selected",
        ],
    )
    write_csv(
        corpus_dir / "corpus_selection.csv",
        [
            {
                "event_id": event["event_id"],
                "amendment_name": event["amendment_name"],
                "event_type": event["event_type"],
                "terminal_outcome": event["terminal_outcome"],
                "vote_state_label": event["vote_state_label"],
                "source_default_vote": event["source_default_vote"],
                "triage_policy_label": event["triage_policy_label"],
                "eligible_metrics": ",".join(event["eligible_metrics"]),
            }
            for event in selected
        ],
        [
            "event_id",
            "amendment_name",
            "event_type",
            "terminal_outcome",
            "vote_state_label",
            "source_default_vote",
            "triage_policy_label",
            "eligible_metrics",
        ],
    )

    rel_root = rel_artifact(root)
    commands = [
        f"scripts/build_xrpl_amendment_lifecycle_heldout.py --source-artifact {rel_artifact(source_root)} --artifact {rel_root}",
        (
            "scripts/validate_xrpl_amendment_lifecycle_corpus.py "
            f"--artifact {rel_root} --min-selected 47 --min-terminal-yes 46 "
            "--min-nonterminal-state 1 --min-sensitive-triage 11"
        ),
        f"scripts/run_xrpl_amendment_lifecycle_baseline.py --artifact {rel_root}",
        (
            "scripts/run_qwen_xrpl_amendment_lifecycle_replay.py "
            f"--artifact {rel_root} --lane all --endpoint http://52.24.227.223:17756/v1 "
            f"--machine-receipt {rel_root}/vast_lifecycle/machine_receipt.json --runs 1 --fail-on-error"
        ),
        f"scripts/summarize_xrpl_amendment_lifecycle_replay.py --artifact {rel_root}",
    ]
    (root / "COMMANDS.txt").write_text("\n".join(commands) + "\n", encoding="utf-8")
    write_readme(root, source_root, selected, labels)
    sha = write_sha256s(root)
    print(root)
    print(
        json.dumps(
            {
                "heldout_rows": len(selected),
                "lane_counts": {lane: len(values) for lane, values in labels.items()},
                "sha256s_hash": sha,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
