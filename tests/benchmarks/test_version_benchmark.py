r"""Benchmarks for the functions of ``feu.version`` that work on version
strings.

Run them explicitly with:

    inv test.benchmark
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from feu.version import (
    filter_stable_versions,
    filter_valid_versions,
    latest_major_versions,
    latest_minor_versions,
    parse_version_request,
)

if TYPE_CHECKING:
    from pytest_benchmark.fixture import BenchmarkFixture

VERSIONS = [
    f"{major}.{minor}.{patch}" for major in range(5) for minor in range(20) for patch in range(5)
]
PRERELEASES = [f"{major}.0.0rc1" for major in range(5)]
VERSIONS_WITH_INVALID = [*VERSIONS, *PRERELEASES, "not-a-version"]


def test_parse_version_request_benchmark(benchmark: BenchmarkFixture) -> None:
    benchmark(parse_version_request, "2.*")


def test_filter_valid_versions_benchmark(benchmark: BenchmarkFixture) -> None:
    benchmark(filter_valid_versions, VERSIONS_WITH_INVALID)


def test_filter_stable_versions_benchmark(benchmark: BenchmarkFixture) -> None:
    benchmark(filter_stable_versions, [*VERSIONS, *PRERELEASES])


def test_latest_major_versions_benchmark(benchmark: BenchmarkFixture) -> None:
    benchmark(latest_major_versions, VERSIONS)


def test_latest_minor_versions_benchmark(benchmark: BenchmarkFixture) -> None:
    benchmark(latest_minor_versions, VERSIONS)
