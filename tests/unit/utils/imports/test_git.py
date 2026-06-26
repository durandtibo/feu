from __future__ import annotations

import logging
from unittest.mock import patch

import pytest

from feu.utils.imports import (
    check_git,
    git_available,
    is_git_available,
    raise_git_missing_error,
)

logger = logging.getLogger(__name__)

MODULE = "feu.utils.imports.git"


@pytest.fixture(autouse=True)
def _cache_clear() -> None:
    is_git_available.cache_clear()


def my_function(n: int = 0) -> int:
    return 42 + n


###############
#     git     #
###############


def test_check_git_with_package() -> None:
    with patch(f"{MODULE}.is_git_available", lambda: True):
        check_git()


def test_check_git_without_package() -> None:
    with (
        patch(f"{MODULE}.is_git_available", lambda: False),
        pytest.raises(RuntimeError, match=r"'git' package is required but not installed."),
    ):
        check_git()


def test_is_git_available() -> None:
    assert isinstance(is_git_available(), bool)


def test_git_available_with_package() -> None:
    with patch(f"{MODULE}.is_git_available", lambda: True):
        fn = git_available(my_function)
        assert fn(2) == 44


def test_git_available_without_package() -> None:
    with patch(f"{MODULE}.is_git_available", lambda: False):
        fn = git_available(my_function)
        assert fn(2) is None


def test_git_available_decorator_with_package() -> None:
    with patch(f"{MODULE}.is_git_available", lambda: True):

        @git_available
        def fn(n: int = 0) -> int:
            return 42 + n

        assert fn(2) == 44


def test_git_available_decorator_without_package() -> None:
    with patch(f"{MODULE}.is_git_available", lambda: False):

        @git_available
        def fn(n: int = 0) -> int:
            return 42 + n

        assert fn(2) is None


def test_raise_git_missing_error() -> None:
    with pytest.raises(RuntimeError, match=r"'git' package is required but not installed."):
        raise_git_missing_error()
