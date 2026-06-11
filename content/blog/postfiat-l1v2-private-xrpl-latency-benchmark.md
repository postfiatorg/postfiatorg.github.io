---
title: "Post Fiat Latency Series I: Certified Finality vs. Validated Ledgers"
date: 2026-06-09T00:00:00Z
summary: "A local one-host, six-validator study comparing Post Fiat L1 v2 certified applied-batch receipts with private rippled validated-ledger inclusion: 88.083 ms p50 for the tested Post Fiat full-vote path, plus an XRPL timer-compression matrix showing median gains and tail damage."
aliases:
  - /post-fiat-latency-series-i/
  - /posts/post-fiat-latency-series-i/
  - /postfiat-l1v2-private-xrpl-latency-benchmark/
  - /posts/postfiat-l1v2-private-xrpl-latency-benchmark/
categories:
  - Post Fiat Research
tags:
  - Post Fiat
  - Research
  - L1
  - XRPL
  - Latency
  - Finality
  - Benchmark
---

A user does not experience consensus as a protocol diagram. A user experiences consensus as a wait.

They sign a transfer, press send, and wait for the application to know whether the transaction is final. Post Fiat is an L1 protocol design whose v2 native-transfer path returns finality from a certified applied batch rather than waiting on an XRPL-style validated-ledger clock.

This first latency study asks one narrow question:

```text
After a wallet submits a native transfer, when can the client observe it as final?
```

## Claim boundary, before the numbers

This article reports a **local, one-host, six-validator, sequential native-transfer benchmark**. It is not a WAN result, not a public-mainnet result, not a throughput result, and not a claim of global L1 supremacy.

Two other boundaries matter:

- **Different finality surfaces.** Post Fiat is measured at a certified applied-batch receipt. Private `rippled` is measured at XRPL validated-ledger inclusion. Those are the closest client-visible local-finality surfaces in this packet, but they are not byte-identical protocol events. No same-surface apples-to-apples comparison is available here.
- **Evidence status.** The evidence is self-published: public raw reports, aggregate files, command logs, lab book, methodology, charts, and SHA256 manifests are provided. The hashes bind this article to those artifacts; they do not constitute independent replication.

The claim-critical packet ran **five sessions per lane** and **1000 sequential signed transfers per session**. The reported p99 values are empirical packet tails, not population tail guarantees.

## TL;DR

In the selected local matched packet:

- Post Fiat L1 v2 **full-vote certified finality** measured `88.083 ms` p50 and `104.705 ms` p95.
- The selected reduced-timing private `rippled` control, `close_750ms`, measured `883.507 ms` p50 at the XRPL validated-ledger boundary.
- Stock private `rippled` measured `3000.565 ms` p50 at the same validated-ledger boundary.
- The aggressive `close_250ms` `rippled` stress lane reached `573.367 ms` p50, but its tail expanded to `15345.814 ms` p95 and `19918.846 ms` p99.

The p50 gaps are `10.03x` versus selected `close_750ms` private `rippled` and `34.07x` versus stock private `rippled`, **with the finality-surface boundary attached**: certified applied-batch receipt versus validated-ledger inclusion. They are client-visible completion ratios, not same-phase internal consensus-speed ratios.

Quote-safe version:

```text
In a local one-host, six-validator, sequential signed-transfer benchmark,
Post Fiat L1 v2 full-vote certified applied-batch finality measured
88.083 ms p50 and 104.705 ms p95, while private rippled validated-ledger
inclusion measured 883.507 ms p50 for the selected close_750ms profile
and 3000.565 ms p50 for stock. These are cross-surface client-visible
completion numbers, not same-phase consensus-speed ratios.
```

## Reader path

- **Result card:** the measured lanes, finality surfaces, and ratios.
- **Method:** what was run, what was excluded, and how to audit the packet.
- **XRPL timing:** why validated-ledger finality naturally contains a ledger-cycle wait.
- **Timer compression:** why reduced `rippled` timers improved medians before damaging tails.
- **Post Fiat path:** what a certified applied-batch receipt does and does not establish.
- **Appendices:** XRPL expiration/load behavior and peer context.

## Result card

### Finality surfaces

```text
Post Fiat certified-batch path

wallet submits signed native transfer
  -> local admission
  -> one-transfer batch
  -> signed proposal
  -> validator votes
  -> quorum/full-vote certificate
  -> local application
  -> finality receipt                         [timer stops]


Private rippled validated-ledger path

wallet submits signed payment
  -> current open ledger
  -> ledger close
  -> establish/proposal convergence
  -> accept/apply
  -> trusted validations
  -> payment observed in validated ledger      [timer stops]
```

