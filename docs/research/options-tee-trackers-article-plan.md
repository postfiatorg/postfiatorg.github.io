# Single-stock options tracker article

The owner requested a published research article with many visual diagrams, then
clarified that it must explain the primitive, its operation, value and trust
properties. Proving performance and implementation history are outside the main
story. This is an explainer of existing work, not a new portfolio specification.

- [x] Explain a rolling single-stock call basket, explicit rules and target outputs.
- [x] Show how measured collection, private computation, SP1 proof and PFTL receipt fit together.
- [x] Explain which operator claims become verifiable and which data, hardware,
  policy, cryptographic and custody assumptions remain.
- [x] Add ten responsive diagrams, including an interactive verification walkthrough.
- [x] Distinguish demonstrated targets/local receipts from future investment products.
- [x] Build with the deployment Hugo version; inspect desktop/mobile and keyboard/no-JS behavior.
- [x] Preserve readable diagram descriptions in Markdown and Copy for LLM output.

Publication target: `/blog/trustless-single-stock-option-indices/`. The website PR
and GitHub Pages deployment provide the publication record; verify the live page,
assets, Markdown output, blog-index entry and research redirect after deployment.

The owner subsequently requested the main blog placement and exact title
“A Framework for Trustless Single Stock Option Indices.” The original research
URL redirects to the blog article. Its body, diagrams and scoped trust claims
remain the published explainer; the main blog index now provides discovery.

Local validation on September 7, 2026 passed with Hugo 0.148.1 and both repository
content checks. Browser checks covered all ten figures at 1280px and 390px, all
five interactive cases, keyboard activation, no-JavaScript fallback, local assets,
and diagram descriptions in both Markdown and clipboard output.

Use the PFTL PR #38 implementation and dated public qualification evidence, the
NAV retained run summary, and primary AWS/SP1/OIC documentation. No raw quotes,
private quantities, credentials or private recovery material are publication inputs.

## September 7: options NAVCoin expansion

The owner requested an update to the live article after discussing an Ethereum
NAVCoin traded on Uniswap and reviewing the earlier NAVCoin proposals. This
authorizes updating and republishing the explainer; it does not authorize fund
deployment, capital movement or new portfolio rules.

- [x] Explain the wallet-held options NAVCoin before the technical proof details.
- [x] Distinguish brokerage custody, Post Fiat verification/accounting and Ethereum
  token ownership/settlement; define NAV from actual portfolio holdings.
- [x] Explain convex calls versus linear margined perpetual exposure.
- [x] Separate Uniswap sales from primary redemption and explain asynchronous
  settlement, market price versus NAV, and both earlier redemption models.
- [x] Link the NAVCoin, UltraShort and Glass proposals, Enzyme and ERC-7540;
  link the two unpublished drafts to their public repository sources.
- [x] Add two responsive diagrams and readable descriptions in both Markdown and
  Copy for LLM output; renumber all twelve figures in article order.
- [x] Preserve the target-only demonstration and the remaining fund, custody,
  reserve, bridge and issuance work as distinct claims.
- [x] Validate Hugo 0.148.1 build and both repository content checks.
- [x] Inspect 1280px/390px rendering, twelve figures without horizontal overflow,
  five interactive scenarios, keyboard controls, no-JavaScript readability,
  blog discovery, and exact Markdown/clipboard output.

The update keeps the existing title and canonical URL. It changes the article,
diagram assets and this publication record; the earlier NAVCoin drafts remain
drafts and no market-data capture is published. The branch PR and Pages run are
the deployment record, followed by a live-page and asset check.

## September 7: product thesis and market sizing

The owner found the expanded article repetitive about limitations and unclear
about product value. The revised editorial objective is explicit: explain a
spot-held primitive for the existing call-premium market, with fully funded
upside exposure and loss limited to invested capital plus fees.

This update publishes derived market aggregates authorized by that request.
The raw Schwab chains, brokerage details and recovery material remain private.
The earlier record above describes the previous publication, which did not
include this market sizing.

- Lead with what the investor buys, why the payoff is useful, and the measured
  market. Explain investor, wallet, exchange and liquidity-provider benefits.
- Distinguish outstanding premium value, underlying notional and reported perp
  OI through positive definitions. Preserve exact source dates and coverage in
  the public aggregate record and an expandable methodology note.
- Treat the two-stock measurement as a measured starting market. Label the 1%
  arithmetic example as illustrative scale; do not invent global premium TAM,
  expected adoption, fee rates or portfolio rules.
