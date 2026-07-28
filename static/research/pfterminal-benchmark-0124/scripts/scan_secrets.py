#!/usr/bin/env python3
"""Fail if any exact campaign credential is present in cached artifacts."""
from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path("/home/pfrpc/repos")
RUN_ROOT = (
    REPO_ROOT
    / "pfterminal-perf-probe/runs/release-0124-comprehensive-20260728"
)
OUTPUT = RUN_ROOT / "secret_scan.json"
SECRET_FILES = [
    Path("/home/pfrpc/fable4.txt"),
    Path("/home/pfrpc/fable5.txt"),
    Path("/home/pfrpc/anthropic_admin.txt"),
    REPO_ROOT / "openai.txt",
    REPO_ROOT / "openrouter_cred.txt",
    REPO_ROOT / "vercel_proper.txt",
]


def main() -> int:
    secrets = [
        path.read_bytes().strip()
        for path in SECRET_FILES
        if path.is_file() and path.read_bytes().strip()
    ]
    hits: list[str] = []
    files = 0
    for path in sorted(item for item in RUN_ROOT.rglob("*") if item.is_file()):
        if path == OUTPUT:
            continue
        files += 1
        data = path.read_bytes()
        if any(secret in data for secret in secrets):
            hits.append(path.relative_to(RUN_ROOT).as_posix())
    result = {
        "run_root": str(RUN_ROOT),
        "secret_files": [str(path) for path in SECRET_FILES],
        "secrets_scanned": len(secrets),
        "files_scanned": files,
        "exact_key_hits": hits,
        "hit_count": len(hits),
    }
    OUTPUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True))
    return 0 if not hits else 1


if __name__ == "__main__":
    raise SystemExit(main())
