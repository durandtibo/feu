from __future__ import annotations

import pytest

from feu.imports import is_requests_available
from feu.testing import (
    requests_available,
    requests_not_available,
    urllib3_not_available,
)
from feu.utils.http import fetch_data, fetch_response

if is_requests_available():
    import requests

################################
#     Tests for fetch_data     #
################################


@requests_available
def test_fetch_data_pypi() -> None:
    metadata = fetch_data(url="https://pypi.org/pypi/feu/json")
    assert isinstance(metadata, dict)
    assert "releases" in metadata


@requests_available
@urllib3_not_available
def test_fetch_data_no_urllib3() -> None:
    metadata = fetch_data(url="https://pypi.org/pypi/feu/json")
    assert isinstance(metadata, dict)
    assert "releases" in metadata


@requests_not_available
def test_fetch_data_no_requests() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        fetch_data(url="https://pypi.org/pypi/feu/json")


####################################
#     Tests for fetch_response     #
####################################


@requests_available
def test_fetch_response_pypi() -> None:
    assert isinstance(fetch_response(url="https://pypi.org/pypi/feu/json"), requests.Response)


@requests_not_available
def test_fetch_response_no_requests() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        fetch_response(url="https://pypi.org/pypi/feu/json")
