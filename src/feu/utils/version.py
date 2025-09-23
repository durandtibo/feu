r"""Contain utility functions to get the version of something."""

from __future__ import annotations

__all__ = ["get_python_major_minor"]

import logging
import sys
from functools import lru_cache

logger = logging.getLogger(__name__)


@lru_cache
def get_python_major_minor() -> str:
    r"""Get the MAJOR.MINOR version of the current python.

    Returns:
        The MAJOR.MINOR version of the current python.

    Example usage:

    ```pycon

    >>> from feu.utils.version import get_python_major_minor
    >>> get_python_major_minor()  # doctest: +SKIP

    ```
    """
    return f"{sys.version_info.major}.{sys.version_info.minor}"
