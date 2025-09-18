from __future__ import annotations

__all__ = ["install_package"]


def install_package(package: str, version: str, installer: str, args: str = "") -> None:
    r"""Install a package and associated packages.

    Args:
        package: The package name e.g. ``'pandas'``.
        version: The target version to install.

    Example usage:

    ```pycon

    >>> from feu import install_package
    >>> install_package("pandas", "2.2.2")  # doctest: +SKIP

    ```
    """
    Installer.get_installer(installer).install(package, version, args)
