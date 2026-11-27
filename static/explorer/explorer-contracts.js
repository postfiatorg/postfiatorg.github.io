/* Post Fiat Explorer — Frozen Phase 0 Contract Helpers (C1 & C4).
 * Pure, framework-free functions shared by static/explorer/explorer.js (browser)
 * and tests/explorer-contracts.test.mjs (Node.js).
 */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.PFTExplorerContracts = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  // ── Pillar 2: pf.ptr v5 & legacy v4 constants (Contract C1) ────────────────
  const MEMO_TYPE_PF_PTR_HEX = '70662e707472'; // "pf.ptr"
  const MEMO_FORMAT_V5_HEX = '7635';           // "v5"
  const MEMO_FORMAT_V4_HEX = '7634';           // "v4"

  const POINTER_FLAG_PRIVATE = 0x01;
  const POINTER_FLAG_PUBLIC = 0x02;
  const POINTER_FLAG_EPHEMERAL = 0x04;
  const POINTER_FLAG_TOMBSTONE = 0x08;
  const POINTER_FLAG_MULTIPART = 0x10;
  const POINTER_FLAG_SEALED = 0x20;
  const POINTER_FLAG_SUPPORTED_MASK = 0x3f;

  const CONTENT_KIND_LABELS = {
    0: 'Unspecified',
    1: 'Task request',
    2: 'Task offer',
    3: 'Task acceptance',
    4: 'Message',
    5: 'Verification',
    6: 'Reward',
    7: 'Context',
    8: 'Submission',
    9: 'Profile',
    10: 'Attestation',
    11: 'System',
    12: 'Governance',
    13: 'NFT',
    14: 'x402 Payment',
    99: 'Test',
  };

  const MAX_PUBLIC_PREVIEW_BYTES = 65536; // 64 KiB explorer display cap
  const NFT_MIGRATED_SERIAL_BIT = 1n << 63n;

  // ── Safe HTML escaping & CID validation ────────────────────────────────────
  function escHtml(v) {
    return String(v ?? '').replace(/[&<>"']/g, (c) => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;',
    }[c]));
  }

  function validatePointerFlags(flags) {
    const f = Number(flags);
    if (!Number.isInteger(f) || f < 0 || (f & ~POINTER_FLAG_SUPPORTED_MASK) !== 0) {
      return { valid: false, visibility: null, modifiers: [], error: 'unsupported_flag_bits' };
    }
    const visBits = [
      (f & POINTER_FLAG_PUBLIC) !== 0 ? 'public' : null,
      (f & POINTER_FLAG_PRIVATE) !== 0 ? 'private' : null,
      (f & POINTER_FLAG_SEALED) !== 0 ? 'sealed' : null,
    ].filter(Boolean);
    if (visBits.length !== 1) {
      return { valid: false, visibility: null, modifiers: [], error: 'visibility_not_mutually_exclusive' };
    }
    const modifiers = [];
    if ((f & POINTER_FLAG_EPHEMERAL) !== 0) modifiers.push('ephemeral');
    if ((f & POINTER_FLAG_TOMBSTONE) !== 0) modifiers.push('tombstone');
    if ((f & POINTER_FLAG_MULTIPART) !== 0) modifiers.push('multipart');
    return { valid: true, visibility: visBits[0], modifiers, error: null };
  }

  function detectPointerMemo(memo) {
    if (!memo || typeof memo !== 'object') return null;
    const typeHex = String(memo.memo_type || '').toLowerCase();
    const typeText = String(memo.memo_type_text || '').toLowerCase();
    const fmtHex = String(memo.memo_format || '').toLowerCase();
    const fmtText = String(memo.memo_format_text || '').toLowerCase();
    const isPfPtr = typeHex === MEMO_TYPE_PF_PTR_HEX || typeText === 'pf.ptr';
    if (!isPfPtr) return null;
    if (fmtHex === MEMO_FORMAT_V5_HEX || fmtText === 'v5') {
      return { version: 'v5', legacy: false, data_hex: String(memo.memo_data || '') };
    }
    if (fmtHex === MEMO_FORMAT_V4_HEX || fmtText === 'v4') {
      return { version: 'v4', legacy: true, data_hex: String(memo.memo_data || '') };
    }
    return null;
  }

  function normalizeVisibility(msg) {
    if (!msg || typeof msg !== 'object') return 'unknown';
    if (msg.pointer && typeof msg.pointer.flags === 'number') {
      const checked = validatePointerFlags(msg.pointer.flags);
      if (checked.valid) return checked.visibility;
    }
    const raw = String(msg.visibility || msg.header?.visibility || '').toLowerCase();
    if (raw === 'public' || raw === 'visibility_public') return 'public';
    if (raw === 'private' || raw === 'visibility_private') return 'private';
    if (raw === 'sealed' || raw === 'visibility_sealed') return 'sealed';
    return 'unknown';
  }

  /**
   * Pillar 2 / Contract C1 spoof-proof "Task reward" badge invariant:
   * Shows "Task reward" ONLY when:
   *   1. Envelope signature is verified AND sender_pubkey matches the tx signer (sender_verified === true)
   *   2. Visibility is strictly PRIVATE (not public, not sealed)
   *   3. Schema is pf.reward.v1 (or schema_id === 201 / content_kind === 6)
   *   4. Verified sender matches the pinned official Task Node payout key/account.
   * Any outsider claiming pf.reward.v1 renders strictly as generic "Private message".
   */
  function classifyMessageBadge(msg, pinnedConfig) {
    const vis = normalizeVisibility(msg);
    const schema = String(msg?.schema_name || msg?.header?.schema_name || '').toLowerCase();
    const schemaId = Number(msg?.schema_id ?? msg?.header?.schema_id ?? 0);
    const kind = Number(msg?.content_kind ?? msg?.pointer?.content_kind ?? msg?.header?.content_kind ?? 0);
    const senderVerified = msg?.sender_verified === true;

    const isRewardSchema = schema === 'pf.reward.v1' || schemaId === 201 || kind === 6;

    let pinnedMatch = msg?.pinned_tasknode_payout_key_matched === true;
    if (!pinnedMatch && pinnedConfig) {
      const pk = String(msg?.sender_pubkey_hex || msg?.envelope?.sender_pubkey_hex || '').toLowerCase();
      const acc = String(msg?.sender_account || msg?.header?.sender_account || '').toLowerCase();
      const pubkeys = (pinnedConfig.tasknode_payout_pubkeys || []).map((x) => String(x).toLowerCase());
      const accounts = (pinnedConfig.tasknode_payout_accounts || []).map((x) => String(x).toLowerCase());
      if (pk && pubkeys.includes(pk)) pinnedMatch = true;
      else if (acc && accounts.includes(acc)) pinnedMatch = true;
    }

    if (senderVerified && vis === 'private' && isRewardSchema && pinnedMatch) {
      return {
        label: 'Task reward',
        cls: 'reward',
        is_task_reward: true,
        spoofed_reward: false,
        visibility: vis,
        sender_verified: true,
      };
    }

    const spoofedReward = isRewardSchema && (!senderVerified || !pinnedMatch);
    if (vis === 'sealed') {
      return { label: 'Sealed message', cls: 'sealed', is_task_reward: false, spoofed_reward: spoofedReward, visibility: vis, sender_verified: senderVerified };
    }
    if (vis === 'private') {
      return { label: 'Private message', cls: 'priv', is_task_reward: false, spoofed_reward: spoofedReward, visibility: vis, sender_verified: senderVerified };
    }
    if (kind === 12 || schema.startsWith('pf.governance.')) {
      return { label: 'Governance', cls: 'lvl', is_task_reward: false, spoofed_reward: false, visibility: vis, sender_verified: senderVerified };
    }
    if (kind === 13 || schema.startsWith('pf.nft.')) {
      return { label: 'NFT record', cls: 'lvl', is_task_reward: false, spoofed_reward: false, visibility: vis, sender_verified: senderVerified };
    }
    if (kind === 14 || schema.startsWith('pf.x402.')) {
      return { label: 'x402', cls: 'fill', is_task_reward: false, spoofed_reward: false, visibility: vis, sender_verified: senderVerified };
    }
    return {
      label: vis === 'public' ? 'Public message' : (CONTENT_KIND_LABELS[kind] || 'Message'),
      cls: 'ok',
      is_task_reward: false,
      spoofed_reward: spoofedReward,
      visibility: vis,
      sender_verified: senderVerified,
    };
  }

  function truncatePublicPreview(text, maxBytes = MAX_PUBLIC_PREVIEW_BYTES) {
    const raw = String(text ?? '');
    if (raw.length <= maxBytes) return { text: raw, truncated: false, total_chars: raw.length };
    return { text: raw.slice(0, maxBytes), truncated: true, total_chars: raw.length };
  }

  function safeIpfsGatewayUrl(uri, gatewayBase = 'https://ipfs.io/ipfs/') {
    const raw = String(uri || '').trim();
    if (!raw.startsWith('ipfs://')) return null;
    const cid = raw.slice('ipfs://'.length).split(/[/?#]/)[0];
    // Strict CIDv1 base32lower ("b...") or CIDv0 ("Qm...") validation — zero script/URL injection
    if (!/^(b[a-z2-7]{32,128}|Qm[1-9A-HJ-NP-Za-km-z]{44})$/.test(cid)) return null;
    return gatewayBase.replace(/\/?$/, '/') + cid;
  }

  // ── Pillar 1: Governance Archive authority verification (Contract C1) ──────
  function isAuthorizedGovernanceAnchor(session, pinnedAuthorityAccounts) {
    if (!session || typeof session !== 'object') return false;
    if (session.authority_verified === false) return false;
    const anchorAccount = String(session.anchor_account || session.sender_account || '').toLowerCase();
    const bindingAccounts = (session.authority?.authorized_accounts || []).map((a) => String(a).toLowerCase());
    if (Array.isArray(pinnedAuthorityAccounts) && pinnedAuthorityAccounts.length > 0) {
      const pinned = pinnedAuthorityAccounts.map((a) => String(a).toLowerCase());
      if (!anchorAccount || !pinned.includes(anchorAccount)) return false;
      if (bindingAccounts.length > 0 && !bindingAccounts.some((a) => pinned.includes(a))) return false;
      return session.authority_verified === true;
    }
    return session.authority_verified === true && (!anchorAccount || bindingAccounts.length === 0 || bindingAccounts.includes(anchorAccount));
  }

  // ── Pillar 4: NFT classification & one-hash verification (C1 + C4 Train A) ─
  function isMigratedNftSerial(serial) {
    if (serial == null || serial === '') return false;
    try {
      const n = typeof serial === 'bigint' ? serial : BigInt(String(serial));
      return (n & NFT_MIGRATED_SERIAL_BIT) !== 0n;
    } catch {
      return false;
    }
  }

  function formatNftCollectionIdentity(nft) {
    const issuer = String(nft?.issuer || nft?.metadata?.collection?.issuer_account || '');
    const collectionId = String(nft?.collection_id || nft?.metadata?.collection?.collection_id || '');
    const collectionName = String(nft?.metadata?.collection?.name || '');
    return {
      issuer,
      collection_id: collectionId,
      collection_name: collectionName,
      // Always pairs issuer + collection_id — never collection name alone
      display_pair: issuer && collectionId ? `${collectionId} · ${issuer}` : (collectionId || issuer || 'Unspecified'),
    };
  }

  function nftVerificationSummary(nft) {
    const v = nft?.verification || {};
    const hashOk = v.metadata_hash_verified;
    const issuerOk = v.issuer_matches_envelope;
    const sigOk = v.envelope_signature_verified;
    if (hashOk === false || issuerOk === false || sigOk === false) {
      return { state: 'mismatch', label: 'Verification mismatch', cls: 'rej', hashOk, issuerOk, sigOk };
    }
    if (hashOk === true && issuerOk === true && sigOk === true) {
      return { state: 'verified', label: 'Hash & issuer signed', cls: 'lvl', hashOk, issuerOk, sigOk };
    }
    return { state: 'unchecked', label: 'Metadata not checked', cls: 'part', hashOk: null, issuerOk: null, sigOk: null };
  }

  function nftOriginBadge(origin) {
    if (!origin || typeof origin !== 'object') {
      return { mode: 'native', label: 'Native L1v2 mint', cls: 'ok' };
    }
    const mode = String(origin.retirement_mode || '').toLowerCase();
    if (mode === 'pin_only' || mode === 'retirement_mode_pin_only' || mode === '2') {
      return { mode: 'pin_only', label: 'Recorded Provenance', cls: 'part' };
    }
    return { mode: 'burn_first', label: 'Migrated (burn-first)', cls: 'lvl' };
  }

  // ── Pillar 6: Identity link classification & search routing (C4 Train B) ───
  const CONSENSUS_LINK_KINDS = new Set(['validator_node', 'old_chain_account', 'agent_controller']);

  function classifyIdentityLinks(links, validatorStatusById) {
    const consensusVerified = [];
    const clientVerified = [];
    for (const raw of links || []) {
      const kind = String(raw.kind || '').toLowerCase();
      const isConsensus = raw.consensus_verified === true && CONSENSUS_LINK_KINDS.has(kind);
      const pending = String(raw.status || '').toLowerCase() === 'pending_reconfirmation';
      let validatorState = null;
      let staleValidator = false;
      if (kind === 'validator_node') {
        validatorState = raw.validator_access_state || validatorStatusById?.[raw.target] || null;
        if (validatorState && ['lapsed', 'revoked', 'inactive', 'removed'].includes(String(validatorState).toLowerCase())) {
          staleValidator = true;
        }
        if (raw.stale_validator === true) staleValidator = true;
      }
      const enriched = {
        ...raw,
        kind,
        consensus_verified: isConsensus,
        pending_reconfirmation: pending,
        validator_state: validatorState,
        stale_validator: staleValidator,
      };
      if (isConsensus) consensusVerified.push(enriched);
      else clientVerified.push(enriched);
    }
    return { consensusVerified, clientVerified };
  }

  function resolveDirectSearchRoute(query) {
    const q = String(query || '').trim();
    if (!q) return null;
    if (/^pf[0-9a-f]{40}$/i.test(q)) return `/account/${q.toLowerCase()}`;
    if (/^npub1[0-9a-z]{20,}$/i.test(q)) return `/identity/${encodeURIComponent(q.toLowerCase())}`;
    if (/^[a-z0-9][a-z0-9._-]{0,30}[a-z0-9]@[a-z0-9.-]+\.[a-z]{2,}$/i.test(q)) {
      return `/identity/${encodeURIComponent(q.toLowerCase())}`;
    }
    if (/^@[a-z0-9][a-z0-9._-]{0,30}[a-z0-9]$/i.test(q)) {
      return `/identity/${encodeURIComponent(q.slice(1).toLowerCase() + '@tasknode.postfiat.org')}`;
    }
    if (/^[0-9a-f]{64}$/i.test(q)) return `/identity/${q.toLowerCase()}`;
    if (/^nft:([0-9a-f]{96})$/i.test(q)) return `/nft/${q.slice(4).toLowerCase()}`;
    if (/^gov:([a-z0-9._-]+)$/i.test(q)) return `/governance/${encodeURIComponent(q.slice(4))}`;
    return null;
  }

  return {
    MEMO_TYPE_PF_PTR_HEX,
    MEMO_FORMAT_V5_HEX,
    MEMO_FORMAT_V4_HEX,
    POINTER_FLAG_PRIVATE,
    POINTER_FLAG_PUBLIC,
    POINTER_FLAG_EPHEMERAL,
    POINTER_FLAG_TOMBSTONE,
    POINTER_FLAG_MULTIPART,
    POINTER_FLAG_SEALED,
    CONTENT_KIND_LABELS,
    MAX_PUBLIC_PREVIEW_BYTES,
    NFT_MIGRATED_SERIAL_BIT,
    escHtml,
    validatePointerFlags,
    detectPointerMemo,
    normalizeVisibility,
    classifyMessageBadge,
    truncatePublicPreview,
    safeIpfsGatewayUrl,
    isAuthorizedGovernanceAnchor,
    isMigratedNftSerial,
    formatNftCollectionIdentity,
    nftVerificationSummary,
    nftOriginBadge,
    classifyIdentityLinks,
    resolveDirectSearchRoute,
  };
});
