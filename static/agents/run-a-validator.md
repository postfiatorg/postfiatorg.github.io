# Run a Post Fiat Validator (L1v2)

> **Status on 27 November 2026: not yet open to outside operators.** This page describes how the program will work. Parts of it are built and not yet released, so you cannot follow it end to end today:
>
> - **Not released yet:** the signed release channel, `postfiat-node upgrade`, `postfiat-node top`, the read-replica RPC profiles, `postfiat-node tasknode-bind`, and the three-observer uptime feed. They are in review ([postfiatl1v2#286](https://github.com/postfiatorg/postfiatl1v2/pull/286), [#290](https://github.com/postfiatorg/postfiatl1v2/pull/290)).
> - **Not built yet:** the commands to apply and be ratified as a validator.
> - **Running today:** six Foundation validators on `postfiat-wan-devnet-2`. The uptime rule and the 14 days of grace are not enforced yet, and the $20 monthly credit is not paid yet.
>
> The hardware numbers below are estimates until the measured ones are published.

> **Looking for the legacy `postfiatd` testnet chain?** See the [Legacy Testnet Validator Setup (`/validator-setup/`)](/validator-setup/). This page is the single canonical guide for **`postfiatl1v2`** validators and read-replica RPC nodes.

## Overview & Rewards

Running an active Post Fiat L1v2 validator requires **no stake and no financial bond**. Approved outside operators who keep their validator online and voting earn three things per operator:

1. **[Finance Hub access](/finance-hub/)** — the full GoodAlexander company/crypto model desk, daily **Today** feed, **Goodbrief** macro roundup, and GoodAlexander Library.
2. **GoodAlexander Research API keys** — programmatic research access reserved exclusively for active validators.
3. **$20/month in Task Node USD credit** — usable directly on Task Node (including Deep Research), granted **once per operator** (not per node) across old and new chains during migration.

### Single Binary Invariant (`postfiat-node`)

There is **no separate RPC codebase**. Validators, private loopback RPC nodes, and public TLS read-replica RPC nodes all run the exact same `postfiat-node` binary (`linux-x86_64` or `linux-aarch64`), installed and upgraded from the exact same **2-of-3 offline ML-DSA-65 signed release channel**.

---

## 1. Requirements, Measured Hardware Sizing & Firewall

### Recommended Hardware

| Resource | Minimum (Validator Only) | Recommended (Validator + Read-Replica RPC) | Notes |
| --- | --- | --- | --- |
| **OS** | Ubuntu 22.04 LTS / 24.04 LTS (`x86_64` or `aarch64`) | Ubuntu 24.04 LTS (`x86_64` or `aarch64`) | Native `systemd` with cgroup v2 required for consensus/RPC isolation |
| **CPU** | 4 vCPU (dedicated or low-steal) | 8 vCPU | ML-DSA-65 signature verification + isolated RPC cgroup |
| **RAM** | 8 GB | 16 GB | Consensus + `redb` page cache; RPC replica capped at `MemoryHigh=3G` / `MemoryMax=4G` |
| **Disk** | 250 GB NVMe SSD | 500 GB NVMe SSD | `postfiat-node upgrade` enforces **`>= 2×` chain-data free space + binary + 512 MiB** before every upgrade |
| **Network** | 100 Mbps symmetric, 1 TB/mo | 1 Gbps symmetric, 2+ TB/mo | Low-jitter connectivity; latency-fair uptime scoring does not penalize distant regions |
| **Est. Monthly Cost** | ~$25–$40/mo | ~$45–$75/mo | Bare-metal or non-crowded cloud VPS (distinct provider/region improves set diversity) |

### Ports & Firewall Posture

| Port / Surface | Exposure | Purpose |
| --- | --- | --- |
| `SSH` (default `22/tcp`) | Operator IP / key-only | Administration and `postfiat-node top` SSH dashboard (no web dashboard port) |
| Consensus P2P (`26656/tcp` or network-assigned peer port) | Public inbound/outbound | Validator consensus gossip and block replication |
| Private RPC (`127.0.0.1:27650`) | **Loopback only** | Local `postfiat-node top`, `rpc-probe`, and private read-replica queries |
| Public RPC (`127.0.0.1:27651` → TLS edge `:443/tcp`) | Opt-in public `:443` via `postfiat-edge` | Optional public TLS 1.3 read-replica RPC; node itself **never** binds `0.0.0.0` |
| Signer socket (`/run/postfiat-signer/signer.sock`) | **Local Unix socket (`0600`)** | Isolated `postfiat-signer` UID only; never TCP, never network-exposed |

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 26656/tcp comment 'Post Fiat L1v2 P2P'
# Only open 443/tcp if opting into a public TLS read-replica RPC edge:
# sudo ufw allow 443/tcp comment 'Post Fiat Public RPC TLS'
sudo ufw --force enable
sudo ufw status verbose
```

---

## 2. Keys, Two-User Signer Isolation & Custody

Post Fiat L1v2 separates long-lived validator identity from live consensus signing using two distinct OS users and an immutable double-sign guard directory:

- **Offline Master Key:** Held offline by the operator. Used only for initial registration, manifest updates, and hot consensus key rotation. Never stays on the live validator host.
- **Hot Consensus Key (`validator-signer-serve`):** Runs inside a dedicated signer process under OS user **`postfiat-signer`** (distinct from consensus node user **`postfiat`** and RPC replica user **`postfiat-rpc`**). Communicates over a local permission-scoped Unix socket.
- **Immutable Double-Sign Guard Directory (`/var/lib/postfiat/signer-guard/`):** Stores monotonic round-floor state preventing equivocation. **This directory MUST be disjoint from `--data-dir` and `--backup-dir` and is NEVER copied, backed up, or rolled back during upgrades.**
- **Custody boundary note:** Hardware Security Module (HSM) custody is not yet implemented in `postfiat-node` v1; software key isolation via the separate `postfiat-signer` UID and offline master key is the supported production boundary.

### Create Dedicated OS Users and Directories

```bash
sudo useradd --system --home-dir /nonexistent --shell /usr/sbin/nologin postfiat
sudo useradd --system --home-dir /nonexistent --shell /usr/sbin/nologin postfiat-signer
sudo useradd --system --home-dir /nonexistent --shell /usr/sbin/nologin postfiat-rpc

sudo mkdir -p /etc/postfiat \
              /var/lib/postfiat/validator-0 \
              /var/lib/postfiat/signer-guard \
              /var/lib/postfiat/backups \
              /var/lib/postfiat-rpc/replica \
              /var/log/postfiat-rpc

sudo chown postfiat:postfiat /var/lib/postfiat/validator-0 /var/lib/postfiat/backups
sudo chown postfiat-signer:postfiat-signer /var/lib/postfiat/signer-guard
sudo chmod 0700 /var/lib/postfiat/signer-guard
sudo chown postfiat-rpc:postfiat-rpc /var/lib/postfiat-rpc/replica /var/log/postfiat-rpc
```

---

## 3. Install from the 2-of-3 Signed Release Channel

Every tagged public release (`linux-x86_64` and `linux-aarch64`) publishes:

- `postfiat-node-linux-x86_64` and `postfiat-node-linux-aarch64` binaries;
- Packaged `systemd` unit templates (validator, two-user signer, private RPC replica, public RPC replica) and Docker Compose profiles;
- Deterministic CycloneDX SBOM (`postfiat-cargo-sbom.cdx.json`) and `SHA256SUMS`;
- Pinned finalized catch-up checkpoint (`height`, `block_hash`, `state_root`, `certificate_id`, `committee_epoch`);
- `release-manifest.json` (`postfiat.release_manifest.v3`) co-signed by **2-of-3 offline ML-DSA-65 release keys** (`release_lead`, `independent_builder`, `security_custodian`) under signing context `postfiat-l1-v2/release-manifest/v3`.

### Pin the Release Keyset and Verify the Binary

1. Install the pinned 2-of-3 release keyset (`postfiat.release_keyset.v1`) at `/etc/postfiat/release-keyset.json` (`0644`, `root:root`) and the 3-observer trust keyset at `/etc/postfiat/observer-keyset.json` (`0644`, `root:root`). Verify keyset fingerprints out-of-band against the signed release announcement.
2. Provision a previously authenticated release verifier at `/usr/local/libexec/postfiat-release-verifier`, owned by root. This is a trusted build of `postfiat-node` with the `release-manifest-verify` command. On first installation it must come through an independently authenticated distribution or reproducible build. Keep it separate from the candidate. When the verifier and pinned keyset are available, run these commands in Bash:

```bash
set -euo pipefail
stage=$(mktemp -d)
trap 'rm -rf -- "$stage"' EXIT
ARCH="$(uname -m)"
case "$ARCH" in
  x86_64)  PF_ARCH="linux-x86_64" ;;
  aarch64) PF_ARCH="linux-aarch64" ;;
  *) echo "Unsupported architecture: $ARCH" >&2; exit 1 ;;
