r"""Contain utility functions to manage HTTP requests."""

from __future__ import annotations

__all__ = ["fetch_data", "fetch_response"]

from typing import TYPE_CHECKING, Any

from feu.imports import check_requests

if TYPE_CHECKING:
    import requests


def fetch_data(url: str, timeout: float = 10.0, **kwargs: Any) -> dict[str, Any]:
    r"""Retrieve the JSON data for a given URL.

    This function performs an HTTP GET request and parses the response
    body as JSON. It configures a retry policy for transient errors
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
        The parsed JSON object returned.

    Raises:
        RuntimeError: If the request times out, if a network or HTTP error occurs,
            or if the response body contains invalid JSON.
        MissingPackageError: If ``requests`` is not installed.

    Example:
        ```pycon
        >>> from feu.utils.http import fetch_data
        >>> data = fetch_data("https://pypi.org/pypi/requests/json")  # doctest: +SKIP

        ```
    """
    resp = fetch_response(url=url, timeout=timeout, **kwargs)
    try:
        return resp.json()
    except ValueError as exc:
        msg = "Invalid JSON received"
        raise RuntimeError(msg) from exc


def fetch_response(url: str, timeout: float = 10.0, **kwargs: Any) -> requests.Response:
    r"""Retrieve data from a given URL with automatic retry logic.

    This function performs an HTTP GET request with a configured retry policy
    for transient errors (429, 500, 502, 503, 504), with exponential
    backoff and up to 5 retry attempts. The function
    validates the HTTP response and raises detailed errors for failures.

    Args:
        url: The URL to fetch.
        timeout: The number of seconds to wait for the server to send
            data before giving up. Defaults to 10.0.
        **kwargs: Optional arguments that ``requests.get`` accepts.
            The underlying session is closed before the function
            returns, so streaming (``stream=True``) is not supported.

    Returns:
        A ``requests.Response`` object containing the HTTP response.

    Raises:
        RuntimeError: If the request times out, or if a network/HTTP error
            occurs.
        MissingPackageError: If ``requests`` is not installed.

    Example:
        ```pycon
        >>> from feu.utils.http import fetch_response
        >>> response = fetch_response("https://pypi.org/pypi/requests/json")  # doctest: +SKIP
        >>> response.json()  # doctest: +SKIP

        ```
    """
    check_requests()
    import requests  # noqa: PLC0415
    from requests.adapters import HTTPAdapter  # noqa: PLC0415
    from urllib3.util.retry import Retry  # noqa: PLC0415

    with requests.Session() as session:
        retry = Retry(
            total=5,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            raise_on_status=False,
        )
        session.mount("https://", HTTPAdapter(max_retries=retry))

        try:
            resp = session.get(url=url, timeout=timeout, **kwargs)
            resp.raise_for_status()
        except requests.exceptions.Timeout as exc:
            msg = f"Request to {url} timed out after {timeout}s"
            raise RuntimeError(msg) from exc
        except requests.exceptions.RequestException as exc:
            msg = f"Network or HTTP error when accessing {url}: {exc}"
            raise RuntimeError(msg) from exc

    return resp
