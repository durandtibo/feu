from __future__ import annotations

import pytest

from feu.discoverer.base import BaseCompatDiscoverer


def test_base_compat_discoverer_is_abstract() -> None:
    with pytest.raises(TypeError):
        BaseCompatDiscoverer()


def test_base_compat_discoverer_subclass_must_implement_discover() -> None:
    class IncompleteDiscoverer(BaseCompatDiscoverer):
        pass

    with pytest.raises(TypeError):
        IncompleteDiscoverer()


def test_base_compat_discoverer_subclass_can_be_instantiated() -> None:
    class StubDiscoverer(BaseCompatDiscoverer):
        def discover(self, pkg_name, targets) -> dict:  # noqa: ANN001, ARG002
            return {}

    discoverer = StubDiscoverer()
    assert discoverer.discover("pkg", ()) == {}
