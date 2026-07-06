# PFTerminal Launch Phase 1 Evidence

Generated: `2026-07-06T01:17:13Z`
Run root: `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705`
Root raw CSV: `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/raw_waves.csv`
Shipped binary evidence: `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/install-evidence` version `pfterminal 0.1.8`.
Exact-key scan: `0` hits; artifact `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/key_scan.json`.
Spend ledger: `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/cost_ledger.json` recorded `$379.515133` cap `$400.00`.

## Method

Speed pools all same-binary paired rows from the day. Vercel legacy `/v1/generation` cost is discarded for launch dollars. Billed Vercel cost comes from `/v1/report` grouped by `api_key_name` before/after deltas for the key-isolated top-up run. Billed frontier cost comes from Anthropic Admin Usage grouped by `api_key_id` and model when the key window is clean. The Fable Claude Code Admin window contains disclosed non-cohort traffic, so publishable Fable benchmark dollars are recovered from counted rows' API-reported token breakdown multiplied by the same published Anthropic price schedule. Per-task and per-row dollars are allocated or recovered as labelled; arm-level clean totals are provider-key billed.

Vercel report settle: `pass`; artifact `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/keyed_parallel_20260705/vercel_report_settle.json`.
Vercel key-name probe adjustment: `True`; details `{'probe_adjustments_by_api_key_name': {'vcel2': {'cost_delta': 7.4e-05, 'request_delta': 1}, 'vcel3': {'cost_delta': 0.000148, 'request_delta': 2}}, 'probe_artifacts': ['/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/keyed_parallel_20260705/vercel_key_name_probe_vercel_proper.json', '/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/keyed_parallel_20260705/vercel_key_name_probe_all.json'], 'reason': 'subtract isolated Vercel key-name probe requests run after benchmark completion'}`.
Anthropic Admin key validation: `pass`; artifact `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/keyed_parallel_20260705/frontier_lane_key_validation.json`.
Anthropic Admin settle: `pass`; artifact `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/keyed_parallel_20260705/frontier_admin_settle.json`.
Same-model fairness controls: `pass`; artifact `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/keyed_parallel_20260705/frontier_fairness_controls.json`.
Frontier row-priced cost recovery: `pass`; artifact `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/keyed_parallel_20260705/frontier_row_priced_cost_recovery.json`.
Proxy transparency/model audit: `review` rows `150` review rows `55`; artifact `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/proxy_transparency_audit.json`.
Scoped Vercel billed-cohort proxy audit: `review` rows `100` review rows `2`; artifact `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/proxy_transparency_audit_keyed_vercel.json`.
Keyed allocations: `301` rows; artifact `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/keyed_parallel_20260705/keyed_cost_allocations.json`.

## Billed Lane Totals

| lane | source | billed total | request/model detail |
| --- | --- | ---: | --- |
| Vercel hermes | `/v1/report api_key_name=vcel3` | $36.576664 | requests delta `962` |
| Vercel pfterminal | `/v1/report api_key_name=vcel2` | $18.458699 | requests delta `796` |
| Frontier opus_pfterminal | `Admin Usage api_key_id/model` | $20.413234 | model `claude-opus-4-8` key `apikey_01CgoTt8K32z8kiqLkERjBpn` |
| Frontier opus_claude_code | `Admin Usage api_key_id/model` | $53.540317 | model `claude-opus-4-8` key `apikey_016t3eMqE5rFmPyzMNGsHBro` |
| Frontier fable_pfterminal | `Admin Usage api_key_id/model` | $59.101639 | model `claude-fable-5` key `apikey_01ETPF8aNWXS17BDVpWkzPQD` |
| Frontier fable_claude_code | `Admin Usage api_key_id/model` | $97.872099 | model `claude-fable-5` key `apikey_01SkUWKM1VvMXAt2CR4H3Mk6` |

## Row-Priced Fable Cost Recovery

Recovery status: `pass`. Fable publishable cost ratio uses counted-row API tokens x published price schedule, not the contaminated raw fable5 Admin window.
Fable clean cost ratio Claude Code/PFTerminal: `1.43x`. Raw Admin-window Fable ratio, not publishable: `1.66x`.
Opus clean Admin headline ratio Claude Code/PFTerminal: `2.62x`.

| lane | rows | row-priced counted cost | raw Admin window cost | row-vs-Admin cost delta | token delta | publish status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| opus_pfterminal | 41 | $20.414204 | $20.413234 | 0.005% | 0.000% | pass_clean_admin_window |
| opus_claude_code | 42 | $53.540317 | $53.540317 | 0.000% | 0.000% | pass_clean_admin_window |
| fable_pfterminal | 59 | $57.025011 | $59.101639 | -3.514% | -2.735% | pass_clean_admin_window |
| fable_claude_code | 59 | $81.699669 | $97.872099 | -16.524% | -16.180% | pass_row_priced_contamination_excluded |

