r"""Contain the default package version compatibility constraints."""

from __future__ import annotations

__all__ = ["DEFAULT_COMPAT", "register_defaults"]

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from feu.compat.registry import CompatRegistry

DEFAULT_COMPAT: dict[str, dict[str, dict[str, str | None]]] = {
    # https://click.palletsprojects.com/en/stable/changes/
    "click": {
        "3.15": {"min": "0.1", "max": None},
        "3.14": {"min": "0.1", "max": None},
        "3.13": {"min": "0.1", "max": None},
        "3.12": {"min": "0.1", "max": None},
        "3.11": {"min": "0.1", "max": None},
        "3.10": {"min": "0.1", "max": None},
        "3.9": {"min": "0.1", "max": "8.1.8"},
    },
    # https://github.com/duckdb/duckdb-python/releases
    "duckdb": {
        "3.15": {"min": "0.0.0", "max": None},
        "3.14": {"min": "0.0.0", "max": None},
        "3.13": {"min": "0.0.0", "max": None},
        "3.12": {"min": "0.0.0", "max": None},
        "3.11": {"min": "0.0.0", "max": None},
        "3.10": {"min": "0.0.0", "max": None},
        "3.9": {"min": "0.0.0", "max": "1.4.5"},
    },
    # https://pypi.org/project/jaxlib/#history
    "jax": {
        "3.15": {"min": "0.0", "max": None},
        "3.14": {"min": "0.0", "max": None},
        "3.13": {"min": "0.0", "max": None},
        "3.12": {"min": "0.0", "max": None},
        "3.11": {"min": "0.0", "max": "0.10.2"},
        "3.10": {"min": "0.0", "max": "0.6.2"},
        "3.9": {"min": "0.0", "max": "0.4.30"},
    },
    # https://matplotlib.org/stable/users/release_notes.html
    "matplotlib": {
        "3.15": {"min": "0.63.0", "max": None},
        "3.14": {"min": "0.63.0", "max": None},
        "3.13": {"min": "0.63.0", "max": None},
        "3.12": {"min": "0.63.0", "max": None},
        "3.11": {"min": "0.63.0", "max": None},
        "3.10": {"min": "0.63.0", "max": "3.10.9"},
        "3.9": {"min": "0.63.0", "max": "3.9.4"},
    },
    # https://numpy.org/devdocs/release.html
    "numpy": {
        "3.15": {"min": "0.9.6", "max": None},
        "3.14": {"min": "0.9.6", "max": None},
        "3.13": {"min": "0.9.6", "max": None},
        "3.12": {"min": "0.9.6", "max": None},
        "3.11": {"min": "0.9.6", "max": "2.4.6"},
        "3.10": {"min": "0.9.6", "max": "2.2.6"},
        "3.9": {"min": "0.9.6", "max": "2.0.2"},
    },
    # https://github.com/pandas-dev/pandas/releases
    # https://pandas.pydata.org/docs/whatsnew/index.html
    "pandas": {
        "3.15": {"min": "0.1", "max": None},
        "3.14": {"min": "0.1", "max": None},
        "3.13": {"min": "0.1", "max": None},
        "3.12": {"min": "0.1", "max": None},
        "3.11": {"min": "0.1", "max": None},
        "3.10": {"min": "0.1", "max": "2.3.3"},
        "3.9": {"min": "0.1", "max": "2.3.3"},
    },
    # https://arrow.apache.org/release/
    "pyarrow": {
        "3.15": {"min": "0.1.0", "max": None},
        "3.14": {"min": "0.1.0", "max": None},
        "3.13": {"min": "0.1.0", "max": None},
        "3.12": {"min": "0.1.0", "max": None},
        "3.11": {"min": "0.1.0", "max": None},
        "3.10": {"min": "0.1.0", "max": None},
        "3.9": {"min": "0.1.0", "max": "21.0.0"},
    },
    "pydantic": {
        "3.15": {"min": "0.0.1", "max": None},
        "3.14": {"min": "0.0.1", "max": None},
        "3.13": {"min": "0.0.1", "max": None},
        "3.12": {"min": "0.0.1", "max": None},
        "3.11": {"min": "0.0.1", "max": None},
        "3.10": {"min": "0.0.1", "max": None},
        "3.9": {"min": "0.0.1", "max": None},
    },
    "requests": {
        "3.15": {"min": "0.0.1", "max": None},
        "3.14": {"min": "0.0.1", "max": None},
        "3.13": {"min": "0.0.1", "max": None},
        "3.12": {"min": "0.0.1", "max": None},
        "3.11": {"min": "0.0.1", "max": None},
        "3.10": {"min": "0.0.1", "max": None},
        "3.9": {"min": "0.0.1", "max": "2.32.5"},
    },
    # https://github.com/scikit-learn/scikit-learn/releases
    "scikit-learn": {
        "3.15": {"min": "0.9", "max": None},
        "3.14": {"min": "0.9", "max": None},
        "3.13": {"min": "0.9", "max": None},
        "3.12": {"min": "0.9", "max": None},
        "3.11": {"min": "0.9", "max": None},
        "3.10": {"min": "0.9", "max": "1.7.2"},
        "3.9": {"min": "0.9", "max": "1.6.1"},
    },
    # https://github.com/scipy/scipy/releases/
    "scipy": {
        "3.15": {"min": "0.4.4", "max": None},
        "3.14": {"min": "0.4.4", "max": None},
        "3.13": {"min": "0.4.4", "max": None},
        "3.12": {"min": "0.4.4", "max": None},
        "3.11": {"min": "0.4.4", "max": "1.17.1"},
        "3.10": {"min": "0.4.4", "max": "1.15.3"},
        "3.9": {"min": "0.4.4", "max": "1.13.1"},
    },
    # https://github.com/pytorch/pytorch/releases
    "torch": {
        "3.15": {"min": "1.0.0", "max": None},
        "3.14": {"min": "1.0.0", "max": None},
        "3.13": {"min": "1.0.0", "max": None},
        "3.12": {"min": "1.0.0", "max": None},
        "3.11": {"min": "1.0.0", "max": None},
        "3.10": {"min": "1.0.0", "max": None},
        "3.9": {"min": "1.0.0", "max": "2.8.0"},
    },
    # https://docs.xarray.dev/en/stable/whats-new.html
    "xarray": {
        "3.15": {"min": "0.7.0", "max": None},
        "3.14": {"min": "0.7.0", "max": None},
        "3.13": {"min": "0.7.0", "max": None},
        "3.12": {"min": "0.7.0", "max": None},
        "3.11": {"min": "0.7.0", "max": None},
        "3.10": {"min": "0.7.0", "max": "2025.6.1"},
        "3.9": {"min": "0.7.0", "max": "2024.7.0"},
    },
}


def register_defaults(registry: CompatRegistry) -> None:
    r"""Populate a registry with the default package compatibility
    constraints.

    Args:
        registry: The registry to populate.
    """
    registry.register_many(DEFAULT_COMPAT)
