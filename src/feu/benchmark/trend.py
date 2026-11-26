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
    "KINDS",
    "TrendKind",
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

import json
import statistics
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

SPARKS = "▁▂▃▄▅▆▇█"

Run = tuple[datetime, dict[str, float]]
Regression = tuple[str, float, float, float]


def get_benchmark_label(benchmark: dict) -> str:
    r"""Get the label of a benchmark.

    Args:
        benchmark: A benchmark entry of a pytest-benchmark JSON file.

    Returns:
        The name of the benchmark without the ``test_`` prefix and the
            ``_benchmark`` suffix.

    Example:
        ```pycon
        >>> from feu.benchmark import get_benchmark_label
        >>> get_benchmark_label({"name": "test_sort_benchmark"})
        'sort'

        ```
    """
    return benchmark["name"].removeprefix("test_").removesuffix("_benchmark")


def get_import_label(benchmark: dict) -> str:
    r"""Get the label of an import time benchmark.

    Args:
        benchmark: A benchmark entry of a pytest-benchmark JSON file.

    Returns:
        The parameter of the benchmark (for example the name of the
            imported subpackage) if it has one, otherwise the label
            returned by ``get_benchmark_label``.

    Example:
        ```pycon
        >>> from feu.benchmark import get_import_label
        >>> get_import_label({"name": "test_import[utils]", "param": "utils"})
        'utils'
        >>> get_import_label({"name": "test_import_benchmark"})
        'import'

        ```
    """
    return benchmark.get("param") or get_benchmark_label(benchmark)


def _get_median(benchmark: dict) -> float | None:
    return benchmark["stats"]["median"]


def _get_import_median(benchmark: dict) -> float | None:
    return benchmark.get("extra_info", {}).get("import_seconds_median")


@dataclass(frozen=True)
class TrendKind:
    r"""Define how to read and show a kind of benchmark results.

    Args:
        name: The name of the kind, used on the command line.
        unit: The unit of the times shown in the reports.
        scale: The conversion from seconds to ``unit``.
        column: The title of the first column of the table.
        heading: The subject of the title of the report.
        get_label: The function that returns the label of a benchmark
            entry.
        get_time: The function that returns the time in seconds of a
            benchmark entry, or ``None`` if the entry has no time
            (the entry is then ignored).

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
    get_label: Callable[[dict], str]
    get_time: Callable[[dict], float | None]


BENCHMARK_KIND = TrendKind(
    name="benchmark",
    unit="µs",
    scale=1e6,
    column="Benchmark",
    heading="Benchmarks",
    get_label=get_benchmark_label,
    get_time=_get_median,
)
IMPORT_KIND = TrendKind(
    name="import",
    unit="ms",
    scale=1e3,
    column="Import",
    heading="Import time",
    get_label=get_import_label,
    get_time=_get_import_median,
)
KINDS: dict[str, TrendKind] = {kind.name: kind for kind in (BENCHMARK_KIND, IMPORT_KIND)}


def load_runs(
    storage: Path, days: int, *, kind: TrendKind = BENCHMARK_KIND, prune: bool = False
) -> list[Run]:
    r"""Load the results of the runs in the window.

    Args:
        storage: The pytest-benchmark storage directory.
        days: The size of the window in days.
        kind: The kind of benchmark results.
        prune: If ``True``, delete the files older than the window.

    Returns:
        The runs sorted by date, each one as ``(date, {label: time in
            seconds})``. A date without time zone is read as UTC.
    """
    limit = datetime.now(tz=UTC) - timedelta(days=days)
    runs = []
    for path in sorted(storage.rglob("*.json")):
        data = json.loads(path.read_text())
        date = datetime.fromisoformat(data["datetime"])
        if date.tzinfo is None:
            date = date.replace(tzinfo=UTC)
        if date < limit:
            if prune:
                path.unlink()
            continue
        times = {}
        for benchmark in data["benchmarks"]:
            seconds = kind.get_time(benchmark)
            if seconds is not None:
                times[kind.get_label(benchmark)] = seconds
        runs.append((date, times))
    return sorted(runs, key=lambda run: run[0])


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
    for _, times in runs:
        for label, seconds in times.items():
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
    for label, latest in runs[-1][1].items():
        previous = [times[label] for _, times in runs[:-1] if label in times][-window:]
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


def build_trend_report(
    storage: Path,
    *,
    kind: TrendKind = BENCHMARK_KIND,
    days: int = 90,
    prune: bool = False,
    window: int = 7,
    threshold: float = 50.0,
) -> tuple[str, list[str]] | None:
    r"""Build the Markdown report and the annotations of the trend.

    Args:
        storage: The pytest-benchmark storage directory.
        kind: The kind of benchmark results.
        days: The size of the window in days.
        prune: If ``True``, delete the files older than the window.
        window: The maximum number of previous runs used to detect the
            regressions.
        threshold: The slowdown in percent above which a benchmark is
            a regression.

    Returns:
        ``(report, annotations)``, or ``None`` if there is no run in the
            window. The report is a Markdown text with the table and,
            if there are regressions, the regression section.
    """
    runs = load_runs(storage, days, kind=kind, prune=prune)
    if not runs:
        return None
    regressions = find_regressions(runs, window=window, threshold=threshold)
    report = (
        f"## {kind.heading} over the last {days} days ({len(runs)} runs)\n\n"
        f"{make_table(runs, kind=kind)}\n"
    )
    section = make_regression_report(regressions, kind=kind)
    if section:
        report += f"\n{section}\n"
    return report, make_annotations(regressions, kind=kind)
