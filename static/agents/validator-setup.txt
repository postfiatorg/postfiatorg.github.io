# Post Fiat Fresh Validator Setup Guide for Agents

> Purpose: end-to-end, agent-readable instructions for installing a fresh Post Fiat `postfiatd` validator on testnet, generating a validator identity, binding it to a domain, publishing domain proof, and verifying that the node is proposing.

## Codex Operator Quick Start

If you want Codex to follow this guide on a server, start Codex from a terminal on the target host. Do not paste `validator-keys.json`, validator tokens, or private key material into Codex chat.

For a full sudo-capable install, authenticate sudo first so Codex can run privileged setup commands when needed:

```bash
sudo -v
codex
```

Then type this into Codex, replacing the placeholders:

```text
Use https://postfiat.org/validator-setup/ to install a fresh Post Fiat testnet validator on this server.

Install mode: sudo.
VALIDATOR_DOMAIN=<bare-domain>
SSH_PORT=22
NETWORK=testnet
POSTFIATD_DIR=/opt/postfiatd

Preserve existing validator keys if any exist. Do not paste private keys or validator tokens into chat. Keep key and token material on disk only. Bind admin/API ports to 127.0.0.1, keep peer port 2559 public, and do not reset firewall rules unless this is confirmed to be a fresh server. If I use GitHub Pages for the validator domain, publish .well-known/pft-ledger.toml and include .well-known in Jekyll config. Verify server_info, validator_info, consensus_info, and the public domain proof before finishing.
```

For a non-sudo Docker-only fallback, use this prompt instead:

```text
Use https://postfiat.org/validator-setup/ to set up a Post Fiat testnet validator if possible.

Install mode: non-sudo.
VALIDATOR_DOMAIN=<bare-domain>
SSH_PORT=22
NETWORK=testnet
POSTFIATD_DIR=$HOME/postfiatd

Do not install packages, change firewall rules, use /opt, or run sudo. Proceed only if Docker is already available to my user. Bind admin/API ports to 127.0.0.1, keep peer port 2559 public, keep key and token material on disk only, and tell me exactly which sudo-only steps remain, especially firewall and Docker service setup. If I use GitHub Pages for the validator domain, publish .well-known/pft-ledger.toml and include .well-known in Jekyll config. Verify server_info, validator_info, consensus_info, and the public domain proof before finishing.
```

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
- Where the operator will publish `https://<VALIDATOR_DOMAIN>/.well-known/pft-ledger.toml`. GitHub Pages works, including `<owner>.github.io`, but Jekyll sites need an explicit `.well-known` include.
- Whether this is truly a fresh validator. If the selected `POSTFIATD_DIR`, `/opt/postfiatd`, `$HOME/postfiatd`, Docker volumes, or an existing `validator-keys.json` exists, do not delete it without explicit operator approval.

Never ask the user to paste private validator keys or validator tokens into a chat transcript. Keep `validator-keys.json` and `[validator_token]` material on the target machine or in the operator's secure storage only.

## Install Mode: Sudo vs Non-Sudo

Use sudo mode for production validators when possible. It can install Docker, enable the Docker service, configure firewall rules, and use the standard `/opt/postfiatd` directory:

```bash
export INSTALL_MODE=sudo
export POSTFIATD_DIR=/opt/postfiatd
```

Use non-sudo mode only as a Docker-only fallback on a host where Docker already works for the current user. Non-sudo mode cannot install packages, enable Docker, write to `/opt`, or configure firewall rules:

```bash
export INSTALL_MODE=non-sudo
export POSTFIATD_DIR="$HOME/postfiatd"
```

Set the install mode and node directory before running the commands below. If `POSTFIATD_DIR` is not set, choose the default path from `INSTALL_MODE`:

```bash
if [ "${INSTALL_MODE:-sudo}" = "non-sudo" ]; then
  export POSTFIATD_DIR="${POSTFIATD_DIR:-$HOME/postfiatd}"
else
  export POSTFIATD_DIR="${POSTFIATD_DIR:-/opt/postfiatd}"
fi
```

## Fresh Server Prerequisites

Assume Ubuntu Server 22.04 LTS or newer.

Minimum hardware:

- 2 CPU cores
- 4 GB RAM
- 100 GB storage

The server must accept inbound peer traffic on TCP `2559`. Admin/API ports such as `5005`, `6006`, and `50051` must not be open to the public internet.

## 1. Install Docker and Basic Tools

