from __future__ import annotations

import logging
from unittest.mock import patch

import pytest

from feu.imports import (
    check_click,
    click_available,
    is_click_available,
    raise_click_missing_error,
)

logger = logging.getLogger(__name__)

MODULE = "feu.imports.click"


@pytest.fixture(autouse=True)
def _cache_clear() -> None:
    is_click_available.cache_clear()


def my_function(n: int = 0) -> int:
    return 42 + n


#################
#     click     #
#################


def test_check_click_with_package() -> None:
    with patch(f"{MODULE}.is_click_available", lambda: True):
        check_click()


def test_check_click_without_package() -> None:
    with (
        patch(f"{MODULE}.is_click_available", lambda: False),
        pytest.raises(RuntimeError, match=r"'click' package is required but not installed."),
    ):
        check_click()


def test_is_click_available() -> None:
    assert isinstance(is_click_available(), bool)


def test_click_available_with_package() -> None:
    with patch(f"{MODULE}.is_click_available", lambda: True):
        fn = click_available(my_function)
        assert fn(2) == 44


def test_click_available_without_package() -> None:
    with patch(f"{MODULE}.is_click_available", lambda: False):
        fn = click_available(my_function)
        assert fn(2) is None


def test_click_available_decorator_with_package() -> None:
    with patch(f"{MODULE}.is_click_available", lambda: True):

        @click_available
        def fn(n: int = 0) -> int:
            return 42 + n

        assert fn(2) == 44


def test_click_available_decorator_without_package() -> None:
    with patch(f"{MODULE}.is_click_available", lambda: False):

        @click_available
        def fn(n: int = 0) -> int:
            return 42 + n

        assert fn(2) is None


def test_raise_click_missing_error() -> None:
    with pytest.raises(RuntimeError, match=r"'click' package is required but not installed."):
        raise_click_missing_error()
