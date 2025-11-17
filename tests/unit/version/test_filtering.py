from __future__ import annotations

import pytest

from feu.version import (
    filter_every_n_versions,
    filter_last_n_versions,
    filter_range_versions,
    filter_stable_versions,
    filter_valid_versions,
    latest_major_versions,
    latest_minor_versions,
    sort_versions,
    unique_versions,
)

#############################################
#     Tests for filter_every_n_versions     #
#############################################


def test_filter_every_n_versions_keep_every_second_version() -> None:
    versions = ["1.0", "1.1", "1.2", "1.3", "1.4"]
    assert filter_every_n_versions(versions, n=2) == ["1.0", "1.2", "1.4"]


def test_filter_every_n_versions_keep_every_third_version() -> None:
    versions = ["0.1", "0.2", "0.3", "0.4", "0.5", "0.6"]
    assert filter_every_n_versions(versions, n=3) == ["0.1", "0.4"]


def test_filter_every_n_versions_n_equals_one() -> None:
    versions = ["1.0", "1.1", "1.2", "1.3", "1.4"]
    assert filter_every_n_versions(versions, n=1) == ["1.0", "1.1", "1.2", "1.3", "1.4"]


def test_filter_every_n_versions_empty_list() -> None:
    assert filter_every_n_versions([], n=2) == []


def test_filter_every_n_versions_n_greater_than_list_length() -> None:
    versions = ["1.0", "1.1", "1.2", "1.3"]
    assert filter_every_n_versions(versions, n=5) == ["1.0"]


def test_filter_every_n_versions_invalid_n_raises() -> None:
    with pytest.raises(ValueError, match=r"n must be >= 1 but receive 0"):
        filter_every_n_versions(["1.0", "1.1"], n=0)


def test_filter_every_n_versions_single_item_list() -> None:
    assert filter_every_n_versions(["1.1"], n=2) == ["1.1"]


def test_filter_every_n_versions_large_n() -> None:
    versions = [str(i) for i in range(100)]
    assert filter_every_n_versions(versions, n=50) == ["0", "50"]


############################################
#     Tests for filter_last_n_versions     #
############################################


def test_filter_last_n_versions_keep_last_three() -> None:
    versions = ["1.0", "1.1", "1.2", "1.3", "1.5", "1.6"]
    assert filter_last_n_versions(versions, n=3) == ["1.3", "1.5", "1.6"]


def test_filter_last_n_versions_keep_last_one() -> None:
    versions = ["1.0", "1.1", "1.2", "1.3", "1.4"]
    assert filter_last_n_versions(versions, n=1) == ["1.4"]


def test_filter_last_n_versions_n_equals_list_length() -> None:
    versions = ["1.0", "1.1", "1.2", "1.3", "1.4"]
    assert filter_last_n_versions(versions, n=5) == ["1.0", "1.1", "1.2", "1.3", "1.4"]


def test_filter_last_n_versions_n_greater_than_list_length() -> None:
    versions = ["1.0", "1.1", "1.2"]
    assert filter_last_n_versions(versions, n=10) == ["1.0", "1.1", "1.2"]


def test_filter_last_n_versions_empty_list() -> None:
    assert filter_last_n_versions([], n=3) == []


def test_filter_last_n_versions_single_item() -> None:
    assert filter_last_n_versions(["1.0"], n=1) == ["1.0"]


def test_filter_last_n_versions_single_item_n_greater() -> None:
    assert filter_last_n_versions(["1.0"], n=5) == ["1.0"]


def test_filter_last_n_versions_invalid_n_raises() -> None:
    with pytest.raises(ValueError, match=r"n must be >= 1 but receive 0"):
        filter_last_n_versions(["1.0", "1.1"], n=0)


def test_filter_last_n_versions_invalid_n_negative_raises() -> None:
    with pytest.raises(ValueError, match=r"n must be >= 1 but receive -1"):
        filter_last_n_versions(["1.0", "1.1"], n=-1)


def test_filter_last_n_versions_large_list() -> None:
    versions = [f"{i}.0" for i in range(100)]
    result = filter_last_n_versions(versions, n=5)
    assert result == ["95.0", "96.0", "97.0", "98.0", "99.0"]


###########################################
#     Tests for filter_range_versions     #
###########################################


def test_filter_range_versions() -> None:
    assert filter_range_versions(
        ["0.9.0", "1.0.0", "1.2.0", "1.3.0", "2.0.0"], lower="1.1.0", upper="2.0.0"
    ) == [
        "1.2.0",
        "1.3.0",
    ]


def test_filter_range_versions_lower() -> None:
    assert filter_range_versions(["0.9.0", "1.0.0", "1.2.0", "1.3.0", "2.0.0"], lower="1.1.0") == [
        "1.2.0",
        "1.3.0",
        "2.0.0",
    ]


def test_filter_range_versions_upper() -> None:
    assert filter_range_versions(["0.9.0", "1.0.0", "1.2.0", "1.3.0", "2.0.0"], upper="2.0.0") == [
        "0.9.0",
        "1.0.0",
        "1.2.0",
        "1.3.0",
    ]


def test_filter_range_versions_empty() -> None:
    assert filter_range_versions([]) == []


############################################
#     Tests for filter_stable_versions     #
############################################


