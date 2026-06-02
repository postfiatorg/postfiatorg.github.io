#!/usr/bin/env python3
"""Shared helpers for XRPL amendment lifecycle replay artifacts."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

LANES = ("vote_outcome", "vote_state", "default_vote", "triage")

LANE_LABEL_FIELD = {
    "vote_outcome": "xrpl_vote_recommendation",
    "vote_state": "vote_state",
    "default_vote": "source_default_vote",
    "triage": "route",
}

LANE_ALLOWED_LABELS = {
    "vote_outcome": ["YES", "NO"],
    "vote_state": ["ENABLED", "NO_MAJORITY", "MAJORITY_ACTIVE", "MAJORITY_LOST", "VETOED_OR_RETIRED", "UNKNOWN"],
    "default_vote": ["YES", "NO", "UNKNOWN"],
    "triage": ["PROCEED", "HOLD_FOR_CHALLENGE", "DELAY_FOR_FIX", "REJECT"],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_text(text: str) -> str:
    return sha_bytes(text.encode("utf-8"))


def sha_json(data: Any) -> str:
    return sha_text(json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":")))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "item"


def clean_markdown(value: str) -> str:
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"`([^`]+)`", r"\1", value)
    value = value.replace("**", "").replace("*", "")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def write_sha256s(root: Path) -> str:
    rows: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name == "SHA256SUMS.txt":
            continue
        rel = path.relative_to(root).as_posix()
        rows.append(f"{sha_bytes(path.read_bytes())}  {rel}")
    text = "\n".join(rows) + "\n"
    (root / "SHA256SUMS.txt").write_text(text, encoding="utf-8")
    return sha_text(text)


def artifact_path(value: str | Path) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path.resolve()
