r"""Contain fallback implementations used when ``git`` dependency is not
available."""

from __future__ import annotations

__all__ = ["Repo", "TagReference"]

from typing import Any

from feu.imports import raise_error_git_missing


class Repo:
    r"""Fallback of ``git.Repo``."""

    tags: Any

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        raise_error_git_missing()


class TagReference:
    r"""Fallback of ``git.TagReference``."""

    commit: Any
    name: Any

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        raise_error_git_missing()
