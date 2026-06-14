#!/usr/bin/env python3
"""Verify the public Proof of Disclosed Leverage artifact.

This script is intentionally self-contained: it uses only Python's standard
library and Arbitrum JSON-RPC. It does not require the StakeHub repository or
private proof witnesses.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


DEFAULT_RPC_URL = "https://arb1.arbitrum.io/rpc"
VERIFIER = "0x3F40563A3D786d008854f046A78Cc2216ceAC3e1"
LATEST_SELECTOR = "0x52bfe789"
PROGRAM_VKEY_SELECTOR = "0x1ddb5d29"

EXPECTED = {
    "schema_version": 2,
    "mode": 1,
    "policy_hash": "0x8fcf3cd44c8180744563e85579ed91b7fd3882e560dc41ea4dc0c18cb01f289d",
    "program_vkey": "0x004d1cd3f36e6ea60662af428edbea9d3aba45f04fe496da909d6bbe9fbf9258",
    "spot_total_usd_e8": 2052942777620,
    "spot_locked_usd_e8": 1079480440653,
    "spot_unlocked_usd_e8": 973462336967,
    "cash_total_usd_e8": 331923955500,
    "cash_locked_usd_e8": 323051509700,
    "cash_unlocked_usd_e8": 8872445800,
    "perp_notional_total_usd_e8": 2423326655000,
    "liability_usd_e8": 19997391450,
    "leg_count": 6,
    "position_row_count": 0,
    "legs": [
        {"kind": 1, "quantity_tier": 1, "valuation_tier": 1},
        {"kind": 2, "quantity_tier": 1, "valuation_tier": 2},
        {"kind": 3, "quantity_tier": 1, "valuation_tier": 2},
        {"kind": 4, "quantity_tier": 1, "valuation_tier": 1},
        {"kind": 5, "quantity_tier": 2, "valuation_tier": 2},
        {"kind": 6, "quantity_tier": 1, "valuation_tier": 2},
    ],
}

LEG_KIND = {
    1: "aave",
    2: "evm_spot",
    3: "xmr_reserve",
    4: "hyperliquid",
    5: "solana_stake",
    6: "near_stake",
}
TIER = {1: "cryptographic", 2: "attested"}


@dataclass(frozen=True)
class Latest:
    schema_version: int
    mode: int
    policy_hash: str
    totals: dict[str, int]
    leg_count: int
    position_row_count: int
    legs: list[dict[str, Any]]


def rpc_call(rpc_url: str, method: str, params: list[Any]) -> Any:
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    request = urllib.request.Request(
        rpc_url,
        data=payload,
        headers={
            "content-type": "application/json",
            "user-agent": "postfiat-proof-of-leverage-verifier/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.loads(response.read())
    except urllib.error.URLError as error:
        raise RuntimeError(f"RPC request failed: {error}") from error
    if "error" in body:
        raise RuntimeError(f"RPC error: {body['error']}")
    return body["result"]


def eth_call(rpc_url: str, to: str, data: str) -> str:
    return rpc_call(rpc_url, "eth_call", [{"to": to, "data": data}, "latest"])


def words(hex_data: str) -> list[str]:
    raw = hex_data.removeprefix("0x")
    if len(raw) % 64:
        raise ValueError("ABI return length is not word-aligned")
    return [raw[i : i + 64] for i in range(0, len(raw), 64)]


def uint(word: str) -> int:
    return int(word, 16)


def bytes32(word: str) -> str:
    return "0x" + word.lower()


def decode_latest(hex_data: str) -> Latest:
    w = words(hex_data)
    if len(w) < 23:
        raise ValueError("latest() return is too short")

    totals = {
        "spot_total_usd_e8": uint(w[3]),
        "spot_locked_usd_e8": uint(w[4]),
        "spot_unlocked_usd_e8": uint(w[5]),
        "cash_total_usd_e8": uint(w[6]),
        "cash_locked_usd_e8": uint(w[7]),
        "cash_unlocked_usd_e8": uint(w[8]),
        "perp_notional_total_usd_e8": uint(w[9]),
        "liability_usd_e8": uint(w[10]),
    }
    latest = Latest(
        schema_version=uint(w[0]),
        mode=uint(w[1]),
        policy_hash=bytes32(w[2]),
        totals=totals,
        leg_count=uint(w[19]),
        position_row_count=uint(w[20]),
        legs=[],
    )

    legs_offset_words = uint(w[21]) // 32
    if legs_offset_words >= len(w):
        raise ValueError("leg disclosure offset is outside return data")
    legs_len = uint(w[legs_offset_words])
    legs: list[dict[str, Any]] = []
    cursor = legs_offset_words + 1
    for _ in range(legs_len):
        if cursor + 10 > len(w):
            raise ValueError("leg disclosure array is truncated")
        legs.append(
            {
                "kind": uint(w[cursor]),
                "quantity_tier": uint(w[cursor + 1]),
                "valuation_tier": uint(w[cursor + 2]),
                "spot_locked_usd_e8": uint(w[cursor + 3]),
                "spot_unlocked_usd_e8": uint(w[cursor + 4]),
                "cash_locked_usd_e8": uint(w[cursor + 5]),
                "cash_unlocked_usd_e8": uint(w[cursor + 6]),
                "perp_notional_usd_e8": uint(w[cursor + 7]),
                "liability_usd_e8": uint(w[cursor + 8]),
                "metadata_hash": bytes32(w[cursor + 9]),
            }
        )
        cursor += 10
    return Latest(
        schema_version=latest.schema_version,
        mode=latest.mode,
        policy_hash=latest.policy_hash,
        totals=latest.totals,
        leg_count=latest.leg_count,
        position_row_count=latest.position_row_count,
        legs=legs,
    )


def verify(latest: Latest, program_vkey: str) -> list[str]:
    failures: list[str] = []
    checks = {
        "schema_version": latest.schema_version,
        "mode": latest.mode,
        "policy_hash": latest.policy_hash,
        "program_vkey": program_vkey.lower(),
        "leg_count": latest.leg_count,
        "position_row_count": latest.position_row_count,
        **latest.totals,
    }
    for key, expected in EXPECTED.items():
        if key == "legs":
            continue
        actual = checks.get(key)
        if actual != expected:
            failures.append(f"{key}: expected {expected}, got {actual}")

    if len(latest.legs) != len(EXPECTED["legs"]):
        failures.append(f"legs length: expected {len(EXPECTED['legs'])}, got {len(latest.legs)}")
    else:
        for index, expected_leg in enumerate(EXPECTED["legs"]):
            actual = latest.legs[index]
            for key, expected in expected_leg.items():
                if actual[key] != expected:
                    failures.append(
                        f"leg[{index}].{key}: expected {expected}, got {actual[key]}"
                    )
    return failures


def format_usd(e8: int) -> str:
    return f"${e8 / 100_000_000:,.2f}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rpc-url", default=DEFAULT_RPC_URL)
    parser.add_argument("--verifier", default=VERIFIER)
    args = parser.parse_args()

    latest = decode_latest(eth_call(args.rpc_url, args.verifier, LATEST_SELECTOR))
    program_vkey = bytes32(words(eth_call(args.rpc_url, args.verifier, PROGRAM_VKEY_SELECTOR))[0])
    failures = verify(latest, program_vkey)

    print(f"verifier={args.verifier}")
    print(f"program_vkey={program_vkey}")
    print(f"policy_hash={latest.policy_hash}")
    for key, value in latest.totals.items():
        print(f"{key}={value} ({format_usd(value)})")
    print(f"leg_count={latest.leg_count}")
    print("legs:")
    for leg in latest.legs:
        print(
            f"  {LEG_KIND.get(leg['kind'], leg['kind'])}: "
            f"quantity={TIER.get(leg['quantity_tier'], leg['quantity_tier'])} "
            f"valuation={TIER.get(leg['valuation_tier'], leg['valuation_tier'])}"
        )

    if failures:
        print("verification=FAIL", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1
    print("verification=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
