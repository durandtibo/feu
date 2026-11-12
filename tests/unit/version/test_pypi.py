from __future__ import annotations

from datetime import UTC, date, datetime
from typing import TYPE_CHECKING, Any
from unittest.mock import Mock, patch

import pytest

from feu.version import (
    PypiFile,
    PypiProject,
    fetch_pypi_pinned_dependency_version,
    fetch_pypi_project,
    fetch_pypi_requires_python,
    fetch_pypi_versions,
    fetch_pypi_wheel_filenames,
)
from feu.version.pypi import (
    _fetch_pypi_project,
    _file_version,
    _is_yanked,
    _parse_project,
    _parse_upload_time,
    _release_date,
    _to_date,
)

if TYPE_CHECKING:
    from collections.abc import Generator

MODULE = "feu.version.pypi"


def _file(
    filename: str,
    *,
    requires_python: str | None = None,
    yanked: bool | str = False,
    upload_time: str | None = "2024-03-01T10:00:00.000000Z",
) -> dict[str, Any]:
    return {
        "filename": filename,
        "requires-python": requires_python,
        "yanked": yanked,
        "upload-time": upload_time,
        "url": f"https://files.pythonhosted.org/{filename}",
    }


# A recorded (trimmed) Simple API document in the JSON form (PEP 691 and PEP 700).
DOCUMENT: dict[str, Any] = {
    "meta": {"api-version": "1.4"},
    "name": "demo-pkg",
    "versions": ["1.10.0", "1.9.0", "2.0.0", "2.0.0rc1", "3.0.0", "legacy-version", "0.5.0"],
    "files": [
        _file(
            "demo_pkg-1.10.0-py3-none-any.whl",
            requires_python=">=3.9",
            upload_time="2024-03-01T10:00:00.000000Z",
        ),
        _file("demo_pkg-1.10.0.tar.gz", requires_python=">=3.8"),
        _file(
            "demo_pkg-1.9.0-cp39-cp39-manylinux_2_17_x86_64.whl", upload_time="2023-01-05T23:30:00Z"
        ),
        _file("demo_pkg-2.0.0-py3-none-any.whl", requires_python=">=3.10", yanked="broken"),
        _file("demo_pkg-2.0.0.tar.gz", yanked=True),
        _file("demo_pkg-2.0.0rc1.tar.gz", upload_time="2024-06-15T00:00:00Z"),
        _file("demo_pkg-1.9.0-py2.7.egg"),
        _file("demo_pkg-0.5.0.exe"),
        _file("demo_pkg-3.0.0.tar.gz", upload_time=None),
    ],
}


@pytest.fixture(autouse=True)
def _reset_cache() -> None:
    _fetch_pypi_project.cache_clear()
    fetch_pypi_pinned_dependency_version.cache_clear()


@pytest.fixture
def fetch_mock() -> Generator[Mock]:
    mock = Mock(return_value=DOCUMENT)
    with patch(f"{MODULE}.fetch_data", mock):
        yield mock


#########################
#     Tests for _to_date #
#########################


def test_to_date_date() -> None:
    assert _to_date(date(2024, 1, 2)) == date(2024, 1, 2)


def test_to_date_string() -> None:
    assert _to_date("2024-01-02") == date(2024, 1, 2)


def test_to_date_invalid_string() -> None:
    with pytest.raises(ValueError, match="Invalid isoformat string"):
        _to_date("not-a-date")


##################################
#     Tests for _parse_upload_time #
##################################


def test_parse_upload_time() -> None:
    assert _parse_upload_time("2017-05-03T20:58:46.547771Z") == datetime(
        2017, 5, 3, 20, 58, 46, 547771, tzinfo=UTC
    )


def test_parse_upload_time_converts_to_utc() -> None:
    assert _parse_upload_time("2024-03-01T01:00:00+02:00") == datetime(
        2024, 2, 29, 23, 0, tzinfo=UTC
    )


@pytest.mark.parametrize("value", [None, ""])
def test_parse_upload_time_empty(value: str | None) -> None:
    assert _parse_upload_time(value) is None


############################
#     Tests for _file_version #
############################


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("demo_pkg-1.2.3-py3-none-any.whl", "1.2.3"),
        ("demo_pkg-1.2.3-cp39-cp39-manylinux_2_17_x86_64.whl", "1.2.3"),
        ("demo-pkg-1.2.3.tar.gz", "1.2.3"),
        ("demo_pkg-1.2.3rc1.tar.gz", "1.2.3rc1"),
        ("demo_pkg-1.2.3.zip", "1.2.3"),
    ],
)
def test_file_version(filename: str, expected: str) -> None:
    assert str(_file_version(filename)) == expected


