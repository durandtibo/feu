r"""Contain a generic registry to register and look up values by name."""

from __future__ import annotations

__all__ = ["Registry"]

from typing import TYPE_CHECKING, Generic, TypeVar, overload

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator, Mapping

T = TypeVar("T")
D = TypeVar("D")


class Registry(Generic[T]):
    r"""Register values and look them up by key.

    This is the only implementation of "register and look up by name"
    of ``feu``: the installer registry and the dependency resolver
    registry are instances of it.

    Args:
        kind: What the registry holds, e.g. ``"installer"``. It is used
            in the error messages.
        normalize: A function applied to every key before it is stored
            or looked up, e.g. ``packaging.utils.canonicalize_name``
            or ``str.lower``. ``None`` means the key is used as is.

    Example:
        ```pycon
        >>> from feu.utils.registry import Registry
        >>> registry = Registry[int]("number", normalize=str.lower)
        >>> registry.register("One", 1)
        >>> registry.find("ONE")
        1
        >>> "one" in registry
        True
        >>> registry.keys()
        ['one']

        ```
    """

    def __init__(self, kind: str, normalize: Callable[[str], str] | None = None) -> None:
        self._kind = kind
        self._normalize = normalize
        self._values: dict[str, T] = {}

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(kind={self._kind!r}, keys={self.keys()})"

    def __contains__(self, key: object) -> bool:
        return isinstance(key, str) and self._key(key) in self._values

    def __len__(self) -> int:
        return len(self._values)

    def __iter__(self) -> Iterator[str]:
        return iter(sorted(self._values))

    def _key(self, key: str) -> str:
        r"""Normalize a key.

        Args:
            key: The key.

        Returns:
            The normalized key.
        """
        return key if self._normalize is None else self._normalize(key)

    def register(self, key: str, value: T, *, exist_ok: bool = False) -> None:
        r"""Register a value for a key.

        Args:
            key: The key, e.g. an installer name or a package name.
            value: The value to register.
            exist_ok: If ``False``, a ``RuntimeError`` is raised when a
                value is already registered for the key. Set to
                ``True`` to overwrite.

        Raises:
            RuntimeError: If a value is already registered for the key
                and ``exist_ok`` is ``False``.

        Example:
            ```pycon
            >>> from feu.utils.registry import Registry
            >>> registry = Registry[int]("number")
            >>> registry.register("one", 1)
            >>> registry.register("one", 11, exist_ok=True)
            >>> registry.find("one")
            11

            ```
        """
        name = self._key(key)
        if name in self._values and not exist_ok:
            msg = (
                f"A {self._kind} ({self._values[name]!r}) is already registered for the key "
                f"{name!r}. Please use `exist_ok=True` if you want to overwrite the {self._kind}"
            )
            raise RuntimeError(msg)
        self._values[name] = value

    def register_many(self, mapping: Mapping[str, T], *, exist_ok: bool = False) -> None:
        r"""Register several values.

        The values are registered one after the other, so the values
        before a conflict stay registered.

        Args:
            mapping: The mapping of key to value.
            exist_ok: Forwarded to ``register``.

        Raises:
            RuntimeError: If a value is already registered for a key
                and ``exist_ok`` is ``False``.

        Example:
            ```pycon
            >>> from feu.utils.registry import Registry
            >>> registry = Registry[int]("number")
            >>> registry.register_many({"one": 1, "two": 2})
            >>> registry.keys()
            ['one', 'two']

            ```
        """
        for key, value in mapping.items():
            self.register(key, value, exist_ok=exist_ok)

    def find(self, key: str) -> T:
        r"""Find the value registered for a key.

        Args:
            key: The key.

        Returns:
            The registered value.

        Raises:
            KeyError: If no value is registered for the key. The
                message lists the known keys.

        Example:
            ```pycon
            >>> from feu.utils.registry import Registry
            >>> registry = Registry[int]("number")
            >>> registry.register("one", 1)
            >>> registry.find("one")
            1

            ```
        """
        name = self._key(key)
        if name not in self._values:
            msg = f"No {self._kind} is registered for the key {name!r}. Known keys: {self.keys()}"
            raise KeyError(msg)
        return self._values[name]

    @overload
    def get(self, key: str) -> T | None: ...

    @overload
    def get(self, key: str, default: D) -> T | D: ...

    def get(self, key: str, default: D | None = None) -> T | D | None:
        r"""Get the value registered for a key, or a default.

        Args:
            key: The key.
            default: The value returned if no value is registered for
                the key.

        Returns:
            The registered value, or ``default``.

        Example:
            ```pycon
            >>> from feu.utils.registry import Registry
            >>> registry = Registry[int]("number")
            >>> registry.get("one", 0)
            0

            ```
        """
        return self._values.get(self._key(key), default)

    def keys(self) -> list[str]:
        r"""Get the registered keys.

        Returns:
            The normalized keys, sorted.

        Example:
            ```pycon
            >>> from feu.utils.registry import Registry
            >>> registry = Registry[int]("number")
            >>> registry.register_many({"two": 2, "one": 1})
            >>> registry.keys()
            ['one', 'two']

            ```
        """
        return sorted(self._values)
