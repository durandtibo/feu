"""Example: Check version compatibility for different Python versions.

This example demonstrates how to check if package versions are compatible
with different Python versions and find the closest valid versions.
"""

from __future__ import annotations

from feu.package import find_closest_version, is_valid_version


def check_version_compatibility() -> None:
    """Check version compatibility for common packages across Python versions."""
    packages = [
        ("numpy", "2.0.2"),
        ("numpy", "1.20.0"),
        ("pandas", "2.0.0"),
        ("torch", "2.0.0"),
        ("scipy", "1.10.0"),
    ]

    python_versions = ["3.9", "3.10", "3.11", "3.12", "3.13"]

    print("Package Version Compatibility Check")
    print("=" * 80)

    for pkg_name, pkg_version in packages:
        print(f"\n{pkg_name} {pkg_version}:")
        print("-" * 80)

        for py_version in python_versions:
            is_valid = is_valid_version(
                pkg_name=pkg_name,
                pkg_version=pkg_version,
                python_version=py_version,
            )

            status = "✓ Valid" if is_valid else "✗ Invalid"

            if not is_valid:
                closest = find_closest_version(
                    pkg_name=pkg_name,
                    pkg_version=pkg_version,
                    python_version=py_version,
                )
                print(f"  Python {py_version}: {status:12} (closest: {closest})")
            else:
                print(f"  Python {py_version}: {status:12}")


def find_best_versions() -> None:
    """Find the best versions for specific Python versions."""
    print("\n\nFinding Best Versions for Python 3.11")
    print("=" * 80)

    test_versions = [
        ("numpy", "2.0.2"),
        ("numpy", "1.0.0"),
        ("pandas", "2.0.0"),
        ("pandas", "1.0.0"),
        ("torch", "2.5.0"),
        ("torch", "1.0.0"),
    ]

    python_version = "3.11"

    for pkg_name, test_version in test_versions:
        closest = find_closest_version(
            pkg_name=pkg_name,
            pkg_version=test_version,
            python_version=python_version,
        )

        if closest == test_version:
            print(f"{pkg_name:15} {test_version:10} → {closest:10} (unchanged)")
        else:
            print(f"{pkg_name:15} {test_version:10} → {closest:10} (adjusted)")


def main() -> None:
    """Run the example."""
    check_version_compatibility()
    find_best_versions()


if __name__ == "__main__":
    main()
