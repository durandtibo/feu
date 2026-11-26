r"""Benchmarks for ``feu.benchmark``, the package that reports the trend of
the benchmarks.

The storage is a set of results written like ``pytest-benchmark`` does
(``<storage>/<machine>/NNNN_<name>.json``), so that the load is measured
on files of a realistic size.

Run them explicitly with:

    inv test.benchmark
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import pytest

from feu.benchmark import find_regressions, load_runs, make_report

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_benchmark.fixture import BenchmarkFixture

NUM_RUNS = 30
NUM_BENCHMARKS = 100


def _make_result(index: int) -> dict:
    date = datetime(2026, 1, 1, tzinfo=UTC) + timedelta(days=index)
    return {
        "datetime": date.isoformat(),
        "benchmarks": [
            {
                "name": f"test_case{i}_benchmark",
                "fullname": f"tests/benchmarks/test_x.py::test_case{i}_benchmark",
                "stats": dict.fromkeys(
                    ("min", "mean", "median", "max"), 1e-06 * (i + 1) * (1 + index / 100)
                ),
            }
            for i in range(NUM_BENCHMARKS)
        ],
    }


@pytest.fixture(scope="module")
def storage(tmp_path_factory: pytest.TempPathFactory) -> Path:
    path = tmp_path_factory.mktemp("storage")
    machine = path / "Linux-CPython-3.12-64bit"
    machine.mkdir()
    for index in range(NUM_RUNS):
        (machine / f"{index + 1:04d}_nightly.json").write_text(json.dumps(_make_result(index)))
    return path


def test_load_runs_benchmark(benchmark: BenchmarkFixture, storage: Path) -> None:
    benchmark(load_runs, storage, days=36500)


def test_find_regressions_benchmark(benchmark: BenchmarkFixture, storage: Path) -> None:
    runs = load_runs(storage, days=36500)
    benchmark(find_regressions, runs, baseline_runs=7, threshold=50.0)


def test_make_report_benchmark(benchmark: BenchmarkFixture, storage: Path) -> None:
    runs = load_runs(storage, days=36500)
    benchmark(make_report, runs, days=36500)