- Use one concise implementation/trust section. Remove repeated negatives from
  introductions, diagrams and transitions; support the product thesis with
  explicit mechanics, evidence and use cases throughout.
- Replace three technical-boundary diagrams with a product overview, market
  sizing figure and single-call expiry payoff. Keep twelve diagrams, with
  desktop/mobile chart layouts and text descriptions in Markdown/clipboard.

The rewrite reduces the source article from 3,076 to about 2,040 words. Market
aggregates reconcile to the prior calculation: $8,045,317,861.50 premium value,
$142,283,543,038 call underlying notional and $787,544,513.37 tracked reported
perp OI. The public source record includes formulas, dates, coverage and the
independent Hyperliquid subset. The chart script builds only from this record.

Validation includes Hugo 0.148.1, both repository content checks, exact aggregate
reconciliation, responsive chart selection, desktop/mobile visual inspection,
all five interactive cases, keyboard/no-JavaScript reading, expandable source
notes, canonical/blog links and exact Markdown/clipboard descriptions. Publish
through the repository PR and Pages workflow, then verify the live article and
all five new data/chart assets.

## September 7: existing demand and continuous exposure

The owner clarified the business thesis: buyers already spend heavily on calls,
including when they expect negative financial returns. Product value comes from
serving that demand through an easy on-chain position that continuously
rebalances and rolls its options. Expected outperformance is outside the thesis.

- Lead with demonstrated demand and the proposed spot interface. Explain the
  persistent token and automatic contract maintenance before the payoff example.
- Make portfolio-funded replacement premiums explicit: the investor keeps one
  token while its assets pay the ongoing costs of exposure.
- Preserve the measured NVDA/MU comparison. The approximately 181x combined
  ratio compares call underlying notional with tracked reported perp notional
  OI. Premium value remains a separately labeled capital-value measure; no
  worldwide options/perps ratio or universal product-novelty claim is inferred.
- Update the product and roll diagrams, metadata and figure numbering to match
  the new reading order. Keep payoff mechanics as a product explanation.
- Retain exact market source dates, the implementation record and funded-product
  responsibilities. This publication changes no portfolio or execution rules.

Hugo 0.148.1 and both repository content checks passed. Browser validation at
1280px and 390px passed for all twelve figures, revised reading order, overflow,
five interactive scenarios, keyboard controls, no-JavaScript reading, blog
discovery and Markdown/clipboard parity. Product and roll diagrams were visually
inspected. The PR and Pages workflow record publication, followed by a live-page
check including exact deployed Markdown parity.

## September 7: systematic TIH improvement

The owner requested systematic improvement after a fresh standard TIH assessment
of 81.40/100. The binding editorial goal remains a product primitive serving
existing call demand: continuing single-stock call exposure held as a spot token.
The article keeps its exact title and avoids a positive-expected-return thesis.

Five candidates were evaluated with fifteen fresh scores each. GPT, Fable and
GLM each contribute five reviews. The full experiment table and hashes are in
[the scoring record](options-tee-trackers-tih-20260907.json). Candidate05 is the
selected passing version: overall83.47, GPT86.60, Fable81.20 and GLM82.60. The
TIH comparison rule holds GPT flat or higher and improves the combined Fable/GLM
average against the current passing baseline. Longer candidates with additional
trust and risk framing did not pass; they were not published.

The selected changes distinguish measured call activity from token adoption,
explain portfolio accounting during a roll, define proof/custody responsibilities
and add a compact product-terms paragraph. A read-only recheck from the retained
authenticated Schwab captures reconciled all published market totals and supplied
stock-price, average-premium and maturity context. The original chain selection
and all portfolio rules are unchanged. Source quotes and recovery material remain
private; only derived aggregates enter the article.

The article retains twelve responsive/interactive figures. Its Markdown and
clipboard exports now embed actual PNG figures with concise descriptions. Run
`scripts/export_options_diagrams.py` against the locally served Hugo build after
changing diagram markup, captions or CSS, then rebuild Hugo to include the PNGs.
The figure manifest records the generated assets.

Validation covers Hugo0.148.1, both repository content checks, aggregate and
figure-manifest reconciliation, 1280px/390px rendering, five interactive cases,
keyboard/no-JavaScript behavior, source notes, Markdown/clipboard parity and
embedded image availability. Publish through the repository PR and Pages
workflow and verify the deployed Markdown and all article assets.
