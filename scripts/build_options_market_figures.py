"""Build the article's static research figures from its public aggregate record.

Run with Python and matplotlib. No brokerage connection or source quotes needed.
"""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'static/research/options-tee-indices'
DATA = json.loads((OUT / 'market-sizing-20260907.json').read_text())
GREEN, BLUE, AMBER = '#9bf080', '#b1d7ff', '#f5cc84'
INK, MUTED, BG, GRID = '#e7f6e3', '#b0c4aa', '#111b12', '#344532'

def setup(font):
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': font,
        'figure.facecolor': BG, 'axes.facecolor': BG, 'text.color': INK,
        'axes.labelcolor': MUTED, 'xtick.color': MUTED, 'ytick.color': INK,
        'text.parse_math': False, 'axes.edgecolor': GRID, 'axes.spines.top': False, 'axes.spines.right': False,
        'axes.spines.left': False, 'svg.fonttype': 'none', 'svg.hashsalt': 'options-convexity-v1'})

def save(fig, name):
    fig.savefig(OUT / name, facecolor=BG, metadata={'Date': None})
    plt.close(fig)

def market(mobile=False):
    setup(11 if mobile else 15)
    fig, axes = plt.subplots(2, 1, figsize=(4.4, 8.6) if mobile else (10, 7.3))
    premium, exposure = axes
    fig.subplots_adjust(left=.18 if mobile else .12, right=.97, top=.9,
                        bottom=.16 if mobile else .14, hspace=.70 if mobile else .72)
    for ax in axes:
        ax.set_axisbelow(True)
        ax.grid(axis='x', color=GRID, linewidth=.7)
        ax.tick_params(axis='y', length=0)
        ax.set_yticks([1, 0], ['NVDA', 'MU'])
        ax.set_ylim(-.6, 1.6)
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'${x:g}B'))
    premium.set_title('Value of outstanding call premiums', loc='left', pad=20,
                      fontsize=12 if mobile else 17, weight='bold')
    exposure.set_title('Underlying notional: calls and perps', loc='left', pad=20,
                       fontsize=12 if mobile else 17, weight='bold')
    for y, row in zip([1, 0], DATA['rows']):
        value = row['call_premium_mid_usd'] / 1e9
        premium.barh(y, value, height=.43, color=GREEN)
        premium.text(value + .1, y, f'${value:.2f}B', va='center', weight='bold', fontsize=12 if mobile else 17)
        calls = row['call_underlying_notional_usd'] / 1e9
        perps = row['perp_reported_tracked_venue_oi_usd'] / 1e9
        exposure.barh(y + .17, calls, height=.27, color=GREEN, label='ATM/OTM calls' if y else None)
        exposure.barh(y - .17, perps, height=.27, color=AMBER, label='Reported perp OI' if y else None)
        exposure.text(calls + 1.5, y + .17, f'${calls:.2f}B', va='center', weight='bold', fontsize=11 if mobile else 15)
        exposure.text(perps + 1.5, y - .17, f'${perps * 1000:.1f}M', va='center', color=AMBER, fontsize=11 if mobile else 15)
    premium.set_xlim(0, 5.7 if mobile else 5.3)
    premium.set_xticks([0, 2, 4] if mobile else [0, 1, 2, 3, 4, 5])
    exposure.set_xlim(0, 115 if mobile else 103)
    exposure.set_xticks([0, 50, 100] if mobile else [0, 25, 50, 75, 100])
    handles, labels = exposure.get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower left', bbox_to_anchor=(.05 if mobile else .1, .015),
               frameon=False, ncol=1 if mobile else 2, labelcolor=MUTED, fontsize=10 if mobile else 12)
    save(fig, 'call-market-sizing-mobile.svg' if mobile else 'call-market-sizing.svg')

def payoff(mobile=False):
    setup(11 if mobile else 16)
    fig, ax = plt.subplots(figsize=(4.4, 5.8) if mobile else (10, 6.8))
    fig.subplots_adjust(left=.19 if mobile else .11, right=.97, top=.81, bottom=.18 if mobile else .16)
    stock = list(range(60, 151))
    pnl = [max(s - 100, 0) - 10 for s in stock]
    ax.set_axisbelow(True)
    ax.grid(color=GRID, linewidth=.7)
    ax.axhline(0, color=MUTED, linewidth=1)
    ax.plot(stock, pnl, color=GREEN, linewidth=3.5)
    ax.fill_between(stock, pnl, 0, where=[v >= 0 for v in pnl], color=GREEN, alpha=.12)
    ax.scatter([80, 110, 140], [-10, 0, 30], color=[AMBER, BLUE, GREEN], s=50, zorder=4)
    ax.annotate('Maximum loss: $10', (80, -10), xytext=(63, -19), color=AMBER,
                fontsize=10 if mobile else 14)
    ax.annotate('Breakeven\n$110' if mobile else 'Breakeven: $110', (110, 0),
                xytext=(91, 10) if mobile else (91, 9), color=BLUE,
                arrowprops={'arrowstyle': '-', 'color': BLUE}, fontsize=10 if mobile else 14)
    ax.annotate('Stock $140\nProfit $30', (140, 30), xytext=(119, 39), color=GREEN,
                arrowprops={'arrowstyle': '-', 'color': GREEN}, fontsize=10 if mobile else 14)
    ax.set_xlim(60, 150); ax.set_ylim(-24, 52)
    ax.set_xticks([60, 80, 100, 120, 140]); ax.set_yticks([-10, 0, 20, 40])
    dollars = FuncFormatter(lambda v, _: f'-${abs(v):g}' if v < 0 else f'${v:g}')
    ax.xaxis.set_major_formatter(dollars); ax.yaxis.set_major_formatter(dollars)
    ax.set_xlabel('Stock price at expiry', labelpad=14)
    ax.set_ylabel('Profit / loss per share', labelpad=8)
    fig.text(.06, .945, 'A defined downside. An open upside.', fontsize=13 if mobile else 23, weight='bold')
    fig.text(.06, .88, 'Illustrative call: $100 strike · $10 premium', fontsize=10 if mobile else 15, color=MUTED)
    save(fig, 'call-payoff-mobile.svg' if mobile else 'call-payoff.svg')

if __name__ == '__main__':
    market(); market(True); payoff(); payoff(True)
    assert DATA['totals']['call_premium_mid_usd'] == 8045317861.5
    print('Built four desktop/mobile SVG figures from the public aggregate record.')
