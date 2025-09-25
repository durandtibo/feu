from __future__ import annotations

import pytest

from feu.utils.package import extract_package_name

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
