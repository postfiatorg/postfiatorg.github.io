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
