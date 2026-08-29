from __future__ import annotations

from pathlib import Path

import pytest

from feu.version.pyproject import (
    read_pyproject_dependencies,
    read_pyproject_optional_dependencies,
    read_pyproject_package_bounds,
)

# These tests read this project's own real pyproject.toml file, so they
# exercise the TOML-parsing logic against a live, evolving file rather than
# a synthetic fixture. Assertions target entries that are unlikely to
# disappear, to stay resilient to routine dependency updates.

PYPROJECT_PATH = Path(__file__).resolve().parents[3] / "pyproject.toml"


@pytest.fixture(scope="module", autouse=True)
def _check_pyproject_exists() -> None:
    assert PYPROJECT_PATH.is_file(), f"pyproject.toml not found at {PYPROJECT_PATH}"


###############################################
#     Tests for read_pyproject_dependencies     #
###############################################


def test_read_pyproject_dependencies() -> None:
    bounds = read_pyproject_dependencies(PYPROJECT_PATH)
    names = {b.name for b in bounds}
    assert "packaging" in names
    packaging_bounds = next(b for b in bounds if b.name == "packaging")
    assert packaging_bounds.section == "project.dependencies"
    assert packaging_bounds.lower is not None
    assert packaging_bounds.upper is not None


########################################################
#     Tests for read_pyproject_optional_dependencies     #
########################################################


def test_read_pyproject_optional_dependencies() -> None:
    bounds = read_pyproject_optional_dependencies(PYPROJECT_PATH)
    sections = {b.section for b in bounds}
    assert "project.optional-dependencies.requests" in sections
    names = {b.name for b in bounds if b.section == "project.optional-dependencies.requests"}
    assert names == {"requests", "urllib3"}


#################################################
#     Tests for read_pyproject_package_bounds     #
#################################################


def test_read_pyproject_package_bounds_project_dependencies() -> None:
    bounds = read_pyproject_package_bounds(PYPROJECT_PATH, "packaging")
    assert len(bounds) == 1
    assert bounds[0].section == "project.dependencies"


def test_read_pyproject_package_bounds_optional_dependencies() -> None:
    bounds = read_pyproject_package_bounds(PYPROJECT_PATH, "requests")
    assert len(bounds) == 1
    assert bounds[0].section == "project.optional-dependencies.requests"


def test_read_pyproject_package_bounds_dependency_groups() -> None:
    bounds = read_pyproject_package_bounds(PYPROJECT_PATH, "pytest")
    assert len(bounds) == 1
    assert bounds[0].section == "dependency-groups.dev"


def test_read_pyproject_package_bounds_name_normalization() -> None:
    # PEP 508 normalization treats hyphens and underscores as equivalent
    # and is case-insensitive.
    assert read_pyproject_package_bounds(
        PYPROJECT_PATH, "Packaging"
    ) == read_pyproject_package_bounds(PYPROJECT_PATH, "packaging")


def test_read_pyproject_package_bounds_not_found() -> None:
    assert read_pyproject_package_bounds(PYPROJECT_PATH, "not-a-real-package") == []


def test_read_pyproject_package_bounds_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        read_pyproject_package_bounds(PYPROJECT_PATH.parent / "does_not_exist.toml", "packaging")
