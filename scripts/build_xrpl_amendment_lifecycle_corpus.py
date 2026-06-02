#!/usr/bin/env python3
"""Build a lane-separated XRPL amendment lifecycle replay corpus."""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from xrpl_lifecycle_common import (
    LANE_ALLOWED_LABELS,
    LANES,
    artifact_path,
    clean_markdown,
    sha_json,
    slugify,
    utc_now,
    write_json,
    write_sha256s,
)


AMENDMENTS_OBJECT_INDEX = "7DB0788C020F02780A673DC74757F23823FA3014C1866E72CC4CD8B226CD6EF4"

SOURCES = {
    "xrpscan_amendments_api": {
        "url": "https://api.xrpscan.com/api/v1/amendments",
        "source_type": "xrpscan_api",
        "summary": "XRPSCAN amendment rows with current support counts, thresholds, introduced versions, and enabled dates.",
    },
    "xrpl_validated_amendments_object": {
        "url": "https://s1.ripple.com:51234/",
        "source_type": "xrpl_rpc",
        "summary": "Validated ledger Amendments object; ledger membership is authoritative for enabled/not-enabled state.",
    },
    "xrpl_known_amendments_md": {
        "url": "https://xrpl.org/resources/known-amendments.md",
        "source_type": "official_docs",
        "summary": "XRPL Known Amendments markdown: amendment IDs, statuses, source default votes, and descriptions.",
    },
    "xrpl_amendments_process_md": {
        "url": "https://xrpl.org/docs/concepts/networks-and-servers/amendments.md",
        "source_type": "official_docs",
        "summary": "XRPL amendment process: validator voting, supermajority, two-week majority period, and amendment blocking.",
    },
    "xrpl_amm_status_update_2024": {
        "url": "https://xrpl.org/blog/2024/amm-status-update",
        "source_type": "official_blog",
        "summary": "AMM post-launch pool discrepancy; advised redeeming LP tokens and avoiding new deposits until a fix amendment.",
    },
    "xrpl_get_ready_for_amm_2024": {
        "url": "https://xrpl.org/blog/2024/get-ready-for-amm",
        "source_type": "official_blog",
        "summary": "AMM was expected to enable on 2024-03-22 after supermajority support if support held.",
    },
    "crypto_basic_amm_vote_revoke_2024": {
        "url": "https://thecryptobasic.com/2024/02/07/xrpl-validators-revoke-votes-on-xls-30d-amm-not-launching-on-feb-14/",
        "source_type": "contemporaneous_reporting",
        "summary": "Contemporaneous reporting that AMM had reached validator consensus on 2024-02-01 and validators then revoked Yes votes after the bug surfaced.",
    },
    "xrpl_permission_delegation_vulnerability_2025": {
        "url": "https://xrpl.org/blog/2025/vulnerabilitydisclosurereport-bug-sep2025",
        "source_type": "official_blog",
        "summary": "PermissionDelegation vulnerability: fee-drain bug, mainnet not enabled, validators advised to vote No.",
    },
    "xrpl_rippled_2_6_1": {
        "url": "https://xrpl.org/blog/2025/rippled-2.6.1",
        "source_type": "official_blog",
        "summary": "rippled 2.6.1 disabled PermissionDelegation after a discovered bug.",
    },
    "xrpl_batch_vulnerability_2026": {
        "url": "https://xrpl.org/blog/2026/vulnerabilitydisclosurereport-bug-feb2026",
        "source_type": "official_blog",
        "summary": "Batch vulnerability: unauthorized inner transaction execution; UNL validators advised to vote No.",
    },
    "xrpl_rippled_3_1_1": {
        "url": "https://xrpl.org/blog/2026/rippled-3.1.1",
        "source_type": "official_blog",
        "summary": "rippled 3.1.1 disabled Batch and fixBatchInnerSigs due to a severe bug.",
    },
    "xrpl_transaction_set_liveness_2026": {
        "url": "https://xrpl.org/blog/2026/vulnerabilitydisclosurereport-bug-mar2026",
        "source_type": "official_blog",
        "summary": "Transaction set handling vulnerabilities affecting liveness, fixed in rippled 3.0.0.",
    },
}

SEED_13_NAMES = {
    "AMM",
    "AMMClawback",
    "Batch",
    "Clawback",
    "LendingProtocol",
    "MPTokensV1",
    "PermissionDelegation",
    "PermissionedDEX",
    "PermissionedDomains",
    "SingleAssetVault",
    "TokenEscrow",
    "fixAMMOverflowOffer",
}