| System | Timer | Starts when | Stops when | What the user learns |
|---|---|---|---|---|
| Post Fiat L1 v2 | `wallet_to_finality_ms` | the wallet submits a signed native transfer | the node returns a finality receipt for a certified and locally applied batch | this transfer is final under the certified-batch path tested here |
| Private `rippled` | `submit_to_validated_ms` | the wallet submits a signed payment | the payment appears in a validated private XRPL ledger | this payment is final at XRPL's validated-ledger boundary |

### Aggregate results

The conservative Post Fiat headline lane is full-vote, not quorum-fast. In this packet, the full-vote lane waited for all six validator votes before returning.

| Lane | Count | p50 ms | p95 ms | p99 ms | Mean ms |
|---|---:|---:|---:|---:|---:|
| Post Fiat L1 v2 full-vote | 5000 | 88.083 | 104.705 | 110.593 | 87.937 |
| Post Fiat L1 v2 quorum-fast | 5000 | 83.936 | 100.362 | 106.561 | 83.188 |
| Selected `close_750ms` private `rippled` | 5000 | 883.507 | 984.493 | 1818.378 | 941.539 |
| Aggressive `close_250ms` private `rippled` stress lane | 5000 | 573.367 | 15345.814 | 19918.846 | 1573.954 |
| Stock private `rippled` | 5000 | 3000.565 | 3054.779 | 6010.940 | 3121.950 |

![Aggregate p50 and p95 chart for the selected matched packet](/benchmarks/postfiat-l1v2-selected-xrpl-matched-latency-postfiat-selected-xrpl-v4-20260609T052252Z/latency-bars.svg)

![Latency CDF for all rounds in the selected matched packet](/benchmarks/postfiat-l1v2-selected-xrpl-matched-latency-postfiat-selected-xrpl-v4-20260609T052252Z/latency-cdf.svg)

### Ratios, with the boundary attached

| Comparison | p50 ratio | Correct reading | Incorrect reading |
|---|---:|---|---|
| Selected `close_750ms` private `rippled` validated-ledger inclusion vs. Post Fiat full-vote certified applied-batch receipt | `10.03x` | In this local packet, the wallet observed Post Fiat full-vote certified finality sooner than selected private `rippled` validated-ledger inclusion. | Post Fiat consensus internals are `10.03x` faster than `rippled` internals. |
| Stock private `rippled` validated-ledger inclusion vs. Post Fiat full-vote certified applied-batch receipt | `34.07x` | In this local packet, the wallet observed Post Fiat full-vote certified finality sooner than stock private `rippled` validated-ledger inclusion. | Post Fiat is globally `34.07x` faster than XRPL or all L1s. |

## Method in one page

The selected matched packet is:

[Post Fiat L1 v2 / selected private XRPL matched latency packet](/benchmarks/postfiat-l1v2-selected-xrpl-matched-latency-postfiat-selected-xrpl-v4-20260609T052252Z/)

| Item | Selected matched packet |
|---|---|
| Run ID | `postfiat-selected-xrpl-v4-20260609T052252Z` |
| Validators | 6 |
| Sessions per lane | 5 |
| Sequential transfers per session | 1000 |
| Post Fiat lanes | `postfiat_full_vote_current`, `postfiat_quorum_fast_current` |
| XRPL lanes | `xrpl_stock`, `xrpl_tuned_selected`, `xrpl_aggressive_250ms` |
| Selected tuned XRPL profile | `close_750ms` |
| Selected tuned XRPL classification | `strained` |
| Aggressive XRPL stress profile | `close_250ms` |
| Lane ordering | rotated by session to reduce ordering, thermal, and cache effects |
| Post Fiat measurement window | wallet quote/sign/submit through certified and locally applied finality receipt |
| XRPL measurement window | JSON-RPC submit until the payment is observed in a validated private ledger |
| Packet charts | `latency-bars.svg`, `latency-cdf.svg` |
| Per-session data | `session-summary.csv` |
| Full setup metadata | `manifest.json` records host specs, build metadata, commits, binaries, command argv, and run matrix |

Generated node databases, generated validator keys, generated wallet material, and private logs are excluded from the public packet. Public raw reports are scanned for known private key and seed fields before the hash manifest is written.

The timing-matrix packet that selected `close_750ms` is:

[XRPL private timing stability matrix](/benchmarks/xrpl-private-timing-stability-matrix-xrpl-timing-stability-20260608T152301Z/)

That matrix tested stock private `rippled` plus reduced-timing profiles before the selected matched rerun.

## Why the XRPL control is a ledger-cycle measurement

