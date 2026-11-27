import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const C = require('../static/explorer/explorer-contracts.js');

const PINNED_PAYOUT_PUBKEY = 'a1'.repeat(64);
const PINNED_PAYOUT_ACCOUNT = 'pf1111111111111111111111111111111111111111';
const OUTSIDER_ACCOUNT = 'pf9999999999999999999999999999999999999999';

test('pf.ptr v5 and legacy v4 memo detection + mutually exclusive visibility flags', () => {
  assert.deepEqual(
    C.detectPointerMemo({ memo_type: '70662e707472', memo_format: '7635', memo_data: '0a24' }),
    { version: 'v5', legacy: false, data_hex: '0a24' },
  );
  assert.deepEqual(
    C.detectPointerMemo({ memo_type: '70662E707472', memo_format: '7634', memo_data: '0A3B' }),
    { version: 'v4', legacy: true, data_hex: '0A3B' },
  );
  assert.equal(C.detectPointerMemo({ memo_type: '74657374', memo_format: '7635', memo_data: '' }), null);

  assert.equal(C.validatePointerFlags(C.POINTER_FLAG_PUBLIC).visibility, 'public');
  assert.equal(C.validatePointerFlags(C.POINTER_FLAG_PRIVATE | C.POINTER_FLAG_MULTIPART).visibility, 'private');
  assert.deepEqual(C.validatePointerFlags(C.POINTER_FLAG_PRIVATE | C.POINTER_FLAG_MULTIPART).modifiers, ['multipart']);
  assert.equal(C.validatePointerFlags(C.POINTER_FLAG_SEALED).visibility, 'sealed');
  // Reject simultaneous visibility bits or unsupported bits
  assert.equal(C.validatePointerFlags(C.POINTER_FLAG_PUBLIC | C.POINTER_FLAG_PRIVATE).valid, false);
  assert.equal(C.validatePointerFlags(0x00).valid, false);
  assert.equal(C.validatePointerFlags(0x40 | C.POINTER_FLAG_PUBLIC).valid, false);
});

test('Spoof-proof Task reward badge enforces verified sender + private + pinned Task Node payout key', () => {
  const pinned = {
    tasknode_payout_pubkeys: [PINNED_PAYOUT_PUBKEY],
    tasknode_payout_accounts: [PINNED_PAYOUT_ACCOUNT],
  };

  // Legitimate official Task Node FastPay reward payout
  const legit = C.classifyMessageBadge({
    schema_name: 'pf.reward.v1',
    content_kind: 6,
    visibility: 'private',
    sender_verified: true,
    sender_pubkey_hex: PINNED_PAYOUT_PUBKEY,
    sender_account: PINNED_PAYOUT_ACCOUNT,
  }, pinned);
  assert.equal(legit.is_task_reward, true);
  assert.equal(legit.label, 'Task reward');
  assert.equal(legit.spoofed_reward, false);

  // Outsider spoofing pf.reward.v1 MUST render strictly as Private message
  const spoofed = C.classifyMessageBadge({
    schema_name: 'pf.reward.v1',
    content_kind: 6,
    visibility: 'private',
    sender_verified: true,
    sender_account: OUTSIDER_ACCOUNT,
    sender_pubkey_hex: 'ff'.repeat(64),
  }, pinned);
  assert.equal(spoofed.is_task_reward, false);
  assert.equal(spoofed.label, 'Private message');
  assert.equal(spoofed.spoofed_reward, true);

  // Unverified signature claiming pinned payout account MUST NOT get Task reward badge
  const unverified = C.classifyMessageBadge({
    schema_name: 'pf.reward.v1',
    visibility: 'private',
    sender_verified: false,
    sender_account: PINNED_PAYOUT_ACCOUNT,
  }, pinned);
  assert.equal(unverified.is_task_reward, false);
  assert.equal(unverified.label, 'Private message');

  // Public or sealed pf.reward.v1 MUST NOT get Task reward badge (Pillar 2 locks Private)
  const sealedReward = C.classifyMessageBadge({
    schema_name: 'pf.reward.v1',
    visibility: 'sealed',
    sender_verified: true,
    pinned_tasknode_payout_key_matched: true,
  });
  assert.equal(sealedReward.is_task_reward, false);
  assert.equal(sealedReward.label, 'Sealed message');
});

test('Governance Archive verifies pinned AuthorityBinding', () => {
  const founder = 'pf1111111111111111111111111111111111111111';
  const session = {
    session_id: 'gov-2026-11-27-001',
    authority_verified: true,
    anchor_account: founder,
    authority: { authorized_accounts: [founder], threshold: 1, total_signers: 1 },
  };
  assert.equal(C.isAuthorizedGovernanceAnchor(session, [founder]), true);
  assert.equal(C.isAuthorizedGovernanceAnchor({ ...session, anchor_account: OUTSIDER_ACCOUNT }, [founder]), false);
  assert.equal(C.isAuthorizedGovernanceAnchor({ ...session, authority_verified: false }, [founder]), false);
});