esac

RELEASE_BASE="https://releases.postfiat.org/latest"
curl -fsSL "$RELEASE_BASE/release-manifest.json" -o "$stage/release-manifest.json"
curl -fsSL "$RELEASE_BASE/postfiat-node-${PF_ARCH}" -o "$stage/postfiat-node"


# Fail-closed 2-of-3 ML-DSA-65 signature + SHA-256 verification before installing:
/usr/local/libexec/postfiat-release-verifier release-manifest-verify \
  --manifest-file "$stage/release-manifest.json" \
  --keyset-file /etc/postfiat/release-keyset.json \
  --runtime-binary-file "$stage/postfiat-node"

sudo install -m 0755 -o root -g root "$stage/postfiat-node" /usr/local/bin/postfiat-node
sudo install -m 0644 -o root -g root "$stage/release-manifest.json" /etc/postfiat/release-manifest.json
```

---

## 4. Join the Validator Set (No Stake / No Bond)

Post Fiat L1v2 validator admission is **stake-free**. The launch minimum set size is **12 validators** with at most **2 seats per correlated operator group** (the Foundation scales down from 6 devnet nodes to at most 2 correlated seats as outside validators join).

### Path A — Genesis Cohort (`G0`, Old-Chain Dynamic UNL Validators)

Approved validators from the old-chain Dynamic UNL round join `G0` by signing an **`IdentityReceiptV1`** binding their legacy validator key to their new post-quantum ML-DSA-65 validator key:

```bash
postfiat-node identity-receipt \
  --legacy-key-file /secure/offline/validator-keys.json \
  --new-validator-pubkey-file /etc/postfiat/validator-master.pub \
  --chain-id postfiat-testnet-1 \
  --out /tmp/identity-receipt.json
