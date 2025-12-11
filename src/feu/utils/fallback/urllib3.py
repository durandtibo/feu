r"""Contain fallback implementations used when ``urllib3`` dependency is
not available."""

from __future__ import annotations

__all__ = ["Retry"]

from unittest.mock import Mock

# Create a fake Retry class
Retry = Mock()
