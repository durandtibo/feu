from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from feu.compat.registry import PackageData, VersionRange
from feu.compat.shipped import ShippedData, format_package_data, parse_package_data
from feu.compat.target import Target

LINUX_312 = Target("3.12", False, "linux", "x86_64")
LINUX_39 = Target("3.9", False, "linux", "x86_64")
LINUX_310 = Target("3.10", False, "linux", "x86_64")
LINUX_313T = Target("3.13", True, "linux", "x86_64")
LINUX_313 = Target("3.13", False, "linux", "x86_64")
MACOS_312 = Target("3.12", False, "macos", "arm64")

#######################################
#     Tests for format_package_data   #
#######################################


def test_format_package_data_whole_output() -> None:
    text = format_package_data(
        "numpy",
        "2026-11-09",
        {LINUX_312: [VersionRange("1.26.0", None)], MACOS_312: []},
    )
    assert text == (
        "{\n"
        '  "package": "numpy",\n'
        '  "generated": "2026-11-09",\n'
        '  "targets": [\n'
        '    {"python": "3.12", "free_threaded": false, "os": "linux", "arch": "x86_64", '
        '"ranges": [["1.26.0", null]]},\n'
        '    {"python": "3.12", "free_threaded": false, "os": "macos", "arch": "arm64", '
        '"ranges": []}\n'
        "  ]\n"
        "}\n"
    )


def test_format_package_data_is_valid_json() -> None:
    text = format_package_data("numpy", "2026-11-09", {LINUX_312: []})
    assert json.loads(text)["package"] == "numpy"


def test_format_package_data_sorts_the_targets_by_python_version_not_by_string() -> None:
    text = format_package_data("numpy", "2026-11-09", {LINUX_310: [], LINUX_39: [], LINUX_313: []})
    assert [t["python"] for t in json.loads(text)["targets"]] == ["3.9", "3.10", "3.13"]


def test_format_package_data_sorts_free_threaded_after_regular() -> None:
    text = format_package_data("numpy", "2026-11-09", {LINUX_313T: [], LINUX_313: []})
    assert [t["free_threaded"] for t in json.loads(text)["targets"]] == [False, True]


def test_format_package_data_is_independent_of_the_input_order() -> None:
    first = format_package_data("n", "2026-11-09", {LINUX_39: [], LINUX_310: []})
    second = format_package_data("n", "2026-11-09", {LINUX_310: [], LINUX_39: []})
    assert first == second


def test_format_package_data_no_target() -> None:
    assert json.loads(format_package_data("n", "2026-11-09", {})) == {
        "package": "n",
        "generated": "2026-11-09",
        "targets": [],
    }


def test_format_package_data_ends_with_a_newline() -> None:
    assert format_package_data("n", "2026-11-09", {}).endswith("}\n")


def test_format_package_data_unspecified_platform() -> None:
    text = format_package_data("n", "2026-11-09", {Target("3.11"): []})
    assert json.loads(text)["targets"][0]["os"] is None


#####################################
#     Tests for parse_package_data  #
#####################################


def test_parse_package_data_whole_output() -> None:
    text = format_package_data(
        "numpy",
        "2026-11-09",
        {LINUX_312: [VersionRange("1.26.0", None)], MACOS_312: [VersionRange("2.0.0", "2.0.0")]},
    )
    assert parse_package_data(text) == PackageData(
        targets={
            LINUX_312: [VersionRange("1.26.0", None)],
            MACOS_312: [VersionRange("2.0.0", "2.0.0")],
        },
    )


def test_parse_package_data_round_trip_keeps_an_unsupported_target() -> None:
    text = format_package_data("n", "2026-11-09", {LINUX_312: []})
    assert parse_package_data(text).targets == {LINUX_312: []}


def test_parse_package_data_unbounded_min() -> None:
    text = format_package_data("n", "2026-11-09", {LINUX_312: [VersionRange(None, "1.0")]})
    assert parse_package_data(text).targets == {LINUX_312: [VersionRange(None, "1.0")]}


@pytest.mark.parametrize(
    "text",
    [
        "{}",
        '{"package": "n"}',
        '{"targets": [{"python": "3.12"}]}',
        (
            '{"targets": [{"python": "3.12", "free_threaded": false, '
            '"os": "linux", "arch": "x86_64", "ranges": [["1.0"]]}]}'
        ),
        '{"targets": 1}',
    ],
)
def test_parse_package_data_invalid_format(text: str) -> None:
    with pytest.raises(ValueError, match="invalid compatibility data"):
        parse_package_data(text)


def test_parse_package_data_invalid_json() -> None:
    with pytest.raises(ValueError, match="Expecting value"):
        parse_package_data("not json")


def test_parse_package_data_invalid_target() -> None:
    text = (
        '{"targets": [{"python": "3.12.1", "free_threaded": false, '
        '"os": "linux", "arch": "x86_64", "ranges": []}]}'
    )
    with pytest.raises(ValueError, match="invalid python_version"):
        parse_package_data(text)


###############################
#     Tests for ShippedData   #
###############################


def test_shipped_data_repr() -> None:
    assert repr(ShippedData()) == "ShippedData()"


def test_shipped_data_packages_contains_numpy() -> None:
    assert "numpy" in ShippedData().packages()


def test_shipped_data_packages_are_sorted() -> None:
    packages = list(ShippedData().packages())
    assert packages == sorted(packages)


def test_shipped_data_packages_do_not_parse_any_file() -> None:
    with patch("feu.compat.shipped.parse_package_data") as parse_mock:
        ShippedData().packages()
        parse_mock.assert_not_called()


def test_shipped_data_packages_ignore_the_other_files() -> None:
    assert "__init__" not in ShippedData().packages()


def test_shipped_data_packages_use_the_file_names() -> None:
    assert "scikit-learn" in ShippedData().packages()


def test_shipped_data_load() -> None:
    data = ShippedData().load("numpy")
    assert data.targets


def test_shipped_data_load_targets_are_targets() -> None:
    data = ShippedData().load("numpy")
    assert all(isinstance(target, Target) for target in data.targets)


def test_shipped_data_load_missing_package() -> None:
    with pytest.raises(FileNotFoundError, match="not-a-package"):
        ShippedData().load("not-a-package")
