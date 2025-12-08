r"""Contain functions to manage package versions."""

from __future__ import annotations

__all__ = [
    "compare_version",
    "fetch_latest_major_versions",
    "fetch_latest_minor_versions",
    "fetch_latest_stable_version",
    "fetch_latest_version",
    "fetch_pypi_versions",
    "fetch_versions",
    "filter_every_n_versions",
    "filter_last_n_versions",
    "filter_range_versions",
    "filter_stable_versions",
    "filter_valid_versions",
    "get_package_version",
    "get_python_major_minor",
    "latest_major_versions",
    "latest_minor_versions",
    "latest_version",
    "sort_versions",
    "unique_versions",
]

from feu.version.comparison import compare_version, latest_version, sort_versions
from feu.version.filtering import (
    filter_every_n_versions,
    filter_last_n_versions,
    filter_range_versions,
    filter_stable_versions,
    filter_valid_versions,
    latest_major_versions,
    latest_minor_versions,
    unique_versions,
)
from feu.version.package import (
    fetch_latest_major_versions,
    fetch_latest_minor_versions,
    fetch_latest_stable_version,
    fetch_latest_version,
    fetch_versions,
)
from feu.version.pypi import fetch_pypi_versions
from feu.version.runtime import get_package_version, get_python_major_minor
