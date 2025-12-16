r"""Contain utility functions to manage HTTP requests."""

from __future__ import annotations

__all__ = ["fetch_data"]

from typing import TYPE_CHECKING, Any

from feu.imports import (
    check_requests,
    is_requests_available,
    is_urllib3_available,
)

if TYPE_CHECKING or is_requests_available():
    import requests
    from requests.adapters import HTTPAdapter
else:  # pragma: no cover
    from feu.utils.fallback.requests import HTTPAdapter, requests

if TYPE_CHECKING or is_urllib3_available():
    from urllib3.util.retry import Retry
else:  # pragma: no cover
    from feu.utils.fallback.urllib3 import Retry


def fetch_data(url: str, timeout: float = 10.0, **kwargs: Any) -> dict[str, Any]:
    r"""Retrieve data for a given URL.

    This function performs an HTTP GET request to fetch repository information.
    It configures a retry policy for transient errors
    (e.g., 429, 500, 502, 503, 504), handles network and
    timeout failures, validates the HTTP response, and returns the parsed JSON
    payload. Any unrecoverable error is raised as a RuntimeError with a clear
    message.

    Args:
        url: The URL.
        timeout: The number of seconds to wait for the server to send
            data before giving up.
        **kwargs: Optional arguments that ``requests.get`` takes.

    Returns:
        dict: The parsed JSON object returned.

    Raises:
        RuntimeError: If the request times out, if a network or HTTP error occurs,
            or if the response body contains invalid JSON.

    Example usage:

    ```pycon

    >>> from feu.utils.http import fetch_data
    >>> data = fetch_data("https://pypi.org/pypi/requests/json")  # doctest: +SKIP

    ```
    """
    check_requests()
    session = requests.Session()

    if is_urllib3_available():
        retry = Retry(
            total=5,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)

    try:
        resp = session.get(url=url, timeout=timeout, **kwargs)
        resp.raise_for_status()
    except requests.exceptions.Timeout as exc:
        msg = "GitHub API request timed out"
        raise RuntimeError(msg) from exc
    except requests.exceptions.RequestException as exc:
        msg = f"Network or HTTP error: {exc}"
        raise RuntimeError(msg) from exc

    try:
        return resp.json()
    except ValueError as exc:
        msg = "Invalid JSON received"
        raise RuntimeError(msg) from exc
