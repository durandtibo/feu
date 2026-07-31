from __future__ import annotations

import pytest

from feu.compat.wheel_tags import WheelTags, parse_wheel_filename

#################################################
#     Tests for parse_wheel_filename            #
#################################################


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        (
            "numpy-2.3.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
            WheelTags(python_version="3.12", free_threaded=False, os="linux", arch="x86_64"),
        ),
        (
            "numpy-2.3.0-cp314-cp314t-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
            WheelTags(python_version="3.14", free_threaded=True, os="linux", arch="x86_64"),
        ),
        (
            "numpy-2.3.0-cp312-cp312-macosx_11_0_arm64.whl",
            WheelTags(python_version="3.12", free_threaded=False, os="macos", arch="arm64"),
        ),
        (
            "numpy-2.3.0-cp39-cp39-win_amd64.whl",
            WheelTags(python_version="3.9", free_threaded=False, os="windows", arch="x86_64"),
        ),
        (
            "numpy-2.3.0-cp310-cp310-manylinux_2_17_aarch64.manylinux2014_aarch64.whl",
            WheelTags(python_version="3.10", free_threaded=False, os="linux", arch="arm64"),
        ),
    ],
)
def test_parse_wheel_filename_recognized(filename: str, expected: WheelTags) -> None:
    assert parse_wheel_filename(filename) == expected


def test_parse_wheel_filename_pure_python_returns_none() -> None:
    assert parse_wheel_filename("click-8.1.8-py3-none-any.whl") is None


def test_parse_wheel_filename_pypy_returns_none() -> None:
    assert parse_wheel_filename("numpy-2.3.0-pp310-pypy310_pp73-manylinux_2_17_x86_64.whl") is None


def test_parse_wheel_filename_unrecognized_platform_returns_none() -> None:
    assert parse_wheel_filename("numpy-2.3.0-cp312-cp312-linux_i686.whl") is None


def test_parse_wheel_filename_universal2_returns_none() -> None:
    assert parse_wheel_filename("numpy-2.3.0-cp312-cp312-macosx_11_0_universal2.whl") is None


def test_parse_wheel_filename_no_extension_match_returns_none() -> None:
    assert parse_wheel_filename("not-a-wheel-file.tar.gz") is None


def test_wheel_tags_is_frozen_and_comparable() -> None:
    a = WheelTags(python_version="3.11", free_threaded=False, os="linux", arch="x86_64")
    b = WheelTags(python_version="3.11", free_threaded=False, os="linux", arch="x86_64")
    assert a == b
    with pytest.raises(AttributeError):
        a.os = "macos"  # type: ignore[misc]
