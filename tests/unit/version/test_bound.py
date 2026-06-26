from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from feu.version import (
    PackageBounds,
    get_package_bounds,
    normalize_package_name,
    partition_package_bounds,
)


def make_bounds(
    name: str,
    lower: str | None = None,
    upper: str | None = None,
    section: str = "project.dependencies",
) -> PackageBounds:
    return PackageBounds(name=name, lower=lower, upper=upper, section=section)


PACKAGES = [
    make_bounds("numpy", lower="1.21", upper="2.0"),
    make_bounds("torch", lower="2.0"),
    make_bounds("requests"),
    make_bounds("scikit-learn", lower="1.0", upper="2.0"),
]

#####################################
#     Tests for PackageBounds       #
#####################################


def test_package_bounds_equal() -> None:
    assert PackageBounds(
        name="numpy", lower="1.21", upper="2.0", section="project.dependencies"
    ) == PackageBounds(name="numpy", lower="1.21", upper="2.0", section="project.dependencies")


def test_package_bounds_not_equal_different_lower() -> None:
    assert PackageBounds(
        name="numpy", lower="1.21", upper="2.0", section="project.dependencies"
    ) != PackageBounds(name="numpy", lower="1.22", upper="2.0", section="project.dependencies")


def test_package_bounds_not_equal_different_upper() -> None:
    assert PackageBounds(
        name="numpy", lower="1.21", upper="2.0", section="project.dependencies"
    ) != PackageBounds(name="numpy", lower="1.21", upper="3.0", section="project.dependencies")


def test_package_bounds_not_equal_different_section() -> None:
    assert PackageBounds(
        name="numpy", lower="1.21", upper="2.0", section="project.dependencies"
    ) != PackageBounds(name="numpy", lower="1.21", upper="2.0", section="dependency-groups.dev")


def test_package_bounds_is_immutable() -> None:
    bounds = PackageBounds(name="numpy", lower="1.21", upper="2.0", section="project.dependencies")
    with pytest.raises(FrozenInstanceError, match=r"cannot assign to field 'lower'"):
        bounds.lower = "1.0"  # type: ignore[misc]


########################################
#     Tests for get_package_bounds     #
########################################


def test_get_package_bounds_first_match() -> None:
    assert get_package_bounds(PACKAGES, "numpy") == make_bounds("numpy", lower="1.21", upper="2.0")


def test_get_package_bounds_no_lower_no_upper() -> None:
    assert get_package_bounds(PACKAGES, "requests") == make_bounds("requests")


def test_get_package_bounds_returns_first_occurrence() -> None:
    packages = [
        make_bounds("numpy", lower="1.21", upper="2.0"),
        make_bounds("numpy", lower="1.24", upper=None, section="project.optional-dependencies.dev"),
    ]
    assert get_package_bounds(packages, "numpy") == make_bounds("numpy", lower="1.21", upper="2.0")


def test_get_package_bounds_case_insensitive() -> None:
    assert get_package_bounds(PACKAGES, "NumPy") == make_bounds("numpy", lower="1.21", upper="2.0")


def test_get_package_bounds_hyphen_underscore_equivalent() -> None:
    assert get_package_bounds(PACKAGES, "scikit_learn") == make_bounds(
        "scikit-learn", lower="1.0", upper="2.0"
    )


def test_get_package_bounds_not_found_raises_value_error() -> None:
    with pytest.raises(ValueError, match="nonexistent"):
        get_package_bounds(PACKAGES, "nonexistent")


def test_get_package_bounds_empty_sequence_raises_value_error() -> None:
    with pytest.raises(ValueError, match="numpy"):
        get_package_bounds([], "numpy")


##############################################
#     Tests for normalize_package_name       #
##############################################


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        pytest.param("numpy", "numpy", id="already_normalized"),
        pytest.param("NumPy", "numpy", id="mixed_case"),
        pytest.param("NUMPY", "numpy", id="uppercase"),
        pytest.param("scikit-learn", "scikit_learn", id="hyphen"),
        pytest.param("scikit_learn", "scikit_learn", id="underscore"),
        pytest.param("Scikit-Learn", "scikit_learn", id="mixed_case_hyphen"),
        pytest.param("SCIKIT-LEARN", "scikit_learn", id="uppercase_hyphen"),
        pytest.param("my-package-name", "my_package_name", id="multiple_hyphens"),
        pytest.param("a", "a", id="single_char"),
        pytest.param("", "", id="empty_string"),
    ],
)
def test_normalize_package_name_parametrized(name: str, expected: str) -> None:
    assert normalize_package_name(name) == expected


