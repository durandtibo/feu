r"""Contain functions to compare package versions."""

from __future__ import annotations

__all__ = ["compare_version", "get_package_version", "get_python_major_minor"]

from feu.versio.comparison import compare_version
from feu.versio.runtime import get_package_version, get_python_major_minor
