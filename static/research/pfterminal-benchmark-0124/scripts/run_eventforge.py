#!/usr/bin/env python3
"""Run EventForge on released PFTerminal and Hermes over OpenRouter."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import sys
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
TASK_BASE = REPO_ROOT / "glm52-agent-bench/baseline"
TASK_PROMPT = REPO_ROOT / "glm52-agent-bench/task_prompt.md"
VERIFIER = REPO_ROOT / "glm52-agent-bench/verifier/verify.py"
PFTERMINAL = RUN_ROOT / "subjects/pfterminal/bin/pfterminal"
RELEASE_COMMIT = "81a6ff2f953ef5463e69e018e3c9515d0bd19ca3"

CELLS = {
    "glm-openrouter": "z-ai/glm-5.2",
    "kimi-openrouter": "moonshotai/kimi-k3",
}


def load_driver():
    spec = importlib.util.spec_from_file_location("eventforge_route_driver", SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load route driver: {SOURCE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def hash_tree(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        rel = path.relative_to(root).as_posix()
        digest.update(rel.encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def build_prompt(workspace: Path) -> str:
    return "\n".join(
        [
            "Read AGENTS.md and BENCHMARK_TASK.md in this repository.",
            "Implement the EventForge contract in src/eventforge without editing "
            "tests or bypassing the verifier.",
            "Run PYTHONPATH=src python3 -m unittest discover -s tests -v.",
            f"Then run python3 {VERIFIER} {workspace}.",
            "Fix failures until both pass. Finish by saying BENCH_DONE.",
        ]
    )


def make_verify(base):
    def verify(workspace: Path, result_dir: Path) -> dict[str, Any]:
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONPATH"] = str(workspace / "src")
        baseline_tests = hash_tree(TASK_BASE / "tests")
        after_agent_tests = hash_tree(workspace / "tests")
        visible = base.run_check(
            [
                sys.executable,
                "-B",
                "-m",
                "unittest",
                "discover",
                "-s",
                "tests",
                "-v",
            ],
            workspace,
            env,
            result_dir / "visible.stdout",
            180,
        )
        hidden = base.run_check(
            [sys.executable, "-B", str(VERIFIER), str(workspace)],
            workspace,
            env,
            result_dir / "hidden.stdout",
            240,
        )
        tests_untouched = baseline_tests == after_agent_tests
        ok = (
            visible["returncode"] == 0
            and hidden["returncode"] == 0
            and tests_untouched
        )
        result = {
            "ok": ok,
            "tests_passed": 1 if visible["returncode"] == 0 else 0,
            "tests_total": 1,
            "bugs_fixed": 1 if hidden["returncode"] == 0 else 0,
            "bugs_total": 1,
            "test_modified_verifier": not tests_untouched,
            "tests_sha256_baseline": baseline_tests,
            "tests_sha256_after_agent": after_agent_tests,
            "visible": visible,
            "hidden": hidden,
        }
        base.write_json(result_dir / "verify.json", result)
        return result

    return verify


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
    base = driver.base
    base.TIMEOUT_SECONDS = 20 * 60
    base.TASK_BASE = TASK_BASE
    base.VERIFIER = VERIFIER
    original_prepare_workspace = base.prepare_workspace

    def prepare_workspace(lane: str, wave: int) -> Path:
        workspace = original_prepare_workspace(lane, wave)
        shutil.copy2(TASK_PROMPT, workspace / "BENCHMARK_TASK.md")
        return workspace

    base.prepare_workspace = prepare_workspace
    base.build_prompt = build_prompt
    base.verify = make_verify(base)
    results: list[dict[str, Any]] = []

    for cell in args.cells:
        model = CELLS[cell]
        driver.ROUTES["openrouter"]["model"] = model
        for wave in args.waves:
            lanes = ["pft", "hermes"] if wave % 2 else ["hermes", "pft"]
            campaign_root = (
                RUN_ROOT
                / "deterministic/eventforge"
                / cell
                / f"wave{wave}"
            )
            driver.CAMPAIGN_ROOT = campaign_root
            returncode = driver.run_route("openrouter", [wave], lanes)
            result = {
                "cell": cell,
                "route": "openrouter",
                "model": model,
                "wave": wave,
                "lanes": lanes,
                "returncode": returncode,
                "artifact_root": str(campaign_root / "openrouter"),
            }
            results.append(result)
            write_json(
                RUN_ROOT / "deterministic/eventforge/campaign_index.json",
                results,
            )
            print(json.dumps({"event": "eventforge_wave_completed", **result}))
    return 0 if all(item["returncode"] == 0 for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
