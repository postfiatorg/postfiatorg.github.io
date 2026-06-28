#!/usr/bin/env python3
"""Build EP-2: XLS amendment origination/status reconciliation.

This joins the frozen XLS provenance packet to current XRPL amendment state.
It is intentionally conservative: XLS status and ledger amendment status are
separate columns, and ambiguous mappings are labeled rather than forced.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from build_xrpl_amendment_lifecycle_corpus import (
    SOURCES,
    build_universe,
    fetch_source,
    parse_known_amendments,
)
from xrpl_lifecycle_common import artifact_path, read_json, sha_bytes, write_json, write_sha256s


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROVENANCE = REPO_ROOT / "static" / "benchmarks" / "xrpl-xls-provenance-20260603T230503Z"


XLS_TO_AMENDMENTS: dict[str, dict[str, Any]] = {
    "XLS-0007": {"names": ["DeletableAccounts"], "mapping_kind": "exact_feature"},
    "XLS-0008": {"names": ["Tickets"], "mapping_kind": "withdrawn_obsolete_related"},
    "XLS-0009": {"names": [], "mapping_kind": "not_in_known_amendments"},
    "XLS-0013": {"names": ["TicketBatch"], "mapping_kind": "exact_feature"},
    "XLS-0020": {
        "names": ["NonFungibleTokensV1", "NonFungibleTokensV1_1", "fixNonFungibleTokensV1_2"],
        "mapping_kind": "feature_family",
    },
    "XLS-0023": {"names": [], "mapping_kind": "not_in_known_amendments"},
    "XLS-0030": {"names": ["AMM"], "mapping_kind": "exact_feature"},
    "XLS-0033": {"names": ["MPTokensV1"], "mapping_kind": "exact_feature"},
    "XLS-0035": {"names": [], "mapping_kind": "not_in_known_amendments"},
    "XLS-0038": {"names": ["XChainBridge"], "mapping_kind": "exact_feature"},
    "XLS-0039": {"names": ["Clawback"], "mapping_kind": "exact_feature"},
    "XLS-0040": {"names": ["DID"], "mapping_kind": "exact_feature"},
    "XLS-0047": {"names": ["PriceOracle"], "mapping_kind": "exact_feature"},
    "XLS-0049": {"names": [], "mapping_kind": "not_in_known_amendments"},
    "XLS-0051": {"names": [], "mapping_kind": "not_in_known_amendments"},
    "XLS-0052": {"names": ["NFTokenMintOffer"], "mapping_kind": "exact_feature"},
    "XLS-0054": {"names": [], "mapping_kind": "not_in_known_amendments"},
    "XLS-0055": {"names": [], "mapping_kind": "not_in_known_amendments"},
    "XLS-0056": {"names": ["Batch"], "mapping_kind": "exact_feature_obsolete"},
    "XLS-0060": {"names": [], "mapping_kind": "not_in_known_amendments"},
    "XLS-0061": {"names": [], "mapping_kind": "not_in_known_amendments"},
    "XLS-0062": {"names": [], "mapping_kind": "not_in_known_amendments"},
    "XLS-0064": {"names": [], "mapping_kind": "not_in_known_amendments"},
    "XLS-0065": {"names": ["SingleAssetVault"], "mapping_kind": "exact_feature"},
    "XLS-0066": {"names": ["LendingProtocol"], "mapping_kind": "exact_feature"},
    "XLS-0067": {"names": [], "mapping_kind": "not_in_known_amendments"},
    "XLS-0068": {"names": ["Sponsor"], "mapping_kind": "tentative_name_from_spec"},
    "XLS-0070": {"names": ["Credentials"], "mapping_kind": "exact_feature"},
    "XLS-0071": {"names": [], "mapping_kind": "not_in_known_amendments"},
    "XLS-0073": {"names": ["AMMClawback"], "mapping_kind": "exact_feature"},
    "XLS-0074": {"names": [], "mapping_kind": "supporting_standard_not_standalone_amendment"},
    "XLS-0075": {"names": ["PermissionDelegation"], "mapping_kind": "exact_feature_obsolete"},
    "XLS-0076": {"names": [], "mapping_kind": "not_in_known_amendments"},
    "XLS-0077": {"names": ["DeepFreeze"], "mapping_kind": "exact_feature"},
    "XLS-0078": {"names": [], "mapping_kind": "not_in_known_amendments"},
    "XLS-0080": {"names": ["PermissionedDomains"], "mapping_kind": "exact_feature"},
    "XLS-0081": {"names": ["PermissionedDEX"], "mapping_kind": "exact_feature"},
    "XLS-0082": {"names": ["MPTokensV2"], "mapping_kind": "exact_feature"},
    "XLS-0085": {"names": ["TokenEscrow"], "mapping_kind": "exact_feature"},
    "XLS-0086": {"names": [], "mapping_kind": "not_in_known_amendments"},
    "XLS-0087": {"names": [], "mapping_kind": "not_in_known_amendments"},
    "XLS-0094": {"names": ["DynamicMPT"], "mapping_kind": "exact_feature"},
    "XLS-0096": {"names": ["ConfidentialTransfer"], "mapping_kind": "exact_feature"},
    "XLS-0100": {"names": ["SmartEscrow"], "mapping_kind": "exact_feature"},
    "XLS-0101": {"names": [], "mapping_kind": "not_in_known_amendments"},
    "XLS-0102": {"names": [], "mapping_kind": "supporting_standard_not_standalone_amendment"},
}


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def mainnet_state(details: list[dict[str, Any]]) -> str:
    if not details:
        return "NOT_PRESENT_IN_KNOWN_AMENDMENTS"
    if any(item.get("current_enabled") for item in details):
        return "ENABLED_IN_VALIDATED_LEDGER"
    statuses = {str(item.get("known_status", "")).upper() for item in details}
    if any("OPEN FOR VOTING" in status for status in statuses):
        return "OPEN_FOR_VOTING_NOT_ENABLED"
    if any("IN DEVELOPMENT" in status for status in statuses):
        return "IN_DEVELOPMENT_NOT_ENABLED"
    if any("OBSOLETE" in status or "RETIRED" in status for status in statuses):
        return "OBSOLETE_OR_RETIRED_NOT_ENABLED"
    return "UNKNOWN_NOT_ENABLED"


def mapping_confidence(mapping_kind: str, names: list[str], details: list[dict[str, Any]]) -> str:
    if not names:
        return "none"
    if not details:
        return "missing_current_state_for_mapped_name"
    if mapping_kind in {"exact_feature", "exact_feature_obsolete"}:
        return "high"
    if mapping_kind in {"feature_family", "tentative_name_from_spec"}:
        return "medium"
    return "low"


def build_packet(provenance_dir: Path, artifact_dir: Path) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = artifact_dir / "source_bodies"
    fetched = {
        source_id: fetch_source(source_id, meta, raw_dir)
        for source_id, meta in SOURCES.items()
        if source_id in {"xrpscan_amendments_api", "xrpl_validated_amendments_object", "xrpl_known_amendments_md"}
    }
    source_receipts = {source_id: item.receipt for source_id, item in fetched.items()}
    write_json(artifact_dir / "source_receipts.json", source_receipts)

    xrpscan_rows = json.loads(fetched["xrpscan_amendments_api"].body.decode("utf-8"))
    ledger_rpc = json.loads(fetched["xrpl_validated_amendments_object"].body.decode("utf-8"))
    ledger_node = ledger_rpc.get("result", {}).get("node", {})
    ledger_ids = {str(value).upper() for value in ledger_node.get("Amendments", [])}
    known = parse_known_amendments(fetched["xrpl_known_amendments_md"].body.decode("utf-8", errors="replace"))
    universe = build_universe(xrpscan_rows, ledger_ids, known)
    universe_by_name = {row["name"].lower(): row for row in universe}
    write_json(artifact_dir / "amendment_universe.json", universe)

    provenance_summary = read_json(provenance_dir / "summary.json")
    provenance_rows = [
        row
        for row in read_csv(provenance_dir / "xls_provenance.csv")
        if row.get("category", "").lower() == "amendment"
    ]

    rows: list[dict[str, Any]] = []
    detail_rows: list[dict[str, Any]] = []
    for row in provenance_rows:
        mapping = XLS_TO_AMENDMENTS.get(row["id"], {"names": [], "mapping_kind": "mapping_not_reviewed"})
        names = list(mapping["names"])
        details = [universe_by_name[name.lower()] for name in names if name.lower() in universe_by_name]
        state = mainnet_state(details)
        confidence = mapping_confidence(mapping["mapping_kind"], names, details)
        enabled_dates = [str(item.get("current_enabled_on") or "") for item in details if item.get("current_enabled_on")]
        mapped_statuses = [str(item.get("known_status") or "") for item in details]
        mapped_default_votes = [str(item.get("source_default_vote") or "") for item in details]
        mapped_ids = [str(item.get("amendment_id") or "") for item in details]
        support_group = row["strict_support_tier"]
        flat = {
            "xls_id": row["id"],
            "xls_title": row["title"],
            "xls_status": row["status"],
            "origin_tier": support_group,
            "author_raw": row["author_raw"],
            "mapping_kind": mapping["mapping_kind"],
            "mapping_confidence": confidence,
            "known_amendment_names": ";".join(names),
            "known_amendment_ids": ";".join(mapped_ids),
            "known_amendments_doc_statuses": ";".join(mapped_statuses),
            "known_amendments_default_votes": ";".join(mapped_default_votes),
            "mainnet_state": state,
            "enabled_dates": ";".join(enabled_dates),
            "support_counts": ";".join(str(item.get("current_support_count") or "") for item in details),
            "validation_counts": ";".join(str(item.get("current_validation_count") or "") for item in details),
            "thresholds": ";".join(str(item.get("current_threshold") or "") for item in details),
            "current_majorities": ";".join(str(item.get("current_majority") or "") for item in details),
            "xls_status_source_url": row["readme_url"],
            "proposal_from": row["proposal_from"],
            "mainnet_state_source_urls": ";".join(
                [
                    source_receipts["xrpl_known_amendments_md"]["url"],
                    source_receipts["xrpscan_amendments_api"]["url"],
                    source_receipts["xrpl_validated_amendments_object"]["url"],
                ]
            ),
            "notes": mapping.get("notes", ""),
        }
        rows.append(flat)
        detail = dict(flat)
        detail["mapped_amendment_details"] = details
        detail_rows.append(detail)

    columns = [
        "xls_id",
        "xls_title",
        "xls_status",
        "origin_tier",
        "author_raw",
        "mapping_kind",
        "mapping_confidence",
        "known_amendment_names",
        "known_amendment_ids",
        "known_amendments_doc_statuses",
        "known_amendments_default_votes",
        "mainnet_state",
        "enabled_dates",
        "support_counts",
        "validation_counts",
        "thresholds",
        "current_majorities",
        "xls_status_source_url",
        "proposal_from",
        "mainnet_state_source_urls",
        "notes",
    ]
    write_csv(artifact_dir / "amendment_status_reconciliation.csv", rows, columns)
    write_json(artifact_dir / "amendment_status_reconciliation.json", detail_rows)

    summary = {
        "generated_at": utc_now(),
        "provenance_packet": provenance_dir.relative_to(REPO_ROOT).as_posix(),
        "provenance_packet_sha256": sha_bytes((provenance_dir / "SHA256SUMS.txt").read_bytes()),
        "provenance_source_commit": provenance_summary.get("source_commit"),
        "amendment_rows": len(rows),
        "source_receipts": source_receipts,
        "live_state": {
            "validated_ledger_index": ledger_rpc.get("result", {}).get("ledger_index"),
            "validated_amendments_object_index": "7DB0788C020F02780A673DC74757F23823FA3014C1866E72CC4CD8B226CD6EF4",
            "validated_amendment_count": len(ledger_ids),
            "xrpscan_row_count": len(xrpscan_rows),
            "known_amendment_section_count": len(known),
        },
        "counts": {
            "origin_tier": Counter(row["origin_tier"] for row in rows),
            "xls_status": Counter(row["xls_status"] for row in rows),
            "mapping_kind": Counter(row["mapping_kind"] for row in rows),
            "mapping_confidence": Counter(row["mapping_confidence"] for row in rows),
            "mainnet_state": Counter(row["mainnet_state"] for row in rows),
        },
        "non_final_rows": [
            row["xls_id"]
            for row in rows
            if row["xls_status"].upper() in {"DRAFT", "STAGNANT", "DEPRECATED", "WITHDRAWN"}
        ],
        "caveat": "XLS status and validated-ledger amendment state are separate surfaces. Some Known Amendments doc statuses can lag validated-ledger membership; this packet exposes both.",
    }
    write_json(artifact_dir / "summary.json", summary)

    no_known = [row for row in rows if row["mainnet_state"] == "NOT_PRESENT_IN_KNOWN_AMENDMENTS"]
    write_csv(artifact_dir / "not_present_in_known_amendments.csv", no_known, columns)

    report = [
        "# XRPL Amendment Origination Status Reconciliation",
        "",
        f"Generated: {summary['generated_at']}",
        "",
        f"Provenance packet: `{summary['provenance_packet']}`",
        "",
        "## Counts",
        "",
        f"- Amendment XLS rows: {len(rows)}",
        f"- Validated ledger index: {summary['live_state']['validated_ledger_index']}",
        f"- Validated amendment count: {summary['live_state']['validated_amendment_count']}",
        f"- Mainnet state counts: `{json.dumps(summary['counts']['mainnet_state'], sort_keys=True)}`",
        f"- Mapping confidence counts: `{json.dumps(summary['counts']['mapping_confidence'], sort_keys=True)}`",
        "",
        "## Caveat",
        "",
        summary["caveat"],
        "",
        "## Files",
        "",
        "- `amendment_status_reconciliation.csv`",
        "- `amendment_status_reconciliation.json`",
        "- `not_present_in_known_amendments.csv`",
        "- `amendment_universe.json`",
        "- `source_receipts.json`",
        "- `summary.json`",
        "- `SHA256SUMS.txt`",
    ]
    (artifact_dir / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    write_sha256s(artifact_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provenance", type=Path, default=DEFAULT_PROVENANCE)
    parser.add_argument("--artifact-dir", type=Path)
    args = parser.parse_args()
    artifact_dir = args.artifact_dir
    if artifact_dir is None:
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        artifact_dir = REPO_ROOT / "static" / "benchmarks" / f"xrpl-origination-status-{stamp}"
    build_packet(artifact_path(args.provenance), artifact_path(artifact_dir))
    print(artifact_dir)


if __name__ == "__main__":
    main()
