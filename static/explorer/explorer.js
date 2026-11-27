/* Post Fiat Explorer. One file, no framework. All state lives in the URL hash. */
(() => {
  const root = document.getElementById('ex');
  if (!root) return;
  const C = window.PFTExplorerContracts || {};
  const API = (root.dataset.api || '/api/explorer/v1').replace(/\/$/, '');
  const LENS = {
    bridge: 'Bridge',
    payments: 'Payments',
    navmarket: 'Coin market',
    private: 'Private',
    navchecks: 'NAV checks',
    market: 'Swaps',
    fastlane: 'Fast lane',
    network: 'Network',
    messages: 'Messages',
    nfts: 'NFTs',
    identity: 'Identity',
  };
  const JOURNEY = { deposit: 'USDC deposit', withdrawal: 'USDC withdrawal', create: 'NAVCoin creation', export: 'Bridge to Ethereum', return: 'Return from Ethereum' };
  const LINK_LABELS = {
    validator_node: 'Validator node',
    old_chain_account: 'Old-chain wallet',
    agent_controller: 'Human controller',
    custom_nip05: 'Custom NIP-05',
    evm_address: 'EVM address',
    solana_address: 'Solana address',
  };
  const GOV_STATE_LABELS = {
    SESSION_STATE_DRAFT: 'Draft',
    SESSION_STATE_LIVE: 'Live',
    SESSION_STATE_FROZEN: 'Frozen',
    SESSION_STATE_IN_REVIEW: 'In review',
    SESSION_STATE_ANCHORING: 'Anchoring',
    SESSION_STATE_PUBLISHED: 'Published',
    SESSION_STATE_ABORTED: 'Aborted',
    SESSION_STATE_RULING_PENDING: 'Ruling pending',
    SESSION_STATE_RULING_ANCHORED: 'Ruling anchored',
    draft: 'Draft', live: 'Live', frozen: 'Frozen', in_review: 'In review',
    anchoring: 'Anchoring', published: 'Published', aborted: 'Aborted',
    ruling_pending: 'Ruling pending', ruling_anchored: 'Ruling anchored',
  };
  const DELIV_STATUS = {
    DELIVERABLE_STATUS_DONE: ['Done', 'done'],
    DELIVERABLE_STATUS_IN_PROGRESS: ['In progress', 'lvl'],
    DELIVERABLE_STATUS_NOT_DONE: ['Not done', 'rej'],
    DELIVERABLE_STATUS_DROPPED: ['Dropped', 'part'],
    done: ['Done', 'done'],
    in_progress: ['In progress', 'lvl'],
    not_done: ['Not done', 'rej'],
    dropped: ['Dropped', 'part'],
  };
  let meta = null, timer = null, lastTop = null, seq = 0;

  // ── helpers ────────────────────────────────────────────────────────────────
  const esc = (v) => (C.escHtml ? C.escHtml(v) : String(v ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])));
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
  const whenMs = (ms) => (ms ? when(Number(ms) / 1000) : '');
  const link = (route, text, cls = '') => `<a href="#${route}"${cls ? ` class="${cls}"` : ''}>${text}</a>`;
  const addr = (a, label) => (a ? (label ? `${esc(label)} ` : '') + link(`/account/${a}`, esc(a), 'hash lk') : '–');
  const sent = (o) => { let h = esc(o.sentence); for (const a of o.addrs || []) { const tok = esc(`${a.slice(0, 8)}…${a.slice(-4)}`); if (!h.includes(tok)) continue; h = h.split(tok).join(a.startsWith('pf') ? `<a class="ad" href="#/account/${esc(a)}" title="${esc(a)}">${tok}</a>` : `<a class="ad" href="https://etherscan.io/address/${esc(a)}" target="_blank" rel="noopener" title="${esc(a)}">${tok}</a>`); } return h; };
  const resultTag = (o, always) => o.accepted === false ? `<span class="tag rej" title="${esc(o.code || '')}">Rejected</span>` : o.code === 'filled' ? '<span class="tag fill">Filled</span>' : o.accepted == null ? '<span class="tag prop">No receipt</span>' : always ? '<span class="tag ok">Accepted</span>' : '';
  const levelTag = (e) => `<span class="tag ${e === 'disputed' ? 'rej' : 'lvl'}" title="How far the explorer has checked this record">${esc(e === 'cross-checked' ? 'Cross-checked' : e === 'disputed' ? 'Disputed' : e === 'linked to parent' ? 'Linked to parent' : 'Reported')}</span>`;
  const copyBtn = (v) => `<button class="copy" data-copy="${esc(v)}">Copy</button>`;
  const hashRow = (v) => (v ? `<span class="hash" title="${esc(v)}">${esc(v)}</span>${copyBtn(v)}` : '<span class="muted">–</span>');
  const etherscan = (e) => { if (!e || !e.tx) return ''; const h = e.tx.startsWith('0x') ? e.tx : '0x' + e.tx; const base = { 1: 'https://etherscan.io', 11155111: 'https://sepolia.etherscan.io', 42161: 'https://arbiscan.io' }[e.chain_id] || 'https://etherscan.io'; return `<a class="hash" href="${base}/tx/${esc(h)}" rel="noopener" target="_blank">${short(h, 10, 6)} ↗</a>`; };
  const seals = (block, small) => { const voted = new Set((block.header?.votes || []).map((v) => v.validator)); const all = block.header?.validators || [...voted]; return `<span class="marks${small ? ' small' : ''}">${all.map((v) => `<span class="mark${voted.has(v) ? ' done' : ' none'}${v === block.proposer ? ' prop' : ''}" title="${esc(v)}${voted.has(v) ? ': recorded accepting vote' : ': no vote recorded'}${v === block.proposer ? ' (proposer)' : ''}"><i></i>${small ? '' : `<b>${esc(v.replace('validator-', 'v'))}</b><em>${v === block.proposer ? 'proposed' : voted.has(v) ? 'voted' : 'no vote'}</em>`}</span>`).join('')}</span>`; };
  const STEP = { done: 'done', unknown: 'on Ethereum, not read', pending: 'waiting', 'not-started': 'not started', rejected: 'refused', mismatched: 'mismatch', 'no receipt': 'no receipt', released: 'released' };
  const dots = (steps) => `<span class="marks small">${steps.map((s) => `<span class="mark ${esc(s.state)}" title="${esc(s.label)}: ${esc(STEP[s.state] || s.state)}"><i></i></span>`).join('')}</span>`;
  const spark = (vals) => { vals = (vals || []).map(Number).filter((v) => isFinite(v) && v > 0); if (vals.length < 2) return '<svg class="spark" viewBox="0 0 120 30"><path d="M2 15H118"/></svg>'; const last = vals[vals.length - 1]; const half = Math.max(last * 0.005, Math.max(...vals.map((v) => Math.abs(v - last))) * 1.15); const lo = last - half, sp = 2 * half; const pt = (v, i) => [2 + (116 * i) / (vals.length - 1), 26 - (22 * (v - lo)) / sp]; const d = vals.map((v, i) => `${i ? 'L' : 'M'}${pt(v, i).map((n) => n.toFixed(1)).join(' ')}`).join(''); const [lx, ly] = pt(last, vals.length - 1); return `<svg class="spark" viewBox="0 0 120 30" aria-hidden="true"><path d="${d}"/><circle cx="${lx.toFixed(1)}" cy="${ly.toFixed(1)}" r="2.2"/></svg>`; };
  const json = (o) => esc(JSON.stringify(o, null, 2)).replace(/&quot;([a-zA-Z0-9_]+)&quot;:/g, '<span class="k">&quot;$1&quot;</span>:');

  let coinPrec = null;
  const coinPrecisions = () => (coinPrec ??= get('/coins').then((d) => Object.fromEntries((d?.coins || []).map((c) => [c.asset_id, c.precision]))).catch(() => ({})));

  async function get(path) {
    const res = await fetch(API + path, { cache: 'no-store' });
    const body = await res.json().catch(() => ({}));
    if (body.meta) { meta = body.meta; pulse(true); }
    if (res.status === 404) return null;
    if (!res.ok || !body.ok) throw new Error('The explorer service did not answer.');
    return body.data;
  }
  async function getOptional(path) {
    try { return await get(path); } catch { return null; }
  }
  function pulse(ok) {
    const el = document.getElementById('ex-pulse'); if (!el) return;
    if (!ok || !meta) { el.className = 'ex-pulse stale'; el.innerHTML = '<span class="dot"></span>Explorer service unreachable. Showing the last data.'; return; }
    const behind = meta.chain_height - meta.index_height;
    el.className = 'ex-pulse' + (behind > 2 ? ' behind' : '');
    el.innerHTML = `<span class="dot"></span>Index at <b>${num(meta.index_height)}</b> · chain at <b>${num(meta.chain_height)}</b>${behind > 2 ? ` · ${behind} blocks behind` : ''}`;
  }
  const msgBadgeForOp = (o) => {
    if (!o.message) return '';
    const b = C.classifyMessageBadge ? C.classifyMessageBadge(o.message) : { label: 'Message', cls: 'ok' };
    return `<span class="tag ${esc(b.cls)}" title="${b.is_task_reward ? 'Verified official Task Node payout key' : esc(b.label)}">${esc(b.label)}</span>`;
  };
  const opLine = (o, isNew) => `<li class="${isNew ? 'new' : ''}${o.accepted === false ? ' rejected' : ''}"><a class="rowlink" href="#/tx/${esc(o.id)}" aria-label="Open operation in block ${o.height}"></a><span class="h">${o.count > 1 ? `${num(o.first)}–${num(o.height)}` : num(o.height)}<small>${when(o.time)}</small></span><span class="s">${sent(o)}${o.count > 1 ? ` <span class="times">× ${o.count}</span>` : ''}<small>${esc(LENS[o.lens] || o.lens)}${o.journey ? ' · ' + esc(JOURNEY[o.journey.kind] || '') : ''}${o.order_hash ? ' · FastPay' : ''}</small></span><span class="st">${o.message ? msgBadgeForOp(o) : o.lens === 'private' ? '<span class="tag sealed">Sealed</span>' : resultTag(o)}</span><span class="go" aria-hidden="true">→</span></li>`;
  const collapse = (ops) => { const out = []; for (const o of ops) { const last = out[out.length - 1]; if (last && last.sentence === o.sentence && last.accepted === o.accepted && !o.message && (last.first - o.height === 1 || o.lens === 'private')) { last.count += 1; last.first = o.height; } else out.push({ ...o, count: 1, first: o.height }); } return out; };
  const head = (label, title, sub, extra = '', cls = '') => `<header class="ex-head"><span class="label">${label}</span><h1 class="${cls}">${title}</h1>${sub ? `<p class="sub">${sub}</p>` : ''}${extra}</header>`;
  const section = (title, more = '') => `<div class="ex-h2"><h2>${title}</h2>${more}</div>`;
  const page = (html, flush) => `<div class="wrap ex-page${flush ? ' flush' : ''}">${html}</div>`;
  const checkPanel = (evidence, call, what) => `<div class="verify"><span class="label"><b>Check it yourself</b> · evidence level: ${esc(evidence === 'cross-checked' ? 'cross-checked' : evidence || 'reported')}</span>
    <div>${evidence === 'cross-checked' ? 'Two validators report the same block hash and state root. That detects a validator answering differently from another.' : evidence === 'disputed' ? 'Two validators answered differently for this block.' : evidence === 'linked to parent' ? 'Read from one validator. Its parent hash matches the block before it; no second validator was compared.' : 'Read from one validator.'} It does not by itself establish that the certificate is valid. Sent to any validator, this call ${what}:</div><code>${esc(call)}</code></div>`;

  // ── shared Wave 1 protocol panels (Messages, Identity, NFTs) ───────────────
  function renderMessagePanel(m, opts = {}) {
    if (!m) return '';
    const badge = C.classifyMessageBadge ? C.classifyMessageBadge(m) : { label: 'Message', cls: 'ok', visibility: 'unknown', sender_verified: false, is_task_reward: false };
    const cid = m.cid_multibase || m.pointer?.cid_multibase || '';
    const schema = m.schema_name || m.header?.schema_name || '';
    const kindCode = m.content_kind ?? m.pointer?.content_kind ?? m.header?.content_kind;
    const kindName = C.CONTENT_KIND_LABELS?.[kindCode] || (kindCode != null ? `Kind ${kindCode}` : '–');
    const isEncrypted = badge.visibility === 'private' || badge.visibility === 'sealed';
    const orderHash = m.order_hash || m.fastpay?.order_hash || '';
    const certDigest = m.certificate_digest || m.fastpay?.certificate_digest || '';

    let bodyHtml = '';
    if (isEncrypted) {
      bodyHtml = `<div class="msg-sealed-note">
        <span class="tag ${esc(badge.cls)}">${esc(badge.label)}</span>
        ${badge.is_task_reward ? '<span class="tag lvl">Official Task Node payout key</span>' : ''}
        ${badge.spoofed_reward ? '<span class="tag prop">Unrecognized reward sender — shown as private message</span>' : ''}
        <p>${badge.visibility === 'sealed'
          ? 'Encrypted with X-Wing (X25519 + ML-KEM-768) + XChaCha20-Poly1305 with recipient-anonymous header. The explorer never touches private keys.'
          : 'Encrypted with X-Wing (X25519 + ML-KEM-768) + XChaCha20-Poly1305. Decryption happens strictly locally in your Task Node wallet or Mac app — never on the explorer.'}</p>
        ${m.thread_id || m.task_id ? `<div class="msg-meta-row">${m.task_id ? `<span>Task: <b class="mono">${esc(m.task_id)}</b></span>` : ''}${m.thread_id ? `<span>Thread: <b class="mono">${esc(m.thread_id)}</b></span>` : ''}</div>` : ''}
      </div>`;
    } else if (m.envelope_unavailable) {
      bodyHtml = `<div class="msg-warn">Envelope not available on IPFS gateway. The on-chain pointer CID is intact; retry later or fetch directly from a pinning node.</div>`;
    } else if (m.public_body != null || m.body_text != null) {
      const text = typeof m.public_body === 'object' ? JSON.stringify(m.public_body, null, 2) : String(m.public_body ?? m.body_text ?? '');
      const trunc = C.truncatePublicPreview ? C.truncatePublicPreview(text) : { text, truncated: false, total_chars: text.length };
      bodyHtml = `<pre class="msg-body">${esc(trunc.text)}</pre>${trunc.truncated ? `<p class="ex-note">Display capped at 64 KiB (${num(trunc.total_chars)} bytes total) for browser safety.</p>` : ''}`;
    } else {
      bodyHtml = `<p class="ex-note">On-chain <code>pf.ptr</code> ${esc(m.pointer_version || 'v5')} pointer recorded. Fetch the raw CIDv1 block to inspect the full envelope.</p>`;
    }

    const mediaHtml = (m.media || []).length ? `<div class="msg-media">${m.media.map((att, idx) => {
      const gw = C.safeIpfsGatewayUrl ? C.safeIpfsGatewayUrl(att.uri) : null;
      return `<div class="msg-media-item"><span>${esc(att.mime_type || 'attachment')} · ${att.byte_length ? num(att.byte_length) + ' B' : esc(att.uri || '')}</span>${gw ? `<button type="button" class="btn sm" data-load-media="${esc(gw)}" data-media-id="m-${idx}">Load media on click</button>` : '<span class="quiet">External media blocked</span>'}</div>`;
    }).join('')}</div>` : '';

    return `<div class="proto-card msg-card">
      <div class="proto-head">
        <div class="proto-badges">
          <span class="tag ${esc(badge.cls)}">${esc(badge.label)}</span>
          ${badge.sender_verified ? '<span class="tag lvl">Verified sender</span>' : '<span class="tag part">Sender not checked</span>'}
          ${m.pointer_version === 'v4' ? '<span class="tag prop">Legacy pf.ptr v4</span>' : '<span class="tag ok">pf.ptr v5</span>'}
          ${m.cipher_suite ? `<span class="tag ok">${esc(m.cipher_suite)}</span>` : ''}
        </div>
        ${!opts.hideLink && m.id ? link(`/message/${esc(m.id)}`, 'Inspect message →', 'lk mono') : ''}
      </div>
      ${bodyHtml}
      ${mediaHtml}
      <div class="kv compact">
        <div>Schema &amp; kind</div><div><span class="mono">${esc(schema || '–')}</span> · ${esc(kindName)}</div>
        <div>Visibility</div><div>${esc(badge.visibility)}</div>
        ${cid ? `<div>Envelope CID (CIDv1 raw)</div><div>${hashRow(cid)}</div>` : ''}
        ${m.sender_account ? `<div>Envelope sender</div><div>${addr(m.sender_account)}</div>` : ''}
        ${orderHash ? `<div>FastPay order hash</div><div>${hashRow(orderHash)}</div>` : ''}
        ${certDigest ? `<div>FastPay certificate digest</div><div><span class="hash" title="${esc(certDigest)}">${short(certDigest, 16, 8)}</span>${copyBtn(certDigest)} <span class="quiet">(informational)</span></div>` : ''}
      </div>
    </div>`;
  }

  function renderIdentityCard(id, extra = {}) {
    if (!id) return '';
    const fullHandle = id.handle ? `${id.handle}@${id.registered_namespace || 'tasknode.postfiat.org'}` : null;
    const { consensusVerified, clientVerified } = C.classifyIdentityLinks
      ? C.classifyIdentityLinks(id.links || [], extra.validatorStates)
      : { consensusVerified: [], clientVerified: [] };
    const linkRow = (l) => `<tr>
      <td><b>${esc(LINK_LABELS[l.kind] || l.kind)}</b>${l.pending_reconfirmation ? ' <span class="tag prop">Pending re-confirmation</span>' : ''}${l.stale_validator ? ` <span class="tag rej">Validator ${esc(l.validator_state || 'stale')}</span>` : ''}</td>
      <td>${l.kind === 'agent_controller' && /^pf[0-9a-f]{40}$/.test(l.target) ? addr(l.target) : `<span class="hash">${esc(l.target)}</span>${copyBtn(l.target)}`}</td>
      <td class="r num">${l.linked_at_height ? link(`/block/${l.linked_at_height}`, num(l.linked_at_height)) : '–'}</td>
    </tr>`;
    return `<div class="proto-card id-card">
      <div class="proto-head">
        <div>
          <span class="label">On-chain Identity · ${esc(id.identity_kind || 'human')} · seq ${num(id.sequence)}</span>
          <h2 class="id-title">${fullHandle ? esc(fullHandle) : esc(id.account)}</h2>
        </div>
        <div class="proto-badges">
          <span class="tag ${id.status === 'revoked' ? 'rej' : 'lvl'}">${id.status === 'revoked' ? 'Revoked' : 'Minted on chain'}</span>
          <span class="tag ok">Nostr v${esc(id.derivation_version || 2)} · idx ${esc(id.key_index ?? 0)}</span>
          ${extra.linkToCard ? link(`/identity/${encodeURIComponent(fullHandle || id.account)}`, 'Open Identity Card →', 'lk mono') : ''}
        </div>
      </div>
      ${extra.compromised_nostr_pubkey ? '<div class="ex-banner">This Nostr public key is tombstoned as compromised on chain and can never be rebound.</div>' : ''}
      ${id.status === 'revoked' ? `<div class="ex-banner">Identity revoked${id.revoked_at_height ? ` at block ${num(id.revoked_at_height)}` : ''}. Hive badges are stripped from all events not anchored before revocation.</div>` : ''}
      <div class="kv compact">
        <div>L1v2 account</div><div>${addr(id.account)}</div>
        <div>Nostr pubkey (x-only)</div><div>${hashRow(id.nostr_pubkey)}</div>
        ${fullHandle ? `<div>Registered handle</div><div class="mono">${esc(fullHandle)}</div>` : ''}
        ${id.avatar_nft_id ? `<div>Profile NFT avatar</div><div>${link(`/nft/${esc(id.avatar_nft_id)}`, esc(id.avatar_nft_id), 'hash lk')}</div>` : ''}
        ${id.message_key ? `<div>X-Wing message key</div><div><span class="hash" title="${esc(id.message_key)}">${short(id.message_key, 18, 10)}</span>${copyBtn(id.message_key)} <span class="quiet">1,216 B post-quantum KEM</span></div>` : ''}
        ${id.pq_receive_address ? `<div>Shielded receive address</div><div>${hashRow(id.pq_receive_address)}</div>` : ''}
        ${(id.relays || []).length ? `<div>Relays</div><div>${id.relays.map((r) => `<span class="tag ok">${esc(r)}</span>`).join(' ')}</div>` : ''}
        <div>Minted / updated</div><div class="num">Block ${id.created_at_height ? link(`/block/${id.created_at_height}`, num(id.created_at_height)) : '–'} · updated ${id.updated_at_height ? link(`/block/${id.updated_at_height}`, num(id.updated_at_height)) : '–'}</div>
      </div>
      <h3 class="subhead">Consensus-verified links (${consensusVerified.length})</h3>
      ${consensusVerified.length
        ? `<table class="ledger tight"><thead><tr><th>Link</th><th>Target</th><th class="r">Block</th></tr></thead><tbody>${consensusVerified.map(linkRow).join('')}</tbody></table>`
        : '<p class="ex-note">No consensus-verified validator, old-chain, or controller links attached.</p>'}
      <h3 class="subhead">Client-verified claims (${clientVerified.length})</h3>
      ${clientVerified.length
        ? `<p class="ex-note">Non-unique claims verified by clients against DNS / <code>nostr.json</code> or external wallet signatures — never enforced unique by consensus.</p><table class="ledger tight dim"><thead><tr><th>Claim</th><th>Target</th><th class="r">Block</th></tr></thead><tbody>${clientVerified.map(linkRow).join('')}</tbody></table>`
        : '<p class="ex-note">No custom NIP-05, EVM, or Solana client-verified claims attached.</p>'}
      ${(extra.registrar_history || []).length ? `<h3 class="subhead">Registrar history &amp; pending reassignments</h3>
        <table class="ledger tight"><thead><tr><th>Handle</th><th>Reason</th><th>State</th><th class="r">Effective block</th></tr></thead><tbody>
        ${extra.registrar_history.map((r) => `<tr><td class="mono">${esc(r.handle)}@${esc(r.namespace)}</td><td>${esc(r.reason_code)}${r.emergency_compromise ? ' <span class="tag rej">Emergency</span>' : ''}</td><td><span class="tag ${r.state === 'canceled' ? 'part' : r.state === 'executed' ? 'done' : 'prop'}">${esc(r.state)}</span></td><td class="r num">${num(r.effective_at_height)}</td></tr>`).join('')}
        </tbody></table>` : ''}
    </div>`;
  }

  function renderNftTile(n) {
    const col = C.formatNftCollectionIdentity ? C.formatNftCollectionIdentity(n) : { display_pair: n.collection_id || '', issuer: n.issuer || '' };
    const ver = C.nftVerificationSummary ? C.nftVerificationSummary(n) : { label: 'Metadata not checked', cls: 'part' };
    const orig = C.nftOriginBadge ? C.nftOriginBadge(n.origin || n.metadata?.origin) : { label: 'Native L1v2 mint', cls: 'ok' };
    const migrated = C.isMigratedNftSerial ? C.isMigratedNftSerial(n.serial) : false;
    const title = n.metadata?.name || n.name || `NFT #${short(String(n.serial ?? n.nft_id), 8, 4)}`;
    return `<a class="nft" href="#/nft/${esc(n.nft_id)}">
      <div class="plate"><span>${esc(title.slice(0, 2).toUpperCase())}</span></div>
      <div class="nft-title">${esc(title)}</div>
      <div class="nft-tags"><span class="tag ${esc(ver.cls)}">${esc(ver.label)}</span><span class="tag ${esc(orig.cls)}">${esc(orig.label)}</span>${n.burned ? '<span class="tag rej">Burned</span>' : ''}${migrated ? '<span class="tag ok">Bit-63 serial</span>' : ''}</div>
      <div class="t">Collection: ${esc(col.collection_id || '–')}<br>Issuer: ${esc(col.issuer || '–')}</div>
    </a>`;
  }

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
      <div class="lenses" role="group" aria-label="Filter by lens">${d.lenses.map((l) => `<button data-lens="${l.lens}" aria-pressed="${lens === l.lens}" title="${num(l.count)} of ${num(d.ops)} operations (${((100 * l.count) / d.ops).toFixed(0)}%)"><span class="v num">${num(l.count)}</span><span class="k">${esc(LENS[l.lens] || l.lens)}</span><span class="bar"><i style="width:${Math.max(3, (100 * l.count) / max).toFixed(1)}%"></i></span><span class="cta">${lens === l.lens ? 'Clear filter ×' : 'Filter →'}</span></button>`).join('')}</div>
      <div class="cols">
        <div>${section(lens ? esc(LENS[lens] || lens) : 'Latest operations', link(`/stream${lens ? `?lens=${lens}` : ''}`, 'All →'))}<ul class="stream" id="ex-stream">${stream.map((o, i) => opLine(o, fresh && i === 0)).join('') || '<li class="ex-empty">Nothing yet.</li>'}</ul></div>
        <div>${section('Latest blocks', link('/blocks', 'All →'))}
          <ul class="rows">${d.latest_blocks.slice(0, 6).map((b) => `<li><a class="rowlink" href="#/block/${b.height}" aria-label="Block ${b.height}"></a><span class="a">${num(b.height)}</span><span class="b">${esc(b.proposer)}<small>${b.n_ops} ${esc(b.kind)} op${b.n_ops === 1 ? '' : 's'}</small></span><span class="c">${seals({ header: { votes: [], validators: [] }, proposer: '' }, true)}${b.votes}/6 · ${when(b.time)}</span></li>`).join('')}</ul>
          ${section('NAVCoins', link('/coins', 'All →'))}
          <ul class="rows">${d.coins.filter((c) => c.listed).map((c) => `<li><a class="rowlink" href="#/coin/${esc(c.asset_id)}" aria-label="${esc(c.code)}"></a><span class="a">${esc(c.code)}</span><span class="b">${usd(c.nav_per_unit, c.nav_decimals, 6)}${c.retired ? ' · retired' : ''}</span><span class="c">${spark(c.spark)}</span></li>`).join('')}</ul>
          ${section('Latest journeys', link('/journeys', 'All →'))}
          <ul class="rows">${(d.latest_journeys || []).map((j) => `<li><a class="rowlink" href="#/journey/${j.kind}/${esc(j.key)}" aria-label="${esc(JOURNEY[j.kind])}"></a><span class="a">${dots(j.steps)}</span><span class="b">${esc(j.headline)}</span><span class="c"><small>${when(j.time)}</small></span></li>`).join('')}</ul>
          ${section('Protocol lenses', '<span class="hint">Phase 0 contracts</span>')}
          <ul class="rows">
            <li><a class="rowlink" href="#/messages" aria-label="Messages"></a><span class="a">pf.ptr v5</span><span class="b">Messages &amp; FastPay Task Rewards<small>Spoof-proof payout badges · X-Wing encrypted</small></span><span class="c">→</span></li>
            <li><a class="rowlink" href="#/governance" aria-label="Governance Archive"></a><span class="a">Hive Gov</span><span class="b">Governance Archive<small>Snapshots · Transcripts · Pass 1/2 Minutes · Rulings</small></span><span class="c">→</span></li>
            <li><a class="rowlink" href="#/nfts" aria-label="NFTs"></a><span class="a">PQ NFTs</span><span class="b">Post-Quantum NFTs<small>SHA3-384 one-hash metadata · Burn-first provenance</small></span><span class="c">→</span></li>
            <li><a class="rowlink" href="#/identities" aria-label="Identity Cards"></a><span class="a">Identity</span><span class="b">Hive Identity Cards<small>On-chain npub · @tasknode handles · Linked keys</small></span><span class="c">→</span></li>
          </ul>
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

  function journeyPanel(j) {
    if (!j) return '';
    return section(esc(JOURNEY[j.kind] || 'Journey'), link(`/journey/${j.kind}/${j.key}`, 'Open journey →')) +
      `<div class="journey">${j.steps.map((s) => `<div class="jstep ${esc(s.state)}"><span class="mark ${esc(s.state)}"><i></i></span><div class="l">${esc(s.label)}</div><div class="n">${
        s.state === 'done' ? `Done · ${s.op ? link(`/tx/${s.op}`, 'block ' + num(s.height)) : `on Ethereum${s.eth?.block ? ', block ' + num(s.eth.block) : ''}<br>${etherscan(s.eth)}`}${s.time ? '<br>' + when(s.time) : ''}` : s.state === 'rejected' ? `Rejected · ${link(`/tx/${s.op}`, esc(s.code || ''))}` : s.state === 'unknown' ? `Not checked${s.eth ? '<br>' + etherscan(s.eth) : ''}` : s.state === 'pending' ? 'Pending' : s.state === 'not-started' ? 'Not started' : `${esc((STEP[s.state] || s.state).replace(/^./, (c) => c.toUpperCase()))}${s.op ? ' · ' + link(`/tx/${s.op}`, 'block ' + num(s.height)) : ''}`}</div></div>`).join('')}</div>
      ${j.trip?.sentence ? `<p class="ex-note"><b>${esc(j.trip.sentence)}</b></p>` : ''}<p class="ex-note">${ethNote(j.steps)}</p>`;
  }
  const ethNote = (steps) => { const open = steps.filter((s) => s.state === 'unknown'); if (!open.length) return ''; return open.some((s) => !s.note || /not read by this build/.test(s.note)) ? 'This build does not read Ethereum. Ethereum steps show "not checked", and any hash shown is the one the network recorded, not a confirmation.' : open.map((s) => esc(s.note)).join(' '); };

  async function tx(id) {
    const d = await get(`/tx/${id}`); if (!d) return notFound('No operation with that ID.');
    const o = d.op, b = d.block, raw = o.raw?.unsigned || o.raw || {};
    const precs = o.asset_precision || await coinPrecisions();
    const prec = (k) => { const base = k.replace(/(_?amount)?(_atoms)?$/, ''); const id = raw[base ? `${base}_asset_id` : 'asset_id'] || raw.asset_id || (o.assets?.length === 1 ? o.assets[0] : null); return precs[id] ?? 6; };
    const skip = new Set(['chain_id', 'genesis_hash', 'protocol_version', 'address_namespace', 'signature_algorithm_id', 'transaction_kind', 'fee']);
    const val = (k, v) => {
      if (v == null || v === '') return '<span class="muted">–</span>';
      if (typeof v === 'object') return `<span class="mono">${esc(JSON.stringify(v)).slice(0, 600)}</span>`;
      const sv = String(v);
      if (/^pf[0-9a-f]{40}$/.test(sv)) return addr(sv, o.party_labels?.[sv]);
      if (k.endsWith('asset_id') && sv.length === 96) return `${link(`/coin/${sv}`, esc(o.asset_names?.[sv] || 'asset'))} <span class="hash">${short(sv, 10, 6)}</span>`;
      if (k === 'nft_id' && sv.length === 96) return link(`/nft/${sv}`, esc(sv), 'hash lk');
      if (/_hash$|_root$|_id$|nonce|digest|commitment|nullifier|anchor/.test(k) && sv.length > 30) return `<span class="hash" title="${esc(sv)}">${short(sv, 16, 8)}</span>${copyBtn(sv)}`;
      if (/atoms$|^amount$|_amount$/.test(k) && /^\d+$/.test(sv)) return `<span class="num">${units(sv, prec(k), prec(k))}</span><span class="sub2">${num(sv)} atoms, the ledger's smallest unit</span>`;
      if (k === 'fee') return `<span class="num">${num(sv)}</span> atoms of PFT`;
      return esc(sv);
    };
    const byAddr = new Map(); for (const p of o.parties || []) byAddr.set(p.address, [...(byAddr.get(p.address) || []), p.role]);
    const grouped = [...byAddr.entries()];
    const partyKeys = new Set((o.parties || []).map((p) => p.role));
    const fields = Object.entries(raw).filter(([k, v]) => !skip.has(k) && !(partyKeys.has(k) && typeof v === 'string' && v.startsWith('pf'))).map(([k, v]) => `<div>${esc(k.replace(/_atoms$/, '').replace(/_/g, ' '))}</div><div>${val(k, v)}</div>`).join('');
    const priv = o.privacy ? `${section('What the public can see')}<div class="privbox"><div class="ps"><div><b>Public</b>${o.privacy.public.map((x) => `<span>${esc(x)}</span>`).join('')}</div><div><b>Not published</b>${o.privacy.sealed.map((x) => `<span>${esc(x)}</span>`).join('')}</div></div></div>` : '';
    const rawMemos = o.memos || raw.memos || [];
    const detectedPtr = !o.message ? rawMemos.map((m) => C.detectPointerMemo && C.detectPointerMemo(m)).find(Boolean) : null;
    const msgSection = o.message
      ? section('Message pointer', link('/messages', 'All messages →')) + renderMessagePanel({ ...o.message, order_hash: o.order_hash || o.message.order_hash, certificate_digest: o.certificate_digest || o.message.certificate_digest })
      : detectedPtr
        ? section('Message pointer', link('/messages', 'All messages →')) + renderMessagePanel({ pointer_version: detectedPtr.version, visibility: 'unknown', order_hash: o.order_hash, certificate_digest: o.certificate_digest })
        : '';
    return page(head(`Devnet · ${esc(LENS[o.lens] || o.lens)} · ${esc(o.kind.replace(/_/g, ' '))}`, sent(o, true), '',
      `<div class="ex-meta">${o.message ? msgBadgeForOp(o) : ''}${o.lens === 'private' ? '<span class="tag sealed">Sealed</span>' : ''}${resultTag(o, true)}${b ? levelTag(b.evidence) : ''}<span class="label">${link(`/block/${o.height}`, 'Block ' + num(o.height), 'lk')}${b?.time ? ` · ${when(b.time)} · ${esc(utc(b.time))}` : ''}${o.fee != null ? ` · fee ${num(o.fee)} atoms of PFT` : ''}</span></div>
       <dl class="facts">${o.tx_id ? `<div><dt>${o.order_hash ? 'FastPay order hash' : 'Transaction'}</dt><dd><span class="hash" title="${esc(o.tx_id)}">${short(o.tx_id, 14, 10)}</span>${copyBtn(o.tx_id)}</dd></div>` : ''}${o.certificate_digest ? `<div><dt>Certificate digest</dt><dd><span class="hash" title="${esc(o.certificate_digest)}">${short(o.certificate_digest, 14, 10)}</span>${copyBtn(o.certificate_digest)}</dd></div>` : ''}${b ? `<div><dt>Validator votes</dt><dd><span title="Filled: recorded accepting vote. Empty: no vote recorded. Ringed: proposer.">${seals(b, true)}</span> ${b.votes} of 6, proposed by ${esc(b.proposer)}</dd></div>` : ''}</dl>
       ${o.accepted === false ? `<p class="sub ox">The network refused this operation: ${esc(o.message || o.code)}.</p>` : ''}`, 'sentence') +
      msgSection + priv + journeyPanel(d.journey) +
      (grouped.length ? section('Parties') + `<div class="kv">${grouped.map(([a, roles]) => `<div>${esc(roles.join(', ').replace(/_/g, ' '))}</div><div>${addr(a, o.party_labels?.[a])}</div>`).join('')}</div>` : '') +
      section('Fields') + `<div class="kv">${fields || '<div>Record</div><div class="muted">No labelled fields.</div>'}</div>` +
      `<details class="fold"><summary>Raw record</summary><pre class="raw">${json(o.raw)}</pre><p class="ex-note">Proofs and signatures are shortened to their first bytes and their length.</p></details>` +
      checkPanel(b?.evidence, o.tx_id ? `{"method":"tx","params":{"tx_id":"${o.tx_id}"}}` : `{"method":"blocks","params":{"from_height":${o.height},"limit":1}}`, 'returns the receipt, the block and its signed certificate'));
  }

  async function accountPage(a) {
    const [d, idRes, nftsRes] = await Promise.all([
      get(`/account/${a}`),
      getOptional(`/identity/${encodeURIComponent(a)}`),
      getOptional(`/nfts?owner=${encodeURIComponent(a)}&limit=8`),
    ]);
    if (!d) return notFound();
    const live = d.live || {};
    const held = (live.lines || []).filter((l) => Number(l.balance) > 0); const empty = (live.lines || []).length - held.length;
    const known = (l) => l.listed || (l.code === 'PFUSDC' && l.issuer === 'pf23d8831301aa1cce6fdd7bf4a2db2aead1619ba8');
    const main = held.filter(known).sort((a, b) => (a.code === 'PFUSDC') - (b.code === 'PFUSDC')), other = held.filter((l) => !known(l)); const pf = main.filter((l) => l.code === 'PFUSDC');
    const lineRow = (l) => `<tr><td>${link(`/coin/${l.asset_id}`, esc(l.code), 'lk')} ${l.listed ? '<span class="tag lvl">Listed NAVCoin</span>' : known(l) ? `<span class="tag lvl">Bridge series ${esc(l.asset_id.slice(0, 4))}</span>` : '<span class="tag prop">Unlisted</span>'} <span class="hash" title="${esc(l.asset_id)}">asset ${short(l.asset_id, 8, 4)}</span></td><td class="r num">${fixed(l.balance, l.precision)}</td></tr>`;
    const identity = d.identity || idRes?.identity || null;
    const acctNfts = d.nfts || nftsRes?.nfts || [];
    return page(head(`Devnet · account${d.label ? ' · ' + esc(d.label) : ''}`, `<span class="mono" style="font-size:.46em;letter-spacing:0">${esc(a)}</span>${copyBtn(a)}`,
      d.op_count ? `${num(d.op_count)} operation${d.op_count === 1 ? '' : 's'} since block ${num(d.first_height)}.` : 'No operations name this address yet.', '') +
      (identity ? section('On-chain Identity', link(`/identity/${encodeURIComponent(identity.handle ? `${identity.handle}@${identity.registered_namespace || 'tasknode.postfiat.org'}` : a)}`, 'Open Identity Card →')) + renderIdentityCard(identity, { linkToCard: false, compromised_nostr_pubkey: idRes?.compromised_nostr_pubkey, registrar_history: idRes?.registrar_history }) : '') +
      section('Balances') + (live.error ? `<p class="ex-note">${esc(live.error)}.</p>` : `<table class="ledger tight"><thead><tr><th>Asset</th><th class="r">Balance</th></tr></thead><tbody>
        <tr><td>PFT <span class="tag lvl">Network token</span></td><td class="r num">${fixed(live.balance, 6)}</td></tr>
        ${main.map(lineRow).join('')}${pf.length > 1 ? `<tr class="total"><td>PFUSDC across ${pf.length} bridge series</td><td class="r num">${fixed(pf.reduce((n, l) => n + Number(l.balance), 0), 6)}</td></tr>` : ''}
        </tbody></table>${other.length ? `<h3 class="subhead">Unlisted assets</h3><p class="ex-note warn">These are not listed NAVCoins or bridge PFUSDC. An unlisted asset can carry the same name as a listed one. Check the asset ID before trusting a name.</p><table class="ledger tight dim"><tbody>${other.map(lineRow).join('')}</tbody></table>` : ''}<p class="ex-note">Read from the validators at block ${num(live.read_at_height)}. Sequence ${num(live.sequence)}.${empty ? ` ${empty} line${empty === 1 ? '' : 's'} with a zero balance ${empty === 1 ? 'is' : 'are'} not shown.` : ''}</p>`) +
      (acctNfts.length ? section('NFTs held', link(`/nfts?owner=${encodeURIComponent(a)}`, `All${nftsRes?.total_count ? ' ' + num(nftsRes.total_count) : ''} →`)) + `<div class="nftgrid">${acctNfts.slice(0, 8).map(renderNftTile).join('')}</div>` : '') +
      section('Operations') + `<ul class="stream">${d.ops.map((o) => opLine(o)).join('') || '<li class="ex-empty">None.</li>'}</ul>`);
  }

  // ── Wave 1 View 1: Messages (Pillar 2 + Contract C1 & C4) ──────────────────
  async function messagesPage(q) {
    const filter = q.get('filter') || '';
    const before = q.get('before') || '';
    const d = await getOptional(`/messages?filter=${encodeURIComponent(filter)}&before=${encodeURIComponent(before)}`);
    const chips = [
      ['', 'All'],
      ['reward', 'Task rewards'],
      ['public', 'Public'],
      ['private', 'Private'],
      ['sealed', 'Sealed'],
      ['governance', 'Governance'],
      ['nft', 'NFT'],
      ['x402', 'x402'],
    ];
    const chipBar = `<div class="chips">${chips.map(([k, v]) => `<a class="chip" href="#/messages${k ? `?filter=${k}` : ''}" aria-current="${filter === k}">${esc(v)}</a>`).join('')}</div>`;
    const items = d?.messages || [];
    const listHtml = items.length
      ? `<ul class="stream">${items.map((m) => {
          const badge = C.classifyMessageBadge ? C.classifyMessageBadge(m) : { label: 'Message', cls: 'ok' };
          const idKey = m.id || m.order_hash || m.tx_id;
          const title = badge.is_task_reward
            ? `Task reward${m.amount_display ? ' · ' + esc(m.amount_display) : ''}${m.recipient_account ? ` to ${short(m.recipient_account, 8, 4)}` : ''}`
            : badge.visibility === 'public' && m.summary
              ? esc(m.summary)
              : `${esc(badge.label)}${m.schema_name ? ' · ' + esc(m.schema_name) : ''}`;
          return `<li>
            <a class="rowlink" href="#/message/${esc(idKey)}" aria-label="Open message ${esc(idKey)}"></a>
            <span class="h">${m.height ? num(m.height) : 'FastPay'}<small>${when(m.time)}</small></span>
            <span class="s">${title}<small>${esc(m.pointer_version === 'v4' ? 'pf.ptr v4' : 'pf.ptr v5')}${m.order_hash ? ' · FastPay order ' + short(m.order_hash, 10, 6) : ''}${m.cid_multibase ? ' · ' + short(m.cid_multibase, 12, 6) : ''}</small></span>
            <span class="st"><span class="tag ${esc(badge.cls)}">${esc(badge.label)}</span>${badge.sender_verified ? ' <span class="tag lvl">Verified</span>' : ''}</span>
            <span class="go" aria-hidden="true">→</span>
          </li>`;
        }).join('')}</ul><div class="pager">${d.next ? link(`/messages?filter=${encodeURIComponent(filter)}&before=${encodeURIComponent(d.next)}`, 'Older →', 'btn') : ''}</div>`
      : `<div class="proto-empty">
          <h3>${d ? 'No messages match this filter yet.' : 'Message indexing activates with L1 Upgrade Train A.'}</h3>
          <p>When FastPay (<code>owned_transfer_v3</code>) and <code>payment_v2</code> transactions carry <code>pf.ptr</code> v5 memos (<code>70662e707472</code> / <code>7635</code>), they appear here automatically keyed by immutable <code>order_hash</code> or <code>tx_id</code>.</p>
          <ul class="proto-rules">
            <li><b>Spoof-proof Task reward badge:</b> Displayed <em>only</em> when the ML-DSA-65 envelope signature verifies, matches the transaction signer, uses <code>pf.reward.v1</code> in <code>PRIVATE</code> mode, and matches the pinned official Task Node payout key. Outsider <code>pf.reward.v1</code> messages render strictly as generic <em>Private message</em>.</li>
            <li><b>Zero key risk:</b> Private and sealed payloads use X-Wing (X25519 + ML-KEM-768) + XChaCha20-Poly1305 and decrypt strictly in your local wallet or Mac app.</li>
            <li><b>Public safety:</b> Decoded text is HTML-escaped, display-capped at 64 KiB, and media loads only on click.</li>
          </ul>
        </div>`;
    return page(head('Devnet · Pillar 2', 'Messages', 'Post-quantum signed message pointers (pf.ptr v5) across FastPay payouts, public records, x402 agent payments, and legacy v4 history.') +
      chipBar + listHtml +
      checkPanel('reported', '{"method":"account_tx","params":{"account":"pf...","limit":20}}', 'returns consensus and FastPay rows (with order_hash, certificate_digest, and decoded memos)'));
  }

  async function messageDetail(id) {
    const d = await getOptional(`/message/${encodeURIComponent(id)}`);
    if (!d) {
      const txFallback = await getOptional(`/tx/${encodeURIComponent(id)}`);
      if (txFallback) return tx(id);
      return page(head('Devnet · Message', `Message ${short(id, 14, 10)}`, 'This message pointer is not in the explorer index yet.', '') +
        checkPanel('reported', `{"method":"tx","params":{"tx_id":"${id}"}}`, 'returns the transaction or FastPay order_hash receipt with raw memos') +
        `<div class="btns" style="margin-top:20px">${link('/messages', '← All messages', 'btn')}</div>`);
    }
    const m = d.message || d;
    const badge = C.classifyMessageBadge ? C.classifyMessageBadge(m) : { label: 'Message', cls: 'ok' };
    return page(head(`Devnet · Message · ${esc(m.pointer_version === 'v4' ? 'pf.ptr v4' : 'pf.ptr v5')}`,
      esc(badge.is_task_reward ? 'Verified Task reward payout' : (m.summary || badge.label)),
      m.height ? `Anchored at block ${num(m.height)}${m.time ? ' · ' + utc(m.time) : ''}.` : '',
      `<div class="ex-meta">${m.tx_id ? link(`/tx/${esc(m.tx_id)}`, 'Open transaction →', 'btn sm') : ''}${link('/messages', '← All messages', 'btn sm')}</div>`) +
      renderMessagePanel(m, { hideLink: true }) +
      `<details class="fold"><summary>Raw envelope metadata</summary><pre class="raw">${json(m)}</pre></details>` +
      checkPanel(m.evidence || 'reported', `{"method":"tx","params":{"tx_id":"${m.order_hash || m.tx_id || id}"}}`, 'returns the anchored transaction or FastPay order_hash receipt'));
  }

  // ── Wave 1 View 2: Governance Archive (Pillar 1 + Contract C1) ─────────────
  async function governancePage(q) {
    const stateFilter = q.get('state') || '';
    const [d, net] = await Promise.all([
      getOptional(`/governance${stateFilter ? `?state=${encodeURIComponent(stateFilter)}` : ''}`),
      getOptional('/network'),
    ]);
    const sessions = (d?.sessions || []).filter((s) => !C.isAuthorizedGovernanceAnchor || C.isAuthorizedGovernanceAnchor(s));
    const filtered = stateFilter ? sessions.filter((s) => String(s.state || '').toLowerCase().includes(stateFilter)) : sessions;
    const chips = [['', 'All sessions'], ['published', 'Published'], ['ruling_anchored', 'With ruling'], ['live', 'Live / Review']];
    const chipBar = `<div class="chips">${chips.map(([k, v]) => `<a class="chip" href="#/governance${k ? `?state=${k}` : ''}" aria-current="${stateFilter === k}">${esc(v)}</a>`).join('')}</div>`;
    const sessionsHtml = filtered.length
      ? `<table class="ledger tight"><thead><tr><th>Session</th><th>Title</th><th>Snapshot block</th><th>Deliverables</th><th>State</th><th>When</th></tr></thead><tbody>
        ${filtered.map((s) => `<tr>
          <td>${link(`/governance/${encodeURIComponent(s.session_id)}`, esc(s.session_id), 'lk')}</td>
          <td><b>${esc(s.title || `Session #${s.session_number}`)}</b><span class="sub2">${esc(s.authority?.identity_handle || s.authority?.signer_set_id || 'Pinned authority')} · ${esc(s.authority?.threshold || 1)}-of-${esc(s.authority?.total_signers || 1)}</span></td>
          <td class="num">${s.finalized_block_height ? link(`/block/${s.finalized_block_height}`, num(s.finalized_block_height)) : '–'}</td>
          <td class="num">${s.deliverables_count != null ? num(s.deliverables_count) : '–'}</td>
          <td><span class="tag ${String(s.state || '').toLowerCase().includes('published') || String(s.state || '').toLowerCase().includes('ruling') ? 'lvl' : 'ok'}">${esc(GOV_STATE_LABELS[s.state] || s.state || 'Published')}</span></td>
          <td>${whenMs(s.finalized_at_unix_ms || s.created_at_unix_ms) || '–'}</td>
        </tr>`).join('')}</tbody></table>`
      : `<div class="proto-empty">
          <h3>No anchored Hive Governance sessions indexed yet.</h3>
          <p>The Governance Archive tracks <code>CONTENT_KIND_GOVERNANCE (12)</code> artifacts anchored on chain via <code>pf.ptr</code> v5 by the pinned <code>AuthorityBinding</code> account (1-of-1 founder at launch; threshold-ready for multi-sig stewards). Unauthorized governance anchors are ignored.</p>
          <ul class="proto-rules">
            <li><b>Single-block snapshot (<code>pf.governance.snapshot.v1</code>):</b> All L1 reads pinned to one finalized block height with raw response SHA-256 and CIDs.</li>
            <li><b>Carry-over accountability (<code>pf.governance.packet.v1</code>):</b> Every prior-session deliverable is scored publicly (<code>DONE</code>, <code>IN_PROGRESS</code>, <code>NOT_DONE</code>, <code>DROPPED</code>).</li>
            <li><b>Canonical transcript &amp; two-pass minutes (<code>pf.governance.transcript.v1</code> / <code>minutes.v1</code>):</b> Ordered by server <code>receipt_seq</code> with isolated Pass 1 (founder decisions) vs Pass 2 (quoted community input).</li>
            <li><b>Replayable rulings (<code>pf.governance.ruling.v1</code>):</b> Optional founder-flagged deterministic rulings executed on read-only compute (Google/Vast) with founder approval signatures.</li>
          </ul>
        </div>`;
    const onchainGov = (net?.governance || []).slice(0, 10);
    return page(head('Devnet · Pillar 1', 'Governance Archive', 'Anchored Hive governance packets, single-block protocol snapshots, receipt-ordered transcripts, two-pass minutes, and deterministic rulings.') +
      chipBar + sessionsHtml +
      (onchainGov.length ? section('On-chain Cobalt rule changes & amendments', link('/network', 'Network view →')) + `<ul class="stream">${onchainGov.map((o) => opLine(o)).join('')}</ul>` : '') +
      checkPanel('reported', '{"method":"blocks","params":{"from_height":1,"limit":10}}', 'returns governance blocks and Cobalt amendments directly from a validator'));
  }

  async function governanceSession(sessionId) {
    const d = await getOptional(`/governance/${encodeURIComponent(sessionId)}`);
    if (!d) {
      return page(head('Devnet · Governance Session', esc(sessionId), 'This governance session is not indexed yet.', '') +
        `<div class="btns">${link('/governance', '← Governance Archive', 'btn')}</div>`);
    }
    const s = d.session || d;
    const authorized = !C.isAuthorizedGovernanceAnchor || C.isAuthorizedGovernanceAnchor(s);
    const snap = s.snapshot || {};
    const packet = s.packet || {};
    const transcript = s.transcript || {};
    const minutes = s.minutes || {};
    const rulings = s.rulings || (s.ruling ? [s.ruling] : []);
    const carryover = minutes.previous_deliverables_review || packet.previous_deliverables_status || [];

    return page(head(`Devnet · Governance Session #${esc(s.session_number ?? '')}`, esc(s.title || sessionId), esc(packet.summary || minutes.summary || ''),
      `<div class="ex-meta">
        <span class="tag ${authorized ? 'lvl' : 'rej'}">${authorized ? 'Pinned authority verified' : 'Unauthorized anchor'}</span>
        <span class="tag ok">${esc(GOV_STATE_LABELS[s.state || minutes.state] || s.state || 'Published')}</span>
        ${s.anchor_tx_id ? link(`/tx/${esc(s.anchor_tx_id)}`, 'Anchor transaction →', 'btn sm') : ''}
        ${link('/governance', '← Governance Archive', 'btn sm')}
      </div>`) +
      (!authorized ? '<div class="ex-banner">Warning: this session was not anchored by a pinned authorized governance account.</div>' : '') +
      section('Authority binding') + `<div class="kv">
        <div>Signer set</div><div class="mono">${esc(s.authority?.signer_set_id || '–')} (${esc(s.authority?.threshold || 1)}-of-${esc(s.authority?.total_signers || 1)})</div>
        <div>Authorized accounts</div><div>${(s.authority?.authorized_accounts || []).map((a) => addr(a)).join('<br>') || '–'}</div>
        <div>Founder Nostr pubkey</div><div>${hashRow(s.authority?.founder_nostr_pubkey)}</div>
        ${s.authority?.identity_handle ? `<div>Identity handle</div><div class="mono">${esc(s.authority.identity_handle)}</div>` : ''}
      </div>` +
      section('Protocol snapshot', snap.finalized_block_height ? link(`/block/${snap.finalized_block_height}`, `Pinned at block ${num(snap.finalized_block_height)} →`) : '') + `<div class="kv">
        <div>Finalized height</div><div class="num">${snap.finalized_block_height ? link(`/block/${snap.finalized_block_height}`, num(snap.finalized_block_height)) : '–'}</div>
        <div>Block hash</div><div>${hashRow(snap.finalized_block_hash)}</div>
        <div>Active validators</div><div class="num">${num(snap.active_validator_count)}</div>
        <div>Sources recorded</div><div class="num">${num((snap.sources || []).length)} raw response hashes</div>
      </div>` +
      section('Carry-over deliverables scorecard') + (carryover.length
        ? `<table class="ledger tight"><thead><tr><th>Deliverable</th><th>Origin</th><th>Status</th><th>Evidence</th></tr></thead><tbody>
          ${carryover.map((c) => {
            const [lbl, cls] = DELIV_STATUS[c.status] || [String(c.status || '–'), 'ok'];
            return `<tr><td><b>${esc(c.title)}</b><span class="sub2">${esc(c.deliverable_id)}</span></td><td class="mono">${esc(c.origin_session_id)}</td><td><span class="tag ${cls}">${esc(lbl)}</span></td><td>${esc(c.evidence_note || '–')}</td></tr>`;
          }).join('')}</tbody></table>`
        : '<p class="ex-note">No prior-session carry-over deliverables recorded.</p>') +
      section('Frozen session transcript') + `<div class="kv">
        <div>Included entries</div><div class="num">${num((transcript.included_entries || []).length || transcript.included_count)} (ordered by server receipt_seq)</div>
        <div>Excluded events</div><div class="num">${num((transcript.excluded_events || []).length || transcript.excluded_count)} audited exclusions</div>
        <div>Transcript root (SHA-256)</div><div>${hashRow(transcript.transcript_root_sha256)}</div>
        <div>Markdown transcript CID</div><div>${hashRow(transcript.markdown_transcript_cid?.cid_multibase || transcript.markdown_transcript_cid)}</div>
      </div>` +
      section('Governance minutes · Pass 1 (Decisions & Next Deliverables)') +
      ((minutes.decisions || []).length
        ? `<table class="ledger tight"><thead><tr><th>Decision</th><th>Resolution</th><th>Deterministic ruling</th></tr></thead><tbody>
          ${minutes.decisions.map((dec) => `<tr><td><b>${esc(dec.title)}</b><span class="sub2">${esc(dec.decision_id)}</span></td><td>${esc(dec.resolution)}</td><td>${dec.run_deterministic_ruling ? '<span class="tag lvl">Flagged</span>' : '<span class="quiet">No</span>'}</td></tr>`).join('')}</tbody></table>`
        : '<p class="ex-note">No finalized decisions recorded.</p>') +
      ((minutes.next_deliverables || []).length
        ? `<h3 class="subhead">Next deliverables (auto-carried to next session)</h3><table class="ledger tight"><thead><tr><th>Deliverable</th><th>Owner</th><th>Target date</th></tr></thead><tbody>
          ${minutes.next_deliverables.map((nd) => `<tr><td><b>${esc(nd.title)}</b><span class="sub2">${esc(nd.description || '')}</span></td><td>${/^pf[0-9a-f]{40}$/.test(nd.owner || '') ? addr(nd.owner) : esc(nd.owner || '–')}</td><td class="mono">${esc(nd.target_date || '–')}</td></tr>`).join('')}</tbody></table>`
        : '') +
      section('Governance minutes · Pass 2 (Community input — isolated quoted data)') +
      ((minutes.community_input || []).length
        ? `<div class="gov-pass2">${minutes.community_input.map((ci) => `<div class="gov-quote"><b>${esc(ci.topic)}</b><p>${esc(ci.summary)}</p><span class="mono quiet">${num((ci.cited_event_ids || []).length)} cited Nostr event(s)</span></div>`).join('')}</div>`
        : '<p class="ex-note">No Pass 2 community input summaries recorded.</p>') +
      (rulings.length ? section('Deterministic ruling anchors') + rulings.map((r) => `<div class="proto-card"><div class="kv compact">
        <div>Ruling ID</div><div class="mono">${esc(r.ruling_id)} (decision ${esc(r.decision_id)})</div>
        <div>Compute backend</div><div><span class="tag ok">${esc(r.compute_backend || '–')}</span> <span class="quiet">Read-only compute · founder-signed approval</span></div>
        <div>Verdict</div><div><b>${esc(r.verdict || '–')}</b></div>
        <div>Model / constitution</div><div class="mono">${esc(r.model_digest || '–')} · ${esc(r.constitution_version || '–')}</div>
        <div>Input bundle SHA-256</div><div>${hashRow(r.input_bundle_sha256)}</div>
        <div>Output ruling SHA-256</div><div>${hashRow(r.output_ruling_sha256)}</div>
        <div>Replay trace SHA-256</div><div>${hashRow(r.replay_trace_sha256)}</div>
      </div></div>`).join('') : '') +
      `<details class="fold"><summary>Raw session packet</summary><pre class="raw">${json(s)}</pre></details>`);
  }

  // ── Wave 1 View 3: NFTs (Pillar 4 + Contract C1 & C4 Train A) ──────────────
  async function nftsPage(q) {
    const owner = q.get('owner') || '';
    const issuer = q.get('issuer') || '';
    const collection = q.get('collection') || '';
    const cursor = q.get('cursor') || '';
    const includeBurned = q.get('burned') === '1';
    const qs = new URLSearchParams();
    if (owner) qs.set('owner', owner);
    if (issuer) qs.set('issuer', issuer);
    if (collection) qs.set('collection', collection);
    if (cursor) qs.set('cursor', cursor);
    if (includeBurned) qs.set('include_burned', '1');
    const d = await getOptional(`/nfts${qs.toString() ? '?' + qs.toString() : ''}`);
    const nfts = d?.nfts || [];
    const filterSummary = [owner && `Owner ${short(owner, 10, 6)}`, issuer && `Issuer ${short(issuer, 10, 6)}`, collection && `Collection ${collection}`].filter(Boolean).join(' · ');
    const bodyHtml = nfts.length
      ? `<div class="nftgrid">${nfts.map(renderNftTile).join('')}</div>
         <div class="pager">${d.next_cursor ? link(`/nfts?${new URLSearchParams({ ...(owner ? { owner } : {}), ...(issuer ? { issuer } : {}), ...(collection ? { collection } : {}), ...(includeBurned ? { burned: '1' } : {}), cursor: d.next_cursor }).toString()}`, 'Next page →', 'btn') : ''}</div>`
      : `<div class="proto-empty">
          <h3>${d ? 'No NFTs found for this query.' : 'Post-quantum NFT indexing activates with L1 Upgrade Train A.'}</h3>
          <p>Native ML-DSA-65 NFTs use keyed <code>nfts_by_id</code> storage, permanent <code>used_nft_serials</code> replay tombstones, and Pillar 2 signed <code>pf.nft.metadata.v1</code> envelopes verified under the one-hash rule.</p>
          <ul class="proto-rules">
            <li><b>Issuer + collection always paired:</b> Every NFT displays its full on-chain issuer address alongside its collection ID — never a collection name alone.</li>
            <li><b>One-hash &amp; signature verification:</b> Checks <code>SHA3-384(raw_envelope) == nft.metadata_hash</code>, <code>account(envelope.sender_pubkey) == nft.issuer</code>, and the ML-DSA-65 envelope signature.</li>
            <li><b>Burn-first vs pin-only provenance:</b> Migrated historical NFTs carry bit-63 partitioned serials and offline-verifiable <code>claim_cid</code> + archived founder-signed burn-proof bundles. Pin-only records render strictly as <em>Recorded Provenance</em>.</li>
          </ul>
        </div>`;
    const rpcCall = owner
      ? `{"method":"account_nfts","params":{"account":"${owner}","include_burned":${includeBurned},"cursor":${cursor ? `"${cursor}"` : 'null'},"limit":50}}`
      : issuer
        ? `{"method":"issuer_nfts","params":{"issuer":"${issuer}","collection_id":${collection ? `"${collection}"` : 'null'},"include_burned":${includeBurned},"cursor":${cursor ? `"${cursor}"` : 'null'},"limit":50}}`
        : '{"method":"nft_info","params":{"nft_id":"<96-hex-nft-id>"}}';
    return page(head('Devnet · Pillar 4', 'NFTs', filterSummary ? `Filtered by ${filterSummary}.${d?.total_count != null ? ` ${num(d.total_count)} total.` : ''}` : 'Native ML-DSA-65 post-quantum NFTs with signed pf.nft.metadata.v1 envelopes and offline-verifiable burn-first provenance.') +
      `<div class="chips"><a class="chip" href="#/nfts" aria-current="${!includeBurned && !filterSummary}">Live NFTs</a><a class="chip" href="#/nfts?burned=1" aria-current="${includeBurned}">Include burned</a></div>` +
      bodyHtml +
      checkPanel('reported', rpcCall, 'returns paginated NFT definitions directly from a validator'));
  }

  async function nftDetail(nftId) {
    const d = await getOptional(`/nft/${encodeURIComponent(nftId)}`);
    if (!d) {
      return page(head('Devnet · NFT', `NFT ${short(nftId, 14, 10)}`, 'This NFT is not in the explorer index yet.', '') +
        checkPanel('reported', `{"method":"nft_info","params":{"nft_id":"${nftId}"}}`, 'returns the on-chain NFT record directly from a validator') +
        `<div class="btns" style="margin-top:20px">${link('/nfts', '← All NFTs', 'btn')}</div>`);
    }
    const n = d.nft || d;
    const metaDoc = n.metadata || {};
    const col = C.formatNftCollectionIdentity ? C.formatNftCollectionIdentity(n) : { issuer: n.issuer, collection_id: n.collection_id, collection_name: '' };
    const ver = C.nftVerificationSummary ? C.nftVerificationSummary(n) : { label: 'Metadata not checked', cls: 'part' };
    const origin = n.origin || metaDoc.origin || null;
    const origBadge = C.nftOriginBadge ? C.nftOriginBadge(origin) : { mode: 'native', label: 'Native L1v2 mint', cls: 'ok' };
    const migrated = C.isMigratedNftSerial ? C.isMigratedNftSerial(n.serial) : false;
    const imgGw = C.safeIpfsGatewayUrl ? C.safeIpfsGatewayUrl(metaDoc.image) : null;

    return page(head(`Devnet · NFT · ${esc(col.collection_id || 'collection')}`, esc(metaDoc.name || `NFT ${short(n.nft_id, 12, 8)}`), esc(metaDoc.description || ''),
      `<div class="ex-meta">
        <span class="tag ${esc(ver.cls)}">${esc(ver.label)}</span>
        <span class="tag ${esc(origBadge.cls)}">${esc(origBadge.label)}</span>
        ${n.burned ? '<span class="tag rej">Burned · serial tombstoned</span>' : '<span class="tag ok">Active</span>'}
        ${migrated ? '<span class="tag ok">Migrated serial (bit 63 = 1)</span>' : '<span class="tag ok">Fresh native serial (bit 63 = 0)</span>'}
        ${link('/nfts', '← All NFTs', 'btn sm')}
      </div>`) +
      `<div class="two nft-detail">
        <div class="nft-art-box">
          <div class="nft-art-frame" id="nft-art-frame">
            ${imgGw ? `<button type="button" class="btn" data-load-art="${esc(imgGw)}">Load IPFS artwork on click</button><span class="sub2 mono">${esc(metaDoc.image)}</span>` : '<span class="quiet">No validated ipfs:// artwork URI</span>'}
          </div>
          ${(metaDoc.attributes || []).length ? `<div class="nft-attrs">${metaDoc.attributes.map((at) => `<div class="nft-attr"><span>${esc(at.trait_type)}</span><b>${esc(at.value)}</b></div>`).join('')}</div>` : ''}
        </div>
        <div>
          <div class="kv">
            <div>NFT ID</div><div>${hashRow(n.nft_id)}</div>
            <div>Issuer (authoritative)</div><div>${addr(col.issuer)}</div>
            <div>Collection ID</div><div><span class="mono">${esc(col.collection_id || '–')}</span>${col.collection_name ? ` · ${esc(col.collection_name)}` : ''}</div>
            <div>Current owner</div><div>${addr(n.owner)}</div>
            <div>Serial</div><div class="mono">${esc(String(n.serial ?? '–'))}</div>
            <div>Metadata URI</div><div>${hashRow(n.metadata_uri)}</div>
            <div>Metadata hash (SHA3-384)</div><div>${hashRow(n.metadata_hash)}</div>
            <div>Transfer &amp; burn policy</div><div>${n.transferable ? 'Transferable' : 'Non-transferable'} · Issuer burnable: <b>${n.issuer_burnable ? 'Yes' : 'No'}</b>${n.collection_burn_locked ? ' · Burn-locked' : ''}${n.collection_transfer_locked ? ' · Transfer-locked' : ''} · Transfer fee: ${num(n.issuer_transfer_fee ?? 0)} atoms</div>
          </div>
        </div>
      </div>` +
      section('One-hash & signature checks') + `<div class="kv">
        <div>SHA3-384(raw envelope) == metadata_hash</div><div>${ver.hashOk === true ? '<span class="tag lvl">Matched</span>' : ver.hashOk === false ? '<span class="tag rej">Mismatch</span>' : '<span class="tag part">Not checked</span>'}</div>
        <div>account(envelope.sender_pubkey) == nft.issuer</div><div>${ver.issuerOk === true ? '<span class="tag lvl">Matched</span>' : ver.issuerOk === false ? '<span class="tag rej">Mismatch</span>' : '<span class="tag part">Not checked</span>'}</div>
        <div>Envelope ML-DSA-65 signature</div><div>${ver.sigOk === true ? '<span class="tag lvl">Valid</span>' : ver.sigOk === false ? '<span class="tag rej">Invalid</span>' : '<span class="tag part">Not checked</span>'}</div>
      </div>` +
      (origin ? section('Origin provenance', `<span class="tag ${esc(origBadge.cls)}">${esc(origBadge.label)}</span>`) +
        `<div class="kv">
          <div>Source chain</div><div class="mono">${esc(origin.source_chain || '–')}</div>
          <div>Original NFTokenID</div><div>${hashRow(origin.nftoken_id)}</div>
          <div>Original issuer</div><div class="mono">${esc(origin.original_issuer || '–')}</div>
          <div>Original owner</div><div class="mono">${esc(origin.original_owner || '–')}</div>
          <div>Source mint tx</div><div>${hashRow(origin.mint_tx)}</div>
          ${origBadge.mode === 'burn_first' ? `<div>Source NFTokenBurn tx</div><div>${hashRow(origin.burn_tx)}${origin.burn_ledger_index ? ` <span class="quiet">ledger ${num(origin.burn_ledger_index)}</span>` : ''}</div>` : ''}
          ${origin.claim_cid ? `<div>Signed claim CID (pf.nft.claim.v1)</div><div>${hashRow(origin.claim_cid.cid_multibase || origin.claim_cid)}</div>` : ''}
          ${origin.claim_hash ? `<div>Claim SHA-256 (burn memo)</div><div>${hashRow(origin.claim_hash)}</div>` : ''}
          ${origin.burn_proof_bundle_cid ? `<div>Archived burn-proof bundle CID</div><div>${hashRow(origin.burn_proof_bundle_cid.cid_multibase || origin.burn_proof_bundle_cid)} <span class="quiet">Offline-verifiable post-Stage-4</span></div>` : ''}
        </div>` : '') +
      ((d.transfers || d.ops || []).length ? section('Transfer & lifecycle history') + `<ul class="stream">${(d.transfers || d.ops).map((o) => opLine(o)).join('')}</ul>` : '') +
      `<details class="fold"><summary>Raw NFT record</summary><pre class="raw">${json(n)}</pre></details>` +
      checkPanel(d.evidence || 'reported', `{"method":"nft_info","params":{"nft_id":"${n.nft_id}"}}`, 'returns this NFT definition directly from a validator'));
  }

  // ── Wave 1 View 4: Identity Card (Pillar 6 + Contract C4 Train B) ──────────
  async function identitiesPage(q) {
    const query = q.get('q') || '';
    const d = await getOptional(`/identities${query ? `?q=${encodeURIComponent(query)}` : ''}`);
    const list = d?.identities || [];
    const lookupForm = `<form class="id-lookup" id="ex-id-lookup">
      <label class="visually-hidden" for="ex-id-q">Look up an identity</label>
      <input id="ex-id-q" type="search" value="${esc(query)}" placeholder="goodalexander@tasknode.postfiat.org, pf… account, 64-hex Nostr pubkey, or validator ID" autocomplete="off" spellcheck="false">
      <button type="submit" class="btn solid sm">Resolve Identity →</button>
    </form>`;
    const listHtml = list.length
      ? `<table class="ledger tight"><thead><tr><th>Handle</th><th>Kind</th><th>L1v2 account</th><th>Nostr pubkey</th><th>Links</th><th>Status</th></tr></thead><tbody>
        ${list.map((id) => {
          const fullHandle = id.handle ? `${id.handle}@${id.registered_namespace || 'tasknode.postfiat.org'}` : null;
          return `<tr>
            <td>${link(`/identity/${encodeURIComponent(fullHandle || id.account)}`, esc(fullHandle || short(id.account, 10, 6)), 'lk')}</td>
            <td><span class="tag ok">${esc(id.identity_kind || 'human')}</span></td>
            <td>${addr(id.account)}</td>
            <td class="mono">${short(id.nostr_pubkey, 10, 6)}</td>
            <td class="num">${num((id.links || []).length)}</td>
            <td><span class="tag ${id.status === 'revoked' ? 'rej' : 'lvl'}">${esc(id.status || 'active')}</span></td>
          </tr>`;
        }).join('')}</tbody></table>`
      : `<div class="proto-empty">
          <h3>${d ? 'No minted identities match that filter yet.' : 'On-chain Identity indexing activates with L1 Upgrade Train B.'}</h3>
          <p>Native <code>identity_set</code> transactions execute strictly through ordered consensus, binding a post-quantum ML-DSA-65 account, BIP-340 proven Nostr key (<code>v1</code> legacy or <code>v2</code> seed KDF), registered <code>@tasknode.postfiat.org</code> handle, X-Wing message key, Profile NFT avatar, and explicitly co-signed links.</p>
          <ul class="proto-rules">
            <li><b>Consensus-verified vs client-verified separation:</b> Validator nodes (30-day cooldown), old-chain accounts, and agent controllers are consensus-verified; custom NIP-05 domains, EVM, and Solana addresses are non-unique client-verified claims.</li>
            <li><b>2-tier registrar safety:</b> Hot registrar issues unclaimed handles only; handle reassignment requires 2-of-3 cold signers + 7-day timelock.</li>
            <li><b>Safe classical kill-switch:</b> Pure ML-DSA-65 updates, account rotation, PQ links, and revocation keep working even if classical proofs are retired.</li>
          </ul>
        </div>`;
    return page(head('Devnet · Pillar 6', 'Hive Identities', 'Searchable on-chain identity cards tying Post Fiat L1v2 accounts, Nostr keys, handles, validators, NFTs, and agents together.') +
      lookupForm + listHtml +
      checkPanel('reported', '{"method":"identity_by_handle","params":{"handle":"goodalexander","namespace":"tasknode.postfiat.org"}}', 'resolves a handle directly from a validator via postfiat-identity-lookup-v1'));
  }

  async function identityDetail(rawQuery) {
    const q = decodeURIComponent(rawQuery || '').trim();
    const d = await getOptional(`/identity/${encodeURIComponent(q)}`);
    const isAccount = /^pf[0-9a-f]{40}$/i.test(q);
    const isNostrHex = /^[0-9a-f]{64}$/i.test(q);
    const isHandle = q.includes('@');
    const rpcCall = isAccount
      ? `{"method":"identity_info","params":{"account":"${q.toLowerCase()}"}}`
      : isNostrHex
        ? `{"method":"identity_by_nostr","params":{"nostr_pubkey":"${q.toLowerCase()}"}}`
        : isHandle
          ? `{"method":"identity_by_handle","params":{"handle":"${q.split('@')[0].toLowerCase()}","namespace":"${q.split('@')[1].toLowerCase()}"}}`
          : `{"method":"identity_by_link","params":{"link_kind":"validator_node","target":"${q}"}}`;

    if (!d || !d.identity) {
      return page(head('Devnet · Identity Card', esc(q), d?.found === false ? 'No active on-chain identity is bound to this lookup key.' : 'Identity lookup is not indexed yet (activates with L1 Upgrade Train B).',
        `<div class="ex-meta">${isAccount ? link(`/account/${q.toLowerCase()}`, 'Open account page →', 'btn sm') : ''}${link('/identities', '← All identities', 'btn sm')}</div>`) +
        (d?.compromised_nostr_pubkey ? '<div class="ex-banner">This Nostr public key is recorded in compromised_nostr_pubkeys and can never be rebound.</div>' : '') +
        checkPanel('reported', rpcCall, 'queries postfiat-identity-lookup-v1 directly from any validator'));
    }
    const id = d.identity;
    const fullHandle = id.handle ? `${id.handle}@${id.registered_namespace || 'tasknode.postfiat.org'}` : id.account;
    return page(head('Devnet · Pillar 6 · Identity Card', esc(fullHandle), `On-chain ${esc(id.identity_kind || 'human')} identity anchored on ${esc(d.chain_id || 'postfiatl1v2')}.`,
      `<div class="ex-meta">${link(`/account/${esc(id.account)}`, 'Open account →', 'btn sm')}${link('/identities', '← Search identities', 'btn sm')}</div>`) +
      renderIdentityCard(id, {
        compromised_nostr_pubkey: d.compromised_nostr_pubkey,
        validatorStates: d.validator_states,
        registrar_history: d.registrar_history,
      }) +
      `<details class="fold"><summary>Raw postfiat-identity-lookup-v1 payload</summary><pre class="raw">${json(d)}</pre></details>` +
      checkPanel(d.evidence || 'reported', rpcCall, 'returns this exact postfiat-identity-lookup-v1 record from a validator'));
  }

  async function coinsPage() {
    const d = await get('/coins');
    const row = (c) => `<tr><td>${link(`/coin/${c.asset_id}`, esc(c.code))}${c.retired ? ' <span class="tag prop">Retired</span>' : ''}${c.halted ? ' <span class="tag rej">Halted</span>' : ''}</td><td class="num">${usd(c.nav_per_unit, c.nav_decimals, 6)}</td><td class="num">${units(c.supply, c.precision, 2)}${c.ledger_supply != null ? `<span class="sub2">${units(c.ledger_supply, c.precision, 2)} on the ledger now</span>` : ''}</td><td class="num">${usd(c.net_assets, c.nav_decimals)}</td><td>${c.checks.length} · last at ${c.last_check_height ? link(`/block/${c.last_check_height}`, num(c.last_check_height)) : '–'}</td><td>${spark(c.checks.map((x) => x.nav_per_unit))}</td></tr>`;
    const listed = d.coins.filter((c) => c.listed), other = d.coins.filter((c) => !c.listed);
    const table = (rows) => `<table class="ledger tight"><thead><tr><th>Coin</th><th>NAV per coin</th><th>Supply at last check</th><th>Reserves</th><th>NAV checks</th><th></th></tr></thead><tbody>${rows.map(row).join('')}</tbody></table>`;
    return page(head('Devnet', 'NAVCoins', 'A NAVCoin trades at the value of the reserves behind it. Each NAV check is a reading of those reserves, submitted with a proof and finalized by the validators.') +
      section('Listed') + table(listed) + (other.length ? section('Earlier and test coins') + table(other) + '<p class="ex-note">Coins registered on the network during development. They are shown because they are on the ledger.</p>' : ''));
  }

  function navBar(c, x) { const v = c.checks.map((k) => Number(k.nav_per_unit)).filter((k) => k > 0); const lo = Math.min(...v), hi = Math.max(...v); if (hi === lo) return '<span class="quiet">no change</span>'; const pos = ((Number(x.nav_per_unit) - lo) / (hi - lo)) * 100; return `<span class="rng" title="Lowest ${usd(lo, c.nav_decimals, 6)}, highest ${usd(hi, c.nav_decimals, 6)}"><i style="left:${pos.toFixed(1)}%"></i></span>`; }
  function navRange(c) { const v = c.checks.map((x) => Number(x.nav_per_unit)).filter((x) => x > 0); if (v.length < 2) return ''; const lo = Math.min(...v), hi = Math.max(...v); return `<span class="hint">Lowest to highest across ${v.length} checks: ${(((hi - lo) / lo) * 100).toFixed(3)}%</span>`; }
  async function coin(id) {
    const c = await get(`/coin/${id}`); if (!c) return notFound('No asset with that name or ID.');
    if (c.plain_asset) return page(head('Devnet · asset', esc(c.code || short(c.asset_id)), esc(c.name || ''), '') + `<div class="kv"><div>Asset ID</div><div>${hashRow(c.asset_id)}</div><div>Issuer</div><div>${addr(c.issuer)}</div><div>Precision</div><div>${esc(c.precision)}</div><div>Holders</div><div>${num(c.detail?.holder_count)}</div></div>` + section('Operations') + `<ul class="stream">${c.ops.map((o) => opLine(o)).join('')}</ul>`);
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
      section('Operations', link(`/stream?asset=${c.asset_id}`, `All ${num(c.op_count)} →`)) + `<ul class="stream">${collapse(c.ops).slice(0, 15).map((o) => opLine(o)).join('')}</ul><p class="ex-note">Showing the latest of ${num(c.op_count)}. ${link(`/stream?asset=${c.asset_id}`, 'See all operations for ' + esc(c.code) + ' →', 'lk')}</p>`);
  }

  async function privatePage() {
    const d = await get('/private'); const share = d.shielded_blocks / Math.max(1, d.blocks); const Ccirc = 2 * Math.PI * 90;
    const names = { asset_orchard_ingress_v2: 'Deposits into the pool', shielded_swap_v1: 'Private swaps', asset_orchard_private_egress_v1: 'Private withdrawals', asset_orchard_private_primary_issue_v1: 'Private NAVCoin creations', asset_orchard_private_primary_redeem_v1: 'Private cash-ins', asset_orchard_egress_v1: 'Withdrawals' };
    return `<section class="ex-night"><div class="wrap">
      <div class="dialrow"><svg class="dial" viewBox="0 0 220 220" role="img" aria-label="${(share * 100).toFixed(1)} percent of blocks are private"><circle class="bg" cx="110" cy="110" r="90"/><circle class="fg" cx="110" cy="110" r="90" stroke-dasharray="${Ccirc.toFixed(1)}" stroke-dashoffset="${(Ccirc * (1 - share)).toFixed(1)}"/><text x="110" y="122" text-anchor="middle">${(share * 100).toFixed(1)}%</text><text class="cap" x="110" y="146" text-anchor="middle">OF BLOCKS</text></svg>
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
      ${d.journeys.map((j) => `<tr><td>${num(j.first_height)}${j.last_height !== j.first_height ? '–' + num(j.last_height) : ''}</td><td>${when(j.time)}</td><td>${link(`/journey/${j.kind}/${j.key}`, esc(JOURNEY[j.kind]), 'lk')}</td><td>${esc(j.headline)}${j.trip?.sentence ? `<span class="sub2">${esc(j.trip.sentence)}</span>` : ''}</td><td>${dots(j.steps)}</td><td>${j.summary === 'rejected' ? '<span class="tag rej">Refused</span>' : j.summary === 'in progress' ? '<span class="tag demo">In progress</span>' : `<span class="quiet">${j.summary === 'complete' ? 'Complete' : j.summary === 'complete on the network' ? 'Done here' : esc(String(j.summary).replace(/^./, (c) => c.toUpperCase()))}</span>`}</td></tr>`).join('')}
      </tbody></table><p class="ex-note">"Done here" means every step on this network is done. Steps on Ethereum are not read by this build, so they are never shown as done.</p>`);
  }
  async function journeyPage(kind, key) {
    const j = await get(`/journey/${kind}/${key}`); if (!j) return notFound('No journey with that key.');
    return page(head(`Devnet · journey · ${esc(JOURNEY[kind] || kind)}`, esc(j.headline), `Blocks ${num(j.first_height)} to ${num(j.last_height)}. State: ${esc(j.summary)}.`, '', 'sentence') + journeyPanel(j).replace(/<a href="#\/journey[^>]*>Open journey →<\/a>/, '') +
      section('Operations in this journey') + `<ul class="stream">${j.ops.map((o) => opLine(o)).join('')}</ul><div class="kv" style="margin-top:28px"><div>Journey key</div><div>${hashRow(j.key)}</div></div>`);
  }

  async function network() {
    const d = await get('/network');
    return page(head('Devnet', 'Network', `Six validators take turns proposing. Running build ${esc(d.status.build_git_revision || '–')}.`, `<div class="ex-meta">${link('/governance', 'Open Hive Governance Archive →', 'btn sm')}<a class="btn sm" href="/run-a-validator/">Run a Validator Guide →</a></div>`) +
      section('Validators') + `<table class="ledger tight"><thead><tr><th>Validator</th><th class="r">Blocks proposed</th><th class="r">Votes in the last 300 blocks</th><th class="r">Last proposed</th></tr></thead><tbody>${d.validators.map((v) => `<tr><td>${esc(v.proposer)}${v.low ? ' <span class="tag rej">Fewer votes</span>' : ''}</td><td class="r num">${num(v.proposed)}</td><td class="r num">${num(v.votes_last_300)}</td><td class="r">${link(`/block/${v.last}`, num(v.last))}</td></tr>`).join('')}</tbody></table>` +
      `<p class="ex-note">${d.validators.some((v) => v.low) ? 'A validator marked "fewer votes" has recorded under four fifths of the typical number of votes in the last 300 blocks. Blocks still need five of six.' : 'All six validators have voted at a similar rate over the last 300 blocks.'}</p>` +
      section('Rule changes and governance', link('/governance', 'Hive Governance Archive →')) + `<ul class="stream">${d.governance.map((o) => opLine(o)).join('')}</ul>`);
  }

  const notFound = (msg) => page(head('Explorer', 'Nothing here.', esc(msg || 'That page does not exist.')) + `<div class="btns">${link('/', 'Back to the devnet', 'btn solid')}</div>`);

  // ── router ─────────────────────────────────────────────────────────────────
  const routes = [
    [/^\/$/, home],
    [/^\/stream$/, streamPage],
    [/^\/blocks$/, blocks],
    [/^\/block\/(\d+)$/, block],
    [/^\/tx\/([^/]+)$/, tx],
    [/^\/account\/([^/]+)$/, accountPage],
    [/^\/messages$/, messagesPage],
    [/^\/message\/([^/]+)$/, messageDetail],
    [/^\/governance$/, governancePage],
    [/^\/governance\/([^/]+)$/, governanceSession],
    [/^\/nfts$/, nftsPage],
    [/^\/nft\/([^/]+)$/, nftDetail],
    [/^\/identities$/, identitiesPage],
    [/^\/identity\/(.+)$/, identityDetail],
    [/^\/coins$/, coinsPage],
    [/^\/coin\/([^/]+)$/, coin],
    [/^\/private$/, privatePage],
    [/^\/journeys$/, journeys],
    [/^\/journey\/([a-z]+)\/([^/]+)$/, journeyPage],
    [/^\/network$/, network],
  ];
  function parse() { const raw = location.hash.replace(/^#/, '') || '/'; const [path, qs = ''] = raw.split('?'); return { path: path || '/', q: new URLSearchParams(qs), raw }; }
  function chrome() {
    const nav = document.getElementById('ex-nav');
    const items = [
      ['/', 'Overview'],
      ['/stream', 'Operations'],
      ['/blocks', 'Blocks'],
      ['/messages', 'Messages'],
      ['/governance', 'Governance'],
      ['/nfts', 'NFTs'],
      ['/identities', 'Identities'],
      ['/coins', 'NAVCoins'],
      ['/journeys', 'Journeys'],
      ['/private', 'Private'],
      ['/network', 'Network'],
    ];
    const here = (location.hash.replace(/^#/, '') || '/').split('?')[0];
    nav.innerHTML = items.map(([r, t]) => {
      const active = here === r || (r !== '/' && here.startsWith(r === '/identities' ? '/identit' : r.replace(/s$/, '')));
      return `<a href="#${r}"${active ? ' aria-current="page"' : ''}>${t}</a>`;
    }).join('');
  }
  async function render(soft) {
    const { path, q } = parse(); const mine = ++seq; chrome();
    const hit = routes.map(([re, fn]) => [path.match(re), fn]).find(([m]) => m);
    if (!soft) root.innerHTML = '<div class="wrap ex-loading">Reading the ledger…</div>';
    try {
      const html = hit ? await hit[1](...hit[0].slice(1), q) : notFound();
      if (mine !== seq) return;
      const y = scrollY; root.innerHTML = html; if (soft) scrollTo(0, y); else scrollTo(0, 0);
      document.title = `${(root.querySelector('h1')?.textContent || 'Explorer').trim().slice(0, 70)} · Post Fiat Explorer`;
    } catch {
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
    if (copy) { navigator.clipboard?.writeText(copy.dataset.copy); const t = copy.textContent; copy.textContent = 'Copied'; setTimeout(() => (copy.textContent = t), 1200); return; }
    const loadArt = e.target.closest('[data-load-art]');
    if (loadArt) {
      const frame = document.getElementById('nft-art-frame');
      if (frame) {
        const img = document.createElement('img');
        img.src = loadArt.dataset.loadArt;
        img.alt = 'NFT IPFS artwork';
        img.loading = 'lazy';
        img.referrerPolicy = 'no-referrer';
        frame.replaceChildren(img);
      }
      return;
    }
    const loadMedia = e.target.closest('[data-load-media]');
    if (loadMedia) {
      const a = document.createElement('a');
      a.href = loadMedia.dataset.loadMedia;
      a.target = '_blank';
      a.rel = 'noopener noreferrer';
      a.className = 'lk mono';
      a.textContent = 'Open IPFS attachment ↗';
      loadMedia.replaceWith(a);
    }
  });
  document.addEventListener('submit', (e) => {
    if (e.target?.id === 'ex-id-lookup') {
      e.preventDefault();
      const v = e.target.querySelector('input')?.value.trim();
      if (v) location.hash = `#/identity/${encodeURIComponent(v)}`;
    }
  });
  document.getElementById('ex-search')?.addEventListener('submit', async (e) => {
    e.preventDefault(); const input = e.target.querySelector('input'); const q = input.value.trim(); if (!q) return;
    const direct = C.resolveDirectSearchRoute ? C.resolveDirectSearchRoute(q) : null;
    try {
      const r = await getOptional(`/search?q=${encodeURIComponent(q)}`);
      if (r?.route) { location.hash = '#' + r.route; input.value = ''; }
      else if (direct) { location.hash = '#' + direct; input.value = ''; }
      else { input.value = ''; input.placeholder = 'Nothing on the network matches that'; }
    } catch {
      if (direct) { location.hash = '#' + direct; input.value = ''; }
      else pulse(false);
    }
  });
  render(false);
})();
