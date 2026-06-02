#!/usr/bin/env python3
"""Build a source-backed XRPL amendment replay corpus packet."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


SOURCES: dict[str, dict[str, str]] = {
    "xrpl_amendments_process": {
        "url": "https://xrpl.org/docs/concepts/networks-and-servers/amendments/",
        "source_type": "official_docs",
        "summary": (
            "XRPL validators vote on amendments; more than 80% support must hold "
            "for two weeks, and servers without enabled amendment code become "
            "amendment-blocked."
        ),
    },
    "xrpl_known_amendments": {
        "url": "https://xrpl.org/resources/known-amendments",
        "source_type": "official_docs",
        "summary": (
            "XRPL's public known-amendments inventory, including status, default "
            "vote, amendment IDs, and descriptions."
        ),
    },
    "xrpl_amm_status_update_2024": {
        "url": "https://xrpl.org/blog/2024/amm-status-update",
        "source_type": "official_blog",
        "summary": (
            "After AMM activation on 2024-03-22, the XRPL community identified "
            "AMM pool discrepancies; the post advised users to redeem LP tokens "
            "and avoid new deposits until a fix amendment activated."
        ),
    },
    "cryptobasic_amm_vote_reversal_2024": {
        "url": (
            "https://thecryptobasic.com/2024/02/07/"
            "xrpl-validators-revoke-votes-on-xls-30d-amm-not-launching-on-feb-14/"
        ),
        "source_type": "news",
        "summary": (
            "External reporting on validators revoking AMM amendment support "
            "after a known AMM bug was identified before activation."
        ),
    },
    "xls_73_amm_clawback": {
        "url": "https://xls.xrpl.org/xls/XLS-0073-amm-clawback.html",
        "source_type": "standard",
        "summary": (
            "XLS-73 describes issuer clawback interaction with AMM pools and "
            "regulatory-compliance motivation."
        ),
    },
    "xrpl_single_asset_vaults": {
        "url": "https://xrpl.org/docs/concepts/tokens/single-asset-vaults",
        "source_type": "official_docs",
        "summary": (
            "Single Asset Vaults aggregate assets from depositors for use by "
            "other protocols such as the Lending Protocol."
        ),
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stable_hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def amendment_id(name: str) -> str:
    return hashlib.sha512(name.encode("ascii")).hexdigest()[:64].upper()


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def fetch_source(source_id: str, source: dict[str, str]) -> dict[str, Any]:
    retrieved_at = utc_now()
    req = urllib.request.Request(
        source["url"],
        headers={
            "User-Agent": "PostFiat governance replay corpus builder/1.0",
            "Accept": "text/html,application/json,text/plain,*/*",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read()
            status_code = getattr(resp, "status", 200)
            content_type = resp.headers.get("content-type", "")
    except urllib.error.HTTPError as exc:
        body = exc.read()
        status_code = exc.code
        content_type = exc.headers.get("content-type", "") if exc.headers else ""
    except Exception as exc:  # noqa: BLE001 - recorded in receipt
        body = f"FETCH_ERROR: {type(exc).__name__}: {exc}".encode("utf-8")
        status_code = 0
        content_type = "text/plain"

    text = body.decode("utf-8", errors="replace")
    return {
        "source_id": source_id,
        "url": source["url"],
        "source_type": source["source_type"],
        "retrieved_at": retrieved_at,
        "status_code": status_code,
        "content_type": content_type,
        "sha256": hashlib.sha256(body).hexdigest(),
        "summary": source["summary"],
        "body_preview": re.sub(r"\s+", " ", text)[:800],
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
    "routine_cleanup": 0,
}


def fact(fid: str, claim: str, source_id: str, summary: str) -> dict[str, str]:
    return {
        "fact_id": fid,
        "claim": claim,
        "source_id": source_id,
        "quote_or_summary": summary,
    }


CANDIDATES: list[dict[str, Any]] = [
    {
        "packet_id": "amm-vote-reversal-2024",
        "amendment_name": "AMM / XLS-30 activation vote reversal",
        "amendment_id": amendment_id("AMM"),
        "event_window": {"start": "2024-02-01", "end": "2024-02-14"},
        "event_type": "revote",
        "short_description": (
            "Validators revoked support after a known AMM bug surfaced before the "
            "scheduled activation window."
        ),
        "technical_change": "Native automated market maker integrated with XRPL DEX settlement.",
        "risk_class": ["new_financial_primitive", "known_bug", "user_fund_or_accounting_risk"],
        "signals": ["public_vote_reversal", "known_bug", "public_debate", "user_fund_or_accounting_risk"],
        "historical_route": "DELAY_FOR_FIX",
        "safe_route_label": {
            "label": "DELAY_FOR_FIX",
            "label_basis": "explicit_validator_reversal",
            "labeler": "researcher",
            "notes": "Known bug before activation made delay the historically safer route.",
        },
        "facts": [
            fact(
                "F1",
                "The AMM amendment added AMM functionality integrated with the existing DEX.",
                "xrpl_known_amendments",
                "Known Amendments describes AMM as adding AMM instances, LP tokens, AMM transactions, and Payment/OfferCreate routing through AMMs.",
            ),
            fact(
                "F2",
                "External reporting recorded validator vote withdrawals after a known AMM issue was identified.",
                "cryptobasic_amm_vote_reversal_2024",
                "The report says validators revoked votes and that consensus fell below the 80% threshold.",
            ),
        ],
        "historical_outcome_summary": "AMM did not activate on the earlier February target; validators waited for fixes.",
    },
    {
        "packet_id": "amm-post-launch-pool-discrepancy-2024",
        "amendment_name": "AMM post-launch pool discrepancy",
        "amendment_id": amendment_id("AMM"),
        "event_window": {"start": "2024-03-22", "end": "2024-03-26"},
        "event_type": "fix",
        "short_description": "A discrepancy in AMM pools appeared soon after AMM went live.",
        "technical_change": "AMM routing through DEX payment paths required a follow-up protocol fix.",
        "risk_class": ["known_bug", "follow_up_fix", "user_fund_or_accounting_risk"],
        "signals": ["known_bug", "follow_up_fix", "user_fund_or_accounting_risk"],
        "historical_route": "DELAY_FOR_FIX",
        "safe_route_label": {
            "label": "DELAY_FOR_FIX",
            "label_basis": "later_bug",
            "labeler": "researcher",
            "notes": "Official status update advised redeeming LP tokens and avoiding new deposits until a fix.",
        },
        "facts": [
            fact(
                "F1",
                "AMM went live on 2024-03-22.",
                "xrpl_amm_status_update_2024",
                "The official AMM status update states the amendment went live on 2024-03-22.",
            ),
            fact(
                "F2",
                "A pool discrepancy indicated some transactions were not executing as intended.",
                "xrpl_amm_status_update_2024",
                "The official status update says a community member identified discrepancies in a few AMM pools.",
            ),
            fact(
                "F3",
                "The fix required another amendment and validators were advised to avoid new AMM deposits until the fix.",
                "xrpl_amm_status_update_2024",
                "The update says the fix required an amendment and advised users to redeem LP tokens and avoid new deposits.",
            ),
        ],
        "historical_outcome_summary": "A follow-up fix path was required after launch.",
    },
    {
        "packet_id": "fix-amm-overflow-offer",
        "amendment_name": "fixAMMOverflowOffer",
        "amendment_id": amendment_id("fixAMMOverflowOffer"),
        "event_window": {"start": "2024-03-26", "end": "2024-04-30"},
        "event_type": "fix",
        "short_description": "Follow-up AMM bug-fix surface after launch.",
        "technical_change": "AMM/DEX payment path correction after pool discrepancy reports.",
        "risk_class": ["follow_up_fix", "user_fund_or_accounting_risk"],
        "signals": ["follow_up_fix", "user_fund_or_accounting_risk"],
        "historical_route": "PROCEED",
        "safe_route_label": {
            "label": "PROCEED",
            "label_basis": "historical_outcome",
            "labeler": "researcher",
            "notes": "A narrow fix amendment after a known AMM issue is the expected proceed route once reviewed.",
        },
        "facts": [
            fact(
                "F1",
                "The AMM pool discrepancy fix required an amendment and validator vote.",
                "xrpl_amm_status_update_2024",
                "The official status update describes the fix path and the 80% two-week activation requirement.",
            ),
            fact(
                "F2",
                "XRPL bug fixes that change transaction processing require amendments.",
                "xrpl_amendments_process",
                "The amendment docs state that transaction-process bug fixes require amendments.",
            ),
        ],
        "historical_outcome_summary": "Fix-oriented amendment route after the AMM launch incident.",
    },
    {
        "packet_id": "ammclawback",
        "amendment_name": "AMMClawback",
        "amendment_id": amendment_id("AMMClawback"),
        "event_window": {"start": "2024-12-01", "end": "2025-02-01"},
        "event_type": "activation",
        "short_description": "Issuer clawback semantics extended into AMM pools.",
        "technical_change": "Adds AMMClawback and changes AMMDeposit behavior for frozen tokens.",
        "risk_class": ["asset_control", "compliance", "new_financial_primitive"],
        "signals": ["asset_control_or_compliance", "new_financial_primitive", "user_fund_or_accounting_risk"],
        "historical_route": "HOLD_FOR_CHALLENGE",
        "safe_route_label": {
            "label": "HOLD_FOR_CHALLENGE",
            "label_basis": "source_consensus",
            "labeler": "researcher",
            "notes": "Compliance clawback inside AMM pools deserves explicit validator challenge even if eventually enabled.",
        },
        "facts": [
            fact(
                "F1",
                "AMMClawback allows issuers to claw back clawback-enabled tokens from AMM pools.",
                "xrpl_known_amendments",
                "Known Amendments describes AMMClawback and frozen-token AMMDeposit changes.",
            ),
            fact(
                "F2",
                "XLS-73 frames the feature as regulatory-compliance related.",
                "xls_73_amm_clawback",
                "The standard describes clawback behavior for AMM pools and compliance motivation.",
            ),
        ],
        "historical_outcome_summary": "Enabled feature with asset-control semantics.",
    },
    {
        "packet_id": "clawback",
        "amendment_name": "Clawback",
        "amendment_id": amendment_id("Clawback"),
        "event_window": {"start": "2023-10-01", "end": "2024-02-01"},
        "event_type": "activation",
        "short_description": "Issuer token recovery for regulatory or sanctions cases.",
        "technical_change": "Adds issuer-controlled recovery of issued tokens.",
        "risk_class": ["asset_control", "compliance"],
        "signals": ["asset_control_or_compliance", "user_fund_or_accounting_risk"],
        "historical_route": "HOLD_FOR_CHALLENGE",
        "safe_route_label": {
            "label": "HOLD_FOR_CHALLENGE",
            "label_basis": "source_consensus",
            "labeler": "researcher",
            "notes": "Issuer clawback is structurally governance-sensitive because it changes asset-control rights.",
        },
        "facts": [
            fact(
                "F1",
                "Clawback lets issuers recover issued tokens for regulatory purposes.",
                "xrpl_known_amendments",
                "Known Amendments describes sanctions or illegal-activity examples for clawback recovery.",
            ),
        ],
        "historical_outcome_summary": "Enabled issuer asset-control primitive.",
    },
    {
        "packet_id": "mptokens-v1",
        "amendment_name": "MPTokensV1",
        "amendment_id": amendment_id("MPTokensV1"),
        "event_window": {"start": "2025-01-01", "end": "2025-09-01"},
        "event_type": "activation",
        "short_description": "New fungible token primitive optimized for stablecoin-like use cases.",
        "technical_change": "Adds MPT ledger entries, issuance transactions, authorization, and payment support.",
        "risk_class": ["new_financial_primitive", "asset_control", "user_fund_or_accounting_risk"],
        "signals": ["new_financial_primitive", "asset_control_or_compliance", "user_fund_or_accounting_risk"],
        "historical_route": "HOLD_FOR_CHALLENGE",
        "safe_route_label": {
            "label": "HOLD_FOR_CHALLENGE",
            "label_basis": "source_consensus",
            "labeler": "researcher",
            "notes": "A new fungible-token accounting surface should receive explicit challenge before default yes.",
        },
        "facts": [
            fact(
                "F1",
                "MPTokensV1 adds a new Multi-Purpose Token type and new issuance/authorization transactions.",
                "xrpl_known_amendments",
                "Known Amendments describes MPT as a new fungible token optimized for common token use cases.",
            ),
        ],
        "historical_outcome_summary": "Enabled new token primitive.",
    },
    {
        "packet_id": "batch-obsolete",
        "amendment_name": "Batch",
        "amendment_id": amendment_id("Batch"),
        "event_window": {"start": "2025-01-01", "end": "2026-05-01"},
        "event_type": "obsolete",
        "short_description": "Batch transaction amendment disabled due to a bug.",
        "technical_change": "Bundles multiple transactions for all-or-nothing processing.",
        "risk_class": ["known_bug", "obsolete", "security_or_liveness"],
        "signals": ["known_bug", "obsolete_or_disabled", "security_or_liveness"],
        "historical_route": "REJECT",
        "safe_route_label": {
            "label": "REJECT",
            "label_basis": "later_bug",
            "labeler": "researcher",
            "notes": "Known Amendments says Batch was disabled in v3.1.1 due to a bug.",
        },
        "facts": [
            fact(
                "F1",
                "Batch allows multiple transactions to be bundled and processed together.",
                "xrpl_known_amendments",
                "Known Amendments describes Batch as bundled transaction processing.",
            ),
            fact(
                "F2",
                "Batch was disabled in v3.1.1 due to a bug and marked obsolete.",
                "xrpl_known_amendments",
                "Known Amendments warning says Batch was disabled due to a bug and will be replaced.",
            ),
        ],
        "historical_outcome_summary": "Obsoleted after bug discovery.",
    },
    {
        "packet_id": "permission-delegation-obsolete",
        "amendment_name": "PermissionDelegation",
        "amendment_id": amendment_id("PermissionDelegation"),
        "event_window": {"start": "2025-01-01", "end": "2026-05-01"},
        "event_type": "obsolete",
        "short_description": "Permission delegation amendment disabled due to a bug.",
        "technical_change": "Allows accounts to delegate some permissions to other accounts.",
        "risk_class": ["known_bug", "obsolete", "security_or_liveness", "asset_control"],
        "signals": ["known_bug", "obsolete_or_disabled", "security_or_liveness", "asset_control_or_compliance"],
        "historical_route": "REJECT",
        "safe_route_label": {
            "label": "REJECT",
            "label_basis": "later_bug",
            "labeler": "researcher",
            "notes": "Known Amendments says PermissionDelegation was disabled in v2.6.1 due to a bug.",
        },
        "facts": [
            fact(
                "F1",
                "PermissionDelegation allows accounts to delegate some permissions.",
                "xrpl_known_amendments",
                "Known Amendments describes account permission delegation.",
            ),
            fact(
                "F2",
                "PermissionDelegation was disabled in v2.6.1 due to a bug and marked obsolete.",
                "xrpl_known_amendments",
                "Known Amendments warning says it will be replaced by PermissionDelegationV1_1.",
            ),
        ],
        "historical_outcome_summary": "Obsoleted after bug discovery.",
    },
    {
        "packet_id": "permissioned-dex",
        "amendment_name": "PermissionedDEX",
        "amendment_id": amendment_id("PermissionedDEX"),
        "event_window": {"start": "2025-01-01", "end": "2026-05-01"},
        "event_type": "activation",
        "short_description": "Controlled DEX environment for permissioned trading.",
        "technical_change": "Permissioned domains control who can place and accept offers.",
        "risk_class": ["compliance", "new_financial_primitive"],
        "signals": ["asset_control_or_compliance", "new_financial_primitive"],
        "historical_route": "HOLD_FOR_CHALLENGE",
        "safe_route_label": {
            "label": "HOLD_FOR_CHALLENGE",
            "label_basis": "source_consensus",
            "labeler": "researcher",
            "notes": "Permissioned market access is exactly the kind of semantics validators should challenge explicitly.",
        },
        "facts": [
            fact(
                "F1",
                "PermissionedDEX creates controlled DEX environments where a permissioned domain controls market access.",
                "xrpl_known_amendments",
                "Known Amendments describes permissioned trading as open DEX behavior gated by a permissioned domain.",
            ),
        ],
        "historical_outcome_summary": "Open-for-voting compliance primitive at the source snapshot.",
    },
    {
        "packet_id": "permissioned-domains",
        "amendment_name": "PermissionedDomains",
        "amendment_id": amendment_id("PermissionedDomains"),
        "event_window": {"start": "2025-01-01", "end": "2026-05-01"},
        "event_type": "activation",
        "short_description": "Controlled access domains for compliance-bound XRPL features.",
        "technical_change": "Adds PermissionedDomain ledger entry and set/delete transactions.",
        "risk_class": ["compliance", "asset_control"],
        "signals": ["asset_control_or_compliance", "new_financial_primitive"],
        "historical_route": "HOLD_FOR_CHALLENGE",
        "safe_route_label": {
            "label": "HOLD_FOR_CHALLENGE",
            "label_basis": "source_consensus",
            "labeler": "researcher",
            "notes": "The source itself frames domains as compliance infrastructure for traditional finance.",
        },
        "facts": [
            fact(
                "F1",
                "PermissionedDomains restrict access for features such as Permissioned DEXes and Lending Protocols.",
                "xrpl_known_amendments",
                "Known Amendments describes domains as compliance-controlled environments.",
            ),
        ],
        "historical_outcome_summary": "Open-for-voting compliance primitive at the source snapshot.",
    },
    {
        "packet_id": "lending-protocol",
        "amendment_name": "LendingProtocol",
        "amendment_id": amendment_id("LendingProtocol"),
        "event_window": {"start": "2025-01-01", "end": "2026-05-01"},
        "event_type": "activation",
        "short_description": "On-chain fixed-term uncollateralized loans using pooled funds.",
        "technical_change": "Lending protocol depends on Single Asset Vaults and off-chain underwriting.",
        "risk_class": ["new_financial_primitive", "off_chain_underwriting", "user_fund_or_accounting_risk"],
        "signals": ["new_financial_primitive", "asset_control_or_compliance", "user_fund_or_accounting_risk"],
        "historical_route": "HOLD_FOR_CHALLENGE",
        "safe_route_label": {
            "label": "HOLD_FOR_CHALLENGE",
            "label_basis": "source_consensus",
            "labeler": "researcher",
            "notes": "Uncollateralized lending with off-chain underwriting deserves explicit governance review.",
        },
        "facts": [
            fact(
                "F1",
                "LendingProtocol enables fixed-term uncollateralized loans using pooled funds from a Single Asset Vault.",
                "xrpl_known_amendments",
                "Known Amendments says creditworthiness is assessed through off-chain underwriting and risk management.",
            ),
        ],
        "historical_outcome_summary": "Open-for-voting financial primitive at the source snapshot.",
    },
    {
        "packet_id": "single-asset-vault",
        "amendment_name": "SingleAssetVault",
        "amendment_id": amendment_id("SingleAssetVault"),
        "event_window": {"start": "2025-01-01", "end": "2026-05-01"},
        "event_type": "activation",
        "short_description": "Pooled vault primitive for asset management and lending markets.",
        "technical_change": "Aggregates depositor assets for use by on-chain protocols.",
        "risk_class": ["new_financial_primitive", "user_fund_or_accounting_risk"],
        "signals": ["new_financial_primitive", "user_fund_or_accounting_risk"],
        "historical_route": "HOLD_FOR_CHALLENGE",
        "safe_route_label": {
            "label": "HOLD_FOR_CHALLENGE",
            "label_basis": "source_consensus",
            "labeler": "researcher",
            "notes": "A vault primitive changes pooled custody and accounting behavior.",
        },
        "facts": [
            fact(
                "F1",
                "Single Asset Vaults aggregate assets from multiple depositors for use by other protocols.",
                "xrpl_single_asset_vaults",
                "The concept documentation describes vaults for asset management and lending markets.",
            ),
        ],
        "historical_outcome_summary": "Financial primitive documented as a dependency for lending markets.",
    },
    {
        "packet_id": "token-escrow",
        "amendment_name": "TokenEscrow",
        "amendment_id": amendment_id("TokenEscrow"),
        "event_window": {"start": "2024-01-01", "end": "2026-05-01"},
        "event_type": "activation",
        "short_description": "Escrow functionality for issued tokens.",
        "technical_change": "Extends escrow behavior beyond XRP into issued assets.",
        "risk_class": ["new_financial_primitive", "user_fund_or_accounting_risk"],
        "signals": ["new_financial_primitive", "user_fund_or_accounting_risk"],
        "historical_route": "HOLD_FOR_CHALLENGE",
        "safe_route_label": {
            "label": "HOLD_FOR_CHALLENGE",
            "label_basis": "source_consensus",
            "labeler": "researcher",
            "notes": "Token escrow changes custody/timing semantics for issued assets.",
        },
        "facts": [
            fact(
                "F1",
                "XRPL Known Amendments lists TokenEscrow as a protocol amendment surface.",
                "xrpl_known_amendments",
                "TokenEscrow is a named amendment in the public known-amendments inventory.",
            ),
        ],
        "historical_outcome_summary": "Financial custody primitive requiring explicit review.",
    },
]


def controversy_score(candidate: dict[str, Any]) -> int:
    return sum(SIGNAL_POINTS[s] for s in candidate["signals"])


def route_to_vote(route: str) -> str:
    return {
        "PROCEED": "YES",
        "DELAY_FOR_FIX": "NO",
        "HOLD_FOR_CHALLENGE": "HOLD",
        "REJECT": "NO",
        "OBSOLETE": "NO",
    }.get(route, "HOLD")


def deterministic_route(packet: dict[str, Any]) -> dict[str, Any]:
    risks = set(packet["risk_class"])
    event_type = packet["event_type"]
    facts = [f["fact_id"] for f in packet["historical_facts"]]
    triggered: list[str] = []
    route = "HOLD_FOR_CHALLENGE"

    if "known_bug" in risks and event_type in {"revote", "fix"}:
        route = "DELAY_FOR_FIX"
        triggered.append("known bug + feature launch/fix review -> DELAY_FOR_FIX")
    if event_type == "obsolete" or "obsolete" in risks:
        route = "REJECT"
        triggered.append("obsolete or disabled status -> REJECT")
    if event_type == "fix" and "follow_up_fix" in risks and "known_bug" not in risks:
        route = "PROCEED"
        triggered.append("narrow fix amendment after known incident -> PROCEED after review")
    if route == "HOLD_FOR_CHALLENGE" and (
        "asset_control" in risks
        or "compliance" in risks
        or "new_financial_primitive" in risks
        or "off_chain_underwriting" in risks
    ):
        triggered.append("new financial/compliance/asset-control primitive -> HOLD_FOR_CHALLENGE")
    if not triggered:
        triggered.append("missing low-risk evidence -> HOLD_FOR_CHALLENGE")

    return {
        "route": route,
        "vote_default": route_to_vote(route),
        "triggered_rules": triggered,
        "cited_facts": facts,
        "limitations": [
            "Rule baseline is intentionally blunt and cannot synthesize nuanced work items.",
            "It uses packet labels and source-backed facts, not private validator deliberation.",
        ],
    }


def build_packet(candidate: dict[str, Any], selected_at: str) -> dict[str, Any]:
    facts = []
    for source_fact in candidate["facts"]:
        item = dict(source_fact)
        item["retrieved_at"] = selected_at
        facts.append(item)
    source_ids = sorted({f["source_id"] for f in facts} | {"xrpl_amendments_process"})
    packet = {
        "packet_version": 1,
        "packet_id": candidate["packet_id"],
        "amendment_name": candidate["amendment_name"],
        "amendment_id": candidate["amendment_id"],
        "event_window": candidate["event_window"],
        "event_type": candidate["event_type"],
        "short_description": candidate["short_description"],
        "technical_change": candidate["technical_change"],
        "risk_class": candidate["risk_class"],
        "controversy_signals": candidate["signals"],
        "controversy_score": controversy_score(candidate),
        "historical_facts": facts,
        "sources": [
            {
                "source_id": sid,
                "url": SOURCES[sid]["url"],
                "source_type": SOURCES[sid]["source_type"],
                "summary": SOURCES[sid]["summary"],
            }
            for sid in source_ids
        ],
        "vote_context": {
            "threshold": "80_percent_for_two_weeks",
            "support_source_id": "xrpl_amendments_process",
        },
        "historical_outcome": {
            "route": candidate["historical_route"],
            "outcome_summary": candidate["historical_outcome_summary"],
            "outcome_source_id": candidate["facts"][-1]["source_id"],
        },
        "safe_route_label": candidate["safe_route_label"],
    }
    packet["packet_hash"] = stable_hash_text(json.dumps(packet, sort_keys=True, ensure_ascii=False))
    return packet


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def write_sha256s(packet_dir: Path) -> None:
    rows: list[str] = []
    for path in sorted(packet_dir.rglob("*")):
        if not path.is_file() or path.name == "SHA256SUMS.txt":
            continue
        rel = path.relative_to(packet_dir).as_posix()
        rows.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {rel}")
    (packet_dir / "SHA256SUMS.txt").write_text("\n".join(rows) + "\n")


def default_output_dir() -> Path:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return REPO_ROOT / "static" / "benchmarks" / f"xrpl-amendment-governance-replay-{ts}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=default_output_dir())
    parser.add_argument("--limit", type=int, default=13)
    args = parser.parse_args(argv)

    selected_at = utc_now()
    packet_dir = args.output.resolve()
    packet_dir.mkdir(parents=True, exist_ok=True)
    amendments_dir = packet_dir / "amendment_packets"
    amendments_dir.mkdir(parents=True, exist_ok=True)

    ranked = sorted(
        CANDIDATES,
        key=lambda c: (
            controversy_score(c),
            c["event_window"]["end"],
            c["amendment_name"],
        ),
        reverse=True,
    )[: args.limit]

    receipts = {sid: fetch_source(sid, src) for sid, src in SOURCES.items()}
    write_json(packet_dir / "source_receipts.json", {"generated_at": selected_at, "sources": receipts})

    packets = []
    deterministic = {}
    for candidate in ranked:
        packet = build_packet(candidate, selected_at)
        packets.append(packet)
        deterministic[packet["packet_id"]] = deterministic_route(packet)
        write_json(amendments_dir / f"{packet['packet_id']}.json", packet)

    with (packet_dir / "corpus_selection.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "rank",
                "packet_id",
                "amendment_or_event",
                "controversy_score",
                "controversy_signals",
                "event_type",
                "historical_route",
                "event_window",
            ],
        )
        writer.writeheader()
        for idx, packet in enumerate(packets, start=1):
            writer.writerow(
                {
                    "rank": idx,
                    "packet_id": packet["packet_id"],
                    "amendment_or_event": packet["amendment_name"],
                    "controversy_score": packet["controversy_score"],
                    "controversy_signals": "|".join(packet["controversy_signals"]),
                    "event_type": packet["event_type"],
                    "historical_route": packet["historical_outcome"]["route"],
                    "event_window": f"{packet['event_window']['start']}..{packet['event_window']['end']}",
                }
            )

    write_json(
        packet_dir / "deterministic_baseline.json",
        {
            "generated_at": selected_at,
            "rule_engine_version": "xrpl-amendment-replay-baseline-v1",
            "results": deterministic,
        },
    )

    readme = f"""# XRPL Amendment Governance Replay Packet

