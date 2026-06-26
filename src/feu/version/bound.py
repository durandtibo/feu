r"""Contains the low and upper bounds for a package dependency."""

from __future__ import annotations

__all__ = [
    "PackageBounds",
    "get_package_bounds",
    "normalize_package_name",
    "partition_package_bounds",
]


from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


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


def get_package_bounds(
    packages: Sequence[PackageBounds],
    name: str,
) -> PackageBounds:
    """Return the first ``PackageBounds`` matching a given package name.

    The name comparison is case-insensitive and treats hyphens and
    underscores as equivalent, following PEP 508 normalisation rules.

    Args:
        packages: A sequence of ``PackageBounds`` instances to search.
        name: The package name to look up.

    Returns:
        The first ``PackageBounds`` whose name matches ``name``.

    Raises:
        ValueError: If no entry matching ``name`` is found in ``packages``.

    Example:
        ```pycon
        >>> from feu.version import PackageBounds, get_package_bounds
        >>> packages = [
        ...     PackageBounds(
        ...         name="numpy", lower="1.21", upper="2.0", section="project.dependencies"
        ...     ),
        ...     PackageBounds(
        ...         name="torch", lower="2.0", upper=None, section="project.dependencies"
        ...     ),
        ... ]
        >>> get_package_bounds(packages, "numpy")
        PackageBounds(name='numpy', lower='1.21', upper='2.0', section='project.dependencies')

        ```
    """
    normalized = normalize_package_name(name)
    for bounds in packages:
        if normalize_package_name(bounds.name) == normalized:
            return bounds
    msg = f"Package {name!r} not found in the provided sequence."
    raise ValueError(msg)


def normalize_package_name(name: str) -> str:
    """Normalize a package name per PEP 508.

    Converts the name to lowercase and replaces hyphens with underscores,
    so that ``"scikit-learn"``, ``"scikit_learn"``, and ``"Scikit_Learn"``
    all compare as equal.

    Args:
        name: The package name to normalize.

    Returns:
        The normalized package name.

    Example:
        ```pycon
        >>> from feu.version import normalize_package_name
        >>> normalize_package_name("Scikit-Learn")
        'scikit_learn'

        ```
    """
    return name.lower().replace("-", "_")


def partition_package_bounds(
    packages: Sequence[PackageBounds],
    names: Sequence[str],
) -> tuple[list[PackageBounds], list[PackageBounds]]:
    """Split a sequence of ``PackageBounds`` into matched and unmatched
    by name.

    Args:
        packages: A sequence of ``PackageBounds`` instances to filter.
        names: The package names to match against.

    Returns:
        A tuple of two lists, both in the order they appear in ``packages``:

        - The first list contains the ``PackageBounds`` instances whose
          name appears in ``names``.
        - The second list contains the ``PackageBounds`` instances whose
          name does not appear in ``names``.

    Example:
        ```pycon
        >>> from feu.version import PackageBounds, partition_package_bounds
        >>> packages = [
        ...     PackageBounds(
        ...         name="numpy", lower="1.21", upper="2.0", section="project.dependencies"
        ...     ),
        ...     PackageBounds(
        ...         name="torch", lower="2.0", upper=None, section="project.dependencies"
        ...     ),
        ... ]
        >>> matched, unmatched = partition_package_bounds(packages, ["numpy"])
        >>> matched
        [PackageBounds(name='numpy', lower='1.21', upper='2.0', section='project.dependencies')]
        >>> unmatched
        [PackageBounds(name='torch', lower='2.0', upper=None, section='project.dependencies')]

        ```
    """
    normalized_names = {normalize_package_name(n) for n in names}
    matched = [p for p in packages if normalize_package_name(p.name) in normalized_names]
    unmatched = [p for p in packages if normalize_package_name(p.name) not in normalized_names]
    return matched, unmatched
