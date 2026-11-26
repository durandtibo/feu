r"""Contain functions to follow the trend of the benchmarks."""

from __future__ import annotations

__all__ = [
    "BENCHMARK_KIND",
    "IMPORT_KIND",
    "KINDS",
    "STATS",
    "TREND_KINDS",
    "UNITS",
    "Regression",
    "Run",
    "TrendKind",
    "build_trend_report",
    "find_regressions",
    "load_runs",
    "make_annotations",
    "make_regression_report",
    "make_table",
    "prune_runs",
    "sparkline",
    "with_unit",
]

from feu.benchmark.runs import KINDS, STATS, Run, load_runs, prune_runs
from feu.benchmark.trend import (
    BENCHMARK_KIND,
    IMPORT_KIND,
    TREND_KINDS,
    UNITS,
    Regression,
    TrendKind,
    build_trend_report,
    find_regressions,
    make_annotations,
    make_regression_report,
    make_table,
    sparkline,
    with_unit,
)
