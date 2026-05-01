(function(){
  const root = document.getElementById('pftValidatorCopyTool');
  if (!root) return;

  const domainInput = document.getElementById('pftValidatorDomain');
  const sshInput = document.getElementById('pftValidatorSshPort');
  const scriptBox = document.getElementById('pftValidatorScript');
  const status = document.getElementById('pftValidatorCopyStatus');

  function normalizeDomain(value) {
    return (value || 'example.com')
      .trim()
      .replace(/^https?:\/\//, '')
      .replace(/\/.*$/, '') || 'example.com';
  }

  function normalizePort(value) {
    return (/^\d+$/.test((value || '').trim()) ? value.trim() : '22');
  }

  function healthCheckCommand() {
    return `docker exec postfiatd curl -s http://localhost:5005/ -X POST \\
  -H "Content-Type: application/json" \\
  -d '{"method": "server_info", "params": [{}]}' \\
  | python3 -m json.tool | grep -E '"server_state"|"build_version"'`;
  }

  function buildScript() {
    const domain = normalizeDomain(domainInput.value);
    const sshPort = normalizePort(sshInput.value);
    return `#!/usr/bin/env bash
set -euo pipefail

VALIDATOR_DOMAIN="${domain}"
SSH_PORT="${sshPort}"

sudo apt update
sudo apt install -y docker.io docker-compose-v2 curl wget jq python3
sudo systemctl enable --now docker

sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow "\${SSH_PORT}/tcp" comment 'SSH'
sudo ufw allow 2559/tcp comment 'Post Fiat peer protocol'
sudo ufw --force enable

sudo mkdir -p /opt/postfiatd/logs
sudo chown -R "$USER":"$USER" /opt/postfiatd
cd /opt/postfiatd
wget https://raw.githubusercontent.com/postfiatorg/postfiatd/main/scripts/docker-compose-external-validator.yml -O docker-compose.yml

cat > .env <<EOF
NETWORK=testnet
HOSTNAME=$(hostname)
EOF

sed -i 's#agtipft/postfiatd:\${NETWORK:-devnet}-light-latest#agtipft/postfiatd:testnet-light-1.0.4#' docker-compose.yml

docker compose pull
docker compose up -d
docker compose ps

docker exec postfiatd mkdir -p /root/.ripple
docker exec postfiatd validator-keys create_keys
docker cp postfiatd:/root/.ripple/validator-keys.json ./validator-keys.json
chmod 600 ./validator-keys.json

docker exec postfiatd validator-keys set_domain "$VALIDATOR_DOMAIN" | tee ./set-domain-output.txt
docker cp postfiatd:/root/.ripple/validator-keys.json ./validator-keys.domain.json
chmod 600 ./validator-keys.domain.json

PUBLIC_KEY="$(sed -n 's/^# validator public key: //p' ./set-domain-output.txt | head -n 1)"
ATTESTATION="$(sed -n 's/^attestation="\\([0-9A-Fa-f]*\\)".*/\\1/p' ./set-domain-output.txt | head -n 1)"
sed -n '/^\\[validator_token\\]/,$p' ./set-domain-output.txt | sed '/^$/d' > ./validator-token.block
chmod 600 ./validator-token.block
grep -q '^\\[validator_token\\]$' ./validator-token.block

docker cp postfiatd:/etc/postfiatd/postfiatd.cfg ./postfiatd.cfg
awk '
  /^\\[validator_token\\]$/ {skip=1; next}
  /^\\[[^]]+\\]$/ {skip=0}
  !skip {print}
' ./postfiatd.cfg > ./postfiatd.cfg.new

printf '\\n' >> ./postfiatd.cfg.new
cat ./validator-token.block >> ./postfiatd.cfg.new
printf '\\n' >> ./postfiatd.cfg.new

test "$(grep -c '^\\[validator_token\\]$' ./postfiatd.cfg.new)" -eq 1
docker cp ./postfiatd.cfg.new postfiatd:/etc/postfiatd/postfiatd.cfg
docker compose restart
docker exec postfiatd rm -rf /root/.ripple

cat > ./pft-ledger.toml <<EOF
[[VALIDATORS]]
public_key = "$PUBLIC_KEY"
attestation = "$ATTESTATION"
EOF

echo
echo "Publish this file at https://${domain}/.well-known/pft-ledger.toml:"
cat ./pft-ledger.toml
echo
echo "Then verify with:"
echo 'curl -fsS "https://\${VALIDATOR_DOMAIN}/.well-known/pft-ledger.toml"'
echo
echo "Node health check:"
${healthCheckCommand()}
`;
  }

  function refreshScript() {
    scriptBox.value = buildScript();
  }

  async function copyText(text, label) {
    try {
      await navigator.clipboard.writeText(text);
    } catch (error) {
      const scratch = document.createElement('textarea');
      scratch.value = text;
      scratch.setAttribute('readonly', '');
      scratch.style.position = 'fixed';
      scratch.style.opacity = '0';
      document.body.appendChild(scratch);
      scratch.select();
      document.execCommand('copy');
      document.body.removeChild(scratch);
    }
    status.textContent = `${label} copied`;
    window.setTimeout(() => { status.textContent = ''; }, 2200);
  }

  domainInput.addEventListener('input', refreshScript);
  sshInput.addEventListener('input', refreshScript);
  root.querySelector('[data-copy-validator-script]').addEventListener('click', () => copyText(scriptBox.value, 'Setup script'));
  root.querySelector('[data-copy-validator-verify]').addEventListener('click', () => copyText(healthCheckCommand(), 'Health check'));
  refreshScript();
})();
