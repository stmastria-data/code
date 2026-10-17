"""Technical indicators on price series.

Every function takes a :class:`pandas.Series` (or an OHLCV frame where noted) and returns a
new Series/DataFrame aligned to the input index. Warm-up periods are ``NaN``.
"""

from quanttools.indicators.momentum import roc, rsi, stochastic
from quanttools.indicators.trend import ema, macd, sma, wma
from quanttools.indicators.volatility import (
    atr,
    bollinger_bands,
    rolling_volatility,
    true_range,
)

__all__ = [
    "atr",
    "bollinger_bands",
    "ema",
    "macd",
    "roc",
    "rolling_volatility",
    "rsi",
    "sma",
    "stochastic",
    "true_range",
    "wma",
]
