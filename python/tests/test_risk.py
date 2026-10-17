import numpy as np
import pandas as pd
import pytest

from quanttools.risk import (
    annualized_return,
    annualized_volatility,
    calmar_ratio,
    cvar,
    drawdown_series,
    max_drawdown,
    performance_summary,
    sharpe_ratio,
    sortino_ratio,
    var,
)


def test_constant_return_metrics():
    r = pd.Series([0.01] * 252)
    assert annualized_return(r) == pytest.approx(1.01**252 - 1)
    assert annualized_volatility(r) == 0.0
    assert np.isnan(sharpe_ratio(r))
    assert np.isnan(sortino_ratio(r))
    assert max_drawdown(r) == 0.0


def test_drawdown_known_path():
    r = pd.Series([0.10, -0.50, 0.20])
    dd = drawdown_series(r)
    assert dd.iloc[0] == 0.0
    assert dd.iloc[1] == pytest.approx(-0.5)
    assert dd.iloc[2] == pytest.approx(1.1 * 0.5 * 1.2 / 1.1 - 1)
    assert max_drawdown(r) == pytest.approx(-0.5)


def test_sharpe_scales_with_sqrt_time():
    rng = np.random.default_rng(0)
    r = pd.Series(rng.normal(0.001, 0.01, 1000))
    assert sharpe_ratio(r, periods_per_year=252) == pytest.approx(
        sharpe_ratio(r, periods_per_year=1) * np.sqrt(252)
    )


def test_var_and_cvar_ordering():
    rng = np.random.default_rng(1)
    r = pd.Series(rng.normal(0, 0.02, 5000))
    v = var(r, 0.95)
    c = cvar(r, 0.95)
    assert v > 0
    assert c >= v
    assert v == pytest.approx(0.02 * 1.645, rel=0.1)
    with pytest.raises(ValueError):
        var(r, 1.5)


def test_calmar_and_summary():
    rng = np.random.default_rng(2)
    r = pd.Series(rng.normal(0.0005, 0.01, 756))
    summary = performance_summary(r)
    assert summary["calmar_ratio"] == pytest.approx(calmar_ratio(r))
    assert summary["periods"] == 756
    assert summary["max_drawdown"] <= 0


def test_empty_series_rejected():
    with pytest.raises(ValueError):
        annualized_return(pd.Series([np.nan, np.nan]))
