import numpy as np
import pandas as pd
import pytest

from quanttools.indicators import (
    atr,
    bollinger_bands,
    ema,
    macd,
    roc,
    rolling_volatility,
    rsi,
    sma,
    stochastic,
    true_range,
    wma,
)


def test_sma_matches_manual(close):
    out = sma(close, 5)
    assert out.iloc[:4].isna().all()
    assert out.iloc[4] == pytest.approx(close.iloc[:5].mean())
    assert out.name == "sma_5"


def test_ema_warmup_and_convergence():
    s = pd.Series(np.ones(50) * 7.0)
    out = ema(s, 10)
    assert out.iloc[:9].isna().all()
    assert out.iloc[-1] == pytest.approx(7.0)


def test_wma_weights_recent_more():
    s = pd.Series([1.0, 2.0, 3.0])
    assert wma(s, 3).iloc[-1] == pytest.approx((1 * 1 + 2 * 2 + 3 * 3) / 6)


def test_macd_columns_and_order(close):
    out = macd(close)
    assert list(out.columns) == ["macd", "signal", "hist"]
    valid = out.dropna()
    assert np.allclose(valid["hist"], valid["macd"] - valid["signal"])
    with pytest.raises(ValueError):
        macd(close, fast=26, slow=12)


def test_rsi_bounds_and_extremes(close):
    out = rsi(close, 14)
    valid = out.dropna()
    assert ((valid >= 0) & (valid <= 100)).all()
    rising = pd.Series(np.arange(1.0, 40.0))
    assert rsi(rising, 14).iloc[-1] == pytest.approx(100.0)
    falling = pd.Series(np.arange(40.0, 1.0, -1))
    assert rsi(falling, 14).iloc[-1] == pytest.approx(0.0)


def test_roc(close):
    out = roc(close, 3)
    assert out.iloc[3] == pytest.approx(close.iloc[3] / close.iloc[0] - 1)


def test_stochastic_in_range(ohlcv):
    out = stochastic(ohlcv)
    valid = out.dropna()
    assert ((valid["k"] >= 0) & (valid["k"] <= 100)).all()
    assert ((valid["d"] >= 0) & (valid["d"] <= 100)).all()


def test_true_range_and_atr(ohlcv):
    tr = true_range(ohlcv)
    assert tr.iloc[0] == pytest.approx(ohlcv["high"].iloc[0] - ohlcv["low"].iloc[0])
    assert (tr.dropna() >= 0).all()
    a = atr(ohlcv, 14)
    assert a.iloc[:13].isna().all()
    assert (a.dropna() > 0).all()


def test_bollinger_geometry(close):
    bb = bollinger_bands(close, 20, 2.0)
    valid = bb.dropna()
    assert (valid["upper"] >= valid["middle"]).all()
    assert (valid["lower"] <= valid["middle"]).all()
    assert np.allclose(valid["bandwidth"], (valid["upper"] - valid["lower"]) / valid["middle"])


def test_rolling_volatility_scales(close):
    r = close.pct_change()
    daily = rolling_volatility(r, 21, periods_per_year=1)
    annual = rolling_volatility(r, 21, periods_per_year=252)
    assert np.allclose(annual.dropna(), daily.dropna() * np.sqrt(252))


@pytest.mark.parametrize("bad", [0, -1, 2.5, True])
def test_window_validation(close, bad):
    with pytest.raises(ValueError):
        sma(close, bad)