For an application using XRPL semantics, a payment is not final merely because a server accepted it into an in-progress ledger. XRPL's documentation distinguishes provisional API results from final immutable results: a transaction is final only if it is signed, submitted, and accepted into a validated ledger version after consensus.[^xrpl-transactions][^xrpl-reliable]

That makes the `rippled` measurement a ledger-cycle measurement:

\[
T_{\text{submit}\rightarrow\text{validated}}
=
R_{\text{open}}
+
T_{\text{establish}}
+
T_{\text{build/apply}}
+
T_{\text{validation}}
+
T_{\text{client observe}}
+
T_{\text{queue}}
\]

| Term | Meaning |
|---|---|
| \(R_{\text{open}}\) | residual time between transaction submission and the next ledger close opportunity |
| \(T_{\text{establish}}\) | active consensus time while servers exchange proposals and converge on an exact transaction set |
| \(T_{\text{build/apply}}\) | time to apply the agreed transaction set to the prior validated ledger |
| \(T_{\text{validation}}\) | time for enough trusted validations to make the new ledger authoritative |
| \(T_{\text{client observe}}\) | RPC/client polling and observation time |
| \(T_{\text{queue}}\) | whole-ledger-cycle delay if the transaction is queued or postponed |

The `rippled` consensus documentation describes an `Open` phase, an `Establish` phase, and an `Accept` phase. The `Open` phase lets transactions build up in the open ledger; shortening it trades latency against throughput.[^rippled-consensus-open] The `Establish` phase is where servers share proposals, compare transaction sets, resolve disagreements, and declare consensus only after minimum timing and supermajority conditions are satisfied.[^rippled-consensus-establish]

The current stock `ConsensusParms` source sets:

| Parameter | Source value | Role |
|---|---:|---|
| `minConsensusPct` | `80%` | threshold above which consensus can be declared |
| `ledgerMinClose` | `2 s` | minimum close wait when there are open transactions |
| `ledgerMinConsensus` | `1950 ms` | minimum establish-phase wait to ensure participation |
| `ledgerGRANULARITY` | `1 s` | heartbeat/check cadence for state changes |
| `ledgerMaxConsensus` | `15 s` | maximum time spent pausing for laggards |
| `ledgerAbandonConsensus` | `120 s` | maximum time given to a consensus round before abandonment |

The source comments warn that these consensus parameters are “not meant to be changed arbitrarily.”[^consensus-parms]

A first-order stock median model is:

\[
T_{\text{stock}}
\approx
R_{\text{open}}
+
T_{\text{establish,min}}
+
\epsilon
\]

If transactions arrive roughly uniformly during an open-ledger interval \(C\), then:

\[
p50(R_{\text{open}}) \approx \frac{C}{2}
\]

With \(C = 2s\) and \(T_{\text{establish,min}} = 1.95s\):

\[
p50(T_{\text{stock}})
\approx
1.0s + 1.95s + \epsilon
\approx
3s
\]

The measured stock private `rippled` p50 was `3000.565 ms`. That is the expected consequence of measuring validated-ledger finality with an open-ledger wait and a minimum establish phase.

XRPL consensus has also been analyzed in safety/liveness and formal-model work; those papers are useful context, while the timing argument here is grounded in the documentation and source constants above.[^xrpl-analysis][^ripple-security][^mauri-formal]

## What timer compression did to private `rippled`

The timing matrix avoids a straw-man comparison against only stock private `rippled`. It tested stock private `rippled` plus `close_1500ms`, `close_1000ms`, `close_750ms`, `close_500ms`, and `close_250ms`, each with five sessions and 1000 sequential payments per session.

The matrix labels are preserved from the packet. In this article, `strained` means the profile was not stable but also not classified unstable; `unstable` is the packet label for profiles whose p99 jumped above 10 seconds with large `>=10s` tail counts.

| Profile | Matrix class | Count | p50 ms | p95 ms | p99 ms | Max ms | >=10s tails |
|---|---|---:|---:|---:|---:|---:|---:|
| `stock` | strained | 5000 | 3001.717 | 3054.519 | 6003.322 | 18008.493 | 4 |
| `close_1500ms` | strained | 5000 | 1811.109 | 1868.058 | 3628.837 | 14426.371 | 1 |
| `close_1000ms` | strained | 5000 | 1193.009 | 1296.206 | 2435.711 | 6048.540 | 0 |
| `close_750ms` | strained | 5000 | 884.057 | 1760.959 | 2689.190 | 5425.243 | 0 |
| `close_500ms` | unstable | 5000 | 623.259 | 1295.996 | 15860.846 | 44978.919 | 81 |
| `close_250ms` | unstable | 5000 | 572.713 | 15291.490 | 20311.839 | 61819.698 | 274 |

