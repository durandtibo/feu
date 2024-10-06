from __future__ import annotations

import pytest
from coola import objects_are_equal
from coola.testing import (
    jax_available,
    numpy_available,
    pandas_available,
    pyarrow_available,
    torch_available,
    xarray_available,
)
from coola.utils import package_available

requests_available = pytest.mark.skipif(
    not package_available("requests"), reason="Requires requests"
)
sklearn_available = pytest.mark.skipif(not package_available("sklearn"), reason="Requires sklearn")
scipy_available = pytest.mark.skipif(not package_available("scipy"), reason="Requires scipy")


@jax_available
def test_jax() -> None:
    import jax.numpy as jnp  # local import because it is an optional dependency

    assert objects_are_equal(jnp.ones((2, 3)) + jnp.ones((2, 3)), jnp.full((2, 3), 2.0))


@numpy_available
def test_numpy() -> None:
    import numpy as np  # local import because it is an optional dependency

    assert objects_are_equal(np.ones((2, 3)) + np.ones((2, 3)), np.full((2, 3), 2.0))


@pandas_available
def test_pandas() -> None:
    import pandas as pd  # local import because it is an optional dependency

    assert objects_are_equal(
        pd.Series([1, 2, 3, 4, 5]) + pd.Series([5, 4, 3, 2, 1]), pd.Series([6, 6, 6, 6, 6])
    )


@pyarrow_available
def test_pyarrow() -> None:
    import pyarrow as pa  # local import because it is an optional dependency

    assert objects_are_equal(
        pa.array([1.0, 2.0, 3.0], type=pa.float64()), pa.array([1.0, 2.0, 3.0], type=pa.float64())
    )


@requests_available
def test_requests() -> None:
    import requests  # local import because it is an optional dependency

    r = requests.get("https://api.github.com/events", timeout=10)
    assert r.status_code in {200, 403}


@sklearn_available
def test_sklearn() -> None:
    from sklearn.svm import SVC  # local import because it is an optional dependency

    model = SVC(C=0.1)
    assert model.C == 0.1


@scipy_available
def test_scipy() -> None:
    from scipy import stats  # local import because it is an optional dependency

    assert stats.norm.cdf(0) == 0.5


@torch_available
def test_torch() -> None:
    import torch  # local import because it is an optional dependency

    assert objects_are_equal(torch.ones(2, 3) + torch.ones(2, 3), torch.full((2, 3), 2.0))


@xarray_available
def test_xarray() -> None:
    import numpy as np  # local import because it is an optional dependency
    import xarray as xr

    assert objects_are_equal(
        xr.DataArray(np.array([1.0, 2.0, 3.0])) + xr.DataArray(np.array([1.0, 2.0, 3.0])),
        xr.DataArray(np.array([2.0, 4.0, 6.0])),
    )
