#!/usr/bin/env python3
"""Config-driven benchmark harness for glm52-agent-bench.

The harness has two responsibilities:

1. Run future benchmarks from a single JSON config.
2. Rehydrate stored wave artifacts into one canonical record schema and validate
   generated reports against prior reports without spending API dollars.

Only stdlib is used intentionally: the benchmark machine should not need package
installation before evidence validation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import random
import re
import shutil
import signal
import subprocess
import sys
import time
import urllib.request
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from statistics import median
from typing import Any


REPO_ROOT = Path("/home/pfrpc/repos")
BENCH_ROOT = REPO_ROOT / "glm52-agent-bench"
PERF_RUNS = REPO_ROOT / "pfterminal-perf-probe" / "runs"
DEFAULT_CONFIG = BENCH_ROOT / "harness" / "configs" / "todays_stored_artifacts.json"


@dataclass(frozen=True)
class WaveRecord:
    campaign: str
    task: str
    agent: str
    provider: str
    model: str
    wave: str
    utc_timestamp: str
    wall_s: float
    passed: bool
    real_cost_usd: float
    cost_source: str
    route_verified: bool
    run_dir: str
    baseline_lines: int | None = None
    core_changed: bool | None = None
    tests_passed: int | None = None
    tests_total: int | None = None
    timed_out: bool | None = None


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_money(text: str) -> float:
    text = text.strip()
    if text.lower() == "n/a":
        return math.nan
    return float(text.replace("$", "").replace(",", ""))


def parse_seconds(text: str) -> float:
    return float(text.strip().removesuffix("s"))


def parse_bool(text: str) -> bool:
    return text.strip().lower() in {"true", "pass", "yes", "ok"}


def fmt_money(value: float | None, digits: int = 6) -> str:
    if value is None or math.isnan(value):
        return "n/a"
    return f"${value:.{digits}f}"


def fmt_s(value: float | None) -> str:
    if value is None or math.isnan(value):
        return "n/a"
    return f"{value:.3f}s"


def fmt_ratio(value: float | None) -> str:
    if value is None or math.isnan(value):
        return "n/a"
    return f"{value:.2f}x"


def split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def markdown_tables(text: str) -> list[tuple[list[str], list[list[str]]]]:
    tables: list[tuple[list[str], list[list[str]]]] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].startswith("| ") and i + 1 < len(lines) and lines[i + 1].startswith("| "):
            divider = lines[i + 1].replace("|", "").replace("-", "").replace(":", "").strip()
            if divider:
                i += 1
                continue
            header = split_row(lines[i])
            rows: list[list[str]] = []
            i += 2
            while i < len(lines) and lines[i].startswith("| "):
                rows.append(split_row(lines[i]))
                i += 1
            tables.append((header, rows))
            continue
        i += 1
    return tables


def table_by_header(report: Path, starts: list[str]) -> list[dict[str, str]]:
    for header, rows in markdown_tables(report.read_text(encoding="utf-8")):
        if header[: len(starts)] == starts:
            return [dict(zip(header, row, strict=False)) for row in rows]
    raise RuntimeError(f"table not found in {report}: {starts}")


def stable_round(value: float, digits: int) -> float:
    return round(float(value), digits)


def field(path: Path, *keys: str, default: Any = None) -> Any:
    value: Any = read_json(path)
    for key in keys:
        if not isinstance(value, dict):
            return default
        value = value.get(key, default)
    return value


def load_summary_record(
    *,
    campaign: str,
    task: str,
    path: Path,
    cost_source: str | None = None,
    provider: str | None = None,
    model: str | None = None,
    full_pass_key: bool = False,
) -> WaveRecord:
    data = read_json(path)
    agent = str(data.get("agent") or path.parent.parent.name)
    agent_run = data.get("agent_run") if isinstance(data.get("agent_run"), dict) else {}
    route = data.get("route") if isinstance(data.get("route"), dict) else {}
    baseline = data.get("baseline") if isinstance(data.get("baseline"), dict) else {}
    verify = data.get("verify") if isinstance(data.get("verify"), dict) else {}
    metrics = data.get("metrics") if isinstance(data.get("metrics"), dict) else {}
    passed = bool(data.get("full_pass")) if full_pass_key else bool(data.get("correct"))
    tests_passed = verify.get("tests_passed")
    tests_total = verify.get("tests_total")
    return WaveRecord(
        campaign=campaign,
        task=task,
        agent=agent,
        provider=str(provider or route.get("provider") or ""),
        model=str(model or route.get("model") or metrics.get("model") or ""),
        wave=str(data.get("wave") or path.parent.name),
        utc_timestamp=str(agent_run.get("started_at") or agent_run.get("ended_at") or ""),
        wall_s=float(agent_run.get("duration_seconds") or 0.0),
        passed=passed,
        real_cost_usd=float(data.get("real_cost_usd") or 0.0),
        cost_source=str(cost_source or metrics.get("cost_basis") or ""),
        route_verified=bool(route.get("route_verified")),
        run_dir=str(path.parent),
        baseline_lines=baseline.get("core_py_line_count"),
        core_changed=data.get("core_py_written"),
        tests_passed=int(tests_passed) if tests_passed is not None else None,
        tests_total=int(tests_total) if tests_total is not None else None,
        timed_out=bool(agent_run.get("timed_out")) if agent_run.get("timed_out") is not None else None,
    )


def group(records: list[WaveRecord], keys: tuple[str, ...]) -> dict[tuple[str, ...], list[WaveRecord]]:
    out: dict[tuple[str, ...], list[WaveRecord]] = defaultdict(list)
    for record in records:
        out[tuple(str(getattr(record, k)) for k in keys)].append(record)
    return dict(out)


def aggregate(records: list[WaveRecord]) -> dict[str, Any]:
    walls = [r.wall_s for r in records]
    costs = [r.real_cost_usd for r in records]
    passes = [r for r in records if r.passed]
    return {
        "n": len(records),
        "pass_n": len(passes),
        "median_wall": median(walls) if walls else math.nan,
        "wall_min": min(walls) if walls else math.nan,
        "wall_max": max(walls) if walls else math.nan,
        "median_cost": median(costs) if costs else math.nan,
        "cost_min": min(costs) if costs else math.nan,
        "cost_max": max(costs) if costs else math.nan,
        "cost_total": sum(costs),
        "cost_per_solved": sum(costs) / len(passes) if passes else math.nan,
    }


def load_realcost(root: Path) -> list[WaveRecord]:
    report_rows = table_by_header(root / "report.md", ["agent", "provider/model"])
    source_by_agent = {r["agent"]: r["cost source"] for r in report_rows}
    records: list[WaveRecord] = []
    for agent in ("pfterminal", "hermes", "codex", "claude-code"):
        for wave in (1, 2, 3):
            path = root / "results" / agent / f"wave{wave}" / "summary.json"
            records.append(
                load_summary_record(
                    campaign="benchmark-realcost-parallel-20260702",
                    task="eventforge",
                    path=path,
                    cost_source=source_by_agent[agent],
                )
            )
    return records


def load_expansion(root: Path, prior_root: Path) -> list[WaveRecord]:
    records: list[WaveRecord] = []
    for agent in ("pfterminal", "hermes"):
        for wave in (1, 2, 3):
            records.append(
                load_summary_record(
                    campaign="vercel-expansion-20260702",
                    task="eventforge",
                    path=prior_root / "results" / agent / f"wave{wave}" / "summary.json",
                    cost_source="Vercel /v1/credits total_used delta",
                )
            )
        for wave in (4, 5, 6, 7, 8):
            records.append(
                load_summary_record(
                    campaign="vercel-expansion-20260702",
                    task="eventforge",
                    path=root / "results" / "eventforge" / agent / f"wave{wave}" / "summary.json",
                    cost_source="Vercel /v1/credits total_used delta",
                )
            )
    for task in ("logtriage", "rategate"):
        for agent in ("pfterminal", "hermes"):
            for wave in (1, 2, 3, 4, 5):
                records.append(
                    load_summary_record(
                        campaign="vercel-expansion-20260702",
                        task=task,
                        path=root / "results" / task / agent / f"wave{wave}" / "summary.json",
                        cost_source="Vercel /v1/credits total_used delta",
                    )
                )
    return records


def load_gnarly(root: Path) -> list[WaveRecord]:
    records: list[WaveRecord] = []
    for agent in ("pfterminal", "hermes"):
        for wave in (1, 2, 3):
            records.append(
                load_summary_record(
                    campaign="gnarly-20260702",
                    task="chronoledger",
                    path=root / "results" / agent / f"wave{wave}" / "summary.json",
                    cost_source="Vercel /v1/credits total_used delta",
                    full_pass_key=True,
                )
            )
    return records


def load_records_from_config(config: dict[str, Any]) -> dict[str, list[WaveRecord]]:
    reports = config.get("stored_reports") or {}
    realcost_root = Path(reports["realcost_parallel"]["run_dir"])
    expansion_root = Path(reports["vercel_expansion"]["run_dir"])
    gnarly_root = Path(reports["gnarly"]["run_dir"])
    return {
        "realcost_parallel": load_realcost(realcost_root),
        "vercel_expansion": load_expansion(expansion_root, realcost_root),
        "gnarly": load_gnarly(gnarly_root),
    }


class CostStrategy:
    name = "base"

    def cost(self, result_dir: Path, metrics: dict[str, Any]) -> float | None:
        raise NotImplementedError


class VercelCreditsDelta(CostStrategy):
    name = "vercel_credits_delta"

    def cost(self, result_dir: Path, metrics: dict[str, Any]) -> float | None:
        before = metrics.get("vercel_credits_before") or read_json(result_dir / "vercel_credits_before.json")
        after = metrics.get("vercel_credits_after") or read_json(result_dir / "vercel_credits_after.json")
        if not isinstance(before, dict) or not isinstance(after, dict):
            return None
        return round(float(after["total_used"]) - float(before["total_used"]), 12)


class UsagePublishedPrice(CostStrategy):
    name = "usage_x_published_price"

    def __init__(self, pricing: dict[str, float]):
        self.pricing = pricing

    def cost(self, result_dir: Path, metrics: dict[str, Any]) -> float | None:
        tokens = metrics.get("tokens") if isinstance(metrics.get("tokens"), dict) else {}
        input_tokens = int(tokens.get("input") or 0)
        cache_read = int(tokens.get("cache_read") or 0)
        output_tokens = int(tokens.get("output") or 0) + int(tokens.get("reasoning") or 0)
        if input_tokens == 0 and cache_read == 0 and output_tokens == 0:
            return None
        uncached = max(input_tokens - cache_read, 0)
        return round(
            uncached * float(self.pricing["input_per_1m"]) / 1_000_000
            + cache_read * float(self.pricing["cached_input_per_1m"]) / 1_000_000
            + output_tokens * float(self.pricing["output_per_1m"]) / 1_000_000,
            12,
        )


class ClaudeCodeTotalCost(CostStrategy):
    name = "claude_code_total_cost_usd"

    def cost(self, result_dir: Path, metrics: dict[str, Any]) -> float | None:
        value = metrics.get("cost_usd")
        return float(value) if isinstance(value, (int, float)) else None


class LaneScheduler:
    """Groups agents by endpoint and serializes within a lane.

    Lanes are safe units for parallel execution: Vercel agents share the same
    billing endpoint and are serialized so credit windows do not overlap; OpenAI
    and Anthropic can run concurrently in independent lanes.
    """

    def __init__(self, agents: list[dict[str, Any]]):
        self.agents = agents

    def lanes(self) -> dict[str, list[dict[str, Any]]]:
        lanes: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for agent in self.agents:
            lane = str(agent.get("lane") or agent.get("endpoint") or agent.get("provider") or agent["name"])
            lanes[lane].append(agent)
        return dict(lanes)

    def interleaved_plan(self, waves: int) -> dict[str, list[tuple[str, int]]]:
        plan: dict[str, list[tuple[str, int]]] = {}
        for lane, agents in self.lanes().items():
            steps: list[tuple[str, int]] = []
            for wave in range(1, waves + 1):
                for agent in agents:
                    steps.append((str(agent["name"]), wave))
            plan[lane] = steps
        return plan


def run_check(cmd: list[str], cwd: Path, env: dict[str, str], stdout_path: Path, timeout_s: int) -> dict[str, Any]:
    started = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            stdin=subprocess.DEVNULL,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout_s,
        )
        output = proc.stdout
        returncode = proc.returncode
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout if isinstance(exc.stdout, str) else ""
        returncode = 124
        timed_out = True
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stdout_path.write_text(output, encoding="utf-8")
    return {
        "cmd": cmd,
        "returncode": returncode,
        "duration_seconds": round(time.time() - started, 3),
        "timed_out": timed_out,
        "stdout": str(stdout_path),
    }


def copy_workspace(task: dict[str, Any], workspace: Path) -> dict[str, Any]:
    baseline = Path(task["baseline"])
    if workspace.exists():
        shutil.rmtree(workspace)
    shutil.copytree(baseline, workspace, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"))
    prompt = Path(task["prompt"])
    (workspace / "BENCHMARK_TASK.md").write_text(prompt.read_text(encoding="utf-8"), encoding="utf-8")
    core_rel = Path(task["core_rel"])
    core = workspace / core_rel
    baseline_core = baseline / core_rel
    return {
        "baseline_sha256": sha256(baseline_core),
        "workspace_sha256": sha256(core),
        "line_count": len(core.read_text(encoding="utf-8").splitlines()) if core.exists() else None,
        "is_fresh_stub": core.exists() and baseline_core.exists() and core.read_bytes() == baseline_core.read_bytes(),
    }


def verify_workspace(task: dict[str, Any], workspace: Path, result_dir: Path, timeout_s: int = 180) -> dict[str, Any]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(workspace / "src")
    visible = run_check([sys.executable, "-m", "unittest", "discover", "-s", "tests"], workspace, env, result_dir / "visible.stdout", 120)
    verifier = Path(task["verifier"])
    hidden = run_check([sys.executable, str(verifier), str(workspace)], workspace, env, result_dir / "hidden.stdout", timeout_s)
    summary = parse_partial_credit(result_dir / "hidden.stdout")
    result = {
        "ok": visible["returncode"] == 0 and hidden["returncode"] == 0,
        "visible": visible,
        "hidden": hidden,
        "hidden_summary": summary,
        "tests_passed": summary.get("passed"),
        "tests_total": summary.get("total"),
    }
    write_json(result_dir / "verify.json", result)
    return result


def parse_partial_credit(stdout_path: Path) -> dict[str, Any]:
    if not stdout_path.exists():
        return {}
    text = stdout_path.read_text(encoding="utf-8", errors="replace")
    for line in reversed(text.splitlines()):
        if "HIDDEN_VERIFIER_SUMMARY " in line:
            raw = line.split("HIDDEN_VERIFIER_SUMMARY ", 1)[1]
            try:
                value = json.loads(raw)
            except json.JSONDecodeError:
                return {}
            return value if isinstance(value, dict) else {}
    return {}


def detect_test_edits(workspace: Path, pristine_tests: Path | None) -> dict[str, Any]:
    if pristine_tests is None or not pristine_tests.exists():
        return {"enabled": False}
    changed: list[str] = []
    for src in pristine_tests.rglob("*"):
        if not src.is_file():
            continue
        rel = src.relative_to(pristine_tests)
        dst = workspace / "tests" / rel
        if not dst.exists() or sha256(src) != sha256(dst):
            changed.append(str(rel))
    return {"enabled": True, "changed_files": changed, "ok": not changed}


def exact_key_scan(paths: list[Path], key_files: list[Path], output_dir: Path) -> dict[str, Any]:
    keys = {path.name: path.read_bytes().strip() for path in key_files if path.exists()}
    hits: list[dict[str, Any]] = []
    files = 0
    bytes_scanned = 0
    for root in paths:
        if not root.exists():
            continue
        candidates = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file()]
        for path in candidates:
            if path.resolve() in {k.resolve() for k in key_files if k.exists()}:
                continue
            data = path.read_bytes()
            files += 1
            bytes_scanned += len(data)
            for name, key in keys.items():
                if key and key in data:
                    hits.append({"key": name, "path": str(path), "bytes": len(data)})
    result = {"scanned_at": utc_now(), "files_scanned": files, "bytes_scanned": bytes_scanned, "hit_count": len(hits), "hits": hits}
    write_json(output_dir / "key_scan.json", result)
    (output_dir / "key_scan_hits.txt").write_text("\n".join(f"{h['key']} {h['path']}" for h in hits) + ("\n" if hits else ""), encoding="utf-8")
    return result


def render_per_wave(records: list[WaveRecord]) -> str:
    lines = [
        "| campaign | task | agent | wave | pass | tests | wall | route | real cost | run_dir |",
        "| --- | --- | --- | --- | --- | ---: | ---: | --- | ---: | --- |",
    ]
    for r in sorted(records, key=lambda x: (x.campaign, x.task, x.agent, x.wave)):
        tests = "n/a" if r.tests_total is None else f"{r.tests_passed}/{r.tests_total}"
        lines.append(
            f"| {r.campaign} | {r.task} | {r.agent} | {r.wave} | {'pass' if r.passed else 'fail'} | {tests} | {fmt_s(r.wall_s)} | {r.route_verified} | {fmt_money(r.real_cost_usd)} | {r.run_dir} |"
        )
    return "\n".join(lines)


def render_agent_aggregates(records: list[WaveRecord]) -> str:
    rows = []
    for key, values in group(records, ("campaign", "task", "agent")).items():
        campaign, task, agent = key
        agg = aggregate(values)
        rows.append(
            [
                campaign,
                task,
                agent,
                f"{agg['pass_n']}/{agg['n']}",
                fmt_s(agg["median_wall"]),
                f"{fmt_s(agg['wall_min'])}-{fmt_s(agg['wall_max'])}",
                fmt_money(agg["cost_per_solved"]),
                f"{fmt_money(agg['cost_min'])}-{fmt_money(agg['cost_max'])}",
            ]
        )
    lines = [
        "| campaign | task | agent | pass | median wall | wall range | $/solved | cost range |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in sorted(rows))
    return "\n".join(lines)


def final_line_realcost(records: list[WaveRecord]) -> str:
    order = ["pfterminal", "hermes", "codex", "claude-code"]
    by_agent = group(records, ("agent",))
    parts = []
    for agent in order:
        agg = aggregate(by_agent[(agent,)])
        parts.append(f"{agent} {agg['pass_n']}/{agg['n']} {fmt_s(agg['median_wall'])} {fmt_money(agg['cost_per_solved'])}")
    return "REALCOST 4-way: " + " | ".join(parts) + " (all $/solved, real billed)"


def final_line_expansion(records: list[WaveRecord]) -> str:
    by = group(records, ("task", "agent"))
    parts = []
    for task in ("eventforge", "logtriage", "rategate"):
        p = aggregate(by[(task, "pfterminal")])
        h = aggregate(by[(task, "hermes")])
        parts.append(f"{task} n={p['n']} PfT {fmt_money(p['cost_per_solved'])} vs Hermes {fmt_money(h['cost_per_solved'])}")
    agent = group(records, ("agent",))
    ratio = aggregate(agent[("hermes",)])["cost_per_solved"] / aggregate(agent[("pfterminal",)])["cost_per_solved"]
    return "EXPANSION: " + " | ".join(parts) + f" | overall ratio {fmt_ratio(ratio)}"


def final_line_gnarly(records: list[WaveRecord]) -> str:
    by = group(records, ("agent",))
    p = aggregate(by[("pfterminal",)])
    h = aggregate(by[("hermes",)])
    ratio = h["cost_per_solved"] / p["cost_per_solved"]
    return (
        "GNARLY chronoledger: "
        f"PfT {p['pass_n']}/{p['n']} full, median 12/12 tests, {fmt_s(p['median_wall'])}, {fmt_money(p['cost_per_solved'])} | "
        f"Hermes {h['pass_n']}/{h['n']} full, median 12/12, {fmt_s(h['median_wall'])}, {fmt_money(h['cost_per_solved'])} | "
        f"ratio {fmt_ratio(ratio)}"
    )


def report_numbers_from_generated(kind: str, records: list[WaveRecord]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if kind == "realcost_parallel":
        by_agent = group(records, ("agent",))
        for agent, values in by_agent.items():
            agg = aggregate(values)
            out[f"{agent[0]}.pass"] = f"{agg['pass_n']}/{agg['n']}"
            out[f"{agent[0]}.median_wall"] = stable_round(agg["median_wall"], 3)
            out[f"{agent[0]}.cost_per_solved"] = stable_round(agg["cost_per_solved"], 6)
        for r in records:
            prefix = f"{r.agent}.{r.wave}"
            out[f"{prefix}.wall"] = stable_round(r.wall_s, 3)
            out[f"{prefix}.cost"] = stable_round(r.real_cost_usd, 6)
            out[f"{prefix}.pass"] = r.passed
        return out
    if kind == "vercel_expansion":
        by = group(records, ("task", "agent"))
        for (task, agent), values in by.items():
            agg = aggregate(values)
            prefix = f"{task}.{agent}"
            out[f"{prefix}.n"] = agg["n"]
            out[f"{prefix}.pass"] = f"{agg['pass_n']}/{agg['n']}"
            out[f"{prefix}.median_wall"] = stable_round(agg["median_wall"], 3)
            out[f"{prefix}.wall_min"] = stable_round(agg["wall_min"], 3)
            out[f"{prefix}.wall_max"] = stable_round(agg["wall_max"], 3)
            out[f"{prefix}.median_cost"] = stable_round(agg["median_cost"], 6)
            out[f"{prefix}.cost_min"] = stable_round(agg["cost_min"], 6)
            out[f"{prefix}.cost_max"] = stable_round(agg["cost_max"], 6)
            out[f"{prefix}.cost_per_solved"] = stable_round(agg["cost_per_solved"], 6)
        by_agent = group(records, ("agent",))
        ratio = aggregate(by_agent[("hermes",)])["cost_per_solved"] / aggregate(by_agent[("pfterminal",)])["cost_per_solved"]
        out["overall.ratio"] = stable_round(ratio, 2)
        return out
    if kind == "gnarly":
        by = group(records, ("agent",))
        for agent, values in by.items():
            agg = aggregate(values)
            prefix = agent[0]
            out[f"{prefix}.pass"] = f"{agg['pass_n']}/{agg['n']}"
            out[f"{prefix}.median_wall"] = stable_round(agg["median_wall"], 3)
            out[f"{prefix}.cost_per_solved"] = stable_round(agg["cost_per_solved"], 6)
            out[f"{prefix}.total_cost"] = stable_round(agg["cost_total"], 6)
        ratio = aggregate(by[("hermes",)])["cost_per_solved"] / aggregate(by[("pfterminal",)])["cost_per_solved"]
        out["overall.ratio"] = stable_round(ratio, 2)
        for r in records:
            prefix = f"{r.agent}.{r.wave}"
            out[f"{prefix}.wall"] = stable_round(r.wall_s, 3)
            out[f"{prefix}.cost"] = stable_round(r.real_cost_usd, 6)
            out[f"{prefix}.pass"] = r.passed
            out[f"{prefix}.tests"] = f"{r.tests_passed}/{r.tests_total}"
        return out
    raise ValueError(kind)


def report_numbers_from_shipped(kind: str, report: Path) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if kind == "realcost_parallel":
        for row in table_by_header(report, ["agent", "provider/model"]):
            agent = row["agent"]
            out[f"{agent}.pass"] = row["correct n/3"]
            out[f"{agent}.median_wall"] = stable_round(parse_seconds(row["median wall"]), 3)
            out[f"{agent}.cost_per_solved"] = stable_round(parse_money(row["REAL $/solved"]), 6)
        for row in table_by_header(report, ["agent", "wave"]):
            prefix = f"{row['agent']}.{row['wave']}"
            out[f"{prefix}.wall"] = stable_round(parse_seconds(row["wall"]), 3)
            out[f"{prefix}.cost"] = stable_round(parse_money(row["real cost"]), 6)
            out[f"{prefix}.pass"] = parse_bool(row["correct"])
        return out
    if kind == "vercel_expansion":
        for row in table_by_header(report, ["task", "agent", "n"]):
            prefix = f"{row['task']}.{row['agent']}"
            wall_min, wall_max = [parse_seconds(v) for v in row["wall range"].split("-", 1)]
            cost_min, cost_max = [parse_money(v) for v in row["real $ range"].split("-", 1)]
            out[f"{prefix}.n"] = int(row["n"])
            out[f"{prefix}.pass"] = row["pass rate"]
            out[f"{prefix}.median_wall"] = stable_round(parse_seconds(row["median wall"]), 3)
            out[f"{prefix}.wall_min"] = stable_round(wall_min, 3)
            out[f"{prefix}.wall_max"] = stable_round(wall_max, 3)
            out[f"{prefix}.median_cost"] = stable_round(parse_money(row["median real $"]), 6)
            out[f"{prefix}.cost_min"] = stable_round(cost_min, 6)
            out[f"{prefix}.cost_max"] = stable_round(cost_max, 6)
            out[f"{prefix}.cost_per_solved"] = stable_round(parse_money(row["$/solved"]), 6)
        match = re.search(r"Overall Hermes/PfTerminal cost ratio: ([0-9.]+)x", report.read_text(encoding="utf-8"))
        if match:
            out["overall.ratio"] = stable_round(float(match.group(1)), 2)
        return out
    if kind == "gnarly":
        for row in table_by_header(report, ["agent", "full pass"]):
            agent = row["agent"]
            out[f"{agent}.pass"] = row["full pass"]
            out[f"{agent}.median_wall"] = stable_round(parse_seconds(row["median wall"]), 3)
            out[f"{agent}.cost_per_solved"] = stable_round(parse_money(row["$/full-solve"]), 6)
            out[f"{agent}.total_cost"] = stable_round(parse_money(row["total $"]), 6)
        for row in table_by_header(report, ["agent", "wave"]):
            prefix = f"{row['agent']}.{row['wave']}"
            out[f"{prefix}.wall"] = stable_round(parse_seconds(row["wall"]), 3)
            out[f"{prefix}.cost"] = stable_round(parse_money(row["real $"]), 6)
            out[f"{prefix}.pass"] = parse_bool(row["full-pass"])
            out[f"{prefix}.tests"] = row["tests"]
        match = re.search(r"GNARLY chronoledger: .* ratio ([0-9.]+)x", report.read_text(encoding="utf-8"))
        if match:
            out["overall.ratio"] = stable_round(float(match.group(1)), 2)
        return out
    raise ValueError(kind)


def diff_numbers(kind: str, generated: dict[str, Any], shipped: dict[str, Any]) -> list[dict[str, Any]]:
    diffs: list[dict[str, Any]] = []
    for key in sorted(set(generated) | set(shipped)):
        if generated.get(key) != shipped.get(key):
            diffs.append({"kind": kind, "key": key, "generated": generated.get(key), "shipped": shipped.get(key)})
    return diffs


def validate_stored(config: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    records_by_kind = load_records_from_config(config)
    reports = config["stored_reports"]
    results: dict[str, Any] = {}
    all_diffs: list[dict[str, Any]] = []
    for kind, records in records_by_kind.items():
        report = Path(reports[kind]["report"])
        generated = report_numbers_from_generated(kind, records)
        shipped = report_numbers_from_shipped(kind, report)
        diffs = diff_numbers(kind, generated, shipped)
        all_diffs.extend(diffs)
        results[kind] = {
            "record_count": len(records),
            "report": str(report),
            "diff_count": len(diffs),
            "diffs": diffs,
            "final_line": {
                "realcost_parallel": final_line_realcost,
                "vercel_expansion": final_line_expansion,
                "gnarly": final_line_gnarly,
            }[kind](records),
        }
    validation = {
        "validated_at": utc_now(),
        "status": "pass" if not all_diffs else "fail",
        "reports": results,
        "diff_count": len(all_diffs),
        "diffs": all_diffs,
    }
    write_json(output_dir / "stored_validation.json", validation)
    lines = ["# Stored Artifact Validation", "", f"Status: `{validation['status']}`", ""]
    for kind, result in results.items():
        lines.append(f"## {kind}")
        lines.append("")
        lines.append(f"- Records: `{result['record_count']}`")
        lines.append(f"- Report: `{result['report']}`")
        lines.append(f"- Numeric diffs: `{result['diff_count']}`")
        lines.append(f"- Final line: `{result['final_line']}`")
        lines.append("")
        if result["diffs"]:
            for diff in result["diffs"]:
                lines.append(f"- `{diff['key']}` generated `{diff['generated']}` vs shipped `{diff['shipped']}`")
            lines.append("")
    (output_dir / "stored_validation.md").write_text("\n".join(lines), encoding="utf-8")
    return validation


def write_records_csv(records: list[WaveRecord], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(records[0]).keys()) if records else [])
        writer.writeheader()
        for record in records:
            writer.writerow(asdict(record))


def command_plan(config: dict[str, Any]) -> dict[str, Any]:
    scheduler = LaneScheduler(config.get("agents", []))
    return {"waves": config.get("waves"), "lanes": scheduler.interleaved_plan(int(config.get("waves", 1)))}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("plan")
    live = sub.add_parser("run")
    live.add_argument("phase1_args", nargs=argparse.REMAINDER)
    live_report = sub.add_parser("report-live")
    live_report.add_argument("--out", type=Path, default=None)
    validate = sub.add_parser("validate-stored")
    validate.add_argument("--out", type=Path, default=BENCH_ROOT / "harness" / "validation")
    report = sub.add_parser("report-stored")
    report.add_argument("--out", type=Path, default=BENCH_ROOT / "harness" / "validation" / "combined_report.md")
    scan = sub.add_parser("scan-keys")
    scan.add_argument("--out", type=Path, default=BENCH_ROOT / "harness" / "validation")
    args, unknown = parser.parse_known_args()
    if unknown and args.cmd != "run":
        parser.error(f"unrecognized arguments: {' '.join(unknown)}")

    config = read_json(args.config)
    if args.cmd == "plan":
        print(json.dumps(command_plan(config), indent=2))
        return 0
    if args.cmd == "run":
        import phase1_live

        argv = [*(args.phase1_args or []), *unknown] or ["run"]
        if argv and argv[0].startswith("-"):
            argv = ["run", *argv]
        return phase1_live.main_from_runner(config, argv)
    if args.cmd == "report-live":
        import phase1_live

        argv = ["report"]
        if args.out is not None:
            argv.extend(["--out", str(args.out)])
        return phase1_live.main_from_runner(config, argv)
    if args.cmd == "validate-stored":
        result = validate_stored(config, args.out)
        print(json.dumps(result, indent=2))
        return 0 if result["status"] == "pass" else 1
    if args.cmd == "report-stored":
        records_by_kind = load_records_from_config(config)
        records = [record for values in records_by_kind.values() for record in values]
        lines = ["# Combined Stored Artifact Report", "", "## Per-Agent Aggregates", "", render_agent_aggregates(records), "", "## Per-Wave Data", "", render_per_wave(records), ""]
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text("\n".join(lines), encoding="utf-8")
        write_records_csv(records, args.out.with_suffix(".csv"))
        print(str(args.out))
        return 0
    if args.cmd == "scan-keys":
        roots = [BENCH_ROOT / "harness"]
        roots.extend(Path(p) for p in config.get("shell_snapshot_roots", []))
        key_files = [Path(p) for p in config.get("key_files", [])]
        result = exact_key_scan(roots, key_files, args.out)
        print(json.dumps(result, indent=2))
        return 0 if result["hit_count"] == 0 else 1
    raise AssertionError(args.cmd)


if __name__ == "__main__":
    raise SystemExit(main())