SENSITIVE_TERMS = (
    "amm",
    "automated market maker",
    "bridge",
    "clawback",
    "compliance",
    "credential",
    "confidential",
    "decentralized identifier",
    "deep freeze",
    "escrow",
    "fee",
    "fee voting",
    "invariant",
    "issuer",
    "lending",
    "loan",
    "multi-purpose token",
    "mpt",
    "nft",
    "oracle",
    "permission",
    "privacy",
    "reserve",
    "sanction",
    "sell offer",
    "single asset vault",
    "vault",
)

DELAY_TERMS = ("unresolved bug", "unresolved vulnerability", "disabled due to a bug", "vote no")
BROAD_FIX_HOLD_TERMS = (
    "all other types of inner objects",
    "amm's balance meets the invariant",
    "canonical binary format",
    "circumventing these restrictions",
    "decimal floating point math",
    "deep-frozen",
    "edge cases",
    "ledgerstatefix",
    "gross amount",
    "issuer's locked token balance",
    "least significant digits",
    "loan accounting",
    "low quality order book offers",
    "net amount",
    "processing of payments",
    "price oracle",
    "ranking of offers",
    "blacklisted accounts",
    "firstnftsequence",
    "frozen lp token",
    "nft directories",
    "repair corruptions",
    "token's total supply accounting",
    "vault assets",
)
SENSITIVE_NAMES = {
    "amm",
    "ammclawback",
    "clawback",
    "confidentialtransfer",
    "credentials",
    "deepfreeze",
    "disallowincoming",
    "dynamicmpt",
    "dynamicnft",
    "did",
    "invariantsv1_1",
    "lendingprotocol",
    "mptokensv1",
    "mptokensv2",
    "nftokenmintoffer",
    "permissioneddex",
    "permissioneddomains",
    "priceoracle",
    "singleassetvault",
    "smartescrow",
    "tokenescrow",
    "xrpfees",
    "xchainbridge",
}


@dataclass
class SourceFetch:
    source_id: str
    body: bytes
    receipt: dict[str, Any]


def fetch_source(source_id: str, meta: dict[str, str], raw_dir: Path) -> SourceFetch:
    retrieved_at = utc_now()
    headers = {
        "User-Agent": "PostFiat-XRPL-amendment-lifecycle-replay/1.0",
        "Accept": "text/markdown,text/html,application/json,text/plain,*/*",
    }
    data = None
    if source_id == "xrpl_validated_amendments_object":
        data = json.dumps(
            {
                "method": "ledger_entry",
                "params": [{"index": AMENDMENTS_OBJECT_INDEX, "ledger_index": "validated"}],
            }
        ).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(meta["url"], data=data, headers=headers, method="POST" if data else "GET")
    body = b""
    status_code = 0
    content_type = "text/plain"
    last_error = ""
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                body = resp.read()
                status_code = getattr(resp, "status", 200)
                content_type = resp.headers.get("content-type", "")
                break
        except urllib.error.HTTPError as exc:
            body = exc.read()
            status_code = exc.code
            content_type = exc.headers.get("content-type", "") if exc.headers else ""
            break
        except Exception as exc:  # noqa: BLE001 - receipt records fetch failure
            last_error = f"{type(exc).__name__}: {exc}"
            if attempt == 3:
                body = f"FETCH_ERROR: {last_error}".encode("utf-8")
                status_code = 0
                content_type = "text/plain"

    suffix = ".json" if "json" in content_type or source_id in {"xrpscan_amendments_api", "xrpl_validated_amendments_object"} else ".txt"
    body_path = raw_dir / f"{source_id}{suffix}"
    body_path.parent.mkdir(parents=True, exist_ok=True)
    body_path.write_bytes(body)
    receipt = {
        "source_id": source_id,
        "url": meta["url"],
        "source_type": meta["source_type"],
        "retrieved_at": retrieved_at,
        "status_code": status_code,
        "content_type": content_type,
        "sha256": __import__("hashlib").sha256(body).hexdigest(),
        "bytes": len(body),
        "summary": meta["summary"],
        "body_path": body_path.relative_to(raw_dir.parent).as_posix(),
        "last_error": last_error,
    }
    return SourceFetch(source_id=source_id, body=body, receipt=receipt)


