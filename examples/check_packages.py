"""Example: Check if multiple packages are installed.

This example demonstrates how to use feu to check the availability
of multiple packages and get their versions.
"""

from __future__ import annotations

from feu import get_package_version, is_package_available


def check_packages(package_names: list[str]) -> None:
    """Check if packages are installed and print their versions.

    Args:
        package_names: List of package names to check.
    """
    print("Checking package availability...\n")

    for pkg_name in package_names:
        if is_package_available(pkg_name):
            version = get_package_version(pkg_name)
            print(f"✓ {pkg_name:20} - Installed (version {version})")
        else:
            print(f"✗ {pkg_name:20} - Not installed")


def main() -> None:
    """Run the example."""
    # List of common packages to check
    packages = [
        "numpy",
        "pandas",
        "scipy",
        "matplotlib",
        "torch",
        "scikit-learn",
        "requests",
        "click",
    ]

    check_packages(packages)

    # You can also check specific modules
    print("\nChecking specific modules...\n")

    from feu import is_module_available

    modules = [
        "numpy.linalg",
        "pandas.core",
        "scipy.stats",
        "torch.nn",
    ]

    for module_name in modules:
        if is_module_available(module_name):
            print(f"✓ {module_name:20} - Available")
        else:
            print(f"✗ {module_name:20} - Not available")


if __name__ == "__main__":
    main()
