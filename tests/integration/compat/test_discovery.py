from __future__ import annotations

import pytest
from packaging.version import Version

from feu.compat.discovery import DEFAULT_PYTHON_VERSIONS, discover_compat
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


def _assert_valid_compat(compat: dict[str, dict[str, str | None]]) -> None:
    for config in compat.values():
        assert set(config) == {"min", "max"}
        if config["min"] is not None and config["max"] is not None:
            assert Version(config["min"]) <= Version(config["max"])


####################################
#     Tests for discover_compat     #
####################################


@requests_available
def test_discover_compat_requests() -> None:
    # requests never declared `requires_python` until 2.31.0 (>=3.7), so
    # early releases without metadata are treated as compatible with every
    # Python version, hence `min == "0.0.1"` (the first ever release).
    # 2.32.5 (>=3.9) is the last release known to still support Python 3.9
    # (https://pypi.org/project/requests/#history).
    compat = discover_compat("requests", python_versions=("3.9", "3.10", "3.11"))
    assert set(compat) == {"3.9", "3.10", "3.11"}
    _assert_valid_compat(compat)
    for config in compat.values():
        assert config["min"] == "0.0.1"
    assert compat["3.9"]["max"] is not None
    assert Version(compat["3.9"]["max"]) >= Version("2.32.5")
    assert compat["3.10"]["max"] is None
    assert compat["3.11"]["max"] is None


@requests_available
def test_discover_compat_torch() -> None:
    # torch's earliest releases predate `requires_python` metadata, hence
    # `min == "1.0.0"` (the first stable release). 2.8.0 is the last
    # release known to still support Python 3.9
    # (https://github.com/pytorch/pytorch/releases).
    compat = discover_compat("torch", python_versions=("3.9", "3.10", "3.11"))
    assert set(compat) == {"3.9", "3.10", "3.11"}
    _assert_valid_compat(compat)
    for config in compat.values():
        assert config["min"] == "1.0.0"
    assert compat["3.9"]["max"] is not None
    assert Version(compat["3.9"]["max"]) >= Version("2.8.0")
    assert compat["3.10"]["max"] is None
    assert compat["3.11"]["max"] is None


@requests_available
def test_discover_compat_default_python_versions() -> None:
    compat = discover_compat("requests")
    assert set(compat) == set(DEFAULT_PYTHON_VERSIONS)
    _assert_valid_compat(compat)
    for config in compat.values():
        assert config["min"] == "0.0.1"
    assert compat["3.9"]["max"] is not None
    assert Version(compat["3.9"]["max"]) >= Version("2.32.5")
    for python_version in ("3.10", "3.11", "3.12", "3.13", "3.14", "3.15"):
        assert compat[python_version]["max"] is None


@requests_not_available
def test_discover_compat_no_requests() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        discover_compat("my_package")
