r"""Utilities for reading package version bounds from pyproject.toml."""

from __future__ import annotations

__all__ = ["PackageBounds", "read_pyproject_package_bounds"]

import sys
from dataclasses import dataclass
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib

from packaging.requirements import Requirement


@dataclass(frozen=True)
class PackageBounds:
    """Lower and upper version bounds for a package dependency.

    Attributes:
        name: The canonical package name as declared in the dependency
            specifier.
        lower: The lower bound version string (from ``>=`` or ``>``
            specifiers), or ``None`` if no lower bound is declared.
        upper: The upper bound version string (from ``<`` or ``<=``
            specifiers), or ``None`` if no upper bound is declared.
        section: The ``pyproject.toml`` section where the dependency
            was found (e.g. ``'project.dependencies'``,
            ``'project.optional-dependencies.dev'``,
            ``'dependency-groups.dev'``).
    """

    name: str
    lower: str | None
    upper: str | None
    section: str


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
    req = Requirement(spec)
    if _normalize_name(req.name) != normalized_package:
        return None

    lower = next(
        (s.version for s in req.specifier if s.operator in (">=", ">")),
        None,
    )
    upper = next(
        (s.version for s in req.specifier if s.operator in ("<", "<=")),
        None,
    )
    return PackageBounds(name=req.name, lower=lower, upper=upper, section=section)
