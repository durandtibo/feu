r"""Define the public interface for package/Python-version
compatibility resolution."""

from __future__ import annotations

__all__ = [
    "find_closest_version",
    "get_default_registry",
    "is_valid_version",
    "register_compat",
]

from feu.compat.defaults import register_defaults
from feu.compat.registry import CompatRegistry


def get_default_registry() -> CompatRegistry:
    r"""Return the default global compatibility registry.

    The registry is created on the first call and reused on all
    subsequent calls (singleton pattern). It is pre-configured with
    the default package version constraints.

    Returns:
        A singleton ``CompatRegistry`` configured with the default
        package version constraints.

    Example:
        ```pycon
        >>> from feu.compat import get_default_registry
        >>> registry = get_default_registry()
        >>> registry.is_valid_version("numpy", "2.0.2", "3.11")
        True

        ```
    """
    if not hasattr(get_default_registry, "_registry"):
        registry = CompatRegistry()
        register_defaults(registry)
        get_default_registry._registry = registry
    return get_default_registry._registry


def register_compat(
    mapping: dict[str, dict[str, dict[str, str | None]]],
    exist_ok: bool = False,
) -> None:
    r"""Register custom package configurations into the default global
    registry.

    Args:
        mapping: Mapping of package name to Python version to
            ``{"min": ..., "max": ...}`` constraints.
        exist_ok: If ``False`` (default), raises an error if any entry
            is already registered. If ``True``, overwrites existing
            registrations silently.

    Raises:
        RuntimeError: If any entry is already registered and
            ``exist_ok`` is ``False``.

    Example:
        ```pycon
        >>> from feu.compat import register_compat
        >>> register_compat({"my_package": {"3.11": {"min": "1.0.0", "max": None}}})

        ```
    """
    get_default_registry().register_many(mapping, exist_ok=exist_ok)


def find_closest_version(pkg_name: str, pkg_version: str, python_version: str) -> str:
    r"""Find the closest valid version for a package using the default
    registry.

    Args:
        pkg_name: The package name to check (e.g., ``"numpy"``).
        pkg_version: The requested package version.
        python_version: The Python version (e.g., ``"3.11"``).

    Returns:
        The closest valid version as a string.

    Example:
        ```pycon
        >>> from feu.compat import find_closest_version
        >>> find_closest_version(pkg_name="numpy", pkg_version="2.0.2", python_version="3.11")
        '2.0.2'

        ```
    """
    return get_default_registry().find_closest_version(
        pkg_name=pkg_name, pkg_version=pkg_version, python_version=python_version
    )


def is_valid_version(pkg_name: str, pkg_version: str, python_version: str) -> bool:
    r"""Check if a package version is valid for a Python version using
    the default registry.

    Args:
        pkg_name: The package name to check (e.g., ``"numpy"``).
        pkg_version: The package version to validate.
        python_version: The Python version (e.g., ``"3.11"``).

    Returns:
        ``True`` if valid or unconfigured, ``False`` otherwise.

    Example:
        ```pycon
        >>> from feu.compat import is_valid_version
        >>> is_valid_version(pkg_name="numpy", pkg_version="2.0.2", python_version="3.11")
        True

        ```
    """
    return get_default_registry().is_valid_version(
        pkg_name=pkg_name, pkg_version=pkg_version, python_version=python_version
    )
