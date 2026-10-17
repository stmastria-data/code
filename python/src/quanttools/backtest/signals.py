"""Helpers that turn indicator series into position series.

A *position* series holds the target exposure at each bar: ``1`` long, ``-1`` short, ``0``
flat, or any fraction in between. Positions are decided on the bar's close and, in
:func:`~quanttools.backtest.run_backtest`, applied from the next bar, so there is no
look-ahead.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def crossover_positions(
    fast: pd.Series, slow: pd.Series, *, allow_short: bool = False
) -> pd.Series:
    """Long when ``fast`` is above ``slow``; flat (or short) otherwise.

    Bars where either input is ``NaN`` are flat.
    """
    diff = (fast - slow).astype(float)
    pos = np.sign(diff)
    if not allow_short:
        pos = pos.clip(lower=0.0)
    pos = pos.where(diff.notna(), 0.0)
    return pos.rename("position")


def threshold_positions(
    indicator: pd.Series,
    *,
    long_below: float | None = None,
    short_above: float | None = None,
    exit_at: float | None = None,
) -> pd.Series:
    """Mean-reversion style positions from an oscillator.

    Enter long when the indicator falls below ``long_below``, short when it rises above
    ``short_above``. If ``exit_at`` is given, close the position when the indicator crosses
    back through it; otherwise positions flip only on the opposite signal.
    """
    if long_below is None and short_above is None:
        raise ValueError("at least one of long_below / short_above is required")

    values = indicator.to_numpy(dtype=float)
    out = np.zeros(len(values))
    state = 0.0
    for i, v in enumerate(values):
        if np.isnan(v):
            out[i] = state
            continue
        if long_below is not None and v < long_below:
            state = 1.0
        elif short_above is not None and v > short_above:
            state = -1.0
        elif exit_at is not None and ((state > 0 and v >= exit_at) or (state < 0 and v <= exit_at)):
            state = 0.0
        out[i] = state
    return pd.Series(out, index=indicator.index, name="position")
