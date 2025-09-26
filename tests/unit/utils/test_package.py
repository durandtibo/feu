from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from feu.utils.package import extract_package_name, generate_extras_string

if TYPE_CHECKING:
    from collections.abc import Sequence

##########################################
#     Tests for extract_package_name     #
##########################################


@pytest.mark.parametrize(
    ("requirement", "expected"),
    [
        ("requests[security,socks]", "requests"),
        ("numpy", "numpy"),
        ("pandas[performance]", "pandas"),
        ("some-package[extra1,extra2]", "some-package"),
    ],
)
def test_extract_package_name(requirement: str, expected: str) -> None:
    assert extract_package_name(requirement) == expected


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
