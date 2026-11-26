r"""Contain functions to make the report of the trend of the benchmarks.

The functions are pure: they take the runs returned by ``load_runs``
and return a Markdown report and the GitHub Actions annotations. They
do not read or write any file.
"""

from __future__ import annotations

__all__ = ["UNITS", "TrendReport", "make_report"]

import math
import statistics
from dataclasses import dataclass
from typing import TYPE_CHECKING

from feu.benchmark.runs import KINDS, STATS, Run
from feu.benchmark.trend import Regression, find_regressions

if TYPE_CHECKING:
    from collections.abc import Sequence

SPARKS = "▁▂▃▄▅▆▇█"
# The conversion from seconds to each time unit.
UNITS: dict[str, float] = {"s": 1.0, "ms": 1e3, "us": 1e6, "ns": 1e9}
# The unit of each kind of results when ``unit`` is not given.
DEFAULT_UNITS = {"benchmark": "us", "import": "ms"}
# The subject of the title and the title of the first column of each kind.
HEADINGS = {"benchmark": "Benchmarks", "import": "Import time"}
COLUMNS = {"benchmark": "Benchmark", "import": "Import"}


@dataclass(frozen=True)
class TrendReport:
    r"""Store the report of the trend of the benchmarks.

    Args:
        markdown: The Markdown report. It is never empty.
        annotations: The GitHub Actions ``::warning::`` commands of
            the regressions, already escaped.
        regressions: The regressions of every machine.

    Example:
        ```pycon
        >>> from feu.benchmark import TrendReport
        >>> TrendReport("## Benchmarks", (), ()).annotations
        ()

        ```
    """

    markdown: str
    annotations: tuple[str, ...]
    regressions: tuple[Regression, ...]


def _sparkline(values: Sequence[float]) -> str:
    r"""Draw the values with block characters.

    Args:
        values: The values to draw.

    Returns:
        One character per value, scaled between the min and the max.
    """
    low, high = min(values), max(values)
    if high == low:
        return SPARKS[0] * len(values)
    return "".join(SPARKS[round((v - low) / (high - low) * (len(SPARKS) - 1))] for v in values)


def _format_time(seconds: float, unit: str) -> str:
    r"""Format a time with three significant digits.

    Args:
        seconds: The time in seconds. It must be greater than zero.
        unit: The unit of the result, one of the keys of ``UNITS``.

    Returns:
        The time in ``unit`` with three significant digits, without
            the unit. A time of at least 100 has no decimal and keeps
            all its integer digits.

    Raises:
        ValueError: If ``seconds`` is not greater than zero.

    Example:
        ```pycon
        >>> from feu.benchmark.report import _format_time
        >>> _format_time(0.0001234, "us")
        '123'
        >>> _format_time(1.234e-06, "us")
        '1.23'

        ```
    """
    if seconds <= 0:
        msg = f"seconds must be greater than 0, but got {seconds}"
        raise ValueError(msg)
    value = seconds * UNITS[unit]
    # Round first, so that 9.996 has the two decimals of 10.0 and not of 9.99.
    magnitude = math.floor(math.log10(float(f"{value:.2e}")))
    return f"{value:.{max(0, 2 - magnitude)}f}"


def _escape_cell(text: str) -> str:
    r"""Escape a text for a cell of a Markdown table.

    Args:
        text: The text to escape.

    Returns:
        The text with ``|`` escaped and the line breaks replaced by a
            space.
    """
    return text.replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def _escape_annotation(text: str) -> str:
    r"""Escape a text for the message of a GitHub workflow command.

    Args:
        text: The text to escape.

    Returns:
        The text with ``%``, carriage return and line feed escaped as
            GitHub expects.
    """
    return text.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def _unit_name(unit: str) -> str:
    r"""Get the name of a unit as it is shown.

    Args:
        unit: One of the keys of ``UNITS``.

    Returns:
        The name of the unit. ``"us"`` is shown as ``"µs"``.
    """
    return "µs" if unit == "us" else unit


