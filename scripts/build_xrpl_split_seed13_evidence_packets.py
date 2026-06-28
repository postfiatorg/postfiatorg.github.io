#!/usr/bin/env python3
"""Build split XRPL seed-13 evidence packets.

The split is intentional:
- historical_vote_replay: XRP-native YES/NO labels with a concrete historical vote surface.
- prospective_open_vote_replay: open-for-voting rows, not scored as history.
- excluded_cases: rows that need a sharper decision surface before scoring.
"""

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

HISTORICAL_CASES = {
    "incident-amm-vote-reversal-2024": {
        "prompt_event_name": "AMM / XLS-30 pre-activation issue",
        "xrpl_vote_outcome": "NO",
        "label_basis": "reported_pre_activation_support_reversal",
        "surface_type": "amendment_activation_vote",
        "decision_question": (
            "Should validators continue supporting AMM/XLS-30 activation after pre-activation "
            "testing surfaced an issue?"
        ),
        "prompt_fact_override": (
            "Pre-activation testing surfaced an AMM/XLS-30 issue before the planned launch. "
            "Validators evaluating the amendment had to decide whether to continue support "
            "before the issue was fixed."
        ),
        "basis_note": (
            "Historical label uses public reporting of validator support withdrawal after the "
            "pre-activation AMM issue. The prompt excludes the phrase that validators revoked votes."
        ),
        "evidence_tier": "B",
    },
    "incident-batch-vulnerability-2026": {
        "prompt_event_name": "Batch disclosed vulnerability",
        "xrpl_vote_outcome": "NO",
        "label_basis": "official_validator_no_advisory",
        "surface_type": "validator_no_advisory",
        "decision_question": "Should validators support the Batch amendment after the disclosed signature-validation flaw?",
        "basis_note": "Official disclosure advised UNL validators to vote No and said 3.1.1 marked Batch unsupported.",
        "evidence_tier": "A",
    },
    "incident-permission-delegation-vulnerability-2025": {
        "prompt_event_name": "PermissionDelegation disclosed vulnerability",
        "xrpl_vote_outcome": "NO",
        "label_basis": "official_validator_no_advisory",
        "surface_type": "validator_no_advisory",
        "decision_question": (
            "Should validators support PermissionDelegation after the disclosed fee-charging vulnerability?"
        ),
        "basis_note": "Official disclosure advised validators to vote No and disabled the amendment.",
        "evidence_tier": "A",
    },
    "known-ammclawback": {
        "xrpl_vote_outcome": "YES",
        "label_basis": "mainnet_enabled_status_held_out",
        "surface_type": "mainnet_amendment_activation",
        "decision_question": "Should validators support enabling AMMClawback on mainnet?",
        "basis_note": "Known-amendments source status is Enabled; final status is held out of the prompt.",
        "evidence_tier": "A",
    },
    "known-clawback": {
        "xrpl_vote_outcome": "YES",
        "label_basis": "mainnet_enabled_status_held_out",
        "surface_type": "mainnet_amendment_activation",
        "decision_question": "Should validators support enabling Clawback on mainnet?",
        "basis_note": "Known-amendments source status is Enabled; final status is held out of the prompt.",
        "evidence_tier": "A",
    },
    "known-fixammoverflowoffer": {
        "xrpl_vote_outcome": "YES",
        "label_basis": "mainnet_enabled_status_and_default_yes",
        "surface_type": "mainnet_amendment_activation",
        "decision_question": "Should validators support enabling fixAMMOverflowOffer on mainnet?",
        "basis_note": (
            "Known-amendments source status is Enabled; final status is held out of the prompt. "
            "The source default vote is Yes and is retained as source-code metadata."
        ),
        "evidence_tier": "A",
    },
    "known-mptokensv1": {
        "xrpl_vote_outcome": "YES",
        "label_basis": "mainnet_enabled_status_held_out",
        "surface_type": "mainnet_amendment_activation",
        "decision_question": "Should validators support enabling MPTokensV1 on mainnet?",
        "basis_note": "Known-amendments source status is Enabled; final status is held out of the prompt.",
        "evidence_tier": "A",
    },
}