```

### Path B — Open Admission (Admission Policy V1 + Ratification)

Subsequent outside operators apply with zero stake:

1. Generate your node manifest, infrastructure attestation, and ML-DSA-65 key proof.
2. Submit your admission packet for deterministic **Admission Policy V1** evaluation (`admit` / `hold` / `reject`). Verified Task Node standing counts as positive evidence.
3. Current active validators explicitly ratify admitted operators via the on-chain Cobalt validator registry transition.

### Hot Consensus Key Rotation

Rotate your hot consensus key without exposing your offline master key using `validator-key-stage` followed by the signed on-chain registry transition:

```bash
# 1. Stage a fresh hot key inside the isolated signer directory
sudo -u postfiat-signer postfiat-node validator-key-stage \
  --signer-guard-dir /var/lib/postfiat/signer-guard

# 2. Sign the key-rotation registry transition with your offline master key and submit
# 3. Verify `signer_key_matches_registry = true` in `postfiat-node top`
```

---

## 5. Safe Manual Upgrades (`postfiat-node upgrade`)

Upgrades are **always manual**. A validator never auto-reboots mid-consensus.

### Read-Only Preflight Check

Run `--check` first to inspect whether the latest verified release is a **rolling** upgrade or an **activation-height** upgrade (`activation_height H`, advance warning window, and `halt_if_missed` behavior) and verify free disk headroom:

```bash
postfiat-node upgrade --check \
  --keyset-file /etc/postfiat/release-keyset.json \
  --data-dir /var/lib/postfiat/validator-0 \
  --signer-guard-dir /var/lib/postfiat/signer-guard \
  --backup-dir /var/lib/postfiat/backups
