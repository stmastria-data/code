import numpy as np
import pandas as pd
import pytest

from quanttools.portfolio import (
    equal_weights,
    inverse_volatility_weights,
    portfolio_returns,
    risk_parity_weights,
)


@pytest.fixture
def returns():
    rng = np.random.default_rng(3)
    idx = pd.bdate_range("2022-01-03", periods=500)
    data = {
        "low_vol": rng.normal(0.0002, 0.005, 500),
        "mid_vol": rng.normal(0.0003, 0.010, 500),
        "high_vol": rng.normal(0.0005, 0.020, 500),
    }
    return pd.DataFrame(data, index=idx)


def test_equal_weights(returns):
    w = equal_weights(returns)
    assert w.sum() == pytest.approx(1.0)
    assert np.allclose(w, 1 / 3)


def test_inverse_vol_orders_by_volatility(returns):
    w = inverse_volatility_weights(returns)
    assert w.sum() == pytest.approx(1.0)
    assert w["low_vol"] > w["mid_vol"] > w["high_vol"]


def test_risk_parity_equalises_risk_contributions(returns):
    w = risk_parity_weights(returns)
    cov = returns.cov().to_numpy()
    contrib = w.to_numpy() * (cov @ w.to_numpy())
    assert w.sum() == pytest.approx(1.0)
    assert (w > 0).all()
    assert np.allclose(contrib, contrib.mean(), rtol=1e-4)


def test_portfolio_returns_constant_mix(returns):
    w = equal_weights(returns)
    pr = portfolio_returns(returns, w)
    pd.testing.assert_series_equal(pr, returns.mean(axis=1).rename("portfolio"))


def test_portfolio_returns_monthly_rebalance_drifts(returns):
    w = equal_weights(returns)
    monthly = portfolio_returns(returns, w, rebalance="M")
    daily = portfolio_returns(returns, w)
    assert len(monthly) == len(returns)
    assert not monthly.isna().any()
    # First bar of each month equals the constant-mix return; later bars drift.
    first_bar = returns.index[0]
    assert monthly[first_bar] == pytest.approx(daily[first_bar])
    assert not np.allclose(monthly, daily)
