from __future__ import annotations

import logging
from unittest.mock import patch

import pytest

from feu.utils.imports import (
    check_requests,
    is_requests_available,
    raise_requests_missing_error,
    requests_available,
)

logger = logging.getLogger(__name__)

MODULE = "feu.utils.imports.requests"


@pytest.fixture(autouse=True)
def _cache_clear() -> None:
    is_requests_available.cache_clear()


def my_function(n: int = 0) -> int:
    return 42 + n


####################
#     requests     #
####################


def test_check_requests_with_package() -> None:
    with patch(f"{MODULE}.is_requests_available", lambda: True):
        check_requests()


def test_check_requests_without_package() -> None:
    with (
        patch(f"{MODULE}.is_requests_available", lambda: False),
        pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."),
    ):
        check_requests()


def test_is_requests_available() -> None:
    assert isinstance(is_requests_available(), bool)


def test_requests_available_with_package() -> None:
    with patch(f"{MODULE}.is_requests_available", lambda: True):
        fn = requests_available(my_function)
        assert fn(2) == 44


def test_requests_available_without_package() -> None:
    with patch(f"{MODULE}.is_requests_available", lambda: False):
        fn = requests_available(my_function)
        assert fn(2) is None


def test_requests_available_decorator_with_package() -> None:
    with patch(f"{MODULE}.is_requests_available", lambda: True):

        @requests_available
        def fn(n: int = 0) -> int:
            return 42 + n

        assert fn(2) == 44


def test_requests_available_decorator_without_package() -> None:
    with patch(f"{MODULE}.is_requests_available", lambda: False):

        @requests_available
        def fn(n: int = 0) -> int:
            return 42 + n

        assert fn(2) is None


def test_raise_requests_missing_error() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        raise_requests_missing_error()