@pytest.mark.parametrize(
    "filename",
    [
        "demo_pkg-1.2.3-py2.7.egg",
        "demo_pkg-1.2.3.exe",
        "not-a-wheel.whl",
        "demo.tar.gz",
        "demo.msi",
    ],
)
def test_file_version_unrecognised(filename: str) -> None:
    assert _file_version(filename) is None


###############################
#     Tests for _parse_project #
###############################


def test_parse_project_whole_output() -> None:
    assert _parse_project("demo-pkg", DOCUMENT) == PypiProject(
        name="demo-pkg",
        releases={
            "0.5.0": (),
            "1.9.0": (
                PypiFile(
                    filename="demo_pkg-1.9.0-cp39-cp39-manylinux_2_17_x86_64.whl",
                    requires_python=None,
                    yanked=False,
                    uploaded=datetime(2023, 1, 5, 23, 30, tzinfo=UTC),
                ),
            ),
            "1.10.0": (
                PypiFile(
                    filename="demo_pkg-1.10.0-py3-none-any.whl",
                    requires_python=">=3.9",
                    yanked=False,
                    uploaded=datetime(2024, 3, 1, 10, 0, tzinfo=UTC),
                ),
                PypiFile(
                    filename="demo_pkg-1.10.0.tar.gz",
                    requires_python=">=3.8",
                    yanked=False,
                    uploaded=datetime(2024, 3, 1, 10, 0, tzinfo=UTC),
                ),
            ),
            "2.0.0rc1": (
                PypiFile(
                    filename="demo_pkg-2.0.0rc1.tar.gz",
                    requires_python=None,
                    yanked=False,
                    uploaded=datetime(2024, 6, 15, 0, 0, tzinfo=UTC),
                ),
            ),
            "2.0.0": (
                PypiFile(
                    filename="demo_pkg-2.0.0-py3-none-any.whl",
                    requires_python=">=3.10",
                    yanked=True,
                    uploaded=datetime(2024, 3, 1, 10, 0, tzinfo=UTC),
                ),
                PypiFile(
                    filename="demo_pkg-2.0.0.tar.gz",
                    requires_python=None,
                    yanked=True,
                    uploaded=datetime(2024, 3, 1, 10, 0, tzinfo=UTC),
                ),
            ),
            "3.0.0": (
                PypiFile(
                    filename="demo_pkg-3.0.0.tar.gz",
                    requires_python=None,
                    yanked=False,
                    uploaded=None,
                ),
            ),
        },
    )


def test_parse_project_pep440_order_not_string_order() -> None:
    assert list(_parse_project("demo-pkg", DOCUMENT).releases) == [
        "0.5.0",
        "1.9.0",
        "1.10.0",
        "2.0.0rc1",
        "2.0.0",
        "3.0.0",
    ]


def test_parse_project_skips_invalid_versions() -> None:
    assert "legacy-version" not in _parse_project("demo-pkg", DOCUMENT).releases


def test_parse_project_yanked_reason_is_true() -> None:
    project = _parse_project(
        "demo-pkg", {"versions": ["1.0"], "files": [_file("d-1.0.tar.gz", yanked="why")]}
    )
    assert project.releases["1.0"][0].yanked is True


def test_parse_project_file_version_not_in_versions_list() -> None:
    project = _parse_project("demo-pkg", {"versions": [], "files": [_file("d-1.0.tar.gz")]})
    assert list(project.releases) == ["1.0"]


def test_parse_project_empty_document() -> None:
    assert _parse_project("demo-pkg", {}) == PypiProject(name="demo-pkg", releases={})


def test_parse_project_releases_are_read_only() -> None:
    project = _parse_project("demo-pkg", DOCUMENT)
    with pytest.raises(TypeError, match="does not support item assignment"):
        project.releases["9.9.9"] = ()  # ty: ignore[invalid-assignment]


def test_parse_project_does_not_mutate_the_document() -> None:
    document = {"versions": ["1.0"], "files": [_file("d-1.0.tar.gz")]}
    expected = {"versions": ["1.0"], "files": [_file("d-1.0.tar.gz")]}
    _parse_project("demo-pkg", document)
    assert document == expected