def parse_known_amendments(md: str) -> dict[str, dict[str, Any]]:
    sections: dict[str, dict[str, Any]] = {}
    matches = list(re.finditer(r"^###\s+(.+?)\s*$", md, flags=re.M))
    for idx, match in enumerate(matches):
        name = match.group(1).strip()
        if not name or name.startswith("#"):
            continue
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(md)
        body = md[start:end].strip()
        row_map: dict[str, str] = {}
        for line in body.splitlines():
            if not line.startswith("|"):
                continue
            cells = [clean_markdown(cell.strip()) for cell in line.strip().strip("|").split("|")]
            if len(cells) >= 2 and cells[0] and not cells[0].startswith("---"):
                row_map[cells[0]] = cells[1]
        desc_lines = []
        in_table = False
        for line in body.splitlines():
            if line.startswith("|"):
                in_table = True
                continue
            if in_table and not line.strip():
                in_table = False
                continue
            if in_table:
                continue
            if line.strip() in {"Warning", "Tip"}:
                desc_lines.append(line.strip() + ".")
                continue
            if line.strip() and not line.startswith("###"):
                desc_lines.append(clean_markdown(line))
        description = clean_markdown(" ".join(desc_lines))
        sections[name.lower()] = {
            "name": name,
            "amendment_id": row_map.get("Amendment ID", ""),
            "known_status": row_map.get("Status", "UNKNOWN").upper(),
            "source_default_vote": normalize_vote(row_map.get("Default Vote (Latest stable release)", "")),
            "pre_amendment_functionality_retired": normalize_yes_no(row_map.get("Pre-amendment functionality retired?", "")),
            "description": description[:1800],
            "anchor": slugify(name).replace("-", ""),
        }
    return sections


def normalize_vote(value: str) -> str:
    value = value.strip().upper()
    if value in {"YES", "NO"}:
        return value
    return "UNKNOWN"


def normalize_yes_no(value: str) -> str:
    value = value.strip().upper()
    if value in {"YES", "NO"}:
        return value
    return "UNKNOWN"


def vote_state(api_row: dict[str, Any], enabled: bool, known_status: str) -> str:
    if enabled:
        return "ENABLED"
    if "OBSOLETE" in known_status:
        return "VETOED_OR_RETIRED"
    count = api_row.get("count")
    threshold = api_row.get("threshold")
    majority = api_row.get("majority")
    try:
        if count is not None and threshold is not None and int(count) >= int(threshold):
            return "MAJORITY_ACTIVE" if majority else "NO_MAJORITY"
    except (TypeError, ValueError):
        pass
    if count is not None and threshold is not None:
        return "NO_MAJORITY"
    return "UNKNOWN"


def triage_label(name: str, description: str, known_status: str, event_type: str) -> str:
    lname = name.lower()
    haystack = f"{name} {description} {known_status} {event_type}".lower()
    if "obsolete" in known_status.lower() or event_type in {"validator_no_advisory", "vetoed_or_retired"}:
        return "REJECT"
    if event_type in {"post_launch_bug", "majority_lost"}:
        return "DELAY_FOR_FIX"
    if lname == "disallowincoming":
        return "PROCEED"
    if lname.startswith("fix"):
        if any(term in haystack for term in BROAD_FIX_HOLD_TERMS):
            return "HOLD_FOR_CHALLENGE"
        return "PROCEED"
    if any(term in haystack for term in DELAY_TERMS):
        return "DELAY_FOR_FIX"
    if lname in SENSITIVE_NAMES:
        return "HOLD_FOR_CHALLENGE"
    if any(term in haystack for term in SENSITIVE_TERMS):
        return "HOLD_FOR_CHALLENGE"
    return "PROCEED"


def infer_event_type(enabled: bool, known_status: str) -> str:
    if enabled:
        return "enabled"
    if "OBSOLETE" in known_status:
        return "vetoed_or_retired"
    return "introduced_open_for_voting"


def default_description(name: str) -> str:
    return f"XRPL amendment named {name}. No detailed known-amendments description was parsed for this row."


