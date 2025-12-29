from __future__ import annotations

import pytest

from feu.github import sort_repos_by_full_name, sort_repos_by_name

########################################
#     Tests for sort_repos_by_name     #
########################################


def test_sort_repos_by_name_ascending_order() -> None:
    """Test sorting repositories in ascending order by name."""
    assert sort_repos_by_name(
        [
            {"name": "zebra", "id": 1},
            {"name": "alpha", "id": 2},
            {"name": "beta", "id": 3},
        ]
    ) == [
        {"name": "alpha", "id": 2},
        {"name": "beta", "id": 3},
        {"name": "zebra", "id": 1},
    ]


def test_sort_repos_by_name_descending_order() -> None:
    """Test sorting repositories in descending order by name."""
    assert sort_repos_by_name(
        [
            {"name": "alpha", "id": 1},
            {"name": "zebra", "id": 2},
            {"name": "beta", "id": 3},
        ],
        reverse=True,
    ) == [
        {"name": "zebra", "id": 2},
        {"name": "beta", "id": 3},
        {"name": "alpha", "id": 1},
    ]


def test_sort_repos_by_name_empty_list() -> None:
    """Test sorting an empty list of repositories."""
    assert sort_repos_by_name([]) == []


def test_sort_repos_by_name_single_item() -> None:
    """Test sorting a list with a single repository."""
    assert sort_repos_by_name([{"name": "solo", "id": 1}]) == [{"name": "solo", "id": 1}]


def test_sort_repos_by_name_already_sorted() -> None:
    """Test sorting repositories that are already in order."""
    assert sort_repos_by_name(
        [
            {"name": "alpha", "id": 1},
            {"name": "beta", "id": 2},
            {"name": "gamma", "id": 3},
        ]
    ) == [
        {"name": "alpha", "id": 1},
        {"name": "beta", "id": 2},
        {"name": "gamma", "id": 3},
    ]


def test_sort_repos_by_name_preserves_other_fields() -> None:
    """Test that sorting preserves all other fields in repository
    dicts."""
    assert sort_repos_by_name(
        [
            {"name": "zoo", "id": 1, "stars": 100, "description": "Zoo app"},
            {"name": "app", "id": 2, "stars": 50, "description": "Main app"},
        ]
    ) == [
        {"name": "app", "id": 2, "stars": 50, "description": "Main app"},
        {"name": "zoo", "id": 1, "stars": 100, "description": "Zoo app"},
    ]


def test_sort_repos_by_name_does_not_mutate_input() -> None:
    """Test that the original list is not modified."""
    repos = [{"name": "zebra", "id": 1}, {"name": "alpha", "id": 2}]
    original_order = [r["name"] for r in repos]
    sort_repos_by_name(repos)
    assert [r["name"] for r in repos] == original_order


def test_sort_repos_by_name_with_duplicate_names() -> None:
    """Test sorting repositories with duplicate names."""
    assert sort_repos_by_name(
        [
            {"name": "duplicate", "id": 1},
            {"name": "alpha", "id": 2},
            {"name": "duplicate", "id": 3},
        ]
    ) == [
        {"name": "alpha", "id": 2},
        {"name": "duplicate", "id": 1},
        {"name": "duplicate", "id": 3},
    ]


def test_sort_repos_by_name_reverse_parameter_must_be_keyword() -> None:
    """Test that reverse parameter must be passed as keyword
    argument."""
    repos = [{"name": "test", "id": 1}]
    # This should raise TypeError because reverse is keyword-only
    with pytest.raises(TypeError):
        sort_repos_by_name(repos, True)


#############################################
#     Tests for sort_repos_by_full_name     #
#############################################


def test_sort_repos_by_full_name_ascending_order() -> None:
    """Test sorting repositories in ascending order by name."""
    assert sort_repos_by_full_name(
        [
            {"full_name": "owner/zebra", "id": 1},
            {"full_name": "owner/alpha", "id": 2},
            {"full_name": "owner/beta", "id": 3},
        ]
    ) == [
        {"full_name": "owner/alpha", "id": 2},
        {"full_name": "owner/beta", "id": 3},
        {"full_name": "owner/zebra", "id": 1},
    ]


