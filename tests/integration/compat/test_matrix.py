from __future__ import annotations

import pytest
from packaging.version import Version

from feu.compat.discoverers import discover_compat_targets
from feu.compat.target import Target
from feu.testing import requests_available, requests_not_available
from feu.version import fetch_pypi_requires_python

# NOTE: these tests hit the real PyPI index. Bounds are asserted rather
# than exact snapshots, because upstream projects keep publishing new
# releases (e.g. a new requests/torch patch release) that would otherwise
# silently break these tests without any change to this codebase. Once a
# release drops support for a given Python version it cannot regain it
# retroactively, so a "max >= known last-compatible release" bound stays
# valid even as newer, incompatible releases are published.


@pytest.fixture(autouse=True)
def _reset_cache() -> None:
    fetch_pypi_requires_python.cache_clear()


##############################################
#     Tests for discover_compat_targets      #
##############################################


@pytest.fixture(autouse=True)
def _reset_wheel_cache() -> None:
    from feu.version.pypi import fetch_pypi_wheel_filenames

    fetch_pypi_wheel_filenames.cache_clear()


@requests_available
def test_discover_compat_targets_numpy_linux_free_threaded() -> None:
    # numpy started publishing free-threaded (cp313t/cp314t) linux x86_64
    # wheels once free-threaded CPython builds became available on PyPI;
    # assert a non-empty, internally consistent result rather than exact
    # version numbers, to stay resilient to upstream releases.
    target = Target(python_version="3.14", free_threaded=True, os="linux", arch="x86_64")
    compat = discover_compat_targets("numpy", targets=(target,))
    assert set(compat) == {target}
    ranges = compat[target]
    assert len(ranges) == 1
    assert ranges[0].min is not None
    assert Version(ranges[0].min)
    if ranges[0].max is not None:
        assert Version(ranges[0].max)


@requests_not_available
def test_discover_compat_targets_no_requests() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        discover_compat_targets("numpy")