test('NFT bit-63 serial partition, issuer+collection pairing, one-hash verification, and pin-only provenance', () => {
  // Contract C1 vector V8 migrated_serial_uint64
  assert.equal(C.isMigratedNftSerial('16447061904156710842'), true);
  assert.equal(C.isMigratedNftSerial('9223372036854775809'), true);
  assert.equal(C.isMigratedNftSerial('42'), false);
  assert.equal(C.isMigratedNftSerial(1), false);

  const pair = C.formatNftCollectionIdentity({
    issuer: 'pf9999999999999999999999999999999999999999',
    collection_id: 'tasknode-profile-v1',
    metadata: { collection: { name: 'Post Fiat Profile NFTs' } },
  });
  assert.ok(pair.display_pair.includes('tasknode-profile-v1'));
  assert.ok(pair.display_pair.includes('pf9999999999999999999999999999999999999999'));

  assert.equal(
    C.nftVerificationSummary({
      verification: { metadata_hash_verified: true, issuer_matches_envelope: true, envelope_signature_verified: true },
    }).state,
    'verified',
  );
  assert.equal(
    C.nftVerificationSummary({
      verification: { metadata_hash_verified: true, issuer_matches_envelope: false, envelope_signature_verified: true },
    }).state,
    'mismatch',
  );
  assert.equal(C.nftVerificationSummary({}).state, 'unchecked');

  assert.equal(C.nftOriginBadge({ retirement_mode: 'RETIREMENT_MODE_BURN_FIRST' }).label, 'Migrated (burn-first)');
  assert.equal(C.nftOriginBadge({ retirement_mode: 'RETIREMENT_MODE_PIN_ONLY' }).label, 'Recorded Provenance');
  assert.equal(C.nftOriginBadge(null).label, 'Native L1v2 mint');
});

test('Identity link separation (consensus vs client-verified), stale validator, and direct search routing', () => {
  const { consensusVerified, clientVerified } = C.classifyIdentityLinks([
    { link_id: 'a', kind: 'validator_node', target: 'validator-01', consensus_verified: true, status: 'active' },
    { link_id: 'b', kind: 'agent_controller', target: PINNED_PAYOUT_ACCOUNT, consensus_verified: true, status: 'pending_reconfirmation' },
    { link_id: 'c', kind: 'custom_nip05', target: 'alice@example.com', consensus_verified: false, status: 'active' },
    // Even if malformed API flags consensus_verified=true on evm_address, contract restricts consensus links to 3 kinds
    { link_id: 'd', kind: 'evm_address', target: '0x1234', consensus_verified: true, status: 'active' },
  ], { 'validator-01': 'lapsed' });

  assert.equal(consensusVerified.length, 2);
  assert.equal(consensusVerified[0].stale_validator, true);
  assert.equal(consensusVerified[1].pending_reconfirmation, true);
  assert.equal(clientVerified.length, 2);

  assert.equal(C.resolveDirectSearchRoute('goodalexander@tasknode.postfiat.org'), '/identity/goodalexander%40tasknode.postfiat.org');
  assert.equal(C.resolveDirectSearchRoute('@goodalexander'), '/identity/goodalexander%40tasknode.postfiat.org');
  assert.equal(C.resolveDirectSearchRoute(PINNED_PAYOUT_ACCOUNT), `/account/${PINNED_PAYOUT_ACCOUNT}`);
  assert.equal(C.resolveDirectSearchRoute('3bf0c63fcb93463407af97a5e5ee64fa883d107ef9e558472c4eb9aaaefa459d'), '/identity/3bf0c63fcb93463407af97a5e5ee64fa883d107ef9e558472c4eb9aaaefa459d');
});

test('XSS escaping, oversize preview cap, and safe ipfs:// gateway validation', () => {
  assert.equal(C.escHtml('<script>alert("x")</script>'), '&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;');
  assert.equal(C.truncatePublicPreview('a'.repeat(70000)).truncated, true);
  assert.equal(C.truncatePublicPreview('a'.repeat(70000)).text.length, C.MAX_PUBLIC_PREVIEW_BYTES);
  assert.equal(
    C.safeIpfsGatewayUrl('ipfs://bafkreibkzqqj3knpgew6r2osaf24a5ncfmy3gknd43mfnxwjz5teg3kshu'),
    'https://ipfs.io/ipfs/bafkreibkzqqj3knpgew6r2osaf24a5ncfmy3gknd43mfnxwjz5teg3kshu',
  );
  assert.equal(C.safeIpfsGatewayUrl('javascript:alert(1)'), null);
  assert.equal(C.safeIpfsGatewayUrl('ipfs://../evil'), null);
});