No reduced-timing profile met the frozen `stable` criteria. The fastest non-unstable profile was `close_750ms`, so it became the selected XRPL control in the matched rerun. The `close_250ms` lane is retained as an aggressive stress lane, not as the optimized XRPL control.

The central XRPL optimization result is simple:

```text
Reducing private rippled timing improved median latency.
Aggressive compression produced large tails.
No reduced-timing profile met the frozen stable criteria.
```

The selected matched packet repeated the same stress shape for `close_250ms`:

```text
close_250ms matched rerun:
  p50:   573.367 ms
  p95: 15345.814 ms
  p99: 19918.846 ms
```

The problem was not that stock private `rippled` failed. The problem is that the most direct route to making private `rippled` feel subsecond—compressing the ledger clock—produced unstable tails before the benchmark left loopback.

## Why the tail gets nonlinear

Timer compression is not linear optimization. It reduces the slack that hides propagation delay, proposal skew, transaction-set disagreement, scheduling noise, and validator lag.

A quorum system waits on an order statistic, not an average. Let \(D_i\) be the delay for validator \(i\) to receive, process, and respond within the relevant phase. If the protocol needs \(q\) of \(n\) participants by time \(t\), the simple binomial quorum model is:

\[
P(D_{(q)} \le t)
=
\sum_{k=q}^{n}
\binom{n}{k}
F(t)^k(1-F(t))^{n-k}
\]

For a six-node, five-of-six quorum-shaped path, this becomes:

\[
P(D_{(5)} \le t)=6p^5(1-p)+p^6
\]

Solving \(6p^5(1-p)+p^6=s\) numerically gives the per-validator-path percentile needed by time \(t\): \(s = 0.95\) gives roughly `93.7%`, and \(s = 0.99\) gives roughly `97.3%`. If the path waits for all six, the model is \(p^6=s\); system-level p95 then requires each individual path to be around `99.15%` by \(t\).

This simple model is not a full model of `rippled`; it explains why p50 and tail behavior can separate quickly. The median asks what happens when ordinary paths behave. The tail asks how often one validator, queue, scheduler, peer proposal, or transaction set arrives late enough to push the round into recovery behavior.

The matched packet makes the tail shape visible:

| Lane | p50 ms | p95 ms | p99 ms | p95/p50 | p99/p50 |
|---|---:|---:|---:|---:|---:|
| Post Fiat full-vote | 88.083 | 104.705 | 110.593 | 1.19x | 1.26x |
| Selected `close_750ms` `rippled` | 883.507 | 984.493 | 1818.378 | 1.11x | 2.06x |
| Stock private `rippled` | 3000.565 | 3054.779 | 6010.940 | 1.02x | 2.00x |
| Aggressive `close_250ms` `rippled` | 573.367 | 15345.814 | 19918.846 | 26.76x | 34.74x |

This is consistent with distributed-systems literature. Partial synchrony is the standard model for protocols that must work despite unknown or temporarily violated network-delay and processor-speed bounds; timer budgets have to dominate the delay distribution that appears in production, not only the delay distribution that appears in a quiet local test.[^dls] Tail-latency work reaches the same operational conclusion from a systems angle: small high-latency episodes can dominate perceived performance as systems scale or utilization rises.[^tail-at-scale]

A one-host benchmark removes real RTT, packet delay variation, clock skew across machines, noisy neighbors, kernel scheduling variance across hosts, and validator-placement differences. That makes a good one-host result useful as a critical-path measurement, but it also makes bad loopback tails important: a multi-host deployment has to absorb more delay distribution, not less.

## What the Post Fiat path changes

The benchmarked Post Fiat path is a direct certified-transfer path:

```text
wallet signs native transfer
  -> local admission
  -> one-transfer batch
  -> signed proposal
  -> validator vote collection
  -> quorum certificate / full-vote certificate
  -> local application
  -> finality receipt
```

Here, a certificate means the node-verified vote set for a proposed batch that satisfies the validator-set and quorum rules. Before returning, the node checks the parent, proposal, batch, validator set, quorum, vote set, certificate id, and state evidence.

For \(n = 6\) validators, the certificate quorum is:

\[
q = \left\lfloor \frac{2n}{3} \right\rfloor + 1 = 5
\]

The quorum-fast lane returned when a valid quorum certificate was available. The full-vote lane still observed `6 of 6` votes before returning.

### What the certified receipt does and does not establish

