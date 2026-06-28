#!/usr/bin/env python3
"""Score homepage hero copy variants with the TIH website lane.

Method: take the latest real homepage snapshot, substitute only the hero
elements (meta description, eyebrow, H1, subhead) for each variant — exactly
the text a Hugo rebuild would produce — register each variant snapshot as a
document, score every document with the same web scoring prompt and run count
as the baseline round, then rank variants and apply the promotion-gate rule
(GPT flat or better, Opus+DeepSeek average improved) against the baseline.

Usage:
  TIH_REPO=../text-improvement-harness-codex-plugin \\
  python3 scripts/hero_copy_experiment.py [--runs 5] [--mock]
"""

from __future__ import annotations

import argparse
import os
import pathlib
import sqlite3
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
DB = REPO / ".tih" / "harness.sqlite3"
SNAPSHOT = REPO / ".tih" / "site-snapshots" / "postfiat-site" / "home.md"
PROJECT = "postfiat-site"
HARNESS = pathlib.Path(os.environ.get("TIH_REPO", REPO.parent / "text-improvement-harness-codex-plugin")).resolve()
OPENAI_KEY = pathlib.Path(os.environ.get("OPENAI_KEY_FILE", REPO.parent / "openai.txt")).resolve()
OPENROUTER_KEY = pathlib.Path(os.environ.get("OPENROUTER_KEY_FILE", REPO.parent / "openx.txt")).resolve()

CURRENT = {
    "eyebrow": "Public testnet infrastructure for AI-native finance",
    "h1": "The Settlement Layer for the AGI Economy",
    "sub": (
        "Post Fiat is a fair, private XRP-derived network for capital markets "
        "and collective intelligence. It keeps XRP-speed settlement, adds "
        "decentralized validator selection and Orchard privacy, and gives "
        "human civilization a way to integrate machine intelligence without "
        "collapsing into centralized control."
    ),
}

VARIANTS = {
    "v1-product-led": {
        "eyebrow": "Public testnet infrastructure for AI-native finance",
        "h1": "Market Infrastructure That Proves What It Claims",
        "sub": (
            "Post Fiat is a fair, private XRP-derived network built for three "
            "products: indexing, compliant information networks, and proof of "
            "reserves. It keeps XRP-speed settlement, adds decentralized "
            "validator selection and Orchard privacy, and publishes replayable "
            "evidence for every claim — so you can verify the network instead "
            "of trusting it."
        ),
    },
    "v2-agi-grounded": {
        "eyebrow": "Public testnet infrastructure for AI-native finance",
        "h1": "The Settlement Layer for the AGI Economy",
        "sub": (
            "Post Fiat is a fair, private XRP-derived network where humans and "
            "machine intelligence transact under rules both can verify. It "
            "keeps XRP-speed settlement, adds decentralized validator "
            "selection and Orchard privacy, and ships three working products "
            "on that foundation: indexing, compliant information networks, and "
            "proof of reserves."
        ),
    },
    "v3-institutional": {
        "eyebrow": "Public testnet — auditable market infrastructure for AI-native finance",
        "h1": "Compliant Rails for Machine-Speed Markets",
        "sub": (
            "Post Fiat keeps XRP-speed settlement and adds what serious "
            "participants need: indexing you can verify, information networks "
            "built for compliance, and proof of reserves anyone can replay "
            "from public artifacts. Validator selection is scored in the open, "
            "and Orchard privacy protects transactions without hiding the "
            "rules."
        ),
    },
    "v4-verification": {
        "eyebrow": "Public testnet infrastructure for AI-native finance",
        "h1": "Don't Trust the Network. Replay It.",
        "sub": (
            "Post Fiat is a fair, private XRP-derived network whose claims "
            "ship with evidence. Indexing, compliant information networks, and "
            "proof of reserves run on XRP-speed settlement, decentralized "
            "validator selection, and Orchard privacy — and every benchmark, "
            "validator score, and governance decision is published as a "
            "replayable public artifact."
        ),
    },
    "v5-collective-grounded": {
        "eyebrow": "Public testnet for AI-native capital markets",
        "h1": "Where Human and Machine Capital Coordinate",
        "sub": (
            "Post Fiat is a fair, private XRP-derived network for capital "
            "markets and collective intelligence. Three products anchor it — "
            "indexing, compliant information networks, and proof of reserves — "
            "built on XRP-speed settlement, decentralized validator selection, "
            "and Orchard privacy, with validator governance auditable in "
            "public."
        ),
    },
}


def meta_description(variant: dict) -> str:
    first_sentence = variant["sub"].split(". ")[0] + "."
    return f"{variant['h1']}. {first_sentence}"


