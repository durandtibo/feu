r"""Define some utility functions for testing."""

from __future__ import annotations

__all__ = ["click_available"]

import pytest

from feu.imports import is_click_available

click_available = pytest.mark.skipif(not is_click_available(), reason="Requires click")