Credibility proof: Opus PfTerminal row-vs-Admin cost delta `0.005%`; Opus Claude Code `0.000%`; Fable PfTerminal row-vs-Admin cost delta `-3.514%` with token delta `-2.735%`.
Fable5 contamination: Admin excess `3649460` tokens, price-weighted `$16.172429`. Direct fable5 probe was `20` tokens / `$0.000360`; remaining excess is attributed to interrupted/resumed fable5 Claude Code attempts outside the counted paired cohort. Resume manifest `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/keyed_parallel_20260705/fable_resume_manifest.json`.

## Vercel GLM Cost Reconciliation

Status: `pass`. GLM cost is clean provider `/v1/report` key-isolated billing by `api_key_name`; non-benchmark key-name probes were subtracted before reporting.
- `hermes` / `vcel3`: benchmark billed delta `$36.576664`, requests `962`, subtracted probes `2` / `$0.000148`.
- `pfterminal` / `vcel2`: benchmark billed delta `$18.458699`, requests `796`, subtracted probes `1` / `$0.000074`.

## Same-Model Fairness Controls

Publish gate: `pass`. Same-model cost claims are blocked unless this is `pass`.
Token reconciliation artifact: `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/keyed_parallel_20260705/frontier_token_reconciliation.json`.
Row-priced recovery artifact: `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/keyed_parallel_20260705/frontier_row_priced_cost_recovery.json`.
Estimator note: Local dollar estimates and Claude Code total_cost_usd are informational only. Admin Usage by api_key_id/model is authoritative for clean key windows; the contaminated fable5 window is disclosed and the publishable Fable benchmark cost is recovered from counted rows' API-reported tokens x the same published price schedule.

| lane | Admin cost | row-priced recovered cost | weighted-token cost | Admin/token delta | row-token total delta | Admin excess tokens | local estimate delta (info) | token breakdown | cleanliness |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| opus_pfterminal | $20.413234 | $20.414204 | $20.413234 | 0.000% | 0.000% | 0 | 0.005% | in 776, out 268068, cache-read 10002521, cache-write 1393023+0 | pass |
| opus_claude_code | $53.540317 | $53.540317 | $53.540317 | 0.000% | 0.000% | 0 | 0.000% | in 1190, out 920533, cache-read 25721822, cache-write 2825621+0 | pass |
| fable_pfterminal | $59.101639 | $57.025011 | $59.101639 | 0.000% | -2.735% | 431003 | 3.514% | in 1106, out 397166, cache-read 13287417, cache-write 2075589+0 | pass |
| fable_claude_code | $97.872099 | $81.699669 | $97.872099 | 0.000% | -16.180% | 3649460 | 16.524% | in 1780, out 892780, cache-read 18917411, cache-write 2743831+0 | pass_row_priced_contamination_excluded |

| comparison | Admin window ratio CC/PfT | weighted-token ratio CC/PfT | publishable cost ratio | publishable method | delta | speed median [IQR] | token check | slow CC rows |
| --- | ---: | ---: | ---: | --- | ---: | ---: | --- | ---: |
| opus_frontier | 2.62x | 2.62x | 2.62x | `admin_usage_api_key_id` | 0.000% | 2.94x [2.47x, 4.87x] | pass | 0 |
| fable_frontier | 1.66x | 1.66x | 1.43x | `row_api_tokens_x_published_price_schedule` | 0.000% | 1.87x [1.53x, 2.13x] | pass | 0 |

Effort/thinking capture:
- `claude-opus-4-8` `pfterminal`: effort `None`, thinking `{'type': 'adaptive', 'display': 'summarized'}`, basis `pfterminal anthropic request dump`, artifact `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/results/opus_frontier/queryforge/pfterminal/wave10`.
- `claude-opus-4-8` `claude-code`: effort `None`, thinking `None`, basis `claude-code command line; raw Anthropic request not exposed by CLI artifact`, artifact `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/results/opus_frontier/queryforge/claude-code/wave10`.
- `claude-fable-5` `pfterminal`: effort `None`, thinking `{'type': 'adaptive', 'display': 'summarized'}`, basis `pfterminal anthropic request dump`, artifact `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/results/fable_frontier/queryforge/pfterminal/wave1`.
- `claude-fable-5` `claude-code`: effort `None`, thinking `None`, basis `claude-code command line; raw Anthropic request not exposed by CLI artifact`, artifact `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/results/fable_frontier/queryforge/claude-code/wave1`.
- Disclosure: PFTerminal request dumps expose explicit thinking fields. Claude Code CLI artifacts expose command flags but not the raw Anthropic request; absent flags are reported as default/unverified rather than assumed matched.

