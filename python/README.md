# quanttools

Small, well-tested Python building blocks for quantitative trading research.

| Module | What it provides |
| --- | --- |
| `quanttools.data` | `load_csv`, `validate_ohlcv`, `resample_ohlcv`, synthetic GBM prices for tests |
| `quanttools.indicators` | `sma`, `ema`, `wma`, `macd`, `rsi`, `roc`, `stochastic`, `true_range`, `atr`, `bollinger_bands`, `rolling_volatility` |
| `quanttools.backtest` | `crossover_positions`, `threshold_positions`, `run_backtest` with costs, slippage and no look-ahead |
| `quanttools.risk` | Sharpe, Sortino, Calmar, max drawdown, VaR, CVaR, `performance_summary` |
| `quanttools.portfolio` | Equal weight, inverse volatility, risk parity, portfolio returns with periodic rebalancing |

All functions take pandas Series/DataFrames, return new objects aligned to the input index,
and never modify their inputs.

## Install

```bash
pip install -e ".[dev]"
```

## Example

```python
from quanttools.backtest import crossover_positions, run_backtest
from quanttools.data import load_csv
from quanttools.indicators import sma

prices = load_csv("prices.csv")["close"]  # columns: date, open, high, low, close, volume
positions = crossover_positions(sma(prices, 20), sma(prices, 50))
result = run_backtest(prices, positions, cost_bps=5, slippage_bps=2)
print(result.summary())
```

A runnable version using synthetic data is in `examples/sma_crossover.py`.

## Development

```bash
ruff check . && ruff format --check .
pytest
```

CI runs the same checks on Python 3.10 to 3.13 for every push and pull request that touches
this folder.
