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
    "rich_available",
    "rich_not_available",
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
    is_rich_available,
    is_urllib3_available,
)
from feu.install import is_pip_available, is_pipx_available, is_uv_available


def _skipif_marks(
    is_available: bool, display_name: str
) -> tuple[pytest.MarkDecorator, pytest.MarkDecorator]:
    r"""Return a ``(<name>_available, <name>_not_available)`` pair of
    ``skipif`` marks for an optional dependency."""
    return (
        pytest.mark.skipif(not is_available, reason=f"Requires {display_name}"),
        pytest.mark.skipif(is_available, reason=f"Skip if {display_name} is available"),
    )


click_available: pytest.MarkDecorator
click_not_available: pytest.MarkDecorator
click_available, click_not_available = _skipif_marks(is_click_available(), "click")
git_available: pytest.MarkDecorator
git_not_available: pytest.MarkDecorator
git_available, git_not_available = _skipif_marks(is_git_available(), "git")
jax_available: pytest.MarkDecorator
jax_not_available: pytest.MarkDecorator
jax_available, jax_not_available = _skipif_marks(is_package_available("jax"), "JAX")
matplotlib_available: pytest.MarkDecorator
matplotlib_not_available: pytest.MarkDecorator
matplotlib_available, matplotlib_not_available = _skipif_marks(
    is_package_available("matplotlib"), "matplotlib"
)
numpy_available: pytest.MarkDecorator
numpy_not_available: pytest.MarkDecorator
numpy_available, numpy_not_available = _skipif_marks(is_package_available("numpy"), "NumPy")
pandas_available: pytest.MarkDecorator
pandas_not_available: pytest.MarkDecorator
pandas_available, pandas_not_available = _skipif_marks(is_package_available("pandas"), "pandas")
pip_available: pytest.MarkDecorator
pip_not_available: pytest.MarkDecorator
pip_available, pip_not_available = _skipif_marks(is_pip_available(), "pip")
pipx_available: pytest.MarkDecorator
pipx_not_available: pytest.MarkDecorator
pipx_available, pipx_not_available = _skipif_marks(is_pipx_available(), "pipx")
polars_available: pytest.MarkDecorator
polars_not_available: pytest.MarkDecorator
polars_available, polars_not_available = _skipif_marks(is_package_available("polars"), "polars")
pyarrow_available: pytest.MarkDecorator
pyarrow_not_available: pytest.MarkDecorator
pyarrow_available, pyarrow_not_available = _skipif_marks(is_package_available("pyarrow"), "pyarrow")
requests_available: pytest.MarkDecorator
requests_not_available: pytest.MarkDecorator
requests_available, requests_not_available = _skipif_marks(is_requests_available(), "requests")
rich_available: pytest.MarkDecorator
rich_not_available: pytest.MarkDecorator
rich_available, rich_not_available = _skipif_marks(is_rich_available(), "rich")
scipy_available: pytest.MarkDecorator
scipy_not_available: pytest.MarkDecorator
scipy_available, scipy_not_available = _skipif_marks(is_package_available("scipy"), "scipy")
sklearn_available: pytest.MarkDecorator
sklearn_not_available: pytest.MarkDecorator
sklearn_available, sklearn_not_available = _skipif_marks(is_package_available("sklearn"), "sklearn")
torch_available: pytest.MarkDecorator
torch_not_available: pytest.MarkDecorator
torch_available, torch_not_available = _skipif_marks(is_package_available("torch"), "PyTorch")
urllib3_available: pytest.MarkDecorator
urllib3_not_available: pytest.MarkDecorator
urllib3_available, urllib3_not_available = _skipif_marks(is_urllib3_available(), "urllib3")
uv_available: pytest.MarkDecorator
uv_not_available: pytest.MarkDecorator
uv_available, uv_not_available = _skipif_marks(is_uv_available(), "uv")
xarray_available: pytest.MarkDecorator
xarray_not_available: pytest.MarkDecorator
xarray_available, xarray_not_available = _skipif_marks(is_package_available("xarray"), "xarray")
