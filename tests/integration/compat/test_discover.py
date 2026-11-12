from __future__ import annotations

import pytest
from packaging.version import Version

from feu.compat import discover_compat_targets
from feu.compat.registry import PackageData
from feu.compat.shipped import format_package_data, parse_package_data
from feu.compat.target import Target
from feu.testing import requests_available, requests_not_available
from feu.version.pypi import _fetch_pypi_project

# NOTE: these tests hit the real PyPI index. Bounds are asserted rather
# than exact snapshots, because upstream projects keep publishing new
# releases (e.g. a new requests/torch patch release) that would otherwise
# silently break these tests without any change to this codebase. Once a
# release drops support for a given Python version it cannot regain it
# retroactively, so a "max >= known last-compatible release" bound stays
# valid even as newer, incompatible releases are published.


@pytest.fixture(autouse=True)
def _reset_cache() -> None:
    _fetch_pypi_project.cache_clear()


##############################################
#     Tests for discover_compat_targets      #
##############################################


@requests_available
def test_discover_compat_targets_numpy_linux_free_threaded() -> None:
    # numpy started publishing free-threaded (cp313t/cp314t) linux x86_64
    # wheels once free-threaded CPython builds became available on PyPI;
    # assert a non-empty, internally consistent result rather than exact
    # version numbers, to stay resilient to upstream releases.
    target = Target(python_version="3.14", free_threaded=True, os="linux", arch="x86_64")
    compat = discover_compat_targets("numpy", targets=(target,)).targets
    assert set(compat) == {target}
    ranges = compat[target]
    assert len(ranges) == 1
    assert ranges[0].min is not None
    assert Version(ranges[0].min)
    if ranges[0].max is not None:
        assert Version(ranges[0].max)


@requests_available
def test_discover_compat_targets_polars_split_runtime_package() -> None:
    # polars started splitting its compiled backend into per-CPU-feature
    # "runtime" packages (e.g. polars-runtime-32) that it pins to an exact
    # version; the polars companion rule resolves platform support through that
    # pinned runtime package instead of polars' own (pure-Python) wheel. Assert a non-empty, internally
    # consistent result rather than exact version numbers, to stay
    # resilient to upstream releases.
    target = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = discover_compat_targets("polars", targets=(target,)).targets
    assert set(compat) == {target}
    ranges = compat[target]
    assert len(ranges) >= 1
    assert ranges[0].min is not None
    assert Version(ranges[0].min)


@requests_available
def test_discover_compat_targets_versions() -> None:
    """Test that the considered versions are the stable releases."""
    versions = discover_compat_targets("requests", targets=()).versions
    assert list(versions) == sorted(versions, key=Version)
    assert "2.32.5" in versions
    assert not [v for v in versions if Version(v).is_prerelease]


@requests_available
def test_discover_compat_targets_pydantic_pure_wheel_next_to_compiled_wheels() -> None:
    """Test that pydantic 1.x, which ships a pure wheel next to its
    compiled wheels, is judged by its compiled wheels."""
    target = Target(python_version="3.12", os="linux", arch="x86_64")
    ranges = discover_compat_targets("pydantic", targets=(target,)).targets[target]
    assert ranges
    assert ranges[0].min is not None
    assert Version(ranges[0].min) >= Version("1.10")


@requests_not_available
def test_discover_compat_targets_no_requests() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        discover_compat_targets("numpy")


@requests_available
def test_generate_the_data_of_a_small_package_round_trips() -> None:
    """Test that the data of a package is formatted, then parsed back to
    the same value."""
    discovery = discover_compat_targets("xy")
    text = format_package_data("xy", "2026-11-09", discovery.targets)
    assert parse_package_data(text) == PackageData(discovery.targets)
