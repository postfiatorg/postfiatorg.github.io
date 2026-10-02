// Refreshes static/tasknode/community-profiles.json from the public Task Node
// directory: public, discoverable members with a profile NFT, in directory rank
// order. CI runs it before every build; if it fails, the committed snapshot stays.
import { writeFileSync } from 'node:fs';

const origin = 'https://tasknode.postfiat.org';
const maxCards = 40;
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const response = await fetch(`${origin}/api/directory/leaderboard`, { signal: AbortSignal.timeout(30_000) });
if (!response.ok) throw new Error(`Task Node directory returned HTTP ${response.status}`);
const members = ((await response.json()).document?.operators || []).filter((member) => member.heroNft?.imageCid).slice(0, maxCards);
if (members.length < 4) throw new Error(`Task Node directory returned only ${members.length} members with NFTs`);

// 512px thumbnails are generated on first request (HTTP 202 while warming).
// Wait until each is served; fall back to the full image so no card is broken.
async function nftImageUrl(cid) {
  const thumbnail = `${origin}/api/profile/nft/pfp/${encodeURIComponent(cid)}?size=512`;
  for (let attempt = 0; attempt < 8; attempt += 1) {
    const result = await fetch(thumbnail, { signal: AbortSignal.timeout(30_000) }).catch(() => null);
    await result?.arrayBuffer().catch(() => null);
    if (result?.status === 200) return thumbnail;
    await sleep(5_000);
  }
  return `${origin}/api/profile/nft/image/${encodeURIComponent(cid)}`;
}

const cards = await Promise.all(members.map(async (member) => {
  const art = member.heroNft.metadataJson?.art || {};
  const wallet = String(member.wallet || '');
  return {
    public_slug: wallet ? `${wallet.slice(0, 6)}…${wallet.slice(-4)}` : 'Task Node member',
    display_name: member.handle ? `@${member.handle}` : member.displayName || 'Task Node member',
    profile_url: `${origin}/#/profile?account=${encodeURIComponent(member.accountId)}`,
    nft_image_url: await nftImageUrl(member.heroNft.imageCid),
    creature: art.creature ? `${art.creature} · Hyperstition ${art.hyperstition ?? 0}` : '',
    network_tasks: Number(member.networkTasks) || 0,
    pft_earned: Math.round(Number(member.rewards) || 0).toLocaleString('en-US'),
    alignment: Number.isFinite(member.alignment) ? member.alignment : '—',
  };
}));

const snapshot = { generated_at: new Date().toISOString(), source: `${origin}/api/directory/leaderboard`, cards };
writeFileSync(new URL('../static/tasknode/community-profiles.json', import.meta.url), `${JSON.stringify(snapshot, null, 1)}\n`);
console.log(`Synced ${cards.length} Task Node community cards.`);
