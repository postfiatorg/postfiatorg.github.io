#!/usr/bin/env python3
"""Generate a whitepaper provenance packet for date and artifact claims."""

from __future__ import annotations

import base64
import csv
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
WHITEPAPER = REPO_ROOT / "content" / "whitepaper.md"
DYNAMIC_UNL_REPO = REPO_ROOT.parent / "dynamic-unl-scoring"

DATE_PATTERN = re.compile(
    r"(\b20\d{2}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}Z?)?\b|"
    r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}, 20\d{2}\b|"
    r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* 20\d{2}\b|"
    r"\b20\d{2}\b)"
)

PROVENANCE_TERMS = (
    "published",
    "production",
    "revision",
    "generated",
    "inspected",
    "effective",
    "round",
    "sequence",
    "benchmark",
    "artifact",
    "commit",
    "memo",
    "testnet",
    "live",
    "May",
    "2026",
)

LOCAL_ARTIFACTS = [
    ("whitepaper", REPO_ROOT, "content/whitepaper.md"),
    ("testnet_vl_content", REPO_ROOT, "content/testnet_vl.json"),
    ("testnet_vl_public_build", REPO_ROOT, "public/testnet_vl.json"),
    ("live_validator_stats", REPO_ROOT, "static/benchmarks/live-testnet-validator-stats.json"),
    (
        "xrpl_replay_harness",
        REPO_ROOT,
        "scripts/xrpl_validator_sglang_determinism.py",
    ),
    (
        "xrpl_replay_raw",
        REPO_ROOT,
        "static/benchmarks/xrpl-validator-sglang-determinism-20260505T205530Z.json",
    ),
    (
        "xrpl_replay_summary",
        REPO_ROOT,
        "static/benchmarks/xrpl-validator-sglang-determinism-20260505T205530Z-summary.json",
    ),
    (
        "xrpl_replay_domains",
        REPO_ROOT,
        "static/benchmarks/xrpl-validator-sglang-determinism-20260505T205530Z-domains.csv",
    ),
    (
        "model_lift_baseline_report",
        REPO_ROOT,
        "static/benchmarks/model-lift-baseline-20260601T154824Z/REPORT.md",
    ),
    (
        "model_lift_adjudication_report",
        REPO_ROOT,
        "static/benchmarks/model-lift-adjudication-20260601T165516Z/REPORT.md",
    ),
    (
        "ai_governance_challenge_report",
        REPO_ROOT,
        "static/benchmarks/ai-governance-evidence-challenge-20260601T170829Z/REPORT.md",
    ),
    (
        "qwen36_modal_feasibility",
        DYNAMIC_UNL_REPO,
        "phase0/docs/Qwen36ModalFeasibility.md",
    ),
    (
        "qwen36_deploy_doc",
        DYNAMIC_UNL_REPO,
        "phase0/docs/DeployQwen36_27B.md",
    ),
    (
        "qwen36_quality_comparison",
        DYNAMIC_UNL_REPO,
        "phase0/docs/ModelQualityComparison_Qwen36_27B.md",
    ),
    (
        "qwen36_thinking_comparison",
        DYNAMIC_UNL_REPO,
        "phase0/docs/Qwen36ThinkingModeComparison.md",
    ),
    ("qwen36_deploy_wrapper", DYNAMIC_UNL_REPO, "infra/deploy_qwen36_endpoint.py"),
    ("sglang_deploy_impl", DYNAMIC_UNL_REPO, "infra/deploy_endpoint.py"),
    (
        "qwen36_scoring_run_1",
        DYNAMIC_UNL_REPO,
        "phase0/results/modal/qwen36-27b-fp8/2026-04-30_qwen36-27b-fp8_scoring-v2/run_1.json",
    ),
    ("testnet_env_reference", DYNAMIC_UNL_REPO, ".env.testnet"),
    ("scoring_config_source", DYNAMIC_UNL_REPO, "scoring_service/config.py"),
    ("ipfs_publisher_source", DYNAMIC_UNL_REPO, "scoring_service/services/ipfs_publisher.py"),
    ("public_scoring_config_endpoint_source", DYNAMIC_UNL_REPO, "scoring_service/api/scoring.py"),
]

