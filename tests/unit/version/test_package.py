from __future__ import annotations

from typing import Any
from unittest.mock import Mock, patch

from feu.version import (
    PackageBounds,
    fetch_latest_major_versions,
    fetch_latest_minor_versions,
    fetch_latest_minor_versions_map,
    fetch_latest_stable_version,
    fetch_latest_version,
    fetch_versions, fetch_latest_major_versions_map,
)

MODULE = f"{MODULE}.package"


def make_bounds(name: str, lower: str | None = None, upper: str | None = None) -> PackageBounds:
    """Convenience factory to create PackageBounds without specifying
    section."""
    return PackageBounds(name=name, lower=lower, upper=upper, section="project.dependencies")


####################################
#     Tests for fetch_versions     #
####################################


def test_fetch_versions() -> None:
    mock = Mock(return_value=("1.0.0", "1.0.1", "1.1.0", "1.1.2", "2.0.0", "2.0.3"))
    with patch(f"{MODULE}.fetch_pypi_versions", mock):
        assert fetch_versions("my_package") == (
            "1.0.0",
            "1.0.1",
            "1.1.0",
            "1.1.2",
            "2.0.0",
            "2.0.3",
        )


def test_fetch_versions_lower() -> None:
    mock = Mock(return_value=("1.0.0", "1.0.1", "1.1.0", "1.1.2", "2.0.0", "2.0.3"))
    with patch(f"{MODULE}.fetch_pypi_versions", mock):
        assert fetch_versions("my_package", lower="1.1.0") == ("1.1.0", "1.1.2", "2.0.0", "2.0.3")


def test_fetch_versions_upper() -> None:
    mock = Mock(return_value=("1.0.0", "1.0.1", "1.1.0", "1.1.2", "2.0.0", "2.0.3"))
    with patch(f"{MODULE}.fetch_pypi_versions", mock):
        assert fetch_versions("my_package", upper="2.0.0") == ("1.0.0", "1.0.1", "1.1.0", "1.1.2")


def test_fetch_versions_range() -> None:
    mock = Mock(return_value=("1.0.0", "1.0.1", "1.1.0", "1.1.2", "2.0.0", "2.0.3"))
    with patch(f"{MODULE}.fetch_pypi_versions", mock):
        assert fetch_versions("my_package", lower="1.1.0", upper="2.0.0") == ("1.1.0", "1.1.2")


#################################################
#     Tests for fetch_latest_major_versions     #
#################################################


def test_fetch_latest_major_versions() -> None:
    mock = Mock(return_value=("0.1.0", "0.8.0", "0.9.0", "1.0.0", "1.2.0", "1.3.0", "2.0.0"))
    with patch(f"{MODULE}.fetch_pypi_versions", mock):
        assert fetch_latest_major_versions("my_package") == ("0.9.0", "1.3.0", "2.0.0")


def test_fetch_latest_major_versions_lower() -> None:
    mock = Mock(return_value=("0.1.0", "0.8.0", "0.9.0", "1.0.0", "1.2.0", "1.3.0", "2.0.0"))
    with patch(f"{MODULE}.fetch_pypi_versions", mock):
        assert fetch_latest_major_versions("my_package", lower="1.0.0") == ("1.3.0", "2.0.0")


def test_fetch_latest_major_versions_upper() -> None:
    mock = Mock(return_value=("0.1.0", "0.8.0", "0.9.0", "1.0.0", "1.2.0", "1.3.0", "2.0.0"))
    with patch(f"{MODULE}.fetch_pypi_versions", mock):
        assert fetch_latest_major_versions("my_package", upper="2.0.0") == ("0.9.0", "1.3.0")


def test_fetch_latest_major_versions_range() -> None:
    mock = Mock(return_value=("0.1.0", "0.8.0", "0.9.0", "1.0.0", "1.2.0", "1.3.0", "2.0.0"))
    with patch(f"{MODULE}.fetch_pypi_versions", mock):
        assert fetch_latest_major_versions("my_package", lower="1.0.0", upper="2.0.0") == ("1.3.0",)