| In this packet, a Post Fiat finality receipt means | It does not mean |
|---|---|
| the signed native transfer is included in a certified batch | Post Fiat has the same ledger object or phase structure as XRPL |
| the batch has a vote set satisfying the validator-set and quorum rules | the measured receipt is byte-identical to XRPL validated-ledger inclusion |
| the node verified the certificate before returning | every public-network observer has independently revalidated the result |
| the batch was locally applied before the receipt was returned | this packet proves WAN durability, public-mainnet reorg behavior, or decentralization properties |
| the path passed the local adversarial gate described below | the `10.03x` or `34.07x` ratios are same-phase consensus-speed ratios |

That distinction is the point of the benchmark. Post Fiat did not make the same ledger clock run faster. It moved the wallet’s synchronous completion point to a certified applied-batch receipt and kept non-finality work out of that path.

| Design move | Latency effect |
|---|---|
| finality receipt from a certificate | the wallet waits for a certified applied batch rather than a ledger-close clock |
| one-transfer batch in the measured path | the critical path stays small |
| account-history/query separation | indexing and read optimization do not sit in front of finality |
| synchronous certificate checks | the fast path still validates the batch it returns |
| full-vote reported as headline | the conservative local lane is fast enough to matter |

The Post Fiat transaction improvement process in this packet is:

```text
Keep the safety-critical certificate checks in the synchronous path;
move non-finality work out of it;
return when the transfer is certified and applied.
```

That is a structural optimization, not a timer tweak.

## Safety gate

A fast number is not useful if the node can finalize conflicting histories or accept stale certificates.

The selected packet included a local adversarial finality gate. It passed `9/9` cases with `residual_work == []`.

| Case family | Result |
|---|---|
| duplicate/conflicting proposal-vote refusal | passed |
| stale vote/certificate rejection | passed |
| parent/state-root tamper rejection | passed |
| under-quorum partition rejection | passed |
| restart persistence | passed |
| one-validator outage | passed |
| delayed vote retry | passed |
| Byzantine disjoint proposer | passed |
| malformed transport/certified-batch rejection | passed |

At this article’s level of detail, the Byzantine disjoint proposer case is a conflicting-proposer attempt; the expected result is refusal to finalize conflicting histories. The safety gate does not create the latency result. It supports the narrower claim that the measured fast path still passed a local adversarial finality check in this harness.

## Evidence and reproduction

### Public packets

| Evidence item | Role |
|---|---|
| [Selected matched latency packet](/benchmarks/postfiat-l1v2-selected-xrpl-matched-latency-postfiat-selected-xrpl-v4-20260609T052252Z/) | claim-critical rerun of Post Fiat against stock private `rippled`, selected `close_750ms`, and aggressive `close_250ms` |
| [XRPL timing stability matrix](/benchmarks/xrpl-private-timing-stability-matrix-xrpl-timing-stability-20260608T152301Z/) | maps stock and reduced-timing private `rippled` profiles and selects `close_750ms` as the fastest non-unstable profile |
| [Safety gate report](/benchmarks/postfiat-l1v2-selected-xrpl-matched-latency-postfiat-selected-xrpl-v4-20260609T052252Z/safety/testnet-finality-chaos-gate.json) | records the local adversarial finality gate |
| [Avalanche/Sui peer calibration packet](/benchmarks/peer-l1-latency-avax-sui-20260607T135723Z/) | context only, not the headline comparison |

The selected matched packet includes `README.md`, `aggregate.json`, `aggregate.md`, `methodology.md`, `endpoint-equivalence.md`, `manifest.json`, `commands.sh`, `lab-book.md`, `session-summary.csv`, `latency-bars.svg`, `latency-cdf.svg`, raw JSON reports, safety artifacts, and `SHA256SUMS.txt`.

### Hashes for the claim-critical artifacts