def test_sort_repos_by_full_name_descending_order() -> None:
    """Test sorting repositories in descending order by name."""
    assert sort_repos_by_full_name(
        [
            {"full_name": "owner/alpha", "id": 1},
            {"full_name": "owner/zebra", "id": 2},
            {"full_name": "owner/beta", "id": 3},
        ],
        reverse=True,
    ) == [
        {"full_name": "owner/zebra", "id": 2},
        {"full_name": "owner/beta", "id": 3},
        {"full_name": "owner/alpha", "id": 1},
    ]


def test_sort_repos_by_full_name_empty_list() -> None:
    """Test sorting an empty list of repositories."""
    assert sort_repos_by_full_name([]) == []


def test_sort_repos_by_full_name_single_item() -> None:
    """Test sorting a list with a single repository."""
    assert sort_repos_by_full_name([{"full_name": "owner/solo", "id": 1}]) == [
        {"full_name": "owner/solo", "id": 1}
    ]


def test_sort_repos_by_full_name_already_sorted() -> None:
    """Test sorting repositories that are already in order."""
    assert sort_repos_by_full_name(
        [
            {"full_name": "owner/alpha", "id": 1},
            {"full_name": "owner/beta", "id": 2},
            {"full_name": "owner/gamma", "id": 3},
        ]
    ) == [
        {"full_name": "owner/alpha", "id": 1},
        {"full_name": "owner/beta", "id": 2},
        {"full_name": "owner/gamma", "id": 3},
    ]


def test_sort_repos_by_full_name_preserves_other_fields() -> None:
    """Test that sorting preserves all other fields in repository
    dicts."""
    assert sort_repos_by_full_name(
        [
            {"full_name": "owner/zoo", "id": 1, "stars": 100, "description": "Zoo app"},
            {"full_name": "owner/app", "id": 2, "stars": 50, "description": "Main app"},
        ]
    ) == [
        {"full_name": "owner/app", "id": 2, "stars": 50, "description": "Main app"},
        {"full_name": "owner/zoo", "id": 1, "stars": 100, "description": "Zoo app"},
    ]


def test_sort_repos_by_full_name_does_not_mutate_input() -> None:
    """Test that the original list is not modified."""
    repos = [{"full_name": "owner/zebra", "id": 1}, {"full_name": "owner/alpha", "id": 2}]
    original_order = [r["full_name"] for r in repos]
    sort_repos_by_full_name(repos)
    assert [r["full_name"] for r in repos] == original_order


def test_sort_repos_by_full_name_with_duplicate_names() -> None:
    """Test sorting repositories with duplicate full names."""
    assert sort_repos_by_full_name(
        [
            {"full_name": "owner/duplicate", "id": 1},
            {"full_name": "owner/alpha", "id": 2},
            {"full_name": "owner/duplicate", "id": 3},
        ]
    ) == [
        {"full_name": "owner/alpha", "id": 2},
        {"full_name": "owner/duplicate", "id": 1},
        {"full_name": "owner/duplicate", "id": 3},
    ]


def test_sort_repos_by_full_name_with_duplicate_repo_names() -> None:
    """Test sorting repositories with duplicate full names."""
    assert sort_repos_by_full_name(
        [
            {"full_name": "owner2/duplicate", "id": 1},
            {"full_name": "owner3/duplicate", "id": 2},
            {"full_name": "owner1/duplicate", "id": 3},
        ]
    ) == [
        {"full_name": "owner1/duplicate", "id": 3},
        {"full_name": "owner2/duplicate", "id": 1},
        {"full_name": "owner3/duplicate", "id": 2},
    ]


def test_sort_repos_by_full_name_reverse_parameter_must_be_keyword() -> None:
    """Test that reverse parameter must be passed as keyword
    argument."""
    repos = [{"name": "test", "id": 1}]
    # This should raise TypeError because reverse is keyword-only
    with pytest.raises(TypeError):
        sort_repos_by_full_name(repos, True)
