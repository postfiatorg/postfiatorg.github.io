#!/usr/bin/env python3
"""Run frozen website cells on released PFTerminal and matched competitors."""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import shutil
import signal
import sqlite3
import subprocess
import time
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path("/home/pfrpc/repos")
RUN_ROOT = (
    REPO_ROOT
    / "pfterminal-perf-probe/runs/release-0124-comprehensive-20260728"
)
FROZEN = RUN_ROOT / "frozen"
BASELINE = FROZEN / "visual_baseline"
PROMPT = FROZEN / "prompts/visual_site.md"
PFTERMINAL = RUN_ROOT / "subjects/pfterminal/bin/pfterminal"
HERMES = Path("/home/pfrpc/.local/bin/hermes")
CLAUDE = Path("/home/pfrpc/.npm-global/bin/claude")
VERIFY_PY = (
    REPO_ROOT
    / "pfterminal-perf-probe/runs/opus5-visual-site-20260726T011738Z"
    / ".venv/bin/python"
)
VERIFY_SCRIPT = (
    REPO_ROOT
    / "pfterminal-perf-probe/runs/opus5-visual-site-20260726T011738Z"
    / "scripts/verify_site.py"
)
OPENAI_KEY = REPO_ROOT / "openai.txt"
OPENROUTER_KEY = REPO_ROOT / "openrouter_cred.txt"
ANTHROPIC_KEYS = {
    "pft": Path("/home/pfrpc/fable4.txt"),
    "cc": Path("/home/pfrpc/fable5.txt"),
}
TIMEOUT_SECONDS = 45 * 60

CELLS: dict[str, dict[str, str]] = {
    "opus": {
        "model": "claude-opus-5",
        "provider": "anthropic",
        "opponent": "cc",
    },
    "kimi-openrouter": {
        "model": "moonshotai/kimi-k3",
        "provider": "openrouter",
        "opponent": "hermes",
    },
    "glm-openrouter": {
        "model": "z-ai/glm-5.2",
        "provider": "openrouter",
        "opponent": "hermes",
    },
}


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )


