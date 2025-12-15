r"""Contain fallback implementations used when ``requests`` dependency
is not available."""

from __future__ import annotations

__all__ = ["HTTPAdapter", "requests"]

from types import ModuleType
from unittest.mock import Mock

# Create a fake requests package
requests = ModuleType("requests")

# Create a fake HTTPAdapter class
HTTPAdapter = Mock()
