from __future__ import annotations

from unittest.mock import Mock, patch

from feu.git import get_last_tag_name, get_tags
from feu.testing import git_available

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


#######################################
#     Tests for get_last_tag_name     #
#######################################


@git_available
def test_get_last_tag_name() -> None:
    assert isinstance(get_last_tag_name(), str)


@git_available
def test_get_last_tag_name_mock() -> None:
    m1 = Mock()
    m1.configure_mock(name="v1.0.0")
    m2 = Mock()
    m2.configure_mock(name="v1.1.0")
    m3 = Mock()
    m3.configure_mock(name="v2.0.0")
    with patch("feu.git.get_tags", lambda: [m1, m2, m3]):
        assert get_last_tag_name() == "v2.0.0"
