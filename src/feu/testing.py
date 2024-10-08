r"""Define some utility functions for testing."""

from __future__ import annotations

__all__ = [
    "click_available",
    "jax_available",
    "numpy_available",
    "pandas_available",
    "polars_available",
    "pyarrow_available",
    "requests_available",
    "scipy_available",
    "sklearn_available",
    "torch_available",
    "xarray_available",
]

import pytest

from feu.imports import is_click_available, is_package_available

click_available = pytest.mark.skipif(not is_click_available(), reason="Requires click")
jax_available = pytest.mark.skipif(not is_package_available("jax"), reason="Requires JAX")
numpy_available = pytest.mark.skipif(not is_package_available("numpy"), reason="Requires NumPy")
pandas_available = pytest.mark.skipif(not is_package_available("pandas"), reason="Requires pandas")
polars_available = pytest.mark.skipif(not is_package_available("polars"), reason="Requires polars")
pyarrow_available = pytest.mark.skipif(
    not is_package_available("pyarrow"), reason="Requires pyarrow"
)
torch_available = pytest.mark.skipif(not is_package_available("torch"), reason="Requires PyTorch")
requests_available = pytest.mark.skipif(
    not is_package_available("requests"), reason="Requires requests"
)
sklearn_available = pytest.mark.skipif(
    not is_package_available("sklearn"), reason="Requires sklearn"
)
scipy_available = pytest.mark.skipif(not is_package_available("scipy"), reason="Requires scipy")
xarray_available = pytest.mark.skipif(not is_package_available("xarray"), reason="Requires xarray")
