from __future__ import annotations

import pytest

from feu.compat.wheel_tags import (
    WheelTags,
    parse_arch,
    parse_os,
    parse_pure_python_tag,
    parse_python_tag,
    parse_wheel_filename,
)

#################################################
#     Tests for parse_wheel_filename            #
#################################################


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        (
            "numpy-2.3.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
            [WheelTags(python_version="3.12", free_threaded=False, os="linux", arch="x86_64")],
        ),
        (
            "numpy-2.3.0-cp314-cp314t-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
            [WheelTags(python_version="3.14", free_threaded=True, os="linux", arch="x86_64")],
        ),
        (
            "numpy-2.3.0-cp312-cp312-macosx_11_0_arm64.whl",
            [WheelTags(python_version="3.12", free_threaded=False, os="macos", arch="arm64")],
        ),
        (
            "numpy-2.3.0-cp39-cp39-win_amd64.whl",
            [WheelTags(python_version="3.9", free_threaded=False, os="windows", arch="x86_64")],
        ),
        (
            "numpy-2.3.0-cp310-cp310-manylinux_2_17_aarch64.manylinux2014_aarch64.whl",
            [WheelTags(python_version="3.10", free_threaded=False, os="linux", arch="arm64")],
        ),
        (
            "safetensors-0.4.5-cp39-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
            [
                WheelTags(
                    python_version="3.9", free_threaded=False, os="linux", arch="x86_64", abi3=True
                )
            ],
        ),
    ],
)
def test_parse_wheel_filename_recognized(filename: str, expected: list[WheelTags]) -> None:
    assert parse_wheel_filename(filename) == expected


def test_parse_wheel_filename_abi3_defaults_to_false() -> None:
    tags = parse_wheel_filename(
        "numpy-2.3.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl"
    )
    assert tags == [
        WheelTags(python_version="3.12", free_threaded=False, os="linux", arch="x86_64")
    ]
    assert tags[0].abi3 is False


def test_parse_wheel_filename_pure_python() -> None:
    assert parse_wheel_filename("click-8.1.8-py3-none-any.whl") == [
        WheelTags(python_version=None, free_threaded=False, os=None, arch=None)
    ]


def test_parse_wheel_filename_pure_python_compressed_tag() -> None:
    assert parse_wheel_filename("six-1.16.0-py2.py3-none-any.whl") == [
        WheelTags(python_version=None, free_threaded=False, os=None, arch=None),
        WheelTags(python_version=None, free_threaded=False, os=None, arch=None),
    ]


def test_parse_wheel_filename_pure_python_versioned_tag() -> None:
    assert parse_wheel_filename("pydantic-0.0.2-py36-none-any.whl") == [
        WheelTags(python_version="3.6", free_threaded=False, os=None, arch=None)
    ]


def test_parse_wheel_filename_pure_python_versioned_compressed_tag() -> None:
    assert parse_wheel_filename("pydantic-0.0.1-py35.py36-none-any.whl") == [
        WheelTags(python_version="3.5", free_threaded=False, os=None, arch=None),
        WheelTags(python_version="3.6", free_threaded=False, os=None, arch=None),
    ]


def test_parse_wheel_filename_pypy_returns_empty() -> None:
    assert parse_wheel_filename("numpy-2.3.0-pp310-pypy310_pp73-manylinux_2_17_x86_64.whl") == []


def test_parse_wheel_filename_unrecognized_platform_returns_empty() -> None:
    assert parse_wheel_filename("numpy-2.3.0-cp312-cp312-linux_i686.whl") == []


def test_parse_wheel_filename_universal2_returns_empty() -> None:
    assert parse_wheel_filename("numpy-2.3.0-cp312-cp312-macosx_11_0_universal2.whl") == []


def test_parse_wheel_filename_no_extension_match_returns_empty() -> None:
    assert parse_wheel_filename("not-a-wheel-file.tar.gz") == []


def test_parse_wheel_filename_too_few_components_returns_empty() -> None:
    assert parse_wheel_filename("numpy-2.3.0-cp312-cp312.whl") == []


def test_wheel_tags_is_frozen_and_comparable() -> None:
    a = WheelTags(python_version="3.11", free_threaded=False, os="linux", arch="x86_64")
    b = WheelTags(python_version="3.11", free_threaded=False, os="linux", arch="x86_64")
    assert a == b
    with pytest.raises(AttributeError):
        a.os = "macos"  # type: ignore[misc]


#################################################
#     Tests for parse_python_tag               #
#################################################


@pytest.mark.parametrize(
    ("python_tag", "expected"),
    [
        ("cp312", "3.12"),
        ("cp39", "3.9"),
        ("cp314", "3.14"),
    ],
)
def test_parse_python_tag_recognized(python_tag: str, expected: str) -> None:
    assert parse_python_tag(python_tag) == expected


@pytest.mark.parametrize("python_tag", ["py3", "pp310", "cpython312", "cp3x"])
def test_parse_python_tag_unrecognized_returns_none(python_tag: str) -> None:
    assert parse_python_tag(python_tag) is None


#################################################
#     Tests for parse_pure_python_tag          #
#################################################


@pytest.mark.parametrize(
    ("python_tag", "expected"),
    [
        ("py3", [None]),
        ("py2", [None]),
        ("py36", ["3.6"]),
        ("py2.py3", [None, None]),
        ("py35.py36", ["3.5", "3.6"]),
        ("py310", ["3.10"]),
    ],
)
def test_parse_pure_python_tag_recognized(python_tag: str, expected: list[str | None]) -> None:
    assert parse_pure_python_tag(python_tag) == expected


@pytest.mark.parametrize("python_tag", ["cp312", "pp310", "py3x", "py"])
def test_parse_pure_python_tag_unrecognized_returns_none(python_tag: str) -> None:
    assert parse_pure_python_tag(python_tag) is None


#################################################
#     Tests for parse_os                       #
#################################################


@pytest.mark.parametrize(
    ("platform_tag", "expected"),
    [
        ("manylinux_2_17_x86_64", "linux"),
        ("linux_x86_64", "linux"),
        ("macosx_11_0_arm64", "macos"),
        ("win_amd64", "windows"),
        ("win_arm64", "windows"),
        ("win32", "windows"),
    ],
)
def test_parse_os_recognized(platform_tag: str, expected: str) -> None:
    assert parse_os(platform_tag) == expected


def test_parse_os_unrecognized_returns_none() -> None:
    assert parse_os("freebsd_x86_64") is None


#################################################
#     Tests for parse_arch                     #
#################################################


@pytest.mark.parametrize(
    ("platform_tag", "expected"),
    [
        ("manylinux_2_17_x86_64", "x86_64"),
        ("win_amd64", "x86_64"),
        ("manylinux_2_17_aarch64", "arm64"),
        ("macosx_11_0_arm64", "arm64"),
    ],
)
def test_parse_arch_recognized(platform_tag: str, expected: str) -> None:
    assert parse_arch(platform_tag) == expected


def test_parse_arch_unrecognized_returns_none() -> None:
    assert parse_arch("manylinux_2_17_i686") is None
