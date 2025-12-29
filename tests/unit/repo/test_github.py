from __future__ import annotations

import logging
import os
from typing import Any
from unittest.mock import Mock, patch

import pytest

from feu.imports import is_requests_available
from feu.repo import display_repos_summary, fetch_github_metadata, fetch_github_repos
from feu.testing import requests_available

if is_requests_available():
    import requests
    from requests import Response
else:
    Response = Mock


@pytest.fixture(autouse=True)
def _reset_cache() -> None:
    fetch_github_metadata.cache_clear()
    fetch_github_repos.cache_clear()


###########################################
#     Tests for fetch_github_metadata     #
###########################################


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
def test_fetch_github_metadata_success(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch requests.Session() to return a mock session
    #  -> Successful request (200 OK)
    session = Mock(get=Mock(return_value=make_mock_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_github_metadata(owner="owner", repo="repo") == {"name": "example-repo"}
    session.get.assert_called_once_with(
        url="https://api.github.com/repos/owner/repo",
        timeout=10,
        headers={"Accept": "application/vnd.github+json"},
    )


@requests_available
@patch.dict(os.environ, {"GITHUB_TOKEN": "meow"}, clear=True)
def test_fetch_github_metadata_success_with_token(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch requests.Session() to return a mock session
    #  -> Successful request (200 OK)
    session = Mock(get=Mock(return_value=make_mock_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_github_metadata(owner="owner", repo="repo") == {"name": "example-repo"}
    session.get.assert_called_once_with(
        url="https://api.github.com/repos/owner/repo",
        timeout=10,
        headers={"Accept": "application/vnd.github+json", "Authorization": "Bearer meow"},
    )


@requests_available
def test_fetch_github_metadata_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch requests.Session() to return a mock session
    #  -> Timeout error
    monkeypatch.setattr(
        requests, "Session", lambda: Mock(get=Mock(side_effect=requests.exceptions.Timeout()))
    )
    with pytest.raises(RuntimeError, match="timed out"):
        fetch_github_metadata(owner="owner", repo="repo")


@requests_available
def test_fetch_github_metadata_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch requests.Session() to return a mock session
    #  -> HTTP error response (status >= 400)
    monkeypatch.setattr(
        requests,
        "Session",
        lambda: Mock(get=Mock(return_value=make_mock_response(status=404))),
    )
    with pytest.raises(RuntimeError, match="Network or HTTP error"):
        fetch_github_metadata(owner="owner", repo="repo")


@requests_available
def test_fetch_github_metadata_request_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch requests.Session() to return a mock session
    #  -> Any other RequestException -> RuntimeError
    monkeypatch.setattr(
        requests,
        "Session",
        lambda: Mock(get=Mock(side_effect=requests.exceptions.RequestException("boom"))),
    )
    with pytest.raises(RuntimeError, match="Network or HTTP error"):
        fetch_github_metadata(owner="owner", repo="repo")


@requests_available
def test_fetch_github_metadata_invalid_json(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch requests.Session() to return a mock session
    #  -> Invalid JSON response
    monkeypatch.setattr(
        requests,
        "Session",
        lambda: Mock(get=Mock(return_value=make_mock_response(raise_json=True))),
    )
    with pytest.raises(RuntimeError, match="Invalid JSON"):
        fetch_github_metadata(owner="owner", repo="repo")


@patch("feu.imports.is_requests_available", lambda: False)
def test_fetch_github_metadata_no_requests() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        fetch_github_metadata(owner="my_name", repo="my_package")


########################################
#     Tests for fetch_github_repos     #
########################################


@pytest.fixture
def mock_response() -> Response:
    """Create a mock response object."""
    response = Mock()
    response.status_code = 200
    response.headers = {}
    return response


@pytest.fixture
def sample_repos() -> list[dict[str, Any]]:
    """Sample repository data."""
    return [
        {"id": 1, "name": "repo1", "full_name": "owner/repo1"},
        {"id": 2, "name": "repo2", "full_name": "owner/repo2"},
    ]


@requests_available
def test_fetch_github_repos_single_page(
    mock_response: Response, sample_repos: list[dict[str, Any]]
) -> None:
    """Test fetching repos with a single page of results."""
    mock_response.json.return_value = sample_repos

    with patch("feu.repo.github.fetch_response", return_value=mock_response):
        result = fetch_github_repos("testowner")

    assert result == (
        {"id": 1, "name": "repo1", "full_name": "owner/repo1"},
        {"id": 2, "name": "repo2", "full_name": "owner/repo2"},
    )


@requests_available
def test_fetch_github_repos_multiple_pages(sample_repos: list[dict[str, Any]]) -> None:
    """Test fetching repos with pagination."""
    # First page
    first_response = Mock()
    first_response.status_code = 200
    first_response.json.return_value = sample_repos[:1]
    first_response.headers = {
        "Link": '<https://api.github.com/users/owner/repos?page=2>; rel="next"'
    }

    # Second page
    second_response = Mock()
    second_response.status_code = 200
    second_response.json.return_value = sample_repos[1:]
    second_response.headers = {}

    with patch("feu.repo.github.fetch_response", side_effect=[first_response, second_response]):
        result = fetch_github_repos("testowner")

    assert result == (
        {"id": 1, "name": "repo1", "full_name": "owner/repo1"},
        {"id": 2, "name": "repo2", "full_name": "owner/repo2"},
    )


@requests_available
def test_fetch_github_repos_no_next_link(sample_repos: list[dict[str, Any]]) -> None:
    """Test fetching repos with a single page of results."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = sample_repos[:1]
    response.headers = {"Link": '<https://api.github.com/users/owner/repos?page=1>; rel="first"'}

    with patch("feu.repo.github.fetch_response", return_value=response):
        result = fetch_github_repos("testowner")

    assert result == ({"id": 1, "name": "repo1", "full_name": "owner/repo1"},)


@requests_available
@patch.dict(os.environ, {"GITHUB_TOKEN": "meow"}, clear=True)
def test_fetch_github_repos_with_github_token(
    mock_response: Response, sample_repos: list[dict[str, Any]]
) -> None:
    """Test that GitHub token is used when available."""
    mock_response.json.return_value = sample_repos

    with patch("feu.repo.github.fetch_response", return_value=mock_response) as mock_fetch:
        fetch_github_repos("testowner")

        call_args = mock_fetch.call_args
        headers = call_args.kwargs["headers"]
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer meow"


@requests_available
@patch.dict(os.environ, {}, clear=True)
def test_fetch_github_repos_without_github_token(
    mock_response: Response, sample_repos: list[dict[str, Any]]
) -> None:
    """Test that authorization header is not added when token is
    missing."""
    mock_response.json.return_value = sample_repos

    with patch("feu.repo.github.fetch_response", return_value=mock_response) as mock_fetch:
        fetch_github_repos("testowner")

        call_args = mock_fetch.call_args
        headers = call_args.kwargs["headers"]
        assert "Authorization" not in headers


@requests_available
def test_fetch_github_repos_api_error() -> None:
    """Test handling of API errors."""
    error_response = Mock()
    error_response.status_code = 404
    error_response.json.return_value = {"message": "Not Found"}

    with patch("feu.repo.github.fetch_response", return_value=error_response):
        result = fetch_github_repos("nonexistent")

    assert result == ()


@requests_available
def test_fetch_github_repos_rate_limit_error() -> None:
    """Test handling of rate limit errors."""
    error_response = Mock()
    error_response.status_code = 403
    error_response.json.return_value = {"message": "API rate limit exceeded"}

    with patch("feu.repo.github.fetch_response", return_value=error_response):
        result = fetch_github_repos("testowner")

    assert result == ()


@requests_available
def test_fetch_github_repos_empty_results(mock_response: Response) -> None:
    """Test fetching repos when user has no repositories."""
    mock_response.json.return_value = []

    with patch("feu.repo.github.fetch_response", return_value=mock_response):
        result = fetch_github_repos("emptyowner")

    assert result == ()


@requests_available
def test_fetch_github_repos_correct_url_and_params(
    mock_response: Response, sample_repos: list[dict[str, Any]]
) -> None:
    """Test that correct URL and parameters are used."""
    mock_response.json.return_value = sample_repos

    with patch("feu.repo.github.fetch_response", return_value=mock_response) as mock_fetch:
        fetch_github_repos("testowner")

        call_args = mock_fetch.call_args
        assert call_args.kwargs["url"] == "https://api.github.com/users/testowner/repos"
        assert call_args.kwargs["params"] == {"per_page": 100, "type": "all"}


@requests_available
def test_fetch_github_repos_headers(
    mock_response: Response, sample_repos: list[dict[str, Any]]
) -> None:
    """Test that correct headers are set."""
    mock_response.json.return_value = sample_repos

    with patch("feu.repo.github.fetch_response", return_value=mock_response) as mock_fetch:
        fetch_github_repos("testowner")

        call_args = mock_fetch.call_args
        headers = call_args.kwargs["headers"]
        assert headers["Accept"] == "application/vnd.github+json"


@requests_available
def test_fetch_github_repos_pagination_link_parsing(sample_repos: list[dict[str, Any]]) -> None:
    """Test parsing of Link header with multiple relations."""
    first_response = Mock()
    first_response.status_code = 200
    first_response.json.return_value = sample_repos[:1]
    first_response.headers = {
        "Link": '<https://api.github.com/users/owner/repos?page=1>; rel="prev", '
        '<https://api.github.com/users/owner/repos?page=2>; rel="next"'
    }

    second_response = Mock()
    second_response.status_code = 200
    second_response.json.return_value = sample_repos[1:]
    second_response.headers = {}

    with patch(
        "feu.repo.github.fetch_response", side_effect=[first_response, second_response]
    ) as mock_fetch:
        result = fetch_github_repos("testowner")

        assert len(result) == 2
        assert mock_fetch.call_count == 2
        # Second call should use the next URL with no params
        second_call_args = mock_fetch.call_args_list[1]
        assert second_call_args.kwargs["url"] == "https://api.github.com/users/owner/repos?page=2"
        assert second_call_args.kwargs["params"] is None


@requests_available
def test_fetch_github_repos_caching(
    mock_response: Response, sample_repos: list[dict[str, Any]]
) -> None:
    """Test that lru_cache is working."""
    mock_response.json.return_value = sample_repos

    with patch("feu.repo.github.fetch_response", return_value=mock_response) as mock_fetch:
        # First call
        result1 = fetch_github_repos("testowner")
        # Second call with same owner
        result2 = fetch_github_repos("testowner")

        # Should only call the API once due to caching
        assert mock_fetch.call_count == 1
        assert result1 == result2
        assert result1 is result2  # Same object due to caching


@patch("feu.imports.is_requests_available", lambda: False)
def test_fetch_github_repos_no_requests() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        fetch_github_repos(owner="testowner")


###########################################
#     Tests for display_repos_summary     #
###########################################


def test_display_repos_summary_empty_list(caplog: pytest.LogCaptureFixture) -> None:
    """Test display_repos_summary with an empty repository list."""
    with caplog.at_level(logging.INFO):
        display_repos_summary([])

    assert "Total repositories: 0" in caplog.text


def test_display_repos_summary_single_repo(caplog: pytest.LogCaptureFixture) -> None:
    """Test display_repos_summary with a single repository."""
    repos = [
        {
            "name": "test-repo",
            "html_url": "https://github.com/user/test-repo",
            "description": "A test repository",
            "stargazers_count": 10,
            "forks_count": 5,
            "language": "Python",
            "private": False,
        }
    ]

    with caplog.at_level(logging.INFO):
        display_repos_summary(repos)

    assert "Total repositories: 1" in caplog.text
    assert "1. test-repo" in caplog.text
    assert "URL: https://github.com/user/test-repo" in caplog.text
    assert "Description: A test repository" in caplog.text
    assert "Stars: 10 | Forks: 5" in caplog.text
    assert "Language: Python" in caplog.text
    assert "Private: False" in caplog.text


def test_display_repos_summary_multiple_repos(caplog: pytest.LogCaptureFixture) -> None:
    """Test display_repos_summary with multiple repositories."""
    repos = [
        {
            "name": "repo1",
            "html_url": "https://github.com/user/repo1",
            "description": "First repo",
            "stargazers_count": 100,
            "forks_count": 20,
            "language": "Python",
            "private": False,
        },
        {
            "name": "repo2",
            "html_url": "https://github.com/user/repo2",
            "description": "Second repo",
            "stargazers_count": 50,
            "forks_count": 10,
            "language": "JavaScript",
            "private": True,
        },
    ]

    with caplog.at_level(logging.INFO):
        display_repos_summary(repos)

    assert "Total repositories: 2" in caplog.text
    assert "1. repo1" in caplog.text
    assert "2. repo2" in caplog.text


def test_display_repos_summary_none_description(caplog: pytest.LogCaptureFixture) -> None:
    """Test display_repos_summary with None description."""
    repos = [
        {
            "name": "no-desc-repo",
            "html_url": "https://github.com/user/no-desc-repo",
            "description": None,
            "stargazers_count": 0,
            "forks_count": 0,
            "language": "Python",
            "private": False,
        }
    ]

    with caplog.at_level(logging.INFO):
        display_repos_summary(repos)

    assert "Description: No description" in caplog.text


def test_display_repos_summary_empty_description(caplog: pytest.LogCaptureFixture) -> None:
    """Test display_repos_summary with empty string description."""
    repos = [
        {
            "name": "empty-desc-repo",
            "html_url": "https://github.com/user/empty-desc-repo",
            "description": "",
            "stargazers_count": 0,
            "forks_count": 0,
            "language": "Python",
            "private": False,
        }
    ]

    with caplog.at_level(logging.INFO):
        display_repos_summary(repos)

    assert "Description: No description" in caplog.text


def test_display_repos_summary_none_language(caplog: pytest.LogCaptureFixture) -> None:
    """Test display_repos_summary with None language."""
    repos = [
        {
            "name": "no-lang-repo",
            "html_url": "https://github.com/user/no-lang-repo",
            "description": "Test repo",
            "stargazers_count": 0,
            "forks_count": 0,
            "language": None,
            "private": False,
        }
    ]

    with caplog.at_level(logging.INFO):
        display_repos_summary(repos)

    assert "Language: Not specified" in caplog.text


def test_display_repos_summary_empty_language(caplog: pytest.LogCaptureFixture) -> None:
    """Test display_repos_summary with empty string language."""
    repos = [
        {
            "name": "empty-lang-repo",
            "html_url": "https://github.com/user/empty-lang-repo",
            "description": "Test repo",
            "stargazers_count": 0,
            "forks_count": 0,
            "language": "",
            "private": False,
        }
    ]

    with caplog.at_level(logging.INFO):
        display_repos_summary(repos)

    assert "Language: Not specified" in caplog.text


def test_display_repos_summary_private_repo(caplog: pytest.LogCaptureFixture) -> None:
    """Test display_repos_summary with a private repository."""
    repos = [
        {
            "name": "private-repo",
            "html_url": "https://github.com/user/private-repo",
            "description": "Private repository",
            "stargazers_count": 0,
            "forks_count": 0,
            "language": "Python",
            "private": True,
        }
    ]

    with caplog.at_level(logging.INFO):
        display_repos_summary(repos)

    assert "Private: True" in caplog.text


def test_display_repos_summary_zero_stars_and_forks(caplog: pytest.LogCaptureFixture) -> None:
    """Test display_repos_summary with zero stars and forks."""
    repos = [
        {
            "name": "new-repo",
            "html_url": "https://github.com/user/new-repo",
            "description": "Brand new repo",
            "stargazers_count": 0,
            "forks_count": 0,
            "language": "Python",
            "private": False,
        }
    ]

    with caplog.at_level(logging.INFO):
        display_repos_summary(repos)

    assert "Stars: 0 | Forks: 0" in caplog.text


def test_display_repos_summary_large_numbers(caplog: pytest.LogCaptureFixture) -> None:
    """Test display_repos_summary with large star and fork counts."""
    repos = [
        {
            "name": "popular-repo",
            "html_url": "https://github.com/user/popular-repo",
            "description": "Very popular repository",
            "stargazers_count": 10000,
            "forks_count": 5000,
            "language": "Python",
            "private": False,
        }
    ]

    with caplog.at_level(logging.INFO):
        display_repos_summary(repos)

    assert "Stars: 10,000 | Forks: 5,000" in caplog.text
