r"""Contain utility functions to manage packages."""

from __future__ import annotations

__all__ = ["extract_package_name", "generate_extras_string"]

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


def extract_package_name(requirement: str) -> str:
    r"""Extract the base package name from a requirement string.

    The requirement string may include optional dependencies in square brackets,
    such as 'package[extra1,extra2]'. This function returns only the base package
    name without the extras.

    Args:
        requirement: The requirement string containing the package name and
            optionally extra dependencies.

    Returns:
        The base package name without extras.

    Example usage:

    ```pycon

    >>> from feu.utils.package import extract_package_name
    >>> extract_package_name("requests[security,socks]")
    'requests'
    >>> extract_package_name("numpy")
    'numpy'
    >>> extract_package_name("pandas[performance]")
    'pandas'

    ```
    """
    match = re.match(r"^([a-zA-Z0-9_\-\.]+)", requirement)
    return match.group(1) if match else requirement


def generate_extras_string(extras: Sequence[str]) -> str:
    r"""Generate a string with the package extras i.e. optional
    dependencies.

    Args:
        extras: The package optional dependencies.

    Returns:
        A string with the package extras.

    Example usage:

    ```pycon

    >>> from feu.utils.package import generate_extras_string
    >>> generate_extras_string(["security"])
    '[security]'
    >>> generate_extras_string(["security", "socks"])
    '[security,socks]'
    >>> generate_extras_string([])
    ''

    ```
    """
    if not extras:
        return ""
    return f"[{','.join(extras)}]"
