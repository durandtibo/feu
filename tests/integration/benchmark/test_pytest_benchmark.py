from __future__ import annotations

import json
import os
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
    runs = load_runs(storage, days=1)
    assert [sorted(run.times) for run in runs] == [["sort[10]", "sort[20]"]]


def test_load_runs_reads_utf8_under_the_ascii_locale(tmp_path: Path) -> None:
    """Test that ``load_runs`` reads a result with non-ASCII characters
    when the locale encoding is not UTF-8."""
    bench = {"name": "test_µ_benchmark", "fullname": "t::µ", "stats": {"median": 0.1}}
    result = {"datetime": "2999-01-01T00:00:00+00:00", "benchmarks": [bench]}
    (tmp_path / "0001_run.json").write_bytes(json.dumps(result, ensure_ascii=False).encode())
    code = (
        "import sys; from pathlib import Path; from feu.benchmark import load_runs;"
        "print(list(load_runs(Path(sys.argv[1]))[0].times))"
    )
    env = {**os.environ, "LC_ALL": "C", "PYTHONUTF8": "0", "PYTHONIOENCODING": "utf-8"}
    out = subprocess.run(  # noqa: S603
        [sys.executable, "-c", code, str(tmp_path)],
        check=True,
        capture_output=True,
        env=env,
    )
    assert out.stdout.decode("utf-8").strip() == "['µ']"
