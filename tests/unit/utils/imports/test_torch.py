from __future__ import annotations

import logging
from unittest.mock import patch

import pytest

from feu.utils.imports import (
    check_tomli,
    is_tomli_available,
    raise_tomli_missing_error,
    tomli_available,
)

logger = logging.getLogger(__name__)

MODULE = "feu.utils.imports.tomli"


@pytest.fixture(autouse=True)
def _cache_clear() -> None:
    is_tomli_available.cache_clear()


def my_function(n: int = 0) -> int:
    return 42 + n


#################
#     tomli     #
#################


def test_check_tomli_with_package() -> None:
    with patch(f"{MODULE}.is_tomli_available", lambda: True):
        check_tomli()


def test_check_tomli_without_package() -> None:
    with (
        patch(f"{MODULE}.is_tomli_available", lambda: False),
        pytest.raises(RuntimeError, match=r"'tomli' package is required but not installed."),
    ):
        check_tomli()


def test_is_tomli_available() -> None:
    assert isinstance(is_tomli_available(), bool)


def test_tomli_available_with_package() -> None:
    with patch(f"{MODULE}.is_tomli_available", lambda: True):
        fn = tomli_available(my_function)
        assert fn(2) == 44


def test_tomli_available_without_package() -> None:
    with patch(f"{MODULE}.is_tomli_available", lambda: False):
        fn = tomli_available(my_function)
        assert fn(2) is None


def test_tomli_available_decorator_with_package() -> None:
    with patch(f"{MODULE}.is_tomli_available", lambda: True):

        @tomli_available
        def fn(n: int = 0) -> int:
            return 42 + n

        assert fn(2) == 44


def test_tomli_available_decorator_without_package() -> None:
    with patch(f"{MODULE}.is_tomli_available", lambda: False):

        @tomli_available
        def fn(n: int = 0) -> int:
            return 42 + n

        assert fn(2) is None


def test_raise_tomli_missing_error() -> None:
    with pytest.raises(RuntimeError, match=r"'tomli' package is required but not installed."):
        raise_tomli_missing_error()
