from __future__ import annotations

import os
from unittest.mock import Mock, patch

import pytest

from feu.imports import is_requests_available
from feu.repo import get_github_metadata
from feu.testing import requests_available

if is_requests_available():
    import requests
    from requests import Response
else:
    Response = Mock


@pytest.fixture(autouse=True)
def _reset_cache() -> None:
    get_github_metadata.cache_clear()


#########################################
#     Tests for get_github_metadata     #
#########################################


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
        resp.json.return_value = {"name": "example-repo"}

    return resp


@requests_available
def test_get_github_metadata_success(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch requests.Session() to return a mock session
    #  -> Successful request (200 OK)
    session = Mock(get=Mock(return_value=make_mock_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert get_github_metadata(owner="owner", repo="repo") == {"name": "example-repo"}
    session.get.assert_called_once_with(
        url="https://api.github.com/repos/owner/repo",
        timeout=10,
        headers={"Accept": "application/vnd.github+json"},
    )


@requests_available
@patch.dict(os.environ, {"GITHUB_TOKEN": "meow"}, clear=True)
def test_get_github_metadata_success_with_token(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch requests.Session() to return a mock session
    #  -> Successful request (200 OK)
    session = Mock(get=Mock(return_value=make_mock_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert get_github_metadata(owner="owner", repo="repo") == {"name": "example-repo"}
    session.get.assert_called_once_with(
        url="https://api.github.com/repos/owner/repo",
        timeout=10,
        headers={"Accept": "application/vnd.github+json", "Authorization": "Bearer meow"},
    )


@requests_available
def test_get_github_metadata_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch requests.Session() to return a mock session
    #  -> Timeout error
    monkeypatch.setattr(
        requests, "Session", lambda: Mock(get=Mock(side_effect=requests.exceptions.Timeout()))
    )
    with pytest.raises(RuntimeError, match="timed out"):
        get_github_metadata(owner="owner", repo="repo")


def test_get_github_metadata_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch requests.Session() to return a mock session
    #  -> HTTP error response (status >= 400)
    monkeypatch.setattr(
        requests,
        "Session",
        lambda: Mock(get=Mock(return_value=make_mock_response(status=404))),
    )
    with pytest.raises(RuntimeError, match="Network or HTTP error"):
        get_github_metadata(owner="owner", repo="repo")


@requests_available
def test_get_github_metadata_request_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch requests.Session() to return a mock session
    #  -> Any other RequestException -> RuntimeError
    monkeypatch.setattr(
        requests,
        "Session",
        lambda: Mock(get=Mock(side_effect=requests.exceptions.RequestException("boom"))),
    )
    with pytest.raises(RuntimeError, match="Network or HTTP error"):
        get_github_metadata(owner="owner", repo="repo")


@requests_available
def test_get_github_metadata_invalid_json(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch requests.Session() to return a mock session
    #  -> Invalid JSON response
    monkeypatch.setattr(
        requests,
        "Session",
        lambda: Mock(get=Mock(return_value=make_mock_response(raise_json=True))),
    )
    with pytest.raises(RuntimeError, match="Invalid JSON"):
        get_github_metadata(owner="owner", repo="repo")


@patch("feu.imports.is_requests_available", lambda: False)
def test_get_github_metadata_no_requests() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        get_github_metadata(owner="my_name", repo="my_package")