#################################################
#     Tests for fetch_latest_minor_versions     #
#################################################


def test_fetch_latest_minor_versions() -> None:
    mock = Mock(return_value=("1.0.0", "1.0.1", "1.1.0", "1.1.2", "2.0.0", "2.0.3"))
    with patch(f"{MODULE}.fetch_pypi_versions", mock):
        assert fetch_latest_minor_versions("my_package") == ("1.0.1", "1.1.2", "2.0.3")


def test_fetch_latest_minor_versions_lower() -> None:
    mock = Mock(return_value=("1.0.0", "1.0.1", "1.1.0", "1.1.2", "2.0.0", "2.0.3"))
    with patch(f"{MODULE}.fetch_pypi_versions", mock):
        assert fetch_latest_minor_versions("my_package", lower="1.1.0") == ("1.1.2", "2.0.3")


def test_fetch_latest_minor_versions_upper() -> None:
    mock = Mock(return_value=("1.0.0", "1.0.1", "1.1.0", "1.1.2", "2.0.0", "2.0.3"))
    with patch(f"{MODULE}.fetch_pypi_versions", mock):
        assert fetch_latest_minor_versions("my_package", upper="2.0.0") == ("1.0.1", "1.1.2")


def test_fetch_latest_minor_versions_range() -> None:
    mock = Mock(return_value=("1.0.0", "1.0.1", "1.1.0", "1.1.2", "2.0.0", "2.0.3"))
    with patch(f"{MODULE}.fetch_pypi_versions", mock):
        assert fetch_latest_minor_versions("my_package", lower="1.1.0", upper="2.0.0") == ("1.1.2",)


##########################################
#     Tests for fetch_latest_version     #
##########################################


def test_fetch_latest_version() -> None:
    mock = Mock(return_value=("1.0.0", "1.0.1", "1.1.0", "1.1.2", "2.0.0", "2.0.3"))
    with patch(f"{MODULE}.fetch_pypi_versions", mock):
        assert fetch_latest_version("my_package") == "2.0.3"


def test_fetch_latest_version_random() -> None:
    mock = Mock(return_value=("3.1.0", "2.0.1", "2.1.0", "1.1.2", "2.0.0", "2.0.3"))
    with patch(f"{MODULE}.fetch_pypi_versions", mock):
        assert fetch_latest_version("my_package") == "3.1.0"


#################################################
#     Tests for fetch_latest_stable_version     #
#################################################


def test_fetch_latest_stable_version() -> None:
    mock = Mock(return_value=("1.0.0", "1.0.0a1", "2.0.0", "2.0.0.dev1", "3.0.0.post1"))
    with patch(f"{MODULE}.fetch_pypi_versions", mock):
        assert fetch_latest_stable_version("my_package") == "2.0.0"


def test_fetch_latest_stable_version_random() -> None:
    mock = Mock(return_value=("2.1.0", "1.0.0a1", "2.0.0", "2.0.0.dev1", "3.0.0.post1"))
    with patch(f"{MODULE}.fetch_pypi_versions", mock):
        assert fetch_latest_stable_version("my_package") == "2.1.0"


##################################################
#     Tests for fetch_latest_minor_versions_map  #
##################################################


def test_fetch_latest_minor_versions_map_empty_sequence() -> None:
    assert fetch_latest_minor_versions_map([]) == {}


def test_fetch_latest_minor_versions_map_single_package() -> None:
    with patch(
        f"{MODULE}.fetch_latest_minor_versions", return_value=iter(["1.21.6", "1.22.4"])
    ) as mock:
        result = fetch_latest_minor_versions_map([make_bounds("numpy", lower="1.21")])
    mock.assert_called_once_with("numpy", lower="1.21")
    assert result == {"numpy": ["1.21.6", "1.22.4"]}


