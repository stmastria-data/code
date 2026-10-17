"""Risk and performance metrics.

All functions take a series of simple periodic returns (``0.01`` = +1%) and return floats.
``periods_per_year`` defaults to 252 (daily bars); use 52 for weekly, 12 for monthly,
or ``24 * 365`` style values for intraday crypto data.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _clean(returns: pd.Series) -> pd.Series:
    r = pd.Series(returns, dtype=float).dropna()
    if r.empty:
        raise ValueError("returns series is empty after dropping NaN")
    return r


def annualized_return(returns: pd.Series, periods_per_year: int = 252) -> float:
    """Compound annual growth rate of the return series."""
    r = _clean(returns)
    total = float((1 + r).prod())
    if total <= 0:
        return -1.0
    years = len(r) / periods_per_year
    return total ** (1 / years) - 1


def annualized_volatility(returns: pd.Series, periods_per_year: int = 252) -> float:
    """Sample standard deviation scaled by the square root of time."""
    r = _clean(returns)
    if len(r) < 2:
        return float("nan")
    return float(r.std(ddof=1) * np.sqrt(periods_per_year))


def sharpe_ratio(returns: pd.Series, risk_free: float = 0.0, periods_per_year: int = 252) -> float:
    """Annualised Sharpe ratio. ``risk_free`` is an annual rate."""
    r = _clean(returns) - risk_free / periods_per_year
    sd = r.std(ddof=1)
    if len(r) < 2 or sd == 0 or np.isnan(sd):
        return float("nan")
    return float(r.mean() / sd * np.sqrt(periods_per_year))


def sortino_ratio(returns: pd.Series, risk_free: float = 0.0, periods_per_year: int = 252) -> float:
    """Annualised Sortino ratio: excess return over downside deviation."""
    r = _clean(returns) - risk_free / periods_per_year
    downside = np.sqrt(np.mean(np.minimum(r, 0.0) ** 2))
    if downside == 0:
        return float("nan")
    return float(r.mean() / downside * np.sqrt(periods_per_year))


def drawdown_series(returns: pd.Series) -> pd.Series:
    """Drawdown at each bar as a non-positive fraction of the running peak equity."""
    r = _clean(returns)
    equity = (1 + r).cumprod()
    peak = equity.cummax()
    return (equity / peak - 1).rename("drawdown")


def max_drawdown(returns: pd.Series) -> float:
    """Largest peak-to-trough loss, as a non-positive fraction (``-0.25`` = -25%)."""
    return float(drawdown_series(returns).min())


def calmar_ratio(returns: pd.Series, periods_per_year: int = 252) -> float:
    """Annualised return divided by the absolute maximum drawdown."""
    mdd = max_drawdown(returns)
    if mdd == 0:
        return float("nan")
    return annualized_return(returns, periods_per_year) / abs(mdd)


def var(returns: pd.Series, level: float = 0.95) -> float:
    """Historical Value at Risk: the loss not exceeded with probability ``level``.

    Returned as a positive number (``0.02`` means a 2% loss).
    """
    if not 0 < level < 1:
        raise ValueError("level must be in (0, 1)")
    r = _clean(returns)
    return float(-np.quantile(r, 1 - level))


def cvar(returns: pd.Series, level: float = 0.95) -> float:
    """Conditional VaR / expected shortfall: mean loss in the worst ``1 - level`` tail."""
    r = _clean(returns)
    cutoff = -var(r, level)
    tail = r[r <= cutoff]
    if tail.empty:
        return float("nan")
    return float(-tail.mean())


def performance_summary(returns: pd.Series, periods_per_year: int = 252) -> dict[str, float]:
    """Common metrics in one dictionary, handy for tables and quick comparisons."""
    r = _clean(returns)
    return {
        "total_return": float((1 + r).prod() - 1),
        "annualized_return": annualized_return(r, periods_per_year),
        "annualized_volatility": annualized_volatility(r, periods_per_year),
        "sharpe_ratio": sharpe_ratio(r, periods_per_year=periods_per_year),
        "sortino_ratio": sortino_ratio(r, periods_per_year=periods_per_year),
        "max_drawdown": max_drawdown(r),
        "calmar_ratio": calmar_ratio(r, periods_per_year),
        "var_95": var(r, 0.95),
        "cvar_95": cvar(r, 0.95),
        "periods": float(len(r)),
    }
