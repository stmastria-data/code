"""Volatility indicators."""

from __future__ import annotations

import numpy as np
import pandas as pd

from quanttools.indicators._util import check_window


def true_range(df: pd.DataFrame) -> pd.Series:
    """True range: max(high - low, |high - prev close|, |low - prev close|)."""
    prev_close = df["close"].shift(1)
    ranges = pd.concat(
        [df["high"] - df["low"], (df["high"] - prev_close).abs(), (df["low"] - prev_close).abs()],
        axis=1,
    )
    # The first bar has no previous close, so its true range is simply high - low.
    return ranges.max(axis=1).rename("true_range")


def atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Average True Range using Wilder's smoothing."""
    check_window(window)
    tr = true_range(df)
    out = tr.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    return out.rename(f"atr_{window}")


def bollinger_bands(series: pd.Series, window: int = 20, num_std: float = 2.0) -> pd.DataFrame:
    """Bollinger Bands: rolling mean plus/minus ``num_std`` rolling standard deviations.

    Returns a frame with ``middle``, ``upper``, ``lower`` and ``bandwidth``
    ((upper - lower) / middle).
    """
    check_window(window)
    if num_std <= 0:
        raise ValueError("num_std must be positive")
    middle = series.rolling(window, min_periods=window).mean()
    std = series.rolling(window, min_periods=window).std(ddof=0)
    upper = middle + num_std * std
    lower = middle - num_std * std
    return pd.DataFrame(
        {"middle": middle, "upper": upper, "lower": lower, "bandwidth": (upper - lower) / middle}
    )


def rolling_volatility(
    returns: pd.Series,
    window: int = 21,
    periods_per_year: int = 252,
) -> pd.Series:
    """Annualised rolling standard deviation of a return series."""
    check_window(window)
    out = returns.rolling(window, min_periods=window).std(ddof=1) * np.sqrt(periods_per_year)
    return out.rename(f"vol_{window}")
