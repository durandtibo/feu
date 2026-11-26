from __future__ import annotations

import subprocess
import sys
from typing import TYPE_CHECKING

from feu.benchmark import load_runs
from feu.testing import pytest_benchmark_available

if TYPE_CHECKING:
    from pathlib import Path

TEST_FILE = """
import pytest


@pytest.mark.parametrize("n", [10, 20])
def test_sort_benchmark(benchmark, n):
    benchmark(sorted, list(range(n)))
"""


def _run_pytest_benchmark(directory: Path, storage: Path) -> None:
    (directory / "test_x_benchmark.py").write_text(TEST_FILE)
    subprocess.run(  # noqa: S603
        [
            sys.executable,
            "-m",
            "pytest",
            "-p",
            "no:cacheprovider",
            "-q",
            "--benchmark-save=run",
            f"--benchmark-storage={storage}",
            "test_x_benchmark.py",
        ],
        cwd=directory,
        check=True,
        capture_output=True,
    )


@pytest_benchmark_available
def test_load_runs_reads_a_result_written_by_pytest_benchmark(tmp_path: Path) -> None:
    """Test that ``load_runs`` reads a result written by the installed
    ``pytest-benchmark``."""
    storage = tmp_path / "store"
    _run_pytest_benchmark(tmp_path, storage)
    runs = load_runs(storage, 1)
    assert [sorted(times) for _, times in runs] == [["sort_benchmark[10]", "sort_benchmark[20]"]]
