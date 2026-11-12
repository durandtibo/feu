r"""Contain functions to read package version bounds from a
``pyproject.toml`` file."""

from __future__ import annotations

__all__ = [
    "read_pyproject_bounds",
    "read_pyproject_dependencies",
    "read_pyproject_optional_dependencies",
    "read_pyproject_package_bounds",
]

import tomllib
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

from feu.version.bound import PackageBounds


def read_pyproject_bounds(path: str | Path, *, package: str | None = None) -> list[PackageBounds]:
    """Read a ``pyproject.toml`` file and return the version bounds of
    its dependencies.

    The file is parsed once. The following standard sections are read,
    in this order:

    - ``[project.dependencies]``
    - ``[project.optional-dependencies.*]``
    - ``[dependency-groups.*]`` (the ``{include-group = ...}`` entries
      of PEP 735 are skipped)

    The names of the returned bounds are canonical (PEP 503).

    Args:
        path: Path to the ``pyproject.toml`` file.
        package: If specified, only the occurrences of this package are
            returned. The comparison uses the canonical names, so it
            is case-insensitive and treats hyphens, underscores and
            dots as equivalent.

    Returns:
        A list of ``PackageBounds`` instances, one per occurrence in
            the sections above. The ``section`` field gives the
            section, e.g. ``'project.optional-dependencies.dev'``.

    Raises:
        FileNotFoundError: If the file does not exist.
        tomllib.TOMLDecodeError: If the file is not valid TOML.

    Example:
        ```python
        bounds = read_pyproject_bounds("pyproject.toml", package="numpy")
        for b in bounds:
            print(b.section, b.lower, b.upper)
        ```
    """
    path = Path(path)
    with path.open("rb") as f:
        data = tomllib.load(f)

    entries: list[tuple[str, str]] = [
        ("project.dependencies", spec) for spec in data.get("project", {}).get("dependencies", [])
    ]
    for group, specs in data.get("project", {}).get("optional-dependencies", {}).items():
        entries.extend((f"project.optional-dependencies.{group}", spec) for spec in specs)
    for group, group_entries in data.get("dependency-groups", {}).items():
        # Skip {include-group = "..."} dicts (PEP 735)
        entries.extend(
            (f"dependency-groups.{group}", entry)
            for entry in group_entries
            if isinstance(entry, str)
        )

    bounds = [_parse_bounds_from_spec(spec, section) for section, spec in entries]
    if package is None:
        return bounds
    name = canonicalize_name(package)
    return [b for b in bounds if b.name == name]


def read_pyproject_dependencies(path: str | Path) -> list[PackageBounds]:
    """Read a ``pyproject.toml`` file and return the bounds for all
    packages defined in ``[project.dependencies]``.

    This function is kept for the scripts that copy
    ``dev/generate_versions.py``; use ``read_pyproject_bounds`` in new
    code.

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
    return [b for b in read_pyproject_bounds(path) if b.section == "project.dependencies"]


def read_pyproject_optional_dependencies(path: str | Path) -> list[PackageBounds]:
    """Read a ``pyproject.toml`` file and return the bounds for all
    packages defined in ``[project.optional-dependencies]``.

    All groups under ``[project.optional-dependencies]`` are included. The
    ``section`` field of each returned ``PackageBounds`` identifies the group,
    e.g. ``'project.optional-dependencies.dev'``.

    This function is kept for the scripts that copy
    ``dev/generate_versions.py``; use ``read_pyproject_bounds`` in new
    code.

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
    return [
        b
        for b in read_pyproject_bounds(path)
        if b.section.startswith("project.optional-dependencies.")
    ]


def read_pyproject_package_bounds(path: str | Path, package: str) -> list[PackageBounds]:
    """Read a ``pyproject.toml`` file and return the version bounds for
    a package.

    This is ``read_pyproject_bounds(path, package=package)``, kept for
    the existing callers.

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
        bounds = read_pyproject_package_bounds("pyproject.toml", "numpy")
        for b in bounds:
            print(b.section, b.lower, b.upper)
        ```
    """
    return read_pyproject_bounds(path, package=package)


def _parse_bounds_from_spec(spec: str, section: str) -> PackageBounds:
    """Parse a PEP 508 dependency specifier and return its bounds.

    Only the first lower (``>=``, ``>``) and the first upper (``<``,
    ``<=``) bound of the specifier are kept; other operators are
    ignored.

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
    return PackageBounds(
        name=canonicalize_name(req.name), lower=lower, upper=upper, section=section
    )
