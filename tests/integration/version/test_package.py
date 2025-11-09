from __future__ import annotations

from feu.testing import requests_available
from feu.version import (
    get_latest_major_versions,
    get_latest_minor_versions,
    get_versions,
)

##################################
#     Tests for get_versions     #
##################################


@requests_available
def test_get_versions_requests() -> None:
    assert get_versions("requests", lower="2.25", upper="2.30") == (
        "2.25.0",
        "2.25.1",
        "2.26.0",
        "2.27.0",
        "2.27.1",
        "2.28.0",
        "2.28.1",
        "2.28.2",
        "2.29.0",
    )


@requests_available
def test_get_versions_torch() -> None:
    assert get_versions("torch", lower="2.5", upper="2.9") == (
        "2.5.0",
        "2.5.1",
        "2.6.0",
        "2.7.0",
        "2.7.1",
        "2.8.0",
    )


###############################################
#     Tests for get_latest_major_versions     #
###############################################


@requests_available
def test_get_latest_major_versions_requests() -> None:
    assert get_latest_major_versions("requests", upper="2.30") == ("0.14.2", "1.2.3", "2.29.0")


@requests_available
def test_get_latest_major_versions_torch() -> None:
    assert get_latest_major_versions("torch", upper="2.9") == ("1.13.1", "2.8.0")


###############################################
#     Tests for get_latest_minor_versions     #
###############################################


@requests_available
def test_get_latest_minor_versions_requests() -> None:
    assert get_latest_minor_versions("requests", lower="2.10", upper="2.30") == (
        "2.10.0",
        "2.11.1",
        "2.12.5",
        "2.13.0",
        "2.14.2",
        "2.15.1",
        "2.16.5",
        "2.17.3",
        "2.18.4",
        "2.19.1",
        "2.20.1",
        "2.21.0",
        "2.22.0",
        "2.23.0",
        "2.24.0",
        "2.25.1",
        "2.26.0",
        "2.27.1",
        "2.28.2",
        "2.29.0",
    )


@requests_available
def test_get_latest_minor_versions_torch() -> None:
    assert get_latest_minor_versions("torch", lower="2.0", upper="2.9") == (
        "2.0.1",
        "2.1.2",
        "2.2.2",
        "2.3.1",
        "2.4.1",
        "2.5.1",
        "2.6.0",
        "2.7.1",
        "2.8.0",
    )
