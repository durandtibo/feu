from __future__ import annotations

from feu.utils.fallback.requests import HTTPAdapter, requests


def test_requests() -> None:
    requests.Session()


def test_http_adapter() -> None:
    HTTPAdapter()
    HTTPAdapter(max_retries=3)
