r"""Contain the loader of the shipped compatibility data.

The data is one JSON file per package in ``feu/compat/data/``, named by
the canonical package name (PEP 503):

.. code-block:: json

    {
      "package": "numpy",
      "generated": "2026-11-09",
      "targets": [
        {"python": "3.12", "free_threaded": false, "os": "linux", "arch": "x86_64",
         "ranges": [["1.26.0", null]]}
      ]
    }

There is no list of versions: a wildcard request is matched against the
releases downloaded from PyPI (see ``CompatRegistry``), so it never goes
stale. A range whose ``max`` is ``null`` is open: the latest release was
compatible when the file was generated. The entries are sorted by
``(python, free_threaded, os, arch)``.

The list of packages is the list of files, so a package is added by
running ``dev/generate_compat_data.py`` with its name.
"""

from __future__ import annotations

__all__ = ["ShippedData", "format_package_data", "parse_package_data"]

import json
from importlib.resources import files
from typing import TYPE_CHECKING, Any

from packaging.version import Version

from feu.compat.registry import PackageData, VersionRange
from feu.compat.target import Target

if TYPE_CHECKING:
    from collections.abc import Collection, Mapping, Sequence

_DATA_PACKAGE = "feu.compat.data"
_SUFFIX = ".json"


def _target_key(target: Target) -> tuple[Version, bool, str, str]:
    r"""Get the sort key of a target.

    Args:
        target: The target.

    Returns:
        The key ``(python, free_threaded, os, arch)``, the Python
            version being compared as a version (``3.9 < 3.10``).
    """
    return (
        Version(target.python_version),
        target.free_threaded,
        target.os or "",
        target.arch or "",
    )


def format_package_data(
    package: str,
    generated: str,
    targets: Mapping[Target, Sequence[VersionRange]],
) -> str:
    r"""Format the compatibility data of a package as the text of its
    JSON file.

    The output is deterministic: the same input gives the same text.
    The targets are sorted by ``(python, free_threaded, os, arch)``,
    one target per line.

    Args:
        package: The canonical package name.
        generated: The generation date, in ISO 8601 format e.g.
            ``"2026-11-09"``.
        targets: The ranges of each target.

    Returns:
        The text of the JSON file, ending with a newline.

    Example:
        ```pycon
        >>> from feu.compat import Target, VersionRange
        >>> from feu.compat.shipped import format_package_data
        >>> target = Target("3.12", False, "linux", "x86_64")
        >>> print(
        ...     format_package_data(
        ...         "numpy", "2026-11-09", {target: [VersionRange("1.0", None)]}
        ...     )
        ... )
        {
          "package": "numpy",
          "generated": "2026-11-09",
          "targets": [
            {"python": "3.12", "free_threaded": false, "os": "linux", "arch": "x86_64", "ranges": [["1.0", null]]}
          ]
        }
        <BLANKLINE>

        ```
    """
    target_lines = ",\n".join(
        "    "
        + json.dumps(
            {
                "python": target.python_version,
                "free_threaded": target.free_threaded,
                "os": target.os,
                "arch": target.arch,
                "ranges": [[r.min, r.max] for r in targets[target]],
            }
        )
        for target in sorted(targets, key=_target_key)
    )
    return (
        "{\n"
        f'  "package": {json.dumps(package)},\n'
        f'  "generated": {json.dumps(generated)},\n'
        f'  "targets": [\n{target_lines}\n  ]\n'
        "}\n"
    )


def parse_package_data(text: str) -> PackageData:
    r"""Parse the text of the JSON file of a package.

    Args:
        text: The text of the JSON file.

    Returns:
        The ranges of each target.

    Raises:
        ValueError: If the text is not valid JSON or does not have the
            format of the shipped data.

    Example:
        ```pycon
        >>> from feu.compat.shipped import parse_package_data
        >>> data = parse_package_data(
        ...     '{"package": "numpy", "generated": "2026-11-09", "targets": []}'
        ... )
        >>> data.targets
        {}

        ```
    """
    document: Any = json.loads(text)
    try:
        targets = {
            Target(
                python_version=entry["python"],
                free_threaded=entry["free_threaded"],
                os=entry["os"],
                arch=entry["arch"],
            ): [VersionRange(min=r[0], max=r[1]) for r in entry["ranges"]]
            for entry in document["targets"]
        }
    except (KeyError, TypeError, IndexError) as exc:
        msg = f"invalid compatibility data: {exc!r}"
        raise ValueError(msg) from exc
    return PackageData(targets=targets)


class ShippedData:
    r"""Load the compatibility data shipped in ``feu/compat/data``.

    The list of packages is read from the file names (no file is
    parsed), and a file is parsed when its package is loaded.

    Example:
        ```pycon
        >>> from feu.compat.shipped import ShippedData
        >>> "numpy" in ShippedData().packages()
        True

        ```
    """

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def packages(self) -> Collection[str]:
        r"""Get the packages that have shipped data.

        Returns:
            The canonical names of the packages, sorted.
        """
        return sorted(
            entry.name.removesuffix(_SUFFIX)
            for entry in files(_DATA_PACKAGE).iterdir()
            if entry.name.endswith(_SUFFIX)
        )

    def load(self, name: str) -> PackageData:
        r"""Load the data of a package.

        Args:
            name: The canonical package name.

        Returns:
            The ranges of each target.

        Raises:
            FileNotFoundError: If there is no data for the package.
            ValueError: If the file is not valid.
        """
        return parse_package_data(files(_DATA_PACKAGE).joinpath(f"{name}{_SUFFIX}").read_text())