def read_secret(path: Path) -> str:
    value = path.read_text(encoding="utf-8").strip()
    if not value:
        raise RuntimeError(f"empty secret file: {path}")
    return value


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


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def openrouter_snapshot(key: str) -> dict[str, Any]:
    request = urllib.request.Request(
        "https://openrouter.ai/api/v1/key",
        headers={"Authorization": f"Bearer {key}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(
            response.read().decode("utf-8", errors="replace")
        ).get("data", {})
    return {
        "at": now(),
        "usage": data.get("usage"),
        "limit": data.get("limit"),
        "limit_remaining": data.get("limit_remaining"),
    }


def cost_delta(before: dict[str, Any], after: dict[str, Any]) -> float | None:
    left, right = before.get("usage"), after.get("usage")
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return round(float(right) - float(left), 6)
    return None


def base_env(cell: str, lane: str) -> dict[str, str]:
    env = os.environ.copy()
    for name in (
        "ANTHROPIC_API_KEY",
        "OPENROUTER_API_KEY",
        "AI_GATEWAY_API_KEY",
        "VERCEL_AI_GATEWAY_API_KEY",
        "CODEX_HOME",
        "HERMES_HOME",
        "CLAUDE_CONFIG_DIR",
        "HTTPS_PROXY",
        "https_proxy",
        "HTTP_PROXY",
        "http_proxy",
        "ALL_PROXY",
        "all_proxy",
    ):
        env.pop(name, None)
    env.update(
        {
            "OPENAI_API_KEY": read_secret(OPENAI_KEY),
            "NO_COLOR": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
        }
    )
    if cell == "opus":
        env["ANTHROPIC_API_KEY"] = read_secret(ANTHROPIC_KEYS[lane])
    else:
        env["OPENROUTER_API_KEY"] = read_secret(OPENROUTER_KEY)
    return env


def prepare_workspace(cell: str, lane: str, wave: int) -> Path:
    workspace = RUN_ROOT / "visual/workspaces" / cell / lane / f"wave{wave}"
    if workspace.exists():
        raise RuntimeError(f"refusing to reuse workspace: {workspace}")
    workspace.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(BASELINE, workspace)
    shutil.copy2(PROMPT, workspace / "BENCHMARK_TASK.md")
    return workspace


def lane_command(
    cell: str,
    lane: str,
    workspace: Path,
    result_dir: Path,
) -> tuple[list[str], dict[str, str], Path, Path]:
    spec = CELLS[cell]
    model = spec["model"]
    provider = spec["provider"]
    prompt = PROMPT.read_text(encoding="utf-8")
    env = base_env(cell, lane)

    if lane == "pft":
        codex_home = result_dir / "codex-home"
        codex_home.mkdir(parents=True)
        env["CODEX_HOME"] = str(codex_home)
        env["PFTERMINAL_TRACE_STREAM_TIMING"] = "1"
        dump_name = (
            "pfterminal.anthropic.request.json"
            if provider == "anthropic"
            else "pfterminal.chat.request.json"
        )
        dump_env = (
            "PFTERMINAL_DUMP_ANTHROPIC_REQUEST"
            if provider == "anthropic"
            else "PFTERMINAL_DUMP_CHAT_REQUEST"
        )
        env[dump_env] = str(result_dir / dump_name)
        command = [
            str(PFTERMINAL),
            "exec",
            "--json",
            "--skip-git-repo-check",
            "--dangerously-bypass-approvals-and-sandbox",
            "-C",
            str(workspace),
            "-c",
            f'model_provider="{provider}"',
            "-m",
            model,
            prompt,
        ]
        return (
            command,
            env,
            result_dir / "pfterminal.stdout",
            result_dir / "pfterminal.stderr",
        )

    if lane == "cc":
        config = result_dir / "claude-config"
        config.mkdir(parents=True)
        env["CLAUDE_CONFIG_DIR"] = str(config)
        command = [
            str(CLAUDE),
            "--bare",
            "--print",
            "--output-format",
            "json",
            "--model",
            model,
            "--dangerously-skip-permissions",
            "--max-budget-usd",
            "8",
            prompt,
        ]
        return (
            command,
            env,
            result_dir / "claude.stdout",
            result_dir / "claude.stderr",
        )

    hermes_home = result_dir / "hermes-home"
    hermes_home.mkdir(parents=True)
    env["HERMES_HOME"] = str(hermes_home)
    command = [
        str(HERMES),
        "--provider",
        provider,
        "-m",
        model,
        "--yolo",
        "--accept-hooks",
        "--ignore-user-config",
        "-z",
        prompt,
    ]
    return (
        command,
        env,
        result_dir / "hermes.stdout",
        result_dir / "hermes.stderr",
    )


def run_process(
    command: list[str],
    workspace: Path,
    env: dict[str, str],
    stdout_path: Path,
    stderr_path: Path,
) -> dict[str, Any]:
    started_at = now()
    started = time.monotonic()
    with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
        process = subprocess.Popen(
            command,
            cwd=workspace,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=stdout,
            stderr=stderr,
            start_new_session=True,
        )
        timed_out = False
        try:
            returncode = process.wait(timeout=TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGTERM)
            try:
                returncode = process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                returncode = process.wait()
    return {
        "started_at": started_at,
        "ended_at": now(),
        "wall_seconds": round(time.monotonic() - started, 3),
        "returncode": returncode,
        "timed_out": timed_out,
    }


def verify(workspace: Path, result_dir: Path) -> dict[str, Any]:
    capture_dir = result_dir / "captures"
    command = [
        str(VERIFY_PY),
        str(VERIFY_SCRIPT),
        str(workspace),
        "--result-dir",
        str(capture_dir),
    ]
    completed = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=15 * 60,
    )
    (result_dir / "verify.stdout").write_text(
        completed.stdout, encoding="utf-8"
    )
    summary_path = capture_dir / "verification.json"
    summary: dict[str, Any] = {}
    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    return {
        "returncode": completed.returncode,
        "ok": completed.returncode == 0 and bool(summary.get("ok")),
        "summary_path": str(summary_path),
        "summary": summary,
    }


def hermes_telemetry(result_dir: Path) -> dict[str, Any]:
    database = result_dir / "hermes-home/state.db"
    if not database.exists():
        return {"error": "state_db_missing"}
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    try:
        row = connection.execute(
            "SELECT model, model_config, message_count, tool_call_count, "
            "api_call_count, input_tokens, cache_read_tokens, "
            "cache_write_tokens, output_tokens, reasoning_tokens, "
            "actual_cost_usd, estimated_cost_usd, cost_status, cost_source "
            "FROM sessions ORDER BY started_at DESC LIMIT 1"
        ).fetchone()
    except sqlite3.Error as exc:
        return {"error": f"sqlite_{type(exc).__name__}"}
    finally:
        connection.close()
    return dict(row) if row else {"error": "session_missing"}


def route_evidence(cell: str, lane: str, result_dir: Path) -> dict[str, Any]:
    spec = CELLS[cell]
    if lane == "pft":
        filename = (
            "pfterminal.anthropic.request.json"
            if cell == "opus"
            else "pfterminal.chat.request.json"
        )
        path = result_dir / filename
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            payload = {}
        return {
            "path": str(path),
            "model": payload.get("model"),
            "reasoning": payload.get("reasoning"),
            "thinking": payload.get("thinking"),
            "route_verified": payload.get("model") == spec["model"],
        }
    if lane == "hermes":
        telemetry = hermes_telemetry(result_dir)
        return {
            "model": telemetry.get("model"),
            "model_config": telemetry.get("model_config"),
            "route_verified": spec["model"] in str(telemetry.get("model") or ""),
            "telemetry": telemetry,
        }
    try:
        payload = json.loads(
            (result_dir / "claude.stdout").read_text(encoding="utf-8")
        )
    except Exception:
        payload = {}
    usage = payload.get("modelUsage") or {}
    return {
        "model": sorted(usage)[-1] if usage else None,
        "route_verified": spec["model"] in usage,
        "client_cost_usd": payload.get("total_cost_usd"),
    }


