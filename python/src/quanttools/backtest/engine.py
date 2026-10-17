"""A small, transparent vectorised backtest engine.

The engine deliberately stays simple: one instrument, fractional positions, proportional
costs on turnover, no margin or borrow modelling. It is meant as a reference implementation
whose numbers you can check by hand, not as a replacement for an event-driven simulator.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class BacktestResult:
    """Output of :func:`run_backtest`.

    Attributes
    ----------
    returns:
        Net strategy return per bar, after costs.
    gross_returns:
        Strategy return per bar before costs.
    positions:
        The exposure actually held during each bar (i.e. the input shifted by one).
    turnover:
        Absolute change in exposure at each bar.
    costs:
        Cost charged at each bar, as a fraction of equity.
    equity:
        Cumulative equity curve starting at ``initial_capital``.
    """

    returns: pd.Series
    gross_returns: pd.Series
    positions: pd.Series
    turnover: pd.Series
    costs: pd.Series
    equity: pd.Series

    def summary(self, periods_per_year: int = 252) -> dict[str, float]:
        """Convenience wrapper around :func:`quanttools.risk.performance_summary`."""
        from quanttools.risk import performance_summary

        return performance_summary(self.returns, periods_per_year=periods_per_year)


def run_backtest(
    prices: pd.Series,
    positions: pd.Series,
    *,
    cost_bps: float = 0.0,
    slippage_bps: float = 0.0,
    initial_capital: float = 1.0,
    lag: int = 1,
) -> BacktestResult:
    """Simulate holding ``positions`` in an instrument quoted at ``prices``.

    Parameters
    ----------
    prices:
        Close prices.
    positions:
        Target exposure decided at each bar's close (see :mod:`quanttools.backtest.signals`).
    cost_bps, slippage_bps:
        Proportional costs in basis points, charged on each unit of turnover.
    initial_capital:
        Starting equity.
    lag:
        Bars between deciding a position and holding it. ``1`` (default) means a signal on
        today's close is held from tomorrow, which removes look-ahead bias.
    """
    if lag < 0:
        raise ValueError("lag must be >= 0")
    if cost_bps < 0 or slippage_bps < 0:
        raise ValueError("costs must be non-negative")

    prices = prices.astype(float)
    positions = positions.reindex(prices.index).astype(float).fillna(0.0)

    held = positions.shift(lag).fillna(0.0)
    asset_returns = prices.pct_change().fillna(0.0)

    gross = held * asset_returns
    turnover = held.diff().abs().fillna(held.abs())
    costs = turnover * (cost_bps + slippage_bps) / 10_000
    net = gross - costs
    equity = initial_capital * (1 + net).cumprod()

    return BacktestResult(
        returns=net.rename("returns"),
        gross_returns=gross.rename("gross_returns"),
        positions=held.rename("position"),
        turnover=turnover.rename("turnover"),
        costs=costs.rename("costs"),
        equity=equity.rename("equity"),
    )


__all__ = ["BacktestResult", "run_backtest"]
