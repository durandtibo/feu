"""Example: Install packages with automatic version resolution.

This example demonstrates how to install packages with automatic
version compatibility checking using feu.

Note: This example is for demonstration purposes. In real scenarios,
you might want to add error handling and user confirmation.
"""

from __future__ import annotations

import sys

from feu import install_package_closest_version, is_package_available
from feu.package import find_closest_version
from feu.utils.installer import InstallerSpec
from feu.utils.package import PackageSpec


def get_python_version() -> str:
    """Get the current Python version as a string.

    Returns:
        Python version string (e.g., "3.11").
    """
    return f"{sys.version_info.major}.{sys.version_info.minor}"


def demo_version_resolution() -> None:
    """Demonstrate version resolution without installation."""
    python_version = get_python_version()

    print(f"Current Python version: {python_version}")
    print("\nVersion Resolution Demo (no installation)")
    print("=" * 80)

    packages = [
        ("numpy", "2.0.2"),
        ("numpy", "1.0.0"),
        ("pandas", "2.0.0"),
        ("pandas", "0.20.0"),
        ("torch", "2.0.0"),
    ]

    for pkg_name, requested_version in packages:
        resolved_version = find_closest_version(
            pkg_name=pkg_name,
            pkg_version=requested_version,
            python_version=python_version,
        )

        if resolved_version == requested_version:
            print(
                f"{pkg_name:15} {requested_version:10} → {resolved_version:10} (no change needed)"
            )
        else:
            print(
                f"{pkg_name:15} {requested_version:10} → {resolved_version:10} "
                f"(adjusted for Python {python_version})"
            )


def demo_safe_installation() -> None:
    """Demonstrate safe package installation with version checking.

    Note: This is commented out by default to prevent unwanted installations.
    Uncomment the install lines if you want to actually install packages.
    """
    print("\n\nSafe Installation Demo")
    print("=" * 80)
    print("Note: Installation commands are commented out for safety.")
    print("Uncomment them in the source code if you want to test installation.\n")

    pkg_name = "packaging"  # Using 'packaging' as it's a common dependency
    pkg_version = "24.0"

    if is_package_available(pkg_name):
        print(f"✓ {pkg_name} is already installed")
    else:
        print(f"✗ {pkg_name} is not installed")
        print(f"Would install {pkg_name} {pkg_version} with version compatibility check")

        # Uncomment the following lines to actually install:
        # print(f"Installing {pkg_name}...")
        # install_package_closest_version(
        #     installer=InstallerSpec(name="pip", arguments="--quiet"),
        #     package=PackageSpec(name=pkg_name, version=pkg_version),
        # )
        # print(f"✓ {pkg_name} installed successfully")


def demo_install_with_extras() -> None:
    """Demonstrate package installation with extras.

    Note: This is commented out by default to prevent unwanted installations.
    """
    print("\n\nInstallation with Extras Demo")
    print("=" * 80)
    print("Note: Installation commands are commented out for safety.\n")

    pkg_name = "requests"
    pkg_version = "2.31.0"
    pkg_extras = ["security", "socks"]

    print(f"Would install {pkg_name}[{','.join(pkg_extras)}] version {pkg_version}")

    # Uncomment to actually install:
    # install_package_closest_version(
    #     installer=InstallerSpec(name="pip", arguments="--quiet"),
    #     package=PackageSpec(
    #         name=pkg_name,
    #         version=pkg_version,
    #         extras=pkg_extras,
    #     ),
    # )


def main() -> None:
    """Run the example."""
    demo_version_resolution()
    demo_safe_installation()
    demo_install_with_extras()

    print("\n" + "=" * 80)
    print("Example completed!")
    print("\nTo enable actual package installation:")
    print("1. Edit this file")
    print("2. Uncomment the install_package_closest_version() calls")
    print("3. Run the script again")


if __name__ == "__main__":
    main()
