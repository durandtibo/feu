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
    assert {
        version: mapping[version]
        for version in (
            "2.28.0",
            "2.28.1",
            "2.28.2",
            "2.29.0",
            "2.30.0",
            "2.31.0",
            "2.32.0",
            "2.32.3",
            "2.32.4",
            "2.32.5",
        )
    } == {
        "2.28.0": ">=3.7, <4",
        "2.28.1": ">=3.7, <4",
        "2.28.2": ">=3.7, <4",
        "2.29.0": ">=3.7",
        "2.30.0": ">=3.7",
        "2.31.0": ">=3.7",
        "2.32.0": ">=3.8",
        "2.32.3": ">=3.8",
        "2.32.4": ">=3.8",
        "2.32.5": ">=3.9",
    }


@requests_available
def test_fetch_pypi_requires_python_torch() -> None:
    mapping = fetch_pypi_requires_python("torch")
    assert isinstance(mapping, dict)
    assert {version: mapping[version] for version in ("2.6.0", "2.7.0", "2.7.1", "2.8.0")} == {
        "2.6.0": ">=3.9.0",
        "2.7.0": ">=3.9.0",
        "2.7.1": ">=3.9.0",
        "2.8.0": ">=3.9.0",
    }


@requests_not_available
def test_fetch_pypi_requires_python_no_requests() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        fetch_pypi_requires_python("my_package")