| File | SHA256 |
|---|---|
| Selected matched packet `SHA256SUMS.txt` | `8463e3ceefc15ee2eea03ae02a194783d54dd383f2eb89cb8e70ec7579458a7e` |
| Selected matched packet `aggregate.json` | `2a50c731ae8c240d2b6413667f055a627a963aa97c9615beb6c9100431131b65` |
| Selected matched packet `manifest.json` | `75344173cf9b0968f045e09d554444540be146c70dbf38ef6c55d3037e7e953c` |
| Selected matched packet `methodology.md` | `dbc598b1b8f12b66224b6e8b5a774c19a79eacfec235b7be0b8d0ca9e96b4b55` |
| Selected matched packet `endpoint-equivalence.md` | `955decc84aaf2e31ec3ad468344cfeb083442c71cc11c58941eb2421c5d0aa31` |
| Selected matched packet `commands.sh` | `ae6d16d77b18f54910068a585537c285d615604cc8799105f9ec503d2fe03b10` |
| Selected matched packet `lab-book.md` | `8647eb9e49f2ba184f3c5de12a230409b25054016b8797bbece4789bf07f462b` |
| Selected matched packet `latency-bars.svg` | `8b013804238a35a7e634a0572824c4f1f9f109ef96c9342fbef9817832df68d4` |
| Selected matched packet `latency-cdf.svg` | `1b4887f1d3c04376546e4777daf1febe90119c36e124c368c07fc57a7b8e9441` |
| Safety gate report | `48a1f1af561c07d730e7ef55487cfa5decef09588df658e4cd246f4dd6201527` |
| Timing matrix `SHA256SUMS.txt` | `15576ce7ccfee1fd11008fac91ab2a8fb1a42d36b3ddc78ac52f7bcf1c3f8969` |
| Timing matrix `aggregate.json` | `04e17ac8b436c0c32a6727c99e7606702af47d5f10c6f992c9b140901b557ef4` |
| Timing matrix `manifest.json` | `91a46f98843fd2dd56103e93a3f42381e154bd56dcd22ae3eca91582606ec8fb` |
| Timing matrix `commands.sh` | `f0f042ecefd1dd60407ffc63ad6f65c2ef71dfc354fa1489db59cb41b9eb0cb4` |
| Peer context packet `SHA256SUMS.txt` | `6c2e0bda5ee3110bb5168f6369cb7930b4c0f5ec072711609f43106d44c888a0` |

### Recorded top-level commands

The selected matched packet records this fresh run command:

```bash
RUN_ID=postfiat-selected-xrpl-v4-20260609T052252Z SESSIONS=5 ROUNDS=1000 VALIDATORS=6 TUNED_BIN=/home/postfiat/repos/rippled/.build/rippled-timing-46b241ace8b3-close_750ms TUNED_PROFILE=close_750ms TUNED_CLASSIFICATION=strained TUNED_SOURCE_MATRIX=/home/postfiat/repos/postfiatorg.github.io/static/benchmarks/xrpl-private-timing-stability-matrix-xrpl-timing-stability-20260608T152301Z AGGRESSIVE_BIN=/home/postfiat/repos/rippled/.build/rippled-timing-46b241ace8b3-close_250ms AGGRESSIVE_PROFILE=close_250ms RUN_SAFETY_GATE=1 BUILD_RELEASE=1 FORCE=1 scripts/postfiat-xrpl-latency-evidence-v4
```

It also records the final repackaging command after raw reports existed:

```bash
RUN_ID=postfiat-selected-xrpl-v4-20260609T052252Z SESSIONS=5 ROUNDS=1000 VALIDATORS=6 TUNED_BIN=/home/postfiat/repos/rippled/.build/rippled-timing-46b241ace8b3-close_750ms TUNED_PROFILE=close_750ms TUNED_CLASSIFICATION=strained TUNED_SOURCE_MATRIX=/home/postfiat/repos/postfiatorg.github.io/static/benchmarks/xrpl-private-timing-stability-matrix-xrpl-timing-stability-20260608T152301Z AGGRESSIVE_BIN=/home/postfiat/repos/rippled/.build/rippled-timing-46b241ace8b3-close_250ms AGGRESSIVE_PROFILE=close_250ms RUN_SAFETY_GATE=1 BUILD_RELEASE=0 RESUME=1 scripts/postfiat-xrpl-latency-evidence-v4
```

The timing matrix records this command:

```bash
RUN_ID=xrpl-timing-stability-20260608T152301Z SESSIONS=5 ROUNDS=1000 VALIDATORS=6 PROFILES=stock,close_1500ms,close_1000ms,close_750ms,close_500ms,close_250ms BUILD_PROFILES=1 FORCE=1 scripts/xrpl-timing-stability-matrix
```

The full expanded command log is in each packet’s `manifest.json` and `commands.sh`. Raw report paths and original start/finish UTCs are in `manifest.json` and `lab-book.md`.

### What this evidence settles

It settles the local claim:

```text
In a local one-host, six-validator native-transfer benchmark, Post Fiat L1 v2
full-vote certified finality completed signed transfers at 88.083 ms p50 and
104.705 ms p95. Stock private rippled validated transfers at 3000.565 ms p50.
The matrix-selected reduced-timing private rippled profile, close_750ms, was
classified strained and validated transfers at 883.507 ms p50. The aggressive
close_250ms stress lane reached 573.367 ms p50 but had 15345.814 ms p95 and
19918.846 ms p99.
```

It does not settle public-mainnet latency, WAN behavior, validator diversity, concurrent throughput, optimized XRPL engineering, independent reproducibility, or superiority over every BFT or object-execution design.

## Next evidence

The next claims require new packets, not stronger adjectives.

