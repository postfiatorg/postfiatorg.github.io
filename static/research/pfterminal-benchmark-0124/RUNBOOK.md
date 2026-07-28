# PFTerminal 0.1.24 comprehensive release benchmark

Date: 2026-07-28 UTC

## Questions

This campaign answers three separate questions:

1. Does released PFTerminal still outperform Claude Code when both use direct
   Anthropic Opus 5 to build the same visual website?
2. Does released PFTerminal outperform Hermes Agent when both use the same Kimi
   K3 or GLM 5.2 route?
3. Do any apparent speed or cost advantages survive tasks with deterministic
   hidden verification, rather than only subjective website judging?

This is a harness benchmark. Model, provider route, task bytes, starting tree,
timeout, and verifier are matched inside each comparison cell. Native system
prompts, tool schemas, context management, caching, reasoning policy, and retry
behavior remain untouched because those are the harness behavior being tested.

## Frozen subjects

Record these in `manifest.json` immediately before the first paid run:

- PFTerminal release tag, commit, `--version`, binary path, and SHA-256.
- Hermes Agent version, source commit, binary path, and SHA-256.
- Claude Code version, binary path, and SHA-256.
- Task-tree and prompt SHA-256 values.
- Live route catalogue entries and prices.
- API-key fingerprints only; never copy key material into an artifact.

The PFTerminal lane must use the binary distributed as PFTerminal 0.1.24 or a
byte-identical binary built from its tagged commit. No later working-tree build
may enter the campaign.

Hermes must be updated once before freezing the manifest. It must not be
updated between cells.

## Matrix

Each cell has three fresh waves. A wave never reuses a workspace, agent home,
conversation, or cache.

| Workload | Model and route | PFTerminal opponent | Waves | Primary evidence |
| --- | --- | --- | ---: | --- |
| PFTerminal visual website | Direct Anthropic `claude-opus-5` | Claude Code | 3 | browser verifier + blind vision judges |
| PFTerminal visual website | OpenRouter `moonshotai/kimi-k3` | Hermes | 3 | browser verifier + blind vision judges |
| PFTerminal visual website | OpenRouter `z-ai/glm-5.2` | Hermes | 3 | browser verifier + blind vision judges |
| Queuecraft debugging | Vercel `zai/glm-5.2` | Hermes | 3 | 35 visible tests + 7 hidden probes |
| Queuecraft debugging | OpenRouter `z-ai/glm-5.2` | Hermes | 3 | 35 visible tests + 7 hidden probes |
| Queuecraft debugging | OpenRouter `moonshotai/kimi-k3` | Hermes | 3 | 35 visible tests + 7 hidden probes |
| EventForge implementation | OpenRouter `z-ai/glm-5.2` | Hermes | 3 | frozen visible and hidden verifier |
| EventForge implementation | OpenRouter `moonshotai/kimi-k3` | Hermes | 3 | frozen visible and hidden verifier |

This is 48 paid agent runs: 18 website runs, 18 Queuecraft runs, and 12
EventForge runs. Smoke probes and judges are additional calls.

## Historical baselines

These values are comparison anchors, not substitutions for fresh 0.1.24 runs.

- PFTerminal 0.1.23 Opus 5 website campaign, 2026-07-27:
  across two matched waves PFTerminal was 44.2% and 46.4% faster and 42.9% and
  32.9% cheaper than Claude Code. PFTerminal cost $3.3882 and $3.7356; Claude
  Code cost $5.9297 and $5.5634. All four sites passed the browser verifier.
  Both balanced GPT-5.6-Sol judgments were order-sensitive and therefore
  inconclusive, with mean score gaps of only 2.5 and 3.0 points toward Claude
  Code.
- Kimi K3 Queuecraft preserved-reasoning rebenchmark, 2026-07-27:
  PFTerminal solved 2/2 in 225.626 total seconds for $0.525786; Hermes solved
  2/2 in 547.410 total seconds for $2.217944.
- GLM 5.2 OpenRouter Queuecraft matched wave, 2026-07-27:
  PFTerminal solved in 161.993 seconds for $0.112968; Hermes solved in 203.354
  seconds for $0.254310.
- GLM 5.2 Vercel-fast Queuecraft control, 2026-07-27:
  both solved 3/3. PFTerminal took 86.980, 97.648, and 107.866 seconds and cost
  $0.218933, $0.263907, and $0.235605. Hermes took 269.618, 118.464, and
  255.824 seconds and cost $0.824789, $0.533337, and $0.879976.

## Execution rules

### Ordering and keys

- Direct Opus lanes run concurrently on different Anthropic API keys.
- Gateway lanes use different keys concurrently only when both key-specific
  billing deltas are available. Otherwise they run serially and alternate
  lane order by wave: PFTerminal/Hermes, Hermes/PFTerminal,
  PFTerminal/Hermes.
- No unrelated workload may use a campaign key during its billing window.
- Every lane gets an isolated `CODEX_HOME`, `HERMES_HOME`, or
  `CLAUDE_CONFIG_DIR`.
- Timeout is 45 minutes for website work and 20 minutes for deterministic
  coding work. A timeout is a measured failure, not a reason to silently extend
  one lane.

### Cost

Primary cost is authoritative provider billing over the exact run window:

- Anthropic Admin usage/cost grouped by API key.
- Vercel `/v1/credits` `total_used` delta.
- OpenRouter `/api/v1/key` `usage` delta.

Harness token telemetry and list-price reconstruction are diagnostic only.
Raw before/after billing responses and settlement timestamps must be cached.
Live pricing must be captured from the provider catalogue before launch; a
hard-coded price is never treated as billing evidence.

Website reporting separates three cost layers:

