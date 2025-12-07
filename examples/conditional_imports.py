"""Example: Use conditional imports based on package availability.

This example demonstrates how to use feu to implement graceful
fallbacks when optional packages are not available.
"""

from __future__ import annotations

from feu import is_package_available


def example_numpy_fallback() -> None:
    """Demonstrate conditional import with NumPy."""
    print("NumPy Example")
    print("=" * 80)

    if is_package_available("numpy"):
        import numpy as np

        print("✓ NumPy is available")

        # Use NumPy for fast array operations
        data = np.array([1, 2, 3, 4, 5])
        mean = np.mean(data)
        print(f"  Using NumPy: mean of {data.tolist()} = {mean}")
    else:
        print("✗ NumPy is not available")
        print("  Using Python built-ins as fallback")

        # Fallback to Python built-ins
        data = [1, 2, 3, 4, 5]
        mean = sum(data) / len(data)
        print(f"  Using built-ins: mean of {data} = {mean}")


def example_pandas_fallback() -> None:
    """Demonstrate conditional import with Pandas."""
    print("\n\nPandas Example")
    print("=" * 80)

    data = {"name": ["Alice", "Bob", "Charlie"], "age": [25, 30, 35], "city": ["NYC", "LA", "SF"]}

    if is_package_available("pandas"):
        import pandas as pd

        print("✓ Pandas is available")

        # Use Pandas for data handling
        df = pd.DataFrame(data)
        print(f"  Using Pandas DataFrame:\n{df}")
        print(f"\n  Average age: {df['age'].mean()}")
    else:
        print("✗ Pandas is not available")
        print("  Using Python dictionaries as fallback")

        # Fallback to simple dictionary operations
        print(f"  Using dictionary: {data}")
        ages = data["age"]
        print(f"\n  Average age: {sum(ages) / len(ages)}")


def example_visualization_fallback() -> None:
    """Demonstrate conditional import with Matplotlib."""
    print("\n\nVisualization Example")
    print("=" * 80)

    if is_package_available("matplotlib"):
        print("✓ Matplotlib is available")
        print("  Could create plots with matplotlib.pyplot")
        print("  (Actual plotting skipped in this example)")
    else:
        print("✗ Matplotlib is not available")
        print("  Would use text-based visualization or skip plotting")


def example_multiple_alternatives() -> None:
    """Demonstrate choosing between multiple alternatives."""
    print("\n\nMultiple Alternatives Example")
    print("=" * 80)

    # Check for multiple JSON libraries, in order of preference
    json_library = None

    if is_package_available("orjson"):
        print("✓ Using orjson (fastest option)")
        json_library = "orjson"
    elif is_package_available("ujson"):
        print("✓ Using ujson (fast option)")
        json_library = "ujson"
    else:
        print("✓ Using standard json library (always available)")
        json_library = "json"

    print(f"  Selected JSON library: {json_library}")


def example_feature_detection() -> None:
    """Demonstrate feature detection based on available packages."""
    print("\n\nFeature Detection Example")
    print("=" * 80)

    features = {
        "numpy": "Fast numerical computations",
        "pandas": "Advanced data manipulation",
        "scipy": "Scientific computing",
        "matplotlib": "Data visualization",
        "torch": "Deep learning",
        "scikit-learn": "Machine learning",
        "requests": "HTTP requests",
    }

    available_features = []
    unavailable_features = []

    for package, description in features.items():
        if is_package_available(package):
            available_features.append((package, description))
        else:
            unavailable_features.append((package, description))

    print(f"Available features ({len(available_features)}):")
    for package, description in available_features:
        print(f"  ✓ {package:15} - {description}")

    if unavailable_features:
        print(f"\nUnavailable features ({len(unavailable_features)}):")
        for package, description in unavailable_features:
            print(f"  ✗ {package:15} - {description}")


def example_module_level_import() -> None:
    """Demonstrate module-level conditional imports."""
    print("\n\nModule-Level Import Example")
    print("=" * 80)

    # This pattern is useful at module level
    from feu import is_module_available

    if is_module_available("numpy.linalg"):
        print("✓ NumPy linear algebra module available")
        print("  Can use advanced linear algebra functions")
    else:
        print("✗ NumPy linear algebra module not available")

    if is_module_available("torch.nn"):
        print("✓ PyTorch neural network module available")
        print("  Can build neural network models")
    else:
        print("✗ PyTorch neural network module not available")


class DataProcessor:
    """Example class that adapts based on available packages."""

    def __init__(self) -> None:
        """Initialize the data processor with available backends."""
        self.numpy_available = is_package_available("numpy")
        self.pandas_available = is_package_available("pandas")

        if self.numpy_available:
            import numpy as np

            self.np = np
        if self.pandas_available:
            import pandas as pd

            self.pd = pd

        print("\nDataProcessor initialized:")
        print(f"  NumPy backend: {'✓ enabled' if self.numpy_available else '✗ disabled'}")
        print(f"  Pandas backend: {'✓ enabled' if self.pandas_available else '✗ disabled'}")

    def process(self, data: list[float]) -> float:
        """Process data using the best available backend."""
        if self.numpy_available:
            # Use NumPy for fast processing
            return float(self.np.mean(data))
        # Fallback to pure Python
        return sum(data) / len(data)


def example_adaptive_class() -> None:
    """Demonstrate an adaptive class that uses available packages."""
    print("\n\nAdaptive Class Example")
    print("=" * 80)

    processor = DataProcessor()
    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    result = processor.process(data)
    print(f"  Processed result: {result}")


def main() -> None:
    """Run all examples."""
    example_numpy_fallback()
    example_pandas_fallback()
    example_visualization_fallback()
    example_multiple_alternatives()
    example_feature_detection()
    example_module_level_import()
    example_adaptive_class()

    print("\n" + "=" * 80)
    print("Example completed!")
    print("\nKey takeaways:")
    print("1. Use is_package_available() to check for optional dependencies")
    print("2. Provide fallbacks for better user experience")
    print("3. Feature detection allows graceful degradation")
    print("4. Adaptive classes can optimize based on available packages")


if __name__ == "__main__":
    main()
