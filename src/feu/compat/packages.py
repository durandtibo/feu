r"""Contain utility functions to inspect the default package
compatibility registry."""

from __future__ import annotations

__all__ = ["get_package_names"]


def get_package_names() -> list[str]:
    r"""Return the names of the packages with default compatibility
    constraints.

    Returns:
        The list of package names defined in the default
        compatibility registry, in the order they are declared.

    Example:
        ```pycon
        >>> from feu.compat.packages import get_package_names
        >>> names = get_package_names()
        >>> "numpy" in names
        True

        ```
    """
    return [
        "click",
        "duckdb",
        "jax",
        "matplotlib",
        "numpy",
        "pandas",
        "polars",
        "pyarrow",
        "pydantic",
        "requests",
        "safetensors",
        "scikit-learn",
        "scipy",
        "torch",
        "xarray",
    ]
