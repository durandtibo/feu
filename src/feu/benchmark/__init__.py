r"""Contain functions to follow the trend of the benchmarks."""

from __future__ import annotations

__all__ = [
    "KINDS",
    "LABELS",
    "STATS",
    "UNITS",
    "Regression",
    "Run",
    "TrendReport",
    "find_regressions",
    "load_runs",
    "make_report",
    "prune_runs",
]

from feu.benchmark.report import UNITS, TrendReport, make_report
from feu.benchmark.runs import KINDS, LABELS, STATS, Run, load_runs, prune_runs
from feu.benchmark.trend import Regression, find_regressions
