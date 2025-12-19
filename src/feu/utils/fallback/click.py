r"""Contain fallback implementations used when ``click`` dependency is
not available."""

from __future__ import annotations

__all__ = ["click"]

from types import SimpleNamespace
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable


def noop_decorator(*args: Any, **kwargs: Any) -> Callable:  # noqa: ARG001
    """Define a no-op decorator that returns the function unchanged.

    This decorator accepts any arguments and keyword arguments, but does not
    modify or wrap the decorated function in any way. It is typically used as
    a placeholder to simulate decorators in contexts where the actual decorator
    may not be available.

    Args:
        *args: Variable length argument list. Ignored.
        **kwargs: Arbitrary keyword arguments. Ignored.

    Returns:
        A decorator function that returns the original function unchanged.
    """
    return lambda f: f


# Create a fake click package
click: SimpleNamespace = SimpleNamespace(
    group=noop_decorator,
    command=noop_decorator,
    option=noop_decorator,
)
