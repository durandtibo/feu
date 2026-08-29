from __future__ import annotations

import pytest

from feu.compat.packages import get_package_names

#############################################
#     Tests for get_package_names            #
#############################################


def test_get_package_names_returns_list() -> None:
    assert isinstance(get_package_names(), list)


EXPECTED_PACKAGES = [
    "bokeh",
    "click",
    "duckdb",
    "jax",
    "matplotlib",
    "numpy",
    "pandas",
    "polars",
    "pyarrow",
    "pydantic",
    "requests",
    "safetensors",
    "scikit-learn",
    "scipy",
    "torch",
    "xarray",
    "xy",
]


@pytest.mark.parametrize("package", EXPECTED_PACKAGES)
def test_get_package_names_contains_expected_packages(package: str) -> None:
    assert package in get_package_names()


def test_get_package_names_length_at_least_expected() -> None:
    assert len(get_package_names()) >= len(EXPECTED_PACKAGES)


def test_get_package_names_no_duplicates() -> None:
    names = get_package_names()
    assert len(names) == len(set(names))


def test_get_package_names_all_strings() -> None:
    assert all(isinstance(name, str) for name in get_package_names())
