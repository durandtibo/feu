r"""Contain functions to follow the trend of the benchmarks."""

from __future__ import annotations

__all__ = [
    "BENCHMARK_KIND",
    "IMPORT_KIND",
    "KINDS",
    "TrendKind",
    "UnknownStatError",
    "build_trend_report",
    "find_regressions",
    "get_benchmark_label",
    "get_import_label",
    "load_runs",
    "make_annotations",
    "make_regression_report",
    "make_table",
    "sparkline",
]

from feu.benchmark.trend import (
    BENCHMARK_KIND,
    IMPORT_KIND,
    KINDS,
    TrendKind,
    UnknownStatError,
    build_trend_report,
    find_regressions,
    get_benchmark_label,
    get_import_label,
    load_runs,
    make_annotations,
    make_regression_report,
    make_table,
    sparkline,
)
