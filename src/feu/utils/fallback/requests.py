r"""Contain fallback implementations used when ``requests`` dependency
is not available."""

from __future__ import annotations

__all__ = ["requests"]

from types import SimpleNamespace

# Create a fake requests package
requests = SimpleNamespace(Session=lambda x: x, exceptions=SimpleNamespace())
