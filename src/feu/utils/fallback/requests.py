r"""Contain fallback implementations used when ``requests`` dependency
is not available."""

from __future__ import annotations

__all__ = ["HTTPAdapter", "requests"]

from types import ModuleType
from typing import Any

from feu.imports import raise_requests_missing_error

# Create a fake requests package
requests: ModuleType = ModuleType("requests")


class HTTPAdapter:
    r"""Create a fake HTTPAdapter class."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        raise_requests_missing_error()