```

### Apply a Verified Upgrade

```bash
sudo postfiat-node upgrade \
  --keyset-file /etc/postfiat/release-keyset.json \
  --data-dir /var/lib/postfiat/validator-0 \
  --signer-guard-dir /var/lib/postfiat/signer-guard \
  --binary-path /usr/local/bin/postfiat-node \
  --backup-dir /var/lib/postfiat/backups \
  --service-units postfiat-validator-0.service,postfiat-validator-0-rpc.service \
  --rpc-host 127.0.0.1 \
  --rpc-port 27650 \
  --health-timeout-ms 60000
```

What `postfiat-node upgrade` enforces in strict order:

1. Verifies **2-of-3 ML-DSA-65 signatures** on `postfiat.release_manifest.v3`, checks `chain_id` and `genesis_hash`, downloads the candidate binary, and verifies `binary_sha256` and `binary_size_bytes`.
2. Verifies `--signer-guard-dir` (`/var/lib/postfiat/signer-guard/`) is strictly disjoint from `--data-dir` and `--backup-dir` (hard refusal `exit 3` on overlap). **Signer guard state is never copied, backed up, or rolled back.**
3. Confirms free disk space satisfies `free_bytes >= 2 * data_dir_bytes + binary_bytes + 512 MiB` before stopping any service.
4. Stops systemd units cleanly, backs up **chain state only** plus the previous binary with SHA-256 checksums, swaps the binary via atomic `rename(2)` + `fsync`, and restarts services.
5. Verifies `rpc-probe`, matching `git_revision`, monotonic `block_height`, and `signer_double_sign_protection = true`. If any check fails within `--health-timeout-ms`, it **automatically rolls back both the prior binary and pre-upgrade chain state together** while leaving `/var/lib/postfiat/signer-guard/` untouched.

### `postfiat-node upgrade` Exit Codes

| Exit Code | Meaning |
| --- | --- |
| `0` | Upgrade applied and healthy (or already up-to-date in `--check` mode) |
| `2` | Invalid CLI arguments or configuration error |
| `3` | Security refusal: invalid 2-of-3 signature, checksum mismatch, chain mismatch, or signer-guard path overlap |
| `4` | Preflight failure: insufficient free disk space (`< 2×` chain data) or unhealthy pre-upgrade state |
| `5` | Post-upgrade health check failed; automatic binary + chain-state rollback succeeded |
| `6` | Critical: post-upgrade health check failed AND rollback verification failed (operator intervention required) |
| `10` | `--check` mode: newer verified rolling or non-urgent upgrade available |
| `11` | `--check` mode: `activation_height` upgrade inside advance warning window (action required before halt height) |

---

## 6. Run a Read-Replica RPC Node (Same `postfiat-node` Binary)

Running a public RPC or `--allow-private-action-admission` endpoint is **opt-in** for outside validators at launch (the Foundation operates the first 2 public RPC + private-admission endpoints; outside operators can opt in and optionally monetize public RPC via Pillar 2 `x402`).

### Consensus Isolation (Anti-DoS)

Public RPC traffic must **never** contend with consensus voting or the consensus node's exclusive `redb` writer lock. Run one of two supported topologies:

- **Topology A (Same host, cgroup-isolated):** `postfiat-rpc-public.service` runs as unprivileged user `postfiat-rpc` with strict systemd cgroups (`CPUQuota=200%`, `CPUWeight=25`, `MemoryHigh=3G`, `MemoryMax=4G`, `IOWeight=50`, `TasksMax=512`) while consensus runs at `CPUWeight=200`, `IOWeight=500`.
- **Topology B (Dedicated follower host):** A separate server runs `postfiat-node` in non-voting follower mode, catching up from release-pinned checkpoints via `postfiat-node rpc-catch-up-certified-delta`.

### Non-Voting Follower Invariants

Both `private-replica` and `public-replica` profiles enforce at startup:

- `node_role = "rpc_follower"`, `voting_enabled = false`, `validator_signer = "none"`;
- Passing any signer key or socket flag fails closed immediately (`rpc_replica_signer_forbidden`);
- Plaintext RPC binds **strictly to loopback** (`127.0.0.1:27650` private, `127.0.0.1:27651` public behind a TLS 1.3 `:443` `postfiat-edge` proxy with `MAX_RPC_REQUEST_BYTES=65536` and per-IP rate limits).

### Catch Up from a Release-Pinned Checkpoint

```bash
sudo -u postfiat-rpc postfiat-node rpc-catch-up-certified-delta \
  --data-dir /var/lib/postfiat-rpc/replica \
  --manifest-file /etc/postfiat/release-manifest.json \
  --keyset-file /etc/postfiat/release-keyset.json
