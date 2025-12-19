r"""Define some utility functions for testing."""

from __future__ import annotations

__all__ = [
    "click_available",
    "click_not_available",
    "git_available",
    "git_not_available",
    "jax_available",
    "matplotlib_available",
    "numpy_available",
    "pandas_available",
    "pip_available",
    "pipx_available",
    "polars_available",
    "pyarrow_available",
    "requests_available",
    "requests_not_available",
    "scipy_available",
    "sklearn_available",
    "torch_available",
    "urllib3_available",
    "urllib3_not_available",
    "uv_available",
    "xarray_available",
]

import pytest

from feu.imports import (
    is_click_available,
    is_git_available,
    is_package_available,
    is_requests_available,
    is_urllib3_available,
)
from feu.install import is_pip_available, is_pipx_available, is_uv_available

click_available: pytest.MarkDecorator = pytest.mark.skipif(
    not is_click_available(), reason="Requires click"
)
click_not_available: pytest.MarkDecorator = pytest.mark.skipif(
    is_click_available(), reason="Skip if click is available"
)
git_available: pytest.MarkDecorator = pytest.mark.skipif(
    not is_git_available(), reason="Requires git"
)
git_not_available: pytest.MarkDecorator = pytest.mark.skipif(
    is_git_available(), reason="Skip if git is available"
)
jax_available: pytest.MarkDecorator = pytest.mark.skipif(
    not is_package_available("jax"), reason="Requires JAX"
)
matplotlib_available: pytest.MarkDecorator = pytest.mark.skipif(
    not is_package_available("matplotlib"), reason="Requires matplotlib"
)
numpy_available: pytest.MarkDecorator = pytest.mark.skipif(
    not is_package_available("numpy"), reason="Requires NumPy"
)
pandas_available: pytest.MarkDecorator = pytest.mark.skipif(
    not is_package_available("pandas"), reason="Requires pandas"
)
polars_available: pytest.MarkDecorator = pytest.mark.skipif(
    not is_package_available("polars"), reason="Requires polars"
)
pyarrow_available: pytest.MarkDecorator = pytest.mark.skipif(
    not is_package_available("pyarrow"), reason="Requires pyarrow"
)
requests_available: pytest.MarkDecorator = pytest.mark.skipif(
    not is_requests_available(), reason="Requires requests"
)
requests_not_available: pytest.MarkDecorator = pytest.mark.skipif(
    is_requests_available(), reason="Skip if requests is available"
)
sklearn_available: pytest.MarkDecorator = pytest.mark.skipif(
    not is_package_available("sklearn"), reason="Requires sklearn"
)
scipy_available: pytest.MarkDecorator = pytest.mark.skipif(
    not is_package_available("scipy"), reason="Requires scipy"
)
torch_available: pytest.MarkDecorator = pytest.mark.skipif(
    not is_package_available("torch"), reason="Requires PyTorch"
)
urllib3_available: pytest.MarkDecorator = pytest.mark.skipif(
    not is_urllib3_available(), reason="Requires urllib3"
)
urllib3_not_available: pytest.MarkDecorator = pytest.mark.skipif(
    is_urllib3_available(), reason="Skip if urllib3 is available"
)
xarray_available: pytest.MarkDecorator = pytest.mark.skipif(
    not is_package_available("xarray"), reason="Requires xarray"
)


pip_available: pytest.MarkDecorator = pytest.mark.skipif(
    not is_pip_available(), reason="Requires pip"
)
pipx_available: pytest.MarkDecorator = pytest.mark.skipif(
    not is_pipx_available(), reason="Requires pipx"
)
uv_available: pytest.MarkDecorator = pytest.mark.skipif(not is_uv_available(), reason="Requires uv")
