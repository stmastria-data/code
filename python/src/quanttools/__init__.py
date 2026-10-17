"""quanttools: open-source quantitative tools for market data, indicators, backtesting and risk.

The package is organised in small, independent modules:

- :mod:`quanttools.data`       load, validate and generate OHLCV data
- :mod:`quanttools.indicators` trend, momentum and volatility indicators
- :mod:`quanttools.backtest`   turn signals into positions and positions into returns
- :mod:`quanttools.risk`       performance and risk metrics on return series
- :mod:`quanttools.portfolio`  simple weighting schemes across assets

All functions operate on :class:`pandas.Series` / :class:`pandas.DataFrame` and never
mutate their inputs.
"""

from quanttools import backtest, data, indicators, portfolio, risk

__all__ = ["backtest", "data", "indicators", "portfolio", "risk"]
__version__ = "0.1.0"
