r"""Contain functions to show the trend of the pytest-benchmark results.

The results are the JSON files saved by ``pytest-benchmark`` (for
example by a scheduled workflow). The functions load the runs of the
last days, detect the benchmarks that are slower than their recent
median, and make a Markdown table.
"""

from __future__ import annotations

__all__ = [
    "BENCHMARK_KIND",
    "IMPORT_KIND",
    "TREND_KINDS",
    "UNITS",
    "TrendKind",
    "build_trend_report",
    "find_regressions",
    "make_annotations",
    "make_regression_report",
    "make_table",
    "sparkline",
    "with_unit",
]

import statistics
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from feu.benchmark.runs import Run, load_runs, prune_runs

if TYPE_CHECKING:
    from pathlib import Path

SPARKS = "▁▂▃▄▅▆▇█"
DEFAULT_STAT = "median"

Regression = tuple[str, float, float, float]


@dataclass(frozen=True)
class TrendKind:
    r"""Define how to read and show a kind of benchmark results.

    Args:
        name: The name of the kind, used on the command line.
        unit: The unit of the times shown in the reports.
        scale: The conversion from seconds to ``unit``.
        column: The title of the first column of the table.
        heading: The subject of the title of the report.

    Example:
        ```pycon
        >>> from feu.benchmark import BENCHMARK_KIND
        >>> BENCHMARK_KIND.unit
        'µs'

        ```
    """

    name: str
    unit: str
    scale: float
    column: str
    heading: str


BENCHMARK_KIND = TrendKind(
    name="benchmark",
    unit="µs",
    scale=1e6,
    column="Benchmark",
    heading="Benchmarks",
)
IMPORT_KIND = TrendKind(
    name="import",
    unit="ms",
    scale=1e3,
    column="Import",
    heading="Import time",
)
TREND_KINDS: dict[str, TrendKind] = {kind.name: kind for kind in (BENCHMARK_KIND, IMPORT_KIND)}
# The conversion from seconds to each time unit.
UNITS: dict[str, float] = {"s": 1.0, "ms": 1e3, "us": 1e6, "µs": 1e6, "ns": 1e9}


def with_unit(kind: TrendKind, unit: str, *, scale: float | None = None) -> TrendKind:
    r"""Change the unit of the times shown in the reports of a kind.

    Args:
        kind: The kind of benchmark results.
        unit: The new unit. It is one of the keys of ``UNITS``
            (``"s"``, ``"ms"``, ``"us"``, ``"µs"`` and ``"ns"``) unless
            ``scale`` is given.
        scale: The conversion from seconds to ``unit``. If ``None``,
            the scale of ``unit`` in ``UNITS`` is used.

    Returns:
        A copy of the kind with the unit and its scale. ``"us"`` is
            shown as ``"µs"``.

    Raises:
        ValueError: If the unit is not in ``UNITS`` and ``scale`` is
            not given, or if ``scale`` is not positive.

    Example:
        ```pycon
        >>> from feu.benchmark import BENCHMARK_KIND, with_unit
        >>> with_unit(BENCHMARK_KIND, "ms").unit
        'ms'
        >>> with_unit(BENCHMARK_KIND, "ms").scale
        1000.0
        >>> with_unit(BENCHMARK_KIND, "min", scale=1 / 60).unit
        'min'

        ```
    """
    if scale is None:
        if unit not in UNITS:
            msg = f"Unknown unit {unit!r}. The valid units are {sorted(UNITS)}, or set the scale"
            raise ValueError(msg)
        scale = UNITS[unit]
    elif scale <= 0:
        msg = f"The scale must be positive, but got {scale}"
        raise ValueError(msg)
    return replace(kind, unit="µs" if unit == "us" else unit, scale=scale)


def sparkline(values: list[float]) -> str:
    r"""Draw the values with block characters.

    Args:
        values: The values to draw.

    Returns:
        One character per value, scaled between the min and the max.

    Example:
        ```pycon
        >>> from feu.benchmark import sparkline
        >>> sparkline([1.0, 2.0, 3.0])
        '▁▅█'

        ```
    """
    low, high = min(values), max(values)
    if high == low:
        return SPARKS[0] * len(values)
    return "".join(SPARKS[round((v - low) / (high - low) * (len(SPARKS) - 1))] for v in values)


