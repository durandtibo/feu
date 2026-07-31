from __future__ import annotations

import pytest

from feu.compat.discovery import discover_compat
from feu.testing import requests_available, requests_not_available
from feu.version import fetch_pypi_requires_python


@pytest.fixture(autouse=True)
def _reset_cache() -> None:
    fetch_pypi_requires_python.cache_clear()


####################################
#     Tests for discover_compat     #
####################################


@requests_available
def test_discover_compat_requests() -> None:
    compat = discover_compat("requests", python_versions=("3.9", "3.10", "3.11"))
    assert set(compat.keys()) == {"3.9", "3.10", "3.11"}
    for config in compat.values():
        assert set(config.keys()) == {"min", "max"}


@requests_available
def test_discover_compat_torch_matches_known_bound() -> None:
    # torch 2.8.0 is the last release compatible with Python 3.9
    # (https://github.com/pytorch/pytorch/releases).
    compat = discover_compat("torch", python_versions=("3.9",))
    assert compat["3.9"]["max"] == "2.8.0"


@requests_available
def test_discover_compat_default_python_versions() -> None:
    compat = discover_compat("requests")
    assert set(compat.keys()) == {"3.9", "3.10", "3.11", "3.12", "3.13", "3.14", "3.15"}


@requests_not_available
def test_discover_compat_no_requests() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        discover_compat("my_package")
