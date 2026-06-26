r"""Define some utility functions for testing."""

from __future__ import annotations

__all__ = [
    "click_available",
    "click_not_available",
    "git_available",
    "git_not_available",
    "jax_available",
    "jax_not_available",
    "matplotlib_available",
    "matplotlib_not_available",
    "numpy_available",
    "numpy_not_available",
    "pandas_available",
    "pandas_not_available",
    "pip_available",
    "pip_not_available",
    "pipx_available",
    "pipx_not_available",
    "polars_available",
    "polars_not_available",
    "pyarrow_available",
    "pyarrow_not_available",
    "requests_available",
    "requests_not_available",
    "scipy_available",
    "scipy_not_available",
    "sklearn_available",
    "sklearn_not_available",
    "torch_available",
    "torch_not_available",
    "urllib3_available",
    "urllib3_not_available",
    "uv_available",
    "uv_not_available",
    "xarray_available",
    "xarray_not_available",
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
jax_not_available: pytest.MarkDecorator = pytest.mark.skipif(
    is_package_available("jax"), reason="Skip if JAX is available"
)

matplotlib_available: pytest.MarkDecorator = pytest.mark.skipif(
    not is_package_available("matplotlib"), reason="Requires matplotlib"
)
matplotlib_not_available: pytest.MarkDecorator = pytest.mark.skipif(
    is_package_available("matplotlib"), reason="Skip if matplotlib is available"
)

numpy_available: pytest.MarkDecorator = pytest.mark.skipif(
    not is_package_available("numpy"), reason="Requires NumPy"
)
numpy_not_available: pytest.MarkDecorator = pytest.mark.skipif(
    is_package_available("numpy"), reason="Skip if NumPy is available"
)

pandas_available: pytest.MarkDecorator = pytest.mark.skipif(
    not is_package_available("pandas"), reason="Requires pandas"
)
pandas_not_available: pytest.MarkDecorator = pytest.mark.skipif(
    is_package_available("pandas"), reason="Skip if pandas is available"
)

polars_available: pytest.MarkDecorator = pytest.mark.skipif(
    not is_package_available("polars"), reason="Requires polars"
)
polars_not_available: pytest.MarkDecorator = pytest.mark.skipif(
    is_package_available("polars"), reason="Skip if polars is available"
)

pyarrow_available: pytest.MarkDecorator = pytest.mark.skipif(
    not is_package_available("pyarrow"), reason="Requires pyarrow"
)
pyarrow_not_available: pytest.MarkDecorator = pytest.mark.skipif(
    is_package_available("pyarrow"), reason="Skip if pyarrow is available"
)

requests_available: pytest.MarkDecorator = pytest.mark.skipif(
    not is_requests_available(), reason="Requires requests"
)
requests_not_available: pytest.MarkDecorator = pytest.mark.skipif(
    is_requests_available(), reason="Skip if requests is available"
)

scipy_available: pytest.MarkDecorator = pytest.mark.skipif(
    not is_package_available("scipy"), reason="Requires scipy"
)
scipy_not_available: pytest.MarkDecorator = pytest.mark.skipif(
    is_package_available("scipy"), reason="Skip if scipy is available"
)

sklearn_available: pytest.MarkDecorator = pytest.mark.skipif(
    not is_package_available("sklearn"), reason="Requires sklearn"
)
sklearn_not_available: pytest.MarkDecorator = pytest.mark.skipif(
    is_package_available("sklearn"), reason="Skip if sklearn is available"
)

torch_available: pytest.MarkDecorator = pytest.mark.skipif(
    not is_package_available("torch"), reason="Requires PyTorch"
)
torch_not_available: pytest.MarkDecorator = pytest.mark.skipif(
    is_package_available("torch"), reason="Skip if PyTorch is available"
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
xarray_not_available: pytest.MarkDecorator = pytest.mark.skipif(
    is_package_available("xarray"), reason="Skip if xarray is available"
)

pip_available: pytest.MarkDecorator = pytest.mark.skipif(
    not is_pip_available(), reason="Requires pip"
)
pip_not_available: pytest.MarkDecorator = pytest.mark.skipif(
    is_pip_available(), reason="Skip if pip is available"
)

pipx_available: pytest.MarkDecorator = pytest.mark.skipif(
    not is_pipx_available(), reason="Requires pipx"
)
pipx_not_available: pytest.MarkDecorator = pytest.mark.skipif(
    is_pipx_available(), reason="Skip if pipx is available"
)

uv_available: pytest.MarkDecorator = pytest.mark.skipif(not is_uv_available(), reason="Requires uv")
uv_not_available: pytest.MarkDecorator = pytest.mark.skipif(
    is_uv_available(), reason="Skip if uv is available"
)