Equivalent output / over-build proxy:
- `opus_frontier` `pfterminal`: pass `41/41`, median source lines `2265.0` IQR `[484.5, 3479.0]`.
- `opus_frontier` `claude-code`: pass `42/42`, median source lines `2273.0` IQR `[594.0, 3482.0]`.
- `fable_frontier` `pfterminal`: pass `59/59`, median source lines `2266.0` IQR `[439.0, 3478.0]`.
- `fable_frontier` `claude-code`: pass `59/59`, median source lines `2266.0` IQR `[599.0, 3481.0]`.

## Tables

### vercel_glm

| task | speed N | billed cost N | pass A/B | A wall mean +/- 95% CI | B wall mean +/- 95% CI | paired B/A speed mean | speed median [IQR] | p speed | A billed cost mean +/- 95% CI | B billed cost mean +/- 95% CI | paired B/A cost mean | cost median [IQR] | p cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| eventforge | 20 | 10 | 20/20 vs 20/20 | 68.481s +/- 9.204s | 90.812s +/- 11.790s | 1.43x | 1.12x [1.00x, 1.67x] | 0.0027 | $0.461126 +/- $0.126163 | $0.579446 +/- $0.133544 | 1.32x | 1.13x [0.98x, 1.79x] | 0.0273 |
| rategate | 20 | 10 | 20/20 vs 20/20 | 30.202s +/- 4.679s | 43.830s +/- 5.501s | 1.56x | 1.37x [1.20x, 1.93x] | 0.0003 | $0.158491 +/- $0.033900 | $0.217892 +/- $0.044658 | 1.45x | 1.27x [1.21x, 1.78x] | 0.0195 |
| confclerk | 20 | 10 | 20/20 vs 20/20 | 24.869s +/- 6.092s | 46.904s +/- 6.502s | 2.21x | 2.07x [1.52x, 2.58x] | 0.0005 | $0.168637 +/- $0.033444 | $0.331789 +/- $0.088818 | 2.12x | 1.73x [1.39x, 2.76x] | 0.0020 |
| queuecraft | 20 | 10 | 20/20 vs 20/20 | 51.296s +/- 9.360s | 89.219s +/- 8.412s | 1.88x | 1.67x [1.50x, 2.18x] | 9.54e-06 | $0.586187 +/- $0.132878 | $1.462447 +/- $0.350396 | 2.64x | 2.39x [2.30x, 3.48x] | 0.0039 |
| pipeflow | 20 | 10 | 20/20 vs 20/20 | 57.810s +/- 7.440s | 111.522s +/- 18.162s | 2.00x | 1.88x [1.45x, 2.25x] | 1.91e-06 | $0.471428 +/- $0.084169 | $1.066093 +/- $0.347238 | 2.41x | 1.98x [1.37x, 3.20x] | 0.0020 |

Overall `vercel_glm`: speed N `100`, billed cost N `50`. `pfterminal` wall 46.531s +/- 4.501s, billed cost $0.369174 +/- $0.060789; `hermes` wall 76.457s +/- 6.932s, billed cost $0.731533 +/- $0.160168; paired speed ratio mean `1.82x`, median/IQR `1.63x [1.28x, 2.20x]`; paired cost ratio mean `1.99x`, median/IQR `1.78x [1.21x, 2.42x]`.

### opus_frontier

| task | speed N | billed cost N | pass A/B | A wall mean +/- 95% CI | B wall mean +/- 95% CI | paired B/A speed mean | speed median [IQR] | p speed | A billed cost mean +/- 95% CI | B billed cost mean +/- 95% CI | paired B/A cost mean | cost median [IQR] | p cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| queuecraft | 20 | 13 | 20/20 vs 20/20 | 50.239s +/- 2.784s | 298.591s +/- 35.734s | 6.01x | 5.73x [4.87x, 7.65x] | 1.91e-06 | $0.409330 +/- $0.029249 | $1.586351 +/- $0.195378 | 3.94x | 3.94x [3.16x, 4.62x] | 0.0002 |
| textwright | 20 | 14 | 20/20 vs 20/20 | 65.269s +/- 5.163s | 176.468s +/- 12.729s | 2.77x | 2.68x [2.52x, 3.15x] | 1.91e-06 | $0.525113 +/- $0.067338 | $1.100779 +/- $0.089360 | 2.20x | 2.10x [1.85x, 2.65x] | 0.0001 |
| queryforge | 20 | 14 | 20/20 vs 20/20 | 154.691s +/- 10.778s | 381.816s +/- 34.093s | 2.52x | 2.43x [2.22x, 2.63x] | 3.81e-06 | $0.552883 +/- $0.065698 | $1.145059 +/- $0.124000 | 2.11x | 2.10x [1.93x, 2.48x] | 0.0001 |

