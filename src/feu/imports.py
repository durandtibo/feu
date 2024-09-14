r"""Contain to check if a package or module is available."""

from __future__ import annotations

__all__ = ["is_module_available", "is_package_available", "check_fire", "is_fire_available"]

from contextlib import suppress
from functools import lru_cache
from importlib import import_module
from importlib.util import find_spec


@lru_cache
def is_package_available(package: str) -> bool:
    """Check if a package is available.

    Args:
        package: Specifies the package name to check.

    Returns:
        ``True`` if the package is available, otherwise ``False``.

    Example usage:

    ```pycon

    >>> from feu import is_package_available
    >>> is_package_available("os")
    True
    >>> is_package_available("os.path")
    True
    >>> is_package_available("my_missing_package")
    False

    ```
    """
    with suppress(Exception):
        return find_spec(package) is not None
    return False


@lru_cache
def is_module_available(module: str) -> bool:
    """Check if a module path is available.

    Args:
        module: Specifies the module to check.

    Example usage:

    ```pycon

    >>> from feu import is_module_available
    >>> is_module_available("os")
    True
    >>> is_module_available("os.path")
    True
    >>> is_module_available("missing.module")
    False

    ```
    """
    if not is_package_available(str(module).split(".", maxsplit=1)[0]):
        return False
    try:
        import_module(module)
    except (ImportError, ModuleNotFoundError):
        return False
    return True


################
#     fire     #
################


@lru_cache
def is_fire_available() -> bool:
    r"""Indicate if the ``fire`` package is installed or not.

    Returns:
        ``True`` if ``fire`` is available otherwise ``False``.

    Example usage:

    ```pycon

    >>> from feu.imports import is_fire_available
    >>> is_fire_available()

    ```
    """
    return is_package_available("fire")


def check_fire() -> None:
    r"""Check if the ``fire`` package is installed.

    Raises:
        RuntimeError: if the ``fire`` package is not installed.

    Example usage:

    ```pycon

    >>> from feu.imports import check_fire
    >>> check_fire()

    ```
    """
    if not is_fire_available():
        msg = (
            "'fire' package is required but not installed. "
            "You can install 'fire' package with the command:\n\n"
            "pip install fire\n"
        )
        raise RuntimeError(msg)
