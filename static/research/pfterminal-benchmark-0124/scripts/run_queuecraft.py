#!/usr/bin/env python3
"""Run three-wave Queuecraft cells using the proven route benchmark driver."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path("/home/pfrpc/repos")
RUN_ROOT = (
    REPO_ROOT
    / "pfterminal-perf-probe/runs/release-0124-comprehensive-20260728"
)
SOURCE = (
    REPO_ROOT
    / "pfterminal-perf-probe/runs/glm52-route-rebench-20260727"
    / "scripts/run_glm52_route_rebench.py"
)
PFTERMINAL = RUN_ROOT / "subjects/pfterminal/bin/pfterminal"
RELEASE_COMMIT = "81a6ff2f953ef5463e69e018e3c9515d0bd19ca3"

CELLS: dict[str, dict[str, str]] = {
    "glm-vercel": {"route": "vercel", "model": "zai/glm-5.2"},
    "glm-openrouter": {"route": "openrouter", "model": "z-ai/glm-5.2"},
    "kimi-openrouter": {
        "route": "openrouter",
        "model": "moonshotai/kimi-k3",
    },
}


def load_driver():
    spec = importlib.util.spec_from_file_location("route_driver_0124", SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load route driver: {SOURCE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cells", nargs="+", choices=sorted(CELLS), required=True)
    parser.add_argument("--waves", nargs="+", type=int, default=[1, 2, 3])
    args = parser.parse_args()
    if len(set(args.waves)) != len(args.waves) or any(
        wave not in (1, 2, 3) for wave in args.waves
    ):
        raise RuntimeError("waves must be a unique subset of 1, 2, 3")
    if not PFTERMINAL.is_file():
        raise RuntimeError(f"frozen release binary is missing: {PFTERMINAL}")

    driver = load_driver()
    driver.PFT_BINARY = PFTERMINAL
    driver.git_head = lambda: RELEASE_COMMIT
    driver.PFT_WEB_SEARCH_DISABLED = False
    driver.PFT_REASONING_EFFORT = None
    driver.base.TIMEOUT_SECONDS = 20 * 60
    results: list[dict[str, Any]] = []

    for cell in args.cells:
        cell_spec = CELLS[cell]
        route = cell_spec["route"]
        model = cell_spec["model"]
        # Preserve the stopped legacy-alias attempt as invalid evidence and
        # write the corrected Hermes v0.19 campaign to a clean artifact root.
        artifact_cell = (
            "glm-vercel-current-hermes" if cell == "glm-vercel" else cell
        )
        driver.ROUTES[route]["model"] = model
        for wave in args.waves:
            lanes = ["pft", "hermes"] if wave % 2 else ["hermes", "pft"]
            campaign_root = (
                RUN_ROOT
                / "deterministic/queuecraft"
                / artifact_cell
                / f"wave{wave}"
            )
            driver.CAMPAIGN_ROOT = campaign_root
            returncode = driver.run_route(route, [wave], lanes)
            result = {
                "cell": cell,
                "artifact_cell": artifact_cell,
                "route": route,
                "model": model,
                "wave": wave,
                "lanes": lanes,
                "returncode": returncode,
                "artifact_root": str(campaign_root / route),
            }
            results.append(result)
            write_json(
                RUN_ROOT / "deterministic/queuecraft/campaign_index.json",
                results,
            )
            print(json.dumps({"event": "queuecraft_wave_completed", **result}))
    return 0 if all(item["returncode"] == 0 for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
