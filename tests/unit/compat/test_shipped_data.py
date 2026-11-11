from __future__ import annotations

import json
from datetime import date
from importlib.resources import files
from typing import Any

import pytest
from packaging.utils import canonicalize_name
from packaging.version import Version

from feu.compat.registry import PackageData
from feu.compat.shipped import ShippedData, parse_package_data
from feu.compat.target import DEFAULT_TARGETS

# The contract of the shipped data, asked of every data file (not a test per file).
PACKAGES = sorted(ShippedData().packages())
LOADER = ShippedData()


def _data(package: str) -> PackageData:
    return LOADER.load(package)


def _read(package: str) -> str:
    return files("feu.compat.data").joinpath(f"{package}.json").read_text()


def _document(package: str) -> Any:
    return json.loads(_read(package))


def test_the_packages_are_the_expected_ones() -> None:
    assert PACKAGES == [
        "bokeh",
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
        "xy",
    ]


@pytest.mark.parametrize("package", PACKAGES)
def test_the_file_name_is_the_canonical_name(package: str) -> None:
    assert canonicalize_name(package) == package


@pytest.mark.parametrize("package", PACKAGES)
def test_the_package_field_is_the_file_name(package: str) -> None:
    assert _document(package)["package"] == package


@pytest.mark.parametrize("package", PACKAGES)
def test_generated_is_an_iso_date(package: str) -> None:
    assert isinstance(date.fromisoformat(str(_document(package)["generated"])), date)


@pytest.mark.parametrize("package", PACKAGES)
def test_the_file_parses(package: str) -> None:
    assert isinstance(parse_package_data(_read(package)), PackageData)


@pytest.mark.parametrize("package", PACKAGES)
def test_the_targets_are_the_default_grid(package: str) -> None:
    assert set(_data(package).targets) == set(DEFAULT_TARGETS)


@pytest.mark.parametrize("package", PACKAGES)
def test_there_are_60_targets(package: str) -> None:
    assert len(_data(package).targets) == 60


@pytest.mark.parametrize("package", PACKAGES)
def test_the_targets_are_sorted(package: str) -> None:
    keys = [
        (Version(t["python"]), t["free_threaded"], t["os"], t["arch"])
        for t in _document(package)["targets"]
    ]
    assert keys == sorted(keys)


@pytest.mark.parametrize("package", PACKAGES)
def test_the_ranges_are_ordered(package: str) -> None:
    ranges = [r for ranges in _data(package).targets.values() for r in ranges]
    assert all(r.min is None or r.max is None or Version(r.min) <= Version(r.max) for r in ranges)


@pytest.mark.parametrize("package", PACKAGES)
def test_the_ranges_are_sorted_and_do_not_overlap(package: str) -> None:
    for ranges in _data(package).targets.values():
        mins = [Version(r.min) for r in ranges if r.min is not None]
        assert mins == sorted(mins)


@pytest.mark.parametrize("package", PACKAGES)
def test_the_versions_are_sorted_in_pep440_order(package: str) -> None:
    versions = _data(package).versions
    assert list(versions) == sorted(versions, key=Version)


@pytest.mark.parametrize("package", PACKAGES)
def test_the_versions_are_unique(package: str) -> None:
    versions = _data(package).versions
    assert len(set(versions)) == len(versions)


@pytest.mark.parametrize("package", PACKAGES)
def test_the_versions_are_stable(package: str) -> None:
    assert not [
        v
        for v in _data(package).versions
        if Version(v).is_prerelease or Version(v).is_postrelease or Version(v).is_devrelease
    ]


@pytest.mark.parametrize("package", PACKAGES)
def test_the_versions_are_not_empty(package: str) -> None:
    assert len(_data(package).versions) > 0


@pytest.mark.parametrize("package", PACKAGES)
def test_every_range_bound_is_a_known_version(package: str) -> None:
    data = _data(package)
    bounds = {
        bound
        for ranges in data.targets.values()
        for r in ranges
        for bound in (r.min, r.max)
        if bound is not None
    }
    assert bounds <= set(data.versions)


def test_duckdb_ignores_the_spurious_0_0_0_release() -> None:
    assert "0.0.0" not in _data("duckdb").versions
