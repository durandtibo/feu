from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pytest

from feu.version import (
    PackageBounds,
    fetch_latest_major_versions_map,
    fetch_latest_minor_versions_map,
    fetch_latest_stable_version,
    fetch_latest_version,
    fetch_latest_versions,
    fetch_package_versions,
    fetch_versions,
)

if TYPE_CHECKING:
    from contextlib import AbstractContextManager
    from pathlib import Path

MODULE = "feu.version.package"
VERSIONS = ("1.0.0", "1.0.1", "1.1.0", "1.1.2", "2.0.0", "2.0.3")


def make_bounds(name: str, lower: str | None = None, upper: str | None = None) -> PackageBounds:
    """Convenience factory to create PackageBounds without specifying
    section."""
    return PackageBounds(name=name, lower=lower, upper=upper, section="project.dependencies")


def patched_versions(versions: tuple[str, ...] = VERSIONS) -> AbstractContextManager[Mock]:
    return patch(f"{MODULE}.fetch_pypi_versions", Mock(return_value=versions))


####################################
#     Tests for fetch_versions     #
####################################


def test_fetch_versions() -> None:
    with patched_versions():
        assert fetch_versions("my_package") == VERSIONS


def test_fetch_versions_lower() -> None:
    with patched_versions():
        assert fetch_versions("my_package", lower="1.1.0") == ("1.1.0", "1.1.2", "2.0.0", "2.0.3")


def test_fetch_versions_upper_is_exclusive() -> None:
    with patched_versions():
        assert fetch_versions("my_package", upper="1.1.0") == ("1.0.0", "1.0.1")


def test_fetch_versions_range() -> None:
    with patched_versions():
        assert fetch_versions("my_package", lower="1.1.0", upper="2.0.0") == ("1.1.0", "1.1.2")


def test_fetch_versions_filters_invalid_unstable_and_duplicates_and_sorts() -> None:
    with patched_versions(("2.0.0", "1.10.0", "1.9.0", "1.9.0", "2.0.0rc1", "not-a-version")):
        assert fetch_versions("my_package") == ("1.9.0", "1.10.0", "2.0.0")


def test_fetch_versions_bounds_are_keyword_only() -> None:
    with patched_versions(), pytest.raises(TypeError, match="positional argument"):
        fetch_versions("my_package", "1.1.0")  # ty: ignore[too-many-positional-arguments]


#########################################
#     Tests for fetch_latest_versions   #
#########################################


def test_fetch_latest_versions_major() -> None:
    with patched_versions():
        assert fetch_latest_versions("my_package", group="major") == ("1.1.2", "2.0.3")


def test_fetch_latest_versions_minor() -> None:
    with patched_versions():
        assert fetch_latest_versions("my_package", group="minor") == ("1.0.1", "1.1.2", "2.0.3")


def test_fetch_latest_versions_invalid_group() -> None:
    with pytest.raises(ValueError, match=r"group must be 'major' or 'minor' but received 'patch'"):
        fetch_latest_versions("my_package", group="patch")  # ty: ignore[invalid-argument-type]


def test_fetch_latest_versions_group_is_required() -> None:
    with pytest.raises(TypeError, match="group"):
        fetch_latest_versions("my_package")  # ty: ignore[missing-argument]


@pytest.mark.parametrize(("group", "expected"), [("major", ("1.1.2",)), ("minor", ("1.1.2",))])
def test_fetch_latest_versions_range(group: str, expected: tuple[str, ...]) -> None:
    with patched_versions():
        assert (
            fetch_latest_versions("my_package", group=group, lower="1.1.0", upper="2.0.0")  # ty: ignore[invalid-argument-type]
            == expected
        )


def test_fetch_latest_versions_include_lower_bound_with_lower() -> None:
    with patched_versions():
        assert fetch_latest_versions(
            "my_package", group="major", lower="1.1.0", include_lower_bound=True
        ) == ("1.1.0", "1.1.2", "2.0.3")


