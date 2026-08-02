r"""Contain a registry-based system for package/target compatibility
resolution."""

from __future__ import annotations

__all__ = [
    "BaseCompatDiscoverer",
    "CompatDiscoverer",
    "CompatDiscovererRegistry",
    "CompatRegistry",
    "JaxCompatDiscoverer",
    "Target",
    "UnsupportedVersionError",
    "VersionRange",
    "WheelTags",
    "discover_compat",
    "discover_compat_targets",
    "find_closest_version",
    "get_default_registry",
    "is_valid_version",
    "parse_wheel_filename",
    "register_compat",
    "show_compat_targets",
]

from feu.compat.discovery import discover_compat, show_compat_targets
from feu.compat.interface import (
    find_closest_version,
    get_default_registry,
    is_valid_version,
    register_compat,
)
from feu.compat.registry import CompatRegistry, UnsupportedVersionError, VersionRange
from feu.compat.target import Target
from feu.compat.wheel_tags import WheelTags, parse_wheel_filename
from feu.discoverer import (
    BaseCompatDiscoverer,
    CompatDiscoverer,
    CompatDiscovererRegistry,
    JaxCompatDiscoverer,
    discover_compat_targets,
)