PROSPECTIVE_CASES = {
    "known-lendingprotocol": {
        "surface_type": "open_for_voting_snapshot",
        "decision_question": "Would the model recommend supporting LendingProtocol in the source snapshot?",
        "basis_note": "Open-for-voting source snapshot; excluded from historical vote alignment.",
    },
    "known-permissioneddex": {
        "surface_type": "open_for_voting_snapshot",
        "decision_question": "Would the model recommend supporting PermissionedDEX in the source snapshot?",
        "basis_note": "Open-for-voting source snapshot; excluded from historical vote alignment.",
    },
    "known-permissioneddomains": {
        "surface_type": "open_for_voting_snapshot",
        "decision_question": "Would the model recommend supporting PermissionedDomains in the source snapshot?",
        "basis_note": "Open-for-voting source snapshot; excluded from historical vote alignment.",
    },
    "known-singleassetvault": {
        "surface_type": "open_for_voting_snapshot",
        "decision_question": "Would the model recommend supporting SingleAssetVault in the source snapshot?",
        "basis_note": "Open-for-voting source snapshot; excluded from historical vote alignment.",
    },
    "known-tokenescrow": {
        "surface_type": "open_for_voting_snapshot",
        "decision_question": "Would the model recommend supporting TokenEscrow in the source snapshot?",
        "basis_note": "Open-for-voting source snapshot; excluded from historical vote alignment.",
    },
}

