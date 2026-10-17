"""Static weighting schemes for a set of assets.

Each ``*_weights`` function takes a DataFrame of asset returns (one column per asset) and
returns a Series of long-only weights summing to one, indexed by asset.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def equal_weights(returns: pd.DataFrame) -> pd.Series:
    """1/N across the columns of ``returns``."""
    n = returns.shape[1]
    if n == 0:
        raise ValueError("no assets")
    return pd.Series(1.0 / n, index=returns.columns, name="weight")


def inverse_volatility_weights(returns: pd.DataFrame) -> pd.Series:
    """Weights proportional to 1 / volatility of each asset."""
    vol = returns.std(ddof=1)
    if (vol <= 0).any() or vol.isna().any():
        raise ValueError("every asset needs positive, finite volatility")
    w = 1.0 / vol
    return (w / w.sum()).rename("weight")


def risk_parity_weights(
    returns: pd.DataFrame,
    *,
    max_iter: int = 1000,
    tol: float = 1e-10,
) -> pd.Series:
    """Equal risk contribution weights via fixed-point iteration on the covariance matrix.

    Each asset ends up contributing the same share of total portfolio variance. Falls back
    to :func:`inverse_volatility_weights` as the starting point.
    """
    cov = returns.cov(ddof=1).to_numpy()
    n = cov.shape[0]
    if n == 0:
        raise ValueError("no assets")
    w = inverse_volatility_weights(returns).to_numpy()
    for _ in range(max_iter):
        port_var = w @ cov @ w
        marginal = cov @ w
        risk_contrib = w * marginal
        target = port_var / n
        new_w = w * np.sqrt(target / np.maximum(risk_contrib, 1e-18))
        new_w /= new_w.sum()
        if np.max(np.abs(new_w - w)) < tol:
            w = new_w
            break
        w = new_w
    return pd.Series(w, index=returns.columns, name="weight")


def portfolio_returns(
    returns: pd.DataFrame,
    weights: pd.Series,
    *,
    rebalance: str | None = None,
) -> pd.Series:
    """Portfolio return series from asset returns and target weights.

    With ``rebalance=None`` the weights are re-applied every bar (constant mix). Pass a pandas
    period alias such as ``"M"`` (monthly), ``"W"`` or ``"Q"`` to rebalance only at the start of
    each period and let weights drift in between.
    """
    weights = weights.reindex(returns.columns).fillna(0.0)
    if rebalance is None:
        return (returns * weights).sum(axis=1).rename("portfolio")

    out = pd.Series(index=returns.index, dtype=float, name="portfolio")
    period = returns.index.to_period(rebalance)
    for _, chunk in returns.groupby(period):
        growth = (1 + chunk).cumprod()
        values = growth * weights
        equity = values.sum(axis=1)
        prev = equity.shift(1).fillna(1.0)
        out.loc[chunk.index] = equity / prev - 1
    return out
