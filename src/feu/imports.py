from __future__ import annotations

__all__ = ["is_package_available", "is_module_available"]

from functools import lru_cache
from importlib import import_module
from importlib.util import find_spec


@lru_cache
def is_package_available(package: str) -> bool:
    """Checks if a package is available.

    Args:
    ----
        name (str): Specifies the package name to check.

    Returns
    -------
        package: ``True`` if the package is available,
            otherwise ``False``.

    Example usage:

    .. code-block:: pycon

        >>> from feu import is_package_available
        >>> is_package_available("os")
        True
        >>> is_package_available("os.path")
        True
        >>> is_package_available("my_missing_package")
        False
    """
    try:
        return find_spec(package) is not None
    except Exception:  # noqa: BLE001
        return False


@lru_cache
def is_module_available(module: str) -> bool:
    """Checks if a module path is available.

    Args:
    ----
        module (str): Specifies the module to check.

    Example usage:

    .. code-block:: pycon

        >>> from feu import is_module_available
        >>> is_module_available("os")
        True
        >>> is_module_available("os.path")
        True
        >>> is_module_available("missing.module")
        False
    """
    if not is_package_available(str(module).split(".", maxsplit=1)[0]):
        return False
    try:
        import_module(module)
        return True
    except (ImportError, ModuleNotFoundError):
        return False
