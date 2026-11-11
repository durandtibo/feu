r"""Define the pip compatible installers."""

from __future__ import annotations

__all__ = ["BasePipInstaller", "PipInstaller", "UvInstaller"]

import sys
from abc import abstractmethod
from importlib.util import find_spec
from shutil import which
from typing import TYPE_CHECKING, Any

from feu.install.installer import BaseInstaller
from feu.install.pip.resolver import (
    DependencyResolverRegistry,
)
from feu.utils.command import run_command
from feu.utils.installer import normalize_arguments

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Self

    from feu.utils.package import PackageDependency, PackageSpec


class BasePipInstaller(BaseInstaller):
    r"""Define an intermediate base class to implement pip compatible
    package installer.

    The command is an argument vector (a list of strings), which is run
    without a shell.

    Args:
        arguments: Optional arguments to pass to the package installer.
            The valid arguments depend on the package installer. A
            string is split once with ``shlex.split``; a list or a
            tuple of strings is used as is.

    Raises:
        TypeError: If ``arguments`` is neither a string nor a list or
            tuple of strings.

    Example:
        ```pycon
        >>> from feu.install.pip.installer import BasePipInstaller
        >>> from feu.utils.package import PackageSpec, PackageDependency
        >>> class MyInstaller(BasePipInstaller):
        ...     def _generate_command(self, deps, args):
        ...         return ["echo", "Installing", *map(str, deps), *args]
        ...
        >>> installer = MyInstaller(arguments="--verbose")
        >>> installer
        MyInstaller(arguments=('--verbose',))
        >>> installer.install(PackageSpec(name="pandas", version="2.2.2"))  # doctest: +SKIP

        ```
    """

    def __init__(self, arguments: str | Sequence[str] = ()) -> None:
        self._arguments = normalize_arguments(arguments)

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(arguments={self._arguments!r})"

    def equal(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._arguments == other._arguments

    def install(self, package: PackageSpec) -> None:
        self._check_available()
        deps = DependencyResolverRegistry.find_resolver(package).resolve(package)
        run_command(self._generate_command(deps=deps, args=self._arguments))

    @classmethod
    def instantiate_with_arguments(cls, arguments: str | Sequence[str]) -> Self:
        return cls(arguments=arguments)

    def _check_available(self) -> None:
        r"""Check that the tool used to install packages is available.

        The default implementation does nothing.

        Raises:
            RuntimeError: If the tool is not available.
        """

    @abstractmethod
    def _generate_command(
        self, deps: Sequence[PackageDependency], args: tuple[str, ...]
    ) -> list[str]:
        r"""Generate the command to run to install the dependencies.

        Args:
            deps: The dependencies to install.
            args: Arguments to pass to the package installer.
                The valid arguments depend on the package installer.

        Returns:
            The command to run to install the dependencies, as an
                argument vector.
        """


class PipInstaller(BasePipInstaller):
    r"""Implement a pip package installer.

    The package dependencies are resolved first, and then installed
    with a single ``python -m pip install`` command, where ``python``
    is the interpreter that runs ``feu`` (``sys.executable``). The
    packages are therefore installed in the environment that is
    checked by the compatibility functions, and not in the one of the
    first ``pip`` found on the ``PATH``.

    Args:
        arguments: Optional arguments to pass to ``pip install``,
            e.g. ``"--upgrade"``. A string is split once with
            ``shlex.split``; a list or a tuple of strings is used as
            is.

    Raises:
        RuntimeError: When installing, if ``pip`` is not available in
            the interpreter that runs ``feu``.

    Example:
        ```pycon
        >>> from feu.install.pip import PipInstaller
        >>> from feu.utils.package import PackageSpec
        >>> installer = PipInstaller()
        >>> installer
        PipInstaller(arguments=())
        >>> installer.install(PackageSpec(name="pandas", version="2.2.2"))  # doctest: +SKIP

        ```
    """

    def _check_available(self) -> None:
        if find_spec("pip") is None:
            msg = (
                f"pip is not available in the interpreter {sys.executable!r}: "
                "run `python -m ensurepip` to install it, or use the 'uv' installer"
            )
            raise RuntimeError(msg)

    def _generate_command(
        self, deps: Sequence[PackageDependency], args: tuple[str, ...]
    ) -> list[str]:
        return [sys.executable, "-m", "pip", "install", *args, *map(str, deps)]


class UvInstaller(BasePipInstaller):
    r"""Implement a uv package installer.

    The package dependencies are resolved first, and then installed
    with a single ``uv pip install --python <sys.executable>`` command,
    so the packages are installed in the interpreter that runs ``feu``.

    Args:
        arguments: Optional arguments to pass to ``uv pip install``,
            e.g. ``"--upgrade"``. A string is split once with
            ``shlex.split``; a list or a tuple of strings is used as
            is.

    Raises:
        RuntimeError: When installing, if ``uv`` is not found on the
            ``PATH``.

    Example:
        ```pycon
        >>> from feu.install.pip import UvInstaller
        >>> from feu.utils.package import PackageSpec
        >>> installer = UvInstaller()
        >>> installer
        UvInstaller(arguments=())
        >>> installer.install(PackageSpec(name="pandas", version="2.2.2"))  # doctest: +SKIP

        ```
    """

    def _check_available(self) -> None:
        if which("uv") is None:
            msg = "uv is not found on the PATH: install it with `pip install uv`"
            raise RuntimeError(msg)

    def _generate_command(
        self, deps: Sequence[PackageDependency], args: tuple[str, ...]
    ) -> list[str]:
        return ["uv", "pip", "install", "--python", sys.executable, *args, *map(str, deps)]