def run_lane(cell: str, lane: str, wave: int) -> dict[str, Any]:
    workspace = prepare_workspace(cell, lane, wave)
    result_dir = RUN_ROOT / "visual/results" / cell / lane / f"wave{wave}"
    result_dir.mkdir(parents=True)
    command, env, stdout_path, stderr_path = lane_command(
        cell, lane, workspace, result_dir
    )
    billing_before = None
    if cell != "opus":
        billing_before = openrouter_snapshot(read_secret(OPENROUTER_KEY))
        write_json(result_dir / "billing_before.json", billing_before)
    record = run_process(
        command, workspace, env, stdout_path, stderr_path
    )
    if cell != "opus":
        time.sleep(20)
        billing_after = openrouter_snapshot(read_secret(OPENROUTER_KEY))
        write_json(result_dir / "billing_after.json", billing_after)
        record["billing"] = {
            "source": "OpenRouter /api/v1/key usage delta",
            "cost_usd": cost_delta(billing_before or {}, billing_after),
            "before": billing_before,
            "after": billing_after,
        }
    verification = verify(workspace, result_dir)
    record.update(
        {
            "cell": cell,
            "lane": lane,
            "wave": wave,
            "model": CELLS[cell]["model"],
            "workspace": str(workspace),
            "workspace_sha256_after": sha256_tree(workspace),
            "result_dir": str(result_dir),
            "route": route_evidence(cell, lane, result_dir),
            "verification": verification,
            "argv_redacted": [
                "<PROMPT>" if item == PROMPT.read_text(encoding="utf-8") else item
                for item in command
            ],
        }
    )
    write_json(result_dir / "agent_run.json", record)
    print(
        json.dumps(
            {
                "event": "visual_lane_completed",
                "cell": cell,
                "lane": lane,
                "wave": wave,
                "wall_seconds": record["wall_seconds"],
                "returncode": record["returncode"],
                "verified": verification["ok"],
                "cost_usd": (record.get("billing") or {}).get("cost_usd"),
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return record


def run_wave(cell: str, wave: int) -> list[dict[str, Any]]:
    opponent = CELLS[cell]["opponent"]
    lanes = ["pft", opponent]
    if cell == "opus":
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(run_lane, cell, lane, wave): lane for lane in lanes
            }
            return [future.result() for future in futures]
    if wave % 2 == 0:
        lanes.reverse()
    return [run_lane(cell, lane, wave) for lane in lanes]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cells", nargs="+", choices=sorted(CELLS), required=True)
    parser.add_argument("--waves", nargs="+", type=int, default=[1, 2, 3])
    args = parser.parse_args()
    if len(set(args.waves)) != len(args.waves) or any(
        wave not in (1, 2, 3) for wave in args.waves
    ):
        raise RuntimeError("waves must be a unique subset of 1, 2, 3")
    for path in (
        PFTERMINAL,
        HERMES,
        CLAUDE,
        VERIFY_PY,
        VERIFY_SCRIPT,
        BASELINE,
        PROMPT,
        OPENAI_KEY,
    ):
        if not path.exists():
            raise RuntimeError(f"missing benchmark dependency: {path}")

    records: list[dict[str, Any]] = []
    for cell in args.cells:
        cell_manifest = RUN_ROOT / "visual" / cell / "manifest.json"
        if cell_manifest.exists():
            raise RuntimeError(f"refusing to reuse visual cell: {cell_manifest}")
        write_json(
            cell_manifest,
            {
                "created_at": now(),
                "cell": cell,
                **CELLS[cell],
                "waves": args.waves,
                "pfterminal_sha256": sha256_file(PFTERMINAL),
                "opponent_sha256": sha256_file(
                    CLAUDE if CELLS[cell]["opponent"] == "cc" else HERMES
                ),
                "prompt_sha256": sha256_file(PROMPT),
                "baseline_sha256": sha256_tree(BASELINE),
                "ordering": (
                    "concurrent on distinct keys"
                    if cell == "opus"
                    else "serial, alternating lane order, shared key billing deltas"
                ),
            },
        )
        for wave in args.waves:
            records.extend(run_wave(cell, wave))
            write_json(RUN_ROOT / "visual/records.json", records)
    return 0 if all(
        record["returncode"] == 0
        and record["verification"]["ok"]
        and record["route"]["route_verified"]
        for record in records
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
