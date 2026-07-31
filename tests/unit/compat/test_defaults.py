from __future__ import annotations

from feu.compat.defaults import DEFAULT_COMPAT, register_defaults
from feu.compat.registry import CompatRegistry
from feu.compat.target import Target

#############################################
#     Tests for register_defaults           #
#############################################


def test_register_defaults_populates_base_layer() -> None:
    registry = CompatRegistry()
    register_defaults(registry)
    assert registry.overrides == {}
    assert registry.base["numpy"][Target(python_version="3.11")] == {
        "min": "1.23.2",
        "max": "2.4.6",
    }


def test_register_defaults_numpy_entry() -> None:
    registry = CompatRegistry()
    register_defaults(registry)
    assert registry.get_config(pkg_name="numpy", target=Target(python_version="3.11")) == {
        "min": "1.23.2",
        "max": "2.4.6",
    }


def test_default_compat_contains_expected_packages() -> None:
    assert set(DEFAULT_COMPAT.keys()) == {
        "click",
        "duckdb",
        "jax",
        "matplotlib",
        "numpy",
        "pandas",
        "pyarrow",
        "pydantic",
        "requests",
        "scikit-learn",
        "scipy",
        "torch",
        "xarray",
    }
