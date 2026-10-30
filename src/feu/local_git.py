r"""Contain git utility functions to inspect the tags of the current
repository.

These functions require the ``gitpython`` package.
"""

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

    The repository is searched from the current working directory
    and its parent directories. The tags are sorted by the commit
    date of the commit they point to.

    Returns:
        The list of git tags sorted by commit date/time, from the
            oldest to the most recent.

    Raises:
        RuntimeError: if the ``gitpython`` package is not installed.
        git.InvalidGitRepositoryError: if the current directory is
            not in a git repository.

    Example:
        ```pycon
        >>> from feu.local_git import get_tags
        >>> tags = get_tags()
        >>> tags

        ```
    """
    check_git()
    repo = git.Repo(search_parent_directories=True)
    return sorted(repo.tags, key=lambda t: t.commit.committed_datetime)


def get_last_tag_name(raise_error: bool = True) -> str | None:
    r"""Get the name of the most recent tag in the current repository.

    The most recent tag is the tag pointing to the most recent commit,
    see ``get_tags``.

    Args:
        raise_error: If ``True``, a ``RuntimeError`` is raised when
            no tag is found. If ``False``, ``None`` is returned
            instead.

    Returns:
        The tag name, or ``None`` if no tag was found and
            ``raise_error=False``.

    Raises:
        RuntimeError: if no tag was found and ``raise_error=True``, or
            if the ``gitpython`` package is not installed.

    Example:
        ```pycon
        >>> from feu.local_git import get_last_tag_name
        >>> tag = get_last_tag_name()
        >>> tag
        >>> tag = get_last_tag_name(raise_error=False)
        >>> tag

        ```
    """
    tags = get_tags()
    if not tags:
        if raise_error:
            msg = "No tag was found"
            raise RuntimeError(msg)
        return None
    return tags[-1].name


def get_last_version_tag_name(raise_error: bool = True) -> str | None:
    r"""Get the name of the most recent version tag in the current
    repository.

    A version tag is a tag made of the prefix ``v`` followed by a
    valid PEP 440 version, e.g. ``v1.2.3``. The other tags are
    ignored.

    Args:
        raise_error: If ``True``, a ``RuntimeError`` is raised when
            no version tag is found. If ``False``, ``None`` is
            returned instead.

    Returns:
        The tag name, or ``None`` if no version tag was found and
            ``raise_error=False``.

    Raises:
        RuntimeError: if no version tag was found and
            ``raise_error=True``, or if the ``gitpython`` package is
            not installed.

    Example:
        ```pycon
        >>> from feu.local_git import get_last_version_tag_name
        >>> tag = get_last_version_tag_name()
        >>> tag
        >>> tag = get_last_version_tag_name(raise_error=False)
        >>> tag

        ```
    """
    tags = get_tags()
    for tag in tags[::-1]:
        if not tag.name.startswith("v"):
            continue
        with suppress(InvalidVersion):
            Version(tag.name[1:])
            return tag.name

    if raise_error:
        msg = "No tag was found"
        raise RuntimeError(msg)
    return None
