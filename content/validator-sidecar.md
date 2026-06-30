---
title: "Post Fiat Validator Scoring Sidecar Setup"
layout: "single"
url: "/validator-sidecar/"
summary: "End-to-end instructions for running the validator-scoring-sidecar alongside a Post Fiat testnet validator: verify the foundation's Dynamic UNL scoring and optionally participate on-chain via commit-reveal."
description: "Agent-readable and human-readable Post Fiat validator scoring sidecar setup guide: verify-only and on-chain commit-reveal participation on testnet."
keywords:
  - Post Fiat validator scoring sidecar
  - validator-scoring-sidecar
  - Dynamic UNL verification
  - commit-reveal participation
  - Modal inference sidecar
copyMarkdownHref: "/agents/validator-sidecar.md"
copyMarkdownButton: "Copy Full Markdown"
copyMarkdownDescription: "Copy and paste into your favorite LLM."
copyMarkdownStatus: "Full sidecar markdown copied."
copyMarkdownId: "pftSidecarCopyTool"
---

# Validator Scoring Sidecar Setup

> Run the validator-scoring-sidecar next to your Post Fiat testnet validator: independently verify the foundation's Dynamic UNL scoring, and — optionally — vote on each round on-chain through the commit-reveal protocol.

## Agent Operator Quick Start

This guide is written to be run by a coding agent (Codex or Claude Code) on your validator host, or followed by hand. Start the agent from a terminal on the same server that runs your validator. Do not paste the relay wallet seed, Modal secrets, or `validator-keys.json` contents into agent chat — keep all secret material in `.env` and on disk only.

For a hands-off run, start the agent in its bypass-permissions mode:

```bash
# Codex
codex --yolo

# or Claude Code
claude --dangerously-skip-permissions
```

Only use bypass-permissions mode on a host where you are comfortable letting the agent make Docker and file changes.

To start verify-only (no wallet, keys, or GPU needed), paste:

```text
Use https://postfiat.org/validator-sidecar/ to set up a verify-only validator scoring sidecar on this server.

NETWORK=testnet
SIDECAR_DIR=/opt/validator-scoring-sidecar

Run the sidecar in the default sync mode only. Do not configure participation, wallets, keys, or inference. Confirm a healthy first sync (`sync completed`) before finishing.
```

To run full on-chain participation, paste this instead and fill the placeholders:

```text
Use https://postfiat.org/validator-sidecar/ to set up a participating validator scoring sidecar on this server.

NETWORK=testnet
SIDECAR_DIR=/opt/validator-scoring-sidecar
INFERENCE=modal

I will provide the relay wallet seed, Modal credentials, and the path to my validator-keys.json through the .env file and on disk, never in chat. Before any step that needs my Modal account, relay wallet, or validator keys, stop and tell me plainly what I must do by hand (create the Modal account and its two tokens, create and fund a Task Node relay wallet, and place validator-keys.json on the host), then wait for me to paste the secrets into .env and confirm before you continue. Keep all secrets out of chat, logs, and image layers. Set up participation mode, start the container with the participation overlay, and verify a round reaches COMMITTED and then REVEALED before finishing.
```

## Scope

Use this guide to run the validator-scoring-sidecar alongside an existing Post Fiat **testnet** validator.

The sidecar does two things:

- **Verify (default).** It downloads the exact frozen inputs the foundation scored for each Dynamic UNL round and checks every file against the on-chain hash, so you can confirm the foundation scored untampered inputs.
- **Participate (opt-in).** It reproduces a round on your own inference runtime and records your independent result on-chain through commit-reveal, producing a public, validator-signed proof that you reproduced the round.

The sidecar never signs or publishes Validator Lists, never changes Validator List authority, never holds your validator master-key seed in process, and never touches consensus. It follows the foundation; it does not replace it.

## Inputs The Agent Needs

Confirm these before starting:

- `NETWORK`: `testnet`.
- `SIDECAR_DIR`: where the deployment lives, for example `/opt/validator-scoring-sidecar`.

For participation only, also:

- A funded operator **relay wallet seed** (a standard `r...` testnet account; Task Node is the default source — see below).
- The host path of your **`validator-keys.json`**.
- An **inference runtime**: a Modal account (default) or a local SGLang H100.

Never ask for or accept the relay seed, Modal secrets, or validator key material in chat. They belong in `.env` and on disk only.

## Prerequisites

