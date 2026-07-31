from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from feu.imports import is_requests_available
from feu.testing import requests_available
from feu.version import fetch_pypi_requires_python, fetch_pypi_versions, fetch_pypi_wheel_filenames

if is_requests_available():
    import requests
    from requests import Response
else:
    Response = Mock


@pytest.fixture(autouse=True)
def _reset_cache() -> None:
    fetch_pypi_versions.cache_clear()
    fetch_pypi_requires_python.cache_clear()
    fetch_pypi_wheel_filenames.cache_clear()


#########################################
#     Tests for fetch_pypi_versions     #
#########################################


def make_mock_response() -> Response:
    resp = Mock(json=Mock(return_value={"releases": {"1.2.0": None, "1.2.3": None, "2.0.0": None}}))
    resp.status_code = 200
    return resp


@requests_available
def test_fetch_pypi_versions(monkeypatch: pytest.MonkeyPatch) -> None:
    session = Mock(get=Mock(return_value=make_mock_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_pypi_versions("my_package") == ("1.2.0", "1.2.3", "2.0.0")
    session.get.assert_called_once_with(url="https://pypi.org/pypi/my_package/json", timeout=10.0)


@requests_available
def test_fetch_pypi_versions_reverse(monkeypatch: pytest.MonkeyPatch) -> None:
    session = Mock(get=Mock(return_value=make_mock_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_pypi_versions("my_package", reverse=True) == ("2.0.0", "1.2.3", "1.2.0")
    session.get.assert_called_once_with(url="https://pypi.org/pypi/my_package/json", timeout=10.0)


@patch("feu.imports.requests.is_requests_available", lambda: False)
def test_fetch_pypi_versions_no_requests() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        fetch_pypi_versions("my_package")


##################################################
#     Tests for fetch_pypi_requires_python     #
##################################################


def make_mock_requires_python_response() -> Response:
    resp = Mock(
        json=Mock(
            return_value={
                "releases": {
                    "1.0.0": [{"requires_python": ">=3.6"}],
                    "1.2.0": [{"requires_python": ">=3.8"}, {"requires_python": ">=3.8"}],
                    "1.3.0": [],
                    "2.0.0": [{"requires_python": None}],
                }
            }
        )
    )
    resp.status_code = 200
    return resp


@requests_available
def test_fetch_pypi_requires_python(monkeypatch: pytest.MonkeyPatch) -> None:
    session = Mock(get=Mock(return_value=make_mock_requires_python_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_pypi_requires_python("my_package") == {
        "1.0.0": ">=3.6",
        "1.2.0": ">=3.8",
        "1.3.0": None,
        "2.0.0": None,
    }
    session.get.assert_called_once_with(url="https://pypi.org/pypi/my_package/json", timeout=10.0)


@patch("feu.imports.requests.is_requests_available", lambda: False)
def test_fetch_pypi_requires_python_no_requests() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        fetch_pypi_requires_python("my_package")


####################################################
#     Tests for fetch_pypi_wheel_filenames          #
####################################################


def make_mock_wheel_filenames_response() -> Response:
    resp = Mock(
        json=Mock(
            return_value={
                "releases": {
                    "1.0.0": [
                        {
                            "filename": "pkg-1.0.0-cp39-cp39-manylinux_2_17_x86_64.whl",
                            "packagetype": "bdist_wheel",
                        },
                        {"filename": "pkg-1.0.0.tar.gz", "packagetype": "sdist"},
                    ],
                    "1.1.0": [
                        {
                            "filename": "pkg-1.1.0-cp39-cp39-manylinux_2_17_x86_64.whl",
                            "packagetype": "bdist_wheel",
                        },
                        {
                            "filename": "pkg-1.1.0-cp310-cp310-manylinux_2_17_x86_64.whl",
                            "packagetype": "bdist_wheel",
                        },
                    ],
                    "1.2.0": [{"filename": "pkg-1.2.0.tar.gz", "packagetype": "sdist"}],
                    "1.3.0": [],
                }
            }
        )
    )
    resp.status_code = 200
    return resp


@requests_available
def test_fetch_pypi_wheel_filenames(monkeypatch: pytest.MonkeyPatch) -> None:
    session = Mock(get=Mock(return_value=make_mock_wheel_filenames_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_pypi_wheel_filenames("my_package") == {
        "1.0.0": ("pkg-1.0.0-cp39-cp39-manylinux_2_17_x86_64.whl",),
        "1.1.0": (
            "pkg-1.1.0-cp39-cp39-manylinux_2_17_x86_64.whl",
            "pkg-1.1.0-cp310-cp310-manylinux_2_17_x86_64.whl",
        ),
        "1.2.0": (),
        "1.3.0": (),
    }
    session.get.assert_called_once_with(url="https://pypi.org/pypi/my_package/json", timeout=10.0)


@patch("feu.imports.requests.is_requests_available", lambda: False)
def test_fetch_pypi_wheel_filenames_no_requests() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        fetch_pypi_wheel_filenames("my_package")
