r"""Define some utility functions for testing."""

from __future__ import annotations

__all__ = ["fire_available"]

import pytest

from feu.imports import is_fire_available

fire_available = pytest.mark.skipif(not is_fire_available(), reason="Requires fire")