def test_pypi_project_is_frozen() -> None:
    project = PypiProject(name="demo", releases={})
    with pytest.raises(AttributeError, match="cannot assign to field 'name'"):
        project.name = "other"  # ty: ignore[invalid-assignment]


#################################
#     Tests for fetch_pypi_project #
#################################


def test_fetch_pypi_project(fetch_mock: Mock) -> None:
    assert fetch_pypi_project("demo-pkg").name == "demo-pkg"
    fetch_mock.assert_called_once_with(
        url="https://pypi.org/simple/demo-pkg/",
        timeout=10,
        headers={"Accept": "application/vnd.pypi.simple.v1+json"},
    )


@pytest.mark.parametrize("name", ["Demo_Pkg", "DEMO.PKG", "demo--pkg"])
def test_fetch_pypi_project_canonicalises_the_name(fetch_mock: Mock, name: str) -> None:
    project = fetch_pypi_project(name)
    assert project.name == "demo-pkg"
    assert fetch_mock.call_args.kwargs["url"] == "https://pypi.org/simple/demo-pkg/"


def test_fetch_pypi_project_is_cached_by_canonical_name(fetch_mock: Mock) -> None:
    fetch_pypi_project("Demo_Pkg")
    fetch_pypi_project("demo-pkg")
    fetch_mock.assert_called_once()


@pytest.mark.usefixtures("fetch_mock")
def test_fetch_pypi_project_returns_the_same_object() -> None:
    assert fetch_pypi_project("demo-pkg") is fetch_pypi_project("DEMO-PKG")


def test_fetch_pypi_project_request_error() -> None:
    with (
        patch(f"{MODULE}.fetch_data", Mock(side_effect=RuntimeError("network down"))),
        pytest.raises(RuntimeError, match="network down"),
    ):
        fetch_pypi_project("demo-pkg")


def test_fetch_pypi_project_error_is_not_cached() -> None:
    with (
        patch(f"{MODULE}.fetch_data", Mock(side_effect=RuntimeError("network down"))),
        pytest.raises(RuntimeError, match="network down"),
    ):
        fetch_pypi_project("demo-pkg")
    with patch(f"{MODULE}.fetch_data", Mock(return_value=DOCUMENT)):
        assert fetch_pypi_project("demo-pkg").name == "demo-pkg"


########################################
#     Tests for _is_yanked, _release_date #
########################################


def test_is_yanked_all_files_yanked() -> None:
    assert _is_yanked((PypiFile("a", None, True, None), PypiFile("b", None, True, None)))


def test_is_yanked_some_files_yanked() -> None:
    assert not _is_yanked((PypiFile("a", None, True, None), PypiFile("b", None, False, None)))


def test_is_yanked_no_files() -> None:
    assert not _is_yanked(())


def test_release_date_is_the_earliest_upload_time() -> None:
    files = (
        PypiFile("a", None, False, datetime(2024, 2, 1, tzinfo=UTC)),
        PypiFile("b", None, False, datetime(2024, 1, 31, 23, 59, tzinfo=UTC)),
        PypiFile("c", None, False, None),
    )
    assert _release_date(files) == date(2024, 1, 31)


def test_release_date_no_upload_time() -> None:
    assert _release_date((PypiFile("a", None, False, None),)) is None


def test_release_date_no_files() -> None:
    assert _release_date(()) is None


#################################
#     Tests for fetch_pypi_versions #
#################################


@pytest.mark.usefixtures("fetch_mock")
def test_fetch_pypi_versions() -> None:
    assert fetch_pypi_versions("demo-pkg") == ("0.5.0", "1.9.0", "1.10.0", "2.0.0rc1", "3.0.0")


@pytest.mark.usefixtures("fetch_mock")
def test_fetch_pypi_versions_include_yanked() -> None:
    assert fetch_pypi_versions("demo-pkg", ignore_yanked=False) == (
        "0.5.0",
        "1.9.0",
        "1.10.0",
        "2.0.0rc1",
        "2.0.0",
        "3.0.0",
    )


@pytest.mark.usefixtures("fetch_mock")
def test_fetch_pypi_versions_start_date_is_inclusive() -> None:
    assert fetch_pypi_versions("demo-pkg", start_date="2024-03-01") == ("1.10.0", "2.0.0rc1")