def build_universe(xrpscan_rows: list[dict[str, Any]], ledger_ids: set[str], known: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    by_name: dict[str, dict[str, Any]] = {str(row.get("name", "")).lower(): row for row in xrpscan_rows}
    names = set(by_name) | set(known)
    universe = []
    for lname in sorted(names):
        api = by_name.get(lname, {})
        k = known.get(lname, {})
        name = k.get("name") or api.get("name") or lname
        amendment_id = (k.get("amendment_id") or api.get("amendment_id") or "").upper()
        enabled = bool(amendment_id and amendment_id in ledger_ids)
        known_status = k.get("known_status") or ("ENABLED" if api.get("enabled") else "UNKNOWN")
        row = {
            "amendment_id": amendment_id,
            "name": name,
            "introduced_version": api.get("introduced") or "",
            "introduced_release_date": "",
            "source_default_vote": k.get("source_default_vote", "UNKNOWN"),
            "current_enabled": enabled,
            "current_enabled_on": api.get("enabled_on") if enabled else "",
            "current_enabled_in_ledger": api.get("enabled_in_ledger") if enabled else None,
            "current_support_count": api.get("count"),
            "current_validation_count": api.get("validations"),
            "current_threshold": api.get("threshold"),
            "current_majority": "ACTIVE" if api.get("majority") and not enabled else "NONE",
            "current_supported_by_code": api.get("supported"),
            "known_status": known_status,
            "known_status_source": "ledger+xrpscan_api+known_amendments_md",
            "description": k.get("description") or default_description(name),
            "source_ids": ["xrpl_known_amendments_md", "xrpscan_amendments_api", "xrpl_validated_amendments_object"],
        }
        universe.append(row)
    return universe


def fact(fid: str, claim: str, source_id: str, lane_visibility: list[str] | None = None) -> dict[str, Any]:
    return {
        "fact_id": fid,
        "claim": clean_markdown(claim)[:1200],
        "source_id": source_id,
        "lane_visibility": lane_visibility or list(LANES),
    }


def event_from_universe(row: dict[str, Any]) -> dict[str, Any]:
    name = row["name"]
    enabled = bool(row["current_enabled"])
    known_status = row.get("known_status", "")
    event_type = infer_event_type(enabled, known_status)
    state = vote_state(
        {
            "count": row.get("current_support_count"),
            "threshold": row.get("current_threshold"),
            "majority": row.get("current_majority") == "ACTIVE",
        },
        enabled,
        known_status,
    )
    terminal = "YES" if enabled else ("NO" if state == "VETOED_OR_RETIRED" else "NONE")
    eligible = ["vote_state", "default_vote", "triage"]
    if terminal in {"YES", "NO"}:
        eligible.insert(0, "vote_outcome")
    support = row.get("current_support_count")
    threshold = row.get("current_threshold")
    validations = row.get("current_validation_count")
    facts = [
        fact("F1", f"{name}: {row.get('description') or default_description(name)}", "xrpl_known_amendments_md", ["vote_outcome", "default_vote", "triage"]),
        fact(
            "F2",
            f"XRPL amendment voting requires sustained validator supermajority before activation; incompatible servers can become amendment-blocked.",
            "xrpl_amendments_process_md",
            list(LANES),
        ),
    ]
    if row.get("introduced_version"):
        facts.append(fact("F3", f"{name} appears in XRPSCAN with introduced rippled version {row['introduced_version']}.", "xrpscan_amendments_api", list(LANES)))
    if enabled:
        facts.append(
            fact(
                "F4",
                f"The validated ledger Amendments object currently contains amendment ID {row['amendment_id']}; XRPSCAN reports enabled_on={row.get('current_enabled_on')} and enabled_in_ledger={row.get('current_enabled_in_ledger')}.",
                "xrpl_validated_amendments_object",
                ["vote_state"],
            )
        )
    elif support is not None and threshold is not None:
        facts.append(
            fact(
                "F4",
                f"XRPSCAN currently reports support count {support} of {validations} validations, threshold {threshold}, and no enabled ledger entry for {name}.",
                "xrpscan_amendments_api",
                ["vote_state", "triage"],
            )
        )
    if "OBSOLETE" in known_status:
        facts.append(fact("F5", f"Known Amendments status for {name} is obsolete/removed: {known_status}.", "xrpl_known_amendments_md", ["vote_outcome", "vote_state", "triage"]))
    event_time = row.get("current_enabled_on") or utc_now()
    return {
        "event_id": f"known-{slugify(name)}-{event_type}",
        "amendment_id": row.get("amendment_id", ""),
        "amendment_name": name,
        "event_type": event_type,
        "event_time": event_time,
        "decision_surface": f"XRPL validator amendment decision surface for {name}.",
        "terminal_outcome": terminal,
        "vote_state_label": state,
        "source_default_vote": row.get("source_default_vote", "UNKNOWN"),
        "triage_policy_label": triage_label(name, row.get("description", ""), known_status, event_type),
        "eligible_metrics": eligible,
        "label_basis": "validated ledger membership for enabled outcomes; Known Amendments obsolete status or live XRPSCAN vote state for non-enabled outcomes.",
        "source_fact_ids": [f["fact_id"] for f in facts],
        "source_facts": facts,
        "source_ids": row.get("source_ids", []),
        "included_in_original_13_seed": name in SEED_13_NAMES,
    }


def incident_events(name_to_id: dict[str, str]) -> list[dict[str, Any]]:
    def eid(name: str) -> str:
        return name_to_id.get(name.lower(), "")

    events = [
        {
            "event_id": "incident-amm-vote-reversal-2024",
            "amendment_id": eid("AMM"),
            "amendment_name": "AMM / XLS-30 activation vote reversal",
            "event_type": "majority_lost",
            "event_time": "2024-02-07T00:00:00Z",
            "decision_surface": "Whether validators should keep supporting AMM activation after a pre-activation AMM bug surfaced.",
            "terminal_outcome": "NONE",
            "vote_state_label": "MAJORITY_LOST",
            "source_default_vote": "UNKNOWN",
            "triage_policy_label": "HOLD_FOR_CHALLENGE",
            "eligible_metrics": ["vote_state", "triage"],
            "label_basis": "public reporting establishes validator vote reversal after the AMM bug surfaced; conservative route is explicit challenge before renewed support.",
            "source_facts": [
                fact("F1", "AMM adds native automated market maker functionality integrated with the XRPL DEX.", "xrpl_known_amendments_md"),
                fact("F2", "AMM went live later, on 2024-03-22, after the validator support process continued.", "xrpl_amm_status_update_2024", ["audit_only"]),
                fact("F3", "Contemporaneous reporting said the AMM amendment had reached required validator consensus on 2024-02-01, then validators revoked Yes votes after the bug surfaced.", "crypto_basic_amm_vote_revoke_2024"),
                fact("F4", "The relevant decision surface is pre-activation bug handling, not the later terminal AMM enablement.", "xrpl_get_ready_for_amm_2024"),
            ],
            "source_ids": ["xrpl_known_amendments_md", "xrpl_get_ready_for_amm_2024", "xrpl_amm_status_update_2024", "crypto_basic_amm_vote_revoke_2024"],
            "included_in_original_13_seed": True,
        },
        {
            "event_id": "incident-amm-post-launch-pool-discrepancy-2024",
            "amendment_id": eid("AMM"),
            "amendment_name": "AMM post-launch pool discrepancy",
            "event_type": "post_launch_bug",
            "event_time": "2024-03-26T00:00:00Z",
            "decision_surface": "How validators and operators should treat AMM pool discrepancies after AMM activation but before the fix amendment.",
            "terminal_outcome": "NONE",
            "vote_state_label": "UNKNOWN",
            "source_default_vote": "UNKNOWN",
            "triage_policy_label": "DELAY_FOR_FIX",
            "eligible_metrics": ["triage"],
            "label_basis": "official AMM status update says a fix required an amendment and advised avoiding new deposits.",
            "source_facts": [
                fact("F1", "The AMM amendment went live on 2024-03-22.", "xrpl_amm_status_update_2024"),
                fact("F2", "A community member identified discrepancies in a few AMM pools indicating transactions were not executing as intended.", "xrpl_amm_status_update_2024"),
                fact("F3", "The official update said the fix required an amendment and advised users to redeem LP tokens and avoid new AMM deposits until the fix was enabled.", "xrpl_amm_status_update_2024"),
            ],
            "source_ids": ["xrpl_amm_status_update_2024"],
            "included_in_original_13_seed": True,
        },
        {
            "event_id": "incident-permission-delegation-vulnerability-2025",
            "amendment_id": eid("PermissionDelegation"),
            "amendment_name": "PermissionDelegation vulnerability",
            "event_type": "validator_no_advisory",
            "event_time": "2025-09-29T00:00:00Z",
            "decision_surface": "Whether validators should support the affected PermissionDelegation amendment after the fee-drain vulnerability was found.",
            "terminal_outcome": "NO",
            "vote_state_label": "VETOED_OR_RETIRED",
            "source_default_vote": "NO",
            "triage_policy_label": "REJECT",
            "eligible_metrics": ["vote_outcome", "vote_state", "default_vote", "triage"],
            "label_basis": "official vulnerability disclosure says validators were advised to vote No and the amendment would be disabled.",
            "source_facts": [
                fact("F1", "A PermissionDelegation bug could have let an account charge transaction fees to any other account and drain XRP balance.", "xrpl_permission_delegation_vulnerability_2025"),
                fact("F2", "The feature was not enabled on mainnet, and validators began voting No as advised.", "xrpl_permission_delegation_vulnerability_2025"),
                fact("F3", "rippled 2.6.1 disabled PermissionDelegation and planned a replacement amendment.", "xrpl_rippled_2_6_1"),
            ],
            "source_ids": ["xrpl_permission_delegation_vulnerability_2025", "xrpl_rippled_2_6_1"],
            "included_in_original_13_seed": True,
        },
        {
            "event_id": "incident-batch-vulnerability-2026",
            "amendment_id": eid("Batch"),
            "amendment_name": "Batch vulnerability",
            "event_type": "validator_no_advisory",
            "event_time": "2026-02-26T00:00:00Z",
            "decision_surface": "Whether validators should support the affected Batch amendment after the unauthorized inner transaction bug was found.",
            "terminal_outcome": "NO",
            "vote_state_label": "VETOED_OR_RETIRED",
            "source_default_vote": "NO",
            "triage_policy_label": "REJECT",
            "eligible_metrics": ["vote_outcome", "vote_state", "default_vote", "triage"],
            "label_basis": "official disclosure says UNL validators were advised to vote No; rippled 3.1.1 disabled Batch and fixBatchInnerSigs.",
            "source_facts": [
                fact("F1", "The Batch bug allowed unauthorized inner transaction execution on behalf of arbitrary victim accounts.", "xrpl_batch_vulnerability_2026"),
                fact("F2", "UNL validators were contacted and advised to vote No on Batch.", "xrpl_batch_vulnerability_2026"),
                fact("F3", "rippled 3.1.1 disabled Batch and fixBatchInnerSigs due to a severe bug.", "xrpl_rippled_3_1_1"),
            ],
            "source_ids": ["xrpl_batch_vulnerability_2026", "xrpl_rippled_3_1_1"],
            "included_in_original_13_seed": True,
        },
        {
            "event_id": "incident-transaction-set-liveness-2026",
            "amendment_id": "",
            "amendment_name": "Transaction set handling liveness vulnerabilities",
            "event_type": "follow_up_fix",
            "event_time": "2026-03-23T00:00:00Z",
            "decision_surface": "How validators should triage liveness vulnerabilities fixed in rippled 3.0.0.",
            "terminal_outcome": "NONE",
            "vote_state_label": "UNKNOWN",
            "source_default_vote": "UNKNOWN",
            "triage_policy_label": "HOLD_FOR_CHALLENGE",
            "eligible_metrics": ["triage"],
            "label_basis": "official disclosure says critical liveness vulnerabilities were fixed in rippled 3.0.0; conservative route is explicit review, not rejection.",
            "source_facts": [
                fact("F1", "Two transaction-set handling vulnerabilities affected XRPL liveness and could have prevented forward progress.", "xrpl_transaction_set_liveness_2026"),
                fact("F2", "The fixes were released as part of rippled 3.0.0.", "xrpl_transaction_set_liveness_2026"),
            ],
            "source_ids": ["xrpl_transaction_set_liveness_2026"],
            "included_in_original_13_seed": False,
        },
    ]
    for event in events:
        event["source_fact_ids"] = [f["fact_id"] for f in event["source_facts"]]
    return events


def select_events(events: list[dict[str, Any]], target_count: int) -> list[dict[str, Any]]:
    by_id = {event["event_id"]: event for event in events}
    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()

    def add(event: dict[str, Any]) -> None:
        if event["event_id"] not in selected_ids:
            selected.append(event)
            selected_ids.add(event["event_id"])

    for event in events:
        if event.get("included_in_original_13_seed"):
            add(event)
    for event in events:
        if event["terminal_outcome"] == "NO" or event["vote_state_label"] in {"NO_MAJORITY", "MAJORITY_ACTIVE", "VETOED_OR_RETIRED"}:
            add(event)
    for event in events:
        if event["terminal_outcome"] == "NONE":
            add(event)
            if len([e for e in selected if e["terminal_outcome"] == "NONE"]) >= 12:
                break
    for event in events:
        if event["triage_policy_label"] in {"HOLD_FOR_CHALLENGE", "DELAY_FOR_FIX", "REJECT"}:
            add(event)
            if len([e for e in selected if e["triage_policy_label"] != "PROCEED"]) >= 20:
                break
    enabled = [event for event in events if event["terminal_outcome"] == "YES"]
    enabled.sort(key=lambda item: (item.get("event_time") or "", item["amendment_name"]), reverse=True)
    for event in enabled:
        if len([e for e in selected if e["terminal_outcome"] == "YES"]) < 50:
            add(event)
    for event in enabled:
        if len(selected) >= target_count:
            break
        add(event)
    return selected[:target_count] if target_count else selected


def packet_for_event(event: dict[str, Any], lane: str) -> dict[str, Any]:
    visible_facts = [
        {key: value for key, value in fact_item.items() if key != "lane_visibility"}
        for fact_item in event["source_facts"]
        if lane in fact_item.get("lane_visibility", LANES)
    ]
    input_context: dict[str, Any] = {
        "amendment_id": event.get("amendment_id", ""),
        "amendment_name": event["amendment_name"],
        "decision_surface": event["decision_surface"],
        "source_facts": visible_facts,
    }
    if lane == "vote_state":
        input_context["state_question"] = "Classify the dated XRPL amendment state using the supplied source facts."
    elif lane == "vote_outcome":
        input_context["outcome_question"] = "Recommend the XRP-native YES/NO vote/outcome for this named decision surface from pre-outcome facts only."
    elif lane == "default_vote":
        input_context["default_vote_question"] = "Infer the latest stable release source default vote from the source-backed amendment description only."
    else:
        input_context["triage_question"] = (
            "Choose the conservative validator review route for this amendment decision surface as if evaluating it at decision time. "
            "Do not treat a historical packet as rejected merely because the real-world event is now complete."
        )
    packet = {
        "packet_version": 1,
        "packet_id": f"{event['case_id']}--{lane}",
        "event_id": event["case_id"],
        "lane": lane,
        "allowed_labels": LANE_ALLOWED_LABELS[lane],
        "held_out_fields": ["terminal_outcome", "vote_state_label", "source_default_vote", "triage_policy_label"],
        "input_context": input_context,
    }
    packet["packet_hash"] = sha_json(packet)
    return packet


def write_packets(root: Path, selected: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    labels: dict[str, dict[str, Any]] = {lane: {} for lane in LANES}
    case_ids = {event["event_id"]: f"case_{idx:03d}" for idx, event in enumerate(selected, start=1)}
    for lane in LANES:
        (root / "packets" / lane).mkdir(parents=True, exist_ok=True)
    for event in selected:
        event["case_id"] = case_ids[event["event_id"]]
        event_labels = {
            "vote_outcome": event["terminal_outcome"],
            "vote_state": event["vote_state_label"],
            "default_vote": event["source_default_vote"],
            "triage": event["triage_policy_label"],
        }
        for lane in event["eligible_metrics"]:
            if event_labels[lane] in {"NONE", ""}:
                continue
            packet = packet_for_event(event, lane)
            write_json(root / "packets" / lane / f"{packet['packet_id']}.json", packet)
            labels[lane][packet["packet_id"]] = {
                "case_id": event["case_id"],
                "event_id": event["event_id"],
                "amendment_name": event["amendment_name"],
                "expected_label": event_labels[lane],
                "label_basis": event["label_basis"],
            }
    labels_dir = root / "labels"
    for lane, lane_labels in labels.items():
        write_json(labels_dir / f"{lane}_labels.json", lane_labels)
    return labels


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def build_readme(root: Path, selected: list[dict[str, Any]], labels: dict[str, dict[str, Any]]) -> None:
    lane_counts = {lane: len(values) for lane, values in labels.items()}
    terminal_counts = {
        label: sum(1 for event in selected if event["terminal_outcome"] == label)
        for label in ["YES", "NO", "NONE"]
    }
    lines = [
        "# XRPL Amendment Lifecycle Replay",
        "",
        f"Generated: {utc_now()}",
        "",
        "This packet separates XRP-native outcomes, dated vote state, source default vote, and conservative governance triage.",
        "`HOLD_FOR_CHALLENGE` is only a triage label and is never compared to XRP validator vote history.",
        "",
        "## Counts",
        "",
        f"- Selected lifecycle rows: {len(selected)}",
        f"- Terminal outcome labels: {terminal_counts}",
        f"- Lane packet counts: {lane_counts}",
        "",
        "## H200",
        "",
        "The H200 machine receipt is under `vast_lifecycle/machine_receipt.json`. Per spec, the instance is retained until the run is thoroughly done and accepted or explicitly shut down.",
    ]
    (root / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", required=True, help="Benchmark artifact root to write into.")
    parser.add_argument("--target-count", type=int, default=72)
    args = parser.parse_args(argv)

    root = artifact_path(args.artifact)
    corpus_dir = root / "corpus"
    raw_dir = corpus_dir / "source_bodies"
    corpus_dir.mkdir(parents=True, exist_ok=True)

    fetched = {source_id: fetch_source(source_id, meta, raw_dir) for source_id, meta in SOURCES.items()}
    source_receipts = {source_id: item.receipt for source_id, item in fetched.items()}
    write_json(corpus_dir / "source_receipts.json", source_receipts)

    xrpscan_rows = json.loads(fetched["xrpscan_amendments_api"].body.decode("utf-8"))
    ledger_rpc = json.loads(fetched["xrpl_validated_amendments_object"].body.decode("utf-8"))
    ledger_node = ledger_rpc.get("result", {}).get("node", {})
    ledger_ids = {str(value).upper() for value in ledger_node.get("Amendments", [])}
    known_md = fetched["xrpl_known_amendments_md"].body.decode("utf-8", errors="replace")
    known = parse_known_amendments(known_md)

    for generated_dir in ("packets", "labels", "baseline", "qwen_runs", "summaries", "reports"):
        path = root / generated_dir
        if path.exists():
            shutil.rmtree(path)

    universe = build_universe(xrpscan_rows, ledger_ids, known)
    universe_by_name = {row["name"].lower(): row for row in universe}
    events = [event_from_universe(row) for row in universe]
    events.extend(incident_events({row["name"].lower(): row["amendment_id"] for row in universe}))
    events.sort(key=lambda event: event["event_id"])
    selected = select_events(events, args.target_count)

    for event in events:
        event["selected"] = event["event_id"] in {item["event_id"] for item in selected}

    labels = write_packets(root, selected)

    write_json(corpus_dir / "amendment_universe.json", universe)
    write_json(corpus_dir / "lifecycle_events.json", events)
    write_json(corpus_dir / "corpus_selection.json", selected)
    write_json(
        corpus_dir / "state_receipts.json",
        {
            "validated_ledger_index": ledger_rpc.get("result", {}).get("ledger_index"),
            "validated_amendments_object_index": AMENDMENTS_OBJECT_INDEX,
            "validated_amendment_count": len(ledger_ids),
            "xrpscan_row_count": len(xrpscan_rows),
            "known_amendment_section_count": len(known),
            "source_ids": ["xrpscan_amendments_api", "xrpl_validated_amendments_object", "xrpl_known_amendments_md"],
        },
    )

    write_csv(
        corpus_dir / "amendment_universe.csv",
        universe,
        [
            "amendment_id",
            "name",
            "introduced_version",
            "source_default_vote",
            "current_enabled",
            "current_enabled_on",
            "current_enabled_in_ledger",
            "current_support_count",
            "current_validation_count",
            "current_threshold",
            "current_majority",
            "known_status",
        ],
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

    commands = [
        f"scripts/build_xrpl_amendment_lifecycle_corpus.py --artifact {root.relative_to(root.parents[2]).as_posix()} --target-count {args.target_count}",
        f"scripts/validate_xrpl_amendment_lifecycle_corpus.py --artifact {root.relative_to(root.parents[2]).as_posix()}",
        f"scripts/run_xrpl_amendment_lifecycle_baseline.py --artifact {root.relative_to(root.parents[2]).as_posix()}",
        f"scripts/run_qwen_xrpl_amendment_lifecycle_replay.py --artifact {root.relative_to(root.parents[2]).as_posix()} --lane all --endpoint http://52.24.227.223:17756/v1 --machine-receipt {root.relative_to(root.parents[2]).as_posix()}/vast_lifecycle/machine_receipt.json --runs 1 --fail-on-error",
        f"scripts/summarize_xrpl_amendment_lifecycle_replay.py --artifact {root.relative_to(root.parents[2]).as_posix()}",
    ]
    (root / "COMMANDS.txt").write_text("\n".join(commands) + "\n", encoding="utf-8")
    build_readme(root, selected, labels)
    write_sha256s(root)
    print(root)
    print(json.dumps({"selected_rows": len(selected), "lane_counts": {lane: len(values) for lane, values in labels.items()}}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
