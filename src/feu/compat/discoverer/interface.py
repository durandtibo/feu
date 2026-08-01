r"""Define the public interface for package compatibility target
discovery."""

from __future__ import annotations

__all__ = ["discover_compat_targets", "get_default_registry", "register_discoverers"]

from typing import TYPE_CHECKING

from feu.compat.discoverer.registry import CompatDiscovererRegistry
from feu.compat.discovery import DEFAULT_TARGETS

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from feu.compat.discoverer.base import BaseCompatDiscoverer
    from feu.compat.registry import VersionRange
    from feu.compat.target import Target


def get_default_registry() -> CompatDiscovererRegistry:
    r"""Return the default global compatibility discoverer registry.

    The registry is created on the first call and reused on all
    subsequent calls (singleton pattern).

    Returns:
        A singleton ``CompatDiscovererRegistry``.

    Example:
        ```pycon
        >>> from feu.compat.discoverer import get_default_registry
        >>> registry = get_default_registry()

        ```
    """
    if not hasattr(get_default_registry, "_registry"):
        get_default_registry._registry = CompatDiscovererRegistry()
    return get_default_registry._registry


def register_discoverers(
    mapping: Mapping[str, BaseCompatDiscoverer], exist_ok: bool = False
) -> None:
    r"""Register custom compatibility discoverers into the default global
    registry.

    Args:
        mapping: Mapping of package name to discoverer.
        exist_ok: If ``False``, ``RuntimeError`` is raised if any
            package already exists. This parameter should be set to
            ``True`` to overwrite the discoverer for a package.

    Example:
        ```pycon
        >>> from feu.compat.discoverer import CompatDiscoverer, register_discoverers
        >>> register_discoverers({"my_package": CompatDiscoverer()})

        ```
    """
    get_default_registry().register_many(mapping, exist_ok=exist_ok)


def discover_compat_targets(
    pkg_name: str, targets: Sequence[Target] = DEFAULT_TARGETS
) -> dict[Target, list[VersionRange]]:
    r"""Discover the version range compatible with each target.

    Uses the compatibility discoverer registered for ``pkg_name`` in
    the default global registry if one exists, otherwise falls back to
    the default ``CompatDiscoverer``.

    Args:
        pkg_name: The package name to inspect (e.g., ``"numpy"``).
        targets: The compatibility targets to compute constraints for.
            Each target must have concrete (non-``None``) ``os`` and
            ``arch``. Defaults to ``DEFAULT_TARGETS``.

    Returns:
        A mapping of ``Target`` to a list of ``VersionRange``, in the
            same shape expected by ``CompatRegistry.register_many``.

    Example:
        ```pycon
        >>> from feu.compat import discover_compat_targets
        >>> compat = discover_compat_targets("numpy")  # doctest: +SKIP

        ```
    """
    return get_default_registry().find_discoverer(pkg_name).discover(pkg_name, targets)