- A host already running a Post Fiat **testnet** validator. If you do not have one yet, set it up first with the [validator setup guide](https://postfiat.org/validator-setup/). The sidecar runs on the same host.
- Docker and Docker Compose (already present if you followed the validator setup guide).

Participation additionally needs the three "bring your own" pieces covered in Part B: a funded relay wallet, your `validator-keys.json` on the host, and an inference runtime (a GPU). With managed Modal the GPU runs only during each weekly scoring round and scales to zero when idle, so the cost is on the order of a few dollars a month.

## Part A — Verify-Only (Start Here)

This is the safe default: it reads and verifies, changes nothing on-chain, and needs no wallet, keys, or GPU.

Create the deployment directory and fetch the published compose files and the testnet env template:

```bash
mkdir -p /opt/validator-scoring-sidecar && cd /opt/validator-scoring-sidecar

curl -fsSLO https://raw.githubusercontent.com/postfiatorg/validator-scoring-sidecar/testnet/docker-compose.yml
curl -fsSLO https://raw.githubusercontent.com/postfiatorg/validator-scoring-sidecar/testnet/docker-compose.participate.yml
curl -fsSL  https://raw.githubusercontent.com/postfiatorg/validator-scoring-sidecar/testnet/.env.testnet.example -o .env
```

Start the sidecar:

```bash
docker compose up -d
```

There is nothing to build: Docker pulls the published `agtipft/validator-scoring-sidecar:testnet-latest` image, runs the sync loop, and stores verified packages and state in a named volume.

Confirm a healthy first sync:

```bash
docker compose logs -f sidecar
```

A `sync completed` line means the first pass succeeded — either it fetched a fresh round, or there was no eligible round to fetch right now. Both are normal; foundation rounds run on a roughly weekly cadence.

If you only want continuous verification, you are done. Participation is the rest of this guide.

## Part B — Participation (On-Chain Commit-Reveal)

Participation reproduces each round and votes on it on-chain. It is **all-or-nothing**: the container refuses to start and changes nothing on-chain unless a relay wallet seed, validator-keys access, a reachable PFTL RPC, and a discoverable foundation publisher address are all present. The startup gate checks that these are present and reachable, not that the wallet holds funds — keep the relay wallet funded (a low-balance round is skipped at run time, see [Running It Reliably](#running-it-reliably)).

### How signing and paying are separated

This is the key safety property. The commit and reveal memos are **signed by your validator master key** (to prove which validator produced the result), but the transaction is **paid for and sent by a separate funded relay wallet** — an ordinary `r...` account that is deliberately *not* your validator identity. The sidecar never holds your master-key seed: it reads only the public key from `validator-keys.json` and signs by invoking the bundled postfiatd `validator-keys` tool, bound to that same file.

### B1 — Set Up Inference (Modal, default)

Participation scores on a GPU runtime that matches the foundation's pinned setup. The managed path is Modal, and it is zero-touch: once configured, the sidecar deploys the foundation-pinned endpoint itself and redeploys when the foundation pins a new runtime.

New to Modal? It is a serverless GPU host, and the agent can walk you through this live. You need an account plus two kinds of token:

1. Sign up at [modal.com](https://modal.com) and add a payment method under **Settings → Billing**. The endpoint runs on an **H100**, billed per GPU-second. Cost is minimal: Modal scales to zero when idle, so you pay only for the few minutes of H100 time each weekly scoring round uses, on the order of a few dollars a month and nothing while idle.
2. **Account token** (lets the sidecar deploy): in the Modal dashboard under **Settings → API Tokens**, create a token. Its id is `MODAL_TOKEN_ID`, its secret is `MODAL_TOKEN_SECRET`. CLI alternative: `pip install modal`, then `modal token new`.
3. **Proxy-auth token** (lets the sidecar call its own deployed endpoint): in the dashboard under **Settings → Proxy Auth Tokens**, create a token. Its id is `POSTFIAT_SIDECAR_MODAL_KEY`, its secret is `POSTFIAT_SIDECAR_MODAL_SECRET`.

These are two different token types: the first authorizes deploys, the second authorizes requests to the deployed endpoint. A token's secret is shown only once, when you create it, so copy it then; if you lose it, create a new one. All four are secret and go in `.env` only. Modal's own setup docs: https://modal.com/docs/guide

Running more than one validator against the same Modal account? Set a distinct `POSTFIAT_SIDECAR_MODAL_APP_NAME` per validator so they do not manage the same Modal app.

> Prefer your own hardware? See [Option: local SGLang](#option-local-sglang) below. Modal is the default and the simplest path.

### B2 — Get A Funded Relay Wallet (Task Node, default)

The relay wallet is a standard testnet `r...` account that pays the small per-round fees. The easiest way to get a funded one is **Task Node**, Post Fiat's onboarding app:

1. Go to [tasknode.postfiat.org](https://tasknode.postfiat.org/) and create a wallet (reply `new_wallet` in the Task Node messaging flow).
2. Task Node creates a self-custodial testnet wallet, sends you its **seed** (save it in a password manager — Post Fiat cannot recover it), and the faucet funds it with **100 testnet PFT** automatically. That is a long runway: each round costs only two tiny fees (commit + reveal).
3. Use that wallet's seed as `POSTFIAT_SIDECAR_VALIDATOR_WALLET_SEED`.

Bring-your-own alternative: any funded testnet `r...` account works, and keeps your participation cleanly separate from your Task Node identity. It must be a **different** account from your validator identity, and if you run more than one sidecar, each needs its own relay wallet so concurrent submissions do not collide on transaction sequence.

### B3 — Place Your `validator-keys.json`

Participation signs commit/reveal authorship with your validator master key, so the `validator-keys.json` you generated during validator setup must be present on the host and is mounted **read-only** into the container.

**Security note.** The validator setup guide recommends moving `validator-keys.json` off the host to offline storage after configuration. Participation needs it back on the host. Bring it back deliberately: place it at a known path and set its host path. The participation overlay mounts it read-only at `/keys/validator-keys.json`; the sidecar reads only the public key from it and never copies it into an image or logs it. The on-chain sender remains the relay wallet, not your validator identity.

**File permissions.** The sidecar container runs as a **non-root** user (uid/gid `1000`), so a root-owned `chmod 600` key file cannot be read inside the container and every commit fails with `could not read validator-keys file … Permission denied`. Grant read access to the container's group while keeping the file unreadable to other host users:

```bash
sudo chown root:1000 /opt/validator-scoring-sidecar/validator-keys.json
sudo chmod 640 /opt/validator-scoring-sidecar/validator-keys.json
```

This keeps the owner as `root` and grants read access only to gid `1000` (the container's user) — not to the world. Do not use `chmod 600` (unreadable by the non-root container) or `chmod 644` (world-readable on the host).

Set the host path:

```text
POSTFIAT_SIDECAR_VALIDATOR_KEYS_FILE=/opt/validator-scoring-sidecar/validator-keys.json
```

### B4 — Configure `.env` For Participation

Edit `.env` and uncomment/set the participation block:

```dotenv
POSTFIAT_SIDECAR_MODE=participate
POSTFIAT_SIDECAR_VALIDATOR_WALLET_SEED=<relay wallet seed>
POSTFIAT_SIDECAR_VALIDATOR_KEYS_FILE=/opt/validator-scoring-sidecar/validator-keys.json

# Inference — Modal (zero-touch); all four are secret
MODAL_TOKEN_ID=<modal account token id>
MODAL_TOKEN_SECRET=<modal account token secret>
POSTFIAT_SIDECAR_MODAL_KEY=<modal proxy-auth token id>
POSTFIAT_SIDECAR_MODAL_SECRET=<modal proxy-auth token secret>
```

If an agent is driving the setup, have it prepare these lines in `.env`, then paste your seed and the four Modal values into the file yourself, so the secrets never pass through the chat.

The PFTL RPC URL and the foundation publisher address are discovered automatically (RPC defaults to `https://rpc.testnet.postfiat.org`, the publisher comes from the scoring service config). Override them only if you have a reason to.

### B5 — Start Participation

Start with the participation overlay on top of the base compose file:

```bash
docker compose -f docker-compose.yml -f docker-compose.participate.yml up -d
```

This switches to the published `testnet-participate-latest` image (which bundles the postfiatd `validator-keys` signing tool) and mounts your key file read-only. If any prerequisite is missing, the container logs a clear error and changes nothing on-chain.

What to expect on Modal: the **first** auto-deploy of the inference endpoint takes roughly **18 minutes** (image build and kernel compilation); later deploys are seconds, and a cold start after idle is about 5 minutes. The endpoint scales to zero when not in use. This is normal — the first scored round is not stuck.

### Option: Local SGLang

If you run your own H100 instead of Modal, the sidecar does not manage that hardware — you start the runtime and the sidecar points at it. On the GPU host:

```bash
# on the GPU host, from a sidecar source checkout: install the local extra
python -m pip install -e ".[local]"
# then start the manifest-pinned runtime
validator-scoring-sidecar start-sglang --network testnet
```

Then set the container-reachable endpoint in `.env` (localhost inside the container is not the host):

```dotenv
POSTFIAT_SIDECAR_LOCAL_ENDPOINT_URL=http://host.docker.internal:8000/v1
```

Leave the four Modal values unset in this mode. If `start-sglang` ran on a different machine than the container, copy its deployment record into the data volume:

```bash
docker compose cp <path>/deployment_record.json sidecar:/data/runtime/deployment_record.json
```

Local mode is operator-managed: when the foundation pins a new runtime, the sidecar reports the round as runtime-incompatible and you re-run `start-sglang`. See the repository [`docs/Deployment.md`](https://github.com/postfiatorg/validator-scoring-sidecar/blob/main/docs/Deployment.md) for details.

## Verifying A Healthy Participation Run

Watch the loop:

```bash
docker compose -f docker-compose.yml -f docker-compose.participate.yml logs -f sidecar
```

Each pass logs `participate completed` (or `participate failed; sleeping …` on a transient error that is retried next pass). There is nothing to do per round — you "join" a round by running while its commit and reveal windows are open.

Inspect per-round state directly (the image ships Python's `sqlite3`):

```bash
docker compose exec sidecar python -c "
import sqlite3
db = sqlite3.connect('/data/sidecar.db'); db.row_factory = sqlite3.Row
for r in db.execute('SELECT round_number, sidecar_state, commit_tx_hash, reveal_tx_hash, error_category, reveal_error_category FROM sidecar_rounds ORDER BY round_number DESC LIMIT 10'):
    print(dict(r))
"
```

A round advances `DISCOVERED → INPUT_PACKAGE_VERIFIED → SCORED → COMMITTED → REVEALED`. Seeing a round reach `COMMITTED` (with a `commit_tx_hash`) and then `REVEALED` (with a `reveal_tx_hash`) is the success signal.

After your reveal, the foundation publishes a per-round convergence report you can read back, keyed on the on-chain round number:

```bash
curl https://scoring-testnet.postfiat.org/api/scoring/rounds/<round_number>/convergence
```

## Running It Reliably

- **Keep the container running** — the reveal happens passes after the commit, so a host down across the reveal window misses that round's vote.
- **Keep the relay wallet funded** — maintain the account reserve plus a long runway of per-round fees. A low-balance commit is skipped for that round; fund ahead.
- **Keep the poll interval short** — the 60-second default sits well inside the windows.
- **Do not wipe the volume** — `docker compose down` keeps your state; only `down -v` erases it.

Update the sidecar with:

```bash
docker compose -f docker-compose.yml -f docker-compose.participate.yml pull
docker compose -f docker-compose.yml -f docker-compose.participate.yml up -d
```

State in the named volume is untouched.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| `participate failed` with `could not read validator-keys file … Permission denied` | The key file is not readable by the container's non-root user (uid/gid `1000`) — typically left at root-owned `chmod 600` | `sudo chown root:1000 … && sudo chmod 640 …` the key file (see the **B3** file-permissions note). A root-only `chmod 600` file cannot be read inside the non-root container. |
| A commit or reveal status is `skipped_low_balance` | Relay wallet underfunded | Fund the relay `r...` account. A low-balance reveal retries while its window is open; a low-balance commit is terminal for that round. |
| Won't start: `PFTL RPC … is not reachable` | RPC down or wrong URL | Fix `POSTFIAT_SIDECAR_PFTL_RPC_URL`; confirm the node answers `server_info`. |
| `participate failed; sleeping …` with an RPC error | Transient RPC failure | No action — the round is retried next pass. If it persists, check the RPC node. |
| Round `error_category` = `MANIFEST_INCOMPATIBLE` | Deployed runtime does not match the round's pinned manifest | Modal redeploys automatically; local SGLang: re-run `start-sglang`. A parser/selector mismatch ("vendor refresh required") means upgrading the sidecar image. |
| Round `error_category` = `MANIFEST_UNSUPPORTED` | Manifest schema newer than this sidecar | Upgrade the sidecar image (`docker compose pull`). |
| Scored round is `divergent` (`OUTPUT_DIVERGENCE`) | Your reproduction differs from the foundation | Not fatal — the round is still committed and revealed. Check the convergence report for the level that diverged. |
| `COMMITTED` round with `reveal_error_category` = `REVEAL_WINDOW_MISSED` | The reveal window closed before the reveal landed | Terminal for that round. Prevent it with funding, uptime, and a short poll interval. |

For the full operator reference, see the repository docs: [`Usage.md`](https://github.com/postfiatorg/validator-scoring-sidecar/blob/main/docs/Usage.md), [`Configuration.md`](https://github.com/postfiatorg/validator-scoring-sidecar/blob/main/docs/Configuration.md), and [`Deployment.md`](https://github.com/postfiatorg/validator-scoring-sidecar/blob/main/docs/Deployment.md).

## Agent Safety Checklist

- Never paste the relay wallet seed, Modal secrets, or `validator-keys.json` contents into chat. Keep them in `.env` and on disk only.
- Keep `validator-keys.json` mounted read-only and readable only by `root` and the container's group (`chown root:1000 && chmod 640` — a root-only `chmod 600` file is unreadable by the non-root container); prefer removing it from the host again if you stop participating.
- The relay wallet is deliberately not your validator identity — keep them separate, and use a distinct relay wallet per sidecar.
- Start verify-only first and confirm `sync completed` before taking on participation cost.
- Participation is all-or-nothing: expect it to fail fast and change nothing on-chain if a prerequisite is missing.
- Verify a round reaches `COMMITTED` then `REVEALED` before declaring the setup healthy.
