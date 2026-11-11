r"""Contain a registry-based system for package/target compatibility
resolution."""

from __future__ import annotations

__all__ = [
    "COMPANIONS",
    "CompatRegistry",
    "Discovery",
    "PinnedDependency",
    "SameVersion",
    "Target",
    "UnsupportedVersionError",
    "VersionRange",
    "WheelTags",
    "discover_compat_targets",
    "find_closest_version",
    "get_compatible_versions",
    "get_default_compat_registry",
    "group_into_ranges",
    "is_compatible",
    "is_valid_version",
    "parse_wheel_filename",
    "register_compat",
    "resolve_target",
    "show_compat_targets",
    "tags_match_exactly",
]

from feu.compat.discover import (
    COMPANIONS,
    Discovery,
    PinnedDependency,
    SameVersion,
    discover_compat_targets,
    group_into_ranges,
    is_compatible,
    tags_match_exactly,
)
from feu.compat.display import show_compat_targets
from feu.compat.interface import (
    find_closest_version,
    get_compatible_versions,
    get_default_compat_registry,
    is_valid_version,
    register_compat,
)
from feu.compat.registry import CompatRegistry, UnsupportedVersionError, VersionRange
from feu.compat.target import Target, resolve_target
from feu.compat.wheel_tags import WheelTags, parse_wheel_filename
