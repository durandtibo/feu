from __future__ import annotations

from feu.version import filter_stable_versions, filter_valid_versions

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