| Claim | Evidence needed |
|---|---|
| application-facing throughput | concurrent load matrix with finalized tx/s, failure rate, p50/p95/p99, RPC admission latency, queue depth, CPU, memory, and state size |
| real network shape | same-region and WAN-shaped multi-host validator runs |
| public-testnet behavior | public RPC clients, external network paths, longer duration, independent operators |
| degraded-network behavior | validator restart, one-validator outage, delayed votes, packet delay, and load during finality |
| broader run variance and reproducibility | host CPU/RAM/OS/kernel summary, bare-metal/VM/container placement, per-session variance, longer repeated runs, and independent reruns |
| lower p50 architecture | owned-value or certificate-first transfer lane with the same adversarial gate |

The engineering goal for the next packets is to preserve the certified receipt path as the environment becomes more real.

## Conclusion

XRPL-style finality gives applications a conservative and well-understood boundary: the validated ledger. That boundary is valuable. It is also a structural latency surface. A transaction waits for the ledger cycle: open-ledger residual time, establish-phase proposal convergence, ledger construction, validations, client observation, and sometimes queueing.

The private `rippled` timing matrix tested the natural shortcut: compress the ledger clock. Median latency improved. Then the aggressive profiles exposed the tail.

Post Fiat took a different route. The wallet waits for a certified applied batch rather than a compressed ledger close. In this local six-validator benchmark, the conservative full-vote path returned signed-transfer finality at `88.083 ms` p50 and `104.705 ms` p95 while the local adversarial finality gate passed.

That is the result worth building around: not “we turned the same clock faster,” but “we made the transaction completion path smaller.”

## Appendix A: XRPL application latency under expiration and load

There is no single honest “maximum XRPL transaction latency” number without assumptions.

For applications, the practical maximum is controlled by reliable submission discipline. If a transaction includes `LastLedgerSequence`, the client can keep querying validated ledgers until one of two events happens: the transaction appears in a validated ledger, or the network validates ledgers beyond the transaction’s last allowed ledger.

In simplified form:

\[
T_{\text{authoritative decision}}
\lesssim
(L_{\text{last}} - L_{\text{submit}} + 1)
\cdot
T_{\text{ledger}}
+
T_{\text{lookup}}
\]

where \(L_{\text{last}}\) is the transaction’s `LastLedgerSequence`, \(L_{\text{submit}}\) is the last validated ledger index observed at submission, and \(T_{\text{ledger}}\) is the observed validated-ledger cadence.

Without expiration, the bound is weaker. XRPL’s reliable-submission documentation notes that if transaction cost rises above what the transaction specifies, a well-formed transaction may not be included in the next validated ledger; if costs later fall and the transaction has no expiration, there is no limit to how much later it can be included.[^xrpl-reliable]

| Layer | Optimization handle | Constraint |
|---|---|---|
| Submission | use trusted healthy servers; avoid overloaded RPC paths | submit results can be provisional |
| Expiration | set `LastLedgerSequence` | too short can cause avoidable expiration; too long weakens the decision bound |
| Fees | pay enough under current open-ledger cost | underpaying can queue or postpone inclusion |
| Sequencing | manage account sequence dependencies | queued transactions from the same sender can block later transactions |
| Confirmation | query validated ledgers | in-progress ledger results are not authoritative |

The claim-critical benchmark is sequential. Under load, XRPL latency has another term:

\[
T_{\text{submit}\rightarrow\text{validated}}
=
T_{\text{cycle}}
+
K_{\text{queue}}\cdot T_{\text{ledger}}
\]

Here \(K_{\text{queue}}\) is the number of ledger cycles a transaction waits before inclusion.

That term is operationally real. `rippled` has a transaction queue. The XRPL documentation explains that the open ledger cost sets a target number of transactions in a ledger; if the open ledger surpasses that target, required transaction cost escalates quickly, and transactions that cannot pay the escalated cost may be queued for later ledgers. The queue is then used to build subsequent ledgers.[^xrpl-queue]

A serious load benchmark must therefore report finalized transactions per second, failures, expired transactions, admission latency, queue depth, fee policy, CPU, memory, and state size. Otherwise the benchmark can hide the difference between a fast finality path and a growing queue.

## Appendix B: Peer context

The XRPL control is the lineage-specific comparison. It is not the whole L1 landscape.

A separate local peer calibration packet included Avalanche and Sui lanes. It showed Post Fiat local account/certified-finality lanes around the same sub-100ms p50 class as the claim-critical packet, Avalanche C-Chain local transfer receipt near two seconds p50, and Sui local effects lanes around four milliseconds p50 in the tested local setup.

