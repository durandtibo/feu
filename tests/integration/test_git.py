from __future__ import annotations

import pytest

from feu.git import get_last_tag_name, get_last_version_tag_name, get_tags
from feu.testing import git_available, git_not_available

##############################
#     Tests for get_tags     #
##############################


@git_available
def test_get_tags() -> None:
    tags = get_tags()
    assert [t.name for t in tags[:17]] == [
        "v0.0.1",
        "v0.0.2",
        "v0.0.3",
        "v0.0.4",
        "v0.0.5",
        "v0.0.6",
        "v0.0.7",
        "v0.1.0",
        "v0.1.1",
        "v0.2.0",
        "v0.2.1",
        "v0.2.2",
        "v0.2.3",
        "v0.2.4",
        "v0.3.0",
        "v0.3.1",
        "v0.3.2",
    ]


@git_not_available
def test_get_tags_no_git() -> None:
    with pytest.raises(RuntimeError, match=r"'git' package is required but not installed."):
        get_tags()


#######################################
#     Tests for get_last_tag_name     #
#######################################


@git_available
def test_get_last_tag_name() -> None:
    assert isinstance(get_last_tag_name(), str)


@git_not_available
def test_get_last_tag_name_no_git() -> None:
    with pytest.raises(RuntimeError, match=r"'git' package is required but not installed."):
        get_last_tag_name()


###############################################
#     Tests for get_last_version_tag_name     #
###############################################


@git_available
def test_get_last_version_tag_name() -> None:
    assert isinstance(get_last_version_tag_name(), str)


@git_not_available
def test_get_last_version_tag_name_no_git() -> None:
    with pytest.raises(RuntimeError, match=r"'git' package is required but not installed."):
        get_last_version_tag_name()
