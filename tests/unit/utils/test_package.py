from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from feu.utils.package import (
    PackageDependency,
    PackageSpec,
    extract_package_extras,
    extract_package_name,
    generate_extras_string,
)

if TYPE_CHECKING:
    from collections.abc import Sequence


#################################
#     Tests for PackageSpec     #
#################################


def test_package_spec_name() -> None:
    assert PackageSpec("my_package").name == "my_package"


def test_package_spec_version() -> None:
    assert PackageSpec("my_package", version="1.2.3").version == "1.2.3"


def test_package_spec_extras() -> None:
    assert PackageSpec("my_package", version="1.2.3", extras=["security", "socks"]).extras == [
        "security",
        "socks",
    ]


def test_package_spec_str_name() -> None:
    assert str(PackageSpec("my_package")) == "my_package"


def test_package_spec_str_version() -> None:
    assert str(PackageSpec("my_package", version="1.2.3")) == "my_package==1.2.3"


def test_package_spec_str_extras() -> None:
    assert (
        str(PackageSpec("my_package", version="1.2.3", extras=["security", "socks"]))
        == "my_package[security,socks]==1.2.3"
    )


def test_package_spec_str_extras_empty() -> None:
    assert str(PackageSpec("my_package", version="1.2.3", extras=[])) == "my_package==1.2.3"


def test_package_spec_to_package_dependency_name() -> None:
    assert PackageSpec("my_package").to_package_dependency() == PackageDependency("my_package")


def test_package_spec_to_package_dependency_version() -> None:
    assert PackageSpec("my_package", version="1.2.3").to_package_dependency() == PackageDependency(
        "my_package", version_specifiers=["==1.2.3"]
    )


def test_package_spec_to_package_dependency_extras() -> None:
    assert PackageSpec(
        "my_package", version="1.2.3", extras=["security", "socks"]
    ).to_package_dependency() == PackageDependency(
        "my_package", version_specifiers=["==1.2.3"], extras=["security", "socks"]
    )


def test_package_spec_to_package_dependency_extras_empty() -> None:
    assert PackageSpec(
        "my_package", version="1.2.3", extras=[]
    ).to_package_dependency() == PackageDependency(
        "my_package", version_specifiers=["==1.2.3"], extras=[]
    )


def test_package_spec_eq_true_name() -> None:
    assert PackageSpec("my_package") == PackageSpec("my_package")


def test_package_spec_eq_true_version() -> None:
    assert PackageSpec("my_package", version="1.2.3") == PackageSpec("my_package", version="1.2.3")


def test_package_spec_eq_true_extras() -> None:
    assert PackageSpec("my_package", version="1.2.3", extras=["security", "socks"]) == PackageSpec(
        "my_package", version="1.2.3", extras=["security", "socks"]
    )


def test_package_spec_eq_false_different_name() -> None:
    assert PackageSpec("my_package") != PackageSpec("my")


def test_package_spec_eq_false_different_version() -> None:
    assert PackageSpec("my_package", version="1.2.3") != PackageSpec("my_package", version="2.0.0")


def test_package_spec_eq_false_different_extras() -> None:
    assert PackageSpec("my_package", version="1.2.3", extras=["security", "socks"]) != PackageSpec(
        "my_package", version="1.2.3", extras=["dev"]
    )


def test_package_spec_with_version() -> None:
    pkg1 = PackageSpec(name="my_package", version="1.2.0")
    pkg2 = pkg1.with_version("1.2.3")
    assert pkg1 is not pkg2
    assert pkg1 == PackageSpec(name="my_package", version="1.2.0")
    assert pkg2 == PackageSpec(name="my_package", version="1.2.3")


def test_package_spec_with_version_no_version() -> None:
    pkg1 = PackageSpec("my_package")
    pkg2 = pkg1.with_version("1.2.3")
    assert pkg1 is not pkg2
    assert pkg1 == PackageSpec(name="my_package")
    assert pkg2 == PackageSpec(name="my_package", version="1.2.3")


def test_package_spec_with_version_extras() -> None:
    pkg1 = PackageSpec(name="my_package", version="1.2.0", extras=["dev"])
    pkg2 = pkg1.with_version("1.2.3")
    assert pkg1 is not pkg2
    assert pkg1 == PackageSpec(name="my_package", version="1.2.0", extras=["dev"])
    assert pkg2 == PackageSpec(name="my_package", version="1.2.3", extras=["dev"])
    assert pkg1.extras is not pkg2.extras


#######################################
#     Tests for PackageDependency     #
#######################################


def test_package_dependency_name() -> None:
    assert PackageDependency("my_package").name == "my_package"


def test_package_dependency_version_specifiers() -> None:
    assert PackageDependency("my_package", version_specifiers=["==1.2.3"]).version_specifiers == [
        "==1.2.3"
    ]


def test_package_dependency_extras() -> None:
    assert PackageDependency(
        "my_package", version_specifiers=["==1.2.3"], extras=["security", "socks"]
    ).extras == [
        "security",
        "socks",
    ]


def test_package_dependency_str_name() -> None:
    assert str(PackageDependency("my_package")) == "my_package"


def test_package_dependency_str_version_specifiers() -> None:
    assert (
        str(PackageDependency("my_package", version_specifiers=["==1.2.3"])) == "my_package==1.2.3"
    )


def test_package_dependency_str_version_specifiers_2() -> None:
    assert (
        str(PackageDependency("my_package", version_specifiers=[">=1.2.3", "<2.0"]))
        == "my_package>=1.2.3,<2.0"
    )


def test_package_dependency_str_version_specifiers_empty() -> None:
    assert str(PackageDependency("my_package", version_specifiers=[])) == "my_package"


def test_package_dependency_str_extras() -> None:
    assert (
        str(
            PackageDependency(
                "my_package", version_specifiers=["==1.2.3"], extras=["security", "socks"]
            )
        )
        == "my_package[security,socks]==1.2.3"
    )


def test_package_dependency_str_extras_empty() -> None:
    assert (
        str(PackageDependency("my_package", version_specifiers=["==1.2.3"], extras=[]))
        == "my_package==1.2.3"
    )


def test_package_dependency_eq_true_name() -> None:
    assert PackageDependency("my_package") == PackageDependency("my_package")


def test_package_dependency_eq_true_version_specifiers() -> None:
    assert PackageDependency("my_package", version_specifiers=["==1.2.3"]) == PackageDependency(
        "my_package", version_specifiers=["==1.2.3"]
    )


def test_package_dependency_eq_true_extras() -> None:
    assert PackageDependency(
        "my_package", version_specifiers=["==1.2.3"], extras=["security", "socks"]
    ) == PackageDependency(
        "my_package", version_specifiers=["==1.2.3"], extras=["security", "socks"]
    )


def test_package_dependency_eq_false_different_name() -> None:
    assert PackageDependency("my_package") != PackageDependency("my")


def test_package_dependency_eq_false_different_version_specifiers() -> None:
    assert PackageDependency("my_package", version_specifiers=["==1.2.3"]) != PackageDependency(
        "my_package", version_specifiers=["==2.0.0"]
    )


def test_package_dependency_eq_false_different_extras() -> None:
    assert PackageDependency(
        "my_package", version_specifiers=["==1.2.3"], extras=["security", "socks"]
    ) != PackageDependency("my_package", version_specifiers=["==1.2.3"], extras=["dev"])


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
def test_extract_package_extras(requirement: str, expected: list[str]) -> None:
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
