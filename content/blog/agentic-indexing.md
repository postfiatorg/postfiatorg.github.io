---
title: "Agentic Indexing: Financial Indices That Replay Byte for Byte"
date: 2026-08-27T00:00:00Z
summary: "A working demonstration of AI-generated thematic indices: Qwen writes continuous rubrics and scores relevance, deterministic fundamentals set scale, and independent H200s reproduce 4,000 tested responses byte for byte."
url: "/blog/agentic-indexing/"
aliases:
  - /agentic-indexing/
  - /posts/agentic-indexing/
show_toc: false
categories:
  - Post Fiat Research
tags:
  - Post Fiat
  - PFTL
  - Flare
  - Financial Indices
  - Deterministic Inference
  - Qwen
  - SGLang
  - Tokenized Stocks
---

Financial indices no longer need to begin with a committee in a conference room. An open model can write a thematic mandate, score a public universe against it, and produce a portfolio whose lineage an independent operator can replay on the same committed compute profile.

We built that system. These four factor runs are live views over frozen output files: every score, accepted constituent, weight, dependency hash, rejection and cross-machine replay receipt. Three became portfolios. Critical Minerals did not: only three companies cleared the relevance floor, while the committed 20% cap requires at least five. The pipeline rejected it instead of changing the rules after seeing the result.

{{< agentic-index-gallery >}}

Call it **trustless financial indexing**, with one precise target: after the methodology and inputs are committed, an operator should not be able to replace the model's portfolio with its own. The current artifacts make substitution detectable; the proposed PFTL/Flare gate would make it rejectable. Qwen proposes the factor and applies bound company inputs, accounting rules set scale, and independent machines replay the result.

**Live in this demonstration:** the 15-mandate catalog, four fresh 1,000-company continuous-score runs, transcript bindings, accounting classifications, three final-weight files, one deterministic rejection and cross-H200 replay files. **Proposed next:** Post Fiat Ledger (PFTL) finalization, optional Flare attestation and ATP execution. The article keeps those two states separate.

The method has four steps. Qwen expands each fixed theme into a continuous eleven-anchor rubric. The same frozen model scores each company from 0 through 100. Companies scoring at least 70 enter the weighting gate. A second matching H200 must reproduce every response byte before deterministic code combines 20% score strength with 80% square-root-market-cap and profitability scale under a 20% holding cap.

## From One Custom Basket to an Index Factory

Our [first article on verifiable thematic baskets](/blog/verifiable-thematic-baskets/) proposed a custom-index product. A customer chose a question—“data-center cooling,” for example—and deterministic inference chose the securities. The next step was to let the model originate the menu too.

We gave a frozen Qwen model a global-macro mandate: describe the economic and speculative environment represented in its training data, then produce 15 differentiated thematic baskets investors could plausibly want. The model first returned qualitative anchors at 0, 25, 50, 75 and 100. For this new run, a second frozen request expanded each of the four tested themes into exact anchors at every ten points while preserving the original theme identity and high-score meanings.

The result was not 15 versions of “AI.” It covered generative compute, grid modernization, critical minerals, defense and space, biotechnology and longevity, digital finance, supply-chain resilience, elder care, climate adaptation, robotics, water security, private credit, cybersecurity, advanced manufacturing, and the experience economy. The complete model-generated catalog is included in the [public evidence packet](/benchmarks/agentic-index-live-samples-20260827.json).

We used each continuous rubric exactly as generated. Every scoring request binds the SEC identity record and clearly labels the earnings-call transcript as **supplemental information**. Qwen assesses the company's substantive business exposure from the identity, products, technologies and industry role encoded in its frozen weights; the transcript adds contemporaneous detail when available. The same classifier scores companies with and without transcripts. Every result is strict JSON containing an integer score, confidence, verdict, counter-case, prior-versus-transcript assessment and exactly four substantive reasoning paragraphs.

