r"""Contain the automatically discovered package/target compatibility
constraints.

Each submodule of this package holds the precomputed output of
``discover_compat_targets`` for one package, refreshed by the
``dev/generate_discovered_compat.py`` maintenance script. The
default registry returned by ``feu.compat.get_default_registry`` is
populated from these modules. Custom constraints can be registered on
top with ``feu.compat.register_compat``.
"""

from __future__ import annotations

__all__ = ["register_discovered"]

import importlib
import pkgutil
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from feu.compat.registry import CompatRegistry


def register_discovered(registry: CompatRegistry) -> None:
    r"""Populate a registry with the automatically discovered package
    compatibility constraints.

    Every submodule of ``feu.compat.discovered`` is imported and must
    define ``PKG_NAME`` (the real package name) and a ``compat()``
    function returning the precomputed output of
    ``discover_compat_targets`` for that package.

    Args:
        registry: The registry to populate.
    """
    for module_info in pkgutil.iter_modules(__path__):
        module = importlib.import_module(f"{__name__}.{module_info.name}")
        registry.register_many({module.PKG_NAME: module.compat()})
