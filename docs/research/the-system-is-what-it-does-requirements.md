# The System Is What It Does: Technical Requirements

Status: scoped build spec
Working title: The System Is What It Does
Companion posts: LLM Governance Replay; Viability of SGLang Replay: Cross-Hardware

## 1. Objective

Build a publishable evidence stack for a blog post about XRPL amendment origination.

The post may claim only this:

> XRPL amendment origination is concentrated, outcome-asymmetric, and increasingly less inspectable at the agenda-setting layer; a transparent-packet, replayable, forkable origination pipeline is constructible with the same primitives demonstrated in the replay posts.

The post must not claim that an LLM knows what amendments should exist, that a model optimizes a correct governance objective, or that transparent origination decentralizes agenda power by itself. The improvement is provenance and replayability, not wisdom.

## 2. Claim Contract

| Claim type | Allowed claim | Forbidden claim |
|---|---|---|
| Origination concentration | A conservative source corpus attributes a majority of amendment-category XLS primary authorship to Ripple-affiliated authors and more when any-coauthor involvement is counted. | Non-Ripple contributors are absent, unwelcome, or irrelevant. |
| Outcome asymmetry | Amendment-category proposals from community-independent authors reach terminal `Final` status at a materially lower rate than Ripple-originated proposals in the frozen corpus. | The gap proves intent, gatekeeping, bad faith, or low quality. |
| Agenda composition | Live Known Amendments cluster heavily into maintenance/fix amendments, with feature amendments concentrated around identifiable protocol surfaces. | Compliance or institutional features are bad, illegitimate, or improper. |
| Venue migration | Some newest specs are hosted on `opensource.ripple.com` and are absent, stubbed, or less complete in the community standards repository at snapshot time. | The community repository is abandoned or all new origination moved. |
| Mechanism | Public packets plus pinned replay functions can make origination inputs, omissions, outputs, and forks inspectable. | The function's output is correct, optimal, binding, or legitimate because of model quality. |

Every empirical sentence in the article must map to one evidence packet row, summary field, or source receipt. Otherwise mark it unverified or remove it.

## 3. Public Artifact Layout

Create one root artifact per publication attempt:

```text
static/benchmarks/xrpl-transparent-origination-YYYYMMDDTHHMMSSZ/
  README.md
  REPORT.md
  CLAIMS.json
  COMMANDS.txt
  SHA256SUMS.txt
  sources/
  ep1_xls_provenance/
  ep2_outcome_asymmetry/
  ep3_agenda_composition/
  ep4_venue_migration/
  ep5_shadow_backlog_triage/
  ep6_packet_spec/
  article_inputs/
  index.html
```

`README.md` is the artifact table of contents. `REPORT.md` is the human-readable packet report. `CLAIMS.json` maps each article claim to supporting files and rows. `COMMANDS.txt` contains exact build and verification commands. `SHA256SUMS.txt` covers every file in the artifact root.

The root must include a simple `index.html` with links to each packet, summary, and hash manifest so all article links resolve on GitHub Pages.

## 4. Source Snapshot Requirements

Every source fetch must emit a receipt:

```json
{
  "source_id": "xrplf_xrpl_standards_repo",
  "url": "https://api.github.com/...",
  "retrieved_at_utc": "2026-..",
  "http_status": 200,
  "etag": "...",
  "last_modified": "...",
  "source_commit_sha": "...",
  "body_sha256": "...",
  "local_path": "sources/..."
}
```

Minimum source set:

| Source | Required for |
|---|---|
| `XRPLF/XRPL-Standards` GitHub contents/git API | EP-1, EP-2, EP-4 |
| XRPL Known Amendments inventory | EP-3 status and `fix*`/feature split |
| XRPL live/mainnet amendment state source | EP-3 enabled/open/in-development reconciliation |
| `opensource.ripple.com` XLS pages | EP-4 venue migration |
| Existing governance replay packet schema/runtime manifests | EP-5, EP-6 |

Do not use ad hoc copied text as evidence. If a source page is HTML, store the fetched HTML and a cleaned text extraction with hashes for both.

## 5. EP-1: XLS Provenance Corpus

Purpose: support origination-concentration claims.

Build script:

```text
scripts/build_xrpl_origination_provenance.py
```

Inputs:

- GitHub API snapshot of `XRPLF/XRPL-Standards`.
- All proposal README files and front matter.
- Git metadata for snapshot commit.

Outputs:

```text
ep1_xls_provenance/xls_proposals.csv
ep1_xls_provenance/xls_proposals.json
ep1_xls_provenance/author_identity_map.json
ep1_xls_provenance/org_classification_rules.json
ep1_xls_provenance/provenance_summary.json
ep1_xls_provenance/REVIEW.md
```

Required row fields:

```text
xls_id
title
category
status
created
updated
source_path
source_url
source_commit_sha
readme_sha256
authors_raw
authors_normalized
emails_raw
proposal_from_raw
primary_author_name
primary_author_org
any_ripple_author
any_ex_ripple_or_labs_author
classification_basis
classification_confidence
manual_review_required
```

Classification rules:

