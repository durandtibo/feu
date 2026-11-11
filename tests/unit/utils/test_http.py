from __future__ import annotations

from unittest.mock import MagicMock, Mock, patch

import pytest

from feu import __version__
from feu.imports import is_requests_available
from feu.testing import requests_available
from feu.utils.http import fetch_data, fetch_response

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


def make_mock_session(get: Mock) -> MagicMock:
    session = MagicMock(get=get)
    session.__enter__.return_value = session
    return session


@requests_available
def test_fetch_data_success(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch requests.Session() to return a mock session
    #  -> Successful request (200 OK)
    session = make_mock_session(get=Mock(return_value=make_mock_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_data(url="https://my_url") == {"key": "value"}
    session.get.assert_called_once_with(
        url="https://my_url", timeout=10.0, headers=None, params=None
    )


@requests_available
def test_fetch_data_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch requests.Session() to return a mock session
    #  -> Successful request (200 OK)
    session = make_mock_session(get=Mock(return_value=make_mock_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_data(url="https://my_url", timeout=5.0) == {"key": "value"}
    session.get.assert_called_once_with(
        url="https://my_url", timeout=5.0, headers=None, params=None
    )


@requests_available
def test_fetch_data_headers(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch requests.Session() to return a mock session
    #  -> Successful request (200 OK)
    session = make_mock_session(get=Mock(return_value=make_mock_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_data(url="https://my_url", headers={"Accept": "application/vnd.github+json"}) == {
        "key": "value"
    }
    session.get.assert_called_once_with(
        url="https://my_url",
        timeout=10.0,
        headers={"Accept": "application/vnd.github+json"},
        params=None,
    )


@requests_available
def test_fetch_data_timeout_error(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch requests.Session() to return a mock session
    #  -> Timeout error
    monkeypatch.setattr(
        requests,
        "Session",
        lambda: make_mock_session(get=Mock(side_effect=requests.exceptions.Timeout())),
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
        lambda: make_mock_session(get=Mock(return_value=make_mock_response(status=404))),
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
        lambda: make_mock_session(
            get=Mock(side_effect=requests.exceptions.RequestException("boom"))
        ),
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
        lambda: make_mock_session(get=Mock(return_value=make_mock_response(raise_json=True))),
    )
    with pytest.raises(RuntimeError, match="Invalid JSON"):
        fetch_data(url="https://my_url")


@patch("feu.imports.optional.is_requests_available", lambda: False)
def test_fetch_data_no_requests() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        fetch_data(url="https://my_url")


####################################
#     Tests for fetch_response     #
####################################


@requests_available
def test_fetch_response_success(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch requests.Session() to return a mock session
    #  -> Successful request (200 OK)
    session = make_mock_session(get=Mock(return_value=make_mock_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_response(url="https://my_url").json() == {"key": "value"}
    session.get.assert_called_once_with(
        url="https://my_url", timeout=10.0, headers=None, params=None
    )


@requests_available
def test_fetch_response_closes_session(monkeypatch: pytest.MonkeyPatch) -> None:
    session = make_mock_session(get=Mock(return_value=make_mock_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    fetch_response(url="https://my_url")
    session.__exit__.assert_called_once()


@requests_available
def test_fetch_response_closes_session_on_error(monkeypatch: pytest.MonkeyPatch) -> None:
    session = make_mock_session(get=Mock(side_effect=requests.exceptions.Timeout()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    with pytest.raises(RuntimeError, match="timed out"):
        fetch_response(url="https://my_url")
    session.__exit__.assert_called_once()


@requests_available
def test_fetch_response_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch requests.Session() to return a mock session
    #  -> Successful request (200 OK)
    session = make_mock_session(get=Mock(return_value=make_mock_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_response(url="https://my_url", timeout=5.0).json() == {"key": "value"}
    session.get.assert_called_once_with(
        url="https://my_url", timeout=5.0, headers=None, params=None
    )


@requests_available
def test_fetch_response_headers(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch requests.Session() to return a mock session
    #  -> Successful request (200 OK)
    session = make_mock_session(get=Mock(return_value=make_mock_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_response(
        url="https://my_url", headers={"Accept": "application/vnd.github+json"}
    ).json() == {"key": "value"}
    session.get.assert_called_once_with(
        url="https://my_url",
        timeout=10.0,
        headers={"Accept": "application/vnd.github+json"},
        params=None,
    )


@requests_available
def test_fetch_response_timeout_error(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch requests.Session() to return a mock session
    #  -> Timeout error
    monkeypatch.setattr(
        requests,
        "Session",
        lambda: make_mock_session(get=Mock(side_effect=requests.exceptions.Timeout())),
    )
    with pytest.raises(RuntimeError, match="timed out"):
        fetch_response(url="https://my_url")


@requests_available
def test_fetch_response_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch requests.Session() to return a mock session
    #  -> HTTP error response (status >= 400)
    monkeypatch.setattr(
        requests,
        "Session",
        lambda: make_mock_session(get=Mock(return_value=make_mock_response(status=404))),
    )
    with pytest.raises(RuntimeError, match="Network or HTTP error"):
        fetch_response(url="https://my_url")


@requests_available
def test_fetch_response_request_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch requests.Session() to return a mock session
    #  -> Any other RequestException -> RuntimeError
    monkeypatch.setattr(
        requests,
        "Session",
        lambda: make_mock_session(
            get=Mock(side_effect=requests.exceptions.RequestException("boom"))
        ),
    )
    with pytest.raises(RuntimeError, match="Network or HTTP error"):
        fetch_response(url="https://my_url")


@patch("feu.imports.optional.is_requests_available", lambda: False)
def test_fetch_response_no_requests() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        fetch_response(url="https://my_url")


#############################################
#     Tests for the options of the fetch    #
#############################################


@requests_available
def test_fetch_response_params(monkeypatch: pytest.MonkeyPatch) -> None:
    session = make_mock_session(get=Mock(return_value=make_mock_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    fetch_response(url="https://my_url", params={"per_page": 100})
    session.get.assert_called_once_with(
        url="https://my_url", timeout=10.0, headers=None, params={"per_page": 100}
    )


@requests_available
def test_fetch_response_accept(monkeypatch: pytest.MonkeyPatch) -> None:
    session = make_mock_session(get=Mock(return_value=make_mock_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    fetch_response(url="https://my_url", accept="application/json")
    assert session.get.call_args.kwargs["headers"] == {"Accept": "application/json"}


@requests_available
def test_fetch_response_headers_take_precedence_over_accept(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = make_mock_session(get=Mock(return_value=make_mock_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    fetch_response(url="https://my_url", accept="a/b", headers={"Accept": "c/d", "X-Key": "1"})
    assert session.get.call_args.kwargs["headers"] == {"Accept": "c/d", "X-Key": "1"}


@requests_available
def test_fetch_response_does_not_mutate_the_headers(monkeypatch: pytest.MonkeyPatch) -> None:
    session = make_mock_session(get=Mock(return_value=make_mock_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)
    headers = {"X-Key": "1"}

    fetch_response(url="https://my_url", accept="a/b", headers=headers)
    assert headers == {"X-Key": "1"}


@requests_available
def test_fetch_response_user_agent(monkeypatch: pytest.MonkeyPatch) -> None:
    session = make_mock_session(get=Mock(return_value=make_mock_response()))
    session.headers = {}
    monkeypatch.setattr(requests, "Session", lambda: session)

    fetch_response(url="https://my_url")
    assert session.headers["User-Agent"] == f"feu/{__version__}"


@requests_available
def test_fetch_response_mounts_the_retry_policy_on_https_and_http(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = make_mock_session(get=Mock(return_value=make_mock_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    fetch_response(url="https://my_url")
    assert [call.args[0] for call in session.mount.call_args_list] == ["https://", "http://"]


@requests_available
def test_fetch_response_the_same_adapter_is_mounted_on_https_and_http(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = make_mock_session(get=Mock(return_value=make_mock_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    fetch_response(url="https://my_url")
    https, http = session.mount.call_args_list
    assert https.args[1] is http.args[1]


@requests_available
def test_fetch_response_retry_policy(monkeypatch: pytest.MonkeyPatch) -> None:
    session = make_mock_session(get=Mock(return_value=make_mock_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    fetch_response(url="https://my_url")
    retry = session.mount.call_args_list[0].args[1].max_retries
    assert (retry.total, retry.backoff_factor, sorted(retry.status_forcelist)) == (
        5,
        0.5,
        [429, 500, 502, 503, 504],
    )


@requests_available
def test_fetch_data_options_are_keyword_only() -> None:
    with pytest.raises(TypeError, match="positional argument"):
        fetch_data("https://my_url", 5.0)  # ty: ignore[too-many-positional-arguments]


@requests_available
def test_fetch_response_does_not_accept_arbitrary_requests_arguments() -> None:
    with pytest.raises(TypeError, match="unexpected keyword argument 'verify'"):
        fetch_response("https://my_url", verify=False)  # ty: ignore[unknown-argument]
