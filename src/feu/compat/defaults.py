r"""Contain the default package version compatibility constraints."""

from __future__ import annotations

__all__ = ["DEFAULT_COMPAT", "register_defaults"]

from typing import TYPE_CHECKING

from feu.compat.registry import VersionRange
from feu.compat.target import Target

if TYPE_CHECKING:
    from feu.compat.registry import CompatRegistry

DEFAULT_COMPAT: dict[str, dict[str, list[VersionRange]]] = {
    # https://click.palletsprojects.com/en/stable/changes/
    "click": {
        "3.15": [VersionRange(None, None)],
        "3.14": [VersionRange(None, None)],
        "3.13": [VersionRange(None, None)],
        "3.12": [VersionRange(None, None)],
        "3.11": [VersionRange(None, None)],
        "3.10": [VersionRange(None, None)],
        "3.9": [VersionRange(None, "8.1.8")],
    },
    # https://github.com/duckdb/duckdb-python/releases
    "duckdb": {
        "3.15": [VersionRange(None, None)],
        "3.14": [VersionRange("1.4.2", None)],
        "3.13": [VersionRange(None, None)],
        "3.12": [VersionRange(None, None)],
        "3.11": [VersionRange(None, None)],
        "3.10": [VersionRange(None, None)],
    },
    # https://pypi.org/project/jaxlib/#history
    "jax": {
        "3.15": [VersionRange(None, None)],
        "3.14": [VersionRange("0.7.1", None)],
        "3.13": [VersionRange("0.4.34", None)],
        "3.12": [VersionRange("0.4.17", None)],
        "3.11": [VersionRange("0.4.6", None)],
        "3.10": [VersionRange("0.4.6", "0.6.2")],
        "3.9": [VersionRange("0.4.6", "0.4.30")],
    },
    # https://matplotlib.org/stable/users/release_notes.html
    "matplotlib": {
        "3.15": [VersionRange(None, None)],
        "3.14": [VersionRange("3.10.5", None)],
        "3.13": [VersionRange(None, None)],
        "3.12": [VersionRange(None, None)],
        "3.11": [VersionRange(None, None)],
        "3.10": [VersionRange(None, None)],
        "3.9": [VersionRange(None, "3.9.4")],
    },
    # https://numpy.org/devdocs/release.html
    "numpy": {
        "3.15": [VersionRange(None, None)],
        "3.14": [VersionRange("2.3.0", None)],
        "3.13": [VersionRange("2.1.0", None)],
        "3.12": [VersionRange("1.26.0", None)],
        "3.11": [VersionRange("1.23.2", "2.4.6")],
        "3.10": [VersionRange("1.21.3", "2.2.6")],
        "3.9": [VersionRange("1.19.3", "2.0.2")],
    },
    # https://github.com/pandas-dev/pandas/releases
    # https://pandas.pydata.org/docs/whatsnew/index.html
    "pandas": {
        "3.15": [VersionRange(None, None)],
        "3.14": [VersionRange("2.3.3", None)],
        "3.13": [VersionRange("2.2.3", None)],
        "3.12": [VersionRange("2.1.1", None)],
        "3.11": [VersionRange("1.3.4", None)],
        "3.10": [VersionRange("1.3.3", "2.3.3")],
        "3.9": [VersionRange(None, "2.3.3")],
    },
    # https://arrow.apache.org/release/
    "pyarrow": {
        "3.15": [VersionRange(None, None)],
        "3.14": [VersionRange("22.0.0", None)],
        "3.13": [VersionRange("18.0.0", None)],
        "3.12": [VersionRange("14.0.0", None)],
        "3.11": [VersionRange("10.0.1", None)],
        "3.10": [VersionRange("6.0.0", None)],
        "3.9": [VersionRange("3.0.0", "16.1.0")],
    },
    # pydantic 1.x (last release 1.10.13) and pydantic 2.x are both valid
    # on Python versions where 1.x still ships wheels (3.9-3.11); pydantic
    # 2.8.0 is the first release with Python 3.13 support
    # (https://github.com/pydantic/pydantic/issues/11524), and 1.x never
    # shipped wheels for 3.12/3.13, so those Python versions only have a
    # single valid range.
    "pydantic": {
        "3.15": [VersionRange(None, None)],
        "3.14": [VersionRange("2.12.0", None)],
        "3.13": [VersionRange("2.8.0", None)],
        "3.12": [VersionRange("2.0.0", None)],
        "3.11": [VersionRange(None, "1.10.13"), VersionRange("2.0.0", None)],
        "3.10": [VersionRange(None, "1.10.13"), VersionRange("2.0.0", None)],
        "3.9": [VersionRange(None, "1.10.13"), VersionRange("2.0.0", None)],
    },
    "requests": {
        "3.15": [VersionRange(None, None)],
        "3.14": [VersionRange(None, None)],
        "3.13": [VersionRange(None, None)],
        "3.12": [VersionRange(None, None)],
        "3.11": [VersionRange(None, None)],
        "3.10": [VersionRange(None, None)],
        "3.9": [VersionRange(None, None)],
    },
    # https://github.com/scikit-learn/scikit-learn/releases
    "scikit-learn": {
        "3.15": [VersionRange(None, None)],
        "3.14": [VersionRange("1.7.2", None)],
        "3.13": [VersionRange("1.6.0", None)],
        "3.12": [VersionRange("1.3.1", None)],
        "3.11": [VersionRange("1.2.0", None)],
        "3.10": [VersionRange("1.1.0", "1.7.2")],
        "3.9": [VersionRange(None, "1.6.1")],
    },
    # https://github.com/scipy/scipy/releases/
    "scipy": {
        "3.15": [VersionRange(None, None)],
        "3.14": [VersionRange("1.16.1", None)],
        "3.13": [VersionRange("1.14.1", None)],
        "3.12": [VersionRange("1.12.0", None)],
        "3.11": [VersionRange("1.10.0", "1.17.1")],
        "3.10": [VersionRange("1.8.0", "1.15.3")],
        "3.9": [VersionRange(None, "1.13.1")],
    },
    # https://github.com/pytorch/pytorch/releases
    "torch": {
        "3.15": [VersionRange(None, None)],
        "3.14": [VersionRange("2.9.0", None)],
        "3.13": [VersionRange("2.6.0", None)],
        "3.12": [VersionRange("2.4.0", None)],
        "3.11": [VersionRange("2.0.0", None)],
        "3.10": [VersionRange("1.11.0", None)],
        "3.9": [VersionRange(None, "2.8.0")],
    },
    # https://docs.xarray.dev/en/stable/whats-new.html
    "xarray": {
        "3.15": [VersionRange(None, None)],
        "3.14": [VersionRange(None, None)],
        "3.13": [VersionRange(None, None)],
        "3.12": [VersionRange(None, None)],
        "3.11": [VersionRange(None, None)],
        "3.10": [VersionRange(None, "2025.6.1")],
        "3.9": [VersionRange(None, "2024.7.0")],
    },
}


def register_defaults(registry: CompatRegistry) -> None:
    r"""Populate a registry's base layer with the default package
    compatibility constraints.

    These are the human-curated constraints, so they overwrite any
    matching automatically discovered entry already registered in the
    base layer (see ``feu.compat.discovered.register_discovered``).

    Args:
        registry: The registry to populate.
    """
    mapping: dict[str, dict[Target, list[VersionRange]]] = {
        pkg_name: {
            Target(python_version=python_version): ranges
            for python_version, ranges in versions.items()
        }
        for pkg_name, versions in DEFAULT_COMPAT.items()
    }
    registry.register_many(mapping, layer="base", exist_ok=True)
