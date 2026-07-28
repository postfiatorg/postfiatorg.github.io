#!/usr/bin/env python3
"""Blind, balanced GPT-5.6-Sol judging for every completed visual pair."""
from __future__ import annotations

import argparse
import importlib.util
import json
import secrets
from pathlib import Path
from typing import Any


REPO_ROOT = Path("/home/pfrpc/repos")
RUN_ROOT = (
    REPO_ROOT
    / "pfterminal-perf-probe/runs/release-0124-comprehensive-20260728"
)
SOURCE = (
    REPO_ROOT
    / "pfterminal-perf-probe/runs/opus5-visual-site-20260726T011738Z"
    / "scripts/judge_pair.py"
)
OPENAI_KEY = REPO_ROOT / "openai.txt"
OPPONENT = {
    "opus": "cc",
    "kimi-openrouter": "hermes",
    "glm-openrouter": "hermes",
}


def load_judge():
    spec = importlib.util.spec_from_file_location("frozen_visual_judge", SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load frozen judge: {SOURCE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cells", nargs="+", choices=sorted(OPPONENT), required=True)
    parser.add_argument("--waves", nargs="+", type=int, default=[1, 2, 3])
    args = parser.parse_args()
    judge = load_judge()
    client = judge.OpenAI(api_key=OPENAI_KEY.read_text(encoding="utf-8").strip())
    campaign_path = RUN_ROOT / "visual/blind/campaign_summary.json"
    campaign_by_cell_wave: dict[tuple[str, int], dict[str, Any]] = {}
    if campaign_path.exists():
        existing = load_json(campaign_path)
        if isinstance(existing, list):
            for item in existing:
                if isinstance(item, dict):
                    campaign_by_cell_wave[
                        (str(item["cell"]), int(item["wave"]))
                    ] = item

    for cell in args.cells:
        for wave in args.waves:
            opponent = OPPONENT[cell]
            lanes = ["pft", opponent]
            blind_dir = RUN_ROOT / "visual/blind" / cell / f"wave{wave}"
            output_dir = blind_dir / "gpt-5.6-sol"
            output_dir.mkdir(parents=True, exist_ok=True)
            summary_path = output_dir / "summary.json"
            if summary_path.exists():
                summary = load_json(summary_path)
                campaign_by_cell_wave[(cell, wave)] = summary
                write_json(
                    campaign_path,
                    [
                        campaign_by_cell_wave[key]
                        for key in sorted(campaign_by_cell_wave)
                    ],
                )
                print(json.dumps({"event": "judge_pair_cached", **summary}))
                continue

            mapping_path = blind_dir / "mapping.json"
            if mapping_path.exists():
                mapping = load_json(mapping_path)
                first_order = [
                    str(mapping["normal"]["a"]),
                    str(mapping["normal"]["b"]),
                ]
                if sorted(first_order) != sorted(lanes):
                    raise RuntimeError(
                        f"stored blind mapping does not match lanes: {mapping_path}"
                    )
            else:
                first_order = (
                    lanes if secrets.randbelow(2) == 0 else list(reversed(lanes))
                )
                mapping = {
                    "normal": {"a": first_order[0], "b": first_order[1]},
                    "swapped": {"a": first_order[1], "b": first_order[0]},
                }
                write_json(mapping_path, mapping)

            def content_for(order: list[str], selected_wave: int):
                content: list[dict[str, Any]] = [
                    {"type": "input_text", "text": judge.JUDGE_PROMPT}
                ]
                for site_label, lane in zip(("A", "B"), order, strict=True):
                    content.append(
                        {
                            "type": "input_text",
                            "text": (
                                f"Begin Site {site_label}. The next six images "
                                "are this site only."
                            ),
                        }
                    )
                    capture_dir = (
                        RUN_ROOT
                        / "visual/results"
                        / cell
                        / lane
                        / f"wave{selected_wave}"
                        / "captures"
                    )
                    for capture_id in judge.CAPTURE_IDS:
                        image_path = capture_dir / f"{capture_id}.png"
                        if not image_path.is_file():
                            raise RuntimeError(
                                f"missing capture for blind judge: {image_path}"
                            )
                        content.extend(
                            [
                                {
                                    "type": "input_text",
                                    "text": (
                                        f"Site {site_label} — screenshot ID: "
                                        f"{capture_id}"
                                    ),
                                },
                                {
                                    "type": "input_image",
                                    "image_url": judge.image_data_url(image_path),
                                    "detail": "original",
                                },
                            ]
                        )
                return content

            judge.content_for = content_for

            def cached_or_run(pass_name: str, order: list[str]) -> dict[str, Any]:
                judgment_path = output_dir / f"{pass_name}.judgment.json"
                if judgment_path.exists():
                    payload = load_json(judgment_path)
                    expected = {"a": order[0], "b": order[1]}
                    if payload.get("_order") != expected:
                        raise RuntimeError(
                            f"cached judge order mismatch: {judgment_path}"
                        )
                    return payload
                return judge.run_pass(
                    client, pass_name, order, wave, output_dir
                )

            normal = cached_or_run("normal", first_order)
            swapped = cached_or_run("swapped", list(reversed(first_order)))
            passes = [normal, swapped]
            winners = [item["_underlying_winner"] for item in passes]
            if winners[0] == winners[1]:
                verdict = winners[0]
                reason = (
                    "both balanced A/B orders selected the same underlying site"
                )
            else:
                verdict = "tie_inconclusive_order_sensitive"
                reason = (
                    "the balanced A/B orders did not select the same underlying site"
                )
            summary = {
                "cell": cell,
                "model": "gpt-5.6-sol",
                "wave": wave,
                "verdict": verdict,
                "verdict_reason": reason,
                "passes": [
                    {
                        "pass": item["_pass"],
                        "order": item["_order"],
                        "underlying_winner": item["_underlying_winner"],
                        "site_a_total": item["site_a"]["total"],
                        "site_b_total": item["site_b"]["total"],
                        "confidence": item["confidence"],
                        "response_id": item["_response_id"],
                        "usage": item["_usage"],
                    }
                    for item in passes
                ],
            }
            write_json(summary_path, summary)
            campaign_by_cell_wave[(cell, wave)] = summary
            write_json(
                campaign_path,
                [
                    campaign_by_cell_wave[key]
                    for key in sorted(campaign_by_cell_wave)
                ],
            )
            print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
