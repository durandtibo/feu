from __future__ import annotations

import pytest

from feu.github import sort_repos_by_key

#######################################
#     Tests for sort_repos_by_key     #
#######################################


def test_sort_repos_by_key_ascending_order() -> None:
    """Test sorting repositories in ascending order by name."""
    assert sort_repos_by_key(
        [
            {"name": "zebra", "id": 1},
            {"name": "alpha", "id": 2},
            {"name": "beta", "id": 3},
        ],
        key="name",
    ) == [
        {"name": "alpha", "id": 2},
        {"name": "beta", "id": 3},
        {"name": "zebra", "id": 1},
    ]


def test_sort_repos_by_key_descending_order() -> None:
    """Test sorting repositories in descending order by name."""
    assert sort_repos_by_key(
        [
            {"name": "alpha", "id": 1},
            {"name": "zebra", "id": 2},
            {"name": "beta", "id": 3},
        ],
        key="name",
        reverse=True,
    ) == [
        {"name": "zebra", "id": 2},
        {"name": "beta", "id": 3},
        {"name": "alpha", "id": 1},
    ]


def test_sort_repos_by_key_empty_list() -> None:
    """Test sorting an empty list of repositories."""
    assert sort_repos_by_key([], key="name") == []


def test_sort_repos_by_key_single_item() -> None:
    """Test sorting a list with a single repository."""
    assert sort_repos_by_key([{"name": "solo", "id": 1}], key="name") == [{"name": "solo", "id": 1}]


def test_sort_repos_by_key_already_sorted() -> None:
    """Test sorting repositories that are already in order."""
    assert sort_repos_by_key(
        [
            {"name": "alpha", "id": 1},
            {"name": "beta", "id": 2},
            {"name": "gamma", "id": 3},
        ],
        key="name",
    ) == [
        {"name": "alpha", "id": 1},
        {"name": "beta", "id": 2},
        {"name": "gamma", "id": 3},
    ]


def test_sort_repos_by_key_preserves_other_fields() -> None:
    """Test that sorting preserves all other fields in repository
    dicts."""
    assert sort_repos_by_key(
        [
            {"name": "zoo", "id": 1, "stars": 100, "description": "Zoo app"},
            {"name": "app", "id": 2, "stars": 50, "description": "Main app"},
        ],
        key="name",
    ) == [
        {"name": "app", "id": 2, "stars": 50, "description": "Main app"},
        {"name": "zoo", "id": 1, "stars": 100, "description": "Zoo app"},
    ]


def test_sort_repos_by_key_does_not_mutate_input() -> None:
    """Test that the original list is not modified."""
    repos = [{"name": "zebra", "id": 1}, {"name": "alpha", "id": 2}]
    original_order = [r["name"] for r in repos]
    sort_repos_by_key(repos, key="name")
    assert [r["name"] for r in repos] == original_order


def test_sort_repos_by_key_with_duplicate_names() -> None:
    """Test sorting repositories with duplicate names."""
    assert sort_repos_by_key(
        [
            {"name": "duplicate", "id": 1},
            {"name": "alpha", "id": 2},
            {"name": "duplicate", "id": 3},
        ],
        key="name",
    ) == [
        {"name": "alpha", "id": 2},
        {"name": "duplicate", "id": 1},
        {"name": "duplicate", "id": 3},
    ]


def test_sort_repos_by_key_with_missing_names() -> None:
    """Test that repositories without names are placed at the end."""
    assert sort_repos_by_key(
        [
            {"name": "zebra", "id": 1},
            {"id": 2},  # No name
            {"name": "alpha", "id": 3},
            {"id": 4},  # No name
        ],
        key="name",
    ) == [
        {"name": "alpha", "id": 3},
        {"name": "zebra", "id": 1},
        {"id": 2},
        {"id": 4},
    ]


def test_sort_repos_by_key_reverse_parameter_must_be_keyword() -> None:
    """Test that reverse parameter must be passed as keyword
    argument."""
    repos = [{"name": "test", "id": 1}]
    # This should raise TypeError because reverse is keyword-only
    with pytest.raises(TypeError):
        sort_repos_by_key(repos, "name", True)
