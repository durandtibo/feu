r"""Contain fallback implementations used when ``git`` dependency is not
available."""

from __future__ import annotations

__all__ = ["git"]

from types import ModuleType

# Create a fake git package
git: ModuleType = ModuleType("git")