@pytest.mark.usefixtures("fetch_mock")
def test_fetch_pypi_versions_end_date_is_inclusive() -> None:
    assert fetch_pypi_versions("demo-pkg", end_date=date(2023, 1, 5)) == ("1.9.0",)


@pytest.mark.usefixtures("fetch_mock")
def test_fetch_pypi_versions_date_range() -> None:
    assert fetch_pypi_versions("demo-pkg", start_date="2024-01-01", end_date="2024-03-01") == (
        "1.10.0",
    )


@pytest.mark.usefixtures("fetch_mock")
def test_fetch_pypi_versions_dates_are_utc() -> None:
    # 1.9.0 was uploaded on 2023-01-05 at 23:30 UTC.
    assert fetch_pypi_versions("demo-pkg", start_date="2023-01-06", end_date="2023-12-31") == ()


@pytest.mark.usefixtures("fetch_mock")
def test_fetch_pypi_versions_date_filter_drops_versions_without_files() -> None:
    assert "0.5.0" not in fetch_pypi_versions("demo-pkg", start_date="1990-01-01")


@pytest.mark.usefixtures("fetch_mock")
def test_fetch_pypi_versions_date_filter_drops_versions_without_upload_time() -> None:
    assert "3.0.0" not in fetch_pypi_versions("demo-pkg", start_date="1990-01-01")


@pytest.mark.usefixtures("fetch_mock")
def test_fetch_pypi_versions_has_no_reverse_option() -> None:
    with pytest.raises(TypeError, match="reverse"):
        fetch_pypi_versions("demo-pkg", reverse=True)  # ty: ignore[unknown-argument]


@pytest.mark.usefixtures("fetch_mock")
def test_fetch_pypi_versions_options_are_keyword_only() -> None:
    with pytest.raises(TypeError, match="positional argument"):
        fetch_pypi_versions("demo-pkg", "2024-01-01")  # ty: ignore[too-many-positional-arguments]


@pytest.mark.usefixtures("fetch_mock")
def test_fetch_pypi_versions_invalid_date() -> None:
    with pytest.raises(ValueError, match="Invalid isoformat string"):
        fetch_pypi_versions("demo-pkg", start_date="not-a-date")


@pytest.mark.usefixtures("fetch_mock")
def test_fetch_pypi_versions_is_a_tuple() -> None:
    assert isinstance(fetch_pypi_versions("demo-pkg"), tuple)


def test_fetch_pypi_versions_makes_one_request_per_project(fetch_mock: Mock) -> None:
    fetch_pypi_versions("demo-pkg")
    fetch_pypi_versions("demo-pkg", start_date="2024-01-01")
    fetch_pypi_requires_python("demo-pkg")
    fetch_pypi_wheel_filenames("demo-pkg")
    fetch_mock.assert_called_once()


####################################
#     Tests for fetch_pypi_requires_python #
####################################


@pytest.mark.usefixtures("fetch_mock")
def test_fetch_pypi_requires_python_whole_output() -> None:
    assert fetch_pypi_requires_python("demo-pkg") == {
        "0.5.0": None,
        "1.9.0": None,
        "1.10.0": ">=3.9",
        "2.0.0rc1": None,
        "2.0.0": ">=3.10",
        "3.0.0": None,
    }


@pytest.mark.usefixtures("fetch_mock")
def test_fetch_pypi_requires_python_is_read_only() -> None:
    mapping = fetch_pypi_requires_python("demo-pkg")
    with pytest.raises(TypeError, match="does not support item assignment"):
        mapping["9.9.9"] = ">=3.9"  # ty: ignore[invalid-assignment]


@pytest.mark.usefixtures("fetch_mock")
def test_fetch_pypi_requires_python_does_not_change_the_cached_project() -> None:
    fetch_pypi_requires_python("demo-pkg")
    assert fetch_pypi_project("demo-pkg").releases["1.10.0"][0].requires_python == ">=3.9"


#########################################
#     Tests for fetch_pypi_wheel_filenames #
#########################################


@pytest.mark.usefixtures("fetch_mock")
def test_fetch_pypi_wheel_filenames_whole_output() -> None:
    assert fetch_pypi_wheel_filenames("demo-pkg") == {
        "0.5.0": (),
        "1.9.0": ("demo_pkg-1.9.0-cp39-cp39-manylinux_2_17_x86_64.whl",),
        "1.10.0": ("demo_pkg-1.10.0-py3-none-any.whl",),
        "2.0.0rc1": (),
        "2.0.0": ("demo_pkg-2.0.0-py3-none-any.whl",),
        "3.0.0": (),
    }


