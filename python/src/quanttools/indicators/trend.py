"""Trend-following indicators: moving averages and MACD."""

from __future__ import annotations

import numpy as np
import pandas as pd

from quanttools.indicators._util import check_window


def sma(series: pd.Series, window: int) -> pd.Series:
    """Simple moving average over ``window`` observations."""
    check_window(window)
    return series.rolling(window, min_periods=window).mean().rename(f"sma_{window}")


def ema(series: pd.Series, window: int) -> pd.Series:
    """Exponential moving average with span ``window`` (alpha = 2 / (window + 1)).

    The first ``window - 1`` values are ``NaN`` so the warm-up matches :func:`sma`.
    """
    check_window(window)
    out = series.ewm(span=window, adjust=False, min_periods=window).mean()
    return out.rename(f"ema_{window}")


def wma(series: pd.Series, window: int) -> pd.Series:
    """Linearly weighted moving average: the most recent observation has weight ``window``."""
    check_window(window)
    weights = np.arange(1, window + 1, dtype=float)
    weights /= weights.sum()
    out = series.rolling(window, min_periods=window).apply(
        lambda x: float(np.dot(x, weights)), raw=True
    )
    return out.rename(f"wma_{window}")


def macd(
    series: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> pd.DataFrame:
    """Moving Average Convergence Divergence.

    Returns a frame with columns ``macd`` (fast EMA minus slow EMA), ``signal`` (EMA of the
    MACD line) and ``hist`` (their difference).
    """
    check_window(fast, "fast")
    check_window(slow, "slow")
    check_window(signal, "signal")
    if fast >= slow:
        raise ValueError("fast must be shorter than slow")
    line = ema(series, fast) - ema(series, slow)
    sig = line.ewm(span=signal, adjust=False, min_periods=signal).mean()
    return pd.DataFrame({"macd": line, "signal": sig, "hist": line - sig})
