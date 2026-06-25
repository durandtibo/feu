r"""Contain fallback implementations used when ``tomli`` dependency is
not available."""

from __future__ import annotations

__all__ = ["tomli"]

from types import ModuleType
from typing import Any, NoReturn

from feu.utils.imports import raise_tomli_missing_error


def fake_function(*args: Any, **kwargs: Any) -> NoReturn:  # noqa: ARG001
    r"""Fake function that raises an error because tomli is not
    installed.

    Args:
        *args: Positional arguments.
        **kwargs: Keyword arguments.

    Raises:
        RuntimeError: tomli is required for this functionality.
    """
    raise_tomli_missing_error()


# Create a fake tomli package
tomli: ModuleType = ModuleType("tomli")
tomli.load = fake_function
