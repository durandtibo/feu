r"""Unit tests for pyproject_utils."""

from __future__ import annotations

import sys
from dataclasses import FrozenInstanceError
from typing import TYPE_CHECKING

import pytest

from feu.testing import tomllib_or_tomli_available
from feu.utils.imports import is_tomli_available
from feu.version import PackageBounds, read_pyproject_package_bounds

if TYPE_CHECKING:
    from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
elif is_tomli_available():  # pragma: no cover
    import tomli as tomllib


@pytest.fixture
def pyproject(tmp_path: Path) -> Path:
    """Write a sample pyproject.toml covering all three sections."""
    content = """\
[project]
name = "myproject"
dependencies = [
    "numpy>=1.21,<2.0",
    "torch>=2.0",
    "requests",
    "coola[all]>=0.1,<1.0",
    "scikit-learn>=1.0,<2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0,<9.0",
    "numpy>=1.24",
]
extra = [
    "scipy>=1.0",
]

[dependency-groups]
dev = [
    "mypy>=1.0,<2.0",
    {include-group = "test"},
    "numpy<3.0",
]
lint = [
    "ruff>=0.1",
]
"""
    path = tmp_path / "pyproject.toml"
    path.write_text(content)
    return path


@pytest.fixture
def pyproject_minimal(tmp_path: Path) -> Path:
    """Write a minimal pyproject.toml with no dependencies."""
    content = """\
[project]
name = "myproject"
"""
    path = tmp_path / "pyproject.toml"
    path.write_text(content)
    return path


#####################################
#     Tests for PackageBounds       #
#####################################


def test_package_bounds_equal() -> None:
    assert PackageBounds(
        name="numpy", lower="1.21", upper="2.0", section="project.dependencies"
    ) == PackageBounds(name="numpy", lower="1.21", upper="2.0", section="project.dependencies")


def test_package_bounds_not_equal_different_lower() -> None:
    assert PackageBounds(
        name="numpy", lower="1.21", upper="2.0", section="project.dependencies"
    ) != PackageBounds(name="numpy", lower="1.22", upper="2.0", section="project.dependencies")


def test_package_bounds_not_equal_different_upper() -> None:
    assert PackageBounds(
        name="numpy", lower="1.21", upper="2.0", section="project.dependencies"
    ) != PackageBounds(name="numpy", lower="1.21", upper="3.0", section="project.dependencies")


def test_package_bounds_not_equal_different_section() -> None:
    assert PackageBounds(
        name="numpy", lower="1.21", upper="2.0", section="project.dependencies"
    ) != PackageBounds(name="numpy", lower="1.21", upper="2.0", section="dependency-groups.dev")


def test_package_bounds_is_immutable() -> None:
    bounds = PackageBounds(name="numpy", lower="1.21", upper="2.0", section="project.dependencies")
    with pytest.raises(FrozenInstanceError, match=r"cannot assign to field 'lower'"):
        bounds.lower = "1.0"  # type: ignore[misc]


###################################################
#     Tests for read_pyproject_package_bounds     #
###################################################


# --- project.dependencies ---


@tomllib_or_tomli_available
def test_read_pyproject_package_bounds_project_dependencies_lower_and_upper(
    pyproject: Path,
) -> None:
    assert read_pyproject_package_bounds(pyproject, "numpy") == [
        PackageBounds(name="numpy", lower="1.21", upper="2.0", section="project.dependencies"),
        PackageBounds(
            name="numpy", lower="1.24", upper=None, section="project.optional-dependencies.dev"
        ),
        PackageBounds(name="numpy", lower=None, upper="3.0", section="dependency-groups.dev"),
    ]


@tomllib_or_tomli_available
def test_read_pyproject_package_bounds_project_dependencies_lower_only(
    pyproject: Path,
) -> None:
    assert read_pyproject_package_bounds(pyproject, "torch") == [
        PackageBounds(name="torch", lower="2.0", upper=None, section="project.dependencies"),
    ]


@tomllib_or_tomli_available
def test_read_pyproject_package_bounds_project_dependencies_no_bounds(
    pyproject: Path,
) -> None:
    assert read_pyproject_package_bounds(pyproject, "requests") == [
        PackageBounds(name="requests", lower=None, upper=None, section="project.dependencies"),
    ]


