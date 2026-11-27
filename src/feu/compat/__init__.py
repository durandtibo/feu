r"""Contain a registry-based system for package/target compatibility
resolution.

A ``Target`` describes an environment (Python version, free-threaded
flag, OS and CPU architecture). A ``CompatRegistry`` holds, for each
package and target, the ranges of compatible versions, and answers if a
version request is valid (``is_valid_version``), which version is the
closest valid one (``find_closest_version``) and which known versions are
compatible (``get_compatible_versions``). The default registry is filled
with the data shipped in ``feu/compat/data``, which is generated from the
files published on PyPI by ``discover_compat_targets``.

Example:
    ```pycon
    >>> from feu.compat import Target, is_valid_version
    >>> is_valid_version("numpy", "2.0.2", Target(python_version="3.11"))
    True

    ```
"""

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
    "WheelTag",
    "discover_compat_targets",
    "fetch_known_versions",
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
    fetch_known_versions,
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
from feu.compat.wheel_tags import WheelTag, parse_wheel_filename
