from __future__ import annotations

import pytest

from feu.testing import (
    click_available,
    click_not_available,
    git_available,
    git_not_available,
    jax_available,
    matplotlib_available,
    numpy_available,
    pandas_available,
    pip_available,
    pipx_available,
    polars_available,
    pyarrow_available,
    requests_available,
    requests_not_available,
    scipy_available,
    sklearn_available,
    torch_available,
    urllib3_available,
    urllib3_not_available,
    uv_available,
    xarray_available,
)

##########################################
#     Tests for click_available         #
##########################################


def test_click_available_is_mark_decorator() -> None:
    assert isinstance(click_available, pytest.MarkDecorator)


def test_click_not_available_is_mark_decorator() -> None:
    assert isinstance(click_not_available, pytest.MarkDecorator)


#######################################
#     Tests for git_available        #
#######################################


def test_git_available_is_mark_decorator() -> None:
    assert isinstance(git_available, pytest.MarkDecorator)


def test_git_not_available_is_mark_decorator() -> None:
    assert isinstance(git_not_available, pytest.MarkDecorator)


#############################################
#     Tests for package availability       #
#############################################


def test_jax_available_is_mark_decorator() -> None:
    assert isinstance(jax_available, pytest.MarkDecorator)


def test_matplotlib_available_is_mark_decorator() -> None:
    assert isinstance(matplotlib_available, pytest.MarkDecorator)


def test_numpy_available_is_mark_decorator() -> None:
    assert isinstance(numpy_available, pytest.MarkDecorator)


def test_pandas_available_is_mark_decorator() -> None:
    assert isinstance(pandas_available, pytest.MarkDecorator)


def test_polars_available_is_mark_decorator() -> None:
    assert isinstance(polars_available, pytest.MarkDecorator)


def test_pyarrow_available_is_mark_decorator() -> None:
    assert isinstance(pyarrow_available, pytest.MarkDecorator)


def test_scipy_available_is_mark_decorator() -> None:
    assert isinstance(scipy_available, pytest.MarkDecorator)


def test_sklearn_available_is_mark_decorator() -> None:
    assert isinstance(sklearn_available, pytest.MarkDecorator)


def test_torch_available_is_mark_decorator() -> None:
    assert isinstance(torch_available, pytest.MarkDecorator)


def test_xarray_available_is_mark_decorator() -> None:
    assert isinstance(xarray_available, pytest.MarkDecorator)


###########################################
#     Tests for requests_available       #
###########################################


def test_requests_available_is_mark_decorator() -> None:
    assert isinstance(requests_available, pytest.MarkDecorator)


def test_requests_not_available_is_mark_decorator() -> None:
    assert isinstance(requests_not_available, pytest.MarkDecorator)


###########################################
#     Tests for urllib3_available        #
###########################################


def test_urllib3_available_is_mark_decorator() -> None:
    assert isinstance(urllib3_available, pytest.MarkDecorator)


def test_urllib3_not_available_is_mark_decorator() -> None:
    assert isinstance(urllib3_not_available, pytest.MarkDecorator)


################################################
#     Tests for installer availability        #
################################################


def test_pip_available_is_mark_decorator() -> None:
    assert isinstance(pip_available, pytest.MarkDecorator)


def test_pipx_available_is_mark_decorator() -> None:
    assert isinstance(pipx_available, pytest.MarkDecorator)


def test_uv_available_is_mark_decorator() -> None:
    assert isinstance(uv_available, pytest.MarkDecorator)