Overall `opus_frontier`: speed N `60`, billed cost N `41`. `pfterminal` wall 90.067s +/- 12.611s, billed cost $0.497884 +/- $0.035905; `claude-code` wall 285.625s +/- 27.164s, billed cost $1.269861 +/- $0.099878; paired speed ratio mean `3.77x`, median/IQR `2.94x [2.47x, 4.87x]`; paired cost ratio mean `2.72x`, median/IQR `2.48x [2.04x, 3.25x]`.

### fable_frontier

| task | speed N | billed cost N | pass A/B | A wall mean +/- 95% CI | B wall mean +/- 95% CI | paired B/A speed mean | speed median [IQR] | p speed | A billed cost mean +/- 95% CI | B billed cost mean +/- 95% CI | paired B/A cost mean | cost median [IQR] | p cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| queuecraft | 20 | 19 | 20/20 vs 20/20 | 85.784s +/- 5.704s | 176.045s +/- 11.668s | 2.08x | 2.07x [1.87x, 2.37x] | 1.91e-06 | $0.969291 +/- $0.053852 | $1.615451 +/- $0.097918 | 1.69x | 1.69x [1.52x, 1.93x] | 3.81e-06 |
| textwright | 20 | 20 | 20/20 vs 20/20 | 73.550s +/- 5.050s | 138.689s +/- 7.724s | 1.94x | 1.83x [1.62x, 2.03x] | 1.91e-06 | $0.856517 +/- $0.057455 | $1.158830 +/- $0.091971 | 1.37x | 1.36x [1.22x, 1.49x] | 9.54e-06 |
| queryforge | 20 | 20 | 20/20 vs 20/20 | 150.257s +/- 14.004s | 223.099s +/- 15.327s | 1.55x | 1.44x [1.19x, 1.93x] | 1.91e-06 | $1.073908 +/- $0.093497 | $1.391475 +/- $0.095411 | 1.35x | 1.19x [1.03x, 1.65x] | 0.0002 |

Overall `fable_frontier`: speed N `60`, billed cost N `59`. `pfterminal` wall 103.197s +/- 10.088s, billed cost $0.966526 +/- $0.045149; `claude-code` wall 179.278s +/- 11.100s, billed cost $1.384740 +/- $0.070925; paired speed ratio mean `1.86x`, median/IQR `1.87x [1.53x, 2.13x]`; paired cost ratio mean `1.47x`, median/IQR `1.46x [1.19x, 1.72x]`.


## Evidence Paths

- Raw waves CSV: `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/raw_waves.csv`
- Keyed run directory: `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/keyed_parallel_20260705`
- Vercel report settle: `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/keyed_parallel_20260705/vercel_report_settle.json`
- Vercel raw settle before probe subtraction: `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/keyed_parallel_20260705/vercel_report_settle.raw_including_key_probes.json`
- Vercel key-name probes: `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/keyed_parallel_20260705/vercel_key_name_probe_vercel_proper.json`, `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/keyed_parallel_20260705/vercel_key_name_probe_all.json`
- Frontier Admin settle: `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/keyed_parallel_20260705/frontier_admin_settle.json`
- Frontier key validation: `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/keyed_parallel_20260705/frontier_lane_key_validation.json`
- Frontier fairness controls: `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/keyed_parallel_20260705/frontier_fairness_controls.json`
- Frontier row-priced cost recovery: `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/keyed_parallel_20260705/frontier_row_priced_cost_recovery.json`
- Keyed cost allocations: `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/keyed_parallel_20260705/keyed_cost_allocations.json`
- Proxy transparency audit: `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/proxy_transparency_audit.json`
- Scoped Vercel billed-cohort proxy audit: `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/proxy_transparency_audit_keyed_vercel.json`
- Key scan: `/home/pfrpc/repos/pfterminal-perf-probe/runs/launch-phase1-0.1.8-highn-20260705/key_scan.json`

## Review Status

Angmar review is required before any of these numbers enter the launch post.
