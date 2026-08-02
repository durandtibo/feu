from __future__ import annotations

from feu.compat.defaults import DEFAULT_COMPAT, register_defaults
from feu.compat.registry import CompatRegistry, VersionRange
from feu.compat.target import Target

#############################################
#     Tests for register_defaults           #
#############################################


def test_register_defaults_populates_registry() -> None:
    registry = CompatRegistry()
    register_defaults(registry)
    assert registry.state["numpy"][Target(python_version="3.11")] == [
        VersionRange("1.23.2", "2.4.6")
    ]


def test_register_defaults_numpy_entry() -> None:
    registry = CompatRegistry()
    register_defaults(registry)
    assert registry.get_config(pkg_name="numpy", target=Target(python_version="3.11")) == [
        VersionRange("1.23.2", "2.4.6")
    ]


def test_register_defaults_pydantic_has_disjoint_ranges_on_python_3_11() -> None:
    registry = CompatRegistry()
    register_defaults(registry)
    ranges = registry.get_config(pkg_name="pydantic", target=Target(python_version="3.11"))
    assert len(ranges) == 2
    assert ranges[0] == VersionRange(None, "1.10.13")
    assert ranges[1].min == "2.0.0"


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


def test_default_compat_values_are_version_ranges() -> None:
    for pkg_versions in DEFAULT_COMPAT.values():
        for ranges in pkg_versions.values():
            assert isinstance(ranges, list)
            assert all(isinstance(r, VersionRange) for r in ranges)