def _make_table(runs: Sequence[Run], *, kind: str, unit: str) -> str:
    r"""Make the Markdown table of the trend of each benchmark.

    Args:
        runs: The runs of one machine.
        kind: The kind of results.
        unit: The unit of the times.

    Returns:
        A Markdown table sorted by latest time then by label.
    """
    series: dict[str, list[float]] = {}
    for run in runs:
        for label, seconds in run.times.items():
            series.setdefault(label, []).append(seconds)
    name = _unit_name(unit)
    lines = [
        (
            f"| {COLUMNS[kind]} | Latest ({name}) | First ({name}) | Change | Median ({name}) "
            f"| Min ({name}) | Max ({name}) | Runs | Trend |"
        ),
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for label, values in sorted(series.items(), key=lambda item: (item[1][-1], item[0])):
        change = (values[-1] - values[0]) / values[0] * 100
        lines.append(
            f"| {_escape_cell(label)} | {_format_time(values[-1], unit)} "
            f"| {_format_time(values[0], unit)} | {change:+.1f}% "
            f"| {_format_time(statistics.median(values), unit)} "
            f"| {_format_time(min(values), unit)} | {_format_time(max(values), unit)} "
            f"| {len(values)} | `{_sparkline(values)}` |"
        )
    return "\n".join(lines)


def _make_regression_table(regressions: Sequence[Regression], *, kind: str, unit: str) -> str:
    r"""Make the Markdown table of the regressions.

    Args:
        regressions: The regressions of one machine.
        kind: The kind of results.
        unit: The unit of the times.

    Returns:
        A Markdown table.
    """
    name = _unit_name(unit)
    lines = [
        f"| {COLUMNS[kind]} | Latest ({name}) | Previous median ({name}) | Change |",
        "|---|---:|---:|---:|",
    ]
    lines.extend(
        f"| {_escape_cell(item.label)} | {_format_time(item.latest, unit)} "
        f"| {_format_time(item.baseline, unit)} | {item.change:+.1f}% |"
        for item in regressions
    )
    return "\n".join(lines)


def _make_annotation(regression: Regression, *, unit: str, show_machine: bool) -> str:
    r"""Make the GitHub Actions warning annotation of a regression.

    Args:
        regression: The regression.
        unit: The unit of the times.
        show_machine: If ``True``, the message has the machine.

    Returns:
        A ``::warning::`` workflow command.
    """
    name = _unit_name(unit)
    where = f" on {regression.machine or '(root)'}" if show_machine else ""
    message = (
        f"{regression.label}{where} is {regression.change:.1f}% slower than the median of the "
        f"previous runs ({_format_time(regression.latest, unit)} {name} instead of "
        f"{_format_time(regression.baseline, unit)} {name})"
    )
    return f"::warning title=Regression::{_escape_annotation(message)}"


def _make_section(
    runs: Sequence[Run], regressions: Sequence[Regression], *, kind: str, unit: str, level: int
) -> str:
    r"""Make the Markdown of the runs of one machine.

    Args:
        runs: The runs of one machine.
        regressions: The regressions of this machine.
        kind: The kind of results.
        unit: The unit of the times.
        level: The level of the heading of the regression block.

    Returns:
        The table and, if there are regressions, the regression block.
    """
    text = f"{_make_table(runs, kind=kind, unit=unit)}\n"
    if regressions:
        table = _make_regression_table(regressions, kind=kind, unit=unit)
        text += f"\n{'#' * level} Regressions\n\n{table}\n"
    return text


def make_report(
    runs: Sequence[Run],
    *,
    kind: str = "benchmark",
    stat: str = "median",
    unit: str | None = None,
    days: int = 90,
    baseline_runs: int = 7,
    threshold: float = 50.0,
) -> TrendReport:
    r"""Make the report of the trend of the benchmarks.

    The report has a table of the trend of each benchmark and, if
    there are regressions, a regression block. If the runs come from
    several machines, the report has one section per machine, because
    the runs of different machines are never compared.

    Args:
        runs: The runs returned by ``load_runs``. There must be at
            least one.
        kind: The kind of results, ``"benchmark"`` or ``"import"``.
        stat: The statistic of the times, it is shown in the title.
        unit: The unit of the times: ``"s"``, ``"ms"``, ``"us"`` or
            ``"ns"``. If ``None``, ``"us"`` is used for the
            ``benchmark`` kind and ``"ms"`` for the ``import`` kind.
            Times are shown with three significant digits.
        days: The size of the window in days, shown in the title.
        baseline_runs: The maximum number of previous runs used to
            detect the regressions, see ``find_regressions``.
        threshold: The slowdown in percent above which a benchmark is
            a regression.

    Returns:
        The report.

    Raises:
        ValueError: If there is no run, if ``kind``, ``stat`` or
            ``unit`` is unknown, or if ``baseline_runs`` or
            ``threshold`` is invalid.

    Example:
        ```pycon
        >>> from datetime import UTC, datetime
        >>> from feu.benchmark import Run, make_report
        >>> date = datetime(2026, 1, 1, tzinfo=UTC)
        >>> runs = [Run(date, "", {"sort": 0.001}), Run(date, "", {"sort": 0.003})]
        >>> report = make_report(runs)
        >>> report.markdown.splitlines()[0]
        '## Benchmarks (median) over the last 90 days (2 runs)'
        >>> report.regressions[0].change
        200.0
        >>> report.annotations[0].startswith("::warning title=Regression::sort is 200.0%25 slower")
        True

        ```
    """
    if not runs:
        msg = "runs must not be empty"
        raise ValueError(msg)
    if kind not in KINDS:
        msg = f"Unknown kind {kind!r}. The valid values are {list(KINDS)}"
        raise ValueError(msg)
    if stat not in STATS:
        msg = f"Unknown stat {stat!r}. The valid values are {list(STATS)}"
        raise ValueError(msg)
    unit = DEFAULT_UNITS[kind] if unit is None else unit
    if unit not in UNITS:
        msg = f"Unknown unit {unit!r}. The valid values are {list(UNITS)}"
        raise ValueError(msg)
    regressions = find_regressions(runs, baseline_runs=baseline_runs, threshold=threshold)
    by_machine: dict[str, list[Run]] = {}
    for run in runs:
        by_machine.setdefault(run.machine, []).append(run)
    count = f"{len(runs)} run" + ("" if len(runs) == 1 else "s")
    markdown = f"## {HEADINGS[kind]} ({stat}) over the last {days} days ({count})\n\n"
    if len(by_machine) == 1:
        markdown += _make_section(runs, regressions, kind=kind, unit=unit, level=3)
    else:
        sections = []
        for machine in sorted(by_machine):
            own = [item for item in regressions if item.machine == machine]
            section = _make_section(by_machine[machine], own, kind=kind, unit=unit, level=4)
            sections.append(f"### {_escape_cell(machine or '(root)')}\n\n{section}")
        markdown += "\n".join(sections)
    annotations = tuple(
        _make_annotation(item, unit=unit, show_machine=len(by_machine) > 1) for item in regressions
    )
    return TrendReport(markdown, annotations, tuple(regressions))
