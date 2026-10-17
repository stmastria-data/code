# Pine Script

Indicators, strategies and libraries for [TradingView](https://www.tradingview.com), written in
**Pine Script v6**.

| Folder | Contents |
| --- | --- |
| `indicators/` | Scripts declared with `indicator()`: studies, oscillators, overlays |
| `strategies/` | Scripts declared with `strategy()`: backtestable rules with orders |
| `libraries/`  | Scripts declared with `library()`: reusable exported functions |
| `templates/`  | Starting points with the standard header and section layout |

## Scripts

| File | Type | What it does |
| --- | --- | --- |
| `indicators/nlt_rsi_bands.pine` | Indicator | RSI with overbought/oversold bands that adapt to recent RSI behaviour |
| `indicators/nlt_volatility_regime.pine` | Indicator | Annualised realised volatility and its percentile rank as low/normal/high regime |
| `strategies/nlt_sma_crossover.pine` | Strategy | Fast/slow SMA crossover with ATR stop; same rules as the Python example |
| `libraries/nlt_risk.pine` | Library | Position sizing, ATR stops, reward/risk, drawdown helpers |

## How to use a script

1. Open TradingView, then **Pine Editor** at the bottom of the chart.
2. Create a new script, delete the default code, paste the file contents.
3. Click **Save**, then **Add to chart**.

To use the library from another script, publish it from your TradingView account first, then
import it with `import <your_username>/NLTRisk/1 as risk`.

## Conventions

- **File names** are `snake_case`, prefixed with `nlt_`, extension `.pine`.
- **Header**: every file starts with the licence block, name, version, description and notes.
  Copy a file from `templates/` to start.
- **Titles** in `indicator()` / `strategy()` start with `NLT · ` so they are easy to find in
  TradingView.
- **Sections** in order: Inputs, Calculation/Signals, Orders, Plots, Alerts.
- **Inputs** are grouped with `group =` and have sensible `minval` limits.
- **No repainting**: avoid `request.security` with `lookahead_on` and future bar references.
  If a script does repaint, say so in the header notes.
- **Strategies** declare realistic `commission_value` and `slippage` defaults.
- **Version**: bump the header version when behaviour changes, and note it in the commit.

## Disclaimer

Educational material, not financial advice. Past backtest results do not guarantee future
performance.
