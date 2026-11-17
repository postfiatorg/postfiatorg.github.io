/* Post Fiat Explorer. One file, no framework. All state lives in the URL hash. */
(() => {
  const root = document.getElementById('ex');
  if (!root) return;
  const API = (root.dataset.api || '/api/explorer/v1').replace(/\/$/, '');
  const LENS = { bridge: 'Bridge', payments: 'Payments', navmarket: 'NAVCoin market', private: 'Private', navchecks: 'NAV checks', market: 'Swaps and orders', fastlane: 'Fast lane', network: 'Network' };
  const JOURNEY = { deposit: 'USDC deposit', withdrawal: 'USDC withdrawal', create: 'NAVCoin creation', export: 'Bridge to Ethereum', return: 'Return from Ethereum' };
  let meta = null, timer = null, lastTop = null, seq = 0;

  // ── helpers ────────────────────────────────────────────────────────────────
  const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const short = (v, h = 8, t = 4) => { v = String(v ?? ''); return v.length <= h + t + 1 ? v : `${v.slice(0, h)}…${v.slice(-t)}`; };
  const num = (v) => (v == null ? '–' : Number(v).toLocaleString('en-US'));
  const units = (atoms, precision = 6, max = 6) => {
    if (atoms == null || atoms === '') return '–';
    let a = BigInt(Math.trunc(Number(atoms)));
    const neg = a < 0n; if (neg) a = -a;
    const base = 10n ** BigInt(precision);
    let frac = (a % base).toString().padStart(precision, '0').slice(0, max).replace(/0+$/, '');
    if (frac.length < 2) frac = (frac + '00').slice(0, 2);
    return `${neg ? '−' : ''}${(a / base).toLocaleString('en-US')}.${frac}`;
  };
  const usd = (atoms, d = 6, max = 2) => (atoms == null ? '–' : `$${units(atoms, d, max)}`);
  const ago = (t) => { if (!t) return ''; const s = Math.max(0, Date.now() / 1000 - t); if (s < 90) return `${Math.round(s)} seconds ago`; if (s < 5400) return `${Math.round(s / 60)} minutes ago`; if (s < 129600) return `${Math.round(s / 3600)} hours ago`; return `${Math.round(s / 86400)} days ago`; };
  const utc = (t) => (t ? new Date(t * 1000).toISOString().replace('T', ' ').slice(0, 19) + ' UTC' : '');
  const link = (route, text, cls = '') => `<a href="#${route}"${cls ? ` class="${cls}"` : ''}>${text}</a>`;
  const addr = (a, label) => (a ? (label ? `${esc(label)} ` : '') + link(`/account/${a}`, esc(a), 'hash') : '–');
  // Sentences arrive with shortened addresses; put the full ones back, linked.
  const sent = (o, linked) => { let h = esc(o.sentence); for (const a of o.addrs || []) { const tok = esc(`${a.slice(0, 8)}…${a.slice(-4)}`); if (!h.includes(tok)) continue; const full = `<span class="ad">${esc(a)}</span>`; h = h.split(tok).join(linked ? (a.startsWith('pf') ? `<a class="ad" href="#/account/${esc(a)}">${esc(a)}</a>` : `<a class="ad" href="https://etherscan.io/address/${esc(a)}" target="_blank" rel="noopener">${esc(a)}</a>`) : full); } return h; };
  const resultTag = (o) => o.accepted === false ? `<span class="tag rej" title="${esc(o.code || '')}">Rejected</span>` : o.accepted === true ? `<span class="tag ok">${esc(o.code === 'filled' ? 'Filled' : 'Accepted')}</span>` : '<span class="tag prop">No receipt</span>';
  const levelTag = (e) => `<span class="tag ${e === 'disputed' ? 'rej' : 'lvl'}" title="How far the explorer has checked this record">${esc(e === 'cross-checked' ? 'Cross-checked' : e === 'disputed' ? 'Disputed' : 'Reported')}</span>`;
  const copyBtn = (v) => `<button class="copy" data-copy="${esc(v)}">Copy</button>`;
  const hashRow = (v) => `<span class="hash" title="${esc(v)}">${esc(v)}</span>${copyBtn(v)}`;
  const etherscan = (e) => { if (!e || !e.tx) return ''; const h = e.tx.startsWith('0x') ? e.tx : '0x' + e.tx; const base = { 1: 'https://etherscan.io', 11155111: 'https://sepolia.etherscan.io', 42161: 'https://arbiscan.io' }[e.chain_id] || 'https://etherscan.io'; return `<a class="hash" href="${base}/tx/${esc(h)}" rel="noopener" target="_blank">${short(h, 10, 6)} ↗</a>`; };
  const seals = (block, small) => { const voted = new Set((block.header?.votes || []).map((v) => v.validator)); const all = block.header?.validators || [...voted]; return `<span class="seals${small ? ' small' : ''}">${all.map((v) => `<span class="seal${voted.has(v) ? ' on' : ''}${v === block.proposer ? ' prop' : ''}" title="${esc(v)}${voted.has(v) ? ': recorded accepting vote' : ': no vote recorded'}${v === block.proposer ? ' (proposer)' : ''}"><i></i>${small ? '' : esc(v.replace('validator-', 'v'))}</span>`).join('')}</span>`; };
  const dots = (steps) => `<span class="jmini">${steps.map((s) => `<i class="${esc(s.state)}" title="${esc(s.label)}: ${esc(s.state)}"></i>`).join('')}</span>`;
  const spark = (vals) => { vals = (vals || []).map(Number).filter((v) => isFinite(v)); if (vals.length < 2) return '<svg class="spark" viewBox="0 0 120 30"><path d="M2 15H118"/></svg>'; const lo = Math.min(...vals), hi = Math.max(...vals), sp = hi - lo || 1; const pt = (v, i) => [2 + (116 * i) / (vals.length - 1), 26 - (22 * (v - lo)) / sp]; const d = vals.map((v, i) => `${i ? 'L' : 'M'}${pt(v, i).map((n) => n.toFixed(1)).join(' ')}`).join(''); const [lx, ly] = pt(vals[vals.length - 1], vals.length - 1); return `<svg class="spark" viewBox="0 0 120 30" aria-hidden="true"><path d="${d}"/><circle cx="${lx.toFixed(1)}" cy="${ly.toFixed(1)}" r="2.2"/></svg>`; };
  const json = (o) => esc(JSON.stringify(o, null, 2)).replace(/&quot;([a-zA-Z0-9_]+)&quot;:/g, '<span class="k">&quot;$1&quot;</span>:');

  async function get(path) {
    const res = await fetch(API + path, { cache: 'no-store' });
    const body = await res.json().catch(() => ({}));
    if (body.meta) { meta = body.meta; pulse(true); }
    if (res.status === 404) return null;
    if (!res.ok || !body.ok) throw new Error('The explorer service did not answer.');
    return body.data;
  }
  function pulse(ok) {
    const el = document.getElementById('ex-pulse'); if (!el) return;
    if (!ok || !meta) { el.className = 'ex-pulse stale'; el.innerHTML = '<span class="dot"></span>Explorer service unreachable. Showing the last data.'; return; }
    const behind = meta.chain_height - meta.index_height;
    el.className = 'ex-pulse' + (behind > 2 ? ' behind' : '');
    el.innerHTML = `<span class="dot"></span>Index at <b>${num(meta.index_height)}</b> · chain at <b>${num(meta.chain_height)}</b>${behind > 2 ? ` · ${behind} blocks behind` : ''}`;
  }
  const opLine = (o, isNew) => `<li class="${o.lens === 'private' ? 'private' : ''}${isNew ? ' new' : ''}"><a href="#/tx/${esc(o.id)}"><span class="h">${num(o.height)}</span><span class="s">${sent(o)}<small>${esc(LENS[o.lens] || o.lens)}${o.journey ? ' · ' + esc(JOURNEY[o.journey.kind] || '') : ''}</small></span><span>${o.lens === 'private' ? '<span class="tag sealed">Sealed</span>' : resultTag(o)}</span></a></li>`;
  const head = (label, title, sub, extra = '', cls = '') => `<header class="ex-head"><span class="label">${label}</span><h1 class="${cls}">${title}</h1>${sub ? `<p class="sub">${sub}</p>` : ''}${extra}</header>`;
  const section = (title, more = '') => `<div class="ex-h2"><h2>${title}</h2>${more}</div>`;
  const page = (html, flush) => `<div class="wrap ex-page${flush ? ' flush' : ''}">${html}</div>`;

  // ── pages: devnet ──────────────────────────────────────────────────────────
  async function home(q) {
    const d = await get('/summary'); if (!d) return notFound();
    const lens = q.get('lens');
    const stream = lens ? (await get(`/stream?lens=${encodeURIComponent(lens)}`)).ops.slice(0, 14) : d.stream;
    const max = Math.max(...d.lenses.map((l) => l.count), 1);
    const top = d.stream[0]?.id; const fresh = lastTop && top !== lastTop && !lens; lastTop = top;
    const lastSeen = d.tip_seen_at ? `Last block seen ${ago(d.tip_seen_at)}.` : 'Waiting for the next block.';
    return page(`
      <section class="ex-hero">
        <div class="big"><small>Devnet · ${esc(d.network.chain_id)} · block</small><span class="num">${num(d.height)}</span></div>
        <p class="lede">Every block here carries the recorded votes of its validators, signed with post-quantum signatures. ${esc(lastSeen)} Read any operation as a sentence, then check the record behind it.</p>
      </section>
      <div class="stats">
        <div><div class="v num">${num(d.ops)}</div><div class="k">Operations</div></div>
        <div><div class="v num">${num(d.addresses)}</div><div class="k">Addresses</div></div>
        <div><div class="v num">${d.coins.filter((c) => c.listed).length}</div><div class="k">NAVCoins listed</div></div>
        <div><div class="v num">${(d.shielded_share * 100).toFixed(1)}%</div><div class="k">Blocks that are private</div></div>
      </div>
      ${section('What the network is doing', lens ? link('/', 'Show everything') : '')}
      <div class="lenses" role="group" aria-label="Filter by lens">${d.lenses.map((l) => `<button data-lens="${l.lens}" aria-pressed="${lens === l.lens}"><span class="v num">${num(l.count)}</span><span class="k">${esc(LENS[l.lens])}</span><span class="bar"><i style="width:${Math.max(3, (100 * l.count) / max).toFixed(1)}%"></i></span></button>`).join('')}</div>
      <div class="cols">
        <div>${section(lens ? esc(LENS[lens]) : 'Latest operations', link(`/stream${lens ? `?lens=${lens}` : ''}`, 'All →'))}<ul class="stream" id="ex-stream">${stream.map((o, i) => opLine(o, fresh && i === 0)).join('') || '<li class="ex-empty">Nothing yet.</li>'}</ul></div>
        <div>${section('Latest blocks', link('/blocks', 'All →'))}
          <table class="ledger tight"><thead><tr><th>Block</th><th>Proposer</th><th>Kind</th><th class="r">Votes</th></tr></thead><tbody>
          ${d.latest_blocks.map((b) => `<tr><td>${link(`/block/${b.height}`, num(b.height))}</td><td>${esc(b.proposer)}</td><td>${esc(b.kind)}</td><td class="r num">${b.votes} of 6</td></tr>`).join('')}
          </tbody></table>
          ${section('NAVCoins', link('/coins', 'All →'))}
          <table class="ledger tight"><thead><tr><th>Coin</th><th>NAV</th><th class="r">Checks</th></tr></thead><tbody>
          ${d.coins.filter((c) => c.listed).map((c) => `<tr><td>${link(`/coin/${c.asset_id}`, esc(c.code))}${c.retired ? ' <span class="tag prop">Retired</span>' : ''}</td><td class="num">${usd(c.nav_per_unit, c.nav_decimals, 6)}</td><td class="r">${spark(c.spark)}</td></tr>`).join('')}
          </tbody></table>
        </div>
      </div>`);
  }

  async function streamPage(q) {
    const lens = q.get('lens') || '', before = q.get('before') || '', rej = q.get('rejected') || '';
    const d = await get(`/stream?lens=${lens}&before=${before}${rej ? '&rejected=1' : ''}`);
    const chip = (l, t) => `<a class="chip" href="#/stream${l ? `?lens=${l}` : ''}" aria-current="${lens === l && !rej}">${t}</a>`;
    return page(head('Devnet', 'Operations', 'Every operation on the network, newest first.') +
      `<div class="chips">${chip('', 'All')}${Object.entries(LENS).map(([k, v]) => chip(k, esc(v))).join('')}<a class="chip" href="#/stream?rejected=1" aria-current="${!!rej}">Rejected</a></div>
      <ul class="stream">${d.ops.map((o) => opLine(o)).join('') || '<li class="ex-empty">Nothing here.</li>'}</ul>
      <div class="pager">${d.next ? link(`/stream?lens=${lens}${rej ? '&rejected=1' : ''}&before=${d.next}`, 'Older →', 'btn') : ''}</div>`);
  }

  async function blocks(q) {
    const d = await get(`/blocks?before=${q.get('before') || ''}`);
    return page(head('Devnet', 'Blocks', 'One block per agreed batch. A filled mark is a recorded accepting vote; the ringed mark is the proposer.') +
      `<table class="ledger tight"><thead><tr><th>Block</th><th>Proposer</th><th>Kind</th><th>Operations</th><th>Votes</th><th>Seen</th><th>Evidence</th></tr></thead><tbody>
      ${d.blocks.map((b) => `<tr><td>${link(`/block/${b.height}`, num(b.height))}</td><td>${esc(b.proposer)}</td><td>${esc(b.kind)}</td><td class="num">${b.n_ops}</td><td class="num">${b.votes} of 6</td><td>${b.observed_at ? `<span title="${utc(b.observed_at)}">${ago(b.observed_at)}</span>` : '<span class="muted">before indexing</span>'}</td><td>${levelTag(b.evidence)}</td></tr>`).join('')}
      </tbody></table><div class="pager">${d.next ? link(`/blocks?before=${d.next}`, 'Older →', 'btn') : ''}</div>`);
  }

  async function block(h) {
    const d = await get(`/block/${h}`); if (!d) return notFound(`Block ${esc(h)} is not on the network.`);
    const b = d.block;
    return page(head(`Devnet · ${esc(b.kind)} block`, `Block ${num(b.height)}`,
      `${b.n_ops} operation${b.n_ops === 1 ? '' : 's'}, proposed by ${esc(b.proposer)}, with ${b.votes} recorded accepting votes of 6 (quorum ${b.quorum}).`,
      `<div class="ex-meta">${levelTag(b.evidence)}${b.observed_at ? `<span class="label" title="${utc(b.observed_at)}">Seen ${ago(b.observed_at)}</span>` : '<span class="label">Seen before indexing began; order only</span>'}<span class="btns">${d.prev ? link(`/block/${d.prev}`, '← Previous', 'ex-more') : ''} ${d.next ? link(`/block/${d.next}`, 'Next →', 'ex-more') : ''}</span></div>`) +
      section('Validators') + seals(b) + `<p class="ex-note">Votes use ${esc(b.header.votes?.[0]?.algorithm_id || 'ML-DSA-65')} signatures. A filled mark means the block's certificate records that validator's accepting vote. The explorer has read these votes; it has not checked the signatures itself.</p>` +
      section('Operations') + `<ul class="stream">${d.ops.map((o) => opLine(o)).join('') || '<li class="ex-empty">This block carries no operations.</li>'}</ul>` +
      section('Record') + `<div class="kv">
        <div>Block hash</div><div>${hashRow(b.hash)}</div>
        <div>Parent</div><div>${d.prev ? link(`/block/${d.prev}`, esc(b.parent), 'hash') : hashRow(b.parent)}</div>
        <div>State root</div><div>${hashRow(b.state_root)}</div>
        <div>Batch</div><div>${hashRow(b.header.batch_id)}</div>
        <div>Certificate</div><div>${hashRow(b.header.certificate_id)}</div>
        <div>View</div><div>${esc(b.view)}${b.header.committee_epoch != null ? ` · committee epoch ${esc(b.header.committee_epoch)}` : ''}</div>
      </div>` + checkPanel(b.evidence, `{"method":"blocks","params":{"from_height":${b.height},"limit":1}}`, 'returns this block with its full signed certificate'));
  }

  const checkPanel = (evidence, call, what) => `<div class="verify"><span class="label"><b>Check it yourself</b> · evidence level: ${esc(evidence === 'cross-checked' ? 'cross-checked' : evidence || 'reported')}</span>
    <div>${evidence === 'cross-checked' ? 'Two validators report the same block hash and state root, and this block links to the one before it.' : evidence === 'disputed' ? 'Two validators answered differently for this block.' : 'Read from one validator.'} That detects a validator answering differently from another. It does not by itself establish that the certificate is valid. Sent to any validator, this call ${what}:</div><code>${esc(call)}</code></div>`;

  function journeyPanel(j) {
    if (!j) return '';
    return section(esc(JOURNEY[j.kind] || 'Journey'), link(`/journey/${j.kind}/${j.key}`, 'Open journey →')) +
      `<div class="journey">${j.steps.map((s) => `<div class="jstep ${esc(s.state)}"><span class="m"></span><div class="l">${esc(s.label)}</div><div class="n">${
        s.state === 'done' ? `Done · ${link(`/tx/${s.op}`, 'block ' + num(s.height))}` : s.state === 'rejected' ? `Rejected · ${link(`/tx/${s.op}`, esc(s.code || ''))}` : s.state === 'unknown' ? `Not checked${s.eth ? '<br>' + etherscan(s.eth) : ''}` : s.state === 'pending' ? 'Pending' : 'Not started'}</div></div>`).join('')}</div>
      <p class="ex-note">${j.steps.some((s) => s.state === 'unknown') ? 'This build does not read Ethereum. Ethereum steps show "not checked", and any hash shown is the one the network recorded, not a confirmation.' : ''}</p>`;
  }

  async function tx(id) {
    const d = await get(`/tx/${id}`); if (!d) return notFound('No operation with that ID.');
    const o = d.op, b = d.block, raw = o.raw?.unsigned || o.raw || {};
    const skip = new Set(['chain_id', 'genesis_hash', 'protocol_version', 'address_namespace', 'signature_algorithm_id', 'transaction_kind']);
    const val = (k, v) => {
      if (v == null || v === '') return '<span class="muted">–</span>';
      if (typeof v === 'object') return `<span class="mono">${esc(JSON.stringify(v)).slice(0, 600)}</span>`;
      const sv = String(v);
      if (/^pf[0-9a-f]{40}$/.test(sv)) return addr(sv, o.party_labels?.[sv]);
      if (k.endsWith('asset_id') && sv.length === 96) return `${link(`/coin/${sv}`, esc(o.asset_names?.[sv] || 'asset'))} <span class="hash">${short(sv, 10, 6)}</span>`;
      if (/_hash$|_root$|_id$|nonce|digest|commitment|nullifier|anchor/.test(k) && sv.length > 30) return `<span class="hash" title="${esc(sv)}">${short(sv, 16, 8)}</span>${copyBtn(sv)}`;
      if (/atoms$|^amount$|_amount$/.test(k) && /^\d+$/.test(sv)) return `<span class="num">${units(sv)}</span> <span class="muted mono">${num(sv)} atoms</span>`;
      if (k === 'fee') return `<span class="num">${num(sv)}</span> atoms of PFT`;
      return esc(sv);
    };
    const fields = Object.entries(raw).filter(([k]) => !skip.has(k)).map(([k, v]) => `<div>${esc(k.replace(/_/g, ' '))}</div><div>${val(k, v)}</div>`).join('');
    const priv = o.privacy ? `${section('What the public can see')}<div class="privbox"><div class="ps"><div><b>Public</b>${o.privacy.public.map((x) => `<span>${esc(x)}</span>`).join('')}</div><div><b>Sealed</b>${o.privacy.sealed.map((x) => `<span>${esc(x)}</span>`).join('')}</div></div></div>` : '';
    return page(head(`Devnet · ${esc(LENS[o.lens] || o.lens)} · ${esc(o.kind.replace(/_/g, ' '))}`, sent(o, true), '',
      `<div class="ex-meta">${o.lens === 'private' ? '<span class="tag sealed">Sealed</span>' : ''}${resultTag(o)}${b ? levelTag(b.evidence) : ''}<span class="label">${link(`/block/${o.height}`, 'Block ' + num(o.height))}${b?.observed_at ? ` · <span title="${utc(b.observed_at)}">${ago(b.observed_at)}</span>` : ''}${o.fee != null ? ` · fee ${num(o.fee)} atoms` : ''}</span>${b ? seals(b, true) : ''}</div>
       ${o.accepted === false ? `<p class="sub ox">The network refused this operation: ${esc(o.message || o.code)}.</p>` : o.message ? `<p class="sub">${esc(o.message)}.</p>` : ''}`, 'sentence') +
      priv + journeyPanel(d.journey) +
      (o.parties?.length ? section('Parties') + `<div class="kv">${o.parties.map((p) => `<div>${esc(p.role.replace(/_/g, ' '))}</div><div>${addr(p.address, o.party_labels?.[p.address])}</div>`).join('')}</div>` : '') +
      section('Fields') + `<div class="kv">${fields || '<div>Record</div><div class="muted">No labelled fields.</div>'}</div>` +
      `<details class="fold"><summary>Raw record</summary><pre class="raw">${json(o.raw)}</pre><p class="ex-note">Proofs and signatures are shortened to their first bytes and their length.</p></details>` +
      checkPanel(b?.evidence, o.tx_id ? `{"method":"tx","params":{"tx_id":"${o.tx_id}"}}` : `{"method":"blocks","params":{"from_height":${o.height},"limit":1}}`, 'returns the receipt, the block and its signed certificate') +
      (o.tx_id ? `<div class="kv" style="margin-top:24px"><div>Transaction ID</div><div>${hashRow(o.tx_id)}</div></div>` : ''));
  }

  async function accountPage(a) {
    const d = await get(`/account/${a}`); if (!d) return notFound();
    const live = d.live || {};
    return page(head(`Devnet · account${d.label ? ' · ' + esc(d.label) : ''}`, `<span class="mono" style="font-size:.5em;letter-spacing:0">${esc(a)}</span>`,
      d.op_count ? `${num(d.op_count)} operation${d.op_count === 1 ? '' : 's'} since block ${num(d.first_height)}.` : 'No operations name this address yet.', `<div class="ex-meta">${copyBtn(a)}</div>`) +
      section('Balances') + (live.error ? `<p class="ex-note">${esc(live.error)}.</p>` : `<table class="ledger tight"><thead><tr><th>Asset</th><th class="r">Balance</th></tr></thead><tbody>
        <tr><td>PFT</td><td class="r num">${units(live.balance)}</td></tr>
        ${(live.lines || []).map((l) => `<tr><td>${link(`/coin/${l.asset_id}`, esc(l.code))}</td><td class="r num">${units(l.balance, l.precision)}</td></tr>`).join('')}
        </tbody></table><p class="ex-note">Read from the validators at block ${num(live.read_at_height)}. Sequence ${num(live.sequence)}.</p>`) +
      section('Operations') + `<ul class="stream">${d.ops.map((o) => opLine(o)).join('') || '<li class="ex-empty">None.</li>'}</ul>`);
  }

  async function coinsPage() {
    const d = await get('/coins');
    const row = (c) => `<tr><td>${link(`/coin/${c.asset_id}`, esc(c.code))}${c.retired ? ' <span class="tag prop">Retired</span>' : ''}${c.halted ? ' <span class="tag rej">Halted</span>' : ''}</td><td class="num">${usd(c.nav_per_unit, c.nav_decimals, 6)}</td><td class="num">${units(c.supply, c.precision, 2)}</td><td class="num">${usd(c.net_assets, c.nav_decimals)}</td><td>${c.checks.length} · last at ${c.last_check_height ? link(`/block/${c.last_check_height}`, num(c.last_check_height)) : '–'}</td><td>${spark(c.checks.map((x) => x.nav_per_unit))}</td></tr>`;
    const listed = d.coins.filter((c) => c.listed), other = d.coins.filter((c) => !c.listed);
    const table = (rows) => `<table class="ledger tight"><thead><tr><th>Coin</th><th>NAV per coin</th><th>Supply</th><th>Reserves</th><th>NAV checks</th><th></th></tr></thead><tbody>${rows.map(row).join('')}</tbody></table>`;
    return page(head('Devnet', 'NAVCoins', 'A NAVCoin trades at the value of the reserves behind it. Each NAV check is a reading of those reserves, submitted with a proof and finalized by the validators.') +
      section('Listed') + table(listed) + (other.length ? section('Earlier and test coins') + table(other) + '<p class="ex-note">Coins registered on the network during development. They are shown because they are on the ledger.</p>' : ''));
  }

  function navChart(c) {
    const pts = c.checks.filter((x) => x.nav_per_unit != null); if (pts.length < 2) return '';
    const W = 1000, H = 260, L = 70, R = 20, T = 20, B = 34; const vals = pts.map((x) => Number(x.nav_per_unit) / 10 ** c.nav_decimals);
    let lo = Math.min(...vals), hi = Math.max(...vals); const pad = (hi - lo || hi * 0.002 || 1) * 0.25; lo -= pad; hi += pad;
    const x = (i) => L + ((W - L - R) * i) / (pts.length - 1), y = (v) => T + (H - T - B) * (1 - (v - lo) / (hi - lo));
    const ticks = [lo + (hi - lo) * 0.1, (lo + hi) / 2, hi - (hi - lo) * 0.1];
    return `<svg class="chart" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" role="img" aria-label="NAV per coin at each check">
      ${ticks.map((t) => `<line class="grid" x1="${L}" x2="${W - R}" y1="${y(t).toFixed(1)}" y2="${y(t).toFixed(1)}"/><text x="${L - 8}" y="${(y(t) + 4).toFixed(1)}" text-anchor="end">$${t.toFixed(t < 10 ? 4 : 2)}</text>`).join('')}
      <path class="line" d="${vals.map((v, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)} ${y(v).toFixed(1)}`).join('')}"/>
      ${vals.map((v, i) => `<circle class="pt${i === vals.length - 1 ? ' last' : ''}" cx="${x(i).toFixed(1)}" cy="${y(v).toFixed(1)}" r="4"><title>Epoch ${pts[i].epoch}, block ${pts[i].height}: $${v}</title></circle>`).join('')}
      <text x="${L}" y="${H - 10}">Epoch ${esc(pts[0].epoch)} · block ${num(pts[0].height)}</text><text x="${W - R}" y="${H - 10}" text-anchor="end">Epoch ${esc(pts[pts.length - 1].epoch)} · block ${num(pts[pts.length - 1].height)}</text></svg>`;
  }

  async function coin(id) {
    const c = await get(`/coin/${id}`); if (!c) return notFound('No asset with that name or ID.');
    if (c.plain_asset) return page(head('Devnet · asset', esc(c.code || short(c.asset_id)), esc(c.name || ''), '') + `<div class="kv"><div>Asset ID</div><div>${hashRow(c.asset_id)}</div><div>Issuer</div><div>${addr(c.issuer)}</div><div>Precision</div><div>${esc(c.precision)}</div><div>Holders</div><div>${num(c.detail?.holder_count)}</div></div>` + section('Operations') + `<ul class="stream">${c.ops.map((o) => opLine(o)).join('')}</ul>`);
    const last = c.checks[c.checks.length - 1] || {};
    const age = meta && c.last_check_height ? meta.chain_height - c.last_check_height : null;
    const fresh = age == null || !c.max_snapshot_age_blocks ? '' : age <= c.max_snapshot_age_blocks ? `${num(age)} blocks old, within the limit of ${num(c.max_snapshot_age_blocks)}` : `${num(age)} blocks old, past the limit of ${num(c.max_snapshot_age_blocks)}`;
    return page(head(`Devnet · NAVCoin${c.retired ? ' · retired' : ''}`, esc(c.code), esc(c.description || c.name || ''),
      `<div class="ex-meta">${c.halted ? '<span class="tag rej">Halted</span>' : ''}${c.verifier_kind ? `<span class="tag demo">${esc(c.verifier_kind)}</span>` : ''}${fresh ? `<span class="label">Last check ${esc(fresh)}</span>` : ''}</div>`) +
      `<div class="stats"><div><div class="v num">${usd(c.nav_per_unit, c.nav_decimals, 6)}</div><div class="k">NAV per coin</div></div><div><div class="v num">${units(c.supply, c.precision, 0).replace(/\.00$/, '')}</div><div class="k">Supply at last check</div></div><div><div class="v num">${usd(c.net_assets, c.nav_decimals, 0).replace(/\.00$/, '')}</div><div class="k">Reserves at last check</div></div><div><div class="v num">${c.checks.length}</div><div class="k">NAV checks</div></div></div>` +
      section('NAV checks') + navChart(c) +
      `<table class="ledger tight"><thead><tr><th>Epoch</th><th>NAV per coin</th><th>Reserves</th><th>Supply</th><th>Block</th><th>Result</th></tr></thead><tbody>
      ${[...c.checks].reverse().map((x) => `<tr><td>${link(`/tx/${x.op}`, 'Epoch ' + esc(x.epoch))}</td><td class="num">${usd(x.nav_per_unit, c.nav_decimals, 6)}</td><td class="num">${usd(x.net_assets, c.nav_decimals)}</td><td class="num">${units(x.supply, c.precision, 2)}</td><td>${link(`/block/${x.height}`, num(x.height))}</td><td>${x.accepted === false ? '<span class="tag rej">Rejected</span>' : '<span class="tag ok">Accepted</span>'}</td></tr>`).join('')}
      </tbody></table><p class="ex-note">A check is a reserve reading submitted with its proof. "Accepted" means the validators accepted the submission under the coin's proof profile; it is the network's result, not the explorer's own check of the proof.</p>` +
      (c.routes?.length ? section('Ethereum') + `<div class="kv">${c.routes.map((r) => `<div>Route</div><div class="mono">${esc(r.route_id)}</div>${r.wrapped_token ? `<div>Wrapped token</div><div><a class="hash" target="_blank" rel="noopener" href="https://etherscan.io/token/${esc(r.wrapped_token)}">${esc(r.wrapped_token)} ↗</a></div>` : ''}${r.controller ? `<div>Controller</div><div><a class="hash" target="_blank" rel="noopener" href="https://etherscan.io/address/${esc(r.controller)}">${esc(r.controller)} ↗</a></div>` : ''}`).join('')}</div>` : '') +
      section(`Operations`, `<span class="label">${num(c.op_count)} in total</span>`) + `<ul class="stream">${c.ops.map((o) => opLine(o)).join('')}</ul>` +
      `<div class="kv" style="margin-top:28px"><div>Asset ID</div><div>${hashRow(c.asset_id)}</div><div>Issuer</div><div>${addr(c.issuer)}</div></div>`);
  }

  async function privatePage() {
    const d = await get('/private'); const share = d.shielded_blocks / Math.max(1, d.blocks); const C = 2 * Math.PI * 90;
    const names = { asset_orchard_ingress_v2: 'Deposits into the pool', shielded_swap_v1: 'Private swaps', asset_orchard_private_egress_v1: 'Private withdrawals', asset_orchard_private_primary_issue_v1: 'Private NAVCoin creations', asset_orchard_private_primary_redeem_v1: 'Private cash-ins', asset_orchard_egress_v1: 'Withdrawals' };
    return `<section class="ex-night"><div class="wrap">
      <div class="dialrow"><svg class="dial" viewBox="0 0 220 220" role="img" aria-label="${(share * 100).toFixed(1)} percent of blocks are private"><circle class="bg" cx="110" cy="110" r="90"/><circle class="fg" cx="110" cy="110" r="90" stroke-dasharray="${C.toFixed(1)}" stroke-dashoffset="${(C * (1 - share)).toFixed(1)}"/><text x="110" y="122" text-anchor="middle">${(share * 100).toFixed(1)}%</text><text class="cap" x="110" y="146" text-anchor="middle">OF BLOCKS</text></svg>
      <div><span class="label">Devnet · private</span><h1 class="display d-l" style="margin-top:14px">${num(d.shielded_blocks)} of ${num(d.blocks)} blocks are sealed.</h1><p class="sub lede" style="margin-top:18px">A private action proves it is valid without saying what it is. This page shows exactly what the ledger publishes for each one, and names what it keeps sealed.</p>
      <div class="chips">${d.kinds.map((k) => `<span class="chip" style="color:var(--night-ink);border-color:var(--night-rule)">${esc(names[k.kind] || k.kind)} · ${k.n}</span>`).join('')}</div></div></div>
      ${section('Latest private actions')}
      <div class="sealed-grid">${d.ops.map((o) => `<a class="sealed" href="#/tx/${esc(o.id)}"><div class="h">Block ${num(o.height)} · ${esc(names[o.kind] || o.kind)}</div><div class="s">${sent(o)}</div><div class="ps"><div><b>Public</b>${(o.privacy?.public || []).map((x) => `<span>${esc(x)}</span>`).join('')}</div><div><b>Sealed</b>${(o.privacy?.sealed || []).map((x) => `<span>${esc(x)}</span>`).join('')}</div></div></a>`).join('')}</div>
    </div></section>`;
  }

  async function journeys(q) {
    const kind = q.get('kind') || ''; const d = await get(`/journeys?kind=${kind}`);
    return page(head('Devnet', 'Journeys', 'One thing a person did, across every step it took. A deposit is a transaction on Ethereum and three operations here; it reads as one line.') +
      `<div class="chips"><a class="chip" href="#/journeys" aria-current="${!kind}">All</a>${Object.entries(JOURNEY).map(([k, v]) => `<a class="chip" href="#/journeys?kind=${k}" aria-current="${kind === k}">${esc(v)}${d.counts[k] ? ' · ' + d.counts[k] : ''}</a>`).join('')}</div>
      <table class="ledger tight"><thead><tr><th>Blocks</th><th>Journey</th><th>What happened</th><th>Steps</th><th>State</th></tr></thead><tbody>
      ${d.journeys.map((j) => `<tr><td>${num(j.first_height)}${j.last_height !== j.first_height ? '–' + num(j.last_height) : ''}</td><td>${link(`/journey/${j.kind}/${j.key}`, esc(JOURNEY[j.kind]))}</td><td>${esc(j.headline)}</td><td>${dots(j.steps)}</td><td><span class="tag ${j.summary === 'rejected' ? 'rej' : j.summary === 'in progress' ? 'demo' : 'ok'}">${esc(j.summary)}</span></td></tr>`).join('')}
      </tbody></table><p class="ex-note">A dashed mark is a step on Ethereum. This build does not read Ethereum, so those steps are shown as not checked and a journey reads "complete on the network" at most.</p>`);
  }
  async function journeyPage(kind, key) {
    const j = await get(`/journey/${kind}/${key}`); if (!j) return notFound('No journey with that key.');
    return page(head(`Devnet · journey · ${esc(JOURNEY[kind] || kind)}`, esc(j.headline), `Blocks ${num(j.first_height)} to ${num(j.last_height)}. State: ${esc(j.summary)}.`, '', 'sentence') + journeyPanel(j).replace(/<a href="#\/journey[^>]*>Open journey →<\/a>/, '') +
      section('Operations in this journey') + `<ul class="stream">${j.ops.map((o) => opLine(o)).join('')}</ul><div class="kv" style="margin-top:28px"><div>Journey key</div><div>${hashRow(j.key)}</div></div>`);
  }

  async function network() {
    const d = await get('/network');
    return page(head('Devnet', 'Network', `Six validators take turns proposing. Running build ${esc(d.status.build_git_revision || '–')}.`) +
      section('Validators') + `<table class="ledger tight"><thead><tr><th>Validator</th><th class="r">Blocks proposed</th><th class="r">Votes in the last 300 blocks</th><th class="r">Last proposed</th></tr></thead><tbody>${d.validators.map((v) => `<tr><td>${esc(v.proposer)}</td><td class="r num">${num(v.proposed)}</td><td class="r num">${num(v.votes_last_300)}</td><td class="r">${link(`/block/${v.last}`, num(v.last))}</td></tr>`).join('')}</tbody></table>` +
      section('Rule changes and governance') + `<ul class="stream">${d.governance.map((o) => opLine(o)).join('')}</ul>`);
  }

  const notFound = (msg) => page(head('Explorer', 'Nothing here.', esc(msg || 'That page does not exist.')) + `<div class="btns">${link('/', 'Back to the devnet', 'btn solid')}</div>`);

  // ── router ─────────────────────────────────────────────────────────────────
  const routes = [
    [/^\/$/, home], [/^\/stream$/, streamPage], [/^\/blocks$/, blocks], [/^\/block\/(\d+)$/, block], [/^\/tx\/([^/]+)$/, tx], [/^\/account\/([^/]+)$/, accountPage],
    [/^\/coins$/, coinsPage], [/^\/coin\/([^/]+)$/, coin], [/^\/private$/, privatePage], [/^\/journeys$/, journeys], [/^\/journey\/([a-z]+)\/([^/]+)$/, journeyPage], [/^\/network$/, network],
  ];
  function parse() { const raw = location.hash.replace(/^#/, '') || '/'; const [path, qs = ''] = raw.split('?'); return { path: path || '/', q: new URLSearchParams(qs), raw }; }
  function chrome(path) {
    const nav = document.getElementById('ex-nav');
    const items = [['/', 'Overview'], ['/stream', 'Operations'], ['/blocks', 'Blocks'], ['/coins', 'NAVCoins'], ['/journeys', 'Journeys'], ['/private', 'Private'], ['/network', 'Network']];
    const here = location.hash.replace(/^#/, '') || '/';
    nav.innerHTML = items.map(([r, t]) => `<a href="#${r}"${here === r || (r !== '/' && here.split('?')[0] === r) ? ' aria-current="page"' : ''}>${t}</a>`).join('');
  }
  async function render(soft) {
    const { path, q } = parse(); const mine = ++seq; chrome(path);
    const hit = routes.map(([re, fn]) => [path.match(re), fn]).find(([m]) => m);
    if (!soft) root.innerHTML = '<div class="wrap ex-loading">Reading the ledger…</div>';
    try {
      const html = hit ? await hit[1](...hit[0].slice(1), q) : notFound();
      if (mine !== seq) return;
      const y = scrollY; root.innerHTML = html; if (soft) scrollTo(0, y); else scrollTo(0, 0);
      document.title = `${(root.querySelector('h1')?.textContent || 'Explorer').trim().slice(0, 70)} · Post Fiat Explorer`;
    } catch (e) {
      pulse(false);
      if (!soft) root.innerHTML = page(head('Explorer', 'The explorer service is not answering.', 'The page will try again on its own. Nothing is wrong with the network because of this.'));
    }
    clearTimeout(timer);
    const live = path === '/';
    timer = setTimeout(() => { if (!document.hidden) render(true); else timer = setTimeout(() => render(true), 6000); }, live ? 6000 : 30000);
  }
  addEventListener('hashchange', () => { lastTop = null; render(false); });
  document.addEventListener('click', (e) => {
    const lens = e.target.closest('[data-lens]');
    if (lens) { const on = lens.getAttribute('aria-pressed') === 'true'; location.hash = on ? '#/' : `#/?lens=${lens.dataset.lens}`; return; }
    const copy = e.target.closest('[data-copy]');
    if (copy) { navigator.clipboard?.writeText(copy.dataset.copy); const t = copy.textContent; copy.textContent = 'Copied'; setTimeout(() => (copy.textContent = t), 1200); }
  });
  document.getElementById('ex-search')?.addEventListener('submit', async (e) => {
    e.preventDefault(); const input = e.target.querySelector('input'); const q = input.value.trim(); if (!q) return;
    try { const r = await get(`/search?q=${encodeURIComponent(q)}`); if (r?.route) { location.hash = '#' + r.route; input.value = ''; } else { input.value = ''; input.placeholder = 'Nothing on the network matches that'; } } catch { pulse(false); }
  });
  render(false);
})();
