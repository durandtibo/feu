from __future__ import annotations

from feu.utils.fallback.urllib3 import Retry


def test_retry() -> None:
    Retry()
    Retry(
        total=5,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
