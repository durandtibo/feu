from __future__ import annotations

from types import ModuleType

from feu.utils.fallback.git import git


def test_git() -> None:
    isinstance(git, ModuleType)