Run as a sudo-capable user in sudo mode:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-v2 curl wget jq python3
sudo systemctl enable --now docker
docker compose version
```

If `docker compose version` fails because the Ubuntu package name differs, install Docker's Compose plugin for the target distribution, then rerun the version check.

In non-sudo mode, do not run package or service commands. Instead, verify Docker already works:

```bash
docker info >/dev/null
docker compose version
```

If either command fails in non-sudo mode, stop and ask the operator to install/enable Docker or grant Docker access.

## 2. Configure Firewall

Set UFW to allow SSH and the Post Fiat peer protocol only:

Only run the reset sequence on a fresh server or after confirming the host has no unrelated firewall rules. On a shared or already-running host, preserve existing service rules and add the Post Fiat peer rule instead of resetting UFW.

```bash
export SSH_PORT="${SSH_PORT:-22}"
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow "${SSH_PORT}/tcp" comment 'SSH'
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

In non-sudo mode, do not change firewall rules. Record this as an operator action:

```text
Required operator action: preserve SSH on the configured SSH_PORT, allow inbound TCP 2559, and keep 5005, 6005, 6006, and 50051 private.
```

## 3. Create the Node Directory

Sudo mode:

```bash
export POSTFIATD_DIR="${POSTFIATD_DIR:-/opt/postfiatd}"
sudo mkdir -p "$POSTFIATD_DIR/logs"
sudo chown -R "$USER":"$USER" "$POSTFIATD_DIR"
cd "$POSTFIATD_DIR"
```

Non-sudo mode:

```bash
export POSTFIATD_DIR="${POSTFIATD_DIR:-$HOME/postfiatd}"
mkdir -p "$POSTFIATD_DIR/logs"
cd "$POSTFIATD_DIR"
```

Download the compose file in either mode:

```bash
wget https://raw.githubusercontent.com/postfiatorg/postfiatd/main/scripts/docker-compose-external-validator.yml -O docker-compose.yml
```

Bind admin/API ports to loopback as defense in depth. The peer protocol on TCP `2559` must remain publicly reachable, but RPC/admin ports should not be published on all interfaces even if the firewall is correct:

```bash
python3 - <<'PY'
from pathlib import Path

path = Path("docker-compose.yml")
text = path.read_text()
for old, new in {
    '      - "5005:5005"': '      - "127.0.0.1:5005:5005"',
    '      - "6005:6005"': '      - "127.0.0.1:6005:6005"',
    '      - "6006:6006"': '      - "127.0.0.1:6006:6006"',
    '      - "50051:50051"': '      - "127.0.0.1:50051:50051"',
}.items():
    text = text.replace(old, new)
path.write_text(text)
PY

docker compose config --format json | python3 -c '
import json, sys

ports = json.load(sys.stdin)["services"]["postfiatd"].get("ports", [])
by_target = {int(port["target"]): port for port in ports}

for port in (5005, 6005, 6006, 50051):
    host_ip = by_target.get(port, {}).get("host_ip")
    print(f"{port} host_ip:", host_ip)
    if host_ip != "127.0.0.1":
        raise SystemExit(f"{port} is not bound to 127.0.0.1")

peer = by_target.get(2559, {})
print("2559 host_ip:", peer.get("host_ip", "0.0.0.0"))
if peer.get("host_ip") == "127.0.0.1":
    raise SystemExit("peer port 2559 must not be loopback-only")
'
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
cd "$POSTFIATD_DIR"
docker compose pull
docker compose up -d
docker compose ps
```

Wait for the container named `postfiatd` to show as running.

## 5. Generate Fresh Validator Keys

Only do this for a fresh validator identity.

```bash
cd "$POSTFIATD_DIR"
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

Run `set_domain` using the fresh master key file. Copy the host backup into the container first so this works even if the container has been recreated or `/root/.ripple` has already been cleaned:

```bash
docker exec postfiatd mkdir -p /root/.ripple
docker cp ./validator-keys.json postfiatd:/root/.ripple/validator-keys.json
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
cd "$POSTFIATD_DIR"
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

- `$POSTFIATD_DIR/validator-keys.json`
- `$POSTFIATD_DIR/validator-keys.domain.json`
- `$POSTFIATD_DIR/validator-token.block`
- `$POSTFIATD_DIR/set-domain-output.txt`

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

### GitHub Pages publishing path

For a GitHub Pages site served from a repository such as `<owner>.github.io`, publish the proof from the repository root:

```bash
cd /path/to/<owner>.github.io
mkdir -p .well-known
cp "$POSTFIATD_DIR/pft-ledger.toml" .well-known/pft-ledger.toml
```

If the site is built by Jekyll, ensure dot directories are included:

```yaml
# _config.yml
include:
  - .well-known
```

Commit, push, and wait for the Pages build/deploy to finish:

