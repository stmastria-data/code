import pandas as pd
import pytest

from quanttools.data import synthetic_ohlcv


@pytest.fixture
def ohlcv() -> pd.DataFrame:
    return synthetic_ohlcv(300, seed=42)


@pytest.fixture
def close(ohlcv: pd.DataFrame) -> pd.Series:
    return ohlcv["close"]