- `@ripple.com` email anywhere in the corpus classifies that normalized person as Ripple-affiliated throughout the corpus.
- `proposal-from` and explicit organization fields can classify a proposal only when present and source-backed.
- Residual unknowns default to community-independent, not Ripple. This makes concentration conservative.
- Ambiguous author identity must be flagged in `manual_review_required`, not silently resolved.

Acceptance criteria:

- Corpus snapshot commit SHA is frozen.
- Every proposal row has a source path, source URL, source commit, and README hash.
- Summary includes overall and amendment-category primary-author percentages.
- Summary includes overall and amendment-category any-Ripple-coauthor percentages.
- A manual-review table lists all ambiguous identities.

## 6. EP-2: Origination Outcome Asymmetry

Purpose: support who-ships claims.

Build script:

```text
scripts/build_xrpl_origination_outcomes.py
```

Inputs:

- EP-1 normalized corpus.
- Amendment-category filter.

Outputs:

```text
ep2_outcome_asymmetry/outcome_by_group.csv
ep2_outcome_asymmetry/status_spread_by_group.json
ep2_outcome_asymmetry/community_final_list.csv
ep2_outcome_asymmetry/confound_note.md
ep2_outcome_asymmetry/outcome_summary.json
```

Required metrics:

```text
group
proposal_count
final_count
final_rate
draft_count
stagnant_count
deprecated_count
rejected_or_withdrawn_count
unknown_status_count
```

Required caveats:

- `Final` in the standards repo is not equivalent to mainnet enabled.
- Outcome asymmetry has plausible non-gatekeeping explanations: full-time engineering capacity, funding, quality, coordination, implementation bandwidth, review responsiveness, and relationship to the reference implementation.
- The article may say "outcome-asymmetric"; it may not say "suppressed" unless separately proven.

Acceptance criteria:

- `confound_note.md` is quoted or paraphrased in the article.
- Every community-independent `Final` amendment is listed by XLS id, title, author group, source URL, and current mainnet-state reconciliation status.
- Summary denominators match EP-1 row counts exactly.

## 7. EP-3: Agenda Composition

Purpose: support "the system is what it does" without making a moral claim.

Build script:

```text
scripts/build_xrpl_agenda_composition.py
```

Inputs:

- XRPL Known Amendments inventory snapshot.
- Mainnet amendment-state source.
- Amendment descriptions.

Outputs:

```text
ep3_agenda_composition/known_amendments_snapshot.json
ep3_agenda_composition/known_amendments.csv
ep3_agenda_composition/fix_vs_feature_summary.json
ep3_agenda_composition/feature_tags.csv
ep3_agenda_composition/status_reconciliation.csv
ep3_agenda_composition/composition_summary.md
```

Required classification:

```text
amendment_name
amendment_id
known_amendments_status
mainnet_state
is_fix_prefix
maintenance_or_feature
feature_theme
theme_justification_quote_or_paraphrase
source_url
source_sha256
manual_review_required
```

Allowed feature themes:

- `authorization_or_permissions`
- `compliance_or_identity_surface`
- `institutional_or_asset_control`
- `market_structure`
- `core_ledger_semantics`
- `developer_or_infrastructure`
- `other`

Acceptance criteria:

- `fix*` ratio is computed directly from the live Known Amendments inventory snapshot.
- Feature tags are justified by amendment descriptions, not vibes.
- The article uses at most one compositional sentence beyond the table.
- `Final`, `enabled`, `open_for_voting`, and `not_present` are reconciled explicitly.

## 8. EP-4: Venue Migration

Purpose: support "current origination is partly moving off the shared venue."

Build script:

```text
scripts/build_xrpl_venue_migration.py
```

Inputs:

- `XRPLF/XRPL-Standards` snapshot.
- `opensource.ripple.com` pages for XLS-96, XLS-100, and check XLS-94/XLS-82.

Outputs:

```text
ep4_venue_migration/venue_inventory.csv
ep4_venue_migration/source_receipts.json
ep4_venue_migration/community_repo_presence.json
ep4_venue_migration/ripple_domain_presence.json
ep4_venue_migration/venue_summary.md
```

Required row fields:

```text
xls_id
title
community_repo_status
community_repo_path
community_repo_url
community_repo_sha256
ripple_domain_status
ripple_domain_url
ripple_domain_sha256
retrieved_at_utc
classification
notes
```

Allowed `classification` values:

- `hosted_in_both`
- `community_complete_ripple_absent`
- `ripple_complete_community_absent`
- `ripple_complete_community_stub`
- `unverified`

Acceptance criteria:

- Every URL has a fetch receipt.
- If any target spec cannot be fetched, article language must say `unverified` or omit the claim.
- The article must say this strengthens EP-1 only if the missing/off-repo specs are not included in EP-1 denominators.

## 9. EP-5: Shadow Backlog Triage

Purpose: bridge origination analysis to the replay mechanism.

Build script:

```text
scripts/build_xrpl_shadow_backlog_triage.py
scripts/run_qwen_xrpl_shadow_backlog_triage.py
scripts/summarize_xrpl_shadow_backlog_triage.py
```

Inputs:

