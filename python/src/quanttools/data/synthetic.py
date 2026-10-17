"""Synthetic price generators for tests, demos and documentation examples."""

from __future__ import annotations

import numpy as np
import pandas as pd


def geometric_brownian_motion(
    n: int,
    *,
    s0: float = 100.0,
    mu: float = 0.05,
    sigma: float = 0.2,
    dt: float = 1 / 252,
    seed: int | None = None,
) -> np.ndarray:
    """Simulate ``n`` prices of a geometric Brownian motion starting at ``s0``.

    ``mu`` and ``sigma`` are annualised drift and volatility; ``dt`` is the step in years.
    """
    if n <= 0:
        raise ValueError("n must be positive")
    rng = np.random.default_rng(seed)
    shocks = rng.standard_normal(n - 1)
    log_returns = (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * shocks
    path = np.empty(n)
    path[0] = s0
    path[1:] = s0 * np.exp(np.cumsum(log_returns))
    return path


def synthetic_ohlcv(
    n: int = 500,
    *,
    start: str = "2020-01-01",
    freq: str = "B",
    seed: int | None = None,
    **gbm_kwargs,
) -> pd.DataFrame:
    """Build a plausible OHLCV frame around a GBM close path.

    High/low are the close widened by a random intraday range, open is the previous close
    plus a small gap, volume is log-normal. Intended for examples and tests, not research.
    """
    rng = np.random.default_rng(seed)
    close = geometric_brownian_motion(n, seed=seed, **gbm_kwargs)
    if freq == "B":
        index = pd.bdate_range(start, periods=n)
    else:
        index = pd.date_range(start, periods=n, freq=freq)

    prev_close = np.concatenate([[close[0]], close[:-1]])
    open_ = prev_close * (1 + rng.normal(0, 0.002, n))
    spread = np.abs(rng.normal(0, 0.01, n)) * close
    high = np.maximum(open_, close) + spread
    low = np.minimum(open_, close) - spread
    volume = rng.lognormal(mean=12, sigma=0.3, size=n).round()

    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume},
        index=index,
    )
