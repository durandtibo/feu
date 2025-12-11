from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

import pytest

from feu.git import get_last_tag_name, get_last_version_tag_name, get_tags
from feu.imports import is_git_available
from feu.testing import git_available

if is_git_available():
    import git


##############################
#     Tests for get_tags     #
##############################


def create_repo_mock() -> Mock:
    tz = timezone(timedelta(hours=0))  # UTC+2
    dt = datetime(year=2025, month=5, day=17, hour=14, minute=30, second=0, tzinfo=tz)

    tag1 = Mock(
        spec=git.TagReference,
        commit=Mock(committed_datetime=dt - timedelta(hours=1)),
    )
    tag1.configure_mock(name="v1")

    tag2 = Mock(spec=git.TagReference, commit=Mock(committed_datetime=dt))
    tag2.configure_mock(name="v2")

    return Mock(tags=[tag2, tag1])


@git_available
def test_get_tags_sorted() -> None:
    with patch("feu.git.Repo", Mock(return_value=create_repo_mock())):
        result = get_tags()
    assert [t.name for t in result] == ["v1", "v2"]


@git_available
def test_get_tags_empty() -> None:
    with patch("feu.git.Repo", Mock(return_value=Mock(tags=[]))):
        result = get_tags()
    assert result == []


@patch("feu.imports.is_git_available", lambda: False)
def test_get_tags_no_git() -> None:
    with pytest.raises(RuntimeError, match=r"'git' package is required but not installed."):
        get_tags()


#######################################
#     Tests for get_last_tag_name     #
#######################################


@git_available
def test_get_last_tag_name() -> None:
    m1 = Mock()
    m1.configure_mock(name="v1.0.0")
    m2 = Mock()
    m2.configure_mock(name="v1.1.0")
    m3 = Mock()
    m3.configure_mock(name="v2.0.0")
    with patch("feu.git.get_tags", lambda: [m1, m2, m3]):
        assert get_last_tag_name() == "v2.0.0"


@git_available
def test_get_last_tag_name_empty() -> None:
    with (
        patch("feu.git.get_tags", list),
        pytest.raises(RuntimeError, match=r"No tag was found"),
    ):
        get_last_tag_name()


@patch("feu.imports.is_git_available", lambda: False)
def test_get_last_tag_name_no_git() -> None:
    with pytest.raises(RuntimeError, match=r"'git' package is required but not installed."):
        get_last_tag_name()


###############################################
#     Tests for get_last_version_tag_name     #
###############################################


@git_available
def test_get_last_version_tag_name() -> None:
    m1 = Mock()
    m1.configure_mock(name="v1.0.0")
    m2 = Mock()
    m2.configure_mock(name="v1.1.0")
    m3 = Mock()
    m3.configure_mock(name="v2.0.0")
    with patch("feu.git.get_tags", lambda: [m1, m2, m3]):
        assert get_last_version_tag_name() == "v2.0.0"


@git_available
def test_get_last_version_tag_name_mock_ignore_other_tag() -> None:
    m1 = Mock()
    m1.configure_mock(name="v1.0.0")
    m2 = Mock()
    m2.configure_mock(name="v1.1.0")
    m3 = Mock()
    m3.configure_mock(name="v2.0.0")
    m4 = Mock()
    m4.configure_mock(name="my_tag")
    with patch("feu.git.get_tags", lambda: [m1, m2, m3, m4]):
        assert get_last_version_tag_name() == "v2.0.0"


@git_available
def test_get_last_version_tag_name_empty() -> None:
    with (
        patch("feu.git.get_tags", list),
        pytest.raises(RuntimeError, match=r"No tag was found"),
    ):
        get_last_version_tag_name()


@patch("feu.imports.is_git_available", lambda: False)
def test_get_last_version_tag_name_no_git() -> None:
    with pytest.raises(RuntimeError, match=r"'git' package is required but not installed."):
        get_last_version_tag_name()
