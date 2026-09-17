# Index turnover and recurring revenue model

17 September 2026. Derived from the existing NavStrategies fundamental-index evaluation; no new portfolio backtest or trading rule was run.

## Historical inputs

The evaluation reconstructed SHARADAR/SP500 historical membership across 113 quarter-end transitions, 31 March 1998 through 30 June 2026. Churn is entrants divided by 500, with a mean of **1.221238938% per quarter**. This counts changed names, not dollars traded. It excludes weight changes within surviving names and may miss additions/removals between snapshots. The denominator remains 500 even when multiple share classes raise the security count.

For an illustrative equal-sized-replacement portfolio only, multiplying the mean by four produces **4.884955752% annual one-way replacement turnover** and **9.769911504% two-sided trade notional**. This is a membership-based scenario, not a measurement of cap-weighted S&P 500 portfolio turnover.

The canonical fundamental-index evaluation separately measured **6.710432357% one-way weight turnover per rebalance**, annualized here at its four-rebalance cadence to **26.841729426%**. Its code measures one-way turnover as half the sum of absolute changes from drifted prior weights. Its mean excludes initial portfolio funding. Total buying plus selling is twice that one-way amount in the fully invested, self-financing case.

## Revenue assumptions

- $1 million constant tracked assets for the sample; no price returns or added/withdrawn capital during the recurring-revenue year.
- Target fee: **20bp on each executed buy and sell notional**, including qualifying rebalances. Hugo must negotiate that fee base directly with Ondo or an alternative; execution through another route does not create an AIC receipt.
- 100% of modeled rebalance notional is followed and executed through the fee-bearing route. At 50% participation, recurring fees halve.
- Illustrative direct costs: 20% of collected fees. Illustrative creator split: 50% of the remainder. Creator and AIC each retain 40% of gross receipts before their own further expenses.
- Curated scenarios assume 25% one-way turnover quarterly or monthly solely to show sensitivity. These are not observed creator behavior, recommended churn targets, or new strategy/backtest rules.

| Case | Annual one-way turnover | Rebalance buys + sells | Annual gross recurring fees | Creator recurring income | AIC recurring contribution |
|---|---:|---:|---:|---:|---:|
| S&P member-count proxy | 4.885% | $97,699 | $195 | $78 | $78 |
| Fundamental-index research | 26.842% | $536,835 | $1,074 | $429 | $429 |
| Curated: 25% quarterly | 100% | $2,000,000 | $4,000 | $1,600 | $1,600 |
| Curated: 25% monthly | 300% | $6,000,000 | $12,000 | $4,800 | $4,800 |

At $1m assets, initial funding adds $2,000 gross and $800 each to creator/AIC; a later full exit adds the same if it incurs the same fee. Neither is included in the recurring columns. At 25% monthly turnover, year one including entry produces $14,000 gross and $5,600 each. Three years of steady assets plus entry and final exit produces $40,000 gross and $16,000 each. Multiply these values by ten for $10m of participating assets.

Revenue is charged on actual notional, not number of orders, not hypothetical rebalances and not a double count of partial-fill receipts. A maintained index can generate repeated fees from the same assets. Portfolio turnover and customer retention are different inputs; voluntary participation and assets remaining on the route determine realized revenue.

## NAVCoin fee business

A NAVCoin series can charge a disclosed recurring fee on average net asset value/TVL, like an ETF fee model. For one year, gross product fees equal average fee-bearing TVL times the annual fee rate. Accrual periods shorter than a year are prorated. Rates below are sensitivities, not agreed fees or retained AIC margins.

| Average TVL | 25bp annually | 50bp annually | 100bp annually |
|---|---:|---:|---:|
| $1m | $2,500 | $5,000 | $10,000 |
| $10m | $25,000 | $50,000 | $100,000 |
| $50m | $125,000 | $250,000 | $500,000 |
| $100m | $250,000 | $500,000 | $1,000,000 |

Custody, administration, data, reserve trading and any manager/creator share determine AIC’s retained economics. Do not count the same assets as both a spot-following account and a NAVCoin fee base without a genuine, separately disclosed fee arrangement. Portfolio trading and entry/exit charges must be disclosed if added to the NAVCoin fee.

## Reproducibility

Source repository: `postfiatorg/navstrategies`, inspected HEAD `4703c2eee3a555c22a573cb1c94287517a8ab181`.

- `research/pre_catalyst/data_exploration/sec_10q_size_proxy/open_sec_fundamental_index_sp500_churn.csv`
- `research/pre_catalyst/data_exploration/sec_10q_size_proxy/open_sec_fundamental_index_profit_measure_comparison.csv`, canonical row
- `navstrategies/research/open_sec_fundamental_index_report.py`, `sp500_membership_churn`
- `navstrategies/research/sec_10q_size_proxy.py`, `calculate_turnover`
- Local derived calculation: `documents/aic-proposal-20260916/sources/calculate_turnover_economics.py`; exact inputs and hashes in `sources/turnover-economics.json`.

Only aggregate research results and hypothetical commercial sensitivities are presented here; the licensed membership history is not redistributed.