def test_fetch_latest_minor_versions_map_multiple_packages() -> None:
    def side_effect(name: str, lower: str | None) -> Any:  # noqa: ARG001
        return iter({"numpy": ["1.21.6", "1.22.4"], "torch": ["2.0.1", "2.1.0"]}[name])

    with patch(f"{MODULE}.fetch_latest_minor_versions", side_effect=side_effect):
        result = fetch_latest_minor_versions_map(
            [
                make_bounds("numpy", lower="1.21"),
                make_bounds("torch", lower="2.0"),
            ]
        )

    assert result == {
        "numpy": ["1.21.6", "1.22.4"],
        "torch": ["2.0.1", "2.1.0"],
    }


def test_fetch_latest_minor_versions_map_passes_lower_bound() -> None:
    with patch(f"{MODULE}.fetch_latest_minor_versions", return_value=iter([])) as mock:
        fetch_latest_minor_versions_map([make_bounds("numpy", lower="1.24")])
    mock.assert_called_once_with("numpy", lower="1.24")


def test_fetch_latest_minor_versions_map_passes_none_lower_bound() -> None:
    with patch(f"{MODULE}.fetch_latest_minor_versions", return_value=iter([])) as mock:
        fetch_latest_minor_versions_map([make_bounds("numpy", lower=None)])
    mock.assert_called_once_with("numpy", lower=None)


def test_fetch_latest_minor_versions_map_upper_bound_is_ignored() -> None:
    # upper is present in PackageBounds but not passed to fetch_latest_minor_versions.
    with patch(f"{MODULE}.fetch_latest_minor_versions", return_value=iter(["1.21.6"])) as mock:
        fetch_latest_minor_versions_map([make_bounds("numpy", lower="1.21", upper="2.0")])
    mock.assert_called_once_with("numpy", lower="1.21")


def test_fetch_latest_minor_versions_map_returns_list_not_iterator() -> None:
    with patch(f"{MODULE}.fetch_latest_minor_versions", return_value=iter(["1.21.6"])):
        result = fetch_latest_minor_versions_map([make_bounds("numpy", lower="1.21")])
    assert isinstance(result["numpy"], list)


def test_fetch_latest_minor_versions_map_empty_versions() -> None:
    with patch(f"{MODULE}.fetch_latest_minor_versions", return_value=iter([])):
        result = fetch_latest_minor_versions_map([make_bounds("numpy", lower="99.0")])
    assert result == {"numpy": []}


def test_fetch_latest_minor_versions_map_duplicate_package_last_wins() -> None:
    # If the same package name appears twice, the last entry overwrites the first.
    calls: list[tuple[str, str | None]] = []

    def side_effect(name: str, lower: str | None) -> Any:
        calls.append((name, lower))
        return iter(["1.21.6"] if lower == "1.21" else ["1.24.0"])

    with patch(f"{MODULE}.fetch_latest_minor_versions", side_effect=side_effect):
        result = fetch_latest_minor_versions_map(
            [
                make_bounds("numpy", lower="1.21"),
                make_bounds("numpy", lower="1.24"),
            ]
        )

    assert result == {"numpy": ["1.24.0"]}
    assert calls == [("numpy", "1.21"), ("numpy", "1.24")]


def test_fetch_latest_minor_versions_map_preserves_package_names() -> None:
    with patch(f"{MODULE}.fetch_latest_minor_versions", return_value=iter(["1.0", "2.0"])):
        result = fetch_latest_minor_versions_map(
            [
                make_bounds("scikit-learn", lower="1.0"),
            ]
        )
    assert "scikit-learn" in result


##################################################
#     Tests for fetch_latest_major_versions_map  #
##################################################


def test_fetch_latest_major_versions_map_empty_sequence() -> None:
    assert fetch_latest_major_versions_map([]) == {}