```

### Canonical Public Read-Replica Systemd Unit (`/etc/systemd/system/postfiat-rpc-public.service`)

```ini
[Unit]
Description=PostFiat Public Read-Replica RPC (non-voting follower)
After=network-online.target
Wants=network-online.target
StartLimitIntervalSec=300
StartLimitBurst=5

[Service]
Type=simple
User=postfiat-rpc
Group=postfiat-rpc
ExecStartPre=/usr/local/libexec/postfiat-release-verifier release-manifest-verify \
  --manifest-file /etc/postfiat/release-manifest.json \
  --keyset-file /etc/postfiat/release-keyset.json \
  --runtime-binary-file /usr/local/bin/postfiat-node
ExecStart=/usr/local/bin/postfiat-node rpc-serve \
  --rpc-profile public-replica \
  --data-dir /var/lib/postfiat-rpc/replica \
  --spool-dir /run/postfiat-rpc-public/spool \
  --ready-file /run/postfiat-rpc-public/ready.json \
  --bind-host 127.0.0.1 \
  --port 27651 \
  --max-requests 100000 \
  --timeout-ms 15000 \
  --child-timeout-ms 15000 \
  --max-child-dispatch-concurrent 8 \
  --max-child-dispatch-per-peer 4 \
  --max-replica-lag-blocks 5 \
  --event-log /var/log/postfiat-rpc/rpc-events.ndjson \
  --keep-alive
RuntimeDirectory=postfiat-rpc-public
RuntimeDirectoryMode=0700
Restart=always
RestartSec=1
TimeoutStopSec=30s
KillMode=control-group
CPUQuota=200%
CPUWeight=25
MemoryHigh=3G
MemoryMax=4G
IOWeight=50
TasksMax=512
LimitNOFILE=65536
LimitCORE=0
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ProtectControlGroups=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectKernelLogs=true
RestrictSUIDSGID=true
LockPersonality=true
RestrictRealtime=true
SystemCallArchitectures=native
CapabilityBoundingSet=
AmbientCapabilities=
ReadWritePaths=/var/lib/postfiat-rpc/replica /var/log/postfiat-rpc /run/postfiat-rpc-public
UMask=0077

