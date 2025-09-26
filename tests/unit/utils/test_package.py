from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from feu.utils.package import (
    extract_package_extras,
    extract_package_name,
    generate_extras_string,
)

if TYPE_CHECKING:
    from collections.abc import Sequence


##########################################
#     Tests for extract_package_name     #
##########################################


@pytest.mark.parametrize(
    ("requirement", "expected"),
    [
        ("numpy", "numpy"),
        ("pandas[performance]", "pandas"),
        ("requests[security,socks]", "requests"),
        ("some-package[extra1,extra2]", "some-package"),
    ],
)
def test_extract_package_name(requirement: str, expected: str) -> None:
    assert extract_package_name(requirement) == expected


############################################
#     Tests for extract_package_extras     #
############################################


@pytest.mark.parametrize(
    ("requirement", "expected"),
    [
        ("numpy", []),
        ("pandas[performance]", ["performance"]),
        ("requests[security,socks]", ["security", "socks"]),
        ("some-package[extra1,extra2]", ["extra1", "extra2"]),
    ],
)
def test_extract_package_extras(requirement: str, expected: str) -> None:
    assert extract_package_extras(requirement) == expected


############################################
#     Tests for generate_extras_string     #
############################################


@pytest.mark.parametrize(
    ("extras", "expected"),
    [
        ([], ""),
        (["security"], "[security]"),
        (["security", "socks"], "[security,socks]"),
        (("security", "socks"), "[security,socks]"),
    ],
)
def test_generate_extras_string(extras: Sequence[str], expected: str) -> None:
    assert generate_extras_string(extras) == expected
