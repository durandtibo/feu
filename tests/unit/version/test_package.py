from __future__ import annotations

from unittest.mock import Mock, patch

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
def test_get_versions() -> None:
    mock = Mock(return_value=("1.0.0", "1.0.1", "1.1.0", "1.1.2", "2.0.0", "2.0.3"))
    with patch("feu.version.package.fetch_pypi_versions", mock):
        assert get_versions("my_package") == ("1.0.0", "1.0.1", "1.1.0", "1.1.2", "2.0.0", "2.0.3")


@requests_available
def test_get_versions_lower() -> None:
    mock = Mock(return_value=("1.0.0", "1.0.1", "1.1.0", "1.1.2", "2.0.0", "2.0.3"))
    with patch("feu.version.package.fetch_pypi_versions", mock):
        assert get_versions("my_package", lower="1.1.0") == ("1.1.0", "1.1.2", "2.0.0", "2.0.3")


@requests_available
def test_get_versions_upper() -> None:
    mock = Mock(return_value=("1.0.0", "1.0.1", "1.1.0", "1.1.2", "2.0.0", "2.0.3"))
    with patch("feu.version.package.fetch_pypi_versions", mock):
        assert get_versions("my_package", upper="2.0.0") == ("1.0.0", "1.0.1", "1.1.0", "1.1.2")


@requests_available
def test_get_versions_range() -> None:
    mock = Mock(return_value=("1.0.0", "1.0.1", "1.1.0", "1.1.2", "2.0.0", "2.0.3"))
    with patch("feu.version.package.fetch_pypi_versions", mock):
        assert get_versions("my_package", lower="1.1.0", upper="2.0.0") == ("1.1.0", "1.1.2")


###############################################
#     Tests for get_latest_major_versions     #
###############################################


@requests_available
def test_get_latest_major_versions() -> None:
    mock = Mock(return_value=("0.1.0", "0.8.0", "0.9.0", "1.0.0", "1.2.0", "1.3.0", "2.0.0"))
    with patch("feu.version.package.fetch_pypi_versions", mock):
        assert get_latest_major_versions("my_package") == ("0.9.0", "1.3.0", "2.0.0")


@requests_available
def test_get_latest_major_versions_lower() -> None:
    mock = Mock(return_value=("0.1.0", "0.8.0", "0.9.0", "1.0.0", "1.2.0", "1.3.0", "2.0.0"))
    with patch("feu.version.package.fetch_pypi_versions", mock):
        assert get_latest_major_versions("my_package", lower="1.0.0") == ("1.3.0", "2.0.0")


@requests_available
def test_get_latest_major_versions_upper() -> None:
    mock = Mock(return_value=("0.1.0", "0.8.0", "0.9.0", "1.0.0", "1.2.0", "1.3.0", "2.0.0"))
    with patch("feu.version.package.fetch_pypi_versions", mock):
        assert get_latest_major_versions("my_package", upper="2.0.0") == ("0.9.0", "1.3.0")


@requests_available
def test_get_latest_major_versions_range() -> None:
    mock = Mock(return_value=("0.1.0", "0.8.0", "0.9.0", "1.0.0", "1.2.0", "1.3.0", "2.0.0"))
    with patch("feu.version.package.fetch_pypi_versions", mock):
        assert get_latest_major_versions("my_package", lower="1.0.0", upper="2.0.0") == ("1.3.0",)


###############################################
#     Tests for get_latest_minor_versions     #
###############################################


@requests_available
def test_get_latest_minor_versions() -> None:
    mock = Mock(return_value=("1.0.0", "1.0.1", "1.1.0", "1.1.2", "2.0.0", "2.0.3"))
    with patch("feu.version.package.fetch_pypi_versions", mock):
        assert get_latest_minor_versions("my_package") == ("1.0.1", "1.1.2", "2.0.3")


@requests_available
def test_get_latest_minor_versions_lower() -> None:
    mock = Mock(return_value=("1.0.0", "1.0.1", "1.1.0", "1.1.2", "2.0.0", "2.0.3"))
    with patch("feu.version.package.fetch_pypi_versions", mock):
        assert get_latest_minor_versions("my_package", lower="1.1.0") == ("1.1.2", "2.0.3")


@requests_available
def test_get_latest_minor_versions_upper() -> None:
    mock = Mock(return_value=("1.0.0", "1.0.1", "1.1.0", "1.1.2", "2.0.0", "2.0.3"))
    with patch("feu.version.package.fetch_pypi_versions", mock):
        assert get_latest_minor_versions("my_package", upper="2.0.0") == ("1.0.1", "1.1.2")


@requests_available
def test_get_latest_minor_versions_range() -> None:
    mock = Mock(return_value=("1.0.0", "1.0.1", "1.1.0", "1.1.2", "2.0.0", "2.0.3"))
    with patch("feu.version.package.fetch_pypi_versions", mock):
        assert get_latest_minor_versions("my_package", lower="1.1.0", upper="2.0.0") == ("1.1.2",)
