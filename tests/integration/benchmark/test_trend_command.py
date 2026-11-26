from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from feu.testing import click_available

# Two results written by pytest-benchmark: the second run is twice as slow as the first.
DATA = Path(__file__).parents[2] / "unit" / "benchmark" / "data"


def run_command(
    *args: str, encoding: str = "utf-8", storage: Path = DATA
) -> subprocess.CompletedProcess[bytes]:
    env = {**os.environ, "PYTHONIOENCODING": encoding, "PYTHONUTF8": "0", "LC_ALL": "C"}
    return subprocess.run(  # noqa: S603
        [sys.executable, "-m", "feu", "benchmark-trend", str(storage), *args],
        check=False,
        capture_output=True,
        env=env,
    )


@click_available
def test_benchmark_trend_writes_utf8_under_a_cp1252_console() -> None:
    """Test that ``feu benchmark-trend`` writes UTF-8 when the standard
    streams are cp1252, so a redirect to a file does not fail."""
    result = run_command("--days", "100000", encoding="cp1252")
    assert (result.returncode, "µs".encode() in result.stdout, "▁".encode() in result.stdout) == (
        0,
        True,
        True,
    )


@click_available
def test_benchmark_trend_fail_on_regression_exit_status() -> None:
    """Test that ``feu benchmark-trend --fail-on-regression`` exits with
    the status 1 for a real result with a regression."""
    result = run_command("--days", "100000", "--fail-on-regression")
    assert result.returncode == 1


@click_available
def test_benchmark_trend_without_fail_on_regression_exit_status() -> None:
    """Test that ``feu benchmark-trend`` exits with the status 0 for a
    real result with a regression."""
    assert run_command("--days", "100000").returncode == 0


@click_available
def test_benchmark_trend_annotations_are_on_the_standard_error() -> None:
    """Test that ``feu benchmark-trend`` writes the annotations on the
    standard error and only the report on the standard output."""
    result = run_command("--days", "100000")
    assert (b"::warning" in result.stderr, b"::warning" in result.stdout) == (True, False)


@click_available
def test_benchmark_trend_no_result_has_an_empty_standard_output(tmp_path: Path) -> None:
    """Test that ``feu benchmark-trend`` has an empty standard output and
    a message on the standard error when there is no result."""
    result = run_command(storage=tmp_path)
    assert (result.returncode, result.stdout, b"No benchmark results" in result.stderr) == (
        0,
        b"",
        True,
    )


@click_available
def test_benchmark_trend_usage_error_exit_status() -> None:
    """Test that ``feu benchmark-trend`` exits with the status 2 for an
    invalid option value."""
    assert run_command("--days", "0").returncode == 2


@click_available
@pytest.mark.parametrize("option", ["--window", "--scale"])
def test_benchmark_trend_removed_options_are_usage_errors(option: str) -> None:
    """Test that ``feu benchmark-trend`` names a removed option in the
    usage error."""
    result = run_command(option, "1")
    assert (result.returncode, option.encode() in result.stderr) == (2, True)
