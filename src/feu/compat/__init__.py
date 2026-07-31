r"""Contain a registry-based system for package/target compatibility
resolution."""

from __future__ import annotations

__all__ = [
    "UNSUPPORTED",
    "CompatRegistry",
    "Target",
    "UnsupportedVersionError",
    "WheelTags",
    "discover_compat",
    "discover_compat_targets",
    "find_closest_version",
    "get_default_registry",
    "is_valid_version",
    "parse_wheel_filename",
    "register_compat",
]

from feu.compat.discovery import discover_compat, discover_compat_targets
from feu.compat.interface import (
    find_closest_version,
    get_default_registry,
    is_valid_version,
    register_compat,
)
from feu.compat.registry import UNSUPPORTED, CompatRegistry, UnsupportedVersionError
from feu.compat.target import Target
from feu.compat.wheel_tags import WheelTags, parse_wheel_filename
