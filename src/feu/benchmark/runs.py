r"""Contain functions to load and prune the pytest-benchmark results.

This module is the only one of ``feu.benchmark`` that reads and deletes
files. The other modules are pure functions of the values it returns.
"""

from __future__ import annotations

__all__ = ["KINDS", "STATS", "Run", "load_runs", "prune_runs"]

import json
import math
import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from types import MappingProxyType
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

KINDS = ("benchmark", "import")
STATS = ("min", "mean", "median", "max")
LABELS = ("name", "fullname")

# pytest-benchmark always prefixes the name of a result file with a counter.
RESULT_PATTERN = "[0-9][0-9][0-9][0-9]_*.json"
# The label of a benchmark: the name without the ``test_`` prefix and the
# ``_benchmark`` suffix, which is placed before the parameter id.
LABEL_PATTERN = re.compile(r"^(?:test_)?(?P<core>.*?)(?:_benchmark)?(?P<param>\[.*\])?$", re.DOTALL)


@dataclass(frozen=True)
class Run:
    r"""Store the times of the benchmarks of one run.

    Args:
        date: The date of the run, with a time zone.
        machine: The directory of the result below the storage
            (``pytest-benchmark`` saves the runs of one machine in one
            directory), or an empty string if there is none.
        times: The time in seconds of each benchmark, by label. The
            times are finite and greater than zero. The mapping is
            read-only.

    Example:
        ```pycon
        >>> from datetime import UTC, datetime
        >>> from feu.benchmark import Run
        >>> run = Run(datetime(2026, 1, 1, tzinfo=UTC), "linux", {"sort": 0.001})
        >>> run.times["sort"]
        0.001

        ```
    """

    date: datetime
    machine: str
    times: Mapping[str, float]

    def __post_init__(self) -> None:
        object.__setattr__(self, "times", MappingProxyType(dict(self.times)))


def _check_days(days: int) -> None:
    r"""Check the size of the window.

    Args:
        days: The size of the window in days.

    Raises:
        ValueError: If ``days`` is less than 1.
    """
    if days < 1:
        msg = f"days must be greater than or equal to 1, but got {days}"
        raise ValueError(msg)


def _check_choice(name: str, value: str, choices: tuple[str, ...]) -> None:
    r"""Check that a value is one of the choices.

    Args:
        name: The name of the argument, used in the message.
        value: The value to check.
        choices: The valid values.

    Raises:
        ValueError: If ``value`` is not in ``choices``.
    """
    if value not in choices:
        msg = f"Unknown {name} {value!r}. The valid values are {list(choices)}"
        raise ValueError(msg)


def _read_json(path: Path) -> dict[str, Any]:
    r"""Read a pytest-benchmark result file.

    Args:
        path: The path of the file.

    Returns:
        The content of the file.

    Raises:
        ValueError: If the file is not a JSON object.
    """
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        msg = f"{path}: not a pytest-benchmark result ({exc})"
        raise ValueError(msg) from exc
    if isinstance(data, dict):
        return data
    msg = f"{path}: not a pytest-benchmark result (the content is not a JSON object)"
    raise ValueError(msg)


def _get_date(path: Path, data: dict[str, Any]) -> datetime:
    r"""Get the date of a result.

    Args:
        path: The path of the file, used in the messages.
        data: The content of the file.

    Returns:
        The date of the run. A date without time zone is read as UTC.

    Raises:
        ValueError: If the date is missing or is not an ISO date.
    """
    if "datetime" not in data:
        msg = f"{path}: not a pytest-benchmark result (missing key 'datetime')"
        raise ValueError(msg)
    try:
        date = datetime.fromisoformat(data["datetime"])
    except (TypeError, ValueError) as exc:
        msg = f"{path}: not a pytest-benchmark result (invalid date {data['datetime']!r})"
        raise ValueError(msg) from exc
    return date if date.tzinfo is not None else date.replace(tzinfo=UTC)


