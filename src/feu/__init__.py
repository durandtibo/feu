r"""Root package of ``feu``.

``feu`` is a lightweight library to manage Python packages and their
versions across Python environments. The only required dependency is
``packaging``. The optional libraries (``click``, ``gitpython``,
``requests`` and ``rich``) are imported lazily, and a feature that
needs one of them raises ``feu.imports.MissingPackageError`` if it is
missing.

The main functions and classes are available from this package:

- ``is_package_available`` and ``is_module_available``: check if a
  package or a module can be used.
- ``get_package_version`` and ``compare_version``: read the installed
  version of a package and compare it to a version.
- ``Target`` and ``resolve_target``: the environment (Python version,
  free-threaded flag, OS and CPU architecture) a compatibility answer
  is about.
- ``is_valid_version`` and ``find_closest_version``: check a version
  request against a target, or find the closest valid version. A
  version request is an exact version (``"2.4.0"``), a wildcard
  (``"2.4.*"``) or ``""`` for the latest version.
- ``install_package`` and ``install_package_closest_version``: install
  a package, as written or at the closest valid version.
  ``InstallerSpec`` and ``PackageSpec`` describe the installer and the
  package.

The public names are imported lazily (PEP 562): ``import feu`` imports
only ``feu.imports``, so it does not import any optional library. ``from
feu import compare_version`` imports ``feu.version`` the first time it
is used.

The subpackages are ``feu.compat`` (compatibility registry and discovery
from PyPI), ``feu.install`` (installers and dependency resolvers),
``feu.version`` (version utilities, PyPI and ``pyproject.toml``),
``feu.imports`` (optional dependencies), ``feu.utils`` (shared helpers),
``feu.benchmark`` (trend of ``pytest-benchmark`` results),
``feu.github`` (GitHub API), ``feu.local_git`` (tags of a git
repository) and ``feu.testing`` (``pytest`` marks).

Example:
    ```pycon
    >>> from feu import is_package_available
    >>> from feu.compat import Target, find_closest_version
    >>> is_package_available("packaging")
    True
    >>> find_closest_version("numpy", "2.3.0", Target(python_version="3.9"))
    '2.0.2'

    ```
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
    from collections.abc import Callable
    from typing import Any

    from feu.compat import Target, find_closest_version, is_valid_version, resolve_target
    from feu.imports import is_module_available, is_package_available
    from feu.install import InstallerSpec, install_package, install_package_closest_version
    from feu.utils.package import PackageSpec
    from feu.version import compare_version, get_package_version

__getattr__: Callable[[str], Any]
__dir__: Callable[[], list[str]]
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
