from __future__ import annotations

import pytest

from feu.testing import requests_available, requests_not_available
from feu.version import (
    fetch_pypi_pinned_dependency_version,
    fetch_pypi_requires_python,
    fetch_pypi_versions,
    fetch_pypi_wheel_filenames,
)


@pytest.fixture(autouse=True)
def _reset_cache() -> None:
    fetch_pypi_versions.cache_clear()
    fetch_pypi_requires_python.cache_clear()
    fetch_pypi_wheel_filenames.cache_clear()
    fetch_pypi_pinned_dependency_version.cache_clear()


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


###################################################
#     Tests for fetch_pypi_wheel_filenames     #
###################################################


@requests_available
def test_fetch_pypi_wheel_filenames_numpy() -> None:
    mapping = fetch_pypi_wheel_filenames("numpy")
    assert isinstance(mapping, dict)
    assert all(isinstance(filenames, tuple) for filenames in mapping.values())
    filenames = mapping["2.0.2"]
    assert filenames
    assert all(filename.startswith("numpy-2.0.2-") for filename in filenames)
    assert all(filename.endswith(".whl") for filename in filenames)


@requests_available
def test_fetch_pypi_wheel_filenames_no_wheel() -> None:
    # 'requests' only ever publishes a pure-Python wheel and sdist, so this
    # exercises a release that has exactly one (universal) wheel filename.
    mapping = fetch_pypi_wheel_filenames("requests")
    assert mapping["2.32.5"] == ("requests-2.32.5-py3-none-any.whl",)


@requests_not_available
def test_fetch_pypi_wheel_filenames_no_requests() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        fetch_pypi_wheel_filenames("my_package")


###########################################################
#     Tests for fetch_pypi_pinned_dependency_version     #
###########################################################


@requests_available
def test_fetch_pypi_pinned_dependency_version_found() -> None:
    # pydantic pins its compiled backend, pydantic-core, to an exact
    # version for each release.
    version = fetch_pypi_pinned_dependency_version("pydantic", "2.9.0", "pydantic-core")
    assert version == "2.23.2"


@requests_available
def test_fetch_pypi_pinned_dependency_version_not_pinned() -> None:
    # requests does not pin urllib3 to an exact version.
    version = fetch_pypi_pinned_dependency_version("requests", "2.32.5", "urllib3")
    assert version is None


@requests_available
def test_fetch_pypi_pinned_dependency_version_dependency_absent() -> None:
    version = fetch_pypi_pinned_dependency_version("requests", "2.32.5", "not-a-real-dependency")
    assert version is None


@requests_not_available
def test_fetch_pypi_pinned_dependency_version_no_requests() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        fetch_pypi_pinned_dependency_version("pydantic", "2.9.0", "pydantic-core")
