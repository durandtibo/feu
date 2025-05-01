r"""Contain git utility functions."""

from __future__ import annotations

__all__ = ["get_tags"]

from unittest.mock import Mock

from feu.imports import check_git, is_git_available

if is_git_available():  # pragma: no cover
    import git
else:
    git = Mock()


def get_tags() -> list[git.TagReference]:
    r"""Get the list of git tags sorted by date/time for the current
    repo.

    Returns:
        The list of git tags sorted by date/time.

    Example usage:

    ```pycon

    >>> from feu.git import get_tags
    >>> tags = get_tags()
    >>> tags

    ```
    """
    check_git()
    repo = git.Repo(search_parent_directories=True)
    return sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
