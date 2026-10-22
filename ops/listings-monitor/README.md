# Listings monitor

`run_monitor.py` checks Post Fiat's Coinbase listing package on a schedule.
The package has two parts:

- the website section https://postfiat.org/listings/ (this repository), and
- the source documents in `postfiatorg/postfiatl1v2`:
  `docs/listings/coinbase/{integration-plan,comparisons,reviewer-agent-guide}.md`,
  plus `README.md`, `docs/index.md` and `docs/whitepaper.md`.

Each run does three things. It runs deterministic freshness and consistency
checks, which cost nothing. It scores the documents with the Text Improvement
Harness (TIH). It asks a red-team model to review the package as a Coinbase
listing reviewer and as a hostile journalist would. Each run writes a dated
Markdown and JSON report. The process exits nonzero when a hard check fails,
so a failed systemd unit means the package needs attention.

The monitor never commits, pushes or sends mail. Its only writes are under
its state directory (default `~/.local/share/postfiat-listings-monitor/`).

## What a run checks

| Step | What | Model calls |
| --- | --- | --- |
| Upstream | `git ls-remote https://github.com/postfiatorg/postfiatl1v2 main`; repository tree at that commit | none |
| Chain facts | Parses network name, validator count and `Updated:` from `docs/status/chain-state-current.md` at public main. Compares them with the network names and validator counts stated on every `/listings/` page, in `index.json` strings, and in `index.json` `project.network` / `project.validators` | none |
| Mirrors | Collects every mirrored page: front matter `source_commit`/`source_path` in the site checkout, rendered "Source" buttons, and `index.json` `pages[]` entries of kind `mirror`. For each one, compares the file at the pinned commit with the file at main, and dates the first upstream change after the pin | none |
| Links | Crawls `/listings/` and its subpages, including the sitemap entries under `/listings/`. Checks every `<a href>` on them and every URL in `/listings/index.json`, GitHub links included, for HTTP 200. Checks in-page anchors. Inside the listing docs, checks that relative links and `blob/main` links resolve to files in the repository | none |
| `index.json`, `llms.txt` | `/listings/index.json` must parse; `/llms.txt` must mention `/listings/` | none |
| TIH audit | `audit` on a build of the site; only findings on `/listings/` pages count toward status | none |
| TIH scores | `score` on the integration plan (TIH default prompt) and on a snapshot of the `/listings/` landing page (TIH web-page prompt). Cheap gate on ordinary days, full gate (5 runs × 3 judges) on Mondays | cheap: 2 · full: 30 |
| Red team | One OpenRouter call to `openai/gpt-5.6-sol-pro` (fallback `anthropic/claude-fable-5.1`) with strict JSON output. Inputs: the landing page text, the three listing docs, an excerpt of the chain-state file and an index of repository paths. The monitor then checks every quote the model returns against the inputs and every file it names against the repository | 1 |

### Hard failures (exit 1)

