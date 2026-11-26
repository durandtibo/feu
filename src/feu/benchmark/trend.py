r"""Contain functions to detect the regressions of the benchmarks.

The functions are pure: they take the runs returned by ``load_runs``.
"""

from __future__ import annotations

__all__ = ["Regression", "find_regressions"]

import statistics
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from feu.benchmark.runs import Run


@dataclass(frozen=True)
class Regression:
    r"""Store a benchmark that is slower than its recent median.

    Args:
        machine: The machine of the runs, see ``Run``.
        label: The label of the benchmark.
        latest: The time in seconds of the latest run.
        baseline: The median time in seconds of the previous runs.
        change: The slowdown in percent.

    Example:
        ```pycon
        >>> from feu.benchmark import Regression
        >>> Regression("", "sort", 0.002, 0.001, 100.0).change
        100.0

        ```
    """

    machine: str
    label: str
    latest: float
    baseline: float
    change: float


def find_regressions(
    runs: Sequence[Run], *, baseline_runs: int = 7, threshold: float = 50.0
) -> list[Regression]:
    r"""Find the benchmarks slower than their recent median.

    The latest run is compared with the median of the previous runs
    (at most ``baseline_runs``), which is more stable than the
    comparison with one run because the runners are noisy. The runs of
    different machines are never compared with each other: each
    machine has its own latest run and its own baseline.

    Args:
        runs: The runs returned by ``load_runs``.
        baseline_runs: The maximum number of previous runs used for
            the median. It must be at least 1.
        threshold: The slowdown in percent above which a benchmark is
            a regression. It must be greater than 0.

    Returns:
        The regressions sorted by decreasing change, then by label and
            machine. It is empty if no machine has two runs.

    Raises:
        ValueError: If ``baseline_runs`` is less than 1 or
            ``threshold`` is not greater than 0.

    Example:
        ```pycon
        >>> from datetime import UTC, datetime
        >>> from feu.benchmark import Run, find_regressions
        >>> date = datetime(2026, 1, 1, tzinfo=UTC)
        >>> runs = [Run(date, "", {"sort": 0.001}), Run(date, "", {"sort": 0.003})]
        >>> find_regressions(runs)
        [Regression(machine='', label='sort', latest=0.003, baseline=0.001, change=200.0)]

        ```
    """
    if baseline_runs < 1:
        msg = f"baseline_runs must be greater than or equal to 1, but got {baseline_runs}"
        raise ValueError(msg)
    if threshold <= 0:
        msg = f"threshold must be greater than 0, but got {threshold}"
        raise ValueError(msg)
    by_machine: dict[str, list[Run]] = {}
    for run in runs:
        by_machine.setdefault(run.machine, []).append(run)
    regressions = []
    for machine, machine_runs in by_machine.items():
        for label, latest in machine_runs[-1].times.items():
            previous = [run.times[label] for run in machine_runs[:-1] if label in run.times]
            if not previous:
                continue
            baseline = statistics.median(previous[-baseline_runs:])
            change = (latest - baseline) / baseline * 100
            if change > threshold:
                regressions.append(Regression(machine, label, latest, baseline, change))
    return sorted(regressions, key=lambda item: (-item.change, item.label, item.machine))
