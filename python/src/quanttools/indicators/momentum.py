"""Momentum oscillators."""

from __future__ import annotations

import numpy as np
import pandas as pd

from quanttools.indicators._util import check_window


def rsi(series: pd.Series, window: int = 14) -> pd.Series:
    """Relative Strength Index (Wilder smoothing), bounded in ``[0, 100]``.

    A flat series yields 100 when there were only gains, 0 when only losses, and ``NaN``
    when there were neither in the window.
    """
    check_window(window)
    delta = series.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    avg_loss = loss.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    out = 100 - 100 / (1 + rs)
    out = out.where(~((avg_loss == 0) & (avg_gain > 0)), 100.0)
    out = out.where(~((avg_gain == 0) & (avg_loss > 0)), 0.0)
    return out.rename(f"rsi_{window}")


def roc(series: pd.Series, window: int = 10) -> pd.Series:
    """Rate of change: ``series / series.shift(window) - 1``."""
    check_window(window)
    return (series / series.shift(window) - 1).rename(f"roc_{window}")


def stochastic(
    df: pd.DataFrame,
    k_window: int = 14,
    d_window: int = 3,
) -> pd.DataFrame:
    """Stochastic oscillator on an OHLCV frame.

    ``%K`` is where the close sits in the ``k_window`` high/low range (0..100); ``%D`` is its
    ``d_window`` simple moving average.
    """
    check_window(k_window, "k_window")
    check_window(d_window, "d_window")
    lowest = df["low"].rolling(k_window, min_periods=k_window).min()
    highest = df["high"].rolling(k_window, min_periods=k_window).max()
    rng = (highest - lowest).replace(0.0, np.nan)
    k = 100 * (df["close"] - lowest) / rng
    d = k.rolling(d_window, min_periods=d_window).mean()
    return pd.DataFrame({"k": k, "d": d})