[Install]
WantedBy=multi-user.target
```

*(Matching Docker Compose profiles `docker-compose.rpc-private.yml` and `docker-compose.rpc-public.yml` ship inside every signed release bundle.)*

### Published `< 250ms` Read-Path SLO Targets

| Method Class | Example Methods | p50 | **p95 (SLA)** | p99 |
| --- | --- | ---: | ---: | ---: |
| Status & readiness | `status`, `server_info`, `metrics`, `private_readiness` | `<= 10 ms` | **`<= 25 ms`** | `<= 50 ms` |
| Account, registry & fee reads | `account`, `account_lines`, `validators`, `fee`, `fastpay_fee_quote` | `<= 25 ms` | **`<= 100 ms`** | `<= 200 ms` |
| Keyed history reads | `blocks` (`limit <= 8`), `receipts`, `tx` | `<= 35 ms` | **`<= 150 ms`** | `<= 250 ms` |
| Bridge & route reads | `vault_bridge_route`, `vault_bridge_status`, `bridge_status` | `<= 50 ms` | **`<= 200 ms`** | `<= 350 ms` |
| Keyed egress witness | `pfusdc_egress_witness`, `shield_turnstile`, `shield_disclose` | `<= 100 ms` | **`<= 250 ms`** | `<= 500 ms` |
| **Global Standard Read SLA** | Combined 50 req/s steady read workload | `<= 50 ms` | **`< 250 ms`** | `<= 500 ms` |

Replica freshness lag target is `<= 1 block` p95; exceeding `5` blocks lag flips `ready = false` so the TLS edge drains traffic cleanly.

---

## 7. Monitor Over SSH (`postfiat-node top`)

`postfiat-node top` is a strictly **read-only** terminal UI over SSH. It binds **no web port**, issues no write RPCs, and never reads private keys or signer guard files.

```bash
# Live interactive SSH dashboard (default 2s refresh)
postfiat-node top \
  --rpc-host 127.0.0.1 \
  --rpc-port 27650 \
  --data-dir /var/lib/postfiat/validator-0 \
  --uptime-feed-url https://uptime.postfiat.org/v1/feed.json \
  --observer-keyset-file /etc/postfiat/observer-keyset.json \
  --release-manifest-url https://releases.postfiat.org/latest/release-manifest.json \
  --release-keyset-file /etc/postfiat/release-keyset.json

# One-shot JSON snapshot (schema: postfiat-node-top-snapshot-v1) for scripts/alerts:
postfiat-node top --once --json
```

**Interactive controls:** `q` / `Ctrl-C` quit · `r` refresh now · `p` pause/resume · `j`/`k` scroll warnings.

**Seven dashboard panels:**

1. **Node & Release Banner** — `node_id`, `role`, `chain_id`, `git_revision`, uptime, and verified upgrade/activation-height countdown.
2. **Height & Sync Lag** — `finalized_height`, tip hash, state root prefix, `committee_epoch`, and height lag vs observers.
3. **Peers & Vote Signing** — connected peers, quorum size, last-100-height vote rate, latest height-day bps, and 30-day mean bps.
4. **Signer Guard Health** — `signer_mode` (`socket`), `signer_double_sign_protection`, `signer_key_matches_registry`, `separate_uid_enforced`.
5. **Disk & RPC Latency** — `data_dir_bytes`, `fs_free_bytes`, `upgrade_headroom_ok` (`>= 2×`), `rpc_read_p95_ms`, RSS, and retention mode.
6. **Task Node Reward Eligibility** — locally verified 2-of-3 observer quorum, `access_state` (`pending`/`active`/`lapsed`/`revoked`), observed height-days (`X/30`), grace countdown & 3-day recovery streak, `finance_hub_access`, and `reward_eligible`.
7. **Active Warnings** — `FEED_STALE`, `FEED_UNAVAILABLE`, `LOW_DISK_FOR_UPGRADE`, `ACTIVATION_IMMINENT`, `PARTICIPATION_BELOW_95`, `SIGNER_SAME_USER`, `HEIGHT_LAG_HIGH`.

---

## 8. Connect to Task Node (`postfiat-node tasknode-bind`)

To unlock Finance Hub, GoodAlexander Research API keys, and the `$20/mo` Task Node USD credit:

1. Open **Task Node → Research → Validator Settings** (`postfiatl1v2` tab) and copy your single-use binding challenge containing `(account_id, chain_id, node_id, nonce, expiry)`.
2. Sign the challenge offline or on your validator host using the bundled `tasknode-bind` command (uses the signer allow-list under FIPS 204 context `postfiat-l1-v2/tasknode-validator-binding/v1` and emits the optional Pillar 6 Hive identity validator-link co-signature under `postfiat-l1-v2/identity-link/v1`):

```bash
postfiat-node tasknode-bind \
  --challenge-file /tmp/tasknode-challenge.json \
  --signer-socket /run/postfiat-signer/signer.sock \
  --out /tmp/tasknode-binding-response.json
