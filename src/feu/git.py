r"""Contain git utility functions."""

from __future__ import annotations

__all__ = ["get_last_tag_name", "get_last_version_tag_name", "get_tags"]

from contextlib import suppress
from typing import TYPE_CHECKING

from packaging.version import InvalidVersion, Version

from feu.imports import check_git, is_git_available

if TYPE_CHECKING or is_git_available():
    import git
else:  # pragma: no cover
    from feu.utils.fallback.git import git


def get_tags() -> list[git.TagReference]:
    r"""Get the list of git tags sorted by date/time for the current
    repository.

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


def get_last_tag_name() -> str:
    r"""Get the name of the most recent tag in the current repository.

    Returns:
        The tag name.

    Example usage:

    ```pycon

    >>> from feu.git import get_last_tag_name
    >>> tag = get_last_tag_name()
    >>> tag

    ```
    """
    tags = get_tags()
    if not tags:
        msg = "No tag was found"
        raise RuntimeError(msg)
    return tags[-1].name


def get_last_version_tag_name() -> str:
    r"""Get the name of the most recent version tag in the current
    repository.

    A version tag is a tag starting with ``v{number}*``.

    Returns:
        The tag name.

    Example usage:

    ```pycon

    >>> from feu.git import get_last_version_tag_name
    >>> tag = get_last_version_tag_name()
    >>> tag

    ```
    """
    tags = get_tags()
    for tag in tags[::-1]:
        with suppress(InvalidVersion):
            Version(tag.name)
            return tag.name

    msg = "No tag was found"
    raise RuntimeError(msg)
