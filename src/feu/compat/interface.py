r"""Define the public interface for package/target compatibility
resolution."""

from __future__ import annotations

__all__ = [
    "find_closest_version",
    "get_default_registry",
    "is_valid_version",
    "register_compat",
]

from typing import TYPE_CHECKING

from feu.compat.defaults import register_defaults
from feu.compat.registry import CompatRegistry

if TYPE_CHECKING:
    from feu.compat.target import Target


def get_default_registry() -> CompatRegistry:
    r"""Return the default global compatibility registry.

    The registry is created on the first call and reused on all
    subsequent calls (singleton pattern). It is pre-configured with
    the default package version constraints in its base layer.

    Returns:
        A singleton ``CompatRegistry`` configured with the default
        package version constraints.

    Example:
        ```pycon
        >>> from feu.compat import get_default_registry, Target
        >>> registry = get_default_registry()
        >>> registry.is_valid_version("numpy", "2.0.2", Target(python_version="3.11"))
        True

        ```
    """
    if not hasattr(get_default_registry, "_registry"):
        registry = CompatRegistry()
        register_defaults(registry)
        get_default_registry._registry = registry
    return get_default_registry._registry


def register_compat(
    mapping: dict[str, dict[Target, dict[str, str | None]]],
    exist_ok: bool = False,
) -> None:
    r"""Register custom package configurations into the default global
    registry's override layer.

    Override entries always take precedence over the default/base
    layer, and are only conflict-checked against other overrides, so
    correcting an inaccurate default never requires ``exist_ok=True``.

    Args:
        mapping: Mapping of package name to ``Target`` to
            ``{"min": ..., "max": ...}`` constraints.
        exist_ok: If ``False`` (default), raises an error if any entry
            is already registered as an override. If ``True``,
            overwrites existing override registrations silently.

    Raises:
        RuntimeError: If any entry is already registered as an
            override and ``exist_ok`` is ``False``.

    Example:
        ```pycon
        >>> from feu.compat import register_compat, Target
        >>> register_compat(
        ...     {"my_package": {Target(python_version="3.11"): {"min": "1.0.0", "max": None}}}
        ... )

        ```
    """
    get_default_registry().register_many(mapping, exist_ok=exist_ok)


def find_closest_version(pkg_name: str, pkg_version: str, target: Target) -> str:
    r"""Find the closest valid version for a package using the default
    registry.

    Args:
        pkg_name: The package name to check (e.g., ``"numpy"``).
        pkg_version: The requested package version.
        target: The compatibility target.

    Returns:
        The closest valid version as a string.

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


def is_valid_version(pkg_name: str, pkg_version: str, target: Target) -> bool:
    r"""Check if a package version is valid for a target using the
    default registry.

    Args:
        pkg_name: The package name to check (e.g., ``"numpy"``).
        pkg_version: The package version to validate.
        target: The compatibility target.

    Returns:
        ``True`` if valid or unconfigured, ``False`` otherwise.

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
