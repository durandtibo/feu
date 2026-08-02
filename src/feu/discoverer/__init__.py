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
    >>> from feu.compat.discoverer import discover_compat_targets
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
    "discover_compat_targets",
    "get_default_registry",
    "register_discoverers",
]

from feu.discoverer.base import BaseCompatDiscoverer
from feu.discoverer.default import CompatDiscoverer
from feu.discoverer.duckdb import DuckdbCompatDiscoverer
from feu.discoverer.interface import (
    discover_compat_targets,
    get_default_registry,
    register_discoverers,
)
from feu.discoverer.jax import JaxCompatDiscoverer
from feu.discoverer.registry import CompatDiscovererRegistry
