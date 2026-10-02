// Refreshes the homepage's live Task Node sections from public Task Node APIs:
// data/task_feed_snapshot.json ("The Hive Mind in Action") from the Hive, and
// static/tasknode/community-profiles.json (community cards) from the directory.
// CI runs it before every build; whatever fails keeps its committed snapshot.
import { writeFileSync } from 'node:fs';

const origin = 'https://tasknode.postfiat.org';
const explorer = 'https://explorer.testnet.postfiat.org/transactions/';
const maxFeedItems = 12;
const maxCards = 40;
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const utc = (iso) => `${new Date(iso).toLocaleString('en-US', { timeZone: 'UTC', month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit', hourCycle: 'h23' })} UTC`;
const writeJson = (path, value) => writeFileSync(new URL(`../${path}`, import.meta.url), `${JSON.stringify(value, null, 1)}\n`);

async function taskNodeDocument(path) {
  const response = await fetch(`${origin}${path}`, { signal: AbortSignal.timeout(30_000) });
  if (!response.ok) throw new Error(`Task Node ${path} returned HTTP ${response.status}`);
  return (await response.json()).document || {};
}

// Hive feed: the latest contributor actions across active Hive boards. The value
// accountability board is an internal compliance check, not network work.
const hiveProjects = Object.values((await taskNodeDocument('/api/hive/projects')).projects || {})
  .filter((project) => project.id !== 'board_value_accountability');
const taskPft = new Map(hiveProjects.flatMap((project) => project.tasks || []).map((task) => [task.taskId, Number(task.pft) || 0]));
const actions = {
  rewarded: (pft) => (pft ? `Rewarded ${pft.toLocaleString('en-US')} PFT.` : 'Rewarded.'),
  verification_response_submitted: () => 'Submitted evidence for verification.',
  verification_requested: () => 'The verifier asked for more evidence.',
  accepted: () => 'Accepted the task.',
};
const items = hiveProjects.flatMap((project) => project.activity || [])
  .filter((event) => actions[event.action] && event.task && event.updatedAt)
  .sort((a, b) => b.updatedAt.localeCompare(a.updatedAt))
  .filter((event, _, all) => all.filter((other) => other.accountId === event.accountId && other.updatedAt >= event.updatedAt).length <= 2) // mix contributors
  .slice(0, maxFeedItems)
  .map((event) => ({
    category: event.project,
    timestamp: event.updatedAt,
    display_time: utc(event.updatedAt),
    title: event.task,
    summary: actions[event.action](taskPft.get(event.taskId)),
    actor: event.hasPublicProfile ? (event.hiveHandle ? `@${event.hiveHandle}` : event.displayName) : 'Task Node member',
    links: event.proofTxHash ? [{ label: 'PFTL proof', url: `${explorer}${encodeURIComponent(event.proofTxHash)}` }] : [],
  }));
if (items.length < 3) throw new Error(`Task Node Hive returned only ${items.length} feed items`);
const now = new Date().toISOString();
writeJson('data/task_feed_snapshot.json', { generated_at: now, generated_at_display: utc(now), source: `${origin}/api/hive/projects`, items });
console.log(`Synced ${items.length} Hive feed items.`);

// Community cards: public, discoverable members with a profile NFT, in directory rank order.
const members = ((await taskNodeDocument('/api/directory/leaderboard')).operators || []).filter((member) => member.heroNft?.imageCid).slice(0, maxCards);
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
writeJson('static/tasknode/community-profiles.json', snapshot);
console.log(`Synced ${cards.length} Task Node community cards.`);