def render_variant(base: str, variant: dict) -> str:
    out = base
    replacements = [
        (
            f"META DESCRIPTION: {meta_description(CURRENT)}",
            f"META DESCRIPTION: {meta_description(variant)}",
        ),
        (CURRENT["eyebrow"], variant["eyebrow"]),
        (f"# {CURRENT['h1']}", f"# {variant['h1']}"),
        (CURRENT["sub"], variant["sub"]),
    ]
    for old, new in replacements:
        if old not in out:
            raise SystemExit(f"hero element not found in snapshot: {old[:60]!r}")
        out = out.replace(old, new)
    return out


def web_prompt() -> str:
    sys.path.insert(0, str(HARNESS))
    from text_improvement_harness.site import web_scoring_prompt

    return web_scoring_prompt("postfiat.org", "/")


def score(path: pathlib.Path, runs: int, mock: bool) -> None:
    cmd = [
        sys.executable,
        "-m",
        "text_improvement_harness",
        "score",
        str(path),
        "--db",
        str(DB),
        "--project",
        PROJECT,
        "--gate",
        "full",
        "--runs",
        str(runs),
        "--concurrency",
        "15",
        "--scoring-prompt",
        web_prompt(),
    ]
    if mock:
        cmd.append("--mock")
    else:
        # --force guarantees fresh runs so cached mock/smoke scores with the
        # same prompt hash can never blend into the experiment.
        cmd.extend(
            [
                "--force",
                "--openai-key-file",
                str(OPENAI_KEY),
                "--openrouter-key-file",
                str(OPENROUTER_KEY),
            ]
        )
    env = {"PYTHONPATH": str(HARNESS), "PATH": "/usr/bin:/bin"}
    subprocess.run(cmd, check=True, env=env, cwd=REPO)


def lane_averages(con: sqlite3.Connection, sha: str) -> dict[str, float]:
    rows = con.execute(
        """
        SELECT provider, model, AVG(score) AS avg_score, COUNT(*) AS n,
               MIN(score) AS lo, MAX(score) AS hi
        FROM score_runs
        WHERE document_sha256 = :sha AND score IS NOT NULL
          AND run_group = (
            SELECT run_group FROM score_runs
            WHERE document_sha256 = :sha AND score IS NOT NULL
            ORDER BY created_at DESC, id DESC LIMIT 1
          )
        GROUP BY provider, model
        """,
        {"sha": sha},
    ).fetchall()
    lanes: dict[str, float] = {}
    for provider, model, avg, n, lo, hi in rows:
        key = "opus" if "opus" in model else "deepseek" if "deepseek" in model else "gpt"
        lanes[key] = float(avg)
        lanes[f"{key}_meta"] = f"n={n} {lo:.0f}-{hi:.0f}"  # type: ignore[assignment]
    return lanes


def sha_for(con: sqlite3.Connection, text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=5)
    ap.add_argument("--mock", action="store_true")
    args = ap.parse_args()

    base = SNAPSHOT.read_text(encoding="utf-8")
    out_dir = SNAPSHOT.parent
    texts = {"baseline": base}
    for name, variant in VARIANTS.items():
        text = render_variant(base, variant)
        path = out_dir / f"home-hero-{name}.md"
        path.write_text(text, encoding="utf-8")
        texts[name] = text
        print(f"== scoring {name}")
        score(path, args.runs, args.mock)
    print("== scoring baseline (cached runs reused if present)")
    score(SNAPSHOT, args.runs, args.mock)

    con = sqlite3.connect(DB)
    results = []
    for name, text in texts.items():
        lanes = lane_averages(con, sha_for(con, text))
        vals = [lanes[k] for k in ("gpt", "opus", "deepseek") if k in lanes]
        if not vals:
            continue
        frontier = (lanes.get("opus", 0) + lanes.get("deepseek", 0)) / 2
        avg = sum(vals) / len(vals)
        results.append((name, lanes, frontier, avg))
    con.close()

    base_row = next(r for r in results if r[0] == "baseline")
    base_gpt, base_frontier = base_row[1].get("gpt", 0.0), base_row[2]
    results.sort(key=lambda r: r[3], reverse=True)

    print(f"\n{'VARIANT':26} {'GPT':>6} {'OPUS':>6} {'DSEEK':>6} {'FRONT':>6} {'AVG':>6}  GATE")
    for name, lanes, frontier, avg in results:
        if name == "baseline":
            gate = "(baseline)"
        else:
            gpt_flat = lanes.get("gpt", 0) + 1.0 >= base_gpt
            frontier_up = frontier > base_frontier + 0.5
            gate = "PROMOTE" if (gpt_flat and frontier_up) else "reject"
        print(
            f"{name:26} {lanes.get('gpt', 0):6.1f} {lanes.get('opus', 0):6.1f} "
            f"{lanes.get('deepseek', 0):6.1f} {frontier:6.1f} {avg:6.1f}  {gate}"
        )
        meta = "  ".join(
            f"{k}[{lanes.get(f'{k}_meta', '')}]" for k in ("gpt", "opus", "deepseek")
        )
        print(f"{'':26} {meta}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
