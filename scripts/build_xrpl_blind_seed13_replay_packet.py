#!/usr/bin/env python3
"""Build blind replay packets for the original XRPL governance seed set."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

ROUTE_MAP = {
    "DELAY_FOR_FIX": "DELAY_FOR_FIX",
    "HOLD_FOR_CHALLENGE": "HOLD_FOR_CHALLENGE",
    "PROCEED_AFTER_REVIEW": "PROCEED",
    "PROCEED_OR_LOW_SIGNAL_HOLD": "HOLD_FOR_CHALLENGE",
    "REJECT": "REJECT",
}

SEED_13_SELECTION = [
    ("AMM post-launch pool discrepancy", "incident-amm-post-launch-pool-discrepancy-2024"),
    ("AMM / XLS-30 activation vote reversal", "incident-amm-vote-reversal-2024"),
    ("AMMClawback", "known-ammclawback"),
    ("Batch", "incident-batch-vulnerability-2026"),
    ("Clawback", "known-clawback"),
    ("fixAMMOverflowOffer", "known-fixammoverflowoffer"),
    ("LendingProtocol", "known-lendingprotocol"),
    ("MPTokensV1", "known-mptokensv1"),
    ("PermissionDelegation", "incident-permission-delegation-vulnerability-2025"),
    ("PermissionedDEX", "known-permissioneddex"),
    ("PermissionedDomains", "known-permissioneddomains"),
    ("SingleAssetVault", "known-singleassetvault"),
    ("TokenEscrow", "known-tokenescrow"),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha_json(data: Any) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


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


def split_pipe(value: str) -> list[str]:
    return [item for item in str(value or "").split("|") if item]


def build_blind_packet(row: dict[str, str], generated_at: str) -> dict[str, Any]:
    source_ids = split_pipe(row["source_ids"])
    source_urls = split_pipe(row["source_urls"])
    sources = [
        {
            "source_id": source_id,
            "source_type": "source_backed",
            "url": source_urls[idx] if idx < len(source_urls) else "",
        }
        for idx, source_id in enumerate(source_ids)
    ]
    packet = {
        "packet_version": "blind-seed13-v2",
        "packet_id": row["event_id"],
        "amendment_or_event_name": row["event_name"],
        "amendment_id": row["amendment_id"],
        "governance_decision_frame": {
            "task": (
                "Classify the governance route that would have been appropriate for "
                "validator/operator review at the relevant decision point described by "
                "the source facts."
            ),
            "do_not_do": [
                "Do not reject merely because the event is historical.",
                "Do not reject merely because an amendment is already enabled.",
                "Do not treat source-code default-vote metadata as the route answer by itself.",
            ],
            "use_source_status_as": (
                "Source status is context for reconstructing the decision point, not an "
                "automatic route label."
            ),
            "use_default_vote_as": (
                "Source-reported default vote is source-code/config metadata. Official "
                "advisories that validators should vote No remain substantive source facts, "
                "but a generic default No does not by itself imply REJECT or DELAY_FOR_FIX."
            ),
        },
        "source_status_context": {
            "status": row["status"],
            "interpretation_boundary": (
                "Use this as source metadata only. It is not a held-out route label."
            ),
        },
        "source_default_vote_context": {
            "default_vote": row["default_vote"],
            "interpretation_boundary": (
                "Use this as source metadata only. It is not a held-out route label."
            ),
        },
        "source_evidence_grade": row["evidence_grade"],
        "source_facts": [
            {
                "fact_id": "F1",
                "source_id": source_ids[0] if source_ids else "expanded_corpus",
                "quote_or_summary": row["description"],
                "retrieved_at": generated_at,
            }
        ],
        "historical_facts": [
            {
                "fact_id": "F1",
                "source_id": source_ids[0] if source_ids else "expanded_corpus",
                "quote_or_summary": row["description"],
                "retrieved_at": generated_at,
            }
        ],
        "sources": sources,
        "vote_context": {
            "threshold": "80_percent_for_two_weeks",
            "support_source_id": "xrpl_amendments_process",
            "process_summary": (
                "XRPL amendments are enabled by validator voting after an 80% supermajority "
                "is maintained for the required interval."
            ),
        },
        "blind_eval_boundary": (
            "This prompt packet intentionally excludes corpus route labels, risk tags, "
            "controversy signals, safe_route labels, and classifier-generated route hints. "
            "Official source statements, including source-reported default votes or validator "
            "advisories, are retained as facts."
        ),
    }
    packet["packet_hash"] = sha_json(packet)
    return packet


def default_output_dir() -> Path:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return REPO_ROOT / "static/benchmarks" / f"xrpl-blind-seed13-governance-replay-{ts}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=REPO_ROOT / "docs/evidence/xrpl-governance-corpus-expansion-20260602T020000Z",
    )
    parser.add_argument("--output", type=Path, default=default_output_dir())
    args = parser.parse_args()

    source = args.source.resolve()
    out = args.output.resolve()
    packets_dir = out / "amendment_packets"
    packets_dir.mkdir(parents=True, exist_ok=True)
    generated_at = utc_now()

    with (source / "real_event_corpus.csv").open(newline="", encoding="utf-8") as fh:
        rows_by_id = {row["event_id"]: row for row in csv.DictReader(fh)}

    labels = {
        "generated_at": generated_at,
        "eval_boundary": (
            "These labels are not included in amendment_packets. They are used only after "
            "model outputs are written."
        ),
        "source_packet": source.relative_to(REPO_ROOT).as_posix(),
        "selection_policy": (
            "Original 13 named examples. For Batch and PermissionDelegation, use the "
            "incident-response rows rather than duplicate known-amendment rows so official "
            "validator no-vote advisories remain in the source facts."
        ),
        "labels": {},
    }
    manifest_rows = []
    for seed_name, event_id in SEED_13_SELECTION:
        row = rows_by_id[event_id]
        packet = build_blind_packet(row, generated_at)
        write_json(packets_dir / f"{packet['packet_id']}.json", packet)
        expected_route = ROUTE_MAP[row["route_hint"]]
        labels["labels"][packet["packet_id"]] = {
            "seed_name": seed_name,
            "event_id": row["event_id"],
            "event_name": row["event_name"],
            "expected_route": expected_route,
            "expected_vote_default": {
                "PROCEED": "YES",
                "DELAY_FOR_FIX": "NO",
                "HOLD_FOR_CHALLENGE": "HOLD",
                "REJECT": "NO",
            }[expected_route],
            "route_hint_source": "held_out_expanded_corpus_label",
            "raw_route_hint": row["route_hint"],
            "held_out_signals": split_pipe(row["signals"]),
            "source_reported_status": row["status"],
            "source_reported_default_vote": row["default_vote"],
        }
        manifest_rows.append(
            {
                "packet_id": packet["packet_id"],
                "seed_name": seed_name,
                "event_name": row["event_name"],
                "source_reported_status": row["status"],
                "source_reported_default_vote": row["default_vote"],
                "expected_route_held_out": expected_route,
                "source_ids": row["source_ids"],
                "source_urls": row["source_urls"],
            }
        )

    write_json(out / "blind_eval_labels.json", labels)
    with (out / "blind_selection_manifest.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(manifest_rows[0]))
        writer.writeheader()
        writer.writerows(manifest_rows)

    (out / "README.md").write_text(
        "\n".join(
            [
                "# XRPL Blind Seed-13 Governance Replay Packet",
                "",
                f"Generated: {generated_at}",
                "",
                "This packet contains the original 13 named governance examples in blind form.",
                "Prompt packets retain official source facts, statuses, default-vote fields, and",
                "validator advisories, but exclude corpus route labels, classifier risk tags,",
                "controversy signals, and generated route-hint facts.",
                "",
                "Held-out labels live in `blind_eval_labels.json` and must not be included in",
                "the model prompt.",
                "",
                "Run:",
                "",
                "```bash",
                f"python3 scripts/run_qwen_amendment_replay.py --corpus {out.relative_to(REPO_ROOT).as_posix()}/amendment_packets --endpoint <OPENAI_COMPATIBLE_SGLANG_ENDPOINT> --model Qwen/Qwen3.6-27B-FP8 --machine-receipt {out.relative_to(REPO_ROOT).as_posix()}/vast_lifecycle/machine_receipt.json --runs 3 --validators 41 --fail-on-error",
                f"python3 scripts/summarize_xrpl_blind_seed13_replay.py --packet {out.relative_to(REPO_ROOT).as_posix()}",
                "```",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (out / "COMMANDS.txt").write_text(
        "\n".join(
            [
                f"python3 scripts/build_xrpl_blind_seed13_replay_packet.py --source {source.relative_to(REPO_ROOT).as_posix()} --output {out.relative_to(REPO_ROOT).as_posix()}",
                f"python3 scripts/run_qwen_amendment_replay.py --corpus {out.relative_to(REPO_ROOT).as_posix()}/amendment_packets --endpoint <OPENAI_COMPATIBLE_SGLANG_ENDPOINT> --model Qwen/Qwen3.6-27B-FP8 --machine-receipt {out.relative_to(REPO_ROOT).as_posix()}/vast_lifecycle/machine_receipt.json --runs 3 --validators 41 --fail-on-error",
                f"python3 scripts/summarize_xrpl_blind_seed13_replay.py --packet {out.relative_to(REPO_ROOT).as_posix()}",
                f"cd {out.relative_to(REPO_ROOT).as_posix()} && sha256sum -c SHA256SUMS.txt",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    packet_root = write_sha256s(out)
    print(json.dumps({"packet": out.relative_to(REPO_ROOT).as_posix(), "packet_count": 13, "packet_root": packet_root}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
