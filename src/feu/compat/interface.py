r"""Define the public interface for package/target compatibility
resolution."""

from __future__ import annotations

__all__ = [
    "find_closest_version",
    "get_default_registry",
    "is_valid_version",
    "register_compat",
]

from functools import cache
from typing import TYPE_CHECKING

from feu.compat.discovered import register_discovered
from feu.compat.registry import CompatRegistry

if TYPE_CHECKING:
    from feu.compat.registry import VersionRange
    from feu.compat.target import Target


@cache
def get_default_registry() -> CompatRegistry:
    r"""Return the default global compatibility registry.

    The registry is created on the first call and reused on all
    subsequent calls (singleton pattern). It is populated with the
    automatically discovered constraints of ``feu.compat.discovered``.

    Returns:
        A singleton ``CompatRegistry`` configured with the
            discovered package version constraints.

    Example:
        ```pycon
        >>> from feu.compat import get_default_registry, Target
        >>> registry = get_default_registry()
        >>> registry.is_valid_version("numpy", "2.0.2", Target(python_version="3.11"))
        True

        ```
    """
    registry = CompatRegistry()
    register_discovered(registry)
    return registry


def register_compat(
    mapping: dict[str, dict[Target, list[VersionRange]]],
    exist_ok: bool = False,
) -> None:
    r"""Register custom package configurations into the default global
    registry.

    Args:
        mapping: Mapping of package name to ``Target`` to a list of
            ``VersionRange``.
        exist_ok: If ``False`` (default), raises an error if any entry
            is already registered. If ``True``, overwrites existing
            registrations silently.

    Raises:
        RuntimeError: If any entry is already registered and
            ``exist_ok`` is ``False``.

    Example:
        ```pycon
        >>> from feu.compat import register_compat, Target, VersionRange
        >>> register_compat(
        ...     {"my_package": {Target(python_version="3.11"): [VersionRange("1.0.0", None)]}}
        ... )

        ```
    """
    get_default_registry().register_many(mapping, exist_ok=exist_ok)


def find_closest_version(pkg_name: str, pkg_version: str | None, target: Target) -> str:
    r"""Find the closest valid version for a package using the default
    registry.

    Args:
        pkg_name: The package name to check (e.g., ``"numpy"``).
        pkg_version: The requested package version: an exact
            version, a wildcard (e.g. ``"2.*"``) or ``""``/``None``
            for the latest version.
        target: The compatibility target.

    Returns:
        The closest valid version as a string. An exact version is
            returned unchanged if it is valid or if the package is not
            configured for the target. A wildcard or empty request is
            resolved to the latest compatible version, or returned
            unchanged if it lies in an open-ended range (see
            ``CompatRegistry.find_closest_version``).

    Raises:
        UnsupportedVersionError: If no package version is valid for
            the given target, or if no known version satisfies a
            wildcard request.
        ValueError: If ``pkg_version`` is not a valid version request.

    Example:
        ```pycon
        >>> from feu.compat import find_closest_version, Target
        >>> find_closest_version(
        ...     pkg_name="numpy", pkg_version="2.0.2", target=Target(python_version="3.11")
        ... )
        '2.0.2'

        ```
    """
    return get_default_registry().find_closest_version(
        pkg_name=pkg_name, pkg_version=pkg_version, target=target
    )


def is_valid_version(pkg_name: str, pkg_version: str | None, target: Target) -> bool:
    r"""Check if a package version is valid for a target using the
    default registry.

    Args:
        pkg_name: The package name to check (e.g., ``"numpy"``).
        pkg_version: The package version request to validate: an
            exact version, a wildcard (e.g. ``"2.*"``) or
            ``""``/``None`` for the latest version.
        target: The compatibility target.

    Returns:
        ``True`` if valid or unconfigured, ``False`` otherwise,
            including when no package version is valid for the
            target. A wildcard or empty request is valid if a known
            compatible version satisfies it.

    Raises:
        ValueError: If ``pkg_version`` is not a valid version request.

    Example:
        ```pycon
        >>> from feu.compat import is_valid_version, Target
        >>> is_valid_version(
        ...     pkg_name="numpy", pkg_version="2.0.2", target=Target(python_version="3.11")
        ... )
        True

        ```
    """
    return get_default_registry().is_valid_version(
        pkg_name=pkg_name, pkg_version=pkg_version, target=target
    )