def test_fetch_latest_versions_minor_include_lower_bound_with_lower() -> None:
    with patched_versions():
        assert fetch_latest_versions(
            "my_package", group="minor", lower="1.0.1", include_lower_bound=True
        ) == ("1.0.1", "1.1.2", "2.0.3")


def test_fetch_latest_versions_include_lower_bound_without_lower_has_no_effect() -> None:
    # Regression test: the docstring says that include_lower_bound has no effect when
    # lower is None, but the first version used to be added.
    with patched_versions():
        assert fetch_latest_versions("my_package", group="major", include_lower_bound=True) == (
            "1.1.2",
            "2.0.3",
        )


def test_fetch_latest_versions_minor_include_lower_bound_without_lower_has_no_effect() -> None:
    with patched_versions():
        assert fetch_latest_versions("my_package", group="minor", include_lower_bound=True) == (
            "1.0.1",
            "1.1.2",
            "2.0.3",
        )


def test_fetch_latest_versions_include_lower_bound_no_duplicate() -> None:
    # 1.1.0 is both the lower bound and the latest patch for major 1: it must appear once.
    with patched_versions(("1.1.0", "2.0.0", "2.0.3")):
        assert fetch_latest_versions(
            "my_package", group="major", lower="1.1.0", include_lower_bound=True
        ) == ("1.1.0", "2.0.3")


def test_fetch_latest_versions_include_lower_bound_empty_range() -> None:
    with patched_versions(()):
        assert (
            fetch_latest_versions(
                "my_package", group="major", lower="9.0.0", include_lower_bound=True
            )
            == ()
        )


def test_fetch_latest_versions_sorted_by_pep440() -> None:
    with patched_versions(("1.9.0", "1.10.0", "1.2.0")):
        assert fetch_latest_versions("my_package", group="minor") == ("1.2.0", "1.9.0", "1.10.0")


def test_fetch_latest_versions_is_a_tuple() -> None:
    with patched_versions():
        assert isinstance(fetch_latest_versions("my_package", group="major"), tuple)


##########################################
#     Tests for fetch_latest_version     #
##########################################


def test_fetch_latest_version() -> None:
    with patched_versions((*VERSIONS, "3.0.0rc1")):
        assert fetch_latest_version("my_package") == "3.0.0rc1"


def test_fetch_latest_version_ignores_invalid_versions() -> None:
    with patched_versions(("1.0.0", "not-a-version")):
        assert fetch_latest_version("my_package") == "1.0.0"


def test_fetch_latest_version_no_version() -> None:
    with patched_versions(()), pytest.raises(ValueError, match="versions list must not be empty"):
        fetch_latest_version("my_package")


###################################################
#     Tests for fetch_latest_stable_version       #
###################################################


def test_fetch_latest_stable_version() -> None:
    with patched_versions((*VERSIONS, "3.0.0rc1")):
        assert fetch_latest_stable_version("my_package") == "2.0.3"


def test_fetch_latest_stable_version_no_stable_version() -> None:
    with (
        patched_versions(("1.0.0rc1",)),
        pytest.raises(ValueError, match="versions list must not be empty"),
    ):
        fetch_latest_stable_version("my_package")


###########################################################
#     Tests for fetch_latest_{major,minor}_versions_map   #
###########################################################


def test_fetch_latest_major_versions_map() -> None:
    with patched_versions():
        assert fetch_latest_major_versions_map(
            [make_bounds("a"), make_bounds("b", lower="1.1.0")]
        ) == {
            "a": ["1.1.2", "2.0.3"],
            "b": ["1.1.2", "2.0.3"],
        }


def test_fetch_latest_major_versions_map_include_lower_bound() -> None:
    with patched_versions():
        assert fetch_latest_major_versions_map(
            [make_bounds("a", lower="1.1.0"), make_bounds("b")], include_lower_bound=True
        ) == {"a": ["1.1.0", "1.1.2", "2.0.3"], "b": ["1.1.2", "2.0.3"]}


def test_fetch_latest_minor_versions_map() -> None:
    with patched_versions():
        assert fetch_latest_minor_versions_map([make_bounds("a")]) == {
            "a": ["1.0.1", "1.1.2", "2.0.3"]
        }


