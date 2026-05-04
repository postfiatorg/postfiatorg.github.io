import { readFileSync } from 'node:fs';

const snapshotPath = new URL('../static/tasknode/community-profiles.json', import.meta.url);
const homepagePath = new URL('../layouts/index.html', import.meta.url);

const allowedTickerSymbols = new Set([
  'AMZN',
  'BTC',
  'BX',
  'CF',
  'COIN',
  'ETH',
  'GOOGL',
  'HOOD',
  'MOS',
  'MSFT',
  'NVDA',
  'SOL',
  'TIA',
  'XYZ'
]);

const blockedTickerSymbols = new Set([
  'ANTHROPIC',
  'FIGMA',
  'FLY',
  'LINEAR',
  'NOTION',
  'OPENAI',
  'PFT',
  'RAILWAY',
  'RENDER',
  'RETOOL',
  'SQ',
  'SUPABASE',
  'VERCEL'
]);

const blockedSkillLabels = [
  'Agent Integration',
  'Ai Workflow',
  'Api And Integrations',
  'Api Design',
  'Applied Ai Systems',
  'Applied AI Systems',
  'Distribution Systems',
  'Frontend Product Delivery',
  'Monetization Systems',
  'Network Collaboration Systems',
  'Onboarding Systems',
  'Quality Assurance Systems',
  'Research Intelligence Synthesis',
  'Revenue Systems',
  'Signal Pipeline',
  'Workflow Automation Systems'
].map(normalizeLabel);

const failures = [];
const snapshot = JSON.parse(readFileSync(snapshotPath, 'utf8'));
const homepage = readFileSync(homepagePath, 'utf8');

if (homepage.includes('Expert Knowledge')) {
  failures.push('homepage still uses the legacy "Expert Knowledge" label');
}

if (!Array.isArray(snapshot.cards) || snapshot.cards.length === 0) {
  failures.push('community profile snapshot has no cards');
}

for (const [cardIndex, card] of (snapshot.cards || []).entries()) {
  const cardRef = `${card.public_slug || `card:${cardIndex}`}`;
  const tickers = Array.isArray(card.associated_tickers) ? card.associated_tickers : [];
  const skills = Array.isArray(card.expert_knowledge) ? card.expert_knowledge : [];

  for (const ticker of tickers) {
    const symbol = String(ticker?.symbol || '').trim().toUpperCase();
    if (!symbol) {
      failures.push(`${cardRef} has an empty associated ticker symbol`);
      continue;
    }
    if (blockedTickerSymbols.has(symbol)) {
      failures.push(`${cardRef} uses blocked associated ticker ${symbol}`);
    }
    if (!allowedTickerSymbols.has(symbol)) {
      failures.push(`${cardRef} uses ticker ${symbol}, which is not in the public snapshot allowlist`);
    }
    if (symbol === 'XYZ' && !/block/i.test(String(ticker?.name || ''))) {
      failures.push(`${cardRef} uses XYZ without naming Block, Inc.`);
    }
  }

  for (const skill of skills) {
    const domain = String(skill?.domain || '').trim();
    const normalized = normalizeLabel(domain);
    if (!domain) {
      failures.push(`${cardRef} has an empty demonstrated skill label`);
      continue;
    }
    if (blockedSkillLabels.includes(normalized)) {
      failures.push(`${cardRef} uses blocked demonstrated skill label "${domain}"`);
    }
    if (domain.split(/\s+/).length < 2) {
      failures.push(`${cardRef} uses underspecified one-word demonstrated skill label "${domain}"`);
    }
  }
}

if (failures.length > 0) {
  console.error('Public profile snapshot validation failed:');
  for (const failure of failures) {
    console.error(`- ${failure}`);
  }
  process.exit(1);
}

console.log(`Validated ${snapshot.cards.length} public Task Node profile cards.`);

function normalizeLabel(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, ' ')
    .trim();
}