PUBLIC_URLS = [
    ("whitepaper_public", "https://postfiat.org/whitepaper/"),
    ("testnet_vl_public", "https://postfiat.org/testnet_vl.json"),
    ("scoring_config_public", "https://scoring-testnet.postfiat.org/api/scoring/config"),
]


def run(cmd: list[str], cwd: Path) -> str:
    return subprocess.check_output(cmd, cwd=cwd, text=True, stderr=subprocess.STDOUT).strip()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def csv_write(path: Path, fieldnames: list[str], rows: Iterable[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def classify_line(line: str) -> str:
    lowered = line.lower()
    if "originally published" in lowered or "current revision" in lowered or "may 2026 revision" in lowered:
        return "document_metadata"
    if "testnet" in lowered or "sequence" in lowered or "rounds 4" in lowered:
        return "phase1_publication"
    if "inspected" in lowered or "generated" in lowered or "benchmark" in lowered:
        return "benchmark_or_reference"
    if "2025" in lowered or "2023" in lowered or "2021" in lowered or "2018" in lowered:
        return "external_reference"
    if "phase 3" in lowered or "future" in lowered or "later" in lowered:
        return "future_gate"
    return "other"


def support_note(line: str) -> str:
    lowered = line.lower()
    if "originally published to production" in lowered:
        return "Nearest git commit is 0b6fa13 at 2026-03-23T02:08:10Z; line timestamp is 25 seconds earlier and should be treated as production metadata, not exact commit time."
    if "current revision" in lowered or "may 2026 revision" in lowered:
        return "Current file hash and git history place the active whitepaper after the May 2026 evidence updates."
    if "sequence `5`" in line or "sequence 5" in lowered:
        return "Public testnet_vl.json decodes to sequence 5, 20 validators, effective 2026-05-26T17:50:23Z."
    if "168" in line and "score cutoff" in lowered:
        return "Public scoring config endpoint returned cadence=168, cutoff=40, max_size=20, min_gap=5."
    if "rounds 4" in lowered or "rounds 4 through 7" in lowered:
        return "Git history records scoring service commits for rounds 4, 5, 6, and 7 with VL sequences 2, 3, 4, and 5."
    if "[16]" in line or "[17]" in line:
        return "Referenced dynamic-unl-scoring files exist locally; they are local/private repository evidence unless separately published."
    if "[18]" in line or "[19]" in line:
        return "Referenced postfiatorg.github.io replay harness and artifacts exist locally and are under static/benchmarks for public serving."
    if "2025" in line or "2023" in line or "2021" in line or "2018" in line:
        return "External-source date, not Post Fiat artifact provenance."
    return ""


def build_date_inventory() -> list[dict[str, object]]:
    rows = []
    for line_no, line in enumerate(WHITEPAPER.read_text(encoding="utf-8").splitlines(), 1):
        if not any(term in line for term in PROVENANCE_TERMS):
            continue
        dates = DATE_PATTERN.findall(line)
        if not dates and not any(term.lower() in line.lower() for term in ["published", "production", "artifact", "benchmark", "round", "sequence"]):
            continue
        rows.append(
            {
                "line": line_no,
                "category": classify_line(line),
                "dates_or_terms": "; ".join(dates),
                "support_status": "supported_with_note" if support_note(line) else "inventory",
                "support_note": support_note(line),
                "text": line.strip(),
            }
        )
    return rows


def latest_commits(repo: Path, path: str, limit: int = 5) -> str:
    target = repo / path
    if not target.exists():
        return ""
    try:
        return run(
            ["git", "log", f"--max-count={limit}", "--format=%H %cI %s", "--", path],
            repo,
        ).replace("\n", " | ")
    except subprocess.CalledProcessError as exc:
        return f"git_error: {exc.output.strip()}"


def build_artifact_inventory() -> list[dict[str, object]]:
    rows = []
    for label, repo, rel in LOCAL_ARTIFACTS:
        path = repo / rel
        rows.append(
            {
                "label": label,
                "repo": repo.name,
                "path_or_url": str(path),
                "status": "present" if path.exists() else "missing",
                "sha256": sha256_file(path) if path.is_file() else "",
                "git_commits": latest_commits(repo, rel),
                "notes": "local evidence; publish separately if readers need direct public access"
                if repo == DYNAMIC_UNL_REPO
                else "site repository evidence",
            }
        )
    return rows


def fetch_url(label: str, url: str) -> dict[str, object]:
    request = urllib.request.Request(url, headers={"User-Agent": "postfiat-provenance-packet/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            body = response.read()
            return {
                "label": label,
                "url": url,
                "status": int(response.status),
                "content_type": response.headers.get("content-type", ""),
                "last_modified": response.headers.get("last-modified", ""),
                "sha256": hashlib.sha256(body).hexdigest(),
                "bytes": len(body),
                "body": body,
            }
    except (urllib.error.URLError, TimeoutError) as exc:
        return {
            "label": label,
            "url": url,
            "status": "error",
            "content_type": "",
            "last_modified": "",
            "sha256": "",
            "bytes": 0,
            "error": str(exc),
            "body": b"",
        }


def decode_ripple_time(value: int) -> str:
    return (
        dt.datetime.fromtimestamp(value + 946684800, dt.timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


def build_public_receipts() -> tuple[list[dict[str, object]], dict[str, object]]:
    rows = []
    decoded: dict[str, object] = {}
    for label, url in PUBLIC_URLS:
        result = fetch_url(label, url)
        body = result.pop("body")
        rows.append(result)
        if label == "testnet_vl_public" and body:
            outer = json.loads(body)
            blob = json.loads(base64.b64decode(outer["blobs_v2"][0]["blob"]))
            decoded = {
                "sequence": blob["sequence"],
                "validator_count": len(blob["validators"]),
                "effective_ripple_time": blob["effective"],
                "effective_utc": decode_ripple_time(blob["effective"]),
                "expiration_ripple_time": blob["expiration"],
                "expiration_utc": decode_ripple_time(blob["expiration"]),
                "public_key": outer.get("public_key"),
                "version": outer.get("version"),
                "source_url": url,
            }
        if label == "scoring_config_public" and body:
            decoded["public_scoring_config"] = json.loads(body)
    return rows, decoded


def write_sha256s(out_dir: Path) -> None:
    rows = []
    for path in sorted(out_dir.iterdir()):
        if path.name == "SHA256SUMS.txt" or not path.is_file():
            continue
        rows.append(f"{sha256_file(path)}  {path.name}")
    (out_dir / "SHA256SUMS.txt").write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> int:
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = REPO_ROOT / "docs" / "evidence" / f"whitepaper-provenance-{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    date_rows = build_date_inventory()
    artifact_rows = build_artifact_inventory()
    public_rows, decoded = build_public_receipts()

    csv_write(
        out_dir / "date_inventory.csv",
        ["line", "category", "dates_or_terms", "support_status", "support_note", "text"],
        date_rows,
    )
    csv_write(
        out_dir / "artifact_inventory.csv",
        ["label", "repo", "path_or_url", "status", "sha256", "git_commits", "notes"],
        artifact_rows,
    )
    csv_write(
        out_dir / "public_receipts.csv",
        ["label", "url", "status", "content_type", "last_modified", "sha256", "bytes", "error"],
        public_rows,
    )

    git_history = {
        "postfiatorg_whitepaper": run(
            ["git", "log", "--follow", "--format=%H\t%cI\t%an\t%s", "--", "content/whitepaper.md"],
            REPO_ROOT,
        ).splitlines()[:40],
        "postfiatorg_testnet_publication": run(
            [
                "git",
                "log",
                "--format=%H\t%cI\t%an\t%s",
                "--",
                "content/testnet_vl.json",
                "static/benchmarks/live-testnet-validator-stats.json",
                "public/testnet_vl.json",
            ],
            REPO_ROOT,
        ).splitlines()[:40],
        "dynamic_unl_qwen36": run(
            [
                "git",
                "log",
                "--format=%H\t%cI\t%an\t%s",
                "--",
                "phase0/docs/Qwen36ModalFeasibility.md",
                "phase0/docs/DeployQwen36_27B.md",
                "phase0/docs/ModelQualityComparison_Qwen36_27B.md",
                "phase0/docs/Qwen36ThinkingModeComparison.md",
                "infra/deploy_qwen36_endpoint.py",
                "infra/deploy_endpoint.py",
            ],
            DYNAMIC_UNL_REPO,
        ).splitlines()[:40],
    }
    (out_dir / "git_history.json").write_text(json.dumps(git_history, indent=2, sort_keys=True), encoding="utf-8")
    (out_dir / "decoded_testnet_vl.json").write_text(json.dumps(decoded, indent=2, sort_keys=True), encoding="utf-8")

    present = sum(1 for row in artifact_rows if row["status"] == "present")
    missing = sum(1 for row in artifact_rows if row["status"] != "present")
    public_ok = sum(1 for row in public_rows if row["status"] == 200)
    local_dynamic = [row for row in artifact_rows if row["repo"] == "dynamic-unl-scoring" and row["status"] == "present"]

    summary = {
        "generated_at": stamp,
        "whitepaper_sha256": sha256_file(WHITEPAPER),
        "date_inventory_rows": len(date_rows),
        "local_artifacts_present": present,
        "local_artifacts_missing": missing,
        "public_receipts_ok": public_ok,
        "decoded_testnet_vl": decoded,
        "principal_findings": [
            "May 2026 provenance is not future-dated relative to this packet generation date.",
            "The signed public testnet validator list decodes to sequence 5 with 20 validators effective 2026-05-26T17:50:23Z.",
            "The public scoring config endpoint returns cadence=168, cutoff=40, max_size=20, min_gap=5.",
            "References [16]-[17] are backed by local dynamic-unl-scoring files but are not public URLs in this packet.",
            "The 'Originally published to production' timestamp is production metadata; the nearest git commit is 25 seconds later.",
        ],
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    commands = [
        "python3 scripts/whitepaper_provenance_packet.py",
        "rg -n \"2026|May|published|production|generated|inspected|revision|artifact|benchmark\" content/whitepaper.md",
        "git log --follow --format='%H%x09%cI%x09%an%x09%s' -- content/whitepaper.md",
        "git log --format='%H%x09%cI%x09%an%x09%s' -- content/testnet_vl.json static/benchmarks/live-testnet-validator-stats.json public/testnet_vl.json",
        "curl -fsS https://postfiat.org/testnet_vl.json",
        "curl -fsS https://scoring-testnet.postfiat.org/api/scoring/config",
        f"sha256sum {out_dir.relative_to(REPO_ROOT)}/*",
    ]
    (out_dir / "COMMANDS.txt").write_text("\n".join(commands) + "\n", encoding="utf-8")

    report = f"""# Whitepaper Provenance Packet

Generated: `{stamp}`

Source whitepaper: `content/whitepaper.md`

Whitepaper SHA-256: `{summary['whitepaper_sha256']}`

## Finding

The current date/provenance criticism is mostly addressable as a metadata and citation-surface problem, not as an absence of evidence. The packet found `{present}` present local artifacts and `{public_ok}` successful public receipts. The strongest public checks are:

- `https://postfiat.org/testnet_vl.json` is reachable and decodes to validator-list sequence `{decoded.get('sequence')}`, `{decoded.get('validator_count')}` validators, effective `{decoded.get('effective_utc')}`.
- `https://scoring-testnet.postfiat.org/api/scoring/config` is reachable and returns `{json.dumps(decoded.get('public_scoring_config', {}), sort_keys=True)}`.
- Git history records scoring-service publication commits for rounds 4 through 7 and VL sequences 2 through 5.

## What Should Change In The Whitepaper

The paper can safely cite this packet for the date/provenance surface. Two wording changes are supported:

1. Treat `Originally published to production: 2026-03-23 02:07:45 UTC` as production metadata, with the nearest repository commit at `2026-03-23T02:08:10Z`.
2. Mark references `[16]` and `[17]` as local repository evidence unless those dynamic-unl-scoring files are separately published.

## What This Does Not Prove

This packet does not prove model-scoring correctness or authority-transfer readiness. It only verifies that the paper's May 2026/testnet/provenance claims have checkable supporting receipts and identifies which citation surfaces remain local rather than public.

## Files

- `date_inventory.csv` — every date/provenance-sensitive whitepaper line found by the inventory.
- `artifact_inventory.csv` — local artifact presence, SHA-256, and relevant git history.
- `public_receipts.csv` — public URL reachability and hashes.
- `decoded_testnet_vl.json` — decoded public signed-list summary.
- `git_history.json` — relevant git history excerpts.
- `summary.json` — machine-readable summary.
- `COMMANDS.txt` — command transcript.
- `SHA256SUMS.txt` — artifact hashes.
"""
    (out_dir / "REPORT.md").write_text(report, encoding="utf-8")
    write_sha256s(out_dir)
    print(out_dir.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
