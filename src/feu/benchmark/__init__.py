r"""Contain functions to follow the trend of the benchmarks.

``load_runs`` reads the results saved by ``pytest-benchmark`` as ``Run``
values, ``find_regressions`` compares the latest run of each machine
with the median of its previous runs, ``make_report`` renders a Markdown
report with GitHub Actions annotations, and ``prune_runs`` deletes the
old results. This package only uses the standard library. The ``feu
benchmark-trend`` command is built on these functions.
"""

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
