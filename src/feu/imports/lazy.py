r"""Implement a utility function to lazily import the names of a
package."""

from __future__ import annotations

__all__ = ["lazy_exports"]

import importlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping


def lazy_exports(
    package: str, exports: Mapping[str, str], namespace: dict[str, Any]
) -> tuple[Callable[[str], Any], Callable[[], list[str]]]:
    r"""Create the ``__getattr__`` and ``__dir__`` of a package that
    imports some of its names when they are used.

    The names are in the ``__all__`` of the package, so ``from package
    import name`` works as usual, but the module that defines a name is
    imported the first time the name is used. This avoids importing the
    optional libraries that a module needs when the package is
    imported.

    Args:
        package: The name of the package, usually ``__name__``.
        exports: The module that defines each lazy name.
        namespace: The namespace of the package, usually ``globals()``.
            A name is added to it when it is imported, so the next
            access does not call ``__getattr__``.

    Returns:
        The ``__getattr__`` and ``__dir__`` functions of the package.
        The returned ``__getattr__`` raises an ``AttributeError`` if the
        name is not in ``exports``.

    Example:
        ```pycon
        >>> namespace = {}
        >>> getattr_, dir_ = lazy_exports("example", {"OrderedDict": "collections"}, namespace)
        >>> getattr_("OrderedDict")
        <class 'collections.OrderedDict'>
        >>> "OrderedDict" in namespace
        True

        ```
    """

    def getattr_(name: str) -> Any:
        module_name = exports.get(name)
        if module_name is None:
            msg = f"module {package!r} has no attribute {name!r}"
            raise AttributeError(msg)
        value = getattr(importlib.import_module(module_name), name)
        namespace[name] = value
        return value

    def dir_() -> list[str]:
        return sorted({*namespace, *exports})

    return getattr_, dir_