@pytest.mark.usefixtures("fetch_mock")
def test_fetch_pypi_wheel_filenames_is_read_only() -> None:
    mapping = fetch_pypi_wheel_filenames("demo-pkg")
    with pytest.raises(TypeError, match="does not support item assignment"):
        mapping["9.9.9"] = ()  # ty: ignore[invalid-assignment]


########################################################
#     Tests for fetch_pypi_pinned_dependency_version   #
########################################################


def _metadata(requires_dist: list[str] | None) -> dict[str, Any]:
    return {"info": {"requires_dist": requires_dist}}


def test_fetch_pypi_pinned_dependency_version_exact_pin() -> None:
    mock = Mock(return_value=_metadata(["pydantic-core==2.23.2", "typing-extensions>=4.6.1"]))
    with patch(f"{MODULE}.fetch_data", mock):
        assert (
            fetch_pypi_pinned_dependency_version("pydantic", "2.9.0", "pydantic-core") == "2.23.2"
        )
    mock.assert_called_once_with(url="https://pypi.org/pypi/pydantic/2.9.0/json", timeout=10)


def test_fetch_pypi_pinned_dependency_version_canonicalises_the_package_name() -> None:
    mock = Mock(return_value=_metadata([]))
    with patch(f"{MODULE}.fetch_data", mock):
        fetch_pypi_pinned_dependency_version("Pydantic_Core", "2.9.0", "x")
    assert mock.call_args.kwargs["url"] == "https://pypi.org/pypi/pydantic-core/2.9.0/json"


def test_fetch_pypi_pinned_dependency_version_dependency_name_is_canonical() -> None:
    with patch(f"{MODULE}.fetch_data", Mock(return_value=_metadata(["pydantic_core==2.23.2"]))):
        assert (
            fetch_pypi_pinned_dependency_version("pydantic", "2.9.0", "Pydantic-Core") == "2.23.2"
        )


def test_fetch_pypi_pinned_dependency_version_no_exact_pin() -> None:
    with patch(f"{MODULE}.fetch_data", Mock(return_value=_metadata(["pydantic-core>=2.0,<3.0"]))):
        assert fetch_pypi_pinned_dependency_version("pydantic", "2.9.0", "pydantic-core") is None


def test_fetch_pypi_pinned_dependency_version_dependency_not_found() -> None:
    with patch(f"{MODULE}.fetch_data", Mock(return_value=_metadata(["typing-extensions==4.6.1"]))):
        assert fetch_pypi_pinned_dependency_version("pydantic", "2.9.0", "pydantic-core") is None


@pytest.mark.parametrize("requires_dist", [None, []])
def test_fetch_pypi_pinned_dependency_version_no_requires_dist(
    requires_dist: list[str] | None,
) -> None:
    with patch(f"{MODULE}.fetch_data", Mock(return_value=_metadata(requires_dist))):
        assert fetch_pypi_pinned_dependency_version("pydantic", "2.9.0", "pydantic-core") is None


def test_fetch_pypi_pinned_dependency_version_skips_a_requirement_with_a_marker() -> None:
    requires_dist = ['pydantic-core==2.0.0; python_version < "3.9"', "pydantic-core==2.23.2"]
    with patch(f"{MODULE}.fetch_data", Mock(return_value=_metadata(requires_dist))):
        assert (
            fetch_pypi_pinned_dependency_version("pydantic", "2.9.0", "pydantic-core") == "2.23.2"
        )


def test_fetch_pypi_pinned_dependency_version_only_a_marker_requirement() -> None:
    requires_dist = ['pydantic-core==2.0.0; python_version < "3.9"']
    with patch(f"{MODULE}.fetch_data", Mock(return_value=_metadata(requires_dist))):
        assert fetch_pypi_pinned_dependency_version("pydantic", "2.9.0", "pydantic-core") is None


def test_fetch_pypi_pinned_dependency_version_is_cached() -> None:
    mock = Mock(return_value=_metadata(["pydantic-core==2.23.2"]))
    with patch(f"{MODULE}.fetch_data", mock):
        fetch_pypi_pinned_dependency_version("pydantic", "2.9.0", "pydantic-core")
        fetch_pypi_pinned_dependency_version("pydantic", "2.9.0", "pydantic-core")
    mock.assert_called_once()
