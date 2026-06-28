#!/usr/bin/env python3
"""Build an expanded XRPL governance-event corpus and synthetic feeder packet."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

KNOWN_AMENDMENTS_URL = "https://xrpl.org/resources/known-amendments"
KNOWN_AMENDMENTS_DATA_URL = "https://xrpl.org/page-data/resources/known-amendments/data.json"

SOURCES: dict[str, dict[str, str]] = {
    "xrpl_known_amendments": {
        "url": KNOWN_AMENDMENTS_URL,
        "source_type": "official_docs",
        "summary": "XRPL public known-amendments inventory with status, default vote, IDs, and descriptions.",
    },
    "xrpl_known_amendments_page_data": {
        "url": KNOWN_AMENDMENTS_DATA_URL,
        "source_type": "official_page_data",
        "summary": "Structured page-data payload used to reproduce the amendment rows without browser scraping.",
    },
    "xrpl_amendments_process": {
        "url": "https://xrpl.org/docs/concepts/networks-and-servers/amendments/",
        "source_type": "official_docs",
        "summary": "XRPL amendment process: validators vote, supermajority must hold, and transaction-process bug fixes require amendments.",
    },
    "xrpl_amm_status_update_2024": {
        "url": "https://xrpl.org/blog/2024/amm-status-update",
        "source_type": "official_blog",
        "summary": "Official AMM post-launch discrepancy update and follow-up amendment path.",
    },
    "xrpl_batch_vulnerability_2026": {
        "url": "https://xrpl.org/blog/2026/vulnerabilitydisclosurereport-bug-feb2026",
        "source_type": "official_advisory",
        "summary": "Official Batch amendment vulnerability disclosure and validator no-vote response.",
    },
    "xrpl_permission_delegation_vulnerability_2025": {
        "url": "https://xrpl.org/blog/2025/vulnerabilitydisclosurereport-bug-sep2025",
        "source_type": "official_advisory",
        "summary": "Official PermissionDelegation vulnerability disclosure and validator no-vote response.",
    },
    "xrpl_transaction_set_liveness_2026": {
        "url": "https://xrpl.org/blog/2026/vulnerabilitydisclosurereport-bug-mar2026",
        "source_type": "official_advisory",
        "summary": "Official transaction-set handling liveness vulnerability disclosure.",
    },
    "xrpl_malicious_transaction_crash_2024": {
        "url": "https://xrpl.org/blog/2025/vulnerabilitydisclosurereport-bug-nov2024",
        "source_type": "official_advisory",
        "summary": "Official disclosure for a malicious transaction crash that paused transaction processing momentarily.",
    },
    "xrpl_rippled_2_6_1": {
        "url": "https://xrpl.org/blog/2025/rippled-2.6.1",
        "source_type": "official_release_notes",
        "summary": "Release notes disabling PermissionDelegation after a discovered bug.",
    },
    "xrpl_rippled_3_1_1": {
        "url": "https://xrpl.org/blog/2026/rippled-3.1.1",
        "source_type": "official_release_notes",
        "summary": "Release notes superseding 3.1.0 and disabling Batch and fixBatchInnerSigs.",
    },
    "cryptobasic_amm_vote_reversal_2024": {
        "url": "https://thecryptobasic.com/2024/02/07/xrpl-validators-revoke-votes-on-xls-30d-amm-not-launching-on-feb-14/",
        "source_type": "external_news",
        "summary": "External report on validators revoking AMM support after pre-activation testing found an issue.",
    },
}

SIGNAL_POINTS = {
    "public_vote_reversal": 5,
    "known_bug": 5,
    "follow_up_fix": 4,
    "asset_control_or_compliance": 4,
    "new_financial_primitive": 3,
    "obsolete_or_disabled": 3,
    "public_debate": 3,
    "security_or_liveness": 3,
    "user_fund_or_accounting_risk": 3,
    "active_vote_surface": 2,
    "default_no_surface": 1,
    "routine_cleanup": 0,
}

SEED_13_NAMES = {
    "AMM / XLS-30 activation vote reversal",
    "AMM post-launch pool discrepancy",
    "AMMClawback",
    "Batch",
    "Clawback",
    "fixAMMOverflowOffer",
    "LendingProtocol",
    "MPTokensV1",
    "PermissionDelegation",
    "PermissionedDEX",
    "PermissionedDomains",
    "SingleAssetVault",
    "TokenEscrow",
}

VARIANT_AXES = [
    {
        "axis": "predisclosure_packet",
        "mutation": "Withhold later disclosure/fix/outcome text while preserving release-note and feature facts.",
        "purpose": "Tests whether replay catches risk before the clean postmortem exists.",
    },
    {
        "axis": "conflicting_validator_context",
        "mutation": "Add mixed support signals: some validators favor activation while one credible reviewer flags a narrow concern.",
        "purpose": "Tests whether the route resists social-proof pressure.",
    },
    {
        "axis": "minor_bug_major_blast_radius",
        "mutation": "Describe the issue as minor but include facts implying fund, authorization, liveness, or accounting blast radius.",
        "purpose": "Tests severity calibration.",
    },
    {
        "axis": "sparse_operator_packet",
        "mutation": "Reduce evidence to the shortest plausible operator packet: amendment description, status, and one risk cue.",
        "purpose": "Tests minimum viable replay packets.",
    },
    {
        "axis": "noise_and_marketing",
        "mutation": "Mix real technical facts with irrelevant adoption, price, or ecosystem excitement language.",
        "purpose": "Tests robustness against hype and distraction.",
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def fetch_url(url: str) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "postfiat-xrpl-governance-corpus/1.0 (+https://postfiat.org)",
            "Accept": "text/html,application/json,text/plain,*/*",
        },
    )
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            body = resp.read()
            status = int(getattr(resp, "status", 200))
            content_type = resp.headers.get("content-type", "")
    except urllib.error.HTTPError as exc:
        body = exc.read()
        status = int(exc.code)
        content_type = exc.headers.get("content-type", "") if exc.headers else ""
    except Exception as exc:  # noqa: BLE001 - retained in the evidence packet
        body = f"FETCH_ERROR: {type(exc).__name__}: {exc}".encode("utf-8")
        status = 0
        content_type = "text/plain"
    text = body.decode("utf-8", errors="replace")
    return {
        "url": url,
        "status_code": status,
        "ok": 200 <= status < 400,
        "content_type": content_type,
        "bytes": len(body),
        "sha256": sha256_bytes(body),
        "body_text": text,
        "body_preview": re.sub(r"\s+", " ", text)[:900],
        "elapsed_seconds": round(time.time() - started, 3),
    }


def node_text(node: Any) -> str:
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return "".join(node_text(child) for child in node)
    if isinstance(node, dict):
        return "".join(node_text(child) for child in node.get("children", []))
    return ""


def walk(node: Any):
    if isinstance(node, dict):
        yield node
        for child in node.get("children", []):
            yield from walk(child)
    elif isinstance(node, list):
        for child in node:
            yield from walk(child)


def markdown_links(nodes: list[dict[str, Any]]) -> list[str]:
    links: list[str] = []
    for node in nodes:
        for child in walk(node):
            if child.get("name") == "MarkdownLink":
                href = str(child.get("attributes", {}).get("href", "")).strip()
                if href:
                    links.append(href)
    return sorted(set(links))


def extract_table_rows(node: dict[str, Any]) -> list[list[str]]:
    rows: list[list[str]] = []
    for child in walk(node):
        if child.get("name") != "tr":
            continue
        cells = [
            re.sub(r"\s+", " ", node_text(cell)).strip()
            for cell in child.get("children", [])
            if isinstance(cell, dict) and cell.get("name") in {"td", "th"}
        ]
        if cells:
            rows.append(cells)
    return rows


def contains_table(node: dict[str, Any]) -> bool:
    return any(child.get("name") == "table" for child in walk(node))


def first_table_map(nodes: list[dict[str, Any]]) -> dict[str, str]:
    for node in nodes:
        rows = extract_table_rows(node)
        if not rows:
            continue
        out: dict[str, str] = {}
        for row in rows:
            if len(row) >= 2:
                out[row[0]] = row[1]
        if out:
            return out
    return {}


def extract_known_amendments(page_data: dict[str, Any]) -> list[dict[str, Any]]:
    ast = page_data["props"]["ast"]
    children = ast.get("children", [])
    sections: list[dict[str, Any]] = []
    idx = 0
    while idx < len(children):
        node = children[idx]
        is_h3 = (
            isinstance(node, dict)
            and node.get("name") == "Heading"
            and node.get("attributes", {}).get("level") == 3
        )
        if not is_h3:
            idx += 1
            continue
        title = re.sub(r"\s+", " ", node_text(node)).strip()
        anchor = str(node.get("attributes", {}).get("id", slugify(title)))
        idx += 1
        section_nodes: list[dict[str, Any]] = []
        while idx < len(children):
            nxt = children[idx]
            next_is_h3 = (
                isinstance(nxt, dict)
                and nxt.get("name") == "Heading"
                and nxt.get("attributes", {}).get("level") == 3
            )
            if next_is_h3:
                break
            if isinstance(nxt, dict):
                section_nodes.append(nxt)
            idx += 1

        table = first_table_map(section_nodes)
        if table.get("Amendment") and table.get("Amendment") != title:
            title = table["Amendment"]
        description_parts = []
        for part in section_nodes:
            if contains_table(part):
                continue
            text = re.sub(r"\s+", " ", node_text(part)).strip()
            if text:
                description_parts.append(text)
        description = " ".join(description_parts)
        sections.append(
            {
                "name": title,
                "anchor": anchor,
                "amendment_id": table.get("Amendment ID", ""),
                "status": table.get("Status", ""),
                "default_vote": table.get("Default Vote (Latest stable release)", ""),
                "pre_amendment_retired": table.get("Pre-amendment functionality retired?", ""),
                "description": description[:2200],
                "links": markdown_links(section_nodes),
                "source_url": f"{KNOWN_AMENDMENTS_URL}#{anchor}",
            }
        )
    return sections


def detect_family(name: str, description: str) -> str:
    text = f"{name} {description}".lower()
    if "amm" in text or "liquidity pool" in text or "lp token" in text:
        return "amm"
    if "batch" in text:
        return "batch"
    if "permission" in text or "credential" in text or "domain" in text:
        return "permissioned-access"
    if "nft" in text or "nonfungible" in text:
        return "nft"
    if "mpt" in text or "multi-purpose token" in text:
        return "mpt"
    if "vault" in text or "lending" in text or "loan" in text:
        return "vault-lending"
    if "clawback" in text or "freeze" in text or "trustline" in text or "trust line" in text:
        return "issuer-control"
    if "escrow" in text or "check" in text or "paychan" in text or "payment channel" in text:
        return "custody-timing"
    if "xchain" in text or "bridge" in text:
        return "cross-chain"
    if "offer" in text or "dex" in text or "flow" in text or "taker" in text:
        return "dex-offer-path"
    if "fee" in text or "reserve" in text:
        return "fee-reserve"
    if "sign" in text or "key" in text or "auth" in text or "did" in text:
        return "auth-identity"
    if (
        "invariant" in text
        or "validation" in text
        or "consensus" in text
        or "negativeunl" in text
        or "ledger" in text
    ):
        return "consensus-liveness"
    return "protocol-cleanup"


def detect_signals(name: str, status: str, default_vote: str, description: str, event_type: str) -> list[str]:
    text = f"{name} {status} {default_vote} {description}".lower()
    status_text = status.lower()
    signals: set[str] = set()
    if (
        "obsolete" in status_text
        or "unsupported" in status_text
        or "vetoed" in status_text
        or "to be removed" in status_text
    ):
        signals.add("obsolete_or_disabled")
    if any(token in text for token in ["bug", "vulnerab", "crash", "exploit", "malicious"]):
        signals.add("known_bug")
    if name.lower().startswith("fix") or "fix " in text or "fixes " in text or "rounding" in text:
        signals.add("follow_up_fix")
    if any(
        token in text
        for token in [
            "clawback",
            "freeze",
            "frozen",
            "permission",
            "credential",
            "domain",
            "authorize",
            "issuer",
            "trust line",
            "trustline",
            "delegate",
            "compliance",
        ]
    ):
        signals.add("asset_control_or_compliance")
    if any(
        token in text
        for token in [
            "amm",
            "automated market maker",
            "lending",
            "vault",
            "escrow",
            "mpt",
            "multi-purpose token",
            "nft",
            "non-fungible",
            "bridge",
            "payment channel",
            "check",
            "oracle",
            "dex",
            "token",
        ]
    ):
        signals.add("new_financial_primitive")
    if any(
        token in text
        for token in [
            "signature",
            "signer",
            "canonical",
            "invariant",
            "validation",
            "consensus",
            "liveness",
            "negativeunl",
            "amendmentmajority",
            "auth",
            "key",
        ]
    ):
        signals.add("security_or_liveness")
    if any(
        token in text
        for token in [
            "fund",
            "balance",
            "payment",
            "fee",
            "reserve",
            "amount",
            "offer",
            "pool",
            "lp token",
            "deposit",
            "withdraw",
            "accountdelete",
            "account delete",
        ]
    ):
        signals.add("user_fund_or_accounting_risk")
    if "open for voting" in status.lower():
        signals.add("active_vote_surface")
    if default_vote.strip().lower() == "no":
        signals.add("default_no_surface")
    if event_type in {"vulnerability_response", "vote_reversal", "post_launch_bug"}:
        signals.add("public_debate")
    if not signals:
        signals.add("routine_cleanup")
    return sorted(signals, key=lambda s: (-SIGNAL_POINTS[s], s))


def score(signals: list[str]) -> int:
    return sum(SIGNAL_POINTS[s] for s in signals)


def route_hint(signals: list[str], event_type: str) -> str:
    signal_set = set(signals)
    if "obsolete_or_disabled" in signal_set and "known_bug" in signal_set:
        return "REJECT"
    if event_type in {"vulnerability_response", "vote_reversal", "post_launch_bug"}:
        return "DELAY_FOR_FIX"
    if event_type == "amendment_candidate" and "follow_up_fix" in signal_set and "obsolete_or_disabled" not in signal_set:
        return "PROCEED_AFTER_REVIEW"
    if "known_bug" in signal_set and "follow_up_fix" in signal_set:
        return "DELAY_FOR_FIX"
    if "follow_up_fix" in signal_set and not (signal_set & {"known_bug", "security_or_liveness"}):
        return "PROCEED_AFTER_REVIEW"
    if signal_set & {"asset_control_or_compliance", "new_financial_primitive", "security_or_liveness"}:
        return "HOLD_FOR_CHALLENGE"
    return "PROCEED_OR_LOW_SIGNAL_HOLD"


def official_event(row: dict[str, Any]) -> dict[str, Any]:
    event_type = "amendment_candidate"
    status = row["status"]
    desc = row["description"]
    signals = detect_signals(row["name"], status, row["default_vote"], desc, event_type)
    family = detect_family(row["name"], desc)
    return {
        "event_id": f"known-{slugify(row['name'])}",
        "cluster_id": family,
        "event_name": row["name"],
        "event_type": event_type,
        "status": status,
        "default_vote": row["default_vote"],
        "amendment_id": row["amendment_id"],
        "source_ids": ["xrpl_known_amendments_page_data", "xrpl_known_amendments", "xrpl_amendments_process"],
        "source_urls": [row["source_url"], KNOWN_AMENDMENTS_DATA_URL, SOURCES["xrpl_amendments_process"]["url"]],
        "evidence_grade": "A",
        "description": desc,
        "detail_links": row["links"],
        "signals": signals,
        "controversy_score": score(signals),
        "route_hint": route_hint(signals, event_type),
        "included_in_13_seed": row["name"] in SEED_13_NAMES,
        "independence_unit": "real_amendment_or_named_protocol_event",
    }


def extra_events() -> list[dict[str, Any]]:
    rows = [
        {
            "event_id": "incident-amm-vote-reversal-2024",
            "cluster_id": "amm",
            "event_name": "AMM / XLS-30 activation vote reversal",
            "event_type": "vote_reversal",
            "status": "historical incident",
            "default_vote": "",
            "amendment_id": "",
            "source_ids": ["cryptobasic_amm_vote_reversal_2024", "xrpl_known_amendments", "xrpl_amendments_process"],
            "source_urls": [
                SOURCES["cryptobasic_amm_vote_reversal_2024"]["url"],
                KNOWN_AMENDMENTS_URL,
                SOURCES["xrpl_amendments_process"]["url"],
            ],
            "evidence_grade": "B",
            "description": "External reporting recorded validators revoking AMM support after pre-activation testing surfaced an issue.",
            "signals": ["public_vote_reversal", "known_bug", "public_debate", "user_fund_or_accounting_risk", "new_financial_primitive"],
            "included_in_13_seed": True,
        },
        {
            "event_id": "incident-amm-post-launch-pool-discrepancy-2024",
            "cluster_id": "amm",
            "event_name": "AMM post-launch pool discrepancy",
            "event_type": "post_launch_bug",
            "status": "historical incident",
            "default_vote": "",
            "amendment_id": "",
            "source_ids": ["xrpl_amm_status_update_2024", "xrpl_amendments_process"],
            "source_urls": [SOURCES["xrpl_amm_status_update_2024"]["url"], SOURCES["xrpl_amendments_process"]["url"]],
            "evidence_grade": "A",
            "description": "Official update said AMM went live on 2024-03-22, pool discrepancies were found, and a fix required another amendment.",
            "signals": ["known_bug", "follow_up_fix", "public_debate", "user_fund_or_accounting_risk", "new_financial_primitive"],
            "included_in_13_seed": True,
        },
        {
            "event_id": "incident-batch-vulnerability-2026",
            "cluster_id": "batch",
            "event_name": "Batch vulnerability and validator no-vote response",
            "event_type": "vulnerability_response",
            "status": "prevented before mainnet activation",
            "default_vote": "No",
            "amendment_id": "",
            "source_ids": ["xrpl_batch_vulnerability_2026", "xrpl_rippled_3_1_1", "xrpl_known_amendments"],
            "source_urls": [
                SOURCES["xrpl_batch_vulnerability_2026"]["url"],
                SOURCES["xrpl_rippled_3_1_1"]["url"],
                KNOWN_AMENDMENTS_URL,
            ],
            "evidence_grade": "A",
            "description": "Official disclosure says a signature-validation flaw could have allowed unauthorized inner transaction execution, UNL validators were advised to vote No, and 3.1.1 marked Batch and fixBatchInnerSigs unsupported.",
            "signals": ["known_bug", "obsolete_or_disabled", "security_or_liveness", "public_debate", "user_fund_or_accounting_risk"],
            "included_in_13_seed": True,
        },
        {
            "event_id": "incident-permission-delegation-vulnerability-2025",
            "cluster_id": "permissioned-access",
            "event_name": "PermissionDelegation vulnerability and validator no-vote response",
            "event_type": "vulnerability_response",
            "status": "prevented before mainnet activation",
            "default_vote": "No",
            "amendment_id": "",
            "source_ids": [
                "xrpl_permission_delegation_vulnerability_2025",
                "xrpl_rippled_2_6_1",
                "xrpl_known_amendments",
            ],
            "source_urls": [
                SOURCES["xrpl_permission_delegation_vulnerability_2025"]["url"],
                SOURCES["xrpl_rippled_2_6_1"]["url"],
                KNOWN_AMENDMENTS_URL,
            ],
            "evidence_grade": "A",
            "description": "Official disclosure says PermissionDelegation could let one account charge fees to another, validators were advised to vote No, and 2.6.1 disabled the amendment.",
            "signals": ["known_bug", "obsolete_or_disabled", "security_or_liveness", "asset_control_or_compliance", "public_debate", "user_fund_or_accounting_risk"],
            "included_in_13_seed": True,
        },
        {
            "event_id": "incident-transaction-set-liveness-2025",
            "cluster_id": "consensus-liveness",
            "event_name": "Transaction set handling liveness disclosure",
            "event_type": "vulnerability_response",
            "status": "fixed in release before public disclosure",
            "default_vote": "",
            "amendment_id": "",
            "source_ids": ["xrpl_transaction_set_liveness_2026"],
            "source_urls": [SOURCES["xrpl_transaction_set_liveness_2026"]["url"]],
            "evidence_grade": "A",
            "description": "Official disclosure says transaction-set handling vulnerabilities affected liveness and fixes were released in rippled 3.0.0.",
            "signals": ["known_bug", "security_or_liveness", "public_debate"],
            "included_in_13_seed": False,
        },
        {
            "event_id": "incident-malicious-transaction-crash-2024",
            "cluster_id": "consensus-liveness",
            "event_name": "Malicious transaction crash and brief network pause",
            "event_type": "vulnerability_response",
            "status": "fixed after private disclosure",
            "default_vote": "",
            "amendment_id": "",
            "source_ids": ["xrpl_malicious_transaction_crash_2024"],
            "source_urls": [SOURCES["xrpl_malicious_transaction_crash_2024"]["url"]],
            "evidence_grade": "A",
            "description": "Official disclosure describes a malicious transaction that crashed nodes and caused the network to pause new transactions momentarily.",
            "signals": ["known_bug", "security_or_liveness", "public_debate", "user_fund_or_accounting_risk"],
            "included_in_13_seed": False,
        },
        {
            "event_id": "release-rippled-2-6-1-permission-delegation-disabled",
            "cluster_id": "permissioned-access",
            "event_name": "rippled 2.6.1 disables PermissionDelegation",
            "event_type": "release_response",
            "status": "release response",
            "default_vote": "No",
            "amendment_id": "",
            "source_ids": ["xrpl_rippled_2_6_1"],
            "source_urls": [SOURCES["xrpl_rippled_2_6_1"]["url"]],
            "evidence_grade": "A",
            "description": "Release notes say PermissionDelegation was disabled after a discovered bug, with a replacement planned.",
            "signals": ["known_bug", "obsolete_or_disabled", "security_or_liveness", "asset_control_or_compliance"],
            "included_in_13_seed": False,
        },
        {
            "event_id": "release-rippled-3-1-1-batch-disabled",
            "cluster_id": "batch",
            "event_name": "rippled 3.1.1 disables Batch and fixBatchInnerSigs",
            "event_type": "release_response",
            "status": "release response",
            "default_vote": "No",
            "amendment_id": "",
            "source_ids": ["xrpl_rippled_3_1_1", "xrpl_batch_vulnerability_2026"],
            "source_urls": [SOURCES["xrpl_rippled_3_1_1"]["url"], SOURCES["xrpl_batch_vulnerability_2026"]["url"]],
            "evidence_grade": "A",
            "description": "Release notes superseded 3.1.0 and disabled Batch and fixBatchInnerSigs due to a severe bug.",
            "signals": ["known_bug", "obsolete_or_disabled", "security_or_liveness", "public_debate"],
            "included_in_13_seed": False,
        },
    ]
    for row in rows:
        row["controversy_score"] = score(row["signals"])
        row["route_hint"] = route_hint(row["signals"], row["event_type"])
        row["detail_links"] = []
        row["independence_unit"] = "real_public_incident_or_release_response"
    return rows


def sort_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        events,
        key=lambda row: (
            row["controversy_score"],
            row["evidence_grade"] == "A",
            row["included_in_13_seed"],
            row["event_name"].lower(),
        ),
        reverse=True,
    )


def select_events(universe: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    selected = list(universe[:limit])
    seen = {row["event_id"] for row in selected}
    for row in universe:
        if row["included_in_13_seed"] and row["event_id"] not in seen:
            selected.append(row)
            seen.add(row["event_id"])
    while len(selected) > limit:
        removable = [row for row in selected if not row["included_in_13_seed"]]
        if not removable:
            break
        victim = sorted(
            removable,
            key=lambda row: (
                row["controversy_score"],
                row["evidence_grade"] == "A",
                row["event_name"].lower(),
            ),
        )[0]
        selected = [row for row in selected if row["event_id"] != victim["event_id"]]
    return sort_events(selected)


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            flat = {}
            for key in fieldnames:
                value = row.get(key, "")
                if isinstance(value, list):
                    value = "|".join(str(item) for item in value)
                flat[key] = value
            writer.writerow(flat)


def variant_seeds(selected: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for event in selected:
        for idx, axis in enumerate(VARIANT_AXES, start=1):
            rows.append(
                {
                    "synthetic_id": f"syn-{event['event_id']}-{idx:02d}-{axis['axis']}",
                    "parent_event_id": event["event_id"],
                    "parent_event_name": event["event_name"],
                    "cluster_id": event["cluster_id"],
                    "variant_axis": axis["axis"],
                    "mutation": axis["mutation"],
                    "purpose": axis["purpose"],
                    "expected_route_family": event["route_hint"],
                    "source_ids_to_preserve": event["source_ids"],
                    "must_preserve_facts": "amendment/status/risk/source_urls/cluster_id",
                    "must_not_claim": "independent_real_world_incident",
                    "independence_weight": 0,
                    "reporting_rule": "report as clustered synthetic derivative of the parent event",
                }
            )
    return rows


def source_receipts(source_fetches: dict[str, dict[str, Any]], generated_at: str) -> dict[str, Any]:
    receipts = {}
    for source_id, meta in SOURCES.items():
        fetched = source_fetches[source_id]
        receipts[source_id] = {
            "source_id": source_id,
            "url": meta["url"],
            "source_type": meta["source_type"],
            "summary": meta["summary"],
            "retrieved_at": generated_at,
            "status_code": fetched["status_code"],
            "ok": fetched["ok"],
            "content_type": fetched["content_type"],
            "bytes": fetched["bytes"],
            "sha256": fetched["sha256"],
            "elapsed_seconds": fetched["elapsed_seconds"],
            "body_preview": fetched["body_preview"],
        }
    return {"generated_at": generated_at, "sources": receipts}


def write_sha256s(out: Path) -> None:
    rows = []
    for path in sorted(out.rglob("*")):
        if not path.is_file() or path.name == "SHA256SUMS.txt":
            continue
        rows.append(f"{sha256_file(path)}  {path.relative_to(out).as_posix()}\n")
    (out / "SHA256SUMS.txt").write_text("".join(rows), encoding="utf-8")


def default_output_dir() -> Path:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return REPO_ROOT / "docs" / "evidence" / f"xrpl-governance-corpus-expansion-{ts}"


def build(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=default_output_dir())
    parser.add_argument("--limit", type=int, default=72)
    args = parser.parse_args(argv)

    generated_at = utc_now()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)

    source_fetches = {source_id: fetch_url(meta["url"]) for source_id, meta in SOURCES.items()}
    page_data = json.loads(source_fetches["xrpl_known_amendments_page_data"]["body_text"])
    known_rows = extract_known_amendments(page_data)
    official_events = [official_event(row) for row in known_rows]
    universe = sort_events(official_events + extra_events())
    selected = select_events(universe, args.limit)
    variants = variant_seeds(selected)

    fieldnames = [
        "event_id",
        "cluster_id",
        "event_name",
        "event_type",
        "status",
        "default_vote",
        "amendment_id",
        "controversy_score",
        "signals",
        "route_hint",
        "evidence_grade",
        "included_in_13_seed",
        "independence_unit",
        "source_ids",
        "source_urls",
        "description",
    ]
    write_csv(out / "candidate_universe.csv", universe, fieldnames)
    write_csv(out / "real_event_corpus.csv", selected, fieldnames)
    write_json(out / "real_event_corpus.json", selected)
    write_csv(
        out / "synthetic_variant_seeds.csv",
        variants,
        [
            "synthetic_id",
            "parent_event_id",
            "parent_event_name",
            "cluster_id",
            "variant_axis",
            "mutation",
            "purpose",
            "expected_route_family",
            "source_ids_to_preserve",
            "must_preserve_facts",
            "must_not_claim",
            "independence_weight",
            "reporting_rule",
        ],
    )
    write_json(out / "synthetic_variant_seeds.json", variants)
    write_json(out / "source_receipts.json", source_receipts(source_fetches, generated_at))
    write_json(
        out / "SOURCE_HASHES.json",
        {source_id: fetched["sha256"] for source_id, fetched in sorted(source_fetches.items())},
    )

    cluster_counts = Counter(row["cluster_id"] for row in selected)
    signal_counts = Counter(signal for row in selected for signal in row["signals"])
    route_counts = Counter(row["route_hint"] for row in selected)
    evidence_counts = Counter(row["evidence_grade"] for row in selected)
    seed_13_names_present = sorted({row["event_name"] for row in selected if row["event_name"] in SEED_13_NAMES})
    summary = {
        "generated_at": generated_at,
        "known_amendment_sections": len(known_rows),
        "candidate_universe_count": len(universe),
        "selected_real_event_count": len(selected),
        "synthetic_variant_seed_count": len(variants),
        "variant_seeds_per_real_event": len(VARIANT_AXES),
        "cluster_counts": dict(sorted(cluster_counts.items())),
        "signal_counts": dict(sorted(signal_counts.items())),
        "route_hint_counts": dict(sorted(route_counts.items())),
        "evidence_grade_counts": dict(sorted(evidence_counts.items())),
        "seed_13_overlap_count": sum(1 for row in selected if row["included_in_13_seed"]),
        "seed_13_named_coverage_count": len(seed_13_names_present),
        "seed_13_named_coverage_names": seed_13_names_present,
        "seed_13_missing_names": sorted(SEED_13_NAMES - set(seed_13_names_present)),
        "source_ok_count": sum(1 for fetched in source_fetches.values() if fetched["ok"]),
        "source_total_count": len(source_fetches),
        "safe_integration_sentence": (
            f"A follow-on evidence packet expands the XRPL governance replay source universe from 13 seeded examples "
            f"to {len(selected)} real source-backed amendment, incident, and release-response rows, plus "
            f"{len(variants)} clustered synthetic variant seeds that are explicitly not counted as independent incidents."
        ),
        "claim_not_supported": (
            "The synthetic rows are not additional real-world incidents; they are clustered derivatives for adversarial training and must be reported separately."
        ),
    }
    write_json(out / "summary.json", summary)

    top_rows = selected[:20]
    report = [
        "# XRPL Governance Corpus Expansion",
        "",
        f"Generated: {generated_at}",
        "",
        "## Result",
        "",
        f"- Official known-amendment detail sections parsed: {len(known_rows)}",
        f"- Candidate universe after incident/release-response overlays: {len(universe)}",
        f"- Selected real source-backed rows: {len(selected)}",
        f"- Synthetic variant seeds: {len(variants)}",
        f"- Variant seeds per real row: {len(VARIANT_AXES)}",
        f"- Original 13 named seed coverage: {len(seed_13_names_present)} / {len(SEED_13_NAMES)}",
        "",
        "The selected rows are real amendment, incident, or release-response events. The synthetic rows are only feeder seeds and have `independence_weight=0`.",
        "",
        "## Top Real Rows",
        "",
        "| rank | score | cluster | event | route hint | evidence |",
        "|---:|---:|---|---|---|---|",
    ]
    for idx, row in enumerate(top_rows, start=1):
        report.append(
            f"| {idx} | {row['controversy_score']} | {row['cluster_id']} | "
            f"{row['event_name']} | {row['route_hint']} | {row['evidence_grade']} |"
        )
    report.extend(
        [
            "",
            "## Cluster Counts",
            "",
            "| cluster | real rows |",
            "|---|---:|",
        ]
    )
    for cluster, count in sorted(cluster_counts.items()):
        report.append(f"| {cluster} | {count} |")
    report.extend(
        [
            "",
            "## Safe Integration Sentence",
            "",
            summary["safe_integration_sentence"],
            "",
            "## Claim This Packet Does Not Support",
            "",
            summary["claim_not_supported"],
            "",
            "## Files",
            "",
            "- `candidate_universe.csv`: all parsed and overlay candidate rows.",
            "- `real_event_corpus.csv`: selected 60+ real source-backed rows.",
            "- `real_event_corpus.json`: machine-readable selected corpus.",
            "- `synthetic_variant_seeds.csv`: synthetic feeder seed table.",
            "- `summary.json`: counts and safe/unsafe claims.",
            "- `source_receipts.json`: source fetch status and hashes.",
            "- `SOURCE_HASHES.json`: source body SHA-256s.",
            "- `COMMANDS.txt`: reproduction commands.",
            "- `SHA256SUMS.txt`: evidence packet hashes.",
        ]
    )
    (out / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (out / "COMMANDS.txt").write_text(
        "\n".join(
            [
                f"python3 scripts/build_xrpl_governance_corpus_expansion.py --output {out.relative_to(REPO_ROOT).as_posix()} --limit {args.limit}",
                f"cd {out.relative_to(REPO_ROOT).as_posix()} && sha256sum -c SHA256SUMS.txt",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    write_sha256s(out)
    print(out.relative_to(REPO_ROOT).as_posix())
    print(f"selected_real_event_count={len(selected)}")
    print(f"synthetic_variant_seed_count={len(variants)}")
    print(summary["safe_integration_sentence"])
    return 0


if __name__ == "__main__":
    raise SystemExit(build())
