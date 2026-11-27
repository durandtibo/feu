# `feu.testing`

The `pytest` marks to skip a test depending on the availability of an optional dependency. The module
needs `pytest`. See the [usage guide](../usage.md#testing-utilities).

| Dependency         | Skips the test if not available | Skips the test if available      |
| ------------------ | ------------------------------- | -------------------------------- |
| `click`            | `click_available`               | `click_not_available`            |
| `git`              | `git_available`                 | `git_not_available`              |
| `jax`              | `jax_available`                 | `jax_not_available`              |
| `matplotlib`       | `matplotlib_available`          | `matplotlib_not_available`       |
| `numpy`            | `numpy_available`               | `numpy_not_available`            |
| `pandas`           | `pandas_available`              | `pandas_not_available`           |
| `pip`              | `pip_available`                 | `pip_not_available`              |
| `polars`           | `polars_available`              | `polars_not_available`           |
| `pyarrow`          | `pyarrow_available`             | `pyarrow_not_available`          |
| `pytest_benchmark` | `pytest_benchmark_available`    | `pytest_benchmark_not_available` |
| `requests`         | `requests_available`            | `requests_not_available`         |
| `rich`             | `rich_available`                | `rich_not_available`             |
| `scipy`            | `scipy_available`               | `scipy_not_available`            |
| `sklearn`          | `sklearn_available`             | `sklearn_not_available`          |
| `torch`            | `torch_available`               | `torch_not_available`            |
| `uv`               | `uv_available`                  | `uv_not_available`               |
| `xarray`           | `xarray_available`              | `xarray_not_available`           |

::: feu.testing