def test_fetch_latest_minor_versions_map_include_lower_bound() -> None:
    with patched_versions():
        assert fetch_latest_minor_versions_map(
            [make_bounds("a", lower="1.0.1"), make_bounds("b")], include_lower_bound=True
        ) == {"a": ["1.0.1", "1.1.2", "2.0.3"], "b": ["1.0.1", "1.1.2", "2.0.3"]}


def test_fetch_latest_versions_map_last_entry_wins() -> None:
    with patched_versions():
        assert fetch_latest_minor_versions_map(
            [make_bounds("a", lower="1.1.0"), make_bounds("a", lower="2.0.0")]
        ) == {"a": ["2.0.3"]}


def test_fetch_latest_versions_map_empty() -> None:
    assert fetch_latest_major_versions_map([]) == {}


def test_fetch_latest_major_versions_map_include_lower_bound_is_keyword_only() -> None:
    with pytest.raises(TypeError, match="positional argument"):
        fetch_latest_major_versions_map([], True)  # ty: ignore[too-many-positional-arguments]


############################################
#     Tests for fetch_package_versions     #
############################################

PYPROJECT = """\
[project]
name = "demo"
dependencies = ["Packaging>=1.0.0", "numpy>=1.1.0,<3"]

[project.optional-dependencies]
dev = ["scikit_learn>=1.0.1"]

[dependency-groups]
test = ["pytest>=7"]
"""


@pytest.fixture
def pyproject(tmp_path: Path) -> Path:
    path = tmp_path / "pyproject.toml"
    path.write_text(PYPROJECT)
    return path


def test_fetch_package_versions_whole_output(pyproject: Path) -> None:
    with patched_versions():
        assert fetch_package_versions(pyproject) == {
            "numpy": ["1.1.0", "1.1.2", "2.0.3"],
            "packaging": ["1.0.0", "1.1.2", "2.0.3"],
            "scikit-learn": ["1.0.1", "1.1.2", "2.0.3"],
        }


def test_fetch_package_versions_packaging_uses_the_major_versions(pyproject: Path) -> None:
    with patched_versions():
        assert fetch_package_versions(pyproject)["packaging"] == ["1.0.0", "1.1.2", "2.0.3"]


def test_fetch_package_versions_other_packages_use_the_minor_versions(pyproject: Path) -> None:
    with patched_versions():
        assert fetch_package_versions(pyproject)["numpy"] == ["1.1.0", "1.1.2", "2.0.3"]


def test_fetch_package_versions_names_are_canonical_and_sorted(pyproject: Path) -> None:
    with patched_versions():
        assert list(fetch_package_versions(pyproject)) == ["numpy", "packaging", "scikit-learn"]


def test_fetch_package_versions_ignores_dependency_groups(pyproject: Path) -> None:
    with patched_versions():
        assert "pytest" not in fetch_package_versions(pyproject)


def test_fetch_package_versions_include_lower_bound_false(pyproject: Path) -> None:
    with patched_versions():
        assert fetch_package_versions(pyproject, include_lower_bound=False)["numpy"] == [
            "1.1.2",
            "2.0.3",
        ]


def test_fetch_package_versions_major_only(pyproject: Path) -> None:
    with patched_versions():
        assert fetch_package_versions(pyproject, major_only=("NumPy",))["numpy"] == [
            "1.1.0",
            "1.1.2",
            "2.0.3",
        ]


def test_fetch_package_versions_major_only_empty(pyproject: Path) -> None:
    with patched_versions():
        assert fetch_package_versions(pyproject, major_only=())["packaging"] == [
            "1.0.0",
            "1.0.1",
            "1.1.2",
            "2.0.3",
        ]


def test_fetch_package_versions_accepts_a_string_path(pyproject: Path) -> None:
    with patched_versions():
        assert "numpy" in fetch_package_versions(str(pyproject))


def test_fetch_package_versions_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match=r"pyproject\.toml"):
        fetch_package_versions(tmp_path / "pyproject.toml")
