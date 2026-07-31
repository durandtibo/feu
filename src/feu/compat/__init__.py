r"""Contain a registry-based system for package/Python-version
compatibility resolution."""

from __future__ import annotations

__all__ = [
    "CompatRegistry",
    "discover_compat",
    "find_closest_version",
    "get_default_registry",
    "is_valid_version",
    "register_compat",
]

from feu.compat.discovery import discover_compat
from feu.compat.interface import (
    find_closest_version,
    get_default_registry,
    is_valid_version,
    register_compat,
)
from feu.compat.registry import CompatRegistry
