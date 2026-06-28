#!/usr/bin/env python3
"""Build a 10-year categorized XRPL amendment universe packet."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from build_xrpl_amendment_lifecycle_corpus import (
    SOURCES,
    build_universe,
    fetch_source,
    parse_known_amendments,
)
from build_xrpl_origination_status_packet import XLS_TO_AMENDMENTS
from xrpl_lifecycle_common import artifact_path, read_json, write_json, write_sha256s


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROVENANCE = REPO_ROOT / "static" / "benchmarks" / "xrpl-xls-provenance-20260603T230503Z"
DEFAULT_CUTOFF = "2016-06-04"


AREA_OVERRIDES = {
    "amm": "dex_amm_liquidity",
    "ticksize": "dex_amm_liquidity",
    "priceoracle": "dex_amm_liquidity",
    "immediateofferkilled": "dex_amm_liquidity",
    "accountdelete": "account_transaction_infrastructure",
    "deletableaccounts": "account_transaction_infrastructure",
    "fixemptydirmaddeletable": "account_transaction_infrastructure",
    "fixmasterkeyasregularkey": "account_transaction_infrastructure",
    "fixreducedoffersv1": "dex_amm_liquidity",
    "fixtrustlinesppermmitted": "mpt_tokenization_rwa",
    "fixxchainrewardrounding": "cross_chain_interop",
    "multiSign".lower(): "compliance_authorization_identity",
    "expandedsignerlist": "compliance_authorization_identity",
    "trustsetauth": "compliance_authorization_identity",
    "depositauth": "compliance_authorization_identity",
    "depositpreauth": "compliance_authorization_identity",
    "disallowincoming": "compliance_authorization_identity",
    "clawback": "compliance_authorization_identity",
    "deepfreeze": "compliance_authorization_identity",
    "permissioneddomains": "compliance_authorization_identity",
    "permissioneddex": "dex_amm_liquidity",
    "negativeunl": "consensus_safety_infrastructure",
    "enforceinvariants": "consensus_safety_infrastructure",
    "invariantsv1_1": "consensus_safety_infrastructure",
    "requirefullycanonicalsig": "consensus_safety_infrastructure",
    "hardenedvalidations": "consensus_safety_infrastructure",
    "shamapv2": "consensus_safety_infrastructure",
    "sorteddirectories": "consensus_safety_infrastructure",
    "multisignreserve": "fees_reserves",
    "flow": "payments_escrow_channels",
    "flowcross": "payments_escrow_channels",
    "flowv2": "payments_escrow_channels",
    "flowsortstrands": "payments_escrow_channels",
    "escrow": "payments_escrow_channels",
    "paychan": "payments_escrow_channels",
    "checks": "payments_escrow_channels",
    "checkcashmakestrustline": "payments_escrow_channels",
    "cryptoconditions": "payments_escrow_channels",
    "cryptoconditionssuite": "payments_escrow_channels",
    "suspay": "payments_escrow_channels",
    "tickets": "account_transaction_infrastructure",
    "ticketbatch": "account_transaction_infrastructure",
    "ownerpaysfee": "fees_reserves",
    "feeescrow": "fees_reserves",
    "feeescalation": "fees_reserves",
    "xrpfees": "fees_reserves",
    "nonfungibletokensv1": "nft",
    "nonfungibletokensv1_1": "nft",
    "dynamicnft": "nft",
    "nftokenmintoffer": "nft",
    "fixnftokendirv1": "nft",
    "fixnftokennegoffer": "nft",
    "mptokensv1": "mpt_tokenization_rwa",
    "mptokensv2": "mpt_tokenization_rwa",
    "dynamicmpt": "mpt_tokenization_rwa",
    "singleassetvault": "mpt_tokenization_rwa",
    "tokenescrow": "mpt_tokenization_rwa",
    "sponsor": "mpt_tokenization_rwa",
    "confidentialtransfer": "privacy_confidentiality",
    "smartescrow": "programmability_batch_contracts",
    "batch": "programmability_batch_contracts",
    "hooks": "programmability_batch_contracts",
    "xchainbridge": "cross_chain_interop",
}

CATEGORY_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("consensus_safety_infrastructure", ("invariant", "negativeunl", "validation", "shamap", "directory", "canonical signature", "amendment majority")),
    ("fees_reserves", ("fee", "reserve", "owner count", "owner reserve", "xrpfees", "fee escalation")),
    ("privacy_confidentiality", ("confidential", "privacy", "private", "zkp", "zero-knowledge")),
    ("compliance_authorization_identity", ("clawback", "freeze", "credential", "permission", "depositauth", "depositpreauth", "did", "disallowincoming", "trustsetauth", "authorized", "authorization", "sanction", "compliance", "signer")),
    ("mpt_tokenization_rwa", ("mpt", "multi-purpose token", "vault", "tokenescrow", "token escrow", "trust line", "trustline", "issued token", "issuer", "iou")),
    ("nft", ("nft", "nftoken", "nonfungibletoken", "non-fungible token", "dynamicnft")),
    ("programmability_batch_contracts", ("batch", "hook", "smartescrow", "smart escrow", "smart contract", "wasm", "plugin")),
    ("cross_chain_interop", ("xchain", "bridge", "sidechain", "cross-chain", "federator")),
    ("payments_escrow_channels", ("payment", "paychan", "payment channel", "check", "escrow", "flow", "autobridge", "direct debit")),
    ("dex_amm_liquidity", ("amm", "automated market maker", "dex", "offer", "ticksize", "order book", "priceoracle", "price oracle")),
    ("account_transaction_infrastructure", ("ticket", "account", "sequence", "delete", "transaction")),
]

INSTITUTIONAL_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("issuer_control", ("issuer", "clawback", "freeze", "deep freeze", "trustline", "trust line", "authorized", "authorization")),
    ("permissioned_access", ("permissioned", "credential", "depositauth", "depositpreauth", "disallowincoming", "kyc", "compliance")),
    ("institutional_privacy", ("confidential", "privacy", "auditor", "regulated", "institution", "compliance")),
    ("tokenization_rwa", ("mpt", "multi-purpose token", "vault", "tokenescrow", "token escrow", "rwa", "issued token")),
    ("market_structure", ("amm", "dex", "price oracle", "oracle", "lending", "loan", "vault")),
    ("enterprise_key_ops", ("signer", "multisign", "walletlocator", "hsm", "key", "delegation")),
]


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_day(value: str) -> date | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def clean_status(value: str) -> str:
    return (value or "UNKNOWN").upper().replace(":", "").split()[0] if value else "UNKNOWN"


def haystack(row: dict[str, Any]) -> str:
    return f"{row.get('name','')} {row.get('description','')} {row.get('known_status','')}".lower()


def feature_area(row: dict[str, Any]) -> str:
    text = haystack(row)
    name = str(row.get("name", "")).lower()
    if name in AREA_OVERRIDES:
        return AREA_OVERRIDES[name]
    if name.startswith("fix") or name.startswith("ticketbatch") or "fix" in name:
        return "maintenance_fix"
    for category, terms in CATEGORY_RULES:
        if any(term in text for term in terms):
            return category
    return "core_protocol_other"


def surface_flags(row: dict[str, Any]) -> list[str]:
    text = haystack(row)
    flags = [flag for flag, terms in INSTITUTIONAL_RULES if any(term in text for term in terms)]
    if str(row.get("name", "")).lower().startswith("fix"):
        flags.append("maintenance_fix")
    return sorted(set(flags))


def feature_class(row: dict[str, Any], area: str) -> str:
    status = str(row.get("known_status") or "").upper()
    name = str(row.get("name") or "")
    if "OBSOLETE" in status:
        return "obsolete_or_retired"
    if name.lower().startswith("fix") or area == "maintenance_fix":
        return "maintenance_or_bugfix"
    if area in {"compliance_authorization_identity", "mpt_tokenization_rwa", "privacy_confidentiality"}:
        return "institutional_feature"
    if area in {"dex_amm_liquidity", "payments_escrow_channels", "cross_chain_interop", "nft", "programmability_batch_contracts"}:
        return "product_feature"
    return "protocol_infrastructure"


def short_description(text: str, limit: int = 280) -> str:
    cleaned = " ".join(str(text or "").split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3].rstrip() + "..."


def load_provenance_map(provenance_dir: Path) -> dict[str, dict[str, str]]:
    path = provenance_dir / "xls_provenance.csv"
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return {row["id"].upper(): row for row in rows}


def xls_id_from_api(row: dict[str, Any], api_by_name: dict[str, dict[str, Any]]) -> str:
    api = api_by_name.get(str(row.get("name", "")).lower(), {})
    raw = str(api.get("xls") or "").strip().upper()
    if not raw:
        return ""
    if raw.startswith("XLS-"):
        parts = raw.split("-", 1)
        try:
            return f"XLS-{int(parts[1]):04d}"
        except ValueError:
            return raw
    return raw


def mapping_from_status_review() -> dict[str, list[str]]:
    out: dict[str, list[str]] = defaultdict(list)
    for xls_id, mapping in XLS_TO_AMENDMENTS.items():
        for name in mapping.get("names", []):
            out[name.lower()].append(xls_id)
    return out


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build_packet(artifact_dir: Path, provenance_dir: Path, cutoff_raw: str) -> None:
    cutoff = date.fromisoformat(cutoff_raw)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = artifact_dir / "source_bodies"
    source_ids = {"xrpscan_amendments_api", "xrpl_validated_amendments_object", "xrpl_known_amendments_md"}
    fetched = {source_id: fetch_source(source_id, SOURCES[source_id], raw_dir) for source_id in sorted(source_ids)}
    source_receipts = {source_id: item.receipt for source_id, item in fetched.items()}

    xrpscan_rows = json.loads(fetched["xrpscan_amendments_api"].body.decode("utf-8"))
    ledger_rpc = json.loads(fetched["xrpl_validated_amendments_object"].body.decode("utf-8"))
    ledger_node = ledger_rpc.get("result", {}).get("node", {})
    ledger_ids = {str(value).upper() for value in ledger_node.get("Amendments", [])}
    known = parse_known_amendments(fetched["xrpl_known_amendments_md"].body.decode("utf-8", errors="replace"))
    universe = build_universe(xrpscan_rows, ledger_ids, known)
    api_by_name = {str(row.get("name", "")).lower(): row for row in xrpscan_rows}
    provenance = load_provenance_map(provenance_dir)
    name_to_reviewed_xls = mapping_from_status_review()

    rows: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    for row in universe:
        enabled_day = parse_day(str(row.get("current_enabled_on") or ""))
        current_enabled = bool(row.get("current_enabled"))
        include = bool((enabled_day and enabled_day >= cutoff) or not current_enabled)
        area = feature_area(row)
        flags = surface_flags(row)
        api_xls = xls_id_from_api(row, api_by_name)
        reviewed_xls = ";".join(sorted(set(name_to_reviewed_xls.get(str(row.get("name", "")).lower(), []))))
        xls_id = api_xls or reviewed_xls.split(";")[0] if reviewed_xls else api_xls
        prov = provenance.get(xls_id, {}) if xls_id else {}
        out = {
            "name": row.get("name", ""),
            "amendment_id": row.get("amendment_id", ""),
            "known_status": row.get("known_status", ""),
            "current_enabled": str(current_enabled).lower(),
            "enabled_on": row.get("current_enabled_on", ""),
            "enabled_in_ledger": row.get("current_enabled_in_ledger") or "",
            "introduced_version": row.get("introduced_version", ""),
            "source_default_vote": row.get("source_default_vote", ""),
            "support_count": row.get("current_support_count") if row.get("current_support_count") is not None else "",
            "validation_count": row.get("current_validation_count") if row.get("current_validation_count") is not None else "",
            "threshold": row.get("current_threshold") if row.get("current_threshold") is not None else "",
            "feature_area": area,
            "feature_class": feature_class(row, area),
            "institutional_surface_flags": ";".join(flags),
            "institutional_surface": str(bool(flags and flags != ["maintenance_fix"])).lower(),
            "xls_id": xls_id,
            "reviewed_xls_ids": reviewed_xls,
            "xls_title": prov.get("title", ""),
            "xls_category": prov.get("category", ""),
            "xls_status": prov.get("status", ""),
            "xls_author_raw": prov.get("author_raw", ""),
            "xls_strict_author_tier": prov.get("strict_support_tier", "NO_XLS_PROVENANCE_IN_PACKET"),
            "xls_readme_url": prov.get("readme_url", ""),
            "xrpscan_xls_url": api_by_name.get(str(row.get("name", "")).lower(), {}).get("xls_url", ""),
            "description_short": short_description(row.get("description", "")),
            "included_in_10y_cut": str(include).lower(),
            "cut_reason": "enabled_since_cutoff" if enabled_day and enabled_day >= cutoff else ("current_not_enabled_surface" if not current_enabled else "enabled_before_cutoff"),
        }
        (rows if include else excluded).append(out)

    fields = [
        "name",
        "known_status",
        "current_enabled",
        "enabled_on",
        "introduced_version",
        "source_default_vote",
        "feature_area",
        "feature_class",
        "institutional_surface",
        "institutional_surface_flags",
        "xls_id",
        "xls_strict_author_tier",
        "xls_author_raw",
        "support_count",
        "validation_count",
        "threshold",
        "description_short",
        "amendment_id",
        "enabled_in_ledger",
        "reviewed_xls_ids",
        "xls_title",
        "xls_category",
        "xls_status",
        "xls_readme_url",
        "xrpscan_xls_url",
        "included_in_10y_cut",
        "cut_reason",
    ]
    rows.sort(key=lambda item: (item["enabled_on"] or "9999-99-99", item["name"]))
    excluded.sort(key=lambda item: (item["enabled_on"] or "9999-99-99", item["name"]))
    write_csv(artifact_dir / "xrpl_amendments_10y_categorized.csv", rows, fields)
    write_json(artifact_dir / "xrpl_amendments_10y_categorized.json", rows)
    write_csv(artifact_dir / "excluded_enabled_before_cutoff.csv", excluded, fields)
    write_json(artifact_dir / "source_receipts.json", source_receipts)

    category_counts = [{"feature_area": key, "count": value} for key, value in Counter(row["feature_area"] for row in rows).most_common()]
    class_counts = [{"feature_class": key, "count": value} for key, value in Counter(row["feature_class"] for row in rows).most_common()]
    status_counts = [{"known_status": key, "count": value} for key, value in Counter(row["known_status"] for row in rows).most_common()]
    author_counts = [{"xls_strict_author_tier": key, "count": value} for key, value in Counter(row["xls_strict_author_tier"] for row in rows).most_common()]
    year_counts = Counter((row["enabled_on"][:4] if row["enabled_on"] else "not_enabled") for row in rows)
    timeline = [{"year": key, "count": year_counts[key]} for key in sorted(year_counts)]
    write_csv(artifact_dir / "category_counts.csv", category_counts, ["feature_area", "count"])
    write_csv(artifact_dir / "class_counts.csv", class_counts, ["feature_class", "count"])
    write_csv(artifact_dir / "status_counts.csv", status_counts, ["known_status", "count"])
    write_csv(artifact_dir / "xls_author_tier_counts.csv", author_counts, ["xls_strict_author_tier", "count"])
    write_csv(artifact_dir / "timeline_counts.csv", timeline, ["year", "count"])

    summary = {
        "generated_at": utc_now(),
        "cutoff_date": cutoff_raw,
        "definition": "Rows are official XRPL Known Amendments joined to XRPSCAN and the validated-ledger Amendments object. The 10-year packet includes amendments enabled on or after the cutoff plus current not-enabled known amendments.",
        "source_receipts": source_receipts,
        "counts": {
            "known_amendment_rows": len(universe),
            "included_10y_rows": len(rows),
            "excluded_enabled_before_cutoff_rows": len(excluded),
            "enabled_included_rows": sum(1 for row in rows if row["current_enabled"] == "true"),
            "current_not_enabled_rows": sum(1 for row in rows if row["current_enabled"] == "false"),
            "institutional_surface_rows": sum(1 for row in rows if row["institutional_surface"] == "true"),
            "with_xls_provenance_rows": sum(1 for row in rows if row["xls_strict_author_tier"] != "NO_XLS_PROVENANCE_IN_PACKET"),
        },
        "feature_area_counts": Counter(row["feature_area"] for row in rows),
        "feature_class_counts": Counter(row["feature_class"] for row in rows),
        "known_status_counts": Counter(row["known_status"] for row in rows),
        "timeline_counts": year_counts,
        "xls_strict_author_tier_counts": Counter(row["xls_strict_author_tier"] for row in rows),
        "excluded_enabled_before_cutoff": [row["name"] for row in excluded],
    }
    write_json(artifact_dir / "summary.json", summary)

    report = [
        "# XRPL Amendments 10-Year Categorized Universe",
        "",
        f"Generated: {summary['generated_at']}",
        f"Cutoff: {cutoff_raw}",
        "",
        "## Definition",
        "",
        summary["definition"],
        "",
        "## Counts",
        "",
        f"- Official Known Amendments rows: {summary['counts']['known_amendment_rows']}",
        f"- Included 10-year rows: {summary['counts']['included_10y_rows']}",
        f"- Enabled rows in cut: {summary['counts']['enabled_included_rows']}",
        f"- Current not-enabled rows in cut: {summary['counts']['current_not_enabled_rows']}",
        f"- Excluded enabled-before-cutoff rows: {summary['counts']['excluded_enabled_before_cutoff_rows']}",
        f"- Institutional-surface rows: {summary['counts']['institutional_surface_rows']}",
        f"- Rows with XLS provenance join: {summary['counts']['with_xls_provenance_rows']}",
        "",
        "## Top Feature Areas",
        "",
        *[f"- {row['feature_area']}: {row['count']}" for row in category_counts],
        "",
        "## Files",
        "",
        "- `xrpl_amendments_10y_categorized.csv`",
        "- `xrpl_amendments_10y_categorized.json`",
        "- `category_counts.csv`",
        "- `class_counts.csv`",
        "- `status_counts.csv`",
        "- `timeline_counts.csv`",
        "- `xls_author_tier_counts.csv`",
        "- `excluded_enabled_before_cutoff.csv`",
        "- `source_receipts.json`",
        "- `summary.json`",
        "- `SHA256SUMS.txt`",
    ]
    (artifact_dir / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (artifact_dir / "index.html").write_text(
        "\n".join(
            [
                "<!doctype html>",
                "<meta charset=\"utf-8\">",
                "<title>XRPL Amendments 10-Year Categorized Universe</title>",
                "<h1>XRPL Amendments 10-Year Categorized Universe</h1>",
                "<ul>",
                "<li><a href=\"REPORT.md\">REPORT.md</a></li>",
                "<li><a href=\"summary.json\">summary.json</a></li>",
                "<li><a href=\"xrpl_amendments_10y_categorized.csv\">xrpl_amendments_10y_categorized.csv</a></li>",
                "<li><a href=\"category_counts.csv\">category_counts.csv</a></li>",
                "<li><a href=\"SHA256SUMS.txt\">SHA256SUMS.txt</a></li>",
                "</ul>",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    write_sha256s(artifact_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path)
    parser.add_argument("--provenance", type=Path, default=DEFAULT_PROVENANCE)
    parser.add_argument("--cutoff", default=DEFAULT_CUTOFF)
    args = parser.parse_args()
    artifact_dir = args.artifact_dir
    if artifact_dir is None:
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        artifact_dir = REPO_ROOT / "static" / "benchmarks" / f"xrpl-amendments-10y-categorized-{stamp}"
    build_packet(artifact_path(artifact_dir), artifact_path(args.provenance), args.cutoff)
    print(artifact_dir)


if __name__ == "__main__":
    main()
