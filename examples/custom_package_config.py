"""Example: Add custom package configurations.

This example demonstrates how to extend feu with custom package
configurations for packages not in the default registry.
"""

from __future__ import annotations

from feu.package import PackageConfig, find_closest_version, is_valid_version


def add_custom_configurations() -> None:
    """Add custom package configurations to the registry."""
    print("Adding custom package configurations...")
    print("=" * 80)

    # Add configuration for a custom package
    PackageConfig.add_config(
        pkg_name="my_custom_package",
        python_version="3.11",
        pkg_version_min="2.0.0",
        pkg_version_max="3.0.0",
        exist_ok=True,
    )
    print("✓ Added config for my_custom_package on Python 3.11")

    # Add configurations for different Python versions
    for py_version in ["3.10", "3.12", "3.13"]:
        PackageConfig.add_config(
            pkg_name="my_custom_package",
            python_version=py_version,
            pkg_version_min="2.0.0",
            pkg_version_max="3.5.0",
            exist_ok=True,
        )
        print(f"✓ Added config for my_custom_package on Python {py_version}")

    # Add a package with only minimum version constraint
    PackageConfig.add_config(
        pkg_name="another_package",
        python_version="3.11",
        pkg_version_min="1.5.0",
        pkg_version_max=None,  # No maximum version
        exist_ok=True,
    )
    print("✓ Added config for another_package on Python 3.11 (no max version)")

    # Add a package with only maximum version constraint
    PackageConfig.add_config(
        pkg_name="legacy_package",
        python_version="3.11",
        pkg_version_min=None,  # No minimum version
        pkg_version_max="1.0.0",
        exist_ok=True,
    )
    print("✓ Added config for legacy_package on Python 3.11 (no min version)")


def demonstrate_custom_configs() -> None:
    """Demonstrate using custom package configurations."""
    print("\n\nUsing custom package configurations...")
    print("=" * 80)

    # Test custom package version validation
    test_cases = [
        ("my_custom_package", "2.5.0", "3.11"),
        ("my_custom_package", "1.0.0", "3.11"),
        ("my_custom_package", "4.0.0", "3.11"),
        ("another_package", "2.0.0", "3.11"),
        ("another_package", "1.0.0", "3.11"),
        ("legacy_package", "0.5.0", "3.11"),
        ("legacy_package", "1.5.0", "3.11"),
    ]

    for pkg_name, pkg_version, py_version in test_cases:
        is_valid = is_valid_version(
            pkg_name=pkg_name,
            pkg_version=pkg_version,
            python_version=py_version,
        )

        closest = find_closest_version(
            pkg_name=pkg_name,
            pkg_version=pkg_version,
            python_version=py_version,
        )

        status = "✓ Valid" if is_valid else "✗ Invalid"
        print(f"{pkg_name:20} {pkg_version:10} → {status:12} (closest: {closest})")


def inspect_configurations() -> None:
    """Inspect package configurations."""
    print("\n\nInspecting package configurations...")
    print("=" * 80)

    packages = ["my_custom_package", "another_package", "legacy_package"]

    for pkg_name in packages:
        print(f"\n{pkg_name}:")

        for py_version in ["3.10", "3.11", "3.12", "3.13"]:
            config = PackageConfig.get_config(
                pkg_name=pkg_name,
                python_version=py_version,
            )

            if config:
                min_ver = config.get("min", "None")
                max_ver = config.get("max", "None")
                print(f"  Python {py_version}: min={min_ver}, max={max_ver}")
            else:
                print(f"  Python {py_version}: No configuration")

    # Get min and max versions for a specific configuration
    print("\n\nDetailed version info for my_custom_package on Python 3.11:")
    min_version, max_version = PackageConfig.get_min_and_max_versions(
        pkg_name="my_custom_package",
        python_version="3.11",
    )
    print(f"  Minimum version: {min_version}")
    print(f"  Maximum version: {max_version}")


def demonstrate_real_package() -> None:
    """Demonstrate with a real package from the registry."""
    print("\n\nComparing with real package (numpy)...")
    print("=" * 80)

    test_versions = ["1.20.0", "1.23.2", "2.0.0"]
    python_versions = ["3.10", "3.11", "3.12"]

    print(f"{'Python Version':<15} {'Requested':<12} {'Status':<12} {'Closest':<12}")
    print("-" * 60)

    for py_version in python_versions:
        for test_version in test_versions:
            is_valid = is_valid_version(
                pkg_name="numpy",
                pkg_version=test_version,
                python_version=py_version,
            )
            closest = find_closest_version(
                pkg_name="numpy",
                pkg_version=test_version,
                python_version=py_version,
            )
            status = "Valid" if is_valid else "Invalid"
            print(f"{py_version:<15} {test_version:<12} {status:<12} {closest:<12}")


def main() -> None:
    """Run the example."""
    add_custom_configurations()
    demonstrate_custom_configs()
    inspect_configurations()
    demonstrate_real_package()

    print("\n" + "=" * 80)
    print("Example completed!")
    print("\nKey takeaways:")
    print("1. You can add custom package configurations with add_config()")
    print("2. Configurations support min and/or max version constraints")
    print("3. Different Python versions can have different constraints")
    print("4. The system automatically finds the closest valid version")


if __name__ == "__main__":
    main()
