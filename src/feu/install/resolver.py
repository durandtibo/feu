r"""Contain the dependency resolvers.

A dependency resolver is a function that takes a ``PackageSpec`` and
returns the list of requirements to install to get a working package,
e.g. ``pandas`` before 2.2.2 needs ``numpy<2.0.0``. The resolvers are
registered by canonical package name in a ``Registry``.
"""

from __future__ import annotations

__all__ = [
    "NUMPY2_MIN_VERSION",
    "Resolver",
    "default_resolver",
    "get_default_resolver_registry",
    "jax_resolver",
    "numpy2_resolver",
    "register_resolver",
    "resolve",
]

from functools import cache
from types import MappingProxyType
from typing import TYPE_CHECKING, TypeAlias

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from packaging.version import Version

from feu.utils.registry import Registry
from feu.version.request import VersionRequest, parse_version_request

if TYPE_CHECKING:
    from collections.abc import Callable

    from feu.utils.package import PackageSpec

#: A dependency resolver: a function from a package to its requirements.
Resolver: TypeAlias = "Callable[[PackageSpec], list[Requirement]]"

#: The first version of each package that is fully compatible with
#: ``numpy`` 2.0. See https://github.com/numpy/numpy/issues/26191.
NUMPY2_MIN_VERSION: MappingProxyType[str, str] = MappingProxyType(
    {
        "matplotlib": "3.8.4",
        "pandas": "2.2.2",
        "pyarrow": "16.0",
        "scikit-learn": "1.4.2",
        "scipy": "1.13.0",
        "torch": "2.3.0",
        "xarray": "2024.6.0",
    }
)

_JAX_NUMPY2_MIN_VERSION = Version("0.4.26")
_JAX_ML_DTYPES_LOWER = Version("0.4.9")
_JAX_ML_DTYPES_UPPER = Version("0.4.12")


def default_resolver(package: PackageSpec) -> list[Requirement]:
    r"""Resolve a package with the default resolver.

    Args:
        package: The package to install.

    Returns:
        The package itself.

    Example:
        ```pycon
        >>> from feu.install.resolver import default_resolver
        >>> from feu.utils.package import PackageSpec
        >>> default_resolver(PackageSpec("my_package", version="1.2.3"))
        [<Requirement('my_package==1.2.3')>]

        ```
    """
    return [package.to_requirement()]


def numpy2_resolver(min_version: str) -> Resolver:
    r"""Create a resolver for a package that did not pin ``numpy<2.0``
    and is not fully compatible with ``numpy`` 2.0 before a version.

    ``numpy<2.0.0`` is added when the **whole** version request lies
    below ``min_version``: ``pandas==2.1.*`` is below ``2.2.2``, but
    ``pandas==2.*`` straddles it and ``""`` is the latest version, so
    no pin is added for them.

    Args:
        min_version: The first version that is fully compatible with
            ``numpy`` 2.0.

    Returns:
        The resolver.

    Example:
        ```pycon
        >>> from feu.install.resolver import numpy2_resolver
        >>> from feu.utils.package import PackageSpec
        >>> resolver = numpy2_resolver("1.2.3")
        >>> resolver(PackageSpec("my_package", version="1.2.3"))
        [<Requirement('my_package==1.2.3')>]
        >>> resolver(PackageSpec("my_package", version="1.2.2"))
        [<Requirement('my_package==1.2.2')>, <Requirement('numpy<2.0.0')>]

        ```
    """
    lower = Version(min_version)

    def resolver(package: PackageSpec) -> list[Requirement]:
        requirements = default_resolver(package)
        if parse_version_request(package.version).entirely_below(lower):
            requirements.append(Requirement("numpy<2.0.0"))
        return requirements

    return resolver


def _is_within(request: VersionRequest, lower: Version, upper: Version) -> bool:
    r"""Indicate if the whole version request lies in ``[lower, upper)``.

    Args:
        request: The version request.
        lower: The lower bound (inclusive).
        upper: The upper bound (exclusive).

    Returns:
        ``True`` if every version that satisfies the request is in the
            interval. A wildcard that straddles a bound and the latest
            request are not within.
    """
    if request.exact is not None:
        return lower <= request.exact < upper
    if request.prefix is not None:
        lowest = Version(".".join(str(part) for part in request.prefix))
        return lowest >= lower and request.entirely_below(upper)
    return False