EXCLUDED_CASES = {
    "incident-amm-post-launch-pool-discrepancy-2024": {
        "exclusion_reason": "ambiguous_vote_surface",
        "basis_note": (
            "The source says AMM was live, pool discrepancies were found, and the fix required "
            "another amendment. A single YES/NO label is ambiguous unless the packet names the "
            "specific vote surface: support for the unfixed state, or support for a corrective "
            "fix amendment."
        ),
        "required_fix": (
            "Split into a named unfixed-AMM activation/reversal surface and a named corrective "
            "fix-amendment surface before scoring as historical replay."
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


def sources_for(row: dict[str, str]) -> list[dict[str, str]]:
    source_ids = split_pipe(row["source_ids"])
    return [
        {
            "source_id": f"S{idx + 1}",
            "source_type": "source_backed",
            "provenance_boundary": (
                "Raw source IDs and URLs are held out of the prompt packet to avoid title/URL "
                "slug leakage. Full provenance is recorded in the packet metadata files."
            ),
        }
        for idx, _source_id in enumerate(source_ids)
    ]


def source_fact_for(row: dict[str, str], generated_at: str, fact_override: str | None = None) -> list[dict[str, str]]:
    return [
        {
            "fact_id": "F1",
            "source_id": "S1",
            "quote_or_summary": fact_override or row["description"],
            "retrieved_at": generated_at,
        }
    ]


def build_packet(
    row: dict[str, str],
    generated_at: str,
    *,
    packet_family: str,
    case_meta: dict[str, str],
    include_source_status: bool,
) -> dict[str, Any]:
    source_facts = source_fact_for(row, generated_at, case_meta.get("prompt_fact_override"))
    packet = {
        "packet_version": f"{packet_family}-v1",
        "packet_family": packet_family,
        "packet_id": row["event_id"],
        "amendment_or_event_name": case_meta.get("prompt_event_name", row["event_name"]),
        "amendment_id": row["amendment_id"],
        "decision_surface": {
            "surface_type": case_meta["surface_type"],
            "question": case_meta["decision_question"],
        },
        "governance_decision_frame": {
            "task": "Predict a single XRP-native amendment vote recommendation for the decision surface.",
            "scored_output_field": "xrpl_vote_recommendation",
            "allowed_scored_values": ["YES", "NO"],
            "do_not_do": [
                "Do not output any third option or internal workflow state as the scored vote.",
                "Do not invent facts outside the packet.",
            ],
            "interpretation": {
                "YES": "support or approve enabling the amendment/change at the stated XRPL vote surface",
                "NO": "oppose, veto, or do not support enabling the amendment/change at the stated XRPL vote surface",
            },
        },
        "source_default_vote_context": {
            "default_vote": row["default_vote"],
            "interpretation_boundary": (
                "Source-code/config metadata. It may be a useful XRP-native cue, but it is not "
                "a held-out route label."
            ),
        },
        "source_evidence_grade": row["evidence_grade"],
        "source_facts": source_facts,
        "historical_facts": source_facts,
        "sources": sources_for(row),
        "vote_context": {
            "threshold": "80_percent_for_two_weeks",
            "support_source_id": "xrpl_amendments_process",
            "process_summary": (
                "XRPL amendments are enabled by validator voting after an 80% supermajority "
                "is maintained for the required interval. Validator voting is XRP-native "
                "YES/support or NO/oppose."
            ),
        },
        "blind_eval_boundary": (
            "Prompt packet excludes held-out vote outcomes, corpus workflow labels, risk tags, "
            "controversy signals, safe labels, and classifier-generated hints."
        ),
    }
    if include_source_status:
        packet["source_status_context"] = {
            "status": row["status"],
            "interpretation_boundary": "Source snapshot context only; not a historical alignment target.",
        }
    else:
        packet["blind_eval_boundary"] += " Final/current source status is also excluded."
    packet["packet_hash"] = sha_json(packet)
    return packet


def default_output_dir() -> Path:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return REPO_ROOT / "static/benchmarks" / f"xrpl-split-seed13-evidence-{ts}"


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
    generated_at = utc_now()

    with (source / "real_event_corpus.csv").open(newline="", encoding="utf-8") as fh:
        rows_by_id = {row["event_id"]: row for row in csv.DictReader(fh)}

    historical_dir = out / "historical_vote_replay"
    prospective_dir = out / "prospective_open_vote_replay"
    excluded_dir = out / "excluded_cases"
    (historical_dir / "amendment_packets").mkdir(parents=True, exist_ok=True)
    (prospective_dir / "amendment_packets").mkdir(parents=True, exist_ok=True)
    excluded_dir.mkdir(parents=True, exist_ok=True)

    manifest_rows: list[dict[str, str]] = []
    historical_labels = {
        "generated_at": generated_at,
        "eval_boundary": (
            "Historical alignment is computed only for rows in this file. Every row is XRP-native "
            "YES/NO and historical_replay_eligible=true."
        ),
        "source_packet": source.relative_to(REPO_ROOT).as_posix(),
        "selection_policy": (
            "Original seed-13 cases split by eligibility. Open-for-voting rows and ambiguous "
            "incident rows are excluded from historical alignment."
        ),
        "labels": {},
    }
    prospective_meta = {
        "generated_at": generated_at,
        "eval_boundary": (
            "Prospective/open-vote rows are not historical labels. Reports may show source-default "
            "match, but must not call it historical vote alignment."
        ),
        "source_packet": source.relative_to(REPO_ROOT).as_posix(),
        "cases": {},
    }
    excluded_cases = {
        "generated_at": generated_at,
        "source_packet": source.relative_to(REPO_ROOT).as_posix(),
        "cases": {},
    }

    for seed_name, event_id in SEED_13_SELECTION:
        row = rows_by_id[event_id]
        if event_id in HISTORICAL_CASES:
            meta = HISTORICAL_CASES[event_id]
            packet = build_packet(
                row,
                generated_at,
                packet_family="historical-vote-replay",
                case_meta=meta,
                include_source_status=False,
            )
            write_json(historical_dir / "amendment_packets" / f"{packet['packet_id']}.json", packet)
            historical_labels["labels"][event_id] = {
                "seed_name": seed_name,
                "event_id": event_id,
                "event_name": row["event_name"],
                "historical_replay_eligible": True,
                "xrpl_vote_outcome": meta["xrpl_vote_outcome"],
                "label_basis": meta["label_basis"],
                "evidence_tier": meta["evidence_tier"],
                "decision_surface": packet["decision_surface"],
                "basis_note": meta["basis_note"],
                "source_status_held_out": row["status"],
                "source_reported_default_vote": row["default_vote"],
                "source_ids": split_pipe(row["source_ids"]),
                "source_urls": split_pipe(row["source_urls"]),
            }
            bucket = "historical_vote_replay"
        elif event_id in PROSPECTIVE_CASES:
            meta = PROSPECTIVE_CASES[event_id]
            packet = build_packet(
                row,
                generated_at,
                packet_family="prospective-open-vote-replay",
                case_meta=meta,
                include_source_status=True,
            )
            write_json(prospective_dir / "amendment_packets" / f"{packet['packet_id']}.json", packet)
            prospective_meta["cases"][event_id] = {
                "seed_name": seed_name,
                "event_id": event_id,
                "event_name": row["event_name"],
                "historical_replay_eligible": False,
                "source_status": row["status"],
                "source_reported_default_vote": row["default_vote"],
                "decision_surface": packet["decision_surface"],
                "basis_note": meta["basis_note"],
                "source_ids": split_pipe(row["source_ids"]),
                "source_urls": split_pipe(row["source_urls"]),
            }
            bucket = "prospective_open_vote_replay"
        elif event_id in EXCLUDED_CASES:
            meta = EXCLUDED_CASES[event_id]
            excluded_cases["cases"][event_id] = {
                "seed_name": seed_name,
                "event_id": event_id,
                "event_name": row["event_name"],
                "historical_replay_eligible": False,
                "exclusion_reason": meta["exclusion_reason"],
                "basis_note": meta["basis_note"],
                "required_fix": meta["required_fix"],
                "source_status": row["status"],
                "source_reported_default_vote": row["default_vote"],
                "source_ids": split_pipe(row["source_ids"]),
                "source_urls": split_pipe(row["source_urls"]),
                "source_fact": row["description"],
            }
            bucket = "excluded_cases"
        else:
            raise KeyError(f"Seed case has no split bucket: {event_id}")
        manifest_rows.append(
            {
                "packet_id": event_id,
                "seed_name": seed_name,
                "event_name": row["event_name"],
                "bucket": bucket,
                "historical_replay_eligible": str(event_id in HISTORICAL_CASES).lower(),
                "source_status": row["status"],
                "source_default_vote": row["default_vote"],
                "notes": (
                    HISTORICAL_CASES.get(event_id, PROSPECTIVE_CASES.get(event_id, EXCLUDED_CASES.get(event_id, {})))
                    .get("basis_note", "")
                ),
            }
        )

    write_json(historical_dir / "historical_vote_labels.json", historical_labels)
    write_json(prospective_dir / "prospective_vote_metadata.json", prospective_meta)
    write_json(excluded_dir / "excluded_cases.json", excluded_cases)

    with (out / "split_selection_manifest.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(manifest_rows[0]))
        writer.writeheader()
        writer.writerows(manifest_rows)

    (out / "README.md").write_text(
        "\n".join(
            [
                "# XRPL Split Seed-13 Evidence Packet",
                "",
                f"Generated: {generated_at}",
                "",
                "This packet fixes the earlier mixed-label design by separating historical vote replay from",
                "prospective/open-vote recommendation and excluded ambiguous incidents.",
                "",
                "Historical alignment is valid only under `historical_vote_replay/`.",
                "Prospective rows under `prospective_open_vote_replay/` are not historical labels.",
                "Excluded rows under `excluded_cases/` must be split or sharpened before scoring.",
                "",
                "Run:",
                "",
                "```bash",
                f"python3 scripts/run_qwen_xrpl_vote_replay.py --corpus {historical_dir.relative_to(REPO_ROOT).as_posix()}/amendment_packets --endpoint <OPENAI_COMPATIBLE_SGLANG_ENDPOINT> --model Qwen/Qwen3.6-27B-FP8 --machine-receipt {historical_dir.relative_to(REPO_ROOT).as_posix()}/vast_lifecycle/machine_receipt.json --runs 3 --validators 41 --fail-on-error",
                f"python3 scripts/summarize_xrpl_historical_vote_replay.py --packet {historical_dir.relative_to(REPO_ROOT).as_posix()}",
                f"python3 scripts/run_qwen_xrpl_vote_replay.py --corpus {prospective_dir.relative_to(REPO_ROOT).as_posix()}/amendment_packets --endpoint <OPENAI_COMPATIBLE_SGLANG_ENDPOINT> --model Qwen/Qwen3.6-27B-FP8 --machine-receipt {prospective_dir.relative_to(REPO_ROOT).as_posix()}/vast_lifecycle/machine_receipt.json --runs 3 --validators 41 --fail-on-error",
                f"python3 scripts/summarize_xrpl_prospective_vote_replay.py --packet {prospective_dir.relative_to(REPO_ROOT).as_posix()}",
                "```",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (out / "COMMANDS.txt").write_text(
        "\n".join(
            [
                f"python3 scripts/build_xrpl_split_seed13_evidence_packets.py --source {source.relative_to(REPO_ROOT).as_posix()} --output {out.relative_to(REPO_ROOT).as_posix()}",
                f"python3 scripts/run_qwen_xrpl_vote_replay.py --corpus {historical_dir.relative_to(REPO_ROOT).as_posix()}/amendment_packets --endpoint <OPENAI_COMPATIBLE_SGLANG_ENDPOINT> --model Qwen/Qwen3.6-27B-FP8 --machine-receipt {historical_dir.relative_to(REPO_ROOT).as_posix()}/vast_lifecycle/machine_receipt.json --runs 3 --validators 41 --fail-on-error",
                f"python3 scripts/summarize_xrpl_historical_vote_replay.py --packet {historical_dir.relative_to(REPO_ROOT).as_posix()}",
                f"python3 scripts/run_qwen_xrpl_vote_replay.py --corpus {prospective_dir.relative_to(REPO_ROOT).as_posix()}/amendment_packets --endpoint <OPENAI_COMPATIBLE_SGLANG_ENDPOINT> --model Qwen/Qwen3.6-27B-FP8 --machine-receipt {prospective_dir.relative_to(REPO_ROOT).as_posix()}/vast_lifecycle/machine_receipt.json --runs 3 --validators 41 --fail-on-error",
                f"python3 scripts/summarize_xrpl_prospective_vote_replay.py --packet {prospective_dir.relative_to(REPO_ROOT).as_posix()}",
                f"cd {out.relative_to(REPO_ROOT).as_posix()} && sha256sum -c SHA256SUMS.txt",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    root_hash = write_sha256s(out)
    print(
        json.dumps(
            {
                "packet": out.relative_to(REPO_ROOT).as_posix(),
                "historical_count": len(historical_labels["labels"]),
                "prospective_count": len(prospective_meta["cases"]),
                "excluded_count": len(excluded_cases["cases"]),
                "packet_root": root_hash,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
