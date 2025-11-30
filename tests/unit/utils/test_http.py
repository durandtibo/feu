from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from feu.imports import is_requests_available
from feu.testing import requests_available
from feu.utils.http import fetch_data

if is_requests_available():
    import requests
    from requests import Response
else:
    Response = Mock


################################
#     Tests for fetch_data     #
################################


def make_mock_response(status: int = 200, raise_json: bool = False) -> Response:
    resp = Mock()
    resp.status_code = status

    # raise_for_status
    if status >= 400:
        resp.raise_for_status.side_effect = requests.exceptions.HTTPError(f"{status} error")
    else:
        resp.raise_for_status.return_value = None

    # json() behavior
    if raise_json:
        resp.json.side_effect = ValueError("Invalid JSON")
    else:
        resp.json.return_value = {"key": "value"}

    return resp


@requests_available
def test_fetch_data_success(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch requests.Session() to return a mock session
    #  -> Successful request (200 OK)
    session = Mock(get=Mock(return_value=make_mock_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_data(url="https://my_url") == {"key": "value"}
    session.get.assert_called_once_with(url="https://my_url", timeout=10.0)


@requests_available
def test_fetch_data_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch requests.Session() to return a mock session
    #  -> Successful request (200 OK)
    session = Mock(get=Mock(return_value=make_mock_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_data(url="https://my_url", timeout=5.0) == {"key": "value"}
    session.get.assert_called_once_with(url="https://my_url", timeout=5.0)


@requests_available
def test_fetch_data_headers(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch requests.Session() to return a mock session
    #  -> Successful request (200 OK)
    session = Mock(get=Mock(return_value=make_mock_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_data(url="https://my_url", headers={"Accept": "application/vnd.github+json"}) == {
        "key": "value"
    }
    session.get.assert_called_once_with(
        url="https://my_url", timeout=10.0, headers={"Accept": "application/vnd.github+json"}
    )


@requests_available
def test_fetch_data_timeout_error(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch requests.Session() to return a mock session
    #  -> Timeout error
    monkeypatch.setattr(
        requests, "Session", lambda: Mock(get=Mock(side_effect=requests.exceptions.Timeout()))
    )
    with pytest.raises(RuntimeError, match="timed out"):
        fetch_data(url="https://my_url")


@requests_available
def test_fetch_data_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch requests.Session() to return a mock session
    #  -> HTTP error response (status >= 400)
    monkeypatch.setattr(
        requests,
        "Session",
        lambda: Mock(get=Mock(return_value=make_mock_response(status=404))),
    )
    with pytest.raises(RuntimeError, match="Network or HTTP error"):
        fetch_data(url="https://my_url")


@requests_available
def test_fetch_data_request_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch requests.Session() to return a mock session
    #  -> Any other RequestException -> RuntimeError
    monkeypatch.setattr(
        requests,
        "Session",
        lambda: Mock(get=Mock(side_effect=requests.exceptions.RequestException("boom"))),
    )
    with pytest.raises(RuntimeError, match="Network or HTTP error"):
        fetch_data(url="https://my_url")


@requests_available
def test_fetch_data_invalid_json(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch requests.Session() to return a mock session
    #  -> Invalid JSON response
    monkeypatch.setattr(
        requests,
        "Session",
        lambda: Mock(get=Mock(return_value=make_mock_response(raise_json=True))),
    )
    with pytest.raises(RuntimeError, match="Invalid JSON"):
        fetch_data(url="https://my_url")


@patch("feu.imports.is_requests_available", lambda: False)
def test_fetch_data_no_requests() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        fetch_data(url="https://my_url")


@requests_available
@patch("feu.utils.http.is_urllib3_available", lambda: False)
def test_fetch_data_no_urllib3(monkeypatch: pytest.MonkeyPatch) -> None:
    session = Mock(get=Mock(return_value=make_mock_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_data(url="https://my_url") == {"key": "value"}
    session.get.assert_called_once_with(url="https://my_url", timeout=10)
