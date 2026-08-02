r"""Contain a registry-based system of per-package compatibility target
discoverers.

Discovering compatibility targets from PyPI wheel metadata is
generally computed the same way for every package (``CompatDiscoverer``),
but some packages need a different strategy (e.g. because their wheel
tags or ``requires_python`` metadata don't reflect their real
compatibility). ``CompatDiscovererRegistry`` allows registering a
package-specific ``BaseCompatDiscoverer`` that takes precedence over
the default one.

Example:
    ```pycon
    >>> from feu.compat.discoverers import discover_compat_targets
    >>> compat = discover_compat_targets("numpy")  # doctest: +SKIP

    ```
"""

from __future__ import annotations

__all__ = [
    "BaseCompatDiscoverer",
    "CompatDiscoverer",
    "CompatDiscovererRegistry",
    "DuckdbCompatDiscoverer",
    "JaxCompatDiscoverer",
    "PydanticCompatDiscoverer",
    "discover_compat_targets",
    "get_default_registry",
    "register_discoverers",
]

from feu.compat.discoverers.base import BaseCompatDiscoverer
from feu.compat.discoverers.default import CompatDiscoverer
from feu.compat.discoverers.duckdb import DuckdbCompatDiscoverer
from feu.compat.discoverers.interface import (
    discover_compat_targets,
    get_default_registry,
    register_discoverers,
)
from feu.compat.discoverers.jax import JaxCompatDiscoverer
from feu.compat.discoverers.pydantic import PydanticCompatDiscoverer
from feu.compat.discoverers.registry import CompatDiscovererRegistry
