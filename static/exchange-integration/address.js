// Copied verbatim from github.com/postfiatorg/postfiatl1v2 wallet-extension/lib/address.js at 8bf0fafae.
// Tested against docs/fixtures/addresses/pftl-address-vectors-v1.json (see test-address.mjs).
// PFTL account address parsing and checksummed display.
//
// Canonical form: "pf" + 40 lowercase hex characters. That is the only form
// that appears on chain and in signed transactions.
//
// Optional checksum (spec: docs/wallets/address-format.md):
//   h = SHA3-256("postfiat.address.checksum.v1" || 0x00 || lowercase 40-hex)
//   hex character i is uppercased when it is a letter a-f and nibble i of h
//   (high nibble of h[i/2] for even i, low nibble for odd i) is >= 8.
//
// parseAddress accepts the all-lowercase form and the exact checksummed form
// and returns the canonical lowercase form. Mirrors
// crates/crypto_provider/src/address.rs and the published vectors in
// docs/fixtures/addresses/pftl-address-vectors-v1.json.

export const ADDRESS_PREFIX = 'pf';
export const ADDRESS_HEX_LEN = 40;
export const ADDRESS_LEN = 42;
export const ADDRESS_CHECKSUM_DOMAIN = 'postfiat.address.checksum.v1';

const MESSAGES = {
  missing_prefix: 'address must start with `pf`',
  uppercase_prefix: 'address prefix must be lowercase `pf`',
  wrong_length: 'address must be `pf` followed by exactly 40 hex characters',
  non_hex: 'address must be `pf` followed by 40 hex characters (0-9, a-f)',
  bad_checksum:
    'address checksum does not match; use the all-lowercase form or the exact checksummed form',
};

export class AddressError extends Error {
  constructor(reason) {
    super(MESSAGES[reason] || reason);
    this.name = 'AddressError';
    this.reason = reason;
    this.malformed = reason !== 'bad_checksum';
  }
}

// Keccak-f[1600] with 64-bit BigInt lanes. Only used on 40-byte inputs, so
// clarity is preferred over speed.
const MASK_64 = (1n << 64n) - 1n;
const ROUND_CONSTANTS = [
  0x0000000000000001n, 0x0000000000008082n, 0x800000000000808an, 0x8000000080008000n,
  0x000000000000808bn, 0x0000000080000001n, 0x8000000080008081n, 0x8000000000008009n,
  0x000000000000008an, 0x0000000000000088n, 0x0000000080008009n, 0x000000008000000an,
  0x000000008000808bn, 0x800000000000008bn, 0x8000000000008089n, 0x8000000000008003n,
  0x8000000000008002n, 0x8000000000000080n, 0x000000000000800an, 0x800000008000000an,
  0x8000000080008081n, 0x8000000000008080n, 0x0000000080000001n, 0x8000000080008008n,
];
// ROTATIONS[x + 5 * y]
const ROTATIONS = [
  0, 1, 62, 28, 27,
  36, 44, 6, 55, 20,
  3, 10, 43, 25, 39,
  41, 45, 15, 21, 8,
  18, 2, 61, 56, 14,
];

function rotl64(value, shift) {
  const s = BigInt(shift);
  if (s === 0n) return value;
  return ((value << s) | (value >> (64n - s))) & MASK_64;
}

function keccakF1600(state) {
  const c = new Array(5);
  const b = new Array(25);
  for (let round = 0; round < 24; round += 1) {
    for (let x = 0; x < 5; x += 1) {
      c[x] = state[x] ^ state[x + 5] ^ state[x + 10] ^ state[x + 15] ^ state[x + 20];
    }
    for (let x = 0; x < 5; x += 1) {
      const d = c[(x + 4) % 5] ^ rotl64(c[(x + 1) % 5], 1);
      for (let y = 0; y < 25; y += 5) state[x + y] ^= d;
    }
    for (let x = 0; x < 5; x += 1) {
      for (let y = 0; y < 5; y += 1) {
        b[y + 5 * ((2 * x + 3 * y) % 5)] = rotl64(state[x + 5 * y], ROTATIONS[x + 5 * y]);
      }
    }
    for (let x = 0; x < 5; x += 1) {
      for (let y = 0; y < 25; y += 5) {
        state[x + y] = b[x + y] ^ (~b[((x + 1) % 5) + y] & MASK_64 & b[((x + 2) % 5) + y]);
      }
    }
    state[0] ^= ROUND_CONSTANTS[round];
  }
}