def test_fetch_latest_major_versions_map_single_package() -> None:
    with patch(f"{MODULE}.fetch_latest_major_versions",
               return_value=iter(["1.21.6", "1.22.4"])) as mock:
        result = fetch_latest_major_versions_map([make_bounds("numpy", lower="1.21")])
    mock.assert_called_once_with("numpy", lower="1.21")
    assert result == {"numpy": ["1.21.6", "1.22.4"]}


def test_fetch_latest_major_versions_map_multiple_packages() -> None:
    def side_effect(name: str, lower: str | None) -> Any:
        return iter({
                        "numpy": ["1.21.6", "1.22.4"],
                        "torch": ["2.0.1", "2.1.0"],
                    }[name])

    with patch(f"{MODULE}.fetch_latest_major_versions", side_effect=side_effect):
        result = fetch_latest_major_versions_map([
            make_bounds("numpy", lower="1.21"),
            make_bounds("torch", lower="2.0"),
        ])

    assert result == {
        "numpy": ["1.21.6", "1.22.4"],
        "torch": ["2.0.1", "2.1.0"],
    }


def test_fetch_latest_major_versions_map_passes_lower_bound() -> None:
    with patch(f"{MODULE}.fetch_latest_major_versions", return_value=iter([])) as mock:
        fetch_latest_major_versions_map([make_bounds("numpy", lower="1.24")])
    mock.assert_called_once_with("numpy", lower="1.24")


def test_fetch_latest_major_versions_map_passes_none_lower_bound() -> None:
    with patch(f"{MODULE}.fetch_latest_major_versions", return_value=iter([])) as mock:
        fetch_latest_major_versions_map([make_bounds("numpy", lower=None)])
    mock.assert_called_once_with("numpy", lower=None)


def test_fetch_latest_major_versions_map_upper_bound_is_ignored() -> None:
    # upper is present in PackageBounds but not passed to fetch_latest_major_versions.
    with patch(f"{MODULE}.fetch_latest_major_versions", return_value=iter(["1.21.6"])) as mock:
        fetch_latest_major_versions_map([make_bounds("numpy", lower="1.21", upper="2.0")])
    mock.assert_called_once_with("numpy", lower="1.21")


def test_fetch_latest_major_versions_map_returns_list_not_iterator() -> None:
    with patch(f"{MODULE}.fetch_latest_major_versions", return_value=iter(["1.21.6"])):
        result = fetch_latest_major_versions_map([make_bounds("numpy", lower="1.21")])
    assert isinstance(result["numpy"], list)


def test_fetch_latest_major_versions_map_empty_versions() -> None:
    with patch(f"{MODULE}.fetch_latest_major_versions", return_value=iter([])):
        result = fetch_latest_major_versions_map([make_bounds("numpy", lower="99.0")])
    assert result == {"numpy": []}


def test_fetch_latest_major_versions_map_duplicate_package_last_wins() -> None:
    # If the same package name appears twice, the last entry overwrites the first.
    calls: list[tuple[str, str | None]] = []

    def side_effect(name: str, lower: str | None) -> Any:
        calls.append((name, lower))
        return iter(["1.21.6"] if lower == "1.21" else ["1.24.0"])

    with patch(f"{MODULE}.fetch_latest_major_versions", side_effect=side_effect):
        result = fetch_latest_major_versions_map([
            make_bounds("numpy", lower="1.21"),
            make_bounds("numpy", lower="1.24"),
        ])

    assert result == {"numpy": ["1.24.0"]}
    assert calls == [("numpy", "1.21"), ("numpy", "1.24")]


def test_fetch_latest_major_versions_map_preserves_package_names() -> None:
    with patch(f"{MODULE}.fetch_latest_major_versions", return_value=iter(["1.0", "2.0"])):
        result = fetch_latest_major_versions_map([
            make_bounds("scikit-learn", lower="1.0"),
        ])
    assert "scikit-learn" in result