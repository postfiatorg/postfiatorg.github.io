#!/usr/bin/env python3
"""Convert the expanded XRPL governance corpus into replay packet JSON files."""

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

RISK_MAP = {
    "active_vote_surface": "active_vote_surface",
    "asset_control_or_compliance": "asset_control",
    "default_no_surface": "default_no_surface",
    "follow_up_fix": "follow_up_fix",
    "known_bug": "known_bug",
    "new_financial_primitive": "new_financial_primitive",
    "obsolete_or_disabled": "obsolete",
    "public_debate": "public_debate",
    "public_vote_reversal": "public_vote_reversal",
    "security_or_liveness": "security_or_liveness",
    "user_fund_or_accounting_risk": "user_fund_or_accounting_risk",
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


def route_to_vote(route: str) -> str:
    return {
        "PROCEED": "YES",
        "DELAY_FOR_FIX": "NO",
        "HOLD_FOR_CHALLENGE": "HOLD",
        "REJECT": "NO",
    }.get(route, "HOLD")


def deterministic_route(packet: dict[str, Any]) -> dict[str, Any]:
    risks = set(packet["risk_class"])
    route = packet["historical_outcome"]["route"]
    triggered = []
    if route == "REJECT":
        triggered.append("obsolete, disabled, or incident-response row -> REJECT")
    elif route == "DELAY_FOR_FIX":
        triggered.append("known bug, public reversal, or post-launch fix sequencing -> DELAY_FOR_FIX")
    elif route == "PROCEED":
        triggered.append("source-backed fix or enabled amendment row -> PROCEED after review")
    elif route == "HOLD_FOR_CHALLENGE":
        triggered.append("new financial, security, asset-control, or compliance semantics -> HOLD_FOR_CHALLENGE")
    if "known_bug" in risks:
        triggered.append("known_bug signal present")
    if "asset_control" in risks:
        triggered.append("asset_control signal present")
    if "new_financial_primitive" in risks:
        triggered.append("new_financial_primitive signal present")
    return {
        "route": route,
        "vote_default": route_to_vote(route),
        "triggered_rules": triggered,
        "cited_facts": [fact["fact_id"] for fact in packet["historical_facts"]],
        "limitations": [
            "This deterministic baseline is a route floor over the selected corpus labels.",
            "It does not claim model lift; lift must be measured against H200/SGLang outputs.",
        ],
    }


def build_packet(row: dict[str, str], generated_at: str) -> dict[str, Any]:
    signals = split_pipe(row["signals"])
    risk_class = sorted({RISK_MAP.get(signal, signal) for signal in signals})
    route = ROUTE_MAP[row["route_hint"]]
    source_ids = split_pipe(row["source_ids"])
    source_urls = split_pipe(row["source_urls"])
    sources = [
        {
            "source_id": source_id,
            "source_type": "source_backed",
            "summary": f"Source for {row['event_name']}",
            "url": source_urls[idx] if idx < len(source_urls) else "",
        }
        for idx, source_id in enumerate(source_ids)
    ]
    packet = {
        "packet_version": 2,
        "packet_id": row["event_id"],
        "amendment_name": row["event_name"],
        "amendment_id": row["amendment_id"],
        "event_window": {"start": "", "end": ""},
        "event_type": row["event_type"],
        "short_description": row["description"][:500],
        "technical_change": row["description"][:1200],
        "risk_class": risk_class,
        "controversy_signals": signals,
        "controversy_score": int(row["controversy_score"]),
        "source_corpus_cluster_id": row["cluster_id"],
        "source_evidence_grade": row["evidence_grade"],
        "included_in_original_13_seed": row["included_in_13_seed"].lower() == "true",
        "historical_facts": [
            {
                "fact_id": "F1",
                "claim": row["description"][:500],
                "source_id": source_ids[0] if source_ids else "expanded_corpus",
                "quote_or_summary": row["description"][:900],
                "retrieved_at": generated_at,
            },
            {
                "fact_id": "F2",
                "claim": f"Corpus classifier route hint for {row['event_name']} is {row['route_hint']}.",
                "source_id": "expanded_corpus_summary",
                "quote_or_summary": "Route hint derived from source-backed signals and used as the historical/research label for replay scoring.",
                "retrieved_at": generated_at,
            },
        ],
        "sources": sources,
        "vote_context": {
            "threshold": "80_percent_for_two_weeks",
            "support_source_id": "xrpl_amendments_process",
        },
        "historical_outcome": {
            "route": route,
            "outcome_summary": row["description"][:900],
            "outcome_source_id": source_ids[0] if source_ids else "expanded_corpus",
        },
        "safe_route_label": {
            "label": route,
            "label_basis": "expanded_source_backed_corpus",
            "labeler": "build_xrpl_governance_corpus_expansion.py",
            "notes": f"Expanded corpus row route_hint={row['route_hint']}; synthetic derivatives are excluded from this real-row replay.",
        },
    }
    packet["packet_hash"] = sha_json(packet)
    return packet


def default_output_dir() -> Path:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return REPO_ROOT / "static" / "benchmarks" / f"xrpl-expanded-governance-h200-replay-{ts}"


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

    rows: list[dict[str, str]]
    with (source / "real_event_corpus.csv").open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    packets = [build_packet(row, generated_at) for row in rows]
    deterministic = {}
    for packet in packets:
        write_json(packets_dir / f"{packet['packet_id']}.json", packet)
        deterministic[packet["packet_id"]] = deterministic_route(packet)

    write_json(
        out / "deterministic_baseline.json",
        {
            "generated_at": generated_at,
            "rule_engine_version": "expanded-xrpl-governance-route-floor-v1",
            "source_packet": source.relative_to(REPO_ROOT).as_posix(),
            "results": deterministic,
        },
    )
    write_json(out / "expanded_corpus_summary.json", json.loads((source / "summary.json").read_text(encoding="utf-8")))
    write_json(out / "expanded_corpus_source_hashes.json", json.loads((source / "SOURCE_HASHES.json").read_text(encoding="utf-8")))
    (out / "corpus_selection.csv").write_text((source / "real_event_corpus.csv").read_text(encoding="utf-8"), encoding="utf-8")
    (out / "synthetic_variant_seeds.csv").write_text(
        (source / "synthetic_variant_seeds.csv").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (out / "README.md").write_text(
        "\n".join(
            [
                "# XRPL Expanded Governance H200 Replay Packet",
                "",
                f"Generated: {generated_at}",
                "",
                f"Source expansion packet: `{source.relative_to(REPO_ROOT).as_posix()}`",
                f"Real replay packets: {len(packets)}",
                "Synthetic variant seeds are copied for feeder traceability but are not replayed in this packet.",
                "",
                "Run model replay:",
                "",
                "```bash",
                f"python3 scripts/run_qwen_amendment_replay.py --corpus {out.relative_to(REPO_ROOT).as_posix()}/amendment_packets --endpoint <OPENAI_COMPATIBLE_SGLANG_ENDPOINT> --model Qwen/Qwen3.6-27B-FP8 --machine-receipt {out.relative_to(REPO_ROOT).as_posix()}/vast_lifecycle/machine_receipt.json --runs 3 --validators 41",
                f"python3 scripts/summarize_xrpl_amendment_replay.py --packet {out.relative_to(REPO_ROOT).as_posix()}",
                "```",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (out / "COMMANDS.txt").write_text(
        "\n".join(
            [
                f"python3 scripts/build_xrpl_expanded_replay_packet.py --source {source.relative_to(REPO_ROOT).as_posix()} --output {out.relative_to(REPO_ROOT).as_posix()}",
                f"python3 scripts/run_qwen_amendment_replay.py --corpus {out.relative_to(REPO_ROOT).as_posix()}/amendment_packets --endpoint <OPENAI_COMPATIBLE_SGLANG_ENDPOINT> --model Qwen/Qwen3.6-27B-FP8 --machine-receipt {out.relative_to(REPO_ROOT).as_posix()}/vast_lifecycle/machine_receipt.json --runs 3 --validators 41",
                f"python3 scripts/summarize_xrpl_amendment_replay.py --packet {out.relative_to(REPO_ROOT).as_posix()}",
                f"cd {out.relative_to(REPO_ROOT).as_posix()} && sha256sum -c SHA256SUMS.txt",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    root = write_sha256s(out)
    print(out.relative_to(REPO_ROOT).as_posix())
    print(f"packet_count={len(packets)}")
    print(f"packet_root={root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
