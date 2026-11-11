from __future__ import annotations

import pytest

from feu.compat.wheel_tags import WheelTag, parse_wheel_filename

LINUX_X86 = "manylinux_2_17_x86_64.manylinux2014_x86_64"


def _tag(
    python_version: str | None,
    os: str | None,
    arch: str | None,
    *,
    free_threaded: bool = False,
    abi3: bool = False,
) -> WheelTag:
    return WheelTag(
        python_version=python_version, free_threaded=free_threaded, os=os, arch=arch, abi3=abi3
    )


########################################
#     Tests for parse_wheel_filename   #
########################################


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        pytest.param(
            f"numpy-2.3.0-cp312-cp312-{LINUX_X86}.whl",
            (_tag("3.12", "linux", "x86_64"),),
            id="manylinux_x86_64",
        ),
        pytest.param(
            "numpy-2.3.0-cp310-cp310-manylinux_2_17_aarch64.manylinux2014_aarch64.whl",
            (_tag("3.10", "linux", "arm64"),),
            id="manylinux_aarch64",
        ),
        pytest.param(
            "numpy-2.3.0-cp312-cp312-linux_x86_64.whl",
            (_tag("3.12", "linux", "x86_64"),),
            id="linux",
        ),
        pytest.param(
            "numpy-2.3.0-cp39-cp39-manylinux2014_x86_64.whl",
            (_tag("3.9", "linux", "x86_64"),),
            id="manylinux2014",
        ),
        pytest.param(
            "numpy-2.3.0-cp312-cp312-macosx_10_9_x86_64.whl",
            (_tag("3.12", "macos", "x86_64"),),
            id="macos_x86_64",
        ),
        pytest.param(
            "numpy-2.3.0-cp312-cp312-macosx_11_0_arm64.whl",
            (_tag("3.12", "macos", "arm64"),),
            id="macos_arm64",
        ),
        pytest.param(
            "numpy-2.3.0-cp39-cp39-win_amd64.whl",
            (_tag("3.9", "windows", "x86_64"),),
            id="win_amd64",
        ),
        pytest.param(
            "numpy-2.3.0-cp311-cp311-win_arm64.whl",
            (_tag("3.11", "windows", "arm64"),),
            id="win_arm64",
        ),
        pytest.param(
            f"numpy-2.3.0-cp314-cp314t-{LINUX_X86}.whl",
            (_tag("3.14", "linux", "x86_64", free_threaded=True),),
            id="free_threaded",
        ),
        pytest.param(
            f"safetensors-0.4.5-cp39-abi3-{LINUX_X86}.whl",
            (_tag("3.9", "linux", "x86_64", abi3=True),),
            id="abi3",
        ),
        pytest.param(
            "pkg-1.0-cp315-abi3t-win_amd64.whl",
            (_tag("3.15", "windows", "x86_64", free_threaded=True, abi3=True),),
            id="abi3t",
        ),
        pytest.param(
            "numpy-2.3.0-cp312-cp312-macosx_11_0_universal2.whl",
            (_tag("3.12", "macos", "arm64"), _tag("3.12", "macos", "x86_64")),
            id="universal2",
        ),
        pytest.param(
            "pkg-1.0-cp39-abi3-macosx_10_9_universal2.whl",
            (_tag("3.9", "macos", "arm64", abi3=True), _tag("3.9", "macos", "x86_64", abi3=True)),
            id="abi3_universal2",
        ),
        pytest.param(
            "pkg-1.0-cp310-cp310-macosx_10_9_x86_64.macosx_11_0_arm64.whl",
            (_tag("3.10", "macos", "arm64"), _tag("3.10", "macos", "x86_64")),
            id="compressed_macos",
        ),
        pytest.param(
            "pkg-1.0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.linux_x86_64.whl",
            (_tag("3.10", "linux", "x86_64"),),
            id="compressed_duplicates",
        ),
        pytest.param("pkg-1.0-py3-none-any.whl", (_tag(None, None, None),), id="pure_python"),
        pytest.param(
            "pkg-1.0-py2.py3-none-any.whl", (_tag(None, None, None),), id="pure_python_py2_py3"
        ),
        pytest.param("pkg-1.0-py39-none-any.whl", (_tag(None, None, None),), id="pure_python_py39"),
        pytest.param(
            "pkg-1.0-1-py3-none-any.whl", (_tag(None, None, None),), id="pure_python_build_tag"
        ),
    ],
)
def test_parse_wheel_filename(filename: str, expected: tuple[WheelTag, ...]) -> None:
    assert parse_wheel_filename(filename) == expected


