"""Loading and validating OHLCV data frames.

A valid OHLCV frame has a sorted, unique :class:`~pandas.DatetimeIndex` and the lower-case
columns ``open, high, low, close, volume``. Every other function in the package that accepts
a "price frame" expects this layout, so run :func:`validate_ohlcv` once at the boundary.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

OHLCV_COLUMNS: tuple[str, ...] = ("open", "high", "low", "close", "volume")

_AGG = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}


def validate_ohlcv(df: pd.DataFrame, *, require_volume: bool = True) -> pd.DataFrame:
    """Return a cleaned copy of ``df`` or raise ``ValueError`` describing the problem.

    Column names are lower-cased and stripped, the index is converted to a sorted
    ``DatetimeIndex`` with duplicates dropped (last wins), and rows whose high is below
    their low are rejected.
    """
    out = df.copy()
    out.columns = [str(c).strip().lower() for c in out.columns]

    required = set(OHLCV_COLUMNS) if require_volume else set(OHLCV_COLUMNS[:-1])
    missing = required - set(out.columns)
    if missing:
        raise ValueError(f"missing OHLCV columns: {sorted(missing)}")

    if not isinstance(out.index, pd.DatetimeIndex):
        try:
            out.index = pd.to_datetime(out.index)
        except (TypeError, ValueError) as exc:
            raise ValueError("index must be convertible to DatetimeIndex") from exc

    out = out[~out.index.duplicated(keep="last")].sort_index()

    for col in required:
        out[col] = pd.to_numeric(out[col], errors="coerce")

    bad = out["high"] < out["low"]
    if bad.any():
        raise ValueError(f"{int(bad.sum())} rows have high < low (first at {out.index[bad][0]})")

    return out


def load_csv(
    path: str | Path,
    *,
    date_column: str = "date",
    require_volume: bool = True,
    **read_csv_kwargs,
) -> pd.DataFrame:
    """Load an OHLCV CSV and validate it.

    ``date_column`` is used as the index. Extra keyword arguments are forwarded to
    :func:`pandas.read_csv` (useful for ``sep``, ``decimal`` or ``thousands``).
    """
    raw = pd.read_csv(path, **read_csv_kwargs)
    raw.columns = [str(c).strip().lower() for c in raw.columns]
    key = date_column.strip().lower()
    if key not in raw.columns:
        raise ValueError(f"date column {date_column!r} not found in {list(raw.columns)}")
    raw = raw.set_index(key)
    return validate_ohlcv(raw, require_volume=require_volume)


def resample_ohlcv(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    """Resample an OHLCV frame to a coarser frequency (e.g. ``"1W"``, ``"1h"``).

    Open takes the first value, high the max, low the min, close the last and volume the sum.
    Empty buckets are dropped.
    """
    cols = [c for c in OHLCV_COLUMNS if c in df.columns]
    agg = {c: _AGG[c] for c in cols}
    out = df[cols].resample(rule).agg(agg)
    return out.dropna(subset=["close"])
