from __future__ import annotations

import pytest

from feu.utils.fallback.git import Repo, TagReference


def test_repo() -> None:
    with pytest.raises(RuntimeError, match=r"'git' package is required but not installed."):
        Repo()


def test_tag_reference() -> None:
    with pytest.raises(RuntimeError, match=r"'git' package is required but not installed."):
        TagReference()
