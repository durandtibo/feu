from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from feu.imports import is_requests_available
from feu.testing import requests_available
from feu.version import fetch_pypi_versions

if is_requests_available():
    import requests
    from requests import Response
else:
    Response = Mock


@pytest.fixture(autouse=True)
def _reset_cache() -> None:
    fetch_pypi_versions.cache_clear()


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


@patch("feu.imports.is_requests_available", lambda: False)
def test_fetch_pypi_versions_no_requests() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        fetch_pypi_versions("my_package")
