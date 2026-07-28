#!/usr/bin/env python3
"""Matched GLM 5.2 Queuecraft benchmark on Vercel and OpenRouter.

The workload implementation is imported from the existing Queuecraft runner.
This wrapper supplies current first-class provider routes, correct route billing
labels, immutable pricing snapshots, and comparable token telemetry for both
PFTerminal and Hermes Agent.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sqlite3
import subprocess
import urllib.request
from pathlib import Path
from typing import Any

REPO_ROOT = Path("/home/pfrpc/repos")
CAMPAIGN_ROOT = (
    REPO_ROOT / "pfterminal-perf-probe/runs/glm52-route-rebench-20260727"
)
BASE_SOURCE = (
    REPO_ROOT
    / "pfterminal-perf-probe/runs/kimi-k3-queuecraft-20260727/scripts/run_kimi_k3.py"
)
PFT_CHECKOUT = REPO_ROOT / "PfTerminal-telegram-hardening"
PFT_BINARY = PFT_CHECKOUT / "codex-rs/target/debug/pfterminal"
HERMES_BINARY = Path("/home/pfrpc/.local/bin/hermes")
PFT_WEB_SEARCH_DISABLED = False
PFT_REASONING_EFFORT: str | None = None

ROUTES: dict[str, dict[str, Any]] = {
    "vercel": {
        "model": "zai/glm-5.2",
        "pft_provider": "vercel",
        "hermes_provider": "custom:vercel-ai-gateway",
        "key_file": REPO_ROOT / "vercel_proper.txt",
        "key_env": "AI_GATEWAY_API_KEY",
        "pricing_per_1m": {
            "input": 1.40,
            "cached_input": 0.26,
            "output": 4.40,
        },
        "pricing_source": "https://vercel.com/ai-gateway/models/glm-5.2/providers",
    },
    "openrouter": {
        "model": "z-ai/glm-5.2",
        "pft_provider": "openrouter",
        "hermes_provider": "openrouter",
        "key_file": REPO_ROOT / "openrouter_cred.txt",
        "key_env": "OPENROUTER_API_KEY",
        "pricing_per_1m": {
            "input": 0.7644,
            "cached_input": 0.14196,
            "output": 2.4024,
        },
        "pricing_source": "https://openrouter.ai/api/v1/models",
    },
}


def load_base():
    spec = importlib.util.spec_from_file_location("queuecraft_runner", BASE_SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load base runner: {BASE_SOURCE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


base = load_base()
_BASE_OPENROUTER_KEY_USAGE = base.openrouter_key_usage


def read_key(route: str) -> str:
    path = Path(ROUTES[route]["key_file"])
    value = path.read_text(encoding="utf-8").strip()
    if not value:
        raise RuntimeError(f"empty key file: {path}")
    return value


def vercel_usage(key: str) -> dict[str, Any]:
    request = urllib.request.Request(
        "https://ai-gateway.vercel.sh/v1/credits",
        headers={"Authorization": f"Bearer {key}", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8", errors="replace"))
        return {
            "at": base.utc_now(),
            "usage": float(data["total_used"]),
            "balance": float(data["balance"]),
        }
    except Exception as exc:  # noqa: BLE001
        return {"at": base.utc_now(), "error": type(exc).__name__}


def openrouter_usage(key: str) -> dict[str, Any]:
    return _BASE_OPENROUTER_KEY_USAGE(key)


def openrouter_model_pricing(model: str) -> dict[str, float]:
    request = urllib.request.Request(
        "https://openrouter.ai/api/v1/models",
        headers={"Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        models = json.loads(
            response.read().decode("utf-8", errors="replace")
        ).get("data", [])
    entry = next(
        (item for item in models if isinstance(item, dict) and item.get("id") == model),
        None,
    )
    if entry is None:
        raise RuntimeError(f"OpenRouter catalog does not contain model {model!r}")
    pricing = entry.get("pricing")
    if not isinstance(pricing, dict):
        raise RuntimeError(f"OpenRouter catalog has no pricing for model {model!r}")

    def per_million(field: str) -> float:
        value = pricing.get(field)
        if value is None:
            raise RuntimeError(
                f"OpenRouter catalog has no {field!r} price for model {model!r}"
            )
        return float(value) * 1_000_000

    result = {
        "input": per_million("prompt"),
        "output": per_million("completion"),
    }
    cache_read = pricing.get("input_cache_read")
    if cache_read is not None:
        result["cached_input"] = float(cache_read) * 1_000_000
    return result


def require_balance(route: str, key: str) -> dict[str, Any]:
    if route == "vercel":
        snapshot = vercel_usage(key)
        balance = snapshot.get("balance")
        if not isinstance(balance, float) or balance < 5.0:
            raise RuntimeError(
                f"Vercel balance {balance!r} is below the $5.00 launch floor"
            )
        return snapshot

    credits = base.openrouter_credits(key)
    if credits["balance_usd"] < 5.0:
        raise RuntimeError(
            f"OpenRouter balance ${credits['balance_usd']:.4f} is below the "
            "$5.00 launch floor"
        )
    return credits


def route_env(route: str, key: str) -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        {
            str(ROUTES[route]["key_env"]): key,
            "NO_COLOR": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
        }
    )
    if route == "vercel":
        env["VERCEL_AI_GATEWAY_API_KEY"] = key
    for stale in (
        "ANTHROPIC_API_KEY",
        "AI_GATEWAY_API_KEY",
        "VERCEL_AI_GATEWAY_API_KEY",
        "OPENROUTER_API_KEY",
        "HTTPS_PROXY",
        "https_proxy",
        "HTTP_PROXY",
        "http_proxy",
        "ALL_PROXY",
        "all_proxy",
    ):
        if stale != ROUTES[route]["key_env"] and not (
            route == "vercel" and stale == "VERCEL_AI_GATEWAY_API_KEY"
        ):
            env.pop(stale, None)
    return env


def lane_command(
    route: str,
    lane: str,
    workspace: Path,
    result_dir: Path,
    prompt: str,
    key: str,
) -> tuple[list[str], dict[str, str], Path, Path]:
    env = route_env(route, key)
    model = str(ROUTES[route]["model"])
    if lane == "pft":
        codex_home = result_dir / "codex-home"
        codex_home.mkdir(parents=True, exist_ok=True)
        env["CODEX_HOME"] = str(codex_home)
        env["PFTERMINAL_TRACE_STREAM_TIMING"] = "1"
        env["PFTERMINAL_DUMP_CHAT_REQUEST"] = str(
            result_dir / "pfterminal.request.json"
        )
        command = [
            str(PFT_BINARY),
            "exec",
            "--json",
            "--skip-git-repo-check",
            "--dangerously-bypass-approvals-and-sandbox",
            "-C",
            str(workspace),
            "-c",
            f'model_provider="{ROUTES[route]["pft_provider"]}"',
        ]
        if PFT_WEB_SEARCH_DISABLED:
            command.extend(["-c", 'web_search="disabled"'])
        if PFT_REASONING_EFFORT is not None:
            command.extend(
                ["-c", f'model_reasoning_effort="{PFT_REASONING_EFFORT}"']
            )
        command.extend(["-m", model, prompt])
        return (
            command,
            env,
            result_dir / "pfterminal.stdout",
            result_dir / "pfterminal.stderr",
        )

    hermes_home = result_dir / "hermes-home"
    hermes_home.mkdir(parents=True, exist_ok=True)
    env["HERMES_HOME"] = str(hermes_home)
    if route == "vercel":
        # Hermes v0.19 removed the legacy built-in ``ai-gateway`` alias.
        # Route the same endpoint through Hermes' supported named-provider
        # contract. Keep credentials in the environment so isolated benchmark
        # homes and cached artifacts never contain the live key.
        (hermes_home / "config.yaml").write_text(
            "\n".join(
                [
                    "providers:",
                    "  vercel-ai-gateway:",
                    "    name: Vercel AI Gateway",
                    "    base_url: https://ai-gateway.vercel.sh/v1",
                    "    key_env: AI_GATEWAY_API_KEY",
                    f"    default_model: {model}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    command = [
        str(HERMES_BINARY),
        "--provider",
        str(ROUTES[route]["hermes_provider"]),
        "-m",
        model,
        "--yolo",
        "--accept-hooks",
    ]
    if route != "vercel":
        command.append("--ignore-user-config")
    command.extend(["-z", prompt])
    return (
        command,
        env,
        result_dir / "hermes.stdout",
        result_dir / "hermes.stderr",
    )


def pfterminal_usage(result_dir: Path) -> dict[str, Any]:
    path = result_dir / "pfterminal.stdout"
    latest: dict[str, Any] | None = None
    if path.exists():
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("type") == "turn.completed" and isinstance(
                event.get("usage"), dict
            ):
                latest = event["usage"]
    return latest or {"error": "turn_completed_usage_missing"}


def hermes_usage(result_dir: Path) -> dict[str, Any]:
    path = result_dir / "hermes-home/state.db"
    if not path.exists():
        return {"error": "state_db_missing"}
    columns = (
        "model, model_config, message_count, tool_call_count, api_call_count, "
        "input_tokens, cache_read_tokens, cache_write_tokens, output_tokens, "
        "reasoning_tokens, billing_provider, billing_base_url, "
        "estimated_cost_usd, actual_cost_usd, cost_status, cost_source"
    )
    try:
        connection = sqlite3.connect(path)
        connection.row_factory = sqlite3.Row
        row = connection.execute(
            f"SELECT {columns} FROM sessions ORDER BY started_at DESC LIMIT 1"
        ).fetchone()
        connection.close()
    except sqlite3.Error as exc:
        return {"error": f"sqlite_{type(exc).__name__}"}
    return dict(row) if row is not None else {"error": "session_row_missing"}


def git_head() -> str:
    return subprocess.check_output(
        ["git", "-C", str(PFT_CHECKOUT), "rev-parse", "HEAD"],
        text=True,
    ).strip()


def hermes_build() -> dict[str, str]:
    version = subprocess.check_output(
        [str(HERMES_BINARY), "--version"],
        text=True,
        stderr=subprocess.STDOUT,
        timeout=30,
    ).splitlines()[0]
    install_root = Path("/home/pfrpc/.hermes/hermes-agent")
    commit = subprocess.check_output(
        ["git", "-C", str(install_root), "rev-parse", "HEAD"],
        text=True,
    ).strip()
    return {"version": version, "commit": commit}


def run_route(route: str, waves: list[int], lanes: list[str]) -> int:
    route_root = CAMPAIGN_ROOT / route
    model = str(ROUTES[route]["model"])
    if route == "openrouter":
        ROUTES[route]["pricing_per_1m"] = openrouter_model_pricing(model)
    base.RUN_ROOT = route_root
    base.MODEL = model
    base.PFTERMINAL = PFT_BINARY
    key = read_key(route)
    preflight = require_balance(route, key)
    usage_fn = vercel_usage if route == "vercel" else openrouter_usage

    base.OPENROUTER_KEY_FILE = Path(ROUTES[route]["key_file"])
    base.read_key = lambda: key
    base.openrouter_key_usage = usage_fn
    base.require_credits = lambda _key: preflight
    base.base_env = lambda _key: route_env(route, key)
    base.lane_command = (
        lambda lane, workspace, result_dir, prompt, _key: lane_command(
            route, lane, workspace, result_dir, prompt, key
        )
    )

    manifest = {
        "created_at": base.utc_now(),
        "campaign_root": str(CAMPAIGN_ROOT),
        "route_root": str(route_root),
        "route": route,
        "model": model,
        "task": "queuecraft",
        "lanes": lanes,
        "waves": waves,
        "lane_order": "wave-major, pft then hermes",
        "preflight": preflight,
        "pricing_per_1m": ROUTES[route]["pricing_per_1m"],
        "pricing_source": ROUTES[route]["pricing_source"],
        "pfterminal": {
            "path": str(PFT_BINARY),
            "sha256": base.sha256_file(PFT_BINARY),
            "commit": git_head(),
            "provider": ROUTES[route]["pft_provider"],
            "web_search": (
                "disabled" if PFT_WEB_SEARCH_DISABLED else "native harness default"
            ),
            "reasoning_effort": PFT_REASONING_EFFORT or "native harness default",
        },
        "hermes": {
            "path": str(HERMES_BINARY),
            "sha256": base.sha256_file(HERMES_BINARY),
            **hermes_build(),
            "provider": ROUTES[route]["hermes_provider"],
        },
        "accounting": (
            "Vercel /v1/credits total_used delta"
            if route == "vercel"
            else "OpenRouter /api/v1/key usage delta"
        ),
        "reasoning_policy": (
            "PFTerminal explicit xhigh (catalog-normalized to K3 max); "
            "Hermes K3 native default max"
            if model == "moonshotai/kimi-k3" and PFT_REASONING_EFFORT == "xhigh"
            else "native harness defaults"
        ),
    }
    base.write_json(route_root / "manifest.json", manifest)
    print(
        json.dumps(
            {
                "event": "route_preflight",
                "route": route,
                "model": model,
                "waves": waves,
                "lanes": lanes,
                "preflight": preflight,
            },
            sort_keys=True,
        ),
        flush=True,
    )

    records: list[dict[str, Any]] = []
    for wave in waves:
        for lane in lanes:
            record = base.run_wave(lane, wave, key)
            result_dir = Path(record["result_dir"])
            cost = record.pop("openrouter_cost_usd", None)
            before = record.pop("openrouter_usage_before", None)
            after = record.pop("openrouter_usage_after", None)
            record["provider"] = route
            record["billing"] = {
                "cost_usd": cost,
                "before": before,
                "after": after,
                "source": manifest["accounting"],
            }
            record["token_telemetry"] = (
                pfterminal_usage(result_dir)
                if lane == "pft"
                else hermes_usage(result_dir)
            )
            base.write_json(result_dir / "agent_run.json", record)
            records.append(record)
            base.write_json(route_root / "records.json", records)

    return 0 if all(
        record["returncode"] == 0 and record["verification"]["ok"]
        for record in records
    ) else 1


def main() -> int:
    global CAMPAIGN_ROOT, PFT_REASONING_EFFORT, PFT_WEB_SEARCH_DISABLED

    parser = argparse.ArgumentParser()
    parser.add_argument("--route", choices=sorted(ROUTES), required=True)
    parser.add_argument(
        "--model",
        help="override the route's canonical model slug for a generic route campaign",
    )
    parser.add_argument("--waves", nargs="+", type=int, default=[1, 2, 3])
    parser.add_argument("--lanes", nargs="+", choices=["pft", "hermes"])
    parser.add_argument(
        "--campaign-root",
        type=Path,
        default=CAMPAIGN_ROOT,
        help="fresh output root; existing route manifests are never overwritten",
    )
    parser.add_argument(
        "--pft-disable-web-search",
        action="store_true",
        help="disable PFTerminal's hosted web-search plugin for an isolation run",
    )
    parser.add_argument(
        "--pft-reasoning-effort",
        choices=["none", "low", "medium", "high", "xhigh"],
        help="override PFTerminal reasoning effort for a matched-policy run",
    )
    args = parser.parse_args()
    CAMPAIGN_ROOT = args.campaign_root.resolve()
    if args.model:
        ROUTES[args.route]["model"] = args.model
    PFT_WEB_SEARCH_DISABLED = args.pft_disable_web_search
    PFT_REASONING_EFFORT = args.pft_reasoning_effort
    lanes = args.lanes or ["pft", "hermes"]

    for binary in (PFT_BINARY, HERMES_BINARY):
        if not binary.exists():
            raise RuntimeError(f"missing binary: {binary}")
    if (CAMPAIGN_ROOT / args.route / "manifest.json").exists():
        raise RuntimeError(
            f"refusing to overwrite completed route: {CAMPAIGN_ROOT / args.route}"
        )
    return run_route(args.route, args.waves, lanes)


if __name__ == "__main__":
    raise SystemExit(main())
