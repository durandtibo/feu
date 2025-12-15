from __future__ import annotations

from types import ModuleType

from feu.utils.fallback.requests import HTTPAdapter, requests


def test_requests() -> None:
    isinstance(requests, ModuleType)


def test_http_adapter() -> None:
    HTTPAdapter()
    HTTPAdapter(max_retries=3)