| Lane | Sessions | Transactions | p50 ms | p95 ms | p99 ms |
|---|---:|---:|---:|---:|---:|
| `postfiat_full_local` | 1 | 1000 | 89.062 | 105.777 | 117.092 |
| `postfiat_quorum_fast_local` | 1 | 1000 | 84.278 | 100.485 | 105.198 |
| `avax_local_c_chain_transfer` | 3 | 3000 | 1957.219 | 1978.009 | 1988.044 |
| `sui_local_owned_transfer` | 3 | 3000 | 3.968 | 230.196 | 311.582 |
| `sui_local_shared_object_tx` | 3 | 3000 | 3.928 | 227.653 | 349.605 |

This context prevents the wrong claim. Post Fiat is not claiming the lowest local p50 among modern systems. The peer packet instead points to the next architectural question: whether Post Fiat should add an owned-value or certificate-first transfer lane for cases that do not need the full account-ledger coordination path.

---

## Source notes

[^xrpl-transactions]: XRPL documentation, "Transactions": a transaction is final only if signed, submitted, and accepted into a validated ledger version; transaction metadata is not final unless the transaction appears in a validated ledger. https://xrpl.org/docs/concepts/transactions

[^xrpl-reliable]: XRPL documentation, "Reliable Transaction Submission": applications should avoid mistaking provisional results for final immutable results; well-formed transactions are usually validated or rejected in seconds, but without expiration there is no limit to how much later a transaction can be included if conditions change. https://xrpl.org/docs/concepts/transactions/reliable-transaction-submission

[^rippled-consensus-open]: `rippled` consensus documentation: the `Open` phase is a period for transactions to build up; its duration is a latency-throughput tradeoff; under normal circumstances an open ledger with transactions closes after `LEDGER_MIN_CLOSE`. https://github.com/XRPLF/rippled/blob/develop/docs/consensus.md

[^rippled-consensus-establish]: `rippled` consensus documentation: consensus proceeds through `Open`, `Establish`, and `Accept`; consensus is declared after `LEDGER_MIN_CONSENSUS`, proposer participation or timeout conditions, and supermajority agreement on the same position. https://github.com/XRPLF/rippled/blob/develop/docs/consensus.md

[^consensus-parms]: `rippled` source, `ConsensusParms.h`: `minConsensusPct = 80`, `ledgerMinConsensus = 1950ms`, `ledgerMinClose = 2s`, `ledgerGRANULARITY = 1s`, `ledgerMaxConsensus = 15s`, `ledgerAbandonConsensus = 120s`, with a source comment that consensus parameters are not meant to be changed arbitrarily. https://raw.githubusercontent.com/XRPLF/rippled/develop/src/xrpld/consensus/ConsensusParms.h

[^xrpl-queue]: XRPL documentation, "Transaction Queue": `rippled` uses a transaction queue to enforce open-ledger cost; open-ledger cost escalates when a ledger exceeds its target size; queued transactions are used to build later ledgers. https://xrpl.org/docs/concepts/transactions/transaction-queue

[^dls]: Cynthia Dwork, Nancy Lynch, and Larry Stockmeyer, "Consensus in the Presence of Partial Synchrony," Journal of the ACM, 1988. The paper introduces the partial synchrony model between synchronous systems with known delay bounds and asynchronous systems with no fixed bounds. https://research.ibm.com/publications/consensus-in-the-presence-of-partial-synchrony

[^tail-at-scale]: Jeffrey Dean and Luiz André Barroso, "The Tail at Scale," Communications of the ACM, 2013. The paper explains why temporary high-latency episodes can dominate perceived performance as systems scale. https://research.google/pubs/the-tail-at-scale/

[^xrpl-analysis]: Brad Chase and Ethan MacBrough, "Analysis of the XRP Ledger Consensus Protocol," arXiv:1802.07242, 2018. The paper describes XRPL consensus as a low-latency Byzantine agreement protocol and derives safety and liveness conditions. https://arxiv.org/abs/1802.07242

[^ripple-security]: Ignacio Amores-Sesar, Christian Cachin, and Jovana Mićić, "Security Analysis of Ripple Consensus," OPODIS 2020 / arXiv:2011.14816. The paper provides an abstract description of Ripple consensus derived from source code and analyzes safety/liveness behavior under network assumptions. https://arxiv.org/abs/2011.14816

[^mauri-formal]: Lara Mauri, Stelvio Cimato, and Ernesto Damiani, "A Formal Approach for the Analysis of the XRP Ledger Consensus Protocol," ICISSP 2020. The paper formalizes XRPL consensus and relates safety/liveness tolerances, validation quorum, and UNL overlap. https://www.scitepress.org/PublishedPapers/2020/89542/
