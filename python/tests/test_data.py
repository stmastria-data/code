import numpy as np
import pandas as pd
import pytest

from quanttools.data import (
    geometric_brownian_motion,
    load_csv,
    resample_ohlcv,
    validate_ohlcv,
)


def test_gbm_is_reproducible_and_starts_at_s0():
    a = geometric_brownian_motion(50, s0=10.0, seed=1)
    b = geometric_brownian_motion(50, s0=10.0, seed=1)
    assert a[0] == 10.0
    assert np.array_equal(a, b)
    assert (a > 0).all()


def test_synthetic_ohlcv_is_consistent(ohlcv):
    assert list(ohlcv.columns) == ["open", "high", "low", "close", "volume"]
    assert (ohlcv["high"] >= ohlcv[["open", "close"]].max(axis=1)).all()
    assert (ohlcv["low"] <= ohlcv[["open", "close"]].min(axis=1)).all()
    assert ohlcv.index.is_monotonic_increasing


def test_validate_normalises_columns_and_index():
    raw = pd.DataFrame(
        {"Open": [1, 2], "High": [2, 3], "Low": [0.5, 1], "Close": [1.5, 2.5], "Volume": [10, 20]},
        index=["2024-01-02", "2024-01-01"],
    )
    out = validate_ohlcv(raw)
    assert list(out.columns) == ["open", "high", "low", "close", "volume"]
    assert isinstance(out.index, pd.DatetimeIndex)
    assert out.index[0] < out.index[1]


def test_validate_rejects_bad_rows():
    raw = pd.DataFrame(
        {"open": [1], "high": [1], "low": [2], "close": [1], "volume": [1]},
        index=pd.to_datetime(["2024-01-01"]),
    )
    with pytest.raises(ValueError, match="high < low"):
        validate_ohlcv(raw)
    with pytest.raises(ValueError, match="missing"):
        validate_ohlcv(raw.drop(columns="volume"))


def test_load_csv_roundtrip(tmp_path, ohlcv):
    path = tmp_path / "prices.csv"
    ohlcv.rename_axis("Date").to_csv(path)
    loaded = load_csv(path).rename_axis(None)
    pd.testing.assert_frame_equal(loaded, ohlcv, check_freq=False)


def test_resample_weekly(ohlcv):
    weekly = resample_ohlcv(ohlcv, "W")
    assert len(weekly) < len(ohlcv)
    first_week = ohlcv.loc[: weekly.index[0]]
    assert weekly["open"].iloc[0] == first_week["open"].iloc[0]
    assert weekly["high"].iloc[0] == first_week["high"].max()
    assert weekly["volume"].iloc[0] == first_week["volume"].sum()