def _get_label(benchmark: dict[str, Any], kind: str, label: str) -> str:
    r"""Get the label of a benchmark.

    Args:
        benchmark: A benchmark entry of a result file.
        kind: The kind of results, see ``load_runs``.
        label: The rule of the label, see ``load_runs``.

    Returns:
        The label of the benchmark.
    """
    if label == "fullname":
        return benchmark["fullname"]
    if kind == "import" and benchmark.get("param"):
        return benchmark["param"]
    return LABEL_PATTERN.sub(r"\g<core>\g<param>", benchmark["name"])


def _get_time(benchmark: dict[str, Any], kind: str, stat: str) -> float | None:
    r"""Get the time of a benchmark.

    Args:
        benchmark: A benchmark entry of a result file.
        kind: The kind of results, see ``load_runs``.
        stat: The statistic of the times, see ``load_runs``.

    Returns:
        The time in seconds, or ``None`` if the entry has no time (only
            for the ``import`` kind).

    Raises:
        KeyError: If the ``benchmark`` kind entry has no ``stats`` or
            not the statistic.
        ValueError: If the time is not a finite number greater than
            zero.
    """
    if kind == "import":
        seconds = benchmark.get("extra_info", {}).get(f"import_seconds_{stat}")
        if seconds is None:
            return None
    else:
        seconds = benchmark["stats"][stat]
    if (
        isinstance(seconds, bool)
        or not isinstance(seconds, int | float)
        or not math.isfinite(seconds)
        or seconds <= 0
    ):
        msg = f"the time {seconds!r} of {benchmark['name']!r} is not a finite number > 0"
        raise ValueError(msg)
    return float(seconds)


def _get_benchmarks(path: Path, data: dict[str, Any]) -> list[dict[str, Any]]:
    r"""Get the benchmark entries of a result.

    Args:
        path: The path of the file, used in the messages.
        data: The content of the file.

    Returns:
        The benchmark entries.

    Raises:
        ValueError: If the benchmarks are missing or are not a list.
    """
    benchmarks = data.get("benchmarks")
    if isinstance(benchmarks, list):
        return benchmarks
    msg = f"{path}: not a pytest-benchmark result (missing key 'benchmarks')"
    raise ValueError(msg)


def _get_times(
    path: Path, data: dict[str, Any], *, kind: str, stat: str, label: str
) -> dict[str, float]:
    r"""Get the time of each benchmark of a result.

    Args:
        path: The path of the file, used in the messages.
        data: The content of the file.
        kind: The kind of results, see ``load_runs``.
        stat: The statistic of the times, see ``load_runs``.
        label: The rule of the label, see ``load_runs``.

    Returns:
        The time in seconds of each benchmark, by label.

    Raises:
        ValueError: If the result is invalid or if two benchmarks have
            the same label.
    """
    times: dict[str, float] = {}
    for benchmark in _get_benchmarks(path, data):
        try:
            seconds = _get_time(benchmark, kind, stat)
            if seconds is None:
                continue
            key = _get_label(benchmark, kind, label)
        except KeyError as exc:
            msg = f"{path}: not a pytest-benchmark result (missing key {exc})"
            raise ValueError(msg) from exc
        except (TypeError, AttributeError) as exc:
            msg = f"{path}: not a pytest-benchmark result (invalid benchmark entry {benchmark!r})"
            raise ValueError(msg) from exc
        except ValueError as exc:
            msg = f"{path}: {exc}"
            raise ValueError(msg) from exc
        if key in times:
            msg = f"{path}: the label {key!r} is used by two benchmarks; use label='fullname'"
            raise ValueError(msg)
        times[key] = seconds
    return times


def _get_machine(storage: Path, path: Path) -> str:
    r"""Get the machine of a result file.

    Args:
        storage: The storage directory.
        path: The path of a result file below the storage.

    Returns:
        The directory of the file relative to the storage, or an empty
            string if the file is directly in the storage.
    """
    relative = path.parent.relative_to(storage).as_posix()
    return "" if relative == "." else relative


