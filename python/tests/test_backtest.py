import numpy as np
import pandas as pd
import pytest

from quanttools.backtest import crossover_positions, run_backtest, threshold_positions
from quanttools.indicators import sma


def test_crossover_positions_long_only_and_short():
    fast = pd.Series([1.0, 3.0, 2.0, np.nan])
    slow = pd.Series([2.0, 2.0, 2.5, 2.0])
    assert crossover_positions(fast, slow).tolist() == [0.0, 1.0, 0.0, 0.0]
    assert crossover_positions(fast, slow, allow_short=True).tolist() == [-1.0, 1.0, -1.0, 0.0]


def test_threshold_positions_with_exit():
    ind = pd.Series([50, 25, 40, 55, 75, 60, 45, np.nan], dtype=float)
    pos = threshold_positions(ind, long_below=30, short_above=70, exit_at=50)
    assert pos.tolist() == [0, 1, 1, 0, -1, -1, 0, 0]


def test_backtest_buy_and_hold_matches_price_ratio(close):
    pos = pd.Series(1.0, index=close.index)
    res = run_backtest(close, pos, lag=0)
    assert res.equity.iloc[-1] == pytest.approx(close.iloc[-1] / close.iloc[0])
    assert res.costs.sum() == 0


def test_backtest_lag_avoids_lookahead(close):
    pos = pd.Series(1.0, index=close.index)
    res = run_backtest(close, pos, lag=1)
    # First bar is flat because the signal is only known at its close.
    assert res.positions.iloc[0] == 0.0
    assert res.returns.iloc[0] == 0.0
    assert res.positions.iloc[1] == 1.0


def test_backtest_costs_reduce_returns(close):
    fast, slow = sma(close, 5), sma(close, 20)
    pos = crossover_positions(fast, slow)
    free = run_backtest(close, pos)
    paid = run_backtest(close, pos, cost_bps=10, slippage_bps=5)
    assert paid.equity.iloc[-1] < free.equity.iloc[-1]
    assert paid.costs.sum() == pytest.approx(paid.turnover.sum() * 15 / 10_000)
    assert paid.turnover.sum() > 0


def test_backtest_rejects_bad_params(close):
    pos = pd.Series(1.0, index=close.index)
    with pytest.raises(ValueError):
        run_backtest(close, pos, lag=-1)
    with pytest.raises(ValueError):
        run_backtest(close, pos, cost_bps=-1)


def test_summary_keys(close):
    pos = pd.Series(1.0, index=close.index)
    summary = run_backtest(close, pos).summary()
    assert {"sharpe_ratio", "max_drawdown", "annualized_return"} <= summary.keys()
