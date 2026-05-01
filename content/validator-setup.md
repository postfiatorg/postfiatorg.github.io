---
title: "Post Fiat Validator Setup"
layout: "single"
url: "/validator-setup/"
summary: "End-to-end instructions for installing, configuring, domain-attesting, and verifying a fresh Post Fiat testnet validator."
description: "Agent-readable and human-readable Post Fiat validator setup guide for fresh testnet validators."
keywords:
  - Post Fiat validator setup
  - postfiatd
  - Dynamic UNL
  - validator domain attestation
  - pft-ledger.toml
---

# Post Fiat Fresh Validator Setup Guide for Agents

> Purpose: end-to-end, agent-readable instructions for installing a fresh Post Fiat `postfiatd` validator on testnet, generating a validator identity, binding it to a domain, publishing domain proof, and verifying that the node is proposing.

<div class="validator-copy-tool" id="pftValidatorCopyTool">
  <style>
    .post-content{overflow-wrap:break-word}
    .validator-copy-tool{margin:28px 0 36px;padding:24px;border:1px solid rgba(148,184,255,.28);border-radius:14px;background:linear-gradient(180deg,rgba(148,184,255,.12),rgba(255,255,255,.035));box-shadow:0 18px 48px rgba(0,0,0,.18)}
    .validator-copy-tool h2{margin:0 0 10px;font-size:1.35rem}
    .validator-copy-tool p{margin:0 0 18px;color:var(--secondary);line-height:1.6}
    .validator-copy-grid{display:grid;grid-template-columns:2fr 1fr;gap:14px;margin-bottom:16px}
    .validator-copy-field label{display:block;margin-bottom:6px;font-size:.78rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--secondary)}
    .validator-copy-field input{width:100%;border:1px solid var(--border);border-radius:10px;background:var(--entry);color:var(--primary);padding:12px 13px;font:inherit}
    .validator-copy-actions{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:14px 0}
    .validator-copy-button{border:0;border-radius:10px;background:var(--primary);color:var(--theme);font-weight:800;padding:11px 14px;cursor:pointer}
    .validator-copy-button.secondary{background:transparent;color:var(--primary);border:1px solid var(--border)}
    .validator-copy-button:focus-visible,.validator-copy-field input:focus-visible{outline:2px solid #8db8ff;outline-offset:2px}
    .validator-copy-status{min-height:1.3em;color:var(--secondary);font-size:.88rem}
    .validator-copy-tool textarea{width:100%;min-height:360px;border:1px solid var(--border);border-radius:12px;background:#0b0f18;color:#e9eefc;font:13px/1.55 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;padding:14px;resize:vertical}
    .validator-copy-note{font-size:.9rem;color:var(--secondary)}
    @media(max-width:720px){
      body{overflow-x:hidden}
      .main,.post-single,.post-content{width:100vw !important;max-width:100vw !important;overflow-x:hidden}
      .post-single{padding-inline:14px !important}
      .post-title,.post-description,.post-content h1,.post-content h2,.post-content p,.post-content blockquote,.validator-copy-tool{width:calc(100vw - 96px) !important;max-width:calc(100vw - 96px) !important;white-space:normal;overflow-wrap:anywhere}
      .post-title{font-size:1.65rem;line-height:1.16;overflow-wrap:break-word}
      .post-description{font-size:1rem;line-height:1.45;max-width:100%}
      .post-content h1{font-size:1.25rem;line-height:1.18;overflow-wrap:break-word}
      .post-content h2{font-size:1.25rem;line-height:1.2;overflow-wrap:break-word}
      .post-content p,.post-content blockquote{overflow-wrap:break-word}
      .post-content > h1,.post-content > p,.post-content > blockquote{width:calc(100vw - 150px) !important;max-width:calc(100vw - 150px) !important}
      .post-content blockquote{padding-inline-start:14px}
      .nav{overflow-x:auto;white-space:nowrap}
      .nav a{flex:0 0 auto}
      .validator-copy-tool h2{font-size:1.2rem}
      .validator-copy-grid{grid-template-columns:1fr}
      .validator-copy-tool{padding:18px}
      .validator-copy-actions{align-items:stretch}
      .validator-copy-button{width:100%}
      .validator-copy-tool textarea{min-height:420px;font-size:12px}
    }
  </style>
  <h2>Copy/Paste Fresh Validator Setup</h2>
  <p>This helper builds a fresh-server command script with your domain and SSH port. Review it before running: it installs Docker, resets UFW, starts `postfiatd`, creates validator keys, sets the domain, injects the validator token, and prints the TOML you must publish.</p>
  <div class="validator-copy-grid">
    <div class="validator-copy-field">
      <label for="pftValidatorDomain">Validator domain</label>
      <input id="pftValidatorDomain" type="text" value="example.com" autocomplete="off" spellcheck="false" />
    </div>
    <div class="validator-copy-field">
      <label for="pftValidatorSshPort">SSH port</label>
      <input id="pftValidatorSshPort" type="text" value="22" inputmode="numeric" />
    </div>
  </div>
  <div class="validator-copy-actions">
    <button class="validator-copy-button" type="button" data-copy-validator-script>Copy setup script</button>
    <button class="validator-copy-button secondary" type="button" data-copy-validator-verify>Copy health check</button>
    <span class="validator-copy-status" id="pftValidatorCopyStatus" aria-live="polite"></span>
  </div>
  <textarea id="pftValidatorScript" readonly spellcheck="false" aria-label="Generated Post Fiat validator setup script"></textarea>
  <p class="validator-copy-note">After the script runs, publish `/opt/postfiatd/pft-ledger.toml` at `https://your-domain/.well-known/pft-ledger.toml`, then run the copied health check.</p>
  <script src="/js/validator-copy.js" defer></script>
</div>

## Scope

Use this guide when a user asks an LLM or automation agent to set up a new Post Fiat validator from a fresh server.

Default target:

- Network: `testnet`
- Node role: validator
- Docker image family: `agtipft/postfiatd:testnet-light-latest`
- Current recommended explicit version as of 2026-05-01: `agtipft/postfiatd:testnet-light-1.0.4`

Do not use older XRPL-style `3.0.0` images for Post Fiat Dynamic UNL eligibility. Official Post Fiat validator builds are `v1.0.0` or newer.

## Inputs the Agent Needs

Ask for, infer, or confirm these values before beginning:

- `VALIDATOR_DOMAIN`: bare domain controlled by the operator, for example `validator.example.com` or `example.com`. Do not include `https://`.
- `SSH_PORT`: usually `22`.
- `NETWORK`: normally `testnet`.
- Whether this is truly a fresh validator. If `/opt/postfiatd` or an existing `validator-keys.json` exists, do not delete it without explicit operator approval.

Never ask the user to paste private validator keys or validator tokens into a chat transcript. Keep `validator-keys.json` and `[validator_token]` material on the target machine or in the operator's secure storage only.

## Fresh Server Prerequisites

Assume Ubuntu Server 22.04 LTS or newer.

Minimum hardware:

- 2 CPU cores
- 4 GB RAM
- 100 GB storage

The server must accept inbound peer traffic on TCP `2559`. Admin/API ports such as `5005`, `6006`, and `50051` must not be open to the public internet.

## 1. Install Docker and Basic Tools

Run as a sudo-capable user:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-v2 curl wget jq python3
sudo systemctl enable --now docker
docker compose version
```

If `docker compose version` fails because the Ubuntu package name differs, install Docker's Compose plugin for the target distribution, then rerun the version check.

## 2. Configure Firewall

Set UFW to allow SSH and the Post Fiat peer protocol only:

```bash
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 2559/tcp comment 'Post Fiat peer protocol'
sudo ufw --force enable
sudo ufw status verbose
```

Add Docker `DOCKER-USER` rate limits for peer traffic:

```bash
sudo iptables -F DOCKER-USER 2>/dev/null || true
sudo iptables -I DOCKER-USER -j RETURN
sudo iptables -I DOCKER-USER -p tcp --dport 2559 -m state --state NEW -j DROP
sudo iptables -I DOCKER-USER -p tcp --dport 2559 -m state --state NEW -m limit --limit 100/second --limit-burst 50 -j ACCEPT
sudo iptables -I DOCKER-USER -p tcp --dport 2559 -m connlimit --connlimit-above 50 -j DROP
sudo iptables -I DOCKER-USER -p tcp --dport 2559 -m state --state ESTABLISHED,RELATED -j ACCEPT
sudo iptables -L DOCKER-USER -n -v
```

Expected security posture:

- Public inbound allowed: SSH and TCP `2559`
- Public inbound blocked: `5005`, `6005`, `6006`, `50051`
- Local admin RPC still reachable from the server through `http://localhost:5005/`

## 3. Create the Node Directory

```bash
sudo mkdir -p /opt/postfiatd/logs
sudo chown -R "$USER":"$USER" /opt/postfiatd
cd /opt/postfiatd
wget https://raw.githubusercontent.com/postfiatorg/postfiatd/main/scripts/docker-compose-external-validator.yml -O docker-compose.yml
```

Create `.env`:

```bash
cat > .env <<EOF
NETWORK=testnet
HOSTNAME=$(hostname)
EOF
```

Optional explicit pin to the current recommended testnet build:

```bash
sed -i 's#agtipft/postfiatd:${NETWORK:-devnet}-light-latest#agtipft/postfiatd:testnet-light-1.0.4#' docker-compose.yml
```

If you do not pin, the compose file uses `agtipft/postfiatd:${NETWORK:-devnet}-light-latest`, which becomes `agtipft/postfiatd:testnet-light-latest` when `NETWORK=testnet`.

## 4. Start the Node

```bash
cd /opt/postfiatd
docker compose pull
docker compose up -d
docker compose ps
```

Wait for the container named `postfiatd` to show as running.

## 5. Generate Fresh Validator Keys

Only do this for a fresh validator identity.

```bash
cd /opt/postfiatd
docker exec postfiatd mkdir -p /root/.ripple
docker exec postfiatd validator-keys create_keys
docker cp postfiatd:/root/.ripple/validator-keys.json ./validator-keys.json
chmod 600 ./validator-keys.json
```

Immediately copy `./validator-keys.json` to secure offline storage. This file is the permanent master validator identity. If it is lost, the operator cannot rotate signing keys, update the domain, or revoke the validator identity.

## 6. Set the Validator Domain and Capture Public Proof

Set `VALIDATOR_DOMAIN` to the bare domain:

```bash
export VALIDATOR_DOMAIN="example.com"
```

Run `set_domain` using the fresh master key file inside the container:

```bash
docker exec postfiatd validator-keys set_domain "$VALIDATOR_DOMAIN" | tee ./set-domain-output.txt
docker cp postfiatd:/root/.ripple/validator-keys.json ./validator-keys.domain.json
chmod 600 ./validator-keys.domain.json
```

The output contains three important values:

- `public_key`: shown after `# validator public key:`
- `attestation`: shown as `attestation="..."`
- `[validator_token]`: multi-line base64 block that must be inserted into `postfiatd.cfg`

Extract public proof values:

```bash
PUBLIC_KEY="$(sed -n 's/^# validator public key: //p' ./set-domain-output.txt | head -n 1)"
ATTESTATION="$(sed -n 's/^attestation="\([0-9A-Fa-f]*\)".*/\1/p' ./set-domain-output.txt | head -n 1)"
printf 'PUBLIC_KEY=%s\nATTESTATION=%s\n' "$PUBLIC_KEY" "$ATTESTATION"
```

Extract the token block into a local file. Treat this file as secret:

```bash
sed -n '/^\[validator_token\]/,$p' ./set-domain-output.txt | sed '/^$/d' > ./validator-token.block
chmod 600 ./validator-token.block
grep -q '^\[validator_token\]$' ./validator-token.block
```

Do not inline the token through a shell variable. Multi-line validator tokens are easy to corrupt.

## 7. Inject the Validator Token into `postfiatd.cfg`

Use a file-based replace so there is exactly one `[validator_token]` section:

```bash
cd /opt/postfiatd
docker cp postfiatd:/etc/postfiatd/postfiatd.cfg ./postfiatd.cfg

awk '
  /^\[validator_token\]$/ {skip=1; next}
  /^\[[^]]+\]$/ {skip=0}
  !skip {print}
' ./postfiatd.cfg > ./postfiatd.cfg.new

printf '\n' >> ./postfiatd.cfg.new
cat ./validator-token.block >> ./postfiatd.cfg.new
printf '\n' >> ./postfiatd.cfg.new

test "$(grep -c '^\[validator_token\]$' ./postfiatd.cfg.new)" -eq 1
docker cp ./postfiatd.cfg.new postfiatd:/etc/postfiatd/postfiatd.cfg
docker compose restart
```

After restart, remove master key material from the container:

```bash
docker exec postfiatd rm -rf /root/.ripple
```

Keep these files secure and private:

- `/opt/postfiatd/validator-keys.json`
- `/opt/postfiatd/validator-keys.domain.json`
- `/opt/postfiatd/validator-token.block`
- `/opt/postfiatd/set-domain-output.txt`

Prefer moving private key/token files off the validator host after configuration.

## 8. Publish Domain Attestation

On the domain's website, publish:

`https://<VALIDATOR_DOMAIN>/.well-known/pft-ledger.toml`

Contents:

```toml
[[VALIDATORS]]
public_key = "<PUBLIC_KEY_FROM_SET_DOMAIN>"
attestation = "<ATTESTATION_FROM_SET_DOMAIN>"
```

Example generation on the validator host:

```bash
cat > ./pft-ledger.toml <<EOF
[[VALIDATORS]]
public_key = "$PUBLIC_KEY"
attestation = "$ATTESTATION"
EOF
cat ./pft-ledger.toml
```

Publish that TOML file through the operator's domain hosting provider. If using a static site, place it so the final URL is exactly `/.well-known/pft-ledger.toml`.

Verify public access:

```bash
curl -fsS "https://${VALIDATOR_DOMAIN}/.well-known/pft-ledger.toml"
```

## 9. Verify Node Health

Check software version and server state:

```bash
docker exec postfiatd curl -s http://localhost:5005/ -X POST \
  -H "Content-Type: application/json" \
  -d '{"method": "server_info", "params": [{}]}' \
  | python3 -m json.tool | grep -E '"server_state"|"build_version"'
```

Expected for a healthy validator after sync:

```text
"server_state": "proposing"
"build_version": "1.0.4"
```

`server_state` may temporarily be `connected`, `syncing`, or `full` while the node catches up. Wait 30-90 seconds and retry before declaring failure.

Check validator domain and manifest sequence:

```bash
docker exec postfiatd curl -s http://localhost:5005/ -X POST \
  -H "Content-Type: application/json" \
  -d '{"method": "validator_info"}' \
  | python3 -c '
import json, sys
d = json.load(sys.stdin)["result"]
print("domain:", d.get("domain", ""))
print("seq:", d.get("seq", ""))
print("master_key:", d.get("master_key", ""))
'
```

Expected:

```text
domain: <VALIDATOR_DOMAIN>
seq: 2
master_key: <PUBLIC_KEY>
```

Check consensus participation:

```bash
docker exec postfiatd curl -s http://localhost:5005/ -X POST \
  -H "Content-Type: application/json" \
  -d '{"method": "consensus_info"}' \
  | python3 -m json.tool | grep -E '"validating"|"proposing"|"synched"'
```

Expected healthy values include:

```text
"validating": true
"proposing": true
"synched": true
```

## 10. Upgrade Procedure After Fresh Install

For unpinned `latest` setups:

```bash
cd /opt/postfiatd
docker compose pull
docker compose up -d
```

For pinned setups, edit `docker-compose.yml` to the recommended tag, then run the same pull/up sequence.

Always verify after an upgrade:

```bash
docker exec postfiatd curl -s http://localhost:5005/ -X POST \
  -H "Content-Type: application/json" \
  -d '{"method": "server_info", "params": [{}]}' \
  | python3 -m json.tool | grep -E '"server_state"|"build_version"'
```

## Troubleshooting

### `domain` is empty in `validator_info`

The validator token in `/etc/postfiatd/postfiatd.cfg` probably does not contain the domain manifest. Re-run `validator-keys set_domain`, replace the token using the file-based method, and restart.

### Token errors in logs

Inspect logs:

```bash
docker compose logs --tail=200 | grep -Ei 'invalid|token|fatal|validator'
```

Most token errors come from corrupted line breaks. Replace the token from a file, not an inline shell variable.

### Node is `full` but not `proposing`

Check that `[validator_token]` exists exactly once:

```bash
docker cp postfiatd:/etc/postfiatd/postfiatd.cfg ./postfiatd.cfg.check
grep -n '^\[validator_token\]$' ./postfiatd.cfg.check
```

Then inspect `validator_info` and `consensus_info`.

### Admin ports are reachable from the internet

Fix the firewall immediately. Only SSH and TCP `2559` should be publicly reachable unless the operator has deliberately placed admin APIs behind a secure private network.

### The operator already has validator keys

Do not run `validator-keys create_keys`. Use the existing secure `validator-keys.json`, copy it into `/root/.ripple/validator-keys.json` only temporarily, then run `validator-keys set_domain` or `validator-keys create_token` as needed.

## Agent Safety Checklist

- Never delete `/opt/postfiatd`, Docker volumes, or existing validator keys unless the operator explicitly asks for a destructive reset.
- Never paste `validator-keys.json` or `[validator_token]` into chat.
- Never expose RPC/admin ports publicly.
- Always publish the public key and attestation at `https://<domain>/.well-known/pft-ledger.toml`.
- Always verify `server_state`, `build_version`, `validator_info.domain`, and consensus participation.
- For Dynamic UNL readiness, prefer official Post Fiat `v1.0.0+` builds and keep the node upgraded.
