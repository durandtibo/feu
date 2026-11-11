from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, Mock, patch

import pytest

from feu.imports import is_requests_available
from feu.testing import requests_available
from feu.version import (
    fetch_pypi_pinned_dependency_version,
    fetch_pypi_requires_python,
    fetch_pypi_versions,
    fetch_pypi_wheel_filenames,
)
from feu.version.pypi import _package_url

if is_requests_available():
    import requests
    from requests import Response
else:
    Response = Mock


@pytest.fixture(autouse=True)
def _reset_cache() -> None:
    fetch_pypi_versions.cache_clear()
    fetch_pypi_requires_python.cache_clear()
    fetch_pypi_wheel_filenames.cache_clear()
    fetch_pypi_pinned_dependency_version.cache_clear()


#########################################
#     Tests for fetch_pypi_versions     #
#########################################


def make_mock_session(get: Mock) -> MagicMock:
    session = MagicMock(get=get)
    session.__enter__.return_value = session
    return session


def make_mock_response() -> Response:
    resp = Mock(json=Mock(return_value={"releases": {"1.2.0": None, "1.2.3": None, "2.0.0": None}}))
    resp.status_code = 200
    return resp


@requests_available
def test_fetch_pypi_versions(monkeypatch: pytest.MonkeyPatch) -> None:
    session = make_mock_session(get=Mock(return_value=make_mock_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_pypi_versions("my_package") == ("1.2.0", "1.2.3", "2.0.0")
    session.get.assert_called_once_with(url="https://pypi.org/pypi/my-package/json", timeout=10.0)


@requests_available
def test_fetch_pypi_versions_reverse(monkeypatch: pytest.MonkeyPatch) -> None:
    session = make_mock_session(get=Mock(return_value=make_mock_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_pypi_versions("my_package", reverse=True) == ("2.0.0", "1.2.3", "1.2.0")
    session.get.assert_called_once_with(url="https://pypi.org/pypi/my-package/json", timeout=10.0)


@patch("feu.imports.optional.is_requests_available", lambda: False)
def test_fetch_pypi_versions_no_requests() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        fetch_pypi_versions("my_package")


def make_mock_dated_response() -> Response:
    resp = Mock(
        json=Mock(
            return_value={
                "releases": {
                    "1.0.0": [{"upload_time_iso_8601": "2023-06-15T00:00:00.000000Z"}],
                    "1.1.0": [{"upload_time_iso_8601": "2024-01-10T00:00:00.000000Z"}],
                    "1.2.0": [{"upload_time_iso_8601": "2024-06-01T00:00:00.000000Z"}],
                    "1.3.0": [{"upload_time_iso_8601": "2024-12-31T00:00:00.000000Z"}],
                    "2.0.0": [{"upload_time_iso_8601": "2025-01-05T00:00:00.000000Z"}],
                    "2.1.0": [],
                }
            }
        )
    )
    resp.status_code = 200
    return resp


@requests_available
def test_fetch_pypi_versions_start_date(monkeypatch: pytest.MonkeyPatch) -> None:
    session = make_mock_session(get=Mock(return_value=make_mock_dated_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_pypi_versions("my_package", start_date="2024-01-01") == (
        "1.1.0",
        "1.2.0",
        "1.3.0",
        "2.0.0",
    )


@requests_available
def test_fetch_pypi_versions_end_date(monkeypatch: pytest.MonkeyPatch) -> None:
    session = make_mock_session(get=Mock(return_value=make_mock_dated_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_pypi_versions("my_package", end_date="2024-12-31") == (
        "1.0.0",
        "1.1.0",
        "1.2.0",
        "1.3.0",
    )


@requests_available
def test_fetch_pypi_versions_start_date_end_date(monkeypatch: pytest.MonkeyPatch) -> None:
    session = make_mock_session(get=Mock(return_value=make_mock_dated_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_pypi_versions("my_package", start_date="2024-01-01", end_date="2024-12-31") == (
        "1.1.0",
        "1.2.0",
        "1.3.0",
    )


@requests_available
def test_fetch_pypi_versions_start_date_end_date_date_objects(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = make_mock_session(get=Mock(return_value=make_mock_dated_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_pypi_versions(
        "my_package", start_date=date(2024, 1, 1), end_date=date(2024, 12, 31)
    ) == ("1.1.0", "1.2.0", "1.3.0")


@requests_available
def test_fetch_pypi_versions_start_date_end_date_reverse(monkeypatch: pytest.MonkeyPatch) -> None:
    session = make_mock_session(get=Mock(return_value=make_mock_dated_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_pypi_versions(
        "my_package", reverse=True, start_date="2024-01-01", end_date="2024-12-31"
    ) == ("1.3.0", "1.2.0", "1.1.0")


@requests_available
def test_fetch_pypi_versions_no_date_filter_excludes_nothing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = make_mock_session(get=Mock(return_value=make_mock_dated_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_pypi_versions("my_package") == (
        "1.0.0",
        "1.1.0",
        "1.2.0",
        "1.3.0",
        "2.0.0",
        "2.1.0",
    )


def make_mock_yanked_response() -> Response:
    resp = Mock(
        json=Mock(
            return_value={
                "releases": {
                    "1.0.0": [{"filename": "pkg-1.0.0.tar.gz", "yanked": False}],
                    "1.1.0": [
                        {"filename": "pkg-1.1.0.tar.gz", "yanked": True},
                        {"filename": "pkg-1.1.0.whl", "yanked": True},
                    ],
                    "1.2.0": [
                        {"filename": "pkg-1.2.0.tar.gz", "yanked": False},
                        {"filename": "pkg-1.2.0.whl", "yanked": True},
                    ],
                    "1.3.0": [],
                }
            }
        )
    )
    resp.status_code = 200
    return resp


@requests_available
def test_fetch_pypi_versions_ignore_yanked_default(monkeypatch: pytest.MonkeyPatch) -> None:
    session = make_mock_session(get=Mock(return_value=make_mock_yanked_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_pypi_versions("my_package") == ("1.0.0", "1.2.0", "1.3.0")


@requests_available
def test_fetch_pypi_versions_ignore_yanked_true(monkeypatch: pytest.MonkeyPatch) -> None:
    session = make_mock_session(get=Mock(return_value=make_mock_yanked_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_pypi_versions("my_package", ignore_yanked=True) == ("1.0.0", "1.2.0", "1.3.0")


@requests_available
def test_fetch_pypi_versions_ignore_yanked_false(monkeypatch: pytest.MonkeyPatch) -> None:
    session = make_mock_session(get=Mock(return_value=make_mock_yanked_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_pypi_versions("my_package", ignore_yanked=False) == (
        "1.0.0",
        "1.1.0",
        "1.2.0",
        "1.3.0",
    )


##################################################
#     Tests for fetch_pypi_requires_python     #
##################################################


def make_mock_requires_python_response() -> Response:
    resp = Mock(
        json=Mock(
            return_value={
                "releases": {
                    "1.0.0": [{"requires_python": ">=3.6"}],
                    "1.2.0": [{"requires_python": ">=3.8"}, {"requires_python": ">=3.8"}],
                    "1.3.0": [],
                    "2.0.0": [{"requires_python": None}],
                }
            }
        )
    )
    resp.status_code = 200
    return resp


@requests_available
def test_fetch_pypi_requires_python(monkeypatch: pytest.MonkeyPatch) -> None:
    session = make_mock_session(get=Mock(return_value=make_mock_requires_python_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_pypi_requires_python("my_package") == {
        "1.0.0": ">=3.6",
        "1.2.0": ">=3.8",
        "1.3.0": None,
        "2.0.0": None,
    }
    session.get.assert_called_once_with(url="https://pypi.org/pypi/my-package/json", timeout=10.0)


@patch("feu.imports.optional.is_requests_available", lambda: False)
def test_fetch_pypi_requires_python_no_requests() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        fetch_pypi_requires_python("my_package")


####################################################
#     Tests for fetch_pypi_wheel_filenames          #
####################################################


def make_mock_wheel_filenames_response() -> Response:
    resp = Mock(
        json=Mock(
            return_value={
                "releases": {
                    "1.0.0": [
                        {
                            "filename": "pkg-1.0.0-cp39-cp39-manylinux_2_17_x86_64.whl",
                            "packagetype": "bdist_wheel",
                        },
                        {"filename": "pkg-1.0.0.tar.gz", "packagetype": "sdist"},
                    ],
                    "1.1.0": [
                        {
                            "filename": "pkg-1.1.0-cp39-cp39-manylinux_2_17_x86_64.whl",
                            "packagetype": "bdist_wheel",
                        },
                        {
                            "filename": "pkg-1.1.0-cp310-cp310-manylinux_2_17_x86_64.whl",
                            "packagetype": "bdist_wheel",
                        },
                    ],
                    "1.2.0": [{"filename": "pkg-1.2.0.tar.gz", "packagetype": "sdist"}],
                    "1.3.0": [],
                }
            }
        )
    )
    resp.status_code = 200
    return resp


@requests_available
def test_fetch_pypi_wheel_filenames(monkeypatch: pytest.MonkeyPatch) -> None:
    session = make_mock_session(get=Mock(return_value=make_mock_wheel_filenames_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_pypi_wheel_filenames("my_package") == {
        "1.0.0": ("pkg-1.0.0-cp39-cp39-manylinux_2_17_x86_64.whl",),
        "1.1.0": (
            "pkg-1.1.0-cp39-cp39-manylinux_2_17_x86_64.whl",
            "pkg-1.1.0-cp310-cp310-manylinux_2_17_x86_64.whl",
        ),
        "1.2.0": (),
        "1.3.0": (),
    }
    session.get.assert_called_once_with(url="https://pypi.org/pypi/my-package/json", timeout=10.0)


@patch("feu.imports.optional.is_requests_available", lambda: False)
def test_fetch_pypi_wheel_filenames_no_requests() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        fetch_pypi_wheel_filenames("my_package")


##############################################################
#     Tests for fetch_pypi_pinned_dependency_version         #
##############################################################


def make_mock_pinned_dependency_response(requires_dist: list[str] | None) -> Response:
    resp = Mock(json=Mock(return_value={"info": {"requires_dist": requires_dist}}))
    resp.status_code = 200
    return resp


@requests_available
def test_fetch_pypi_pinned_dependency_version_exact_pin(monkeypatch: pytest.MonkeyPatch) -> None:
    session = make_mock_session(
        get=Mock(
            return_value=make_mock_pinned_dependency_response(
                ["pydantic-core==2.23.2", "typing-extensions>=4.6.1"]
            )
        )
    )
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_pypi_pinned_dependency_version("pydantic", "2.9.0", "pydantic-core") == "2.23.2"
    session.get.assert_called_once_with(
        url="https://pypi.org/pypi/pydantic/2.9.0/json", timeout=10.0
    )


@requests_available
def test_fetch_pypi_pinned_dependency_version_no_exact_pin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = make_mock_session(
        get=Mock(return_value=make_mock_pinned_dependency_response(["pydantic-core>=2.0,<3.0"]))
    )
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_pypi_pinned_dependency_version("pydantic", "2.9.0", "pydantic-core") is None


@requests_available
def test_fetch_pypi_pinned_dependency_version_dependency_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = make_mock_session(
        get=Mock(return_value=make_mock_pinned_dependency_response(["typing-extensions>=4.6.1"]))
    )
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_pypi_pinned_dependency_version("pydantic", "2.9.0", "pydantic-core") is None


@requests_available
def test_fetch_pypi_pinned_dependency_version_no_requires_dist(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = make_mock_session(get=Mock(return_value=make_mock_pinned_dependency_response(None)))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_pypi_pinned_dependency_version("pydantic", "2.9.0", "pydantic-core") is None


@patch("feu.imports.optional.is_requests_available", lambda: False)
def test_fetch_pypi_pinned_dependency_version_no_requests() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        fetch_pypi_pinned_dependency_version("pydantic", "2.9.0", "pydantic-core")


####################################
#     Tests for canonical names    #
####################################


@pytest.mark.parametrize(
    ("package", "expected"),
    [
        pytest.param("numpy", "https://pypi.org/pypi/numpy/json", id="canonical"),
        pytest.param("NumPy", "https://pypi.org/pypi/numpy/json", id="uppercase"),
        pytest.param("scikit_learn", "https://pypi.org/pypi/scikit-learn/json", id="underscore"),
        pytest.param("Zope.Interface", "https://pypi.org/pypi/zope-interface/json", id="dot"),
        pytest.param("a--b", "https://pypi.org/pypi/a-b/json", id="run_of_separators"),
    ],
)
def test_package_url(package: str, expected: str) -> None:
    assert _package_url(package) == expected


def test_package_url_with_version() -> None:
    assert (
        _package_url("Pydantic_Core", "2.23.2") == "https://pypi.org/pypi/pydantic-core/2.23.2/json"
    )


@requests_available
def test_fetch_pypi_versions_canonicalises_name(monkeypatch: pytest.MonkeyPatch) -> None:
    session = make_mock_session(get=Mock(return_value=make_mock_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    fetch_pypi_versions("Scikit_Learn")
    session.get.assert_called_once_with(url="https://pypi.org/pypi/scikit-learn/json", timeout=10.0)


@requests_available
def test_fetch_pypi_pinned_dependency_version_dependency_name_is_canonical(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = make_mock_session(
        get=Mock(return_value=make_mock_pinned_dependency_response(["pydantic_core==2.23.2"]))
    )
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_pypi_pinned_dependency_version("pydantic", "2.9.0", "Pydantic-Core") == "2.23.2"
