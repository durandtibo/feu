from __future__ import annotations

__all__ = ["is_package_available"]

from functools import lru_cache
from importlib.util import find_spec


@lru_cache(maxsize=1)
def is_package_available(package: str) -> bool:
    """Checks if a package is available in your environment.

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
        >>> is_package_available("my_missing_package")
        False
    """
    return find_spec(package) is not None
