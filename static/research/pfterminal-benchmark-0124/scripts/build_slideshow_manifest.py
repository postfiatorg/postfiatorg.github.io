#!/usr/bin/env python3
"""Index cached benchmark evidence for later slide-deck production."""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"not a PNG: {path}")
    return struct.unpack(">II", header[16:24])


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> int:
    screenshots: list[dict[str, Any]] = []
    for path in sorted(
        (RUN_ROOT / "visual/results").glob("*/*/wave*/captures/*.png")
    ):
        parts = path.relative_to(RUN_ROOT / "visual/results").parts
        cell, lane, wave = parts[0], parts[1], parts[2]
        width, height = png_dimensions(path)
        screenshots.append(
            {
                "cell": cell,
                "lane": lane,
                "wave": int(wave.removeprefix("wave")),
                "capture": path.stem,
                "width": width,
                "height": height,
                "sha256": sha256(path),
                "path": str(path.relative_to(RUN_ROOT)),
                "suggested_slide_role": (
                    "desktop comparison"
                    if path.stem in {"desktop_hero", "desktop_full"}
                    else "responsive comparison"
                    if path.stem.startswith("mobile_")
                    else "interaction evidence"
                ),
            }
        )

    evidence_paths = [
        "RUNBOOK.md",
        "MATRIX.json",
        "manifest.json",
        "summary.json",
        "summary.csv",
        "REPORT.md",
        "secret_scan.json",
        "RELEASE_EVIDENCE.md",
        "OPENAI_PRICING_SNAPSHOT.md",
        "visual/blind/campaign_summary.json",
        "visual/image_generation_audit.json",
        "visual/lane_conformance_audit.json",
        "visual/opus/admin_costs.json",
    ]
    evidence = []
    for relative in evidence_paths:
        path = RUN_ROOT / relative
        if path.is_file():
            evidence.append(
                {
                    "path": relative,
                    "sha256": sha256(path),
                    "bytes": path.stat().st_size,
                }
            )
    payload = {
        "campaign": "pfterminal-0.1.24-comprehensive-20260728",
        "subject": "PFTerminal 0.1.24 release artifact",
        "screenshots": screenshots,
        "evidence": evidence,
        "notes": [
            "Use summary.json for chart data rather than transcribing REPORT.md.",
            "Preserve blind mappings until after visual verdicts are finalized.",
            "Agent cost, required image output estimate, and judge overhead are separate.",
            "Use visual/image_generation_audit.json for confirmed discarded "
            "outputs and timeout upper bounds.",
            "Do not chart conformance-invalid runs as matched-route successes; "
            "use visual/lane_conformance_audit.json for exclusions.",
            "Do not include artifacts under a directory marked INVALID_HARNESS.md.",
        ],
    }
    output = RUN_ROOT / "slideshow/manifest.json"
    write_json(output, payload)
    print(
        json.dumps(
            {
                "output": str(output),
                "screenshots": len(screenshots),
                "evidence_files": len(evidence),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