Using one model to author and apply the rubric is deliberate: the objective is internally consistent factor expression, not independent validation. Introducing an uncommitted second model would add another semantic authority capable of silently redefining the factor. This is not a keyword or transcript-sentiment index. Repeating thematic language cannot turn a grocery chain into an AI-compute company or a diversified user of AI into a major AI supplier. The transcript grounds current operations; it does not replace the model's durable knowledge of the company's products, customers, assets, research and recognized industry role. A score of 80 requires major current economic exposure, not management emphasis.

The score answers one question only:

> How strongly does this company express this particular thematic factor?

A score of 70 or more now qualifies. In every continuous rubric, 70 means substantial, durable exposure, 80 means major current economic exposure and a prominent durable business role, 90 means category leadership or near-pure exposure, and 100 means a true category-defining pure play. The model may interpolate to any integer, so 72 and 93 carry more information than a five-bucket label. Scores below 70 remain secondary, incidental or merely adjacent exposure.

The frozen rubric receipts still contain the original phrase “below the index-membership bar” at 70 because the first published epoch used an 80 floor. We did not rewrite those model outputs after reviewing the baskets. Instead, the new `cutoff70.v4` methodology admits the already-defined substantial-exposure tier and receives a different methodology hash. The earlier 80-floor artifacts remain immutable. No analyst can promote a 69 because the name “feels right,” and no sponsor can delete an awkward 70 after seeing the final weights.

{{< agentic-index-diagram kind="pipeline" >}}

Revenue, free cash flow and net income do not decide whether a company is AI, defense or elder care. Qwen makes that classification; fundamentals size only the companies that passed it.

## The Quantitative Spine

The eligible universe is the 1,000 largest U.S. reporting companies by trailing four-quarter revenue. That SEC-derived ranking defines who is scored; revenue does not determine the live thematic weights. For an accepted company, the current demonstration uses a dated USD market-capitalization packet from Sharadar, transformed by square root so a mega-cap matters without swallowing the portfolio.

For an ordinary operating company, trailing free cash flow is:

```text
TTM free cash flow
  = sum(last four discrete quarters of operating cash flow)
  - sum(abs(last four discrete quarters of capital expenditure))
```

For a bank or insurer, cash is inventory and funding; operating cash flow is not an industrial surplus measure. For a regulated utility, capital expenditure may be recovered through the rate base, so subtracting it as ordinary discretionary plant spending can invert the economics. Those issuers use trailing net income.

The SEC-fact classifier applies these categories in order:

- **Regulated utility:** current filing facts show regulated operations, rate-base accounting or utility plant. Use net income.
- **Balance-sheet financial:** deposits, loans, regulatory capital, insurance liabilities or material trading assets define the operating model. Use net income.
- **Settlement float:** customer settlement assets are substantially matched by settlement liabilities. Keep these payment networks on FCF.
- **Ordinary operating company:** use FCF when none of the earlier regimes applies.
- **Ambiguous:** use neither. Missing or irreconcilable facts are excluded rather than imputed.

The frozen universe contained 884 ordinary operating companies, three settlement-float businesses, 79 balance-sheet financials, 33 regulated utilities and one ambiguous issuer. The classifier therefore routed 887 issuers to FCF and 112 to net income. Exact routed profitability was available for 981; the other 18 were excluded without imputation.

{{< agentic-index-diagram kind="fundamentals" >}}

The selected profitability number is standardized across those 981 issuers with a population z-score. For each company scoring at least 70:

```text
factor strength(i) = (Qwen score(i) - 70) / 30
factor share(i) = factor strength(i) / sum(factor strength)

fundamental scale(i)
  = sqrt(market capitalization(i))
  × exp[0.03 × z(selected profitability(i))]

fundamental share(i)
  = fundamental scale(i) / sum(fundamental scale)

pre-cap weight(i)
  = 20% × factor share(i)
  + 80% × fundamental share(i)
```

Weights above 20% are clipped and redistributed proportionally among uncapped holdings until the portfolio again sums to 100%. The result is normalized to one trillion integer units using a largest-remainder rule with CIK as the tie-break. Negative profitability remains in the population. There is no revenue percentile, ordinal score rank, confidence multiplier, winsorization or imputation.

