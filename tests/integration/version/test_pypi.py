from __future__ import annotations

import pytest

from feu.testing import requests_available, requests_not_available
from feu.version import fetch_pypi_requires_python, fetch_pypi_versions


@pytest.fixture(autouse=True)
def _reset_cache() -> None:
    fetch_pypi_versions.cache_clear()
    fetch_pypi_requires_python.cache_clear()


#########################################
#     Tests for fetch_pypi_versions     #
#########################################


@requests_available
def test_fetch_pypi_versions_requests() -> None:
    versions = fetch_pypi_versions("requests")
    assert isinstance(versions, tuple)
    assert len(versions) >= 157
    assert "2.32.5" in versions


@requests_available
def test_fetch_pypi_versions_torch() -> None:
    versions = fetch_pypi_versions("torch")
    assert isinstance(versions, tuple)
    assert len(versions) >= 42
    assert "2.8.0" in versions


@requests_not_available
def test_fetch_pypi_versions_no_requests() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        fetch_pypi_versions("my_package")


##################################################
#     Tests for fetch_pypi_requires_python     #
##################################################


@requests_available
def test_fetch_pypi_requires_python_requests() -> None:
    mapping = fetch_pypi_requires_python("requests")
    assert isinstance(mapping, dict)
    assert mapping["2.31.0"] == ">=3.7"
    assert mapping["2.32.3"] == ">=3.8"
    assert mapping["2.32.5"] == ">=3.9"


@requests_available
def test_fetch_pypi_requires_python_torch() -> None:
    mapping = fetch_pypi_requires_python("torch")
    assert isinstance(mapping, dict)
    assert "2.8.0" in mapping


@requests_not_available
def test_fetch_pypi_requires_python_no_requests() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        fetch_pypi_requires_python("my_package")
