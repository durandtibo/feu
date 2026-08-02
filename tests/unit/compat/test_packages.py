from __future__ import annotations

from feu.compat.defaults import DEFAULT_COMPAT
from feu.compat.packages import get_package_names

#############################################
#     Tests for get_package_names            #
#############################################


def test_get_package_names_returns_list() -> None:
    assert isinstance(get_package_names(), list)


def test_get_package_names_matches_default_compat_keys() -> None:
    assert get_package_names() == list(DEFAULT_COMPAT.keys())


def test_get_package_names_contains_expected_packages() -> None:
    assert set(get_package_names()) == {
        "click",
        "duckdb",
        "jax",
        "matplotlib",
        "numpy",
        "pandas",
        "pyarrow",
        "pydantic",
        "requests",
        "scikit-learn",
        "scipy",
        "torch",
        "xarray",
    }


def test_get_package_names_no_duplicates() -> None:
    names = get_package_names()
    assert len(names) == len(set(names))


def test_get_package_names_all_strings() -> None:
    assert all(isinstance(name, str) for name in get_package_names())