```bash
git add _config.yml .well-known/pft-ledger.toml
git commit -m "Publish Post Fiat validator proof"
git push
```

Verify public access:

```bash
curl -fsS "https://${VALIDATOR_DOMAIN}/.well-known/pft-ledger.toml"
```

Verify the public proof matches the generated values:

```bash
curl -fsS "https://${VALIDATOR_DOMAIN}/.well-known/pft-ledger.toml" -o ./pft-ledger.public.toml
grep -F "public_key = \"$PUBLIC_KEY\"" ./pft-ledger.public.toml
grep -F "attestation = \"$ATTESTATION\"" ./pft-ledger.public.toml
```

## 9. Verify Node Health

Check software version, server state, and the active validator public key:

```bash
docker exec postfiatd curl -s http://localhost:5005/ -X POST \
  -H "Content-Type: application/json" \
  -d '{"method": "server_info", "params": [{}]}' \
  | PUBLIC_KEY="$PUBLIC_KEY" python3 -c '
import json, os, sys

expected_public_key = os.environ["PUBLIC_KEY"]
info = json.load(sys.stdin)["result"]["info"]

print("build_version:", info.get("build_version"))
print("server_state:", info.get("server_state"))
print("pubkey_validator:", info.get("pubkey_validator"))
print("peers:", info.get("peers"))
print("complete_ledgers:", info.get("complete_ledgers"))

if info.get("server_state") != "proposing":
    raise SystemExit("validator is not proposing yet")
if info.get("pubkey_validator") != expected_public_key:
    raise SystemExit("pubkey_validator does not match generated public key")
'
```

Expected for a healthy validator after sync:

```text
build_version: 1.0.4
server_state: proposing
pubkey_validator: <PUBLIC_KEY>
```

`server_state` may temporarily be `disconnected`, `connected`, `syncing`, or `full` while the node starts and catches up. If `server_state` is `full` but not `proposing`, inspect `validator_info`, `consensus_info`, and token configuration before declaring the node healthy.

Check validator domain and manifest sequence:

```bash
docker exec postfiatd curl -s http://localhost:5005/ -X POST \
  -H "Content-Type: application/json" \
  -d '{"method": "validator_info"}' \
  | VALIDATOR_DOMAIN="$VALIDATOR_DOMAIN" PUBLIC_KEY="$PUBLIC_KEY" python3 -c '
import json, os, sys

expected_domain = os.environ["VALIDATOR_DOMAIN"]
expected_public_key = os.environ["PUBLIC_KEY"]
d = json.load(sys.stdin)["result"]

print("domain:", d.get("domain", ""))
print("seq:", d.get("seq", ""))
print("master_key:", d.get("master_key", ""))

if d.get("domain") != expected_domain:
    raise SystemExit("validator_info domain mismatch")
if d.get("master_key") != expected_public_key:
    raise SystemExit("validator_info master_key mismatch")
if int(d.get("seq", 0)) < 1:
    raise SystemExit("validator manifest sequence is missing")
'
```

Expected:

```text
domain: <VALIDATOR_DOMAIN>
seq: 1 or higher
master_key: <PUBLIC_KEY>
```

For a fresh validator, `seq` is commonly `1`; later domain changes, signing key rotations, or manifest updates can increase it.

Check consensus participation:

```bash
docker exec postfiatd curl -s http://localhost:5005/ -X POST \
  -H "Content-Type: application/json" \
  -d '{"method": "consensus_info"}' \
  | python3 -c '
import json, sys

info = json.load(sys.stdin)["result"]["info"]
for key in ("validating", "proposing", "synched"):
    print(f"{key}:", info.get(key))
    if info.get(key) is not True:
        raise SystemExit(f"consensus_info {key} is not true")
'
```

Expected healthy values include:

```text
validating: True
proposing: True
synched: True
```

## 10. Upgrade Procedure After Fresh Install

For unpinned `latest` setups:

```bash
cd "$POSTFIATD_DIR"
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

- Never delete the selected `POSTFIATD_DIR`, `/opt/postfiatd`, `$HOME/postfiatd`, Docker volumes, or existing validator keys unless the operator explicitly asks for a destructive reset.
- Never paste `validator-keys.json` or `[validator_token]` into chat.
- Never expose RPC/admin ports publicly.
- Always publish the public key and attestation at `https://<domain>/.well-known/pft-ledger.toml`.
- Always verify `server_state`, `build_version`, `validator_info.domain`, and consensus participation.
- For Dynamic UNL readiness, prefer official Post Fiat `v1.0.0+` builds and keep the node upgraded.
