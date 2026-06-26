r"""Utilities for reading package version bounds from pyproject.toml."""

from __future__ import annotations

__all__ = [
    "read_pyproject_dependencies",
    "read_pyproject_optional_dependencies",
    "read_pyproject_package_bounds",
]

import sys
from pathlib import Path

from feu.version.bound import PackageBounds

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib

from packaging.requirements import Requirement


def read_pyproject_dependencies(path: str | Path) -> list[PackageBounds]:
    """Read a ``pyproject.toml`` file and return the bounds for all
    packages defined in ``[project.dependencies]``.

    Args:
        path: Path to the ``pyproject.toml`` file.

    Returns:
        A list of ``PackageBounds`` instances, one per entry in
        ``[project.dependencies]``. Returns an empty list if the section
        is absent or empty.

    Raises:
        FileNotFoundError: If the file does not exist.
        tomllib.TOMLDecodeError: If the file is not valid TOML.

    Example:
        ```python
        bounds = read_pyproject_dependencies("pyproject.toml")
        for b in bounds:
            print(b.name, b.lower, b.upper)
        ```
    """
    path = Path(path)
    with path.open("rb") as f:
        data = tomllib.load(f)

    return [
        bounds
        for spec in data.get("project", {}).get("dependencies", [])
        if (bounds := _parse_bounds_from_spec(spec, "project.dependencies")) is not None
    ]


def read_pyproject_optional_dependencies(path: str | Path) -> list[PackageBounds]:
    """Read a ``pyproject.toml`` file and return the bounds for all
    packages defined in ``[project.optional-dependencies]``.

    All groups under ``[project.optional-dependencies]`` are included. The
    ``section`` field of each returned ``PackageBounds`` identifies the group,
    e.g. ``'project.optional-dependencies.dev'``.

    Args:
        path: Path to the ``pyproject.toml`` file.

    Returns:
        A list of ``PackageBounds`` instances, one per entry across all
        optional-dependency groups, in the order they appear in the file.
        Returns an empty list if the section is absent or empty.

    Raises:
        FileNotFoundError: If the file does not exist.
        tomllib.TOMLDecodeError: If the file is not valid TOML.

    Example:
        ```python
        bounds = read_pyproject_optional_dependencies("pyproject.toml")
        for b in bounds:
            print(b.name, b.section, b.lower, b.upper)
        ```
    """
    path = Path(path)
    with path.open("rb") as f:
        data = tomllib.load(f)

    return [
        bounds
        for group, specs in data.get("project", {}).get("optional-dependencies", {}).items()
        for spec in specs
        if (bounds := _parse_bounds_from_spec(spec, f"project.optional-dependencies.{group}"))
        is not None
    ]


def read_pyproject_package_bounds(
    path: str | Path,
    package: str,
) -> list[PackageBounds]:
    """Read a ``pyproject.toml`` file and return the version bounds for
    a package.

    Searches the following standard sections:

    - ``[project.dependencies]``
    - ``[project.optional-dependencies.*]``
    - ``[dependency-groups.*]``

    The package name comparison is case-insensitive and treats hyphens
    and underscores as equivalent, following PEP 508 normalisation rules.

    Args:
        path: Path to the ``pyproject.toml`` file.
        package: The name of the package to look up.

    Returns:
        A list of ``PackageBounds`` instances, one per occurrence of the
        package across all sections. Returns an empty list if the package
        is not found.

    Raises:
        FileNotFoundError: If the file does not exist.
        tomllib.TOMLDecodeError: If the file is not valid TOML.

    Example:
        ```python
        bounds = find_package_bounds("pyproject.toml", "numpy")
        for b in bounds:
            print(b.section, b.lower, b.upper)
        ```
    """
    path = Path(path)
    with path.open("rb") as f:
        data = tomllib.load(f)

    normalized_package = _normalize_name(package)
    results: list[PackageBounds] = []

    # [project.dependencies]
    for spec in data.get("project", {}).get("dependencies", []):
        bounds = _parse_bounds(spec, normalized_package, "project.dependencies")
        if bounds is not None:
            results.append(bounds)

    # [project.optional-dependencies.*]
    for group, specs in data.get("project", {}).get("optional-dependencies", {}).items():
        for spec in specs:
            bounds = _parse_bounds(
                spec, normalized_package, f"project.optional-dependencies.{group}"
            )
            if bounds is not None:
                results.append(bounds)

    # [dependency-groups.*]
    for group, entries in data.get("dependency-groups", {}).items():
        for entry in entries:
            if not isinstance(entry, str):
                # Skip {include-group = "..."} dicts (PEP 735)
                continue
            bounds = _parse_bounds(entry, normalized_package, f"dependency-groups.{group}")
            if bounds is not None:
                results.append(bounds)

    return results


def _normalize_name(name: str) -> str:
    """Normalize a package name per PEP 508 (lowercase, hyphens to
    underscores)."""
    return name.lower().replace("-", "_")


def _parse_bounds_from_spec(spec: str, section: str) -> PackageBounds:
    """Parse a PEP 508 dependency specifier and return its bounds.

    Args:
        spec: A PEP 508 dependency specifier string.
        section: The section label to include in the returned ``PackageBounds``.

    Returns:
        A ``PackageBounds`` instance for the given specifier.
    """
    req = Requirement(spec)
    lower = next(
        (s.version for s in req.specifier if s.operator in (">=", ">")),
        None,
    )
    upper = next(
        (s.version for s in req.specifier if s.operator in ("<", "<=")),
        None,
    )
    return PackageBounds(name=req.name, lower=lower, upper=upper, section=section)


def _parse_bounds(
    spec: str,
    normalized_package: str,
    section: str,
) -> PackageBounds | None:
    """Parse a PEP 508 dependency specifier and return bounds if it
    matches the package.

    Args:
        spec: A PEP 508 dependency specifier string.
        normalized_package: The normalized package name to match against.
        section: The section label to include in the returned ``PackageBounds``.

    Returns:
        A ``PackageBounds`` instance if the specifier matches the package,
        ``None`` otherwise.
    """
    bounds = _parse_bounds_from_spec(spec, section)
    return bounds if _normalize_name(bounds.name) == normalized_package else None
