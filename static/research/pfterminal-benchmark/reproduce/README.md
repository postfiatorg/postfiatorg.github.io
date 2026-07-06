# Reproducing the Post Fiat Terminal benchmarks

This directory lets you (a) re-derive and validate every published number from the stored
raw artifacts **without spending anything**, and (b) run the live benchmark yourself with
your own provider accounts.

The harness is `runner.py` — pure Python standard library, no dependencies to install. The
benchmark machine should not need `pip install` before you can validate evidence.

## Files

- `runner.py` — the config-driven harness. Subcommands: `plan`, `run`, `validate-stored`,
  `report-stored`, `scan-keys`.
- `config.example.json` — a **sanitized** config template. Key files and absolute paths are
  placeholders (`/path/to/...`, `YOUR_..._API_KEY_ID`) — fill them in for a live run.
- The evidence files one directory up (`../`):
  - `raw-waves.csv` — one row per run: task, agent, wave, pass/fail, tests passed, wall-clock
    seconds, provider-billed cost, cost source, route verification.
  - `phase1-evidence-report.md` — the full report: methodology, billed lane totals, per-task
    tables with 95% CIs and paired p-values, and the billing reconciliation.
  - `vercel-report-settle.json` — Vercel `/v1/report` before/after billing by API key (GLM).
  - `frontier-token-reconciliation.json` — Anthropic Admin Usage tokens vs counted-run tokens
    per key (Opus & Fable); this is the key-cleanliness check.
  - `frontier-row-priced-cost-recovery.json` — the clean Fable cost derivation and the 0.005%
    Opus validation of the row×price method against real billing.
  - `frontier-fairness-controls.json` — same-model fairness controls (matched-effort
    disclosure, equivalent-output proxy, cost-ratio-equals-token-ratio gate).
  - `key-scan.json` — automated secret scan across all evidence artifacts (0 hits).

## No-spend validation (anyone can run this)

Re-derive the published tables from the stored artifacts and check them against the committed
report. Spends nothing, needs no API keys:

```sh
python3 runner.py --config config.example.json validate-stored
```

Scan every artifact for accidentally-committed secrets:

```sh
python3 runner.py scan-keys
```

## Live run (spends real provider credits)

You supply your own provider accounts and keys. **Keys are read from files or a vault — never
passed inline, never printed, never committed.** Point the config at your key files and set a
spend cap.

```sh
# dry-run plan first (no spend):
python3 runner.py --config config.example.json plan

# live:
python3 runner.py --config config.example.json run
```

## Method (short version)

- Shipped binary `pfterminal 0.1.8`. Ten Python tasks, each with a hidden held-out verifier;
  a run "passes" only if the verifier passes.
- **Paired**: Post Fiat Terminal and the baseline run the same task in the same wave, same day.
  Provider conditions swing day-to-day, so only same-day pairs are compared.
- **Speed** = wall-clock seconds to a verifier-passing solution.
- **Cost** = the provider's own billed amount (Vercel `/v1/report` by key; Anthropic Admin
  Usage by key/model), never internal token estimates. Each arm runs on its own dedicated key
  so concurrent arms never mix in the billing.
- **Significance** = paired test (Wilcoxon / paired-t) per task.

## A note on portability

`runner.py` and the real configs were written for the benchmark machine, so some paths (e.g.
`REPO_ROOT`, run directories, key-file locations) are environment-specific. `validate-stored`
works against the stored artifacts as shipped; for a live run on your own machine, adjust the
paths in your config and, if needed, `REPO_ROOT` at the top of `runner.py`.
