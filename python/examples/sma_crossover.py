"""Minimal end-to-end example: SMA crossover on synthetic data.

Run with ``python examples/sma_crossover.py`` from the ``python/`` directory after
``pip install -e .``. Replace ``synthetic_ohlcv`` with ``load_csv("your_file.csv")`` to use
real data.
"""

from quanttools.backtest import crossover_positions, run_backtest
from quanttools.data import synthetic_ohlcv
from quanttools.indicators import sma


def main() -> None:
    prices = synthetic_ohlcv(1000, seed=7)["close"]
    fast, slow = sma(prices, 20), sma(prices, 50)
    positions = crossover_positions(fast, slow)

    result = run_backtest(prices, positions, cost_bps=5, slippage_bps=2)

    print("SMA 20/50 crossover, long only, 7 bps round-trip costs")
    for key, value in result.summary().items():
        print(f"  {key:<22} {value:>10.4f}")


if __name__ == "__main__":
    main()
