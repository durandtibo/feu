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
    # requests never declared `requires_python` until 2.31.0 (>=3.7), so
    # early releases without metadata are treated as compatible with every
    # Python version, hence `min == "0.0.1"` (the first ever release).
    # 2.32.5 (>=3.9) is the last release still compatible with Python 3.9
    # (https://pypi.org/project/requests/#history).
    compat = discover_compat("requests", python_versions=("3.9", "3.10", "3.11"))
    assert compat == {
        "3.9": {"min": "0.0.1", "max": "2.32.5"},
        "3.10": {"min": "0.0.1", "max": None},
        "3.11": {"min": "0.0.1", "max": None},
    }


@requests_available
def test_discover_compat_torch() -> None:
    # torch's earliest releases predate `requires_python` metadata, hence
    # `min == "1.0.0"` (the first stable release). 2.8.0 is the last
    # release compatible with Python 3.9
    # (https://github.com/pytorch/pytorch/releases).
    compat = discover_compat("torch", python_versions=("3.9", "3.10", "3.11"))
    assert compat == {
        "3.9": {"min": "1.0.0", "max": "2.8.0"},
        "3.10": {"min": "1.0.0", "max": None},
        "3.11": {"min": "1.0.0", "max": None},
    }


@requests_available
def test_discover_compat_default_python_versions() -> None:
    compat = discover_compat("requests")
    assert compat == {
        "3.9": {"min": "0.0.1", "max": "2.32.5"},
        "3.10": {"min": "0.0.1", "max": None},
        "3.11": {"min": "0.0.1", "max": None},
        "3.12": {"min": "0.0.1", "max": None},
        "3.13": {"min": "0.0.1", "max": None},
        "3.14": {"min": "0.0.1", "max": None},
        "3.15": {"min": "0.0.1", "max": None},
    }


@requests_not_available
def test_discover_compat_no_requests() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        discover_compat("my_package")