/** SHA3-256 (FIPS 202) of a Uint8Array. */
export function sha3_256(bytes) {
  const rate = 136;
  const padded = new Uint8Array((Math.floor(bytes.length / rate) + 1) * rate);
  padded.set(bytes);
  padded[bytes.length] ^= 0x06;
  padded[padded.length - 1] ^= 0x80;
  const state = new Array(25).fill(0n);
  for (let offset = 0; offset < padded.length; offset += rate) {
    for (let lane = 0; lane < rate / 8; lane += 1) {
      let value = 0n;
      for (let index = 7; index >= 0; index -= 1) {
        value = (value << 8n) | BigInt(padded[offset + lane * 8 + index]);
      }
      state[lane] ^= value;
    }
    keccakF1600(state);
  }
  const out = new Uint8Array(32);
  for (let index = 0; index < 32; index += 1) {
    out[index] = Number((state[index >> 3] >> BigInt(8 * (index & 7))) & 0xffn);
  }
  return out;
}

function asciiBytes(text) {
  const out = new Uint8Array(text.length);
  for (let index = 0; index < text.length; index += 1) out[index] = text.charCodeAt(index);
  return out;
}

function checksumHex(lowercaseHex) {
  const domain = asciiBytes(ADDRESS_CHECKSUM_DOMAIN);
  const hex = asciiBytes(lowercaseHex);
  const preimage = new Uint8Array(domain.length + 1 + hex.length);
  preimage.set(domain);
  preimage.set(hex, domain.length + 1);
  const digest = sha3_256(preimage);
  let out = '';
  for (let index = 0; index < lowercaseHex.length; index += 1) {
    const character = lowercaseHex[index];
    const byte = digest[index >> 1];
    const nibble = index % 2 === 0 ? byte >> 4 : byte & 0x0f;
    out += character >= 'a' && character <= 'f' && nibble >= 8 ? character.toUpperCase() : character;
  }
  return out;
}

function addressHexPart(input) {
  if (typeof input !== 'string' || input.length < 2) throw new AddressError('missing_prefix');
  const prefix = input.slice(0, 2);
  if (prefix !== ADDRESS_PREFIX) {
    throw new AddressError(prefix.toLowerCase() === ADDRESS_PREFIX ? 'uppercase_prefix' : 'missing_prefix');
  }
  // Non-ASCII input is rejected before the length check so the reason does
  // not depend on how an implementation counts string length.
  if (/[^\x00-\x7f]/.test(input)) throw new AddressError('non_hex');
  if (input.length !== ADDRESS_LEN) throw new AddressError('wrong_length');
  const hex = input.slice(2);
  if (!/^[0-9a-fA-F]{40}$/.test(hex)) throw new AddressError('non_hex');
  return hex;
}

/**
 * Parses human input (lowercase or exactly checksummed) and returns the
 * canonical lowercase address. Does not trim; trim pasted text first.
 */
export function parseAddress(input) {
  const hex = addressHexPart(input);
  const lowercase = hex.toLowerCase();
  if (hex !== lowercase && checksumHex(lowercase) !== hex) {
    throw new AddressError('bad_checksum');
  }
  return ADDRESS_PREFIX + lowercase;
}

/** True only for "pf" + 40 lowercase hex characters. */
export function isCanonicalAddress(value) {
  return typeof value === 'string' && /^pf[0-9a-f]{40}$/.test(value);
}

/** Checksummed display form of an accepted address. */
export function checksumAddress(address) {
  const canonical = parseAddress(address);
  return ADDRESS_PREFIX + checksumHex(canonical.slice(2));
}

/** Checksummed form when the value is an accepted address, else unchanged. */
export function displayAddress(value) {
  try {
    return checksumAddress(value);
  } catch {
    return value;
  }
}
