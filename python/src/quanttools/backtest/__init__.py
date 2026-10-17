"""Vectorised backtesting: signals -> positions -> returns."""

from quanttools.backtest.engine import BacktestResult, run_backtest
from quanttools.backtest.signals import crossover_positions, threshold_positions

__all__ = ["BacktestResult", "crossover_positions", "run_backtest", "threshold_positions"]
