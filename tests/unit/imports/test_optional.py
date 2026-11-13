from __future__ import annotations

from unittest.mock import patch

import pytest

from feu.imports import (
    MissingPackageError,
    check_click,
    check_git,
    check_requests,
    check_rich,
    clear_availability_caches,
    is_click_available,
    is_git_available,
    is_requests_available,
    is_rich_available,
)


@pytest.fixture(autouse=True)
def _reset() -> None:
    clear_availability_caches()


@pytest.mark.parametrize(
    ("is_available", "module"),
    [
        (is_click_available, "click"),
        (is_git_available, "git"),
        (is_requests_available, "requests"),
        (is_rich_available, "rich"),
    ],
)
def test_is_available_uses_module_available(is_available: object, module: str) -> None:
    with patch("feu.imports.optional.module_available", return_value=True) as available_mock:
        assert is_available()  # ty: ignore[not-callable]
        available_mock.assert_called_once_with(module)


@pytest.mark.parametrize(
    "is_available",
    [is_click_available, is_git_available, is_requests_available, is_rich_available],
)
def test_is_available_false_when_the_module_is_broken(is_available: object) -> None:
    with patch("feu.imports.optional.module_available", return_value=False):
        assert not is_available()  # ty: ignore[not-callable]


@pytest.mark.parametrize(
    ("check", "name"),
    [
        (check_click, "click"),
        (check_git, "git"),
        (check_requests, "requests"),
        (check_rich, "rich"),
    ],
)
def test_check_without_package(check: object, name: str) -> None:
    with (
        patch("feu.imports.optional.module_available", return_value=False),
        pytest.raises(MissingPackageError, match=f"'{name}' package is required but not installed"),
    ):
        check()  # ty: ignore[not-callable]


def test_check_git_gives_the_gitpython_install_command() -> None:
    with (
        patch("feu.imports.optional.module_available", return_value=False),
        pytest.raises(MissingPackageError, match="pip install gitpython"),
    ):
        check_git()


@pytest.mark.parametrize("check", [check_click, check_git, check_requests, check_rich])
def test_check_with_package(check: object) -> None:
    with patch("feu.imports.optional.module_available", return_value=True):
        check()  # ty: ignore[not-callable]


def test_check_without_package_is_still_a_runtime_error() -> None:
    with (
        patch("feu.imports.optional.module_available", return_value=False),
        pytest.raises(RuntimeError, match="'requests' package is required"),
    ):
        check_requests()


def test_check_without_package_is_an_import_error() -> None:
    with (
        patch("feu.imports.optional.module_available", return_value=False),
        pytest.raises(ImportError, match="'requests' package is required"),
    ):
        check_requests()
