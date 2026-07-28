#!/usr/bin/env python3
"""Freeze released binaries, competitors, prompts, tasks, routes, and prices."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path("/home/pfrpc/repos")
RUN_ROOT = (
    REPO_ROOT
    / "pfterminal-perf-probe/runs/release-0124-comprehensive-20260728"
)
VISUAL_SOURCE = (
    REPO_ROOT
    / "pfterminal-perf-probe/runs/opus5-visual-site-20260726T011738Z"
)
QUEUECRAFT = REPO_ROOT / "glm52-agent-bench/tasks/queuecraft"
EVENTFORGE_SOURCE = (
    REPO_ROOT
    / "pfterminal-perf-probe/runs/pfterminal-vs-hermes-vercel-20260702"
)
HERMES_SOURCE = Path("/home/pfrpc/.hermes/hermes-agent")
HERMES_BINARY = Path("/home/pfrpc/.local/bin/hermes")
CLAUDE_BINARY = Path("/home/pfrpc/.npm-global/bin/claude")
OPENROUTER_KEY_FILE = REPO_ROOT / "openrouter_cred.txt"
VERCEL_KEY_FILE = REPO_ROOT / "vercel_proper.txt"
ANTHROPIC_KEY_FILES = [Path("/home/pfrpc/fable4.txt"), Path("/home/pfrpc/fable5.txt")]
OPENAI_KEY_FILE = REPO_ROOT / "openai.txt"


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_tree(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        rel = path.relative_to(root).as_posix()
        digest.update(rel.encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def command(*argv: str) -> str:
    return subprocess.check_output(argv, text=True, stderr=subprocess.STDOUT).strip()


def key_fingerprint(path: Path) -> dict[str, Any]:
    value = path.read_text(encoding="utf-8").strip()
    if not value:
        raise RuntimeError(f"empty key file: {path}")
    return {
        "source_path": str(path),
        "sha256": hashlib.sha256(value.encode()).hexdigest(),
        "length": len(value),
    }


def request_json(url: str, key: str | None = None) -> dict[str, Any]:
    headers = {"Accept": "application/json", "User-Agent": "pfterminal-benchmark/0.1.24"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def model_entry(payload: dict[str, Any], model: str) -> dict[str, Any]:
    rows = payload.get("data")
    if not isinstance(rows, list):
        raise RuntimeError("model catalogue response has no data array")
    entry = next(
        (item for item in rows if isinstance(item, dict) and item.get("id") == model),
        None,
    )
    if not isinstance(entry, dict):
        raise RuntimeError(f"model catalogue does not contain {model}")
    return entry


def extract_release(archive: Path) -> Path:
    subject_root = RUN_ROOT / "subjects/pfterminal"
    if subject_root.exists():
        raise RuntimeError(f"refusing to replace frozen subject: {subject_root}")
    subject_root.mkdir(parents=True)
    with tarfile.open(archive, "r:gz") as bundle:
        members = bundle.getmembers()
        if any(member.name.startswith("/") or ".." in Path(member.name).parts for member in members):
            raise RuntimeError("release archive contains an unsafe member path")
        bundle.extractall(subject_root, filter="data")
    binary = subject_root / "bin/pfterminal"
    if not binary.is_file():
        raise RuntimeError(f"release archive has no expected binary: {binary}")
    binary.chmod(binary.stat().st_mode | 0o111)
    return binary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-archive", type=Path, required=True)
    parser.add_argument("--release-tag", default="rust-v0.1.24")
    parser.add_argument(
        "--release-commit",
        default="81a6ff2f953ef5463e69e018e3c9515d0bd19ca3",
    )
    args = parser.parse_args()

    manifest_path = RUN_ROOT / "manifest.json"
    if manifest_path.exists():
        raise RuntimeError(f"refusing to overwrite frozen manifest: {manifest_path}")
    release_archive = args.release_archive.resolve()
    if not release_archive.is_file():
        raise RuntimeError(f"missing release archive: {release_archive}")

    pfterminal = extract_release(release_archive)
    version = command(str(pfterminal), "--version")
    if "0.1.24" not in version:
        raise RuntimeError(f"unexpected PFTerminal version: {version}")

    openrouter_catalogue = request_json("https://openrouter.ai/api/v1/models")
    vercel_key = VERCEL_KEY_FILE.read_text(encoding="utf-8").strip()
    vercel_catalogue = request_json(
        "https://ai-gateway.vercel.sh/v1/models", vercel_key
    )
    catalogue_dir = RUN_ROOT / "catalogues"
    catalogue_dir.mkdir(parents=True)
    selected_catalogue = {
        "captured_at": now(),
        "openrouter": {
            model: model_entry(openrouter_catalogue, model)
            for model in ("moonshotai/kimi-k3", "z-ai/glm-5.2")
        },
        "vercel": {
            "zai/glm-5.2": model_entry(vercel_catalogue, "zai/glm-5.2")
        },
    }
    (catalogue_dir / "selected_models.json").write_text(
        json.dumps(selected_catalogue, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    frozen_dir = RUN_ROOT / "frozen"
    shutil.copytree(VISUAL_SOURCE / "baseline", frozen_dir / "visual_baseline")
    (frozen_dir / "prompts").mkdir(parents=True)
    shutil.copy2(
        VISUAL_SOURCE / "prompt/task_prompt.md",
        frozen_dir / "prompts/visual_site.md",
    )

    key_files = [
        *ANTHROPIC_KEY_FILES,
        OPENROUTER_KEY_FILE,
        VERCEL_KEY_FILE,
        OPENAI_KEY_FILE,
    ]
    manifest = {
        "created_at": now(),
        "release": {
            "tag": args.release_tag,
            "commit": args.release_commit,
            "archive_path": str(release_archive),
            "archive_sha256": sha256_file(release_archive),
            "binary_path": str(pfterminal),
            "binary_sha256": sha256_file(pfterminal),
            "version": version,
        },
        "hermes": {
            "source_path": str(HERMES_SOURCE),
            "commit": command("git", "-C", str(HERMES_SOURCE), "rev-parse", "HEAD"),
            "status": command("git", "-C", str(HERMES_SOURCE), "status", "--short"),
            "binary_path": str(HERMES_BINARY),
            "binary_sha256": sha256_file(HERMES_BINARY),
            "version": command(str(HERMES_BINARY), "--version").splitlines()[0],
        },
        "claude_code": {
            "binary_path": str(CLAUDE_BINARY),
            "binary_sha256": sha256_file(CLAUDE_BINARY),
            "version": command(str(CLAUDE_BINARY), "--version").splitlines()[0],
        },
        "tasks": {
            "visual_prompt_sha256": sha256_file(
                frozen_dir / "prompts/visual_site.md"
            ),
            "visual_baseline_sha256": sha256_tree(
                frozen_dir / "visual_baseline"
            ),
            "queuecraft_bugged_sha256": sha256_tree(QUEUECRAFT / "bugged"),
            "queuecraft_verifier_sha256": sha256_file(
                QUEUECRAFT / "verifier/verify.py"
            ),
            "eventforge_source_path": str(EVENTFORGE_SOURCE),
            "eventforge_baseline_sha256": sha256_tree(
                REPO_ROOT / "glm52-agent-bench/baseline"
            ),
            "eventforge_prompt_sha256": sha256_file(
                REPO_ROOT / "glm52-agent-bench/task_prompt.md"
            ),
            "eventforge_verifier_sha256": sha256_file(
                REPO_ROOT / "glm52-agent-bench/verifier/verify.py"
            ),
        },
        "catalogue_snapshot": str(catalogue_dir / "selected_models.json"),
        "openai_pricing_snapshot": {
            "path": str(RUN_ROOT / "OPENAI_PRICING_SNAPSHOT.md"),
            "sha256": sha256_file(RUN_ROOT / "OPENAI_PRICING_SNAPSHOT.md"),
        },
        "key_fingerprints": [key_fingerprint(path) for path in key_files],
        "environment": {
            "hostname": os.uname().nodename,
            "python": command("python3", "--version"),
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
