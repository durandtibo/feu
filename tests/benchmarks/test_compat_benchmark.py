r"""Benchmarks for the compatibility registry of ``feu.compat``.

Run them explicitly with:

    inv test.benchmark
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from feu.compat import (
    find_closest_version,
    get_compatible_versions,
    is_valid_version,
    resolve_target,
)

if TYPE_CHECKING:
    from pytest_benchmark.fixture import BenchmarkFixture

TARGET = resolve_target("3.12")


@pytest.mark.parametrize("pkg_version", ["", "2.0.2", "2.*"])
def test_find_closest_version_benchmark(benchmark: BenchmarkFixture, pkg_version: str) -> None:
    benchmark(find_closest_version, "numpy", pkg_version, TARGET)


def test_is_valid_version_benchmark(benchmark: BenchmarkFixture) -> None:
    benchmark(is_valid_version, "numpy", "2.0.2", TARGET)


def test_get_compatible_versions_benchmark(benchmark: BenchmarkFixture) -> None:
    benchmark(get_compatible_versions, "numpy", TARGET)


def test_resolve_target_benchmark(benchmark: BenchmarkFixture) -> None:
    benchmark(resolve_target, "3.12")