The coefficient `0.03` was chosen to make profitability matter without allowing one accounting outlier to dominate the scale term. At one standard deviation above the profitability mean, the multiplier is only 1.0305; at one standard deviation below, it is 0.9704. The separate historical research used revenue as the primary scale variable and showed why `0.03` was preferable to the more concentrated `0.05` alternative. That experiment validated the routing discipline and the modest profitability tilt; it did not backtest this new square-root-market-cap and 20/80 thematic blend.

The thematic score contributes a fixed 20% of aggregate portfolio weight through factor share. A score of 100 has factor strength 1.0; 90 has 0.6667; 80 has 0.3333; and an exact 70 enters through the fundamental sleeve with zero factor strength. None of the four demonstrated score vectors contains an exact 70. The remaining 80% reflects transformed company size and the small profitability overlay. Equal scores receive equal factor strength; ordinal ranking never enters the formula.

One constituent shows the calculation. Qwen scored NVIDIA **95** because it is the category leader in generative-AI compute, while retaining a small deduction for gaming, automotive and other edge businesses. Its $5.074 trillion dated market capitalization became a $2.253 million square-root term. Selected trailing FCF of $119.076 billion produced a `+14.7791z` profitability score and a `1.55795531×` multiplier, creating $3.509 million of fundamental scale. NVIDIA represented 5.330490% of factor share and 12.204812% of fundamental share; the locked 20/80 blend produced a final **10.829947%** weight in the 40-company AI index.

The same rules can reject an otherwise coherent theme. Critical Minerals produced SCCO at 100 and ALB and FCX at 92—but no fourth or fifth company reached 70. A 20% cap cannot fully invest a three-name portfolio. The canonical cutoff-70 outcome is therefore a rejection with hash `57dbaef7dc5c92252d91914884da90b0b07bde8c09bf6b2d7a9c9cbb84241f9d`, not a post-hoc exception or higher cap.

## Does the Underlying Fundamental Discipline Survive Contact With History?

Before adding themes, we asked whether revenue selection plus the same FCF/net-income routing and 0.03 profitability tilt produced a reasonable large-cap index. The frozen test selected 500 U.S. issuers, retained incumbents through rank 750, and rebalanced quarterly. From March 17, 1998 through August 24, 2026, the candidate recorded 10.92% CAGR, 18.91% annualized volatility and a -55.05% maximum drawdown. SPY recorded 8.98%, 19.37% and -55.20%. Daily return correlation was 0.949.

{{< agentic-index-diagram kind="backtest" >}}

The backtest used Sharadar's licensed point-in-time normalized statements and SEP adjusted prices; SPY used Tiingo adjusted closes. It does **not** assume that modern EDGAR XBRL APIs existed in 1998. Licensed institutional history tests the economics. The live calculation uses the SEC as the authoritative filing source and publishes accession, acceptance time, period, amendment state, facts and hashes. Reconstructing an open pre-XBRL history would require deterministic extraction from legacy filings, but that is not a coverage defect in this backtest.

