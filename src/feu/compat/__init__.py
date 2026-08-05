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
    "discover_compat_targets",
    "find_closest_version",
    "get_default_registry",
    "is_valid_version",
    "parse_wheel_filename",
    "register_compat",
    "resolve_target",
    "show_compat_targets",
]

from feu.compat.discoverers import (
    BaseCompatDiscoverer,
    CompatDiscoverer,
    CompatDiscovererRegistry,
    JaxCompatDiscoverer,
    discover_compat_targets,
)
from feu.compat.interface import (
    find_closest_version,
    get_default_registry,
    is_valid_version,
    register_compat,
)
from feu.compat.matrix import show_compat_targets
from feu.compat.registry import CompatRegistry, UnsupportedVersionError, VersionRange
from feu.compat.target import Target, resolve_target
from feu.compat.wheel_tags import WheelTags, parse_wheel_filename