def make_table(runs: list[Run], *, kind: TrendKind = BENCHMARK_KIND) -> str:
    r"""Make the Markdown table of the trend of each benchmark.

    Args:
        runs: The runs returned by ``load_runs``.
        kind: The kind of benchmark results.

    Returns:
        A Markdown table sorted by latest time.
    """
    series: dict[str, list[float]] = {}
    for run in runs:
        for label, seconds in run.times.items():
            series.setdefault(label, []).append(seconds * kind.scale)
    unit = kind.unit
    lines = [
        (
            f"| {kind.column} | Latest ({unit}) | First ({unit}) | Change | Median ({unit}) "
            f"| Min ({unit}) | Max ({unit}) | Runs | Trend |"
        ),
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for label, values in sorted(series.items(), key=lambda item: item[1][-1]):
        change = (values[-1] - values[0]) / values[0] * 100 if values[0] else 0.0
        lines.append(
            f"| {label} | {values[-1]:.1f} | {values[0]:.1f} | {change:+.1f}% "
            f"| {statistics.median(values):.1f} | {min(values):.1f} | {max(values):.1f} "
            f"| {len(values)} | `{sparkline(values)}` |"
        )
    return "\n".join(lines)


def find_regressions(
    runs: list[Run], *, window: int = 7, threshold: float = 50.0
) -> list[Regression]:
    r"""Find the benchmarks slower than their recent median.

    The latest run is compared with the median of the previous runs
    (at most ``window``), which is more stable than the comparison with
    one run because the runners are noisy.

    Args:
        runs: The runs returned by ``load_runs``.
        window: The maximum number of previous runs used for the median.
        threshold: The slowdown in percent above which a benchmark is
            a regression.

    Returns:
        The regressions sorted by decreasing change, each one as
            ``(label, latest, median of the previous runs, change in
            percent)``. It is empty if there are fewer than two runs.
    """
    if len(runs) < 2:
        return []
    regressions = []
    for label, latest in runs[-1].times.items():
        previous = [run.times[label] for run in runs[:-1] if label in run.times][-window:]
        if not previous:
            continue
        baseline = statistics.median(previous)
        change = (latest - baseline) / baseline * 100 if baseline else 0.0
        if change > threshold:
            regressions.append((label, latest, baseline, change))
    return sorted(regressions, key=lambda item: item[3], reverse=True)


def make_regression_report(
    regressions: list[Regression], *, kind: TrendKind = BENCHMARK_KIND
) -> str:
    r"""Make the Markdown report of the regressions.

    Args:
        regressions: The regressions returned by ``find_regressions``.
        kind: The kind of benchmark results.

    Returns:
        A Markdown section, or an empty string if there is no regression.
    """
    if not regressions:
        return ""
    unit = kind.unit
    lines = [
        "### Regressions",
        "",
        f"| {kind.column} | Latest ({unit}) | Previous median ({unit}) | Change |",
        "|---|---:|---:|---:|",
    ]
    lines.extend(
        f"| {label} | {latest * kind.scale:.1f} | {baseline * kind.scale:.1f} | {change:+.1f}% |"
        for label, latest, baseline, change in regressions
    )
    return "\n".join(lines)


def make_annotations(
    regressions: list[Regression], *, kind: TrendKind = BENCHMARK_KIND
) -> list[str]:
    r"""Make the GitHub Actions warning annotations of the regressions.

    Args:
        regressions: The regressions returned by ``find_regressions``.
        kind: The kind of benchmark results.

    Returns:
        One ``::warning::`` workflow command per regression.
    """
    unit = kind.unit
    return [
        f"::warning title=Regression::{label} is {change:.1f}% slower than the median of the "
        f"previous runs ({latest * kind.scale:.1f} {unit} instead of "
        f"{baseline * kind.scale:.1f} {unit})"
        for label, latest, baseline, change in regressions
    ]


def _make_trend_report(
    runs: list[Run],
    *,
    kind: TrendKind,
    stat: str,
    days: int,
    window: int,
    threshold: float,
) -> tuple[str, list[str]] | None:
    r"""Make the Markdown report and the annotations of the runs.

    Args:
        runs: The runs returned by ``load_runs``.
        kind: The kind of benchmark results.
        stat: The statistic of the times. It is added to the title if it
            is not ``"median"``.
        days: The size of the window in days.
        window: The maximum number of previous runs used to detect the
            regressions.
        threshold: The slowdown in percent above which a benchmark is
            a regression.

    Returns:
        ``(report, annotations)``, or ``None`` if there is no run.
    """
    if not runs:
        return None
    regressions = find_regressions(runs, window=window, threshold=threshold)
    suffix = "" if stat == DEFAULT_STAT else f" ({stat})"
    report = (
        f"## {kind.heading}{suffix} over the last {days} days ({len(runs)} runs)\n\n"
        f"{make_table(runs, kind=kind)}\n"
    )
    section = make_regression_report(regressions, kind=kind)
    if section:
        report += f"\n{section}\n"
    return report, make_annotations(regressions, kind=kind)


def build_trend_report(
    storage: Path,
    *,
    kind: TrendKind = BENCHMARK_KIND,
    stat: str = DEFAULT_STAT,
    days: int = 90,
    prune: bool = False,
    window: int = 7,
    threshold: float = 50.0,
) -> tuple[str, list[str]] | None:
    r"""Build the Markdown report and the annotations of the trend.

    Args:
        storage: The pytest-benchmark storage directory.
        kind: The kind of benchmark results.
        stat: The statistic of the times, see ``load_runs``. It is
            added to the title of the report if it is not
            ``"median"``.
        days: The size of the window in days.
        prune: If ``True``, delete the files older than the window
            after the report is made, so nothing is deleted if the
            load fails.
        window: The maximum number of previous runs used to detect the
            regressions.
        threshold: The slowdown in percent above which a benchmark is
            a regression.

    Returns:
        ``(report, annotations)``, or ``None`` if there is no run in the
            window. The report is a Markdown text with the table and,
            if there are regressions, the regression section.

    Raises:
        ValueError: If an argument is invalid or a result file is
            invalid, see ``load_runs``.
    """
    runs = load_runs(storage, days=days, kind=kind.name, stat=stat)
    result = _make_trend_report(
        runs, kind=kind, stat=stat, days=days, window=window, threshold=threshold
    )
    if prune:
        prune_runs(storage, days=days)
    return result