@pytest.mark.parametrize(
    "filename",
    [
        pytest.param("pkg-1.0-cp312-cp312-musllinux_1_2_x86_64.whl", id="musllinux"),
        pytest.param("pkg-1.0-cp312-cp312-musllinux_1_2_aarch64.whl", id="musllinux_aarch64"),
        pytest.param("pkg-1.0-cp312-cp312-win32.whl", id="win32"),
        pytest.param("pkg-1.0-cp312-cp312-manylinux2014_i686.whl", id="i686"),
        pytest.param("pkg-1.0-cp312-cp312-manylinux_2_17_armv7l.whl", id="armv7l"),
        pytest.param("pkg-1.0-cp312-cp312-manylinux_2_17_ppc64le.whl", id="ppc64le"),
        pytest.param("pkg-1.0-cp312-cp312-manylinux_2_17_s390x.whl", id="s390x"),
        pytest.param("pkg-1.0-cp310-cp310-macosx_10_6_intel.whl", id="macos_intel"),
        pytest.param("pkg-1.0-cp312-cp312-ios_13_0_arm64_iphoneos.whl", id="ios"),
        pytest.param("pkg-1.0-cp312-cp312-android_21_arm64_v8a.whl", id="android"),
        pytest.param("pkg-1.0-pp310-pypy310_pp73-manylinux2014_x86_64.whl", id="pypy"),
        pytest.param("pkg-1.0-graalpy311-graalpy242_311_native-win_amd64.whl", id="graalpy"),
        pytest.param("pkg-1.0-cp27-cp27mu-manylinux1_x86_64.whl", id="cpython_2"),
    ],
)
def test_parse_wheel_filename_out_of_scope(filename: str) -> None:
    assert parse_wheel_filename(filename) == ()


@pytest.mark.parametrize(
    "filename",
    ["pkg-1.0.tar.gz", "pkg-1.0-py2.7.egg", "not-a-wheel.whl", "pkg-1.0.whl", "", ".whl"],
)
def test_parse_wheel_filename_invalid(filename: str) -> None:
    assert parse_wheel_filename(filename) == ()


def test_parse_wheel_filename_abi3_defaults_to_false() -> None:
    (tag,) = parse_wheel_filename(f"numpy-2.3.0-cp312-cp312-{LINUX_X86}.whl")
    assert not tag.abi3


def test_parse_wheel_filename_mixed_in_scope_and_out_of_scope_tags() -> None:
    filename = "pkg-1.0-cp312-cp312-manylinux_2_17_x86_64.musllinux_1_2_x86_64.whl"
    assert parse_wheel_filename(filename) == (_tag("3.12", "linux", "x86_64"),)


def test_parse_wheel_filename_is_deterministic() -> None:
    filename = "pkg-1.0-cp310-cp310-macosx_10_9_x86_64.macosx_11_0_arm64.macosx_11_0_universal2.whl"
    assert parse_wheel_filename(filename) == parse_wheel_filename(filename)


def test_parse_wheel_filename_returns_a_tuple() -> None:
    assert isinstance(parse_wheel_filename(f"numpy-2.3.0-cp312-cp312-{LINUX_X86}.whl"), tuple)


###############################
#     Tests for WheelTag      #
###############################


def test_wheel_tag_is_hashable() -> None:
    assert len({_tag("3.12", "linux", "x86_64"), _tag("3.12", "linux", "x86_64")}) == 1


def test_wheel_tag_repr() -> None:
    assert repr(_tag("3.12", "linux", "x86_64")) == (
        "WheelTag(python_version='3.12', free_threaded=False, os='linux', arch='x86_64', abi3=False)"
    )