```

3. Submit `/tmp/tasknode-binding-response.json` in Task Node. **Per-operator deduplication:** rewards are capped at **one grant per operator** across old and new chains (bound to your Pillar 6 on-chain identity once live — running multiple nodes does not multiply the `$20/mo` credit).

---

## 9. Active-Liveness Rules, 3-Observer Feed & 14-Day Grace

Connecting once does not unlock Finance Hub forever. Active liveness is measured by **3 independent, geographically distributed read-only observers** publishing the ML-DSA-65 signed `postfiat-validator-uptime-v1` feed (`postfiat-l1-v2/validator-uptime-feed/v1`). Task Node and `postfiat-node top` require **2-of-3 verified observer agreement**.

### Latency-Fair Participation Metric

Rather than counting only `precommit_qc.votes` (which penalizes geographically distant validators when fast peers reach quorum first), observers credit **any valid ML-DSA-65 signed consensus message submitted within each block-height round window**:

- `prepare_vote`
- `precommit_vote` (whether or not included in the finalized `precommit_qc.votes`)
- `timeout_vote`
- `consensus_heartbeat`

Scoring runs over deterministic **block-height windows (height-days)** with zero wall-clock drift using exact integer basis points (`9500` bps = `95.00%`). Steady-state requirement: **`>= 95%` mean daily participation across at least `25` of the trailing `30` completed height-days** while remaining active in the on-chain validator registry.

### Access Lifecycle State Machine

| State | Registry Active | Finance Hub | Research API Keys | `$20/mo` Credit | Notes |
| --- | --- | --- | --- | --- | --- |
| `pending` | No | Locked | Locked | Paused | Applicant not yet ratified into on-chain registry |
| `active` | Yes | **Unlocked** | **Active** | **Eligible** | Immediate **Day-0 ramp-in** on ratification (exempt from 25-day history check for first 30 height-days while `>= 95%`) |
| `lapsed` (**14d grace**) | Yes or No | **Unlocked (grace)** | **Active (grace)** | Paused | Operator warning triggered; **fast recovery back to `active` after `3` consecutive height-days `>= 95%`** |
| `revoked` | Yes or No | **Disabled** | **Invalidated** | Paused | Triggered when 14-day grace expires; eligible for explicit validator-ratified removal proposal if still in registry |

### Stale-Feed Safety Invariant

If the observer feed is stale (`> 3600` seconds old) or fewer than 2 pinned observers agree:

- New validator bindings and new `$20/mo` credit grants are paused;
- **Existing Finance Hub access and active Research API keys are NEVER revoked.** An observer outage can never punish healthy validators.

---

## 10. Troubleshooting

- **`upgrade` exits `3` (`guard_path_overlap`):** Move `/var/lib/postfiat/signer-guard` outside `--data-dir` and `--backup-dir`. Never nest signer guard files inside chain data.
- **`upgrade` exits `4` (`insufficient_disk_space`):** Free disk space or prune old backups in `/var/lib/postfiat/backups/` until free space exceeds `2 × data_dir + binary + 512 MiB`.
- **`rpc-serve` fails with `rpc_replica_signer_forbidden`:** Remove all `--finality-key-file` / `--finality-signer-socket` flags from read-replica systemd units. Replicas are strictly non-voting.
- **`top` displays `FEED_STALE` or `FEED_UNAVAILABLE`:** Verify outbound HTTPS to the observer feed URL and `/etc/postfiat/observer-keyset.json`. Local node metrics continue operating unaffected.
- **Lapsed into 14-day grace after a multi-day outage:** Bring the node back online cleanly; sustaining **`>= 95%` for 3 consecutive completed height-days** immediately restores `active` status (reseting the trailing evaluation floor so a 6-day outage does not trap you for 25 days).
