#!/usr/bin/env python3
"""Build vote-only blind replay packets for the original XRPL seed set."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

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

VOTE_OUTCOMES = {
    "incident-amm-post-launch-pool-discrepancy-2024": {
        "xrpl_vote_outcome": "NO",
        "comparison_basis": "official_post_launch_discrepancy_fix_required",
        "basis_note": (
            "Incident row, not a named amendment activation row: source says the live AMM state "
            "had pool discrepancies and required a follow-up amendment, so the XRP-native replay "
            "vote target is no support for proceeding with the unfixed state."
        ),
    },
    "incident-amm-vote-reversal-2024": {
        "xrpl_vote_outcome": "NO",
        "comparison_basis": "reported_validator_support_reversal",
        "basis_note": (
            "Incident row: source reporting says validators revoked support after pre-activation "
            "testing surfaced an issue."
        ),
    },
    "incident-batch-vulnerability-2026": {
        "xrpl_vote_outcome": "NO",
        "comparison_basis": "official_validator_no_advisory",
        "basis_note": "Official disclosure advised UNL validators to vote No.",
    },
    "incident-permission-delegation-vulnerability-2025": {
        "xrpl_vote_outcome": "NO",
        "comparison_basis": "official_validator_no_advisory",
        "basis_note": "Official disclosure advised validators to vote No and disabled the amendment.",
    },
    "known-ammclawback": {
        "xrpl_vote_outcome": "YES",
        "comparison_basis": "mainnet_enabled_status_held_out",
        "basis_note": "Known-amendments source status is Enabled; status is held out of the prompt.",
    },
    "known-clawback": {
        "xrpl_vote_outcome": "YES",
        "comparison_basis": "mainnet_enabled_status_held_out",
        "basis_note": "Known-amendments source status is Enabled; status is held out of the prompt.",
    },
    "known-fixammoverflowoffer": {
        "xrpl_vote_outcome": "YES",
        "comparison_basis": "mainnet_enabled_status_and_default_yes",
        "basis_note": (
            "Known-amendments source status is Enabled and source default vote is Yes; status is "
            "held out of the prompt, default vote is retained as source metadata."
        ),
    },
    "known-mptokensv1": {
        "xrpl_vote_outcome": "YES",
        "comparison_basis": "mainnet_enabled_status_held_out",
        "basis_note": "Known-amendments source status is Enabled; status is held out of the prompt.",
    },
    "known-lendingprotocol": {
        "xrpl_vote_outcome": "NO",
        "comparison_basis": "source_default_vote_snapshot_open_for_voting",
        "basis_note": (
            "Open-for-voting row without final mainnet outcome in this source snapshot; score "
            "uses the XRP-native source default vote, not final validator history."
        ),
    },
    "known-permissioneddex": {
        "xrpl_vote_outcome": "NO",
        "comparison_basis": "source_default_vote_snapshot_open_for_voting",
        "basis_note": (
            "Open-for-voting row without final mainnet outcome in this source snapshot; score "
            "uses the XRP-native source default vote, not final validator history."
        ),
    },
    "known-permissioneddomains": {
        "xrpl_vote_outcome": "NO",
        "comparison_basis": "source_default_vote_snapshot_open_for_voting",
        "basis_note": (
            "Open-for-voting row without final mainnet outcome in this source snapshot; score "
            "uses the XRP-native source default vote, not final validator history."
        ),
    },
    "known-singleassetvault": {
        "xrpl_vote_outcome": "NO",
        "comparison_basis": "source_default_vote_snapshot_open_for_voting",
        "basis_note": (
            "Open-for-voting row without final mainnet outcome in this source snapshot; score "
            "uses the XRP-native source default vote, not final validator history."
        ),
    },
    "known-tokenescrow": {
        "xrpl_vote_outcome": "NO",
        "comparison_basis": "source_default_vote_snapshot_open_for_voting",
        "basis_note": (
            "Open-for-voting row without final mainnet outcome in this source snapshot; score "
            "uses the XRP-native source default vote, not final validator history."
        ),
    },
}


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


def build_vote_packet(row: dict[str, str], generated_at: str) -> dict[str, Any]:
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
    source_facts = [
        {
            "fact_id": "F1",
            "source_id": source_ids[0] if source_ids else "expanded_corpus",
            "quote_or_summary": row["description"],
            "retrieved_at": generated_at,
        }
    ]
    packet = {
        "packet_version": "vote-only-seed13-v1",
        "packet_id": row["event_id"],
        "amendment_or_event_name": row["event_name"],
        "amendment_id": row["amendment_id"],
        "governance_decision_frame": {
            "task": (
                "Predict a single XRP-native amendment vote outcome for the relevant decision "
                "point described by the packet facts."
            ),
            "scored_output_field": "xrpl_vote_recommendation",
            "allowed_scored_values": ["YES", "NO"],
            "do_not_do": [
                "Do not output any third option or internal workflow state as the scored vote.",
                "Do not invent facts outside the packet.",
                "Do not treat missing final status as permission to create a third vote option.",
            ],
            "interpretation": {
                "YES": "support or approve enabling the amendment/change at the relevant vote surface",
                "NO": "oppose, veto, or do not support enabling the amendment/change at the relevant vote surface",
            },
        },
        "source_default_vote_context": {
            "default_vote": row["default_vote"],
            "interpretation_boundary": (
                "Retained source-code/config metadata. It is an XRP-native vote cue, but the "
                "model must still justify the final YES/NO from packet facts."
            ),
        },
        "source_evidence_grade": row["evidence_grade"],
        "source_facts": source_facts,
        "historical_facts": source_facts,
        "sources": sources,
        "vote_context": {
            "threshold": "80_percent_for_two_weeks",
            "support_source_id": "xrpl_amendments_process",
            "process_summary": (
                "XRPL amendments are enabled by validator voting after an 80% supermajority "
                "is maintained for the required interval. Validator voting is XRP-native "
                "YES/support or NO/oppose; internal review states are not XRP vote options."
            ),
        },
        "blind_eval_boundary": (
            "This prompt packet intentionally excludes held-out vote outcomes, source status "
            "when it would reveal final outcome, corpus workflow labels, risk tags, controversy "
            "signals, safe labels, and classifier-generated hints. Source default "
            "votes and explicit validator advisories remain because they are XRP-native source facts."
        ),
    }
    packet["packet_hash"] = sha_json(packet)
    return packet


def default_output_dir() -> Path:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return REPO_ROOT / "static/benchmarks" / f"xrpl-vote-only-seed13-replay-{ts}"


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
            "These YES/NO labels are not included in amendment_packets. They are used only "
            "after model outputs are written. Alignment compares only xrpl_vote_recommendation "
            "against xrpl_vote_outcome."
        ),
        "source_packet": source.relative_to(REPO_ROOT).as_posix(),
        "selection_policy": (
            "Original 13 named examples. Batch and PermissionDelegation use incident-response "
            "rows so official validator no-vote advisories remain in source facts. Final/current "
            "source status is held out of prompt packets because it can reveal the vote outcome."
        ),
        "labels": {},
    }
    manifest_rows = []
    for seed_name, event_id in SEED_13_SELECTION:
        row = rows_by_id[event_id]
        packet = build_vote_packet(row, generated_at)
        write_json(packets_dir / f"{packet['packet_id']}.json", packet)
        label = VOTE_OUTCOMES[event_id]
        labels["labels"][packet["packet_id"]] = {
            "seed_name": seed_name,
            "event_id": row["event_id"],
            "event_name": row["event_name"],
            "xrpl_vote_outcome": label["xrpl_vote_outcome"],
            "comparison_basis": label["comparison_basis"],
            "basis_note": label["basis_note"],
            "source_status_held_out": row["status"],
            "source_reported_default_vote": row["default_vote"],
        }
        manifest_rows.append(
            {
                "packet_id": packet["packet_id"],
                "seed_name": seed_name,
                "event_name": row["event_name"],
                "xrpl_vote_outcome_held_out": label["xrpl_vote_outcome"],
                "comparison_basis": label["comparison_basis"],
                "source_status_held_out": row["status"],
                "source_reported_default_vote": row["default_vote"],
                "source_ids": row["source_ids"],
                "source_urls": row["source_urls"],
            }
        )

    write_json(out / "vote_eval_labels.json", labels)
    with (out / "vote_selection_manifest.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(manifest_rows[0]))
        writer.writeheader()
        writer.writerows(manifest_rows)

    (out / "README.md").write_text(
        "\n".join(
            [
                "# XRPL Vote-Only Seed-13 Replay Packet",
                "",
                f"Generated: {generated_at}",
                "",
                "This packet contains the original 13 named governance examples in vote-only blind form.",
                "The scored output is only `xrpl_vote_recommendation`, with allowed values `YES` or `NO`.",
                "Prompt packets exclude held-out vote outcomes, source status when it would reveal final outcome,",
                "route labels, risk tags, controversy signals, safe-route labels, and generated route-hint facts.",
                "",
                "Held-out labels live in `vote_eval_labels.json` and must not be included in the model prompt.",
                "",
                "Run:",
                "",
                "```bash",
                f"python3 scripts/run_qwen_xrpl_vote_replay.py --corpus {out.relative_to(REPO_ROOT).as_posix()}/amendment_packets --endpoint <OPENAI_COMPATIBLE_SGLANG_ENDPOINT> --model Qwen/Qwen3.6-27B-FP8 --machine-receipt {out.relative_to(REPO_ROOT).as_posix()}/vast_lifecycle/machine_receipt.json --runs 3 --validators 41 --fail-on-error",
                f"python3 scripts/summarize_xrpl_vote_only_seed13_replay.py --packet {out.relative_to(REPO_ROOT).as_posix()}",
                "```",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (out / "COMMANDS.txt").write_text(
        "\n".join(
            [
                f"python3 scripts/build_xrpl_vote_only_seed13_replay_packet.py --source {source.relative_to(REPO_ROOT).as_posix()} --output {out.relative_to(REPO_ROOT).as_posix()}",
                f"python3 scripts/run_qwen_xrpl_vote_replay.py --corpus {out.relative_to(REPO_ROOT).as_posix()}/amendment_packets --endpoint <OPENAI_COMPATIBLE_SGLANG_ENDPOINT> --model Qwen/Qwen3.6-27B-FP8 --machine-receipt {out.relative_to(REPO_ROOT).as_posix()}/vast_lifecycle/machine_receipt.json --runs 3 --validators 41 --fail-on-error",
                f"python3 scripts/summarize_xrpl_vote_only_seed13_replay.py --packet {out.relative_to(REPO_ROOT).as_posix()}",
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