def test_filter_stable_versions() -> None:
    assert filter_stable_versions(["1.0.0", "1.0.0a1", "2.0.0", "2.0.0.dev1", "3.0.0.post1"]) == [
        "1.0.0",
        "2.0.0",
    ]


def test_filter_stable_versions_all() -> None:
    assert filter_stable_versions(
        [
            "1.0.0",
            "2.0.1",
            "3.3.3",
            "0.9",
            "v1.0.0",
            "2024.6",
            "2024.07",
        ]
    ) == [
        "1.0.0",
        "2.0.1",
        "3.3.3",
        "0.9",
        "v1.0.0",
        "2024.6",
        "2024.07",
    ]


def test_filter_stable_versions_prereleases() -> None:
    assert filter_stable_versions(["1.0.0", "2.0.0a1", "2.0.0b2", "2.0.0rc3"]) == ["1.0.0"]


def test_filter_stable_versions_postreleases() -> None:
    assert filter_stable_versions(["1.0.0", "1.0.0.post1", "2.0.0.post2"]) == ["1.0.0"]


def test_filter_stable_versions_devreleases() -> None:
    assert filter_stable_versions(["1.0.0", "1.0.0.dev1", "2.0.0.dev2"]) == ["1.0.0"]


def test_filter_stable_versions_empty() -> None:
    assert filter_stable_versions([]) == []


###########################################
#     Tests for filter_valid_versions     #
###########################################


def test_filter_valid_versions() -> None:
    assert filter_valid_versions(
        [
            "1.0.0",
            "1.0.0a1",
            "2.0.0.post1",
            "not-a-version",
            "",
            "2",
            "3.0",
            "v1.0.0",
            "1.0.0.0.0",
            "4.0.0.dev1",
            "2024.6",
        ]
    ) == [
        "1.0.0",
        "1.0.0a1",
        "2.0.0.post1",
        "2",
        "3.0",
        "v1.0.0",
        "1.0.0.0.0",
        "4.0.0.dev1",
        "2024.6",
    ]


def test_filter_valid_versions_all_valid() -> None:
    assert filter_valid_versions(["1.0.0", "2.0.0a1", "2.1.3.post1", "0.1.dev2", "3.0"]) == [
        "1.0.0",
        "2.0.0a1",
        "2.1.3.post1",
        "0.1.dev2",
        "3.0",
    ]


def test_filter_valid_versions_all_invalid() -> None:
    assert filter_valid_versions(["not-a-version", "", "abc", "invalid"]) == []


def test_filter_valid_versions_mixed() -> None:
    assert filter_valid_versions(["1.0.0", "invalid", "", "2024.6", "!!", "2.0"]) == [
        "1.0.0",
        "2024.6",
        "2.0",
    ]


def test_filter_valid_versions_empty() -> None:
    assert filter_valid_versions([]) == []


###########################################
#     Tests for latest_major_versions     #
###########################################


def test_latest_major_versions() -> None:
    assert latest_major_versions(["1.0.0", "1.1.0", "1.2.0", "1.2.1", "2.0.0"]) == [
        "1.2.1",
        "2.0.0",
    ]


def test_latest_major_versions_sort() -> None:
    assert latest_major_versions(["1.0.0", "1.2.1", "2.0.0", "1.1.0", "1.2.0"]) == [
        "1.2.1",
        "2.0.0",
    ]


def test_latest_major_versions_missing_version() -> None:
    assert latest_major_versions(["1.0.0", "2.0.0", "3.0", "5"]) == [
        "1.0.0",
        "2.0.0",
        "3.0",
        "5",
    ]


def test_latest_major_versions_empty() -> None:
    assert latest_major_versions([]) == []


###########################################
#     Tests for latest_minor_versions     #
###########################################


def test_latest_minor_versions() -> None:
    assert latest_minor_versions(["1.0.0", "1.0.1", "1.1.0", "1.1.2", "2.0.0", "2.0.3"]) == [
        "1.0.1",
        "1.1.2",
        "2.0.3",
    ]


def test_latest_minor_versions_sort() -> None:
    assert latest_minor_versions(["2.0.3", "1.0.0", "1.0.1", "1.1.2", "1.1.0", "2.0.0"]) == [
        "1.0.1",
        "1.1.2",
        "2.0.3",
    ]


def test_latest_minor_versions_missing_version() -> None:
    assert latest_minor_versions(
        ["1.0.0", "1.1.0", "1.1.1", "1.2.0", "1.2.1", "1.2.2", "1.4.1"]
    ) == [
        "1.0.0",
        "1.1.1",
        "1.2.2",
        "1.4.1",
    ]


def test_latest_minor_versions_empty() -> None:
    assert latest_minor_versions([]) == []


#####################################
#     Tests for unique_versions     #
#####################################


def test_unique_versions() -> None:
    assert sort_versions(unique_versions(["1.0.0", "1.0.1", "1.0.0", "1.2.0"])) == [
        "1.0.0",
        "1.0.1",
        "1.2.0",
    ]


def test_unique_versions_single_item() -> None:
    assert sort_versions(unique_versions(["1.0.0"])) == ["1.0.0"]


def test_unique_versions_empty() -> None:
    assert unique_versions([]) == []
