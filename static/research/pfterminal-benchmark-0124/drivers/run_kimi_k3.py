#!/usr/bin/env python3
"""Kimi K3 via OpenRouter on the queuecraft debugging benchmark.

Two harnesses, one model, one provider:

  lane `pft`    : PFTerminal   -c model_provider="openrouter" -m moonshotai/kimi-k3
  lane `hermes` : Hermes Agent --provider openrouter -m moonshotai/kimi-k3

Lanes run SERIALLY on purpose. Both lanes bill the same OpenRouter key, so the
only sound attribution is a per-wave /api/v1/key usage delta around an otherwise
idle key. Running them concurrently would make cost unattributable.

Task, prompt, and verification are byte-identical to the harness_showdown
queuecraft lane so results are comparable to the Opus 5 campaign.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path("/home/pfrpc/repos")
RUN_ROOT = REPO_ROOT / "pfterminal-perf-probe/runs/kimi-k3-queuecraft-20260727"
TASK_ROOT = REPO_ROOT / "glm52-agent-bench/tasks/queuecraft"
TASK_BASE = TASK_ROOT / "bugged"
VERIFIER = TASK_ROOT / "verifier/verify.py"
VERIFIER_PREFIX = "QUEUECRAFT_VERIFIER_SUMMARY"
EXPECTED_TESTS = 35
EXPECTED_BUGS = 7

MODEL = "moonshotai/kimi-k3"
OPENROUTER_KEY_FILE = REPO_ROOT / "openrouter_cred.txt"
PFTERMINAL = REPO_ROOT / "PfTerminal-telegram-hardening/codex-rs/target/debug/pfterminal"
HERMES = Path("/home/pfrpc/.local/bin/hermes")

TIMEOUT_SECONDS = 45 * 60
# OpenRouter published pricing for moonshotai/kimi-k3, dollars per 1M tokens.
PRICING = {"input_per_1m": 3.00, "output_per_1m": 15.00}


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_key() -> str:
    value = OPENROUTER_KEY_FILE.read_text(encoding="utf-8").strip()
    if not value:
        raise RuntimeError(f"empty key file: {OPENROUTER_KEY_FILE}")
    return value


# --------------------------------------------------------------------------
# OpenRouter accounting
# --------------------------------------------------------------------------

def openrouter_key_usage(key: str) -> dict[str, Any]:
    req = urllib.request.Request("https://openrouter.ai/api/v1/key")
    req.add_header("Authorization", f"Bearer {key}")
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8", errors="replace"))
        data = payload.get("data") or {}
        return {
            "at": utc_now(),
            "usage": data.get("usage"),
            "limit": data.get("limit"),
            "limit_remaining": data.get("limit_remaining"),
        }
    except urllib.error.HTTPError as exc:
        return {"at": utc_now(), "error": f"http_{exc.code}"}
    except Exception as exc:  # noqa: BLE001
        return {"at": utc_now(), "error": type(exc).__name__}


def openrouter_credits(key: str) -> dict[str, Any]:
    """Account-level credit balance.

    The 2026-07-27 first attempt failed because /api/v1/key reported a healthy
    per-key `limit_remaining` while the account itself was overdrawn by $0.17.
    Per-key limits are caps on a shared pool, not a balance. Always check this.
    """
    req = urllib.request.Request("https://openrouter.ai/api/v1/credits")
    req.add_header("Authorization", f"Bearer {key}")
    with urllib.request.urlopen(req, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8", errors="replace"))["data"]
    total = float(data.get("total_credits") or 0)
    used = float(data.get("total_usage") or 0)
    return {"total_credits": total, "total_usage": used,
            "balance_usd": round(total - used, 6)}


def require_credits(key: str, minimum: float = 5.0) -> dict[str, Any]:
    credits = openrouter_credits(key)
    if credits["balance_usd"] < minimum:
        raise RuntimeError(
            f"OpenRouter account balance ${credits['balance_usd']:.4f} is below the "
            f"${minimum:.2f} preflight minimum; refusing to launch"
        )
    return credits


def usage_delta(before: dict[str, Any], after: dict[str, Any]) -> float | None:
    b, a = before.get("usage"), after.get("usage")
    if isinstance(b, (int, float)) and isinstance(a, (int, float)):
        return round(a - b, 6)
    return None


# --------------------------------------------------------------------------
# Task setup, identical to harness_showdown queuecraft
# --------------------------------------------------------------------------

def prepare_workspace(lane: str, wave: int) -> Path:
    workspace = RUN_ROOT / "workspaces" / lane / f"wave{wave}"
    if workspace.exists():
        raise RuntimeError(f"refusing to reuse workspace: {workspace}")
    workspace.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        TASK_BASE, workspace,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"),
    )
    return workspace


def build_prompt(workspace: Path) -> str:
    visible_failure = (workspace / "VISIBLE_FAILURE.txt").read_text(
        encoding="utf-8", errors="replace"
    )
    return "\n".join([
        "Read AGENTS.md, BENCHMARK_TASK.md, and VISIBLE_FAILURE.txt in this repository.",
        "The queuecraft benchmark is failing. Fix product behavior, not just the surface symptom.",
        "Do not modify tests. Do not bypass the verifier. Keep the package standard-library only.",
        "",
        "Start by reproducing the visible failure:",
        "PYTHONPATH=src python3 -m unittest discover -s tests -v",
        "",
        "Visible failing output:",
        "```",
        visible_failure[-5000:],
        "```",
        "",
        "When done, run:",
        "PYTHONPATH=src python3 -m unittest discover -s tests -v",
        f"python3 {VERIFIER} {workspace}",
        "Finish by saying BENCH_DONE.",
    ])


# --------------------------------------------------------------------------
# Verification
# --------------------------------------------------------------------------

def run_check(cmd: list[str], cwd: Path, env: dict[str, str], out: Path, timeout: int) -> dict[str, Any]:
    out.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    with out.open("wb") as handle:
        proc = subprocess.Popen(
            cmd, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
            stdout=handle, stderr=subprocess.STDOUT, start_new_session=True,
        )
        try:
            rc = proc.wait(timeout=timeout)
            timed_out = False
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(proc.pid, signal.SIGKILL)
            rc = proc.wait()
    return {"returncode": rc, "timed_out": timed_out,
            "seconds": round(time.monotonic() - started, 3), "log": str(out)}


def parse_summary(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    marker = VERIFIER_PREFIX + " "
    for line in reversed(text.splitlines()):
        if line.startswith(marker):
            try:
                return json.loads(line.split(" ", 1)[1])
            except json.JSONDecodeError:
                break
    return {"ok": False, "tests_passed": 0, "tests_total": EXPECTED_TESTS,
            "error": "summary_missing"}


def sha256_file(path: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tests_untouched(workspace: Path) -> dict[str, Any]:
    base, live = TASK_BASE / "tests", workspace / "tests"
    base_files = {p.relative_to(base) for p in base.rglob("*.py")} if base.exists() else set()
    live_files = {p.relative_to(live) for p in live.rglob("*.py")} if live.exists() else set()
    modified = [str(r) for r in sorted(base_files & live_files)
                if sha256_file(base / r) != sha256_file(live / r)]
    missing = [str(r) for r in sorted(base_files - live_files)]
    extra = [str(r) for r in sorted(live_files - base_files)]
    return {"modified": modified, "missing": missing, "extra": extra,
            "test_modified": bool(modified or missing or extra)}


def verify(workspace: Path, result_dir: Path) -> dict[str, Any]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(workspace / "src")
    visible = run_check([sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"],
                        workspace, env, result_dir / "visible.stdout", 180)
    # Snapshot the tests tree BEFORE the verifier runs. queuecraft's verifier
    # injects its own private test modules into workspace/tests, so a filesystem
    # diff taken afterwards always reports them as "extra" and would produce a
    # false tamper finding.
    diff = tests_untouched(workspace)
    hidden = run_check([sys.executable, "-B", str(VERIFIER), str(workspace)],
                       workspace, env, result_dir / "hidden.stdout", 240)
    summary = parse_summary(result_dir / "hidden.stdout")
    # queuecraft is a debugging task: the verifier is authoritative for both
    # pass/fail and tamper detection, exactly as in harness_showdown.
    result = {
        "ok": bool(summary.get("ok")) and not bool(summary.get("test_modified")),
        "test_modified_verifier": bool(summary.get("test_modified")),
        "test_diff_advisory_pre_verifier": diff,
        "tests_passed": summary.get("tests_passed"),
        "tests_total": summary.get("tests_total") or EXPECTED_TESTS,
        "bugs_fixed": summary.get("bug_probes_passed"),
        "bugs_total": summary.get("bug_probes_total") or EXPECTED_BUGS,
        "summary": summary,
        "visible": visible,
        "hidden": hidden,
    }
    write_json(result_dir / "verify.json", result)
    return result


# --------------------------------------------------------------------------
# Agent lanes
# --------------------------------------------------------------------------

def base_env(key: str) -> dict[str, str]:
    env = os.environ.copy()
    env.update({"OPENROUTER_API_KEY": key, "NO_COLOR": "1",
                "PYTHONDONTWRITEBYTECODE": "1"})
    for stale in ("ANTHROPIC_API_KEY", "AI_GATEWAY_API_KEY",
                  "VERCEL_AI_GATEWAY_API_KEY", "HTTPS_PROXY", "https_proxy",
                  "HTTP_PROXY", "http_proxy", "ALL_PROXY", "all_proxy"):
        env.pop(stale, None)
    return env


def lane_command(lane: str, workspace: Path, result_dir: Path, prompt: str,
                 key: str) -> tuple[list[str], dict[str, str], Path, Path]:
    env = base_env(key)
    if lane == "pft":
        codex_home = result_dir / "codex-home"
        codex_home.mkdir(parents=True, exist_ok=True)
        env["CODEX_HOME"] = str(codex_home)
        env["PFTERMINAL_TRACE_STREAM_TIMING"] = "1"
        env["PFTERMINAL_DUMP_CHAT_REQUEST"] = str(result_dir / "pfterminal.request.json")
        cmd = [
            str(PFTERMINAL), "exec", "--json", "--skip-git-repo-check",
            "--dangerously-bypass-approvals-and-sandbox",
            "-C", str(workspace),
            "-c", 'model_provider="openrouter"',
            "-m", MODEL,
            prompt,
        ]
        return cmd, env, result_dir / "pfterminal.stdout", result_dir / "pfterminal.stderr"

    hermes_home = result_dir / "hermes-home"
    hermes_home.mkdir(parents=True, exist_ok=True)
    env["HERMES_HOME"] = str(hermes_home)
    cmd = [
        str(HERMES), "--provider", "openrouter", "-m", MODEL,
        "--yolo", "--accept-hooks", "--ignore-user-config", "-z", prompt,
    ]
    return cmd, env, result_dir / "hermes.stdout", result_dir / "hermes.stderr"


def run_wave(lane: str, wave: int, key: str) -> dict[str, Any]:
    workspace = prepare_workspace(lane, wave)
    result_dir = RUN_ROOT / "results" / lane / f"wave{wave}"
    result_dir.mkdir(parents=True, exist_ok=True)
    prompt = build_prompt(workspace)
    (result_dir / "prompt.txt").write_text(prompt, encoding="utf-8")

    cmd, env, stdout_path, stderr_path = lane_command(lane, workspace, result_dir, prompt, key)

    before = openrouter_key_usage(key)
    started_at, started = utc_now(), time.monotonic()
    with stdout_path.open("wb") as so, stderr_path.open("wb") as se:
        proc = subprocess.Popen(cmd, cwd=workspace, env=env, stdin=subprocess.DEVNULL,
                                stdout=so, stderr=se, start_new_session=True)
        timed_out = False
        try:
            returncode = proc.wait(timeout=TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                returncode = proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                returncode = proc.wait()
    wall = round(time.monotonic() - started, 3)
    ended_at = utc_now()
    time.sleep(20)  # let OpenRouter settle the final generations
    after = openrouter_key_usage(key)

    verification = verify(workspace, result_dir)

    record = {
        "lane": lane,
        "wave": wave,
        "model": MODEL,
        "provider": "openrouter",
        "started_at": started_at,
        "ended_at": ended_at,
        "wall_seconds": wall,
        "returncode": returncode,
        "timed_out": timed_out,
        "workspace": str(workspace),
        "result_dir": str(result_dir),
        "openrouter_usage_before": before,
        "openrouter_usage_after": after,
        "openrouter_cost_usd": usage_delta(before, after),
        "verification": {k: verification[k] for k in
                         ("ok", "tests_passed", "tests_total", "bugs_fixed",
                          "bugs_total", "test_modified_verifier")},
        "argv_redacted": [c if c != prompt else "<PROMPT>" for c in cmd],
    }
    write_json(result_dir / "agent_run.json", record)
    print(json.dumps({"event": "wave_completed", **{k: record[k] for k in
                      ("lane", "wave", "wall_seconds", "returncode",
                       "openrouter_cost_usd")},
                      "ok": verification["ok"],
                      "tests": f"{verification['tests_passed']}/{verification['tests_total']}",
                      "bugs": f"{verification['bugs_fixed']}/{verification['bugs_total']}"},
                     sort_keys=True), flush=True)
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lanes", nargs="+", default=["pft", "hermes"])
    parser.add_argument("--waves", nargs="+", type=int, default=[1])
    args = parser.parse_args()

    for binary in (PFTERMINAL, HERMES):
        if not binary.exists():
            raise RuntimeError(f"missing binary: {binary}")
    key = read_key()
    credits = require_credits(key)
    print(json.dumps({"event": "preflight_credits", **credits}, sort_keys=True), flush=True)

    manifest = {
        "created_at": utc_now(),
        "preflight_credits": credits,
        "run_root": str(RUN_ROOT),
        "task": "queuecraft",
        "task_base": str(TASK_BASE),
        "model": MODEL,
        "provider": "openrouter",
        "pricing_per_1m": PRICING,
        "lanes": args.lanes,
        "waves": args.waves,
        "pfterminal": {"path": str(PFTERMINAL), "sha256": sha256_file(PFTERMINAL)},
        "hermes": {"path": str(HERMES), "version": "0.13.0"},
        "key_file": str(OPENROUTER_KEY_FILE),
        "note": "lanes run serially so OpenRouter key usage deltas are attributable",
    }
    tag = "_".join(args.lanes) + "_w" + "_".join(map(str, args.waves))
    write_json(RUN_ROOT / f"manifest_{tag}.json", manifest)

    records: list[dict[str, Any]] = []
    for wave in args.waves:
        for lane in args.lanes:
            records.append(run_wave(lane, wave, key))
    write_json(RUN_ROOT / f"records_{tag}.json", records)
    return 0 if all(r["returncode"] == 0 for r in records) else 1


if __name__ == "__main__":
    raise SystemExit(main())
