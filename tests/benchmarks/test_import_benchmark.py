r"""Benchmarks for the import time of ``feu`` and its subpackages.

Each import is measured in a fresh interpreter (``sys.modules`` caches
imports, so an in-process measurement only sees the first import). Run
them explicitly with:

    inv test.benchmark

The wall time of the subprocess includes the start of the interpreter,
so ``test_python_startup_benchmark`` gives the baseline to subtract. The
``extra_info`` of each result, saved with the benchmark JSON, records
the import time measured inside the interpreter
(``import_seconds_<stat>``, read by ``feu benchmark-trend --kind
import``) and the number of modules loaded.
"""

from __future__ import annotations

import json
import pkgutil
import statistics
import subprocess
import sys
from typing import TYPE_CHECKING

import pytest

import feu

if TYPE_CHECKING:
    from pytest_benchmark.fixture import BenchmarkFixture

SUBPACKAGES = sorted(m.name for m in pkgutil.iter_modules(feu.__path__) if m.ispkg)

ROUNDS = 10

CODE = """
import json, sys, time
start = time.perf_counter()
{statement}
elapsed = time.perf_counter() - start
print(json.dumps({{"seconds": elapsed, "num_modules": len(sys.modules)}}))
"""


def run_import(statement: str) -> dict[str, float]:
    r"""Run ``statement`` in a fresh isolated interpreter.

    Returns:
        The import time and the number of loaded modules, measured
            inside the interpreter.
    """
    code = CODE.format(statement=statement)
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-I", "-c", code], check=True, capture_output=True, text=True
    )
    return json.loads(result.stdout)


def benchmark_import(benchmark: BenchmarkFixture, statement: str) -> None:
    r"""Benchmark the import ``statement`` and save the import times in
    the ``extra_info`` of the result."""
    measures: list[dict[str, float]] = []

    def target() -> None:
        measures.append(run_import(statement))

    benchmark.pedantic(target, rounds=ROUNDS, iterations=1, warmup_rounds=1)
    seconds = [m["seconds"] for m in measures[1:]]
    benchmark.extra_info.update(
        {
            "import_seconds_min": min(seconds),
            "import_seconds_mean": statistics.mean(seconds),
            "import_seconds_median": statistics.median(seconds),
            "import_seconds_max": max(seconds),
            "num_modules": measures[-1]["num_modules"],
        }
    )


def test_python_startup_benchmark(benchmark: BenchmarkFixture) -> None:
    # No import time in the extra_info: the wall time is the baseline to subtract.
    benchmark.pedantic(run_import, args=("pass",), rounds=ROUNDS, iterations=1, warmup_rounds=1)


def test_import_feu_benchmark(benchmark: BenchmarkFixture) -> None:
    benchmark_import(benchmark, "import feu")


@pytest.mark.parametrize("subpackage", SUBPACKAGES)
def test_import_subpackage_benchmark(benchmark: BenchmarkFixture, subpackage: str) -> None:
    benchmark_import(benchmark, f"import feu.{subpackage}")
