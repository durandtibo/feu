from __future__ import annotations

import pytest

from feu.testing import (
    requests_available,
    requests_not_available,
    urllib3_not_available,
)
from feu.utils.http import fetch_data

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
