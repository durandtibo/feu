r"""Root package of ``feu``.

The public names are imported lazily (PEP 562): ``import feu`` does not
import any submodule, so it does not import any optional library. ``from
feu import compare_version`` imports ``feu.version`` the first time it
is used.
"""

from __future__ import annotations

__all__ = [
    "InstallerSpec",
    "PackageSpec",
    "Target",
    "compare_version",
    "find_closest_version",
    "get_package_version",
    "install_package",
    "install_package_closest_version",
    "is_module_available",
    "is_package_available",
    "is_valid_version",
    "resolve_target",
]

from importlib.metadata import PackageNotFoundError, version as metadata_version
from typing import TYPE_CHECKING

from feu.imports.lazy import lazy_exports

if TYPE_CHECKING:
    from feu.compat import Target, find_closest_version, is_valid_version, resolve_target
    from feu.imports import is_module_available, is_package_available
    from feu.install import InstallerSpec, install_package, install_package_closest_version
    from feu.utils.package import PackageSpec
    from feu.version import compare_version, get_package_version

__getattr__, __dir__ = lazy_exports(
    __name__,
    {
        "InstallerSpec": "feu.install",
        "PackageSpec": "feu.utils.package",
        "Target": "feu.compat",
        "compare_version": "feu.version",
        "find_closest_version": "feu.compat",
        "get_package_version": "feu.version",
        "install_package": "feu.install",
        "install_package_closest_version": "feu.install",
        "is_module_available": "feu.imports",
        "is_package_available": "feu.imports",
        "is_valid_version": "feu.compat",
        "resolve_target": "feu.compat",
    },
    globals(),
)

try:
    __version__ = metadata_version(__name__)
except PackageNotFoundError:  # pragma: no cover
    # Package is not installed, fallback if needed
    __version__ = "0.0.0"
