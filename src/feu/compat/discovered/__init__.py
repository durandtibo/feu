r"""Contain the automatically discovered package/target compatibility
constraints.

Each submodule of this package holds the precomputed output of
``discover_compat_targets`` for one package, refreshed by the
``dev/generate_discovered_compat.py`` maintenance script. This is
the automatic counterpart to ``feu.compat.defaults.DEFAULT_COMPAT``,
the human-curated variant, which takes precedence when both specify a
given package/target.
"""

from __future__ import annotations

__all__ = ["register_discovered"]

import importlib
import pkgutil
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from feu.compat.registry import CompatRegistry


def register_discovered(registry: CompatRegistry) -> None:
    r"""Populate a registry's base layer with the automatically
    discovered package compatibility constraints.

    Every submodule of ``feu.compat.discovered`` is imported and must
    define ``PKG_NAME`` (the real package name) and a ``compat()``
    function returning the precomputed output of
    ``discover_compat_targets`` for that package.

    Args:
        registry: The registry to populate.
    """
    for module_info in pkgutil.iter_modules(__path__):
        module = importlib.import_module(f"{__name__}.{module_info.name}")
        registry.register_many({module.PKG_NAME: module.compat()}, layer="base")