def test_normalize_package_name_returns_str() -> None:
    assert isinstance(normalize_package_name("numpy"), str)


def test_normalize_package_name_hyphen_and_underscore_equivalent() -> None:
    assert normalize_package_name("scikit-learn") == normalize_package_name("scikit_learn")


def test_normalize_package_name_case_insensitive() -> None:
    assert normalize_package_name("NumPy") == normalize_package_name("numpy")


##############################################
#     Tests for partition_package_bounds     #
##############################################


def test_partition_package_bounds_matched_and_unmatched() -> None:
    matched, unmatched = partition_package_bounds(PACKAGES, ["numpy", "torch"])
    assert matched == [
        make_bounds("numpy", lower="1.21", upper="2.0"),
        make_bounds("torch", lower="2.0"),
    ]
    assert unmatched == [
        make_bounds("requests"),
        make_bounds("scikit-learn", lower="1.0", upper="2.0"),
    ]


def test_partition_package_bounds_all_matched() -> None:
    names = ["numpy", "torch", "requests", "scikit-learn"]
    matched, unmatched = partition_package_bounds(PACKAGES, names)
    assert matched == list(PACKAGES)
    assert unmatched == []


def test_partition_package_bounds_none_matched() -> None:
    matched, unmatched = partition_package_bounds(PACKAGES, ["scipy", "pandas"])
    assert matched == []
    assert unmatched == list(PACKAGES)


def test_partition_package_bounds_empty_packages() -> None:
    matched, unmatched = partition_package_bounds([], ["numpy", "torch"])
    assert matched == []
    assert unmatched == []


def test_partition_package_bounds_empty_names() -> None:
    matched, unmatched = partition_package_bounds(PACKAGES, [])
    assert matched == []
    assert unmatched == list(PACKAGES)


def test_partition_package_bounds_both_empty() -> None:
    matched, unmatched = partition_package_bounds([], [])
    assert matched == []
    assert unmatched == []


def test_partition_package_bounds_preserves_package_order_in_matched() -> None:
    # Names are given in reverse order; matched must follow packages order.
    matched, _ = partition_package_bounds(PACKAGES, ["torch", "numpy"])
    assert [p.name for p in matched] == ["numpy", "torch"]


def test_partition_package_bounds_preserves_package_order_in_unmatched() -> None:
    _, unmatched = partition_package_bounds(PACKAGES, ["numpy"])
    assert [p.name for p in unmatched] == ["torch", "requests", "scikit-learn"]


def test_partition_package_bounds_matched_and_unmatched_cover_all_packages() -> None:
    matched, unmatched = partition_package_bounds(PACKAGES, ["numpy", "torch"])
    assert matched + unmatched == list(PACKAGES)


def test_partition_package_bounds_case_insensitive() -> None:
    matched, unmatched = partition_package_bounds(PACKAGES, ["NumPy", "TORCH"])
    assert matched == [
        make_bounds("numpy", lower="1.21", upper="2.0"),
        make_bounds("torch", lower="2.0"),
    ]
    assert unmatched == [
        make_bounds("requests"),
        make_bounds("scikit-learn", lower="1.0", upper="2.0"),
    ]


def test_partition_package_bounds_hyphen_underscore_equivalent() -> None:
    matched, unmatched = partition_package_bounds(PACKAGES, ["scikit_learn"])
    assert matched == [make_bounds("scikit-learn", lower="1.0", upper="2.0")]
    assert unmatched == [
        make_bounds("numpy", lower="1.21", upper="2.0"),
        make_bounds("torch", lower="2.0"),
        make_bounds("requests"),
    ]


def test_partition_package_bounds_returns_tuple_of_two_lists() -> None:
    result = partition_package_bounds(PACKAGES, ["numpy"])
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert isinstance(result[0], list)
    assert isinstance(result[1], list)
