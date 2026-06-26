r"""Contains the low and upper bounds for a package dependency."""

from __future__ import annotations

__all__ = ["PackageBounds"]

from dataclasses import dataclass


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
