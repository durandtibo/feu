r"""Contain the package installers and their registry."""

from __future__ import annotations

__all__ = [
    "Installer",
    "InstallerSpec",
    "PipInstaller",
    "UvInstaller",
    "get_default_installer_registry",
    "is_pip_available",
    "is_uv_available",
    "normalize_arguments",
    "register_installer",
]

import shlex
import sys
from dataclasses import dataclass
from functools import cache
from importlib.util import find_spec
from shutil import which
from typing import TYPE_CHECKING, ClassVar

from feu.install.resolver import get_default_resolver_registry, resolve
from feu.utils.command import run_command
from feu.utils.registry import Registry

if TYPE_CHECKING:
    from collections.abc import Sequence

    from packaging.requirements import Requirement

    from feu.install.resolver import Resolver
    from feu.utils.package import PackageSpec


def normalize_arguments(arguments: str | Sequence[str]) -> tuple[str, ...]:
    r"""Normalize the arguments of an installer to a tuple of strings.

    A string is split once with ``shlex.split`` (POSIX rules, on every
    platform). A sequence of strings is converted to a tuple and is not
    split again.

    Args:
        arguments: The installer arguments, as one string e.g.
            ``"-U --pre"`` or as a sequence of arguments.

    Returns:
        The arguments as a tuple of strings.

    Raises:
        TypeError: If ``arguments`` is neither a string nor a sequence
            of strings.

    Example:
        ```pycon
        >>> from feu.install.installer import normalize_arguments
        >>> normalize_arguments("-U --pre")
        ('-U', '--pre')
        >>> normalize_arguments(["--index-url", "https://example.com/my index"])
        ('--index-url', 'https://example.com/my index')

        ```
    """
    if isinstance(arguments, str):
        return tuple(shlex.split(arguments))
    if isinstance(arguments, (list, tuple)) and all(isinstance(arg, str) for arg in arguments):
        return tuple(arguments)
    msg = (
        "installer arguments must be a string or a list/tuple of strings but received "
        f"{arguments!r}"
    )
    raise TypeError(msg)


@dataclass(frozen=True, init=False)
class InstallerSpec:
    r"""Define a dataclass to represent an installer specification.

    Args:
        name: The installer name.
        arguments: The optional installer arguments. A string is
            split once with ``shlex.split``; a list or a tuple of
            strings is used as is. The arguments are stored as a
            tuple.

    Raises:
        TypeError: If ``arguments`` is neither a string nor a list or
            tuple of strings.

    Example:
        ```pycon
        >>> from feu.install import InstallerSpec
        >>> installer1 = InstallerSpec("pip")
        >>> installer1
        InstallerSpec(name='pip', arguments=())
        >>> installer2 = InstallerSpec("pip", arguments="-U --pre")
        >>> installer2
        InstallerSpec(name='pip', arguments=('-U', '--pre'))
        >>> installer3 = InstallerSpec("pip", arguments=["-U", "--pre"])
        >>> installer3 == installer2
        True

        ```
    """

    name: str
    arguments: tuple[str, ...]

    def __init__(self, name: str, arguments: str | Sequence[str] = ()) -> None:
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "arguments", normalize_arguments(arguments))


@dataclass(frozen=True, init=False)
class Installer:
    r"""Define the base class of the package installers.

    An installer builds one command, as an argument vector, that
    installs the requirements of a package. The subclasses differ by
    their ``prefix``.

    Args:
        arguments: Optional arguments to pass to the package
            installer, after the prefix. The valid arguments depend on
            the package installer. A string is split once with
            ``shlex.split``; a list or a tuple of strings is used as
            is.

    Raises:
        TypeError: If ``arguments`` is neither a string nor a list or
            tuple of strings.

    Example:
        ```pycon
        >>> from feu.install import PipInstaller
        >>> from feu.utils.package import PackageSpec
        >>> installer = PipInstaller("-U")
        >>> installer
        PipInstaller(arguments=('-U',))
        >>> installer.install(PackageSpec(name="pandas", version="2.2.2"))  # doctest: +SKIP

        ```
    """

    arguments: tuple[str, ...]
    prefix: ClassVar[tuple[str, ...]] = ()

    def __init__(self, arguments: str | Sequence[str] = ()) -> None:
        object.__setattr__(self, "arguments", normalize_arguments(arguments))

    def command(self, requirements: Sequence[Requirement]) -> list[str]:
        r"""Build the command that installs requirements.

        Args:
            requirements: The requirements to install.

        Returns:
            The command, as an argument vector: the prefix, the
                installer arguments and the requirements.

        Example:
            ```pycon
            >>> from packaging.requirements import Requirement
            >>> from feu.install import PipInstaller
            >>> command = PipInstaller("-U").command([Requirement("numpy==2.0.0")])
            >>> command[1:]
            ['-m', 'pip', 'install', '-U', 'numpy==2.0.0']

            ```
        """
        return [*self.prefix, *self.arguments, *map(str, requirements)]

    def check_available(self) -> None:
        r"""Check that the tool used to install packages is available.

        The default implementation does nothing.

        Raises:
            RuntimeError: If the tool is not available.
        """

    def install(self, package: PackageSpec, *, resolvers: Registry[Resolver] | None = None) -> None:
        r"""Install a package and its associated requirements with a
        single command.

        Args:
            package: The package to install.
            resolvers: The dependency resolver registry. ``None``
                means the default registry.

        Raises:
            RuntimeError: If the tool used to install packages is not
                available.
            subprocess.CalledProcessError: If the installation command
                fails.

        Example:
            ```pycon
            >>> from feu.install import PipInstaller
            >>> from feu.utils.package import PackageSpec
            >>> PipInstaller().install(PackageSpec("pandas", "2.2.2"))  # doctest: +SKIP

            ```
        """
        self.check_available()
        registry = get_default_resolver_registry() if resolvers is None else resolvers
        run_command(self.command(resolve(package, registry)))


