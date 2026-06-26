from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from feu.version import PackageBounds

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