- EP-1 and EP-2 corpus rows.
- Community-independent amendment-category proposals with `Stagnant`, `Draft`, `Deprecated`, or equivalent non-final status.
- Existing governance replay runtime profile and parser where compatible.

Outputs:

```text
ep5_shadow_backlog_triage/selection_manifest.csv
ep5_shadow_backlog_triage/origination_packets/
ep5_shadow_backlog_triage/qwen_runs/
ep5_shadow_backlog_triage/commit_reveal/
ep5_shadow_backlog_triage/omission_logs/
ep5_shadow_backlog_triage/triage_summary.json
ep5_shadow_backlog_triage/runtime_manifest.json
ep5_shadow_backlog_triage/machine_receipt.json
```

Packet schema additions:

```text
proposal_identity
source_list
source_excerpts
submitter_claims
implementation_status
risk_surface_tags
missing_evidence
conflicting_evidence
omission_log
packet_compiler_identity
packet_hash
schema_version
objective_function: null
```

Allowed output labels:

```text
NEEDS_SOURCE_PACKET
NEEDS_IMPLEMENTATION_EVIDENCE
NEEDS_SECURITY_REVIEW
NEEDS_ECONOMIC_ANALYSIS
NEEDS_SPEC_CLARITY
READY_FOR_PUBLIC_DISCUSSION
REJECT_PACKET_INSUFFICIENT
```

Forbidden output behavior:

- No autonomous `PROCEED`.
- No "should pass".
- No ranking by author identity.
- No objective-function optimization.

Acceptance criteria:

- Every packet has an omission log.
- Every output is hash-bound by packet hash, prompt hash, model profile hash, raw output hash, and parsed output hash.
- Summary foregrounds failure and missing-evidence counts.
- Article claim is only: "this produces transparent, replayable, contestable first-pass work items over a dead/ignored backlog."

## 10. EP-6: Transparent-Origination Packet Spec

Purpose: make the mechanism concrete.

Build script:

```text
scripts/build_transparent_origination_packet_spec.py
```

Outputs:

```text
ep6_packet_spec/transparent_origination_packet.schema.json
ep6_packet_spec/example_packet.json
ep6_packet_spec/example_commit_reveal.json
ep6_packet_spec/field_level_claims.md
ep6_packet_spec/non_goals.md
```

Required field-level statement:

> No objective function is encoded. The replay function reads a public packet and emits a typed first pass. It does not optimize a named governance goal, weigh author identity, or grant legitimacy to the output.

Optional fields:

```text
submitter_identity_did
declared_stake
motivated_reasoning_disclosure
packet_compiler_identity
```

Constraint: optional identity/stake fields are transparency amplifiers only. They must not be weighting inputs in this piece.

## 11. Validation Gates

Implement one validator:

```text
scripts/validate_xrpl_transparent_origination_artifact.py
```

Gate checks:

- `SHA256SUMS.txt` verifies.
- All source receipts have URL, retrieval time, body hash, and local path.
- EP-1 denominators equal EP-2 denominators where expected.
- No empirical claim in `CLAIMS.json` points to a missing file or missing row.
- No article claim uses forbidden language: `proves gatekeeping`, `LLM should decide`, `model discovered what should pass`, `decentralizes origination`, `objective function`.
- Every public artifact directory has `index.html`.
- Every article-relative `/benchmarks/...` link exists in `public/` after Hugo build.

## 12. Article Build Gate

Before promotion:

1. Build all packets from scratch into a new timestamped root.
2. Run the artifact validator.
3. Run Hugo locally or through Actions.
4. Crawl all `/benchmarks/...` links in the generated article.
5. Score the article with the standard 5-run GPT/Opus/DeepSeek harness.
6. Promote only if score does not drop relative to the current comparable candidate and Opus objections are addressed in the claim boundary.

Minimum publishable state:

- EP-1 through EP-4 complete and verified.
- EP-6 complete.
- EP-5 may be absent only if the article clearly says the transparent origination pipeline is specified but not yet replay-demonstrated. If EP-5 is absent, do not claim the mechanism has been demonstrated upstream.

Preferred publishable state:

- EP-1 through EP-6 complete.
- EP-5 run on the full conservative community backlog subset.
- All evidence links live at `postfiat.org` before social distribution.

## 13. Implementation Order

1. Build EP-1/EP-2 corpus freeze and outcome tables.
2. Build EP-3 Known Amendments composition and status reconciliation.
3. Build EP-4 venue migration receipts.
4. Build EP-6 packet schema.
5. Build EP-5 shadow backlog triage only after EP-1/EP-2 selection is frozen.
6. Draft article from `CLAIMS.json`, not from memory.
7. Score, revise, build, deploy, and live-link-check.

## 14. Article Skeleton Constraint

The article should use this five-beat structure:

1. The originary question: from whence does the menu come?
2. The data: concentration, outcome asymmetry, composition, venue migration.
3. The turn: the fix is transparent whence, not better whence.
4. The mechanism: forkable packets, pinned replay, typed output, public commit.
5. Boundaries and open door: keep identity-aware memory/refusal for a later piece.

The title can be `The System Is What It Does`. The phrase should refer to measured origination/output composition, not to intent.