class PipInstaller(Installer):
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
        >>> from feu.install import PipInstaller
        >>> installer = PipInstaller()
        >>> installer
        PipInstaller(arguments=())

        ```
    """

    prefix: ClassVar[tuple[str, ...]] = (sys.executable, "-m", "pip", "install")

    def check_available(self) -> None:
        if not is_pip_available():
            msg = (
                f"pip is not available in the interpreter {sys.executable!r}: "
                "run `python -m ensurepip` to install it, or use the 'uv' installer"
            )
            raise RuntimeError(msg)


class UvInstaller(Installer):
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
        >>> from feu.install import UvInstaller
        >>> installer = UvInstaller()
        >>> installer
        UvInstaller(arguments=())

        ```
    """

    prefix: ClassVar[tuple[str, ...]] = ("uv", "pip", "install", "--python", sys.executable)

    def check_available(self) -> None:
        if not is_uv_available():
            msg = "uv is not found on the PATH: install it with `pip install uv`"
            raise RuntimeError(msg)


@cache
def is_pip_available() -> bool:
    r"""Check if ``pip`` is available in the interpreter that runs
    ``feu``.

    The result is cached.

    Returns:
        ``True`` if the ``pip`` module is available, otherwise
            ``False``.

    Example:
        ```pycon
        >>> from feu.install import is_pip_available
        >>> isinstance(is_pip_available(), bool)
        True

        ```
    """
    return find_spec("pip") is not None


@cache
def is_uv_available() -> bool:
    r"""Check if ``uv`` is available.

    The result is cached.

    Returns:
        ``True`` if ``uv`` is found on the ``PATH``, otherwise
            ``False``.

    Example:
        ```pycon
        >>> from feu.install import is_uv_available
        >>> isinstance(is_uv_available(), bool)
        True

        ```
    """
    return which("uv") is not None


@cache
def get_default_installer_registry() -> Registry[type[Installer]]:
    r"""Get the default installer registry.

    The registry maps an installer name (case-insensitive) to an
    installer class. ``"pip"`` and ``"uv"`` are registered by default.
    The same instance is returned by every call.

    Returns:
        The default registry.

    Example:
        ```pycon
        >>> from feu.install import get_default_installer_registry
        >>> get_default_installer_registry().keys()
        ['pip', 'uv']

        ```
    """
    registry: Registry[type[Installer]] = Registry("installer", normalize=str.lower)
    registry.register("pip", PipInstaller)
    registry.register("uv", UvInstaller)
    return registry


def register_installer(name: str, installer: type[Installer], *, exist_ok: bool = False) -> None:
    r"""Register an installer class in the default registry.

    Args:
        name: The installer name e.g. ``"pip"`` or ``"uv"``.
        installer: The installer class used for the given name.
        exist_ok: If ``False``, a ``RuntimeError`` is raised when an
            installer is already registered for the name. Set to
            ``True`` to overwrite.

    Raises:
        RuntimeError: If an installer is already registered for the
            name and ``exist_ok`` is ``False``.

    Example:
        ```pycon
        >>> from feu.install import PipInstaller, register_installer
        >>> register_installer("pip", PipInstaller, exist_ok=True)

        ```
    """
    get_default_installer_registry().register(name, installer, exist_ok=exist_ok)
