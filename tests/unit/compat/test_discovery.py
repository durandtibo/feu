from __future__ import annotations

from unittest.mock import patch

from feu.compat.discovery import discover_compat
from feu.compat.registry import UNSUPPORTED


@patch(
    "feu.compat.discovery.fetch_pypi_requires_python",
    lambda *_args: {
        "1.0.0": ">=3.6",
        "1.5.0": ">=3.8",
        "2.0.0": ">=3.9",
        "2.1.0": ">=3.9",
        "2.1.0a1": ">=3.9",  # pre-release, should be ignored
        "not-a-version": ">=3.9",  # invalid, should be ignored
    },
)
def test_discover_compat() -> None:
    compat = discover_compat("my_package", python_versions=("3.8", "3.9", "3.10"))
    assert compat == {
        "3.8": {"min": "1.0.0", "max": "1.5.0"},
        "3.9": {"min": "1.0.0", "max": None},
        "3.10": {"min": "1.0.0", "max": None},
    }


@patch(
    "feu.compat.discovery.fetch_pypi_requires_python",
    lambda *_args: {"1.0.0": ">=3.9", "2.0.0": ">=3.9"},
)
def test_discover_compat_no_compatible_version() -> None:
    compat = discover_compat("my_package", python_versions=("3.7",))
    assert compat == {"3.7": {"min": UNSUPPORTED, "max": UNSUPPORTED}}


@patch(
    "feu.compat.discovery.fetch_pypi_requires_python",
    lambda *_args: {"1.0.0": None, "2.0.0": None},
)
def test_discover_compat_no_requires_python() -> None:
    compat = discover_compat("my_package", python_versions=("3.9",))
    assert compat == {"3.9": {"min": "1.0.0", "max": None}}


@patch(
    "feu.compat.discovery.fetch_pypi_requires_python",
    lambda *_args: {"1.0.0": "invalid specifier!!", "2.0.0": ">=3.9"},
)
def test_discover_compat_invalid_specifier() -> None:
    compat = discover_compat("my_package", python_versions=("3.5",))
    assert compat == {"3.5": {"min": "1.0.0", "max": "1.0.0"}}


@patch("feu.compat.discovery.fetch_pypi_requires_python", lambda *_args: {})
def test_discover_compat_empty() -> None:
    compat = discover_compat("my_package", python_versions=("3.9",))
    assert compat == {"3.9": {"min": UNSUPPORTED, "max": UNSUPPORTED}}


def test_discover_compat_default_python_versions() -> None:
    with patch(
        "feu.compat.discovery.fetch_pypi_requires_python",
        lambda *_args: {"1.0.0": None},
    ):
        compat = discover_compat("my_package")
    assert set(compat.keys()) == {"3.9", "3.10", "3.11", "3.12", "3.13", "3.14", "3.15"}