def load_runs(
    storage: Path,
    *,
    days: int = 90,
    kind: str = "benchmark",
    stat: str = "median",
    label: str = "name",
) -> list[Run]:
    r"""Load the results of the runs in the window.

    Only the files that ``pytest-benchmark`` names (``NNNN_*.json``)
    are read, the other files are ignored. A run without time is
    dropped.

    Args:
        storage: The pytest-benchmark storage directory.
        days: The size of the window in days. It must be at least 1.
        kind: The kind of results, ``"benchmark"`` or ``"import"``. The
            ``benchmark`` kind reads the statistic from the ``stats``
            of ``pytest-benchmark``; the ``import`` kind reads
            ``import_seconds_<stat>`` of the ``extra_info``, and
            ignores the benchmarks that do not have it.
        stat: The statistic of the times: ``"min"``, ``"mean"``,
            ``"median"`` or ``"max"``.
        label: The rule of the label of a benchmark. ``"name"`` is
            the name without the ``test_`` prefix and the
            ``_benchmark`` suffix (``test_sort_benchmark[10]`` is
            ``sort[10]``), or the parameter for the ``import`` kind.
            ``"fullname"`` is the full name of the benchmark.

    Returns:
        The runs sorted by date then by machine.

    Raises:
        ValueError: If an argument is invalid, if a result file is
            invalid (the message has its path), or if two benchmarks
            of a run have the same label.

    Example:
        ```pycon
        >>> import json
        >>> import tempfile
        >>> from pathlib import Path
        >>> from feu.benchmark import load_runs
        >>> with tempfile.TemporaryDirectory() as tmp:
        ...     result = {
        ...         "datetime": "2999-01-01T00:00:00+00:00",
        ...         "benchmarks": [{"name": "test_sort_benchmark", "stats": {"median": 0.001}}],
        ...     }
        ...     _ = Path(tmp, "0001_run.json").write_text(json.dumps(result))
        ...     runs = load_runs(Path(tmp))
        ...
        >>> runs[0].times["sort"]
        0.001

        ```
    """
    _check_days(days)
    _check_choice("kind", kind, KINDS)
    _check_choice("stat", stat, STATS)
    _check_choice("label", label, LABELS)
    limit = datetime.now(tz=UTC) - timedelta(days=days)
    runs = []
    for path in sorted(storage.rglob(RESULT_PATTERN)):
        data = _read_json(path)
        date = _get_date(path, data)
        if date < limit:
            continue
        times = _get_times(path, data, kind=kind, stat=stat, label=label)
        if times:
            runs.append(Run(date, _get_machine(storage, path), times))
    return sorted(runs, key=lambda run: (run.date, run.machine))


def prune_runs(storage: Path, *, days: int = 90) -> list[Path]:
    r"""Delete the results older than the window.

    Args:
        storage: The pytest-benchmark storage directory.
        days: The size of the window in days. It must be at least 1.

    Returns:
        The paths of the deleted files, sorted.

    Raises:
        ValueError: If ``days`` is invalid or if a result file has no
            valid date. The files that were sorted before it may be
            deleted.

    Example:
        ```pycon
        >>> import json
        >>> import tempfile
        >>> from pathlib import Path
        >>> from feu.benchmark import prune_runs
        >>> with tempfile.TemporaryDirectory() as tmp:
        ...     result = {"datetime": "2000-01-01T00:00:00+00:00", "benchmarks": []}
        ...     _ = Path(tmp, "0001_run.json").write_text(json.dumps(result))
        ...     [path.name for path in prune_runs(Path(tmp))]
        ...
        ['0001_run.json']

        ```
    """
    _check_days(days)
    limit = datetime.now(tz=UTC) - timedelta(days=days)
    old = [
        path
        for path in sorted(storage.rglob(RESULT_PATTERN))
        if _get_date(path, _read_json(path)) < limit
    ]
    for path in old:
        path.unlink()
    return old
