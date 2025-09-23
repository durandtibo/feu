r"""Define some utility functions for testing."""

from __future__ import annotations

__all__ = [
    "click_available",
    "git_available",
    "jax_available",
    "matplotlib_available",
    "numpy_available",
    "pandas_available",
    "pip_available",
    "pipx_available",
    "polars_available",
    "pyarrow_available",
    "requests_available",
    "scipy_available",
    "sklearn_available",
    "torch_available",
    "uv_available",
    "xarray_available",
]

import pytest

from feu.imports import (
    is_click_available,
    is_git_available,
    is_package_available,
    is_requests_available,
)
from feu.install import is_pip_available, is_pipx_available, is_uv_available

click_available = pytest.mark.skipif(not is_click_available(), reason="Requires click")
git_available = pytest.mark.skipif(not is_git_available(), reason="Requires git")
jax_available = pytest.mark.skipif(not is_package_available("jax"), reason="Requires JAX")
matplotlib_available = pytest.mark.skipif(
    not is_package_available("matplotlib"), reason="Requires matplotlib"
)
numpy_available = pytest.mark.skipif(not is_package_available("numpy"), reason="Requires NumPy")
pandas_available = pytest.mark.skipif(not is_package_available("pandas"), reason="Requires pandas")
polars_available = pytest.mark.skipif(not is_package_available("polars"), reason="Requires polars")
pyarrow_available = pytest.mark.skipif(
    not is_package_available("pyarrow"), reason="Requires pyarrow"
)
torch_available = pytest.mark.skipif(not is_package_available("torch"), reason="Requires PyTorch")
requests_available = pytest.mark.skipif(not is_requests_available(), reason="Requires requests")
sklearn_available = pytest.mark.skipif(
    not is_package_available("sklearn"), reason="Requires sklearn"
)
scipy_available = pytest.mark.skipif(not is_package_available("scipy"), reason="Requires scipy")
xarray_available = pytest.mark.skipif(not is_package_available("xarray"), reason="Requires xarray")


pip_available = pytest.mark.skipif(not is_pip_available(), reason="Requires pip")
pipx_available = pytest.mark.skipif(not is_pipx_available(), reason="Requires pipx")
uv_available = pytest.mark.skipif(not is_uv_available(), reason="Requires uv")