@tomllib_or_tomli_available
def test_read_pyproject_package_bounds_project_dependencies_with_extras(
    pyproject: Path,
) -> None:
    # coola[all]>=0.1,<1.0 — extras are ignored, name is still 'coola'
    assert read_pyproject_package_bounds(pyproject, "coola") == [
        PackageBounds(name="coola", lower="0.1", upper="1.0", section="project.dependencies"),
    ]


# --- project.optional-dependencies ---


@tomllib_or_tomli_available
def test_read_pyproject_package_bounds_optional_dependencies(pyproject: Path) -> None:
    assert read_pyproject_package_bounds(pyproject, "pytest") == [
        PackageBounds(
            name="pytest", lower="7.0", upper="9.0", section="project.optional-dependencies.dev"
        ),
    ]


@tomllib_or_tomli_available
def test_read_pyproject_package_bounds_optional_dependencies_lower_only(
    pyproject: Path,
) -> None:
    assert read_pyproject_package_bounds(pyproject, "scipy") == [
        PackageBounds(
            name="scipy", lower="1.0", upper=None, section="project.optional-dependencies.extra"
        ),
    ]


# --- dependency-groups ---


@tomllib_or_tomli_available
def test_read_pyproject_package_bounds_dependency_groups(pyproject: Path) -> None:
    assert read_pyproject_package_bounds(pyproject, "mypy") == [
        PackageBounds(name="mypy", lower="1.0", upper="2.0", section="dependency-groups.dev"),
    ]


@tomllib_or_tomli_available
def test_read_pyproject_package_bounds_dependency_groups_skips_include_group(
    pyproject: Path,
) -> None:
    # {include-group = "test"} should not raise and should not appear in results.
    assert read_pyproject_package_bounds(pyproject, "test") == []


@tomllib_or_tomli_available
def test_read_pyproject_package_bounds_dependency_groups_lower_only(
    pyproject: Path,
) -> None:
    assert read_pyproject_package_bounds(pyproject, "ruff") == [
        PackageBounds(name="ruff", lower="0.1", upper=None, section="dependency-groups.lint"),
    ]


# --- name normalisation ---


@tomllib_or_tomli_available
def test_read_pyproject_package_bounds_case_insensitive(pyproject: Path) -> None:
    assert read_pyproject_package_bounds(pyproject, "numpy") == read_pyproject_package_bounds(
        pyproject, "NumPy"
    )


@tomllib_or_tomli_available
def test_read_pyproject_package_bounds_hyphen_underscore_equivalent(
    pyproject: Path,
) -> None:
    assert read_pyproject_package_bounds(
        pyproject, "scikit-learn"
    ) == read_pyproject_package_bounds(pyproject, "scikit_learn")


# --- not found ---


@tomllib_or_tomli_available
def test_read_pyproject_package_bounds_package_not_found_returns_empty_list(
    pyproject: Path,
) -> None:
    assert read_pyproject_package_bounds(pyproject, "nonexistent") == []


# --- accepts str and Path ---


@tomllib_or_tomli_available
def test_read_pyproject_package_bounds_accepts_str_path(pyproject: Path) -> None:
    assert read_pyproject_package_bounds(str(pyproject), "torch") == read_pyproject_package_bounds(
        pyproject, "torch"
    )


@tomllib_or_tomli_available
def test_read_pyproject_package_bounds_accepts_path_object(pyproject: Path) -> None:
    assert read_pyproject_package_bounds(pyproject, "torch") == [
        PackageBounds(name="torch", lower="2.0", upper=None, section="project.dependencies"),
    ]


# --- error handling ---


@tomllib_or_tomli_available
def test_read_pyproject_package_bounds_file_not_found(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="No such file or directory"):
        read_pyproject_package_bounds(tmp_path / "missing.toml", "numpy")


@tomllib_or_tomli_available
def test_read_pyproject_package_bounds_invalid_toml(tmp_path: Path) -> None:
    path = tmp_path / "pyproject.toml"
    path.write_text("this is not : valid [ toml")
    with pytest.raises(tomllib.TOMLDecodeError):
        read_pyproject_package_bounds(path, "numpy")


# --- minimal file ---


@tomllib_or_tomli_available
def test_read_pyproject_package_bounds_minimal_file_returns_empty_list(
    pyproject_minimal: Path,
) -> None:
    assert read_pyproject_package_bounds(pyproject_minimal, "numpy") == []
