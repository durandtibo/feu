r"""Contain functions to manage package versions."""

from __future__ import annotations

__all__ = [
    "PackageBounds",
    "PypiFile",
    "PypiProject",
    "VersionRequest",
    "compare_version",
    "fetch_latest_major_versions_map",
    "fetch_latest_minor_versions_map",
    "fetch_latest_stable_version",
    "fetch_latest_version",
    "fetch_latest_versions",
    "fetch_package_versions",
    "fetch_pypi_pinned_dependency_version",
    "fetch_pypi_project",
    "fetch_pypi_requires_python",
    "fetch_pypi_versions",
    "fetch_pypi_wheel_filenames",
    "fetch_versions",
    "filter_every_n_versions",
    "filter_last_n_versions",
    "filter_range_versions",
    "filter_stable_versions",
    "filter_valid_versions",
    "get_package_bounds",
    "get_package_version",
    "latest_major_versions",
    "latest_minor_versions",
    "latest_version",
    "parse_version_request",
    "partition_package_bounds",
    "read_pyproject_bounds",
    "read_pyproject_dependencies",
    "read_pyproject_optional_dependencies",
    "read_pyproject_package_bounds",
    "sort_versions",
    "unique_versions",
]

from feu.version.bound import (
    PackageBounds,
    get_package_bounds,
    partition_package_bounds,
)
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
    fetch_latest_major_versions_map,
    fetch_latest_minor_versions_map,
    fetch_latest_stable_version,
    fetch_latest_version,
    fetch_latest_versions,
    fetch_package_versions,
    fetch_versions,
)
from feu.version.pypi import (
    PypiFile,
    PypiProject,
    fetch_pypi_pinned_dependency_version,
    fetch_pypi_project,
    fetch_pypi_requires_python,
    fetch_pypi_versions,
    fetch_pypi_wheel_filenames,
)
from feu.version.pyproject import (
    read_pyproject_bounds,
    read_pyproject_dependencies,
    read_pyproject_optional_dependencies,
    read_pyproject_package_bounds,
)
from feu.version.request import VersionRequest, parse_version_request
from feu.version.runtime import get_package_version
