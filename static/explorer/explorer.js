/* Post Fiat Explorer. One file, no framework. All state lives in the URL hash. */
(() => {
  const root = document.getElementById('ex');
  if (!root) return;
  const API = (root.dataset.api || '/api/explorer/v1').replace(/\/$/, '');
  const LENS = { bridge: 'Bridge', payments: 'Payments', navmarket: 'Coin market', private: 'Private', navchecks: 'NAV checks', market: 'Swaps', fastlane: 'Fast lane', network: 'Network' };
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
  const fixed = (atoms, precision = 6) => { const a = BigInt(Math.trunc(Number(atoms || 0))); const base = 10n ** BigInt(precision); return `${(a / base).toLocaleString('en-US')}.${(a % base).toString().padStart(precision, '0')}`; };
  const usd = (atoms, d = 6, max = 2) => (atoms == null ? '–' : `$${units(atoms, d, max)}`);
  const ago = (t) => { if (!t) return ''; const s = Math.max(0, Date.now() / 1000 - t); if (s < 90) return `${Math.round(s)} sec ago`; if (s < 5400) return `${Math.round(s / 60)} min ago`; if (s < 129600) return `${Math.round(s / 3600)} hours ago`; if (s < 86400 * 45) return `${Math.round(s / 86400)} days ago`; return new Date(t * 1000).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' }); };
  const when = (t) => (t ? `<time datetime="${new Date(t * 1000).toISOString()}" title="${utc(t)}">${ago(t)}</time>` : '');
  const utc = (t) => (t ? new Date(t * 1000).toISOString().replace('T', ' ').slice(0, 19) + ' UTC' : '');
  const link = (route, text, cls = '') => `<a href="#${route}"${cls ? ` class="${cls}"` : ''}>${text}</a>`;
  const addr = (a, label) => (a ? (label ? `${esc(label)} ` : '') + link(`/account/${a}`, esc(a), 'hash lk') : '–');
  // Sentences arrive with shortened addresses; put the full ones back, linked.
  // Sentences carry shortened addresses. Each one becomes a link to the full address page.
  const sent = (o) => { let h = esc(o.sentence); for (const a of o.addrs || []) { const tok = esc(`${a.slice(0, 8)}…${a.slice(-4)}`); if (!h.includes(tok)) continue; h = h.split(tok).join(a.startsWith('pf') ? `<a class="ad" href="#/account/${esc(a)}" title="${esc(a)}">${tok}</a>` : `<a class="ad" href="https://etherscan.io/address/${esc(a)}" target="_blank" rel="noopener" title="${esc(a)}">${tok}</a>`); } return h; };
  // Success is the normal case and gets no chip. Only exceptions are marked.
  const resultTag = (o, always) => o.accepted === false ? `<span class="tag rej" title="${esc(o.code || '')}">Rejected</span>` : o.code === 'filled' ? '<span class="tag fill">Filled</span>' : o.accepted == null ? '<span class="tag prop">No receipt</span>' : always ? '<span class="tag ok">Accepted</span>' : '';
  const levelTag = (e) => `<span class="tag ${e === 'disputed' ? 'rej' : 'lvl'}" title="How far the explorer has checked this record">${esc(e === 'cross-checked' ? 'Cross-checked' : e === 'disputed' ? 'Disputed' : 'Reported')}</span>`;
  const copyBtn = (v) => `<button class="copy" data-copy="${esc(v)}">Copy</button>`;
  const hashRow = (v) => `<span class="hash" title="${esc(v)}">${esc(v)}</span>${copyBtn(v)}`;
  const etherscan = (e) => { if (!e || !e.tx) return ''; const h = e.tx.startsWith('0x') ? e.tx : '0x' + e.tx; const base = { 1: 'https://etherscan.io', 11155111: 'https://sepolia.etherscan.io', 42161: 'https://arbiscan.io' }[e.chain_id] || 'https://etherscan.io'; return `<a class="hash" href="${base}/tx/${esc(h)}" rel="noopener" target="_blank">${short(h, 10, 6)} ↗</a>`; };
  const seals = (block, small) => { const voted = new Set((block.header?.votes || []).map((v) => v.validator)); const all = block.header?.validators || [...voted]; return `<span class="marks${small ? ' small' : ''}">${all.map((v) => `<span class="mark${voted.has(v) ? ' done' : ' none'}${v === block.proposer ? ' prop' : ''}" title="${esc(v)}${voted.has(v) ? ': recorded accepting vote' : ': no vote recorded'}${v === block.proposer ? ' (proposer)' : ''}"><i></i>${small ? '' : `<b>${esc(v.replace('validator-', 'v'))}</b><em>${v === block.proposer ? 'proposed' : voted.has(v) ? 'voted' : 'no vote'}</em>`}</span>`).join('')}</span>`; };
  const STEP = { done: 'done', unknown: 'on Ethereum, not read', pending: 'waiting', 'not-started': 'not started', rejected: 'refused', mismatched: 'mismatch' };
  const dots = (steps) => `<span class="marks small">${steps.map((s) => `<span class="mark ${esc(s.state)}" title="${esc(s.label)}: ${esc(STEP[s.state] || s.state)}"><i></i></span>`).join('')}</span>`;
  const spark = (vals) => { vals = (vals || []).map(Number).filter((v) => isFinite(v) && v > 0); if (vals.length < 2) return '<svg class="spark" viewBox="0 0 120 30"><path d="M2 15H118"/></svg>'; const last = vals[vals.length - 1]; const half = Math.max(last * 0.005, Math.max(...vals.map((v) => Math.abs(v - last))) * 1.15); const lo = last - half, sp = 2 * half; const pt = (v, i) => [2 + (116 * i) / (vals.length - 1), 26 - (22 * (v - lo)) / sp]; const d = vals.map((v, i) => `${i ? 'L' : 'M'}${pt(v, i).map((n) => n.toFixed(1)).join(' ')}`).join(''); const [lx, ly] = pt(last, vals.length - 1); return `<svg class="spark" viewBox="0 0 120 30" aria-hidden="true"><path d="${d}"/><circle cx="${lx.toFixed(1)}" cy="${ly.toFixed(1)}" r="2.2"/></svg>`; };
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
  const opLine = (o, isNew) => `<li class="${isNew ? 'new' : ''}${o.accepted === false ? ' rejected' : ''}"><a class="rowlink" href="#/tx/${esc(o.id)}" aria-label="Open operation in block ${o.height}"></a><span class="h">${o.count > 1 ? `${num(o.first)}–${num(o.height)}` : num(o.height)}<small>${when(o.time)}</small></span><span class="s">${sent(o)}${o.count > 1 ? ` <span class="times">× ${o.count}</span>` : ''}<small>${esc(LENS[o.lens] || o.lens)}${o.journey ? ' · ' + esc(JOURNEY[o.journey.kind] || '') : ''}</small></span><span class="st">${o.lens === 'private' ? '<span class="tag sealed">Sealed</span>' : resultTag(o)}</span><span class="go" aria-hidden="true">→</span></li>`;
  // Runs of identical operations in consecutive blocks collapse to one row with a count.
  const collapse = (ops) => { const out = []; for (const o of ops) { const last = out[out.length - 1]; if (last && last.sentence === o.sentence && last.accepted === o.accepted && (last.first - o.height === 1 || o.lens === 'private')) { last.count += 1; last.first = o.height; } else out.push({ ...o, count: 1, first: o.height }); } return out; };
  const head = (label, title, sub, extra = '', cls = '') => `<header class="ex-head"><span class="label">${label}</span><h1 class="${cls}">${title}</h1>${sub ? `<p class="sub">${sub}</p>` : ''}${extra}</header>`;
  const section = (title, more = '') => `<div class="ex-h2"><h2>${title}</h2>${more}</div>`;
  const page = (html, flush) => `<div class="wrap ex-page${flush ? ' flush' : ''}">${html}</div>`;

  // ── pages: devnet ──────────────────────────────────────────────────────────
  async function home(q) {
    const d = await get('/summary'); if (!d) return notFound();
    const lens = q.get('lens');
    const raw = lens ? (await get(`/stream?lens=${encodeURIComponent(lens)}`)).ops : d.stream;
    const stream = collapse(raw).slice(0, 12);
    const max = Math.max(...d.lenses.map((l) => l.count), 1);
    const top = d.stream[0]?.id; const fresh = lastTop && top !== lastTop && !lens; lastTop = top;
    return page(`
      <section class="ex-hero">
        <div class="big"><small>Devnet · ${esc(d.network.chain_id)} · latest block</small><span class="num">${num(d.height)}</span><span class="since">${d.tip_time ? ago(d.tip_time) : ''}</span></div>
        <div><p class="status-line"><span class="dot"></span>${d.latest_blocks[0] ? `${d.latest_blocks[0].votes} of 6 validators voted on it` : 'Live'} · blocks are made when there is something to record</p><p class="lede">Every block carries the recorded votes of its validators, signed with post-quantum signatures. Read any operation as a sentence, then check the record behind it.</p></div>
      </section>
      <div class="stats">
        <div><div class="v num">${num(d.ops)}</div><div class="k">Operations</div></div>
        <div><div class="v num">${num(d.addresses)}</div><div class="k">Addresses</div></div>
        <div><div class="v num">${d.coins.filter((c) => c.listed).length}</div><div class="k">NAVCoins listed</div></div>
        <div><div class="v num">${(d.shielded_share * 100).toFixed(1)}%</div><div class="k">Blocks that are private</div></div>
      </div>
      ${section('What the network is doing', lens ? link('/', 'Show everything') : '<span class="hint">All operations since block 1</span>')}
      <div class="lenses" role="group" aria-label="Filter by lens">${d.lenses.map((l) => `<button data-lens="${l.lens}" aria-pressed="${lens === l.lens}" title="${num(l.count)} of ${num(d.ops)} operations (${((100 * l.count) / d.ops).toFixed(0)}%)"><span class="v num">${num(l.count)}</span><span class="k">${esc(LENS[l.lens])}</span><span class="bar"><i style="width:${Math.max(3, (100 * l.count) / max).toFixed(1)}%"></i></span><span class="cta">${lens === l.lens ? 'Clear filter ×' : 'Filter →'}</span></button>`).join('')}</div>
      <div class="cols">
        <div>${section(lens ? esc(LENS[lens]) : 'Latest operations', link(`/stream${lens ? `?lens=${lens}` : ''}`, 'All →'))}<ul class="stream" id="ex-stream">${stream.map((o, i) => opLine(o, fresh && i === 0)).join('') || '<li class="ex-empty">Nothing yet.</li>'}</ul></div>
        <div>${section('Latest blocks', link('/blocks', 'All →'))}
          <ul class="rows">${d.latest_blocks.slice(0, 6).map((b) => `<li><a class="rowlink" href="#/block/${b.height}" aria-label="Block ${b.height}"></a><span class="a">${num(b.height)}</span><span class="b">${esc(b.proposer)}<small>${b.n_ops} ${esc(b.kind)} op${b.n_ops === 1 ? '' : 's'}</small></span><span class="c">${seals({ header: { votes: [], validators: [] }, proposer: '' }, true)}${b.votes}/6 · ${when(b.time)}</span></li>`).join('')}</ul>
          ${section('NAVCoins', link('/coins', 'All →'))}
          <ul class="rows">${d.coins.filter((c) => c.listed).map((c) => `<li><a class="rowlink" href="#/coin/${esc(c.asset_id)}" aria-label="${esc(c.code)}"></a><span class="a">${esc(c.code)}</span><span class="b">${usd(c.nav_per_unit, c.nav_decimals, 6)}${c.retired ? ' · retired' : ''}</span><span class="c">${spark(c.spark)}</span></li>`).join('')}</ul>
          ${section('Latest journeys', link('/journeys', 'All →'))}
          <ul class="rows">${(d.latest_journeys || []).map((j) => `<li><a class="rowlink" href="#/journey/${j.kind}/${esc(j.key)}" aria-label="${esc(JOURNEY[j.kind])}"></a><span class="a">${dots(j.steps)}</span><span class="b">${esc(j.headline)}</span><span class="c"><small>${when(j.time)}</small></span></li>`).join('')}</ul>
        </div>
      </div>`);
  }

  async function streamPage(q) {
    const lens = q.get('lens') || '', before = q.get('before') || '', rej = q.get('rejected') || '', asset = q.get('asset') || '';
    const d = await get(`/stream?lens=${lens}&before=${before}${rej ? '&rejected=1' : ''}${asset ? '&asset=' + asset : ''}`);
    const chip = (l, t) => `<a class="chip" href="#/stream${l ? `?lens=${l}` : ''}" aria-current="${lens === l && !rej}">${t}</a>`;
    return page(head('Devnet', 'Operations', 'Every operation on the network, newest first.') +
      `<div class="chips">${chip('', 'All')}${Object.entries(LENS).map(([k, v]) => chip(k, esc(v))).join('')}<a class="chip" href="#/stream?rejected=1" aria-current="${!!rej}">Rejected</a></div>
      <ul class="stream">${d.ops.map((o) => opLine(o)).join('') || '<li class="ex-empty">Nothing here.</li>'}</ul>
      <div class="pager">${d.next ? link(`/stream?lens=${lens}${rej ? '&rejected=1' : ''}${asset ? '&asset=' + asset : ''}&before=${d.next}`, 'Older →', 'btn') : ''}</div>`);
  }

  async function blocks(q) {
    const d = await get(`/blocks?before=${q.get('before') || ''}`);
    return page(head('Devnet', 'Blocks', 'One block per agreed batch. A filled mark is a recorded accepting vote; the ringed mark is the proposer.') +
      `<table class="ledger tight"><thead><tr><th>Block</th><th>Proposer</th><th>Kind</th><th>Operations</th><th>Votes</th><th>When</th><th>Evidence</th></tr></thead><tbody>
      ${d.blocks.map((b) => `<tr><td>${link(`/block/${b.height}`, num(b.height))}</td><td>${esc(b.proposer)}</td><td>${esc(b.kind)}</td><td class="num">${b.n_ops}</td><td class="num">${b.votes} of 6</td><td>${when(b.time) || '–'}</td><td>${levelTag(b.evidence)}</td></tr>`).join('')}
      </tbody></table><div class="pager">${d.next ? link(`/blocks?before=${d.next}`, 'Older →', 'btn') : ''}</div>`);
  }

  async function block(h) {
    const d = await get(`/block/${h}`); if (!d) return notFound(`Block ${esc(h)} is not on the network.`);
    const b = d.block;
    return page(head(`Devnet · ${esc(b.kind)} block`, `Block ${num(b.height)}`,
      `${b.n_ops} operation${b.n_ops === 1 ? '' : 's'}, proposed by ${esc(b.proposer)}, with ${b.votes} recorded accepting votes of 6 (quorum ${b.quorum}).`,
      `<div class="ex-meta">${levelTag(b.evidence)}${b.time ? `<span class="label">${when(b.time)} · ${esc(utc(b.time))} · time from ${esc(b.time_source === 'validator vote record' ? "a validator's vote record" : 'the explorer seeing the block')}</span>` : ''}</div><div class="ex-meta">${d.prev ? link(`/block/${d.prev}`, '← Block ' + num(d.prev), 'btn sm') : ''}${d.next ? link(`/block/${d.next}`, 'Block ' + num(d.next) + ' →', 'btn sm') : ''}</div>`) +
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
      `<div class="journey">${j.steps.map((s) => `<div class="jstep ${esc(s.state)}"><span class="mark ${esc(s.state)}"><i></i></span><div class="l">${esc(s.label)}</div><div class="n">${
        s.state === 'done' ? `Done · ${link(`/tx/${s.op}`, 'block ' + num(s.height))}${s.time ? '<br>' + when(s.time) : ''}` : s.state === 'rejected' ? `Rejected · ${link(`/tx/${s.op}`, esc(s.code || ''))}` : s.state === 'unknown' ? `Not checked${s.eth ? '<br>' + etherscan(s.eth) : ''}` : s.state === 'pending' ? 'Pending' : 'Not started'}</div></div>`).join('')}</div>
      <p class="ex-note">${j.steps.some((s) => s.state === 'unknown') ? 'This build does not read Ethereum. Ethereum steps show "not checked", and any hash shown is the one the network recorded, not a confirmation.' : ''}</p>`;
  }

  async function tx(id) {
    const d = await get(`/tx/${id}`); if (!d) return notFound('No operation with that ID.');
    const o = d.op, b = d.block, raw = o.raw?.unsigned || o.raw || {};
    const skip = new Set(['chain_id', 'genesis_hash', 'protocol_version', 'address_namespace', 'signature_algorithm_id', 'transaction_kind', 'fee']);
    const val = (k, v) => {
      if (v == null || v === '') return '<span class="muted">–</span>';
      if (typeof v === 'object') return `<span class="mono">${esc(JSON.stringify(v)).slice(0, 600)}</span>`;
      const sv = String(v);
      if (/^pf[0-9a-f]{40}$/.test(sv)) return addr(sv, o.party_labels?.[sv]);
      if (k.endsWith('asset_id') && sv.length === 96) return `${link(`/coin/${sv}`, esc(o.asset_names?.[sv] || 'asset'))} <span class="hash">${short(sv, 10, 6)}</span>`;
      if (/_hash$|_root$|_id$|nonce|digest|commitment|nullifier|anchor/.test(k) && sv.length > 30) return `<span class="hash" title="${esc(sv)}">${short(sv, 16, 8)}</span>${copyBtn(sv)}`;
      if (/atoms$|^amount$|_amount$/.test(k) && /^\d+$/.test(sv)) return `<span class="num">${units(sv)}</span><span class="sub2">${num(sv)} atoms, the ledger's smallest unit</span>`;
      if (k === 'fee') return `<span class="num">${num(sv)}</span> atoms of PFT`;
      return esc(sv);
    };
    const byAddr = new Map(); for (const p of o.parties || []) byAddr.set(p.address, [...(byAddr.get(p.address) || []), p.role]);
    const grouped = [...byAddr.entries()];
    const partyKeys = new Set((o.parties || []).map((p) => p.role));
    const fields = Object.entries(raw).filter(([k, v]) => !skip.has(k) && !(partyKeys.has(k) && typeof v === 'string' && v.startsWith('pf'))).map(([k, v]) => `<div>${esc(k.replace(/_atoms$/, '').replace(/_/g, ' '))}</div><div>${val(k, v)}</div>`).join('');
    const priv = o.privacy ? `${section('What the public can see')}<div class="privbox"><div class="ps"><div><b>Public</b>${o.privacy.public.map((x) => `<span>${esc(x)}</span>`).join('')}</div><div><b>Not published</b>${o.privacy.sealed.map((x) => `<span>${esc(x)}</span>`).join('')}</div></div></div>` : '';
    return page(head(`Devnet · ${esc(LENS[o.lens] || o.lens)} · ${esc(o.kind.replace(/_/g, ' '))}`, sent(o, true), '',
      `<div class="ex-meta">${o.lens === 'private' ? '<span class="tag sealed">Sealed</span>' : ''}${resultTag(o, true)}${b ? levelTag(b.evidence) : ''}<span class="label">${link(`/block/${o.height}`, 'Block ' + num(o.height), 'lk')}${b?.time ? ` · ${when(b.time)} · ${esc(utc(b.time))}` : ''}${o.fee != null ? ` · fee ${num(o.fee)} atoms of PFT` : ''}</span></div>
       <dl class="facts">${o.tx_id ? `<div><dt>Transaction</dt><dd><span class="hash" title="${esc(o.tx_id)}">${short(o.tx_id, 14, 10)}</span>${copyBtn(o.tx_id)}</dd></div>` : ''}${b ? `<div><dt>Validator votes</dt><dd><span title="Filled: recorded accepting vote. Empty: no vote recorded. Ringed: proposer.">${seals(b, true)}</span> ${b.votes} of 6, proposed by ${esc(b.proposer)}</dd></div>` : ''}</dl>
       ${o.accepted === false ? `<p class="sub ox">The network refused this operation: ${esc(o.message || o.code)}.</p>` : ''}`, 'sentence') +
      priv + journeyPanel(d.journey) +
      (grouped.length ? section('Parties') + `<div class="kv">${grouped.map(([a, roles]) => `<div>${esc(roles.join(', ').replace(/_/g, ' '))}</div><div>${addr(a, o.party_labels?.[a])}</div>`).join('')}</div>` : '') +
      section('Fields') + `<div class="kv">${fields || '<div>Record</div><div class="muted">No labelled fields.</div>'}</div>` +
      `<details class="fold"><summary>Raw record</summary><pre class="raw">${json(o.raw)}</pre><p class="ex-note">Proofs and signatures are shortened to their first bytes and their length.</p></details>` +
      checkPanel(b?.evidence, o.tx_id ? `{"method":"tx","params":{"tx_id":"${o.tx_id}"}}` : `{"method":"blocks","params":{"from_height":${o.height},"limit":1}}`, 'returns the receipt, the block and its signed certificate') +
      '');
  }

  async function accountPage(a) {
    const d = await get(`/account/${a}`); if (!d) return notFound();
    const live = d.live || {};
    const held = (live.lines || []).filter((l) => Number(l.balance) > 0); const empty = (live.lines || []).length - held.length;
    const known = (l) => l.listed || (l.code === 'PFUSDC' && l.issuer === 'pf23d8831301aa1cce6fdd7bf4a2db2aead1619ba8');
    const main = held.filter(known).sort((a, b) => (a.code === 'PFUSDC') - (b.code === 'PFUSDC')), other = held.filter((l) => !known(l)); const pf = main.filter((l) => l.code === 'PFUSDC');
    const lineRow = (l) => `<tr><td>${link(`/coin/${l.asset_id}`, esc(l.code), 'lk')} ${l.listed ? '<span class="tag lvl">Listed NAVCoin</span>' : known(l) ? `<span class="tag lvl">Bridge series ${esc(l.asset_id.slice(0, 4))}</span>` : '<span class="tag prop">Unlisted</span>'} <span class="hash" title="${esc(l.asset_id)}">asset ${short(l.asset_id, 8, 4)}</span></td><td class="r num">${fixed(l.balance, l.precision)}</td></tr>`;
    const seen = {}; for (const l of held) seen[l.code] = (seen[l.code] || 0) + 1; const dup = new Set(Object.keys(seen).filter((k) => seen[k] > 1));
    return page(head(`Devnet · account${d.label ? ' · ' + esc(d.label) : ''}`, `<span class="mono" style="font-size:.46em;letter-spacing:0">${esc(a)}</span>${copyBtn(a)}`,
      d.op_count ? `${num(d.op_count)} operation${d.op_count === 1 ? '' : 's'} since block ${num(d.first_height)}.` : 'No operations name this address yet.', '') +
      section('Balances') + (live.error ? `<p class="ex-note">${esc(live.error)}.</p>` : `<table class="ledger tight"><thead><tr><th>Asset</th><th class="r">Balance</th></tr></thead><tbody>
        <tr><td>PFT <span class="tag lvl">Network token</span></td><td class="r num">${fixed(live.balance, 6)}</td></tr>
        ${main.map(lineRow).join('')}${pf.length > 1 ? `<tr class="total"><td>PFUSDC across ${pf.length} bridge series</td><td class="r num">${fixed(pf.reduce((n, l) => n + Number(l.balance), 0), 6)}</td></tr>` : ''}
        </tbody></table>${other.length ? `<h3 class="subhead">Unlisted assets</h3><p class="ex-note warn">These are not listed NAVCoins or bridge PFUSDC. An unlisted asset can carry the same name as a listed one. Check the asset ID before trusting a name.</p><table class="ledger tight dim"><tbody>${other.map(lineRow).join('')}</tbody></table>` : ''}<p class="ex-note">Read from the validators at block ${num(live.read_at_height)}. Sequence ${num(live.sequence)}.${empty ? ` ${empty} line${empty === 1 ? '' : 's'} with a zero balance ${empty === 1 ? 'is' : 'are'} not shown.` : ''}</p>`) +
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

  // One bar per check: how far the NAV sits from $1.00, in hundredths of a percent, on a fixed ±0.5% scale.
  function navChart(c) {
    const pts = c.checks.filter((x) => x.nav_per_unit != null); if (pts.length < 2) return '';
    const vals = pts.map((x) => Number(x.nav_per_unit) / 10 ** c.nav_decimals); const ref = Math.abs(vals[vals.length - 1] - 1) < 0.05 ? 1 : vals[0];
    const dev = vals.map((v) => ((v - ref) / ref) * 100); const scale = Math.max(0.5, ...dev.map(Math.abs)) ;
    return `<div class="devs" role="img" aria-label="Deviation of NAV from ${ref === 1 ? '$1.00' : 'the first check'} at each check"><div class="devs-key">${ref === 1 ? 'Distance from $1.00' : 'Change since the first check'} at each check · scale ±${scale.toFixed(1)}%</div>${pts.map((x, i) => `<a class="dev" href="#/tx/${esc(x.op)}" title="Epoch ${esc(x.epoch)}, block ${x.height}"><span class="e">Epoch ${esc(x.epoch)}</span><span class="track"><i class="${dev[i] < 0 ? 'neg' : 'pos'}" style="${dev[i] < 0 ? 'right' : 'left'}:50%;width:${Math.max(0.4, (Math.abs(dev[i]) / scale) * 50).toFixed(2)}%"></i></span><span class="v">${dev[i] === 0 ? '0.000' : (dev[i] > 0 ? '+' : '−') + Math.abs(dev[i]).toFixed(3)}%</span><span class="n">$${vals[i].toFixed(6)}</span></a>`).join('')}</div>`;
  }
  function navBar(c, x) { const v = c.checks.map((k) => Number(k.nav_per_unit)).filter((k) => k > 0); const lo = Math.min(...v), hi = Math.max(...v); if (hi === lo) return '<span class="quiet">no change</span>'; const pos = ((Number(x.nav_per_unit) - lo) / (hi - lo)) * 100; return `<span class="rng" title="Lowest ${usd(lo, c.nav_decimals, 6)}, highest ${usd(hi, c.nav_decimals, 6)}"><i style="left:${pos.toFixed(1)}%"></i></span>`; }
  function navRange(c) { const v = c.checks.map((x) => Number(x.nav_per_unit)).filter((x) => x > 0); if (v.length < 2) return ''; const lo = Math.min(...v), hi = Math.max(...v); return `<span class="hint">Lowest to highest across ${v.length} checks: ${(((hi - lo) / lo) * 100).toFixed(3)}%</span>`; }
  async function coin(id) {
    const c = await get(`/coin/${id}`); if (!c) return notFound('No asset with that name or ID.');
    if (c.plain_asset) return page(head('Devnet · asset', esc(c.code || short(c.asset_id)), esc(c.name || ''), '') + `<div class="kv"><div>Asset ID</div><div>${hashRow(c.asset_id)}</div><div>Issuer</div><div>${addr(c.issuer)}</div><div>Precision</div><div>${esc(c.precision)}</div><div>Holders</div><div>${num(c.detail?.holder_count)}</div></div>` + section('Operations') + `<ul class="stream">${c.ops.map((o) => opLine(o)).join('')}</ul>`);
    const last = c.checks[c.checks.length - 1] || {};
    const age = meta && c.last_check_height ? meta.chain_height - c.last_check_height : null;
    const fresh = age == null || !c.max_snapshot_age_blocks ? '' : age <= c.max_snapshot_age_blocks ? `${num(age)} blocks old, within the limit of ${num(c.max_snapshot_age_blocks)}` : `${num(age)} blocks old, past the limit of ${num(c.max_snapshot_age_blocks)}`;
    return page(head(`Devnet · NAVCoin${c.retired ? ' · retired' : ''}`, esc(c.code), esc(c.description || c.name || ''),
      `<div class="ex-meta">${c.halted ? '<span class="tag rej">Halted</span>' : ''}${c.verifier_kind ? `<span class="tag demo">${esc(c.verifier_kind)}</span>` : ''}${fresh ? `<span class="label">Last check ${esc(fresh)}</span>` : ''}</div>`) +
      `<div class="stats"><div><div class="v num">${usd(c.nav_per_unit, c.nav_decimals, 6)}</div><div class="k">NAV per coin</div></div><div><div class="v num">${units(c.supply, c.precision, 0).replace(/\.00$/, '')}</div><div class="k">Supply at last check</div></div><div><div class="v num">${usd(c.net_assets, c.nav_decimals, 0).replace(/\.00$/, '')}</div><div class="k">Reserves at last check</div></div><div><div class="v num">${c.checks.length}</div><div class="k">NAV checks</div></div></div>` +
      `<div class="kv compact"><div>Asset ID</div><div>${hashRow(c.asset_id)}</div><div>Issuer</div><div>${addr(c.issuer)}</div></div>` +
      section('NAV checks', navRange(c)) +
      `<table class="ledger tight"><thead><tr><th>Epoch</th><th>NAV per coin</th><th>Move within the observed range</th><th>Reserves</th><th>Supply</th><th>Block</th><th>Result</th></tr></thead><tbody>
      ${[...c.checks].reverse().map((x) => `<tr><td>${link(`/tx/${x.op}`, 'Epoch ' + esc(x.epoch))}</td><td class="num">${usd(x.nav_per_unit, c.nav_decimals, 6)}</td><td>${navBar(c, x)}</td><td class="num">${usd(x.net_assets, c.nav_decimals)}</td><td class="num">${units(x.supply, c.precision, 2)}</td><td>${link(`/block/${x.height}`, num(x.height))}</td><td>${x.accepted === false ? '<span class="tag rej">Rejected</span>' : '<span class="quiet">Accepted</span>'}</td></tr>`).join('')}
      </tbody></table><p class="ex-note">A check is a reserve reading submitted with its proof. "Accepted" means the validators accepted the submission under the coin's proof profile; it is the network's result, not the explorer's own check of the proof.</p>` +
      (c.routes?.length ? section('Ethereum') + `<div class="kv">${c.routes.map((r) => `<div>Route</div><div class="mono">${esc(r.route_id)}</div>${r.wrapped_token ? `<div>Wrapped token</div><div><a class="hash" target="_blank" rel="noopener" href="https://etherscan.io/token/${esc(r.wrapped_token)}">${esc(r.wrapped_token)} ↗</a></div>` : ''}${r.controller ? `<div>Controller</div><div><a class="hash" target="_blank" rel="noopener" href="https://etherscan.io/address/${esc(r.controller)}">${esc(r.controller)} ↗</a></div>` : ''}`).join('')}</div>` : '') +
      section(`Operations`, link(`/stream?asset=${c.asset_id}`, `All ${num(c.op_count)} →`)) + `<ul class="stream">${collapse(c.ops).slice(0, 15).map((o) => opLine(o)).join('')}</ul><p class="ex-note">Showing the latest of ${num(c.op_count)}. ${link(`/stream?asset=${c.asset_id}`, 'See all operations for ' + esc(c.code) + ' →', 'lk')}</p>` +
      '');
  }

  async function privatePage() {
    const d = await get('/private'); const share = d.shielded_blocks / Math.max(1, d.blocks); const C = 2 * Math.PI * 90;
    const names = { asset_orchard_ingress_v2: 'Deposits into the pool', shielded_swap_v1: 'Private swaps', asset_orchard_private_egress_v1: 'Private withdrawals', asset_orchard_private_primary_issue_v1: 'Private NAVCoin creations', asset_orchard_private_primary_redeem_v1: 'Private cash-ins', asset_orchard_egress_v1: 'Withdrawals' };
    return `<section class="ex-night"><div class="wrap">
      <div class="dialrow"><svg class="dial" viewBox="0 0 220 220" role="img" aria-label="${(share * 100).toFixed(1)} percent of blocks are private"><circle class="bg" cx="110" cy="110" r="90"/><circle class="fg" cx="110" cy="110" r="90" stroke-dasharray="${C.toFixed(1)}" stroke-dashoffset="${(C * (1 - share)).toFixed(1)}"/><text x="110" y="122" text-anchor="middle">${(share * 100).toFixed(1)}%</text><text class="cap" x="110" y="146" text-anchor="middle">OF BLOCKS</text></svg>
      <div><span class="label">Devnet · private</span><h1 class="display d-l" style="margin-top:14px">${num(d.shielded_blocks)} of ${num(d.blocks)} blocks are sealed.</h1><p class="sub lede" style="margin-top:18px">A private action proves it is valid without saying what it is. This page shows exactly what the ledger publishes for each one, and names what it keeps sealed.</p>
      <div class="chips">${d.kinds.map((k) => `<span class="chip" style="color:var(--night-ink);border-color:var(--night-rule)">${esc(names[k.kind] || k.kind)} · ${k.n}</span>`).join('')}</div></div></div>
      ${section('Latest private actions', link('/stream?lens=private', `All ${num(d.kinds.reduce((n, k) => n + k.n, 0))} →`))}
      <div class="sealed-grid">${collapse(d.ops).map((o) => `<div class="sealed"><a class="rowlink" href="#/${o.count > 1 ? 'stream?lens=private' : 'tx/' + esc(o.id)}" aria-label="Open"></a><div class="h">${o.count > 1 ? `Blocks ${num(o.first)}–${num(o.height)} · ${o.count} ${esc((names[o.kind] || o.kind).toLowerCase())}` : `Block ${num(o.height)} · ${esc(names[o.kind] || o.kind)}`} · ${when(o.time)}</div><div class="s">${sent(o)}</div><div class="ps"><div><b>Public</b>${(o.privacy?.public || []).map((x) => `<span>${esc(x)}</span>`).join('')}</div><div><b>Not published</b>${(o.privacy?.sealed || []).map((x) => `<span>${esc(x)}</span>`).join('')}</div></div></div>`).join('')}</div>
    </div></section>`;
  }

  async function journeys(q) {
    const kind = q.get('kind') || ''; const d = await get(`/journeys?kind=${kind}`);
    return page(head('Devnet', 'Journeys', 'One thing a person did, across every step it took. A deposit is a transaction on Ethereum and three operations here; it reads as one line.') +
      `<ul class="key"><li><span class="mark done"><i></i></span>Done on this network</li><li><span class="mark unknown"><i></i></span>On Ethereum, not read by the explorer</li><li><span class="mark pending"><i></i></span>Waiting</li><li><span class="mark rejected"><i></i></span>Refused</li></ul>` +
      `<div class="chips"><a class="chip" href="#/journeys" aria-current="${!kind}">All</a>${Object.entries(JOURNEY).map(([k, v]) => `<a class="chip" href="#/journeys?kind=${k}" aria-current="${kind === k}">${esc(v)}${d.counts[k] ? ' · ' + d.counts[k] : ''}</a>`).join('')}</div>
      <table class="ledger tight"><thead><tr><th>Blocks</th><th>When</th><th>Journey</th><th>What happened</th><th>Steps</th><th>State</th></tr></thead><tbody>
      ${d.journeys.map((j) => `<tr><td>${num(j.first_height)}${j.last_height !== j.first_height ? '–' + num(j.last_height) : ''}</td><td>${when(j.time)}</td><td>${link(`/journey/${j.kind}/${j.key}`, esc(JOURNEY[j.kind]), 'lk')}</td><td>${esc(j.headline)}</td><td>${dots(j.steps)}</td><td>${j.summary === 'rejected' ? '<span class="tag rej">Refused</span>' : j.summary === 'in progress' ? '<span class="tag demo">In progress</span>' : `<span class="quiet">${j.summary === 'complete' ? 'Complete' : 'Done here'}</span>`}</td></tr>`).join('')}
      </tbody></table><p class="ex-note">"Done here" means every step on this network is done. Steps on Ethereum are not read by this build, so they are never shown as done.</p>`);
  }
  async function journeyPage(kind, key) {
    const j = await get(`/journey/${kind}/${key}`); if (!j) return notFound('No journey with that key.');
    return page(head(`Devnet · journey · ${esc(JOURNEY[kind] || kind)}`, esc(j.headline), `Blocks ${num(j.first_height)} to ${num(j.last_height)}. State: ${esc(j.summary)}.`, '', 'sentence') + journeyPanel(j).replace(/<a href="#\/journey[^>]*>Open journey →<\/a>/, '') +
      section('Operations in this journey') + `<ul class="stream">${j.ops.map((o) => opLine(o)).join('')}</ul><div class="kv" style="margin-top:28px"><div>Journey key</div><div>${hashRow(j.key)}</div></div>`);
  }

  async function network() {
    const d = await get('/network');
    return page(head('Devnet', 'Network', `Six validators take turns proposing. Running build ${esc(d.status.build_git_revision || '–')}.`) +
      section('Validators') + `<table class="ledger tight"><thead><tr><th>Validator</th><th class="r">Blocks proposed</th><th class="r">Votes in the last 300 blocks</th><th class="r">Last proposed</th></tr></thead><tbody>${d.validators.map((v) => `<tr><td>${esc(v.proposer)}${v.low ? ' <span class="tag rej">Fewer votes</span>' : ''}</td><td class="r num">${num(v.proposed)}</td><td class="r num">${num(v.votes_last_300)}</td><td class="r">${link(`/block/${v.last}`, num(v.last))}</td></tr>`).join('')}</tbody></table>` +
      `<p class="ex-note">${d.validators.some((v) => v.low) ? 'A validator marked "fewer votes" has recorded under four fifths of the typical number of votes in the last 300 blocks. Blocks still need five of six.' : 'All six validators have voted at a similar rate over the last 300 blocks.'}</p>` + section('Rule changes and governance') + `<ul class="stream">${d.governance.map((o) => opLine(o)).join('')}</ul>`);
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