def jax_resolver(package: PackageSpec) -> list[Requirement]:
    r"""Resolve ``jax``.

    ``jaxlib`` is pinned to the same version request (and not at all
    for the latest version). ``numpy`` 2.0 support was added in
    ``jax`` 0.4.26, so ``numpy<2.0.0`` is added below it.
    ``ml_dtypes<=0.2.0`` is added for 0.4.9 to 0.4.11
    (https://github.com/google/jax/issues/17693).

    Args:
        package: The ``jax`` package to install.

    Returns:
        The requirements.

    Example:
        ```pycon
        >>> from feu.install.resolver import jax_resolver
        >>> from feu.utils.package import PackageSpec
        >>> jax_resolver(PackageSpec("jax", version="0.4.26"))
        [<Requirement('jax==0.4.26')>, <Requirement('jaxlib==0.4.26')>]
        >>> jax_resolver(PackageSpec("jax", version="0.4.25"))
        [<Requirement('jax==0.4.25')>, <Requirement('jaxlib==0.4.25')>, <Requirement('numpy<2.0.0')>]

        ```
    """
    requirements = default_resolver(package)
    request = parse_version_request(package.version)
    if not request.is_latest:
        requirements.append(Requirement(f"jaxlib=={request.text}"))
    if request.entirely_below(_JAX_NUMPY2_MIN_VERSION):
        requirements.append(Requirement("numpy<2.0.0"))
    if _is_within(request, lower=_JAX_ML_DTYPES_LOWER, upper=_JAX_ML_DTYPES_UPPER):
        requirements.append(Requirement("ml_dtypes<=0.2.0"))
    return requirements


@cache
def get_default_resolver_registry() -> Registry[Resolver]:
    r"""Get the default dependency resolver registry.

    The registry maps a canonical package name (PEP 503) to a resolver.
    The packages that are not compatible with ``numpy`` 2.0 before a
    version (``NUMPY2_MIN_VERSION``) and ``jax`` have a resolver. The
    same instance is returned by every call.

    Returns:
        The default registry.

    Example:
        ```pycon
        >>> from feu.install.resolver import get_default_resolver_registry
        >>> registry = get_default_resolver_registry()
        >>> "Scikit_Learn" in registry
        True

        ```
    """
    registry: Registry[Resolver] = Registry("dependency resolver", normalize=canonicalize_name)
    registry.register("jax", jax_resolver)
    for name, min_version in NUMPY2_MIN_VERSION.items():
        registry.register(name, numpy2_resolver(min_version))
    return registry


def register_resolver(
    package: str,
    resolver: Resolver,
    *,
    exist_ok: bool = False,
) -> None:
    r"""Register a dependency resolver in the default registry.

    Args:
        package: The package name, e.g. ``"torch"``. It is
            canonicalised (PEP 503).
        resolver: The resolver used for the package.
        exist_ok: If ``False``, a ``RuntimeError`` is raised when a
            resolver is already registered for the package. Set to
            ``True`` to overwrite.

    Raises:
        RuntimeError: If a resolver is already registered for the
            package and ``exist_ok`` is ``False``.

    Example:
        ```pycon
        >>> from feu.install.resolver import default_resolver, register_resolver
        >>> register_resolver("torch", default_resolver, exist_ok=True)

        ```
    """
    get_default_resolver_registry().register(package, resolver, exist_ok=exist_ok)


def resolve(
    package: PackageSpec,
    registry: Registry[Resolver] | None = None,
) -> list[Requirement]:
    r"""Resolve the requirements to install for a package.

    Args:
        package: The package to install.
        registry: The resolver registry. ``None`` means the default
            registry. The default resolver is used for a package
            without a registered resolver.

    Returns:
        The requirements to install.

    Example:
        ```pycon
        >>> from feu.install.resolver import resolve
        >>> from feu.utils.package import PackageSpec
        >>> resolve(PackageSpec("pandas", version="2.2.1"))
        [<Requirement('pandas==2.2.1')>, <Requirement('numpy<2.0.0')>]

        ```
    """
    registry = get_default_resolver_registry() if registry is None else registry
    return registry.get(package.name, default_resolver)(package)
