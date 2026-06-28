#!/usr/bin/env python3
"""Build EP-3 origination replay packets from non-final XLS amendments."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from xrpl_lifecycle_common import artifact_path, clean_markdown, read_json, sha_json, write_json, write_sha256s


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROVENANCE = REPO_ROOT / "static" / "benchmarks" / "xrpl-xls-provenance-20260603T230503Z"
DEFAULT_STATUS = REPO_ROOT / "static" / "benchmarks" / "xrpl-origination-status-20260604T011710Z"
DEFAULT_STANDARDS_DIR = REPO_ROOT / ".tih" / "external-cache" / "XRPL-Standards"

ALLOWED_LABELS = [
    "OPEN_RESEARCH_PACKET",
    "NEEDS_IMPLEMENTATION_OWNER",
    "NEEDS_SECURITY_REVIEW",
    "MERGE_WITH_RELATED_SPEC",
    "WAIT_FOR_DEPENDENCY",
    "PUBLIC_DISCUSSION_NEEDED",
    "CLOSE_AS_SUPERSEDED",
    "INSUFFICIENT_EVIDENCE",
]

NON_FINAL_STATUSES = {"DRAFT", "STAGNANT", "DEPRECATED", "WITHDRAWN"}

OUTPUT_SCHEMA = {
    "work_item_label": "OPEN_RESEARCH_PACKET | NEEDS_IMPLEMENTATION_OWNER | NEEDS_SECURITY_REVIEW | MERGE_WITH_RELATED_SPEC | WAIT_FOR_DEPENDENCY | PUBLIC_DISCUSSION_NEEDED | CLOSE_AS_SUPERSEDED | INSUFFICIENT_EVIDENCE",
    "confidence": 0.0,
    "problem_statement": "...",
    "public_work_item": {
        "title": "...",
        "next_action": "...",
        "owner_needed": True,
        "review_questions": ["..."],
    },
    "source_citations": ["S1"],
    "missing_evidence": ["..."],
    "risks": ["..."],
    "fork_points": ["..."],
    "non_claims": [
        "This is not a validator vote recommendation.",
        "This does not decide whether the amendment should pass.",
    ],
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


def short_excerpt(text: str, max_chars: int = 5200) -> str:
    text = re.sub(r"<pre>|</pre>", "", text, flags=re.I)
    text = clean_markdown(text)
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + " ..."


def packet_hash(packet: dict[str, Any]) -> str:
    clean = dict(packet)
    clean.pop("packet_hash", None)
    return sha_json(clean)


def risk_tags(prov: dict[str, str], status: dict[str, str]) -> list[str]:
    tags = set()
    for value in (prov.get("institutional_categories", ""), prov.get("institutional_terms", "")):
        for item in re.split(r"[;,]", value):
            item = item.strip()
            if item:
                tags.add(item)
    state = status.get("mainnet_state", "")
    if state:
        tags.add(f"mainnet:{state.lower()}")
    xls_status = prov.get("status", "")
    if xls_status:
        tags.add(f"xls_status:{xls_status.lower()}")
    if status.get("mapping_kind") == "not_in_known_amendments":
        tags.add("no_known_amendment_mapping")
    return sorted(tags)


def missing_evidence(prov: dict[str, str], status: dict[str, str]) -> list[str]:
    missing: list[str] = []
    if not prov.get("implementation"):
        missing.append("No implementation link is present in XLS front matter.")
    if status.get("mainnet_state") == "NOT_PRESENT_IN_KNOWN_AMENDMENTS":
        missing.append("EP-2 found no current XRPL Known Amendments mapping for this XLS.")
    if not prov.get("proposal_from"):
        missing.append("No proposal discussion URL is present in XLS front matter.")
    if status.get("mapping_confidence") in {"none", "low"}:
        missing.append("Known-amendment mapping is absent or low-confidence.")
    return missing


def source_entry(source_id: str, kind: str, url: str, title: str, sha256: str = "") -> dict[str, Any]:
    return {"source_id": source_id, "kind": kind, "url": url, "title": title, "sha256": sha256}


def source_fact(source_id: str, claim: str, quote: str = "") -> dict[str, str]:
    return {"source_id": source_id, "claim": clean_markdown(claim)[:1200], "excerpt": clean_markdown(quote)[:1800]}


def build_packet(
    *,
    prov: dict[str, str],
    status: dict[str, str],
    readme_text: str,
    readme_sha: str,
    generated_at: str,
    packet_compiler: str,
    fork_of: str = "",
    fork_kind: str = "",
    fork_note: str = "",
) -> dict[str, Any]:
    packet_id = f"origination-{prov['id'].lower()}"
    if fork_kind:
        packet_id = f"{packet_id}--fork-{fork_kind}"
    sources = [
        source_entry("S1", "xls_readme", prov["readme_url"], f"{prov['id']} README", readme_sha),
        source_entry("S2", "provenance_packet", prov["readme_url"], "EP-1 provenance row", prov.get("readme_sha256", "")),
        source_entry("S3", "status_reconciliation", status["mainnet_state_source_urls"], "EP-2 status reconciliation"),
    ]
    if prov.get("proposal_from"):
        sources.append(source_entry("S4", "proposal_discussion", prov["proposal_from"], "XRPLF proposal discussion"))
    if prov.get("implementation"):
        sources.append(source_entry("S5", "implementation", prov["implementation"], "Implementation link from XLS front matter"))
    facts = [
        source_fact(
            "S1",
            f"{prov['id']} is titled {prov['title']!r}; XLS status is {prov['status']}; authors are {prov['author_raw']}.",
            readme_text,
        ),
        source_fact(
            "S2",
            f"EP-1 provenance classifies {prov['id']} as {prov['strict_support_tier']} with author string {prov['author_raw']}.",
            prov.get("front_author_root_labels", ""),
        ),
        source_fact(
            "S3",
            (
                f"EP-2 maps {prov['id']} to known amendment names "
                f"{status.get('known_amendment_names') or 'none'} with mapping kind {status['mapping_kind']} "
                f"and current mainnet state {status['mainnet_state']}."
            ),
            json.dumps(
                {
                    "known_amendment_names": status.get("known_amendment_names"),
                    "known_statuses": status.get("known_amendments_doc_statuses"),
                    "mainnet_state": status.get("mainnet_state"),
                    "enabled_dates": status.get("enabled_dates"),
                },
                sort_keys=True,
            ),
        ),
    ]
    if prov.get("proposal_from"):
        facts.append(source_fact("S4", f"{prov['id']} has proposal discussion URL {prov['proposal_from']}."))
    if prov.get("implementation"):
        facts.append(source_fact("S5", f"{prov['id']} includes implementation URL {prov['implementation']}."))
    if fork_kind:
        sources.append(source_entry("S_FORK", "fork_control", "", f"Fork control: {fork_kind}"))
        facts.append(source_fact("S_FORK", fork_note or f"Fork control applied: {fork_kind}."))

    packet = {
        "packet_id": packet_id,
        "schema_version": "origination-replay-packet-v1",
        "generated_at": generated_at,
        "fork_of": fork_of,
        "fork_kind": fork_kind,
        "decision_question": "Given this public amendment packet, what public work item should be originated next?",
        "allowed_output_labels": ALLOWED_LABELS,
        "output_schema": OUTPUT_SCHEMA,
        "amendment_identity": {
            "xls_id": prov["id"],
            "title": prov["title"],
            "category": prov["category"],
            "xls_status": prov["status"],
            "created": prov["created"],
            "updated": prov.get("updated", ""),
            "authors": prov["author_raw"],
            "origin_tier": prov["strict_support_tier"],
        },
        "known_status": {
            "known_amendment_names": [item for item in status.get("known_amendment_names", "").split(";") if item],
            "known_amendment_ids": [item for item in status.get("known_amendment_ids", "").split(";") if item],
            "known_amendments_doc_statuses": [
                item for item in status.get("known_amendments_doc_statuses", "").split(";") if item
            ],
            "mainnet_state": status["mainnet_state"],
            "mapping_kind": status["mapping_kind"],
            "mapping_confidence": status["mapping_confidence"],
            "enabled_dates": [item for item in status.get("enabled_dates", "").split(";") if item],
        },
        "known_dependencies": [item.strip() for item in re.split(r"[,;]", prov.get("requires", "")) if item.strip()],
        "related_specs": [item.strip() for item in re.findall(r"XLS-\d+", readme_text, flags=re.I)],
        "implementation_links": [prov["implementation"]] if prov.get("implementation") else [],
        "open_discussion_links": [prov["proposal_from"]] if prov.get("proposal_from") else [],
        "risk_surface_tags": risk_tags(prov, status),
        "missing_evidence": missing_evidence(prov, status),
        "omission_log": [
            "GitHub discussion comments were not fetched for v1 packet construction.",
            "README body was excerpted and truncated for prompt budget.",
            "No private author, validator, or Ripple internal context was included.",
            "This packet does not include a normative objective function for XRPL governance.",
        ],
        "source_list": sources,
        "source_facts": facts,
        "source_excerpts": {"S1": short_excerpt(readme_text)},
        "packet_compiler": packet_compiler,
        "non_claims": [
            "This packet is for origination replay, not validator voting.",
            "The output must be a public work item, not an adoption recommendation.",
            "The model is not asked to decide whether the amendment is good.",
        ],
        "packet_hash": "",
    }
    packet["related_specs"] = sorted(set(packet["related_specs"]))
    packet["packet_hash"] = packet_hash(packet)
    return packet


def write_packet(path: Path, packet: dict[str, Any]) -> None:
    write_json(path, packet)


def build_artifact(provenance_dir: Path, status_dir: Path, standards_dir: Path, artifact_dir: Path) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    generated_at = utc_now()
    packet_compiler = "scripts/build_xrpl_origination_replay_packets.py"
    prov_rows = {row["id"]: row for row in read_csv(provenance_dir / "xls_provenance.csv")}
    status_rows = {row["xls_id"]: row for row in read_csv(status_dir / "amendment_status_reconciliation.csv")}
    selected = [
        row
        for row in prov_rows.values()
        if row.get("category", "").lower() == "amendment" and row.get("status", "").upper() in NON_FINAL_STATUSES
    ]
    selected.sort(key=lambda row: int(row["xls_number"]))

    packets: list[dict[str, Any]] = []
    manifest_rows: list[dict[str, Any]] = []
    for prov in selected:
        readme_path = standards_dir / prov["relpath"]
        readme_text = readme_path.read_text(encoding="utf-8", errors="replace")
        readme_sha = hashlib.sha256(readme_path.read_bytes()).hexdigest()
        packet = build_packet(
            prov=prov,
            status=status_rows[prov["id"]],
            readme_text=readme_text,
            readme_sha=readme_sha,
            generated_at=generated_at,
            packet_compiler=packet_compiler,
        )
        packets.append(packet)
        write_packet(artifact_dir / "packets" / f"{packet['packet_id']}.json", packet)
        manifest_rows.append(
            {
                "packet_id": packet["packet_id"],
                "xls_id": prov["id"],
                "title": prov["title"],
                "xls_status": prov["status"],
                "origin_tier": prov["strict_support_tier"],
                "mainnet_state": status_rows[prov["id"]]["mainnet_state"],
                "packet_hash": packet["packet_hash"],
            }
        )

    forks: list[dict[str, Any]] = []
    fork_specs = [
        (
            "XLS-0066",
            "remove_implementation_source",
            "Fork control: the implementation URL was removed to test whether the work item depends on implementation evidence.",
        ),
        (
            "XLS-0054",
            "add_not_present_status_emphasis",
            "Fork control: emphasize that EP-2 found no current XRPL Known Amendments mapping for this non-final NFT-offer proposal.",
        ),
        (
            "XLS-0100",
            "add_dependency_status_emphasis",
            "Fork control: emphasize that SmartEscrow is IN DEVELOPMENT and its WASM execution dependency is represented by a separate draft XLS.",
        ),
    ]
    by_xls = {packet["amendment_identity"]["xls_id"]: packet for packet in packets}
    for xls_id, fork_kind, note in fork_specs:
        base = by_xls[xls_id]
        prov = prov_rows[xls_id]
        status = status_rows[xls_id]
        readme_path = standards_dir / prov["relpath"]
        fork = build_packet(
            prov=prov,
            status=status,
            readme_text=readme_path.read_text(encoding="utf-8", errors="replace"),
            readme_sha=hashlib.sha256(readme_path.read_bytes()).hexdigest(),
            generated_at=generated_at,
            packet_compiler=packet_compiler,
            fork_of=base["packet_id"],
            fork_kind=fork_kind,
            fork_note=note,
        )
        if fork_kind == "remove_implementation_source":
            fork["implementation_links"] = []
            fork["source_list"] = [source for source in fork["source_list"] if source["source_id"] != "S5"]
            fork["source_facts"] = [fact for fact in fork["source_facts"] if fact["source_id"] != "S5"]
            fork["missing_evidence"] = sorted(set(fork["missing_evidence"] + ["Implementation evidence removed by fork control."]))
            fork["packet_hash"] = packet_hash(fork)
        forks.append(fork)
        write_packet(artifact_dir / "fork_packets" / f"{fork['packet_id']}.json", fork)

    write_json(artifact_dir / "schema" / "origination_output_schema.json", OUTPUT_SCHEMA)
    write_json(
        artifact_dir / "manifest.json",
        {
            "generated_at": generated_at,
            "schema_version": "origination-replay-artifact-v1",
            "provenance_packet": provenance_dir.relative_to(REPO_ROOT).as_posix(),
            "status_packet": status_dir.relative_to(REPO_ROOT).as_posix(),
            "standards_dir_commit": "",
            "allowed_output_labels": ALLOWED_LABELS,
            "packet_count": len(packets),
            "fork_packet_count": len(forks),
            "packets": manifest_rows,
            "forks": [
                {
                    "packet_id": fork["packet_id"],
                    "fork_of": fork["fork_of"],
                    "fork_kind": fork["fork_kind"],
                    "packet_hash": fork["packet_hash"],
                }
                for fork in forks
            ],
        },
    )
    write_csv(
        artifact_dir / "packet_manifest.csv",
        manifest_rows,
        ["packet_id", "xls_id", "title", "xls_status", "origin_tier", "mainnet_state", "packet_hash"],
    )
    commands = [
        f"python3 scripts/build_xrpl_origination_replay_packets.py --artifact-dir {artifact_dir.relative_to(REPO_ROOT).as_posix()}",
        f"python3 scripts/validate_xrpl_origination_replay.py --artifact {artifact_dir.relative_to(REPO_ROOT).as_posix()}",
        f"python3 scripts/run_qwen_xrpl_origination_replay.py --artifact {artifact_dir.relative_to(REPO_ROOT).as_posix()} --endpoint <OPENAI_COMPATIBLE_SGLANG_ENDPOINT> --machine-receipt <MACHINE_RECEIPT> --runs 5 --fail-on-error",
        f"python3 scripts/summarize_xrpl_origination_replay.py --artifact {artifact_dir.relative_to(REPO_ROOT).as_posix()}",
    ]
    (artifact_dir / "COMMANDS.txt").write_text("\n".join(commands) + "\n", encoding="utf-8")
    (artifact_dir / "README.md").write_text(
        "\n".join(
            [
                "# XRPL Origination Replay Packets",
                "",
                f"Generated: {generated_at}",
                "",
                "This packet set asks a narrow origination question over unresolved XLS amendment proposals:",
                "",
                "> Given this public amendment packet, what public work item should be originated next?",
                "",
                f"- Main packets: {len(packets)}",
                f"- Fork-control packets: {len(forks)}",
                "",
                "The output is not a validator vote recommendation and does not decide whether an amendment should pass.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    write_sha256s(artifact_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provenance", type=Path, default=DEFAULT_PROVENANCE)
    parser.add_argument("--status", type=Path, default=DEFAULT_STATUS)
    parser.add_argument("--standards-dir", type=Path, default=DEFAULT_STANDARDS_DIR)
    parser.add_argument("--artifact-dir", type=Path)
    args = parser.parse_args()
    artifact_dir = args.artifact_dir
    if artifact_dir is None:
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        artifact_dir = REPO_ROOT / "static" / "benchmarks" / f"xrpl-origination-replay-{stamp}"
    build_artifact(
        artifact_path(args.provenance),
        artifact_path(args.status),
        artifact_path(args.standards_dir),
        artifact_path(artifact_dir),
    )
    print(artifact_dir)


if __name__ == "__main__":
    main()