The result establishes reasonableness, not alpha. Candidate-minus-SPY annualized arithmetic return was 1.68%, with a Newey-West t-statistic of 1.59 and a 95% interval of -0.40% to 3.76%. Five-factor annualized alpha fell to 0.64% with a t-statistic of 0.91. The study was developed in sample; it is a methodology test, not a forecast. The [frozen report at commit `d4d6b4f`](https://github.com/postfiatorg/navstrategies/blob/d4d6b4f13d4725e637e2b17fe8e859815f7d5486/research/pre_catalyst/data_exploration/sec_10q_size_proxy/open_sec_fundamental_index_research_report.md) publishes the complete data lineage, coefficient sweep, cost tests, delisting stress and factor attribution.

This backtest validates the **accounting routing and modest profitability overlay**, not the exact live square-root-market-cap blend and not historical AI themes. A 2026 Qwen rubric cannot honestly be projected backward as though the model existed in 1998. The four live factor runs demonstrate internally consistent scoring and replay; three demonstrate portfolio construction, while the fourth demonstrates deterministic rejection. Score stability and thematic performance require prospective observation.

## What “Byte-Reproducible” Actually Means

Temperature zero is not a reproducibility protocol. GPU reductions can occur in different orders, and dynamic batching can change floating-point results. The [SGLang deterministic-inference design](https://github.com/sgl-project/sglang/blob/main/docs_new/docs/advanced_features/deterministic_inference.mdx) addresses this with batch-invariant kernels and a deterministic serving path.

The strict profile pinned:

- `Qwen/Qwen3.8-27B-FP8` at revision `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a`;
- the tokenizer and content-addressed SGLang runtime image;
- H200 hardware, tensor parallelism one and 32-request batches;
- deterministic inference with radix cache, overlap scheduling and CUDA graphs disabled; and
- seed `438916795` plus canonical prompt, schema, parser, universe, transcripts and rubric.

We ran 1,000 companies across four of the 15 factors and replayed every request on the other H200. All 4,000 raw responses, parsed objects and attempt traces matched. The opening gallery links the comparison files containing request and response hashes for every CIK, while the replay diagram exposes one raw original/replay pair inline. Byte replay held for the rejected Critical Minerals factor too; reproducible inference does not guarantee that the committed portfolio constraints admit a portfolio.

{{< agentic-index-diagram kind="replay" >}}

A parsed-score match could hide changed reasoning, so the test compares raw UTF-8 bytes before parsing and weighting. Both hosts used the same H200 profile; cross-hardware portability remains untested. The result proves execution reproducibility for committed inputs, not economic correctness.

## Rebalancing When the World Model Changes

A new admitted open-weight model can be an index information event, but not permission to rerun at will. The series locks its update policy first. A model qualifies only after its license, shard and tokenizer hashes, runtime compatibility and conformance tests are published. SEC inputs freeze, the index regenerates once, replay must match, and turnover controls determine effectiveness.

{{< agentic-index-diagram kind="rebalance" >}}

The Thomson Reuters report [*Thomson: Continual Learning of Frontier Models for SovereignAI*](https://www.thomsonreuters.com/content/dam/ewp-m/documents/thomsonreuters/en/pdf/reports/thomson-technical-report.pdf) shows why this is practical. Starting from open Qwen checkpoints, Thomson built stable artifact identifiers and a queryable provenance graph; its final large-model run took three weeks and was estimated below $450,000 in GPU expense. That supports institution-controlled model releases, not higher turnover or better returns. Each admitted release creates a new lineage instead of overwriting the old one.

## Who Proves the Model?

Byte replay does not prove where the model came from. An admitted manifest must bind the repository revision, license, tokenizer, configuration and every weight-shard digest. Independent operators mirror those shards and publish matching receipts. The epoch also binds the runtime image, SGLang revision, hardware profile, schema and parser; an attested process can sign the digest of the artifacts actually loaded.

The [Flare Compute Extension scaffold](https://github.com/flare-foundation/fce-extension-scaffold) registers allowed TEE code versions and signed results. An index extension could accept one manifest and methodology, hash the loaded shards, verify replay receipts and sign `AcceptedIndexEpoch`; a contract rejects any mismatch. Confidential Compute runs end to end on Coston2, although simulated attestation is not hardware isolation. [Web2Json](https://dev.flare.network/fdc/guides/foundry/web2-json) can attest small manifest facts, not model weights or semantic truth.

Open weights also do not reveal a base model's entire training corpus. The defensible claim is exact model-byte identity and execution lineage, not omniscience about every document that shaped the checkpoint.

## ATPs Are the Missing Last Mile

Bitwise's Automated Token Portfolios show how an index file can reach assets without becoming a pooled fund. Eligible non-U.S. investors can select Mag7X, Robotics or AI Leaders portfolios: [Bitwise publishes the model, Glider rebalances, and Coinbase supplies the tokenized shares](https://www.morningstar.com/news/pr-newswire/20260825sf32693/bitwise-launches-automated-token-portfolios-atps-powered-by-coinbase-and-glider). Bitwise's stated methodology fee is 0.15%, plus trading and Glider fees.

{{< agentic-index-diagram kind="atp" >}}

An ATP separates model authorship from execution. [Glider](https://docs.glider.fi/guides/portfolio-creation) implements target weights through a smart-contract vault and user-approved session key. A Post Fiat index can publish an epoch; the vault verifies its hash and trades within the user's authorization.

Wallet control of the token is not personal custody of the registered share. [Coinbase describes B20](https://www.coinbase.com/tokenize) as tokens backed one-for-one by shares in regulated, bankruptcy-remote custody, giving holders a beneficial claim. Issuer, custodian, legal wrapper, redemption and jurisdiction remain separate dependencies. Index-provider and investment-advice treatment likewise depends on product design and jurisdiction; replayability does not answer that legal question.

The point is programmable distribution: one weight object can reach many execution venues without the index author holding customer assets.

## The PFTL Implementation

PFTL should finalize index lineage, not supply accounting truth or custody assets:

- A **series registry** stores the mandate, universe, threshold, weighting, rebalance and model-admission policies.
- An **epoch manifest** binds every SEC accession, transcript, prompt, model, score, accounting fact, exclusion and final weight.
- Independent operators submit **replay receipts** with matching raw-response and final-weight roots.
- PFTL finalizes one `pft.index.snapshot.v1` object, pins it to IPFS and publishes its pointer. Execution systems handle custody, trading and redemption separately.

{{< agentic-index-diagram kind="pftl" >}}

Optional Flare integration binds an allowed trusted-execution-environment image to the model manifest and signed epoch. An onchain gate can then reject substituted weights; the Flare Data Connector contributes narrow source attestations where Web2Json fits.

The clean division is:

> **Qwen's frozen company knowledge supplies the qualitative baseline; supplemental transcripts ground it in current operations. Deterministic accounting supplies economic scale. PFTL records agreement and lineage. Flare can attest the authorized compute path. An execution venue or token issuer moves assets.**

## What the Demonstration Establishes

The result is not that Qwen can name AI stocks. It is that a model can originate a catalog, apply continuous rubrics to 1,000 companies, combine qualifying scores with committed fundamentals, reproduce every response on a second machine and reject a factor when the frozen portfolio constraints cannot be satisfied. Humans choose the universe, evidence, model, threshold, weighting, cap and turnover rules; every later change leaves a different hash.

> A financial index that can explain where it came from, reproduce itself on another machine, and arrive directly in an investor-controlled account.

That is agentic indexing: a financial index that behaves like a versioned software artifact rather than an editable spreadsheet.

## Appendix: The Jargon in Plain English

### Index Construction and Accounting

- **Agentic index:** An index whose mandate, company classifications and weights are generated by a specified model-and-code process instead of being edited security by security by a portfolio manager.
- **Thematic mandate:** A written definition of the economic exposure an index is meant to capture, such as grid modernization or critical minerals.
- **Scoring rubric:** The fixed descriptions at 0, 10, 20 and so on through 100. Qwen may interpolate to any integer. In the current `cutoff70.v4` epoch, scores of 70 or more qualify for the weighting gate.
- **Factor expression:** How strongly a portfolio represents its stated theme. Excluding partially relevant companies keeps that exposure from being diluted.
- **Eligible universe:** The complete list of companies that may be scored. Here it is the 1,000 largest eligible U.S. reporting companies by trailing revenue.
- **CIK:** The stable identifier the SEC assigns to a filing entity. It avoids depending on tickers, which can change or be reused.
- **SEC accession:** The unique identifier for one submitted SEC filing. Binding an accession identifies the exact filing used by the calculation.
- **XBRL fact:** A tagged accounting value in an SEC filing, accompanied by metadata such as period, unit and filing form.
- **Trailing four quarters, or TTM:** The sum of the latest four discrete fiscal quarters. This avoids treating one unusually strong or weak quarter as a full-year result.
- **Revenue:** Sales generated by the business. The methodology uses trailing revenue as its primary measure of company scale, not as evidence of thematic relevance.
- **Operating cash flow, or OCF:** Cash generated by normal operations before capital expenditure and financing activity.
- **Capital expenditure, or capex:** Cash spent on long-lived assets such as factories, equipment or infrastructure.
- **Free cash flow, or FCF:** In this methodology, trailing OCF minus the absolute value of trailing capex. It is the profitability measure for ordinary operating companies.
- **Net income:** Accounting profit after expenses and taxes. It replaces FCF for balance-sheet financial companies and regulated utilities, where ordinary industrial FCF can be misleading.
- **Balance-sheet financial:** A bank, insurer or similar company whose deposits, loans, regulatory capital, insurance liabilities or trading assets are part of the operating business rather than incidental financing.
- **Regulated utility:** A utility whose investment and returns are materially governed by a regulator. Large capital programs may enter a recoverable rate base, making ordinary FCF treatment economically misleading.
- **Settlement float:** Customer money temporarily held to complete payments. Substantially matched settlement assets and liabilities do not automatically turn a payment network into a bank for this classifier.
- **Imputation:** Filling a missing value with an estimate. This methodology does not do it; a missing required fact causes exclusion.
- **Population z-score:** The number of population standard deviations an issuer's selected profitability lies above or below the universe mean.
- **Market capitalization:** Share price multiplied by shares outstanding. The live demonstration uses a dated Sharadar USD market-cap packet; it is not extracted from SEC statements.
- **Square-root market cap:** The market-cap transformation used to preserve company-size information while compressing the gap between mega-caps and smaller constituents.
- **Profitability multiplier:** `exp(0.03 × z-score)`, the deliberately small adjustment applied to square-root market cap.
- **Factor strength:** `(Qwen score - 70) / 30` for a qualifying company. An exact 70 receives zero thematic strength but remains eligible for the fundamental sleeve; an 80 receives one-third, a 90 two-thirds and a 100 one unit of strength.
- **Factor share:** One company's factor strength divided by the total strength of all qualifying companies. This supplies 20% of pre-cap portfolio weight.
- **Fundamental scale:** Square-root market cap multiplied by the profitability multiplier.
- **Fundamental share:** One company's fundamental scale divided by the total fundamental scale of all qualifying companies. This supplies 80% of pre-cap weight.
- **Pre-cap weight:** `20% × factor share + 80% × fundamental share`.
- **Holding cap:** The maximum permitted final weight, fixed here at 20%. Excess is redistributed proportionally among uncapped holdings; fewer than five qualifying names makes the cap infeasible and rejects the index.
- **Largest-remainder normalization:** A deterministic way to convert fractional weights into fixed integer units while preserving a total of exactly one trillion units. Remaining units go to the largest fractional remainders, with CIK breaking ties.
- **Winsorization:** Replacing extreme values with less-extreme boundary values. The published methodology does not use it.
- **Rebalance:** A scheduled recalculation of constituents and weights using newly admitted inputs.
- **Retention band:** A turnover-control rule that lets an existing constituent remain eligible through rank 750 even though new entrants normally must rank in the top 500.
- **Index epoch:** One immutable version of an index, including its cutoff time, inputs, scores, rules and final weights.

### Backtest and Portfolio Statistics

- **Point-in-time data:** Historical data stored as it was available on each date, rather than corrected with information published later. It helps prevent look-ahead bias.
- **Adjusted close:** A historical security price adjusted for events such as splits and distributions so returns can be compared through time.
- **CAGR:** Compound annual growth rate, the constant annual rate that would connect a starting value to an ending value.
- **Annualized volatility:** The standard deviation of returns scaled to one year. It describes variability, not merely losses.
- **Maximum drawdown:** The largest peak-to-trough decline during the tested period.
- **Correlation:** A measure from -1 to 1 describing how closely two return series moved together.
- **Return-to-volatility:** Annualized return divided by annualized volatility. It is a simple risk-adjusted comparison, not proof of skill.
- **Newey–West t-statistic:** A significance statistic whose standard error is adjusted for autocorrelation and changing variance in returns.
- **Five-factor alpha:** Return left unexplained after controlling for the Fama–French market, size, value, profitability and investment factors. An insignificant alpha is not evidence of persistent outperformance.
- **In sample:** Evaluated on history that influenced development of the rule. It is useful for rejecting incoherent mechanics but is not an independent forecast test.

### Models, Deterministic Inference and Replay

- **Open-weight model:** A model whose learned numerical weights can be downloaded and independently run, subject to its license.
- **Checkpoint or model revision:** One exact release of a model. A repository name alone is insufficient because its files can change.
- **Qwen3.8-27B-FP8:** The specific open-weight model used here: roughly 27 billion parameters represented with eight-bit floating-point weights for efficient inference.
- **H200:** The NVIDIA data-center GPU profile used on both replay machines.
- **SGLang:** The model-serving runtime used to execute the Qwen requests.
- **Deterministic inference:** An execution mode designed so the same committed request and compute profile produce the same output bytes, even when requests are processed in batches.
- **Tokenizer:** The exact software and vocabulary that convert text into the numerical tokens processed by the model.
- **Temperature:** A sampling control. Temperature zero removes ordinary random sampling, although it is not sufficient by itself for byte reproducibility.
- **Seed:** A fixed initial value used by pseudorandom operations. It must be bound with the rest of the runtime configuration.
- **Tensor parallelism:** Splitting one model across multiple GPUs. This demonstration used tensor parallelism one, meaning one GPU served each model replica.
- **Radix cache:** A serving optimization that reuses common prompt prefixes. It was disabled to keep the replay profile simple and controlled.
- **CUDA graph:** A captured sequence of GPU operations reused for speed. Prefill and decode CUDA graphs were disabled in the strict profile.
- **Canonical request:** One precisely serialized prompt and schema whose bytes are fixed before execution. Semantically equivalent wording is still a different request.
- **UTF-8 bytes:** The actual encoded output compared by the replay test. Matching parsed scores is weaker than matching the complete response bytes.
- **Byte-identical:** Every byte is in the same position on both machines. The 4,000 demonstrated replays met this standard.
- **SHA-256:** A cryptographic hash function that turns any artifact into a short fixed-length digest. Changing even one byte changes the digest with overwhelming probability.
- **Content-addressed image:** A container image identified by its cryptographic digest rather than a mutable label such as `latest`.
- **Manifest:** A machine-readable list of the exact inputs, versions, rules and hashes admitted for one run.
- **Provenance or lineage:** The recorded chain connecting source documents, model files, runtime, outputs and final index weights.
- **Replay receipt:** A signed or published record showing which request was rerun and which output hashes the independent operator obtained.

### PFTL, Flare and Onchain Delivery

- **PFTL:** Post Fiat Ledger, the proposed network for registering index series, collecting replay receipts and finalizing canonical index epochs.
- **IPFS:** A distributed content-addressed file system. A file is retrieved by a hash-derived identifier, so silent modification produces a different address.
- **TEE:** Trusted execution environment, hardware intended to isolate code and data from the machine operator while producing evidence about what ran.
- **Attestation:** A signed statement from trusted hardware or an attestation service about an execution environment and the code it loaded. It does not prove that the model's judgment is economically correct.
- **Flare Compute Extension, or FCE:** Flare infrastructure for admitting trusted code versions and verifying signed compute results.
- **Flare Data Connector, or FDC:** Flare's system for reaching consensus on specified external data claims.
- **Web2Json:** An FDC workflow that extracts and attests defined JSON fields from a web source. It is suitable for narrow facts, not for proving the semantic truth of an entire model output.
- **Coston2:** Flare's public test network, used to test integrations without requiring production FLR.
- **Onchain gate:** A smart contract that accepts an index epoch only when its required hashes and attestations match the registered policy.
- **ATP:** Automated Token Portfolio, a portfolio methodology delivered through programmable tokenized-asset execution rather than a conventional pooled robo-adviser account.
- **Smart-contract vault:** Onchain code that holds or controls assets under predefined rules and can rebalance toward published target weights.
- **Session key:** A limited authorization allowing an automation system to perform specified actions without receiving unrestricted control of the owner's wallet.
- **Tokenized share:** A blockchain token connected through an issuer and custody structure to an underlying security or claim. The token is not automatically the registered share itself.
- **Beneficial claim:** The holder's economic entitlement through a legal and custody structure even when another entity is the registered owner of the underlying share.