- contestant coding-model spend, which is the primary harness comparison;
- `gpt-image-2` generation spend, reconstructed from every evidenced billed
  response (including overwritten, discarded, and diagnostic generations)
  using the captured official image-output price; when traces expose only the
  final three-entry manifest, that manifest estimate is explicitly labeled a
  lower bound;
- neutral-judge spend, reported as experiment overhead and never assigned to a
  contestant.

Both contestant-only and all-in website totals must be shown. Do not silently
exclude the required image work from the all-in number.

The campaign targets at least $30 of settled agent spend so that it is not a
toy sample. Stop launching new cells at $75 cumulative spend and report the
completed matrix; never interrupt an active lane merely to hit the ceiling.

### Model policy

- Use the exact catalogue model IDs in the matrix.
- The headline harness cells use each product's catalogue-derived native
  default reasoning behavior. The exact outgoing reasoning controls are
  captured and reported; they are product behavior, not silently normalized.
- If the harness defaults differ, add a separately labeled matched-effort
  sensitivity pair after the three headline waves. Never mix that control into
  the headline aggregate.
- Opus uses direct Anthropic in both lanes and separate keys.
- Hosted search and image generation are either enabled identically or disabled
  identically within a cell. Website image generation uses the same image API
  and image-model policy for both lanes.
- A route mismatch invalidates the lane.

## Website validity and judging

Reuse byte-for-byte:

- the baseline tree and task prompt from
  `runs/opus5-visual-site-20260726T011738Z`;
- its static and Playwright browser verifier;
- six matched viewport captures;
- its visual rubric and structured judge schema.

A valid lane must exit successfully, pass static/browser checks, have no
uncaught browser errors, and produce all matched captures. Do not manually
repair a generated site.

Each valid pair is judged blind in both A/B orders. GPT-5.6-Sol is the primary
vision judge. A second independent vision judge is recorded separately; its
scores are not averaged with the primary judge unless both judges completed
all waves and both balanced orders. A winner is reported only when:

- both A/B orders select the same underlying site for that judge; and
- at least two of three waves select the same harness.

Otherwise the quality result is `inconclusive`. Functional failures always
remain failures regardless of visual score.

## Deterministic workload validity

Queuecraft reuses:

- source: `/home/pfrpc/repos/glm52-agent-bench/tasks/queuecraft/bugged`;
- verifier:
  `/home/pfrpc/repos/glm52-agent-bench/tasks/queuecraft/verifier/verify.py`;
- prompt builder from the preserved Kimi K3 campaign.

A solve requires process success, 35/35 visible tests, 35/35 hidden tests,
7/7 hidden probes, and proof that tests were not modified.

EventForge reuses the frozen baseline, prompt, and verifier from the
2026-07-02 PFTerminal-vs-Hermes campaign. The verifier is run independently
after the harness exits. Editing tests or verifier artifacts invalidates the
lane.

## Statistics and reporting

Report every raw wave and the following per cell:

- solves and valid outputs out of three;
- total and median wall time;
- total and median settled cost;
- time and cost per successful solve;
- input, cache-read, cache-write, output, and reasoning tokens when exposed;
- cache-read ratio and tool/API call counts;
- relative ratios with direction stated explicitly;
- browser verification and judge results for websites.

With only three waves, do not claim statistical significance. Label a result
`consistent` only when all three directional comparisons agree. Label it
`mixed` otherwise. Failed and timed-out runs remain in denominators and spend
totals.

## Cached artifacts

The campaign root must retain:

- `manifest.json` and a machine-readable matrix;
- immutable prompts and baseline hashes;
- fresh workspaces;
- stdout, stderr, exit metadata, and timing traces;
- request dumps with authorization removed;
- isolated agent homes or extracted session telemetry;
- raw verifier output;
- raw provider billing snapshots and calculated deltas;
- all website screenshots;
- `visual/image_generation_audit.json`, preserving per-lane evidence for
  billed image attempts that do not appear in the final manifest;
- `visual/lane_conformance_audit.json`, preserving route or requirement
  violations that mechanical site verification alone cannot detect;
- blind mappings, judge prompts, raw judgments, and response IDs;
- `REPORT.md`, `summary.json`, `summary.csv`;
- `slideshow/manifest.json` mapping every chart and screenshot to source
  evidence.

Secrets and full authorization headers must never be cached.

## Commands

After the GitHub release publishes, download the Linux x86 archive and freeze
the exact release subject:

```bash
python3 scripts/freeze_subjects.py \
  --release-archive downloads/pfterminal-package-x86_64-unknown-linux-gnu.tar.gz
```

Run deterministic cells:

```bash
python3 scripts/run_queuecraft.py \
  --cells glm-vercel glm-openrouter kimi-openrouter \
  --waves 1 2 3

python3 scripts/run_eventforge.py \
  --cells glm-openrouter kimi-openrouter \
  --waves 1 2 3
```

Run and judge website cells:

```bash
python3 scripts/run_visual.py \
  --cells opus kimi-openrouter glm-openrouter \
  --waves 1 2 3

python3 scripts/judge_visual.py \
  --cells opus kimi-openrouter glm-openrouter \
  --waves 1 2 3
```

After Anthropic usage settles, snapshot each exact Opus wave from the two
dedicated API keys, then build final artifacts:

```bash
python3 scripts/snapshot_anthropic_costs.py --waves 1 2 3
python3 scripts/summarize.py
python3 scripts/build_slideshow_manifest.py
python3 scripts/scan_secrets.py
```

The current Hermes release no longer has the historical built-in
`ai-gateway` alias. The Vercel control therefore uses Hermes' supported named
custom-provider contract (`custom:vercel-ai-gateway`) in an isolated
`HERMES_HOME`; the endpoint is stored in config and the credential remains
only in `AI_GATEWAY_API_KEY`.
