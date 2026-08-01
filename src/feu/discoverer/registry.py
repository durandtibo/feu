r"""Define the compatibility discoverer registry."""

from __future__ import annotations

__all__ = ["CompatDiscovererRegistry"]

from typing import TYPE_CHECKING

from feu.discoverer.default import CompatDiscoverer

if TYPE_CHECKING:
    from collections.abc import Mapping

    from feu.discoverer.base import BaseCompatDiscoverer


class CompatDiscovererRegistry:
    r"""Implement a registry that manages and dispatches compatibility
    discoverers based on package name.

    Args:
        initial_state: Optional initial mapping of package name to
            discoverer. If provided, the state is copied to prevent
            external mutations.

    Example:
        ```pycon
        >>> from feu.compat.discoverer import CompatDiscovererRegistry, CompatDiscoverer
        >>> registry = CompatDiscovererRegistry()
        >>> registry.register("my_package", CompatDiscoverer())
        >>> registry.has_discoverer("my_package")
        True

        ```
    """

    def __init__(self, initial_state: dict[str, BaseCompatDiscoverer] | None = None) -> None:
        self._state: dict[str, BaseCompatDiscoverer] = dict(initial_state or {})

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(\n  (state): {self._state}\n)"

    def register(
        self, pkg_name: str, discoverer: BaseCompatDiscoverer, exist_ok: bool = False
    ) -> None:
        r"""Register a compatibility discoverer for a given package.

        Args:
            pkg_name: The package name.
            discoverer: The discoverer used for the given package.
            exist_ok: If ``False``, ``RuntimeError`` is raised if the
                package already exists. This parameter should be set
                to ``True`` to overwrite the discoverer for a package.

        Raises:
            RuntimeError: if a discoverer is already registered for the
                package name and ``exist_ok=False``.

        Example:
            ```pycon
            >>> from feu.compat.discoverer import CompatDiscovererRegistry, CompatDiscoverer
            >>> registry = CompatDiscovererRegistry()
            >>> registry.register("my_package", CompatDiscoverer())
            >>> registry.has_discoverer("my_package")
            True

            ```
        """
        if pkg_name in self._state and not exist_ok:
            msg = (
                f"A compatibility discoverer is already registered for the package "
                f"{pkg_name!r}. Please use `exist_ok=True` if you want to overwrite the "
                "discoverer for this package"
            )
            raise RuntimeError(msg)
        self._state[pkg_name] = discoverer

    def register_many(
        self, mapping: Mapping[str, BaseCompatDiscoverer], exist_ok: bool = False
    ) -> None:
        r"""Register multiple compatibility discoverers at once.

        Args:
            mapping: Mapping of package name to discoverer.
            exist_ok: If ``False``, ``RuntimeError`` is raised if any
                package already exists. This parameter should be set
                to ``True`` to overwrite the discoverer for a package.

        Raises:
            RuntimeError: if a discoverer is already registered for any
                of the package names and ``exist_ok=False``.

        Example:
            ```pycon
            >>> from feu.compat.discoverer import CompatDiscovererRegistry, CompatDiscoverer
            >>> registry = CompatDiscovererRegistry()
            >>> registry.register_many({"my_package": CompatDiscoverer()})
            >>> registry.has_discoverer("my_package")
            True

            ```
        """
        for pkg_name, discoverer in mapping.items():
            self.register(pkg_name, discoverer, exist_ok=exist_ok)

    def has_discoverer(self, pkg_name: str) -> bool:
        r"""Indicate if a compatibility discoverer is registered for the
        given package name.

        Args:
            pkg_name: The package name.

        Returns:
            ``True`` if a discoverer is registered, otherwise
                ``False``.

        Example:
            ```pycon
            >>> from feu.compat.discoverer import CompatDiscovererRegistry
            >>> registry = CompatDiscovererRegistry()
            >>> registry.has_discoverer("pydantic")
            False

            ```
        """
        return pkg_name in self._state

    def find_discoverer(self, pkg_name: str) -> BaseCompatDiscoverer:
        r"""Find the relevant compatibility discoverer for the given
        package.

        Args:
            pkg_name: The package name.

        Returns:
            The compatibility discoverer for the package, or a
                ``CompatDiscoverer`` if none is registered.

        Example:
            ```pycon
            >>> from feu.compat.discoverer import CompatDiscovererRegistry
            >>> registry = CompatDiscovererRegistry()
            >>> discoverer = registry.find_discoverer("pydantic")
            >>> discoverer
            CompatDiscoverer()

            ```
        """
        return self._state.get(pkg_name, CompatDiscoverer())
