r"""User-defined compatibility overrides for ``pydantic``.

Empty by default. Add entries here to override the default/discovered
constraints for this package, e.g.::

    Target(python_version="3.11"): [VersionRange("1.0.0", None)]
"""

from __future__ import annotations

__all__ = ["PKG_NAME", "compat"]

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from feu.compat.registry import VersionRange
    from feu.compat.target import Target

PKG_NAME = "pydantic"


def compat() -> dict[Target, list[VersionRange]]:
    r"""Return the user-defined compatibility overrides for
    ``pydantic``."""
    return {}
