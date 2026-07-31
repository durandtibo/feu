r"""Contain the default package version compatibility constraints."""

from __future__ import annotations

__all__ = ["DEFAULT_COMPAT", "register_defaults"]

from typing import TYPE_CHECKING

from feu.compat.registry import VersionRange
from feu.compat.target import Target

if TYPE_CHECKING:
    from feu.compat.registry import CompatRegistry

DEFAULT_COMPAT: dict[str, dict[str, dict[str, str | None]]] = {
    # https://click.palletsprojects.com/en/stable/changes/
    "click": {
        "3.15": {"min": None, "max": None},
        "3.14": {"min": None, "max": None},
        "3.13": {"min": None, "max": None},
        "3.12": {"min": None, "max": None},
        "3.11": {"min": None, "max": None},
        "3.10": {"min": None, "max": None},
        "3.9": {"min": None, "max": "8.1.8"},
    },
    # https://github.com/duckdb/duckdb-python/releases
    "duckdb": {
        "3.15": {"min": None, "max": None},
        "3.14": {"min": "1.4.2", "max": None},
        "3.13": {"min": None, "max": None},
        "3.12": {"min": None, "max": None},
        "3.11": {"min": None, "max": None},
        "3.10": {"min": None, "max": None},
    },
    # https://pypi.org/project/jaxlib/#history
    "jax": {
        "3.15": {"min": None, "max": None},
        "3.14": {"min": "0.7.1", "max": None},
        "3.13": {"min": "0.4.34", "max": None},
        "3.12": {"min": "0.4.17", "max": None},
        "3.11": {"min": "0.4.6", "max": None},
        "3.10": {"min": "0.4.6", "max": "0.6.2"},
        "3.9": {"min": "0.4.6", "max": "0.4.30"},
    },
    # https://matplotlib.org/stable/users/release_notes.html
    "matplotlib": {
        "3.15": {"min": None, "max": None},
        "3.14": {"min": "3.10.5", "max": None},
        "3.13": {"min": None, "max": None},
        "3.12": {"min": None, "max": None},
        "3.11": {"min": None, "max": None},
        "3.10": {"min": None, "max": None},
        "3.9": {"min": None, "max": "3.9.4"},
    },
    # https://numpy.org/devdocs/release.html
    "numpy": {
        "3.15": {"min": None, "max": None},
        "3.14": {"min": "2.3.0", "max": None},
        "3.13": {"min": "2.1.0", "max": None},
        "3.12": {"min": "1.26.0", "max": None},
        "3.11": {"min": "1.23.2", "max": "2.4.6"},
        "3.10": {"min": "1.21.3", "max": "2.2.6"},
        "3.9": {"min": "1.19.3", "max": "2.0.2"},
    },
    # https://github.com/pandas-dev/pandas/releases
    # https://pandas.pydata.org/docs/whatsnew/index.html
    "pandas": {
        "3.15": {"min": None, "max": None},
        "3.14": {"min": "2.3.3", "max": None},
        "3.13": {"min": "2.2.3", "max": None},
        "3.12": {"min": "2.1.1", "max": None},
        "3.11": {"min": "1.3.4", "max": None},
        "3.10": {"min": "1.3.3", "max": "2.3.3"},
        "3.9": {"min": None, "max": "2.3.3"},
    },
    # https://arrow.apache.org/release/
    "pyarrow": {
        "3.15": {"min": None, "max": None},
        "3.14": {"min": "22.0.0", "max": None},
        "3.13": {"min": "18.0.0", "max": None},
        "3.12": {"min": "14.0.0", "max": None},
        "3.11": {"min": "10.0.1", "max": None},
        "3.10": {"min": "6.0.0", "max": None},
        "3.9": {"min": "3.0.0", "max": "16.1.0"},
    },
    "pydantic": {
        "3.15": {"min": None, "max": None},
        "3.14": {"min": "2.12.0", "max": None},
        "3.13": {"min": "2.8.0", "max": None},
        "3.12": {"min": None, "max": None},
        "3.11": {"min": None, "max": None},
        "3.10": {"min": None, "max": None},
    },
    "requests": {
        "3.15": {"min": None, "max": None},
        "3.14": {"min": None, "max": None},
        "3.13": {"min": None, "max": None},
        "3.12": {"min": None, "max": None},
        "3.11": {"min": None, "max": None},
        "3.10": {"min": None, "max": None},
        "3.9": {"min": None, "max": None},
    },
    # https://github.com/scikit-learn/scikit-learn/releases
    "scikit-learn": {
        "3.15": {"min": None, "max": None},
        "3.14": {"min": "1.7.2", "max": None},
        "3.13": {"min": "1.6.0", "max": None},
        "3.12": {"min": "1.3.1", "max": None},
        "3.11": {"min": "1.2.0", "max": None},
        "3.10": {"min": "1.1.0", "max": "1.7.2"},
        "3.9": {"min": None, "max": "1.6.1"},
    },
    # https://github.com/scipy/scipy/releases/
    "scipy": {
        "3.15": {"min": None, "max": None},
        "3.14": {"min": "1.16.1", "max": None},
        "3.13": {"min": "1.14.1", "max": None},
        "3.12": {"min": "1.12.0", "max": None},
        "3.11": {"min": "1.10.0", "max": "1.17.1"},
        "3.10": {"min": "1.8.0", "max": "1.15.3"},
        "3.9": {"min": None, "max": "1.13.1"},
    },
    # https://github.com/pytorch/pytorch/releases
    "torch": {
        "3.15": {"min": None, "max": None},
        "3.14": {"min": "2.9.0", "max": None},
        "3.13": {"min": "2.6.0", "max": None},
        "3.12": {"min": "2.4.0", "max": None},
        "3.11": {"min": "2.0.0", "max": None},
        "3.10": {"min": "1.11.0", "max": None},
        "3.9": {"min": None, "max": "2.8.0"},
    },
    # https://docs.xarray.dev/en/stable/whats-new.html
    "xarray": {
        "3.15": {"min": None, "max": None},
        "3.14": {"min": None, "max": None},
        "3.13": {"min": None, "max": None},
        "3.12": {"min": None, "max": None},
        "3.11": {"min": None, "max": None},
        "3.10": {"min": None, "max": "2025.6.1"},
        "3.9": {"min": None, "max": "2024.7.0"},
    },
}


def register_defaults(registry: CompatRegistry) -> None:
    r"""Populate a registry's base layer with the default package
    compatibility constraints.

    Args:
        registry: The registry to populate.
    """
    mapping: dict[str, dict[Target, list[VersionRange]]] = {
        pkg_name: {
            Target(python_version=python_version): [
                VersionRange(config["min"], config["max"])
            ]
            for python_version, config in versions.items()
        }
        for pkg_name, versions in DEFAULT_COMPAT.items()
    }
    registry.register_many(mapping, layer="base")
