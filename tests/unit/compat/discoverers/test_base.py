from __future__ import annotations

import pytest

from feu.compat.discoverers.base import BaseCompatDiscoverer


def instantiate(cls: type[BaseCompatDiscoverer]) -> BaseCompatDiscoverer:
    return cls()


def test_base_compat_discoverer_is_abstract() -> None:
    with pytest.raises(TypeError):
        instantiate(BaseCompatDiscoverer)


def test_base_compat_discoverer_subclass_must_implement_discover() -> None:
    class IncompleteDiscoverer(BaseCompatDiscoverer):
        pass

    with pytest.raises(TypeError):
        instantiate(IncompleteDiscoverer)


def test_base_compat_discoverer_subclass_can_be_instantiated() -> None:
    class StubDiscoverer(BaseCompatDiscoverer):
        def discover(self, pkg_name, targets) -> dict:  # noqa: ANN001, ARG002
            return {}

    discoverer = StubDiscoverer()
    assert discoverer.discover("pkg", ()) == {}
