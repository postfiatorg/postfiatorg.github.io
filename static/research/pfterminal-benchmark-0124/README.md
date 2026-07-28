# PFTerminal 0.1.24 benchmark appendix

This directory is the public, sanitized appendix for the July 28, 2026
PFTerminal 0.1.24 campaign described in
`content/posts/introducing-pf-terminal.md`.

The campaign ran 48 paid contestant lanes:

- 18 visual-site lanes;
- 18 QueueCraft repair lanes;
- 12 EventForge implementation lanes.

It also ran 18 balanced-order GPT-5.6-Sol vision-judge passes. The summarized
results are in `REPORT.md`, `summary.json`, and `summary.csv`.

## Contents

- `RUNBOOK.md`: frozen methodology and execution commands.
- `MATRIX.json`: models, routes, workloads, lanes, and wave counts.
- `REPORT.md`: human-readable results.
- `summary.json` and `summary.csv`: chart-ready result data.
- `scripts/`: the exact campaign wrapper, accounting, judging, reporting, and
  secret-scan scripts.
- `drivers/`: inherited route drivers and the browser verifier used by those
  wrappers.
- `tasks/queuecraft/`: bugged QueueCraft repository, pristine tests, and hidden
  verifier.
- `tasks/eventforge/`: EventForge baseline, visible contract, task prompt, and
  hidden verifier.
- `visual/prompt.md`: the byte-frozen website-generation prompt.
- `visual/blind_judgments.json`: both A/B orders for all nine visual pairs.
- `visual/image_generation_audit.json`: confirmed discarded image generations
  and uncertain timeout upper bounds.
- `visual/lane_conformance_audit.json`: route violations excluded from matched
  success counts.
- `images/`: four representative captures used in the research post.
- `secret_scan.json`: exact-key scan result for the complete private campaign
  tree before this public subset was prepared.

## Reproduction boundary

The scripts are preserved as executed, including absolute paths from the
original benchmark host. They are evidence, not a turnkey installer. A rerun
requires:

1. updating `REPO_ROOT`, `RUN_ROOT`, binary, and credential-file paths;
2. installing PFTerminal, Hermes Agent, Claude Code, Python 3.12, and the
   Playwright browser dependencies;
3. supplying dedicated provider keys outside the repository;
4. restoring the directory layout expected by the inherited drivers; and
5. accepting that a live rerun spends provider and image credits.

No API keys, authorization headers, contestant home databases, or raw request
bodies are included here.

## Primary commands

```bash
python3 scripts/run_queuecraft.py \
  --cells glm-vercel glm-openrouter kimi-openrouter \
  --waves 1 2 3

python3 scripts/run_eventforge.py \
  --cells glm-openrouter kimi-openrouter \
  --waves 1 2 3

python3 scripts/run_visual.py \
  --cells opus kimi-openrouter glm-openrouter \
  --waves 1 2 3

python3 scripts/judge_visual.py \
  --cells opus kimi-openrouter glm-openrouter \
  --waves 1 2 3

python3 scripts/snapshot_anthropic_costs.py --waves 1 2 3
python3 scripts/summarize.py
python3 scripts/build_slideshow_manifest.py
python3 scripts/scan_secrets.py
```

The published data establish three-wave replication, not statistical
significance. Provider billing deltas are the primary cost evidence; internal
token telemetry is diagnostic.
