from __future__ import annotations

import pytest

from feu.imports import (
    check_click,
    check_git,
    check_requests,
    check_urllib3,
    is_click_available,
    is_git_available,
    is_requests_available,
    is_urllib3_available,
)
from feu.testing import (
    click_available,
    click_not_available,
    git_available,
    git_not_available,
    requests_available,
    requests_not_available,
    urllib3_available,
    urllib3_not_available,
)

#################
#     click     #
#################


@click_available
def test_check_click_with_package() -> None:
    check_click()


@click_not_available
def test_check_click_without_package() -> None:
    with pytest.raises(RuntimeError, match=r"'click' package is required but not installed."):
        check_click()


@click_available
def test_is_click_available_true() -> None:
    assert is_click_available()


@click_not_available
def test_is_click_available_false() -> None:
    assert not is_click_available()


###############
#     git     #
###############


@git_available
def test_check_git_with_package() -> None:
    check_git()


@git_not_available
def test_check_git_without_package() -> None:
    with pytest.raises(RuntimeError, match=r"'git' package is required but not installed."):
        check_git()


@git_available
def test_is_git_available_true() -> None:
    assert is_git_available()


@git_not_available
def test_is_git_available_false() -> None:
    assert not is_git_available()


####################
#     requests     #
####################


@requests_available
def test_check_requests_with_package() -> None:
    check_requests()


@requests_not_available
def test_check_requests_without_package() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        check_requests()


@requests_available
def test_is_requests_available_true() -> None:
    assert is_requests_available()


@requests_not_available
def test_is_requests_available_false() -> None:
    assert not is_requests_available()


###################
#     urllib3     #
###################


@urllib3_available
def test_check_urllib3_with_package() -> None:
    check_urllib3()


@urllib3_not_available
def test_check_urllib3_without_package() -> None:
    with pytest.raises(RuntimeError, match=r"'urllib3' package is required but not installed."):
        check_urllib3()


@urllib3_available
def test_is_urllib3_available_true() -> None:
    assert is_urllib3_available()


@urllib3_not_available
def test_is_urllib3_available_false() -> None:
    assert not is_urllib3_available()