Generated: {selected_at}

This packet supports the Post Fiat post `LLM Governance Replay`.

It contains {len(packets)} source-backed amendment/event packets selected by a
declared controversy-score rule, source receipts, and a deterministic rule
baseline. Run Qwen replay and summarization with:

```bash
python3 scripts/run_qwen_amendment_replay.py \\
  --corpus {packet_dir.relative_to(REPO_ROOT).as_posix()}/amendment_packets \\
  --endpoint <OPENAI_COMPATIBLE_SGLANG_ENDPOINT> \\
  --model Qwen/Qwen3.6-27B-FP8 \\
  --machine-receipt {packet_dir.relative_to(REPO_ROOT).as_posix()}/vast_lifecycle/machine_receipt.json \\
  --runs 3 \\
  --validators 41

python3 scripts/summarize_xrpl_amendment_replay.py \\
  --packet {packet_dir.relative_to(REPO_ROOT).as_posix()}
```
"""
    (packet_dir / "README.md").write_text(readme)
    (packet_dir / "COMMANDS.txt").write_text(
        "\n".join(
            [
                f"python3 scripts/build_xrpl_amendment_replay_corpus.py --output {packet_dir.relative_to(REPO_ROOT).as_posix()}",
                f"python3 scripts/run_qwen_amendment_replay.py --corpus {packet_dir.relative_to(REPO_ROOT).as_posix()}/amendment_packets --endpoint <OPENAI_COMPATIBLE_SGLANG_ENDPOINT> --model Qwen/Qwen3.6-27B-FP8 --machine-receipt {packet_dir.relative_to(REPO_ROOT).as_posix()}/vast_lifecycle/machine_receipt.json --runs 3 --validators 41",
                f"python3 scripts/summarize_xrpl_amendment_replay.py --packet {packet_dir.relative_to(REPO_ROOT).as_posix()}",
                f"cd {packet_dir.relative_to(REPO_ROOT).as_posix()} && sha256sum -c SHA256SUMS.txt",
            ]
        )
        + "\n"
    )

    write_sha256s(packet_dir)
    print(packet_dir.relative_to(REPO_ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