- `/listings/` does not answer 200.
- A broken link on a `/listings/` page or in `index.json`: HTTP 404/410 or another 4xx (except 401, 403 and 429), or a DNS failure.
- A broken relative link or `blob/main` link inside a listing doc.
- `/listings/index.json` is missing or is not valid JSON.
- Mirror drift: main changed (or first published) a mirrored file more than `--drift-days` days ago (default 7) and the site still shows the older copy. Also a hard failure: the site mirrors a file that does not exist at public main, or pins a commit that does not exist upstream.
- One of the three listing docs is missing.
- A TIH audit error on a `/listings/` page, or `/listings/` is missing from the build.
- Full gate only: the integration plan averages below `--plan-threshold` (default 86, the mean of the three judges' lane averages), or the full gate could not finish.
- Public main cannot be read, or a stage of the monitor crashed (the traceback is in `runs/<id>/logs/`).

### Warnings (reported, exit unaffected)

- Links that answer 401/403 (coinbase.com sits behind a Cloudflare challenge), 429, 5xx, a timeout, or a 2xx other than 200 (EUR-Lex answers 202). These are marked "unverified" because the monitor could not check them. GitHub `blob`/`tree` links and crates.io links that fail over HTTP are re-checked through the GitHub contents API and the crates.io API before they count as broken. `link-expectations.json` lists the links whose non-200 answer is intended (for example the Coinbase currencies API's `NotFound` for an unlisted asset).
- A network name or validator count on the pages that disagrees with `chain-state-current.md`, or `/llms.txt` not mentioning `/listings/`. `--strict` turns both into hard failures.
- A mirror that drifted within the allowed window, a copy taken from uncommitted text (`source_dirty: true`), or an "in review" placeholder whose source document is not on main yet.
- Any judge lane that fell more than `--lane-drop` points (default 3) since the previous run at the same gate.
- `README.md` or `docs/index.md` does not link `docs/listings/coinbase/`, or a listing doc is not yet on public main.
- The red-team call failed, or its answer was not in the requested shape.

The red team's findings do not change the exit code. They are listed in the
report for a person to judge.

## Files

| File | Purpose |
| --- | --- |
| `run_monitor.py` | the monitor (standard library only; run with `--help` or `--self-test`) |
| `adversarial_prompt.md` | the red-team system and user prompt, with placeholders |
| `link-expectations.json` | links whose non-200 status is intended |
| `systemd/postfiat-listings-monitor.service`, `.timer` | user units: daily 06:30 UTC, full gate on Mondays |
| `systemd/monitor.env.example` | the options the service passes, for before and after launch |

## Running it

Run from any directory with the system `python3` (3.10 or later; standard
library only). TIH must be checked out at
`~/repos/text-improvement-harness-codex-plugin`, or pass `--tih-dir`. TIH's
key lookup supplies the OpenAI and OpenRouter keys (`python3 -m
text_improvement_harness keys` shows where they come from). The red-team
call reads the OpenRouter key from the same file. The key is used only in
the request header. It is never printed or logged.

Before launch, check the listings branch through a local server that the
monitor starts and stops itself:

```bash
python3 ops/listings-monitor/run_monitor.py --mode cheap --serve-local \
  --site-repo ~/repos/postfiatorg-site-listings-20261022 \
  --docs-repo ~/repos/postfiatl1v2-coinbase-listing-20261022
```

To check a site you build and serve yourself, run something like this:

```bash
~/.local/bin/hugo --gc --minify -d /tmp/pfsite --baseURL http://127.0.0.1:8765/
python3 -m http.server 8765 --bind 127.0.0.1 --directory /tmp/pfsite &
python3 ops/listings-monitor/run_monitor.py --base-url http://127.0.0.1:8765/ \
  --build-dir /tmp/pfsite --site-repo . --docs-repo ~/repos/postfiatl1v2-coinbase-listing-20261022
```

After launch, check the live site and read the docs from public main:

```bash
python3 ops/listings-monitor/run_monitor.py --mode full --site-repo ~/repos/postfiatorg.github.io
```

When the target is a local build, links to `https://postfiat.org/...` are
checked against the local server, so the run tests the build you are about
to deploy. `--site-repo` is optional for the live site. Without it, mirrors
are found from the rendered pages and `index.json`, and the TIH audit is
skipped with a warning.

Test runs that cost nothing:

```bash
python3 ops/listings-monitor/run_monitor.py --self-test      # offline parser tests
python3 ops/listings-monitor/run_monitor.py --mode full --mock --adversarial dry-run \
  --serve-local --site-repo . --docs-repo ~/repos/postfiatl1v2-coinbase-listing-20261022 \
  --state-dir /tmp/pflm-test
```

`--mock` passes `--mock` to TIH, which returns fixed fake scores. The
`dry-run` value of `--adversarial` builds and saves the red-team prompt but
does not send it. Use a separate `--state-dir` for test runs. Otherwise mock
scores land in the real history, although score deltas only ever compare
mock runs with mock runs.

Useful options (`--help` lists them all):

| Option | Default | Meaning |
| --- | --- | --- |
| `--mode` | `cheap` | `cheap`, `full`, or `auto` (full on Mondays, UTC) |
| `--runs` | 1 cheap, 5 full | runs per judge lane |
| `--score-docs` | `plan,landing` | which documents to score |
| `--cheap-lane` | `fable` | judge used by the cheap gate |
| `--adversarial` | `real` | `real`, `dry-run`, or `skip` |
| `--adversarial-reuse-days` | 7 | in cheap mode, reuse the last review if its inputs are byte-identical and it is this recent; 0 always calls |
| `--plan-threshold` / `--lane-drop` / `--drift-days` | 86 / 3 / 7 | hard and warning thresholds |
| `--strict` | off | chain-fact and `llms.txt` problems become hard failures |
| `--state-dir`, `--db`, `--project` | `~/.local/share/postfiat-listings-monitor`, `<state>/tih.sqlite3`, `postfiat-listings` | where state goes |

## Output

Under the state directory:

```text
reports/YYYY-MM-DD-<mode>.md     the report (a rerun on the same day overwrites it)
reports/YYYY-MM-DD-<mode>.json   everything in the report, machine-readable
reports/latest.md, latest.json   symlinks to the newest report
runs/<run-id>/                   fetched sources, page text, TIH logs, red-team prompt and raw answer
history.jsonl                    one line per run; used for score deltas and "changed since last run"
tih.sqlite3                      TIH database (project postfiat-listings); scores are under run group plm-<run-id>-<doc>
site-snapshots/postfiat-listings/listings.md   the landing-page text TIH scored
adversarial-cache.json           the last red-team input hash, for cheap-mode reuse
```

Reports are written outside the repository, under
`~/.local/share/postfiat-listings-monitor/reports/`, because they hold the
red team's raw findings and local paths. Do not commit them.

## How to read the report

1. **Status line.** PASS or FAIL, with counts. A "TEST RUN" banner means the
   scores were mock values or the red-team step was skipped.
2. **Hard failures, then warnings.** Each line names the check and
   what to fix. Work these first.
3. **Freshness and consistency.**
   - The mirror table shows, for each copied document, the pinned commit,
     how many commits main is ahead, whether the file changed, and the
     drift age.
   - The chain-facts table shows every network name and validator-count
     statement found on the pages, with a verdict for each.
   - The links table lists only the links that did not answer 200.
   - The source-documents table shows hashes and whether each document
     changed since the last run.
4. **Text Improvement Harness.**
   - The audit gives site-wide counts for context; only `/listings/`
     findings count.
   - The scores table gives each lane's average, minimum and maximum, the
     previous run's average and the change. Below it, each lane's
     lowest-scoring run is quoted with its "worst thing" and "next edit".
5. **Adversarial review.**
   - Readiness verdict and summary.
   - Unsupported or contradicted claims. Each quote carries the monitor's
     check: `verified` means found verbatim, `partial` means part of it was
     found, `not_found` means the model may have paraphrased or invented
     it. Each cited repository file is marked `exists at main`, `local
     checkout only`, or `NOT FOUND`.
   - Misleading framing and omissions, by topic: audit status, validator
     decentralization, privacy, NAVCoin reserve proofs, quantum claims.
   - Broken or circular references.
   - The five questions Coinbase would still ask.
   - Hostile-journalist headlines.
6. **Cost.** Tokens and dollars for each model, from provider-reported usage
   where available and OpenRouter list prices otherwise.

## Cost

These figures come from the 2026-10-22 runs. At that time the integration
plan was about 36k characters, the `/listings/` snapshot about 8k
characters, and the red-team prompt about 193k characters (all three listing
docs, the chain-state excerpt and the repository index). Prices are per
million tokens, input/output: `gpt-6-astra` $10/$50, `claude-fable-5.1`
$10/$50, `glm-5.3` $0.08/$1.40, `gpt-5.6-sol-pro` $4/$20.

| Call | Tokens in / out | Cost per call | Source |
| --- | --- | --- | --- |
| TIH fable, integration plan | 14,857 / 1,395 | $0.22 | measured (provider-reported) |
| TIH fable, landing page | about 3k / 1.4k | about $0.10 | estimate |
| TIH gpt-6-astra, plan / landing | about 15k / 2–4k; 3k / 1.5k | about $0.30 / $0.10 | estimate (reasoning output varies) |
| TIH glm-5.3, plan / landing | as above | under $0.01 | estimate |
| Red team, `gpt-5.6-sol-pro` | 249,524 / 42,203 (27,397 reasoning) | $1.46 | measured; the pro model bills the prompt about 5 times (multi-pass), and the call took 281 s |

| Run | Model calls | Cost |
| --- | --- | --- |
| Cheap (daily) | 2 TIH calls, plus 1 red-team call when any input changed in the last 7 days (otherwise the last review is reused) | about $0.32 with no input changes; about $1.80 with changes |
| Full (Mondays) | 30 TIH calls (2 docs × 3 judges × 5 runs) + 1 red-team call (never reused) | about $5 |
| A week (6 cheap + 1 full) | 42–48 calls | about $7 if nothing changes, about $16 if inputs change every day |

The deterministic checks cost nothing beyond GitHub and site requests: about
12 GitHub API calls and 6 raw fetches per run, using `gh auth token` when it
is available, plus one request for each unique link. Every report has a
**Cost** table that sums the actual tokens and dollars for that run.
`--adversarial skip` or `--score-docs plan` cut a run down further.

## Scheduling

`systemd/postfiat-listings-monitor.service` and `.timer` are user units. The
timer fires daily at 06:30 UTC with `Persistent=true`, so a missed run
happens at the next boot. The service runs `--mode auto`: the full gate on
Mondays and the cheap gate on other days. The monitor's own options come
from `~/.config/postfiat-listings-monitor/monitor.env` (see
`systemd/monitor.env.example`). Without that file, the service checks the
live site and reads the docs from GitHub main.

Install (not done by this change; run by hand when ready):

```bash
mkdir -p ~/.config/systemd/user ~/.config/postfiat-listings-monitor
cp ops/listings-monitor/systemd/postfiat-listings-monitor.{service,timer} ~/.config/systemd/user/
cp ops/listings-monitor/systemd/monitor.env.example ~/.config/postfiat-listings-monitor/monitor.env
chmod 600 ~/.config/postfiat-listings-monitor/monitor.env   # then edit it
systemctl --user daemon-reload
systemctl --user start postfiat-listings-monitor.service    # one run now, to try it
systemctl --user enable --now postfiat-listings-monitor.timer
```

To see results, use `systemctl --user list-timers postfiat-listings-monitor.timer`,
`journalctl --user -u postfiat-listings-monitor` and
`~/.local/share/postfiat-listings-monitor/reports/latest.md`. After the
listings branch merges, point `PFLM_SCRIPT` at the main checkout of this
repository, or delete the env file to use the live-site defaults.

## What depends on the live site

These parts need https://postfiat.org/listings/ to be deployed. Until then,
run them with `--serve-local` or `--base-url` pointed at a local build:

- link, `index.json` and `llms.txt` checks against the production host;
- the landing-page snapshot that TIH scores, taken from the production
  page; on a local target it comes from the build directory;
- the chain-fact and mirror checks as a reader sees them.

The listing docs are read from GitHub main unless `--docs-repo` is given.
Until `docs/listings/coinbase/` merges, a default run reports those
documents as missing, and links to them as broken.
