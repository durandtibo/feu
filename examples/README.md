# Examples

This directory contains practical examples demonstrating how to use `feu` in real-world scenarios.

## Available Examples

1. **[check_packages.py](check_packages.py)** - Check if multiple packages are installed
2. **[version_compatibility.py](version_compatibility.py)** - Check version compatibility for different Python versions
3. **[install_with_compatibility.py](install_with_compatibility.py)** - Install packages with automatic version resolution
4. **[custom_package_config.py](custom_package_config.py)** - Add custom package configurations
5. **[conditional_imports.py](conditional_imports.py)** - Use conditional imports based on package availability

## Running the Examples

Make sure you have `feu` installed:

```bash
pip install feu
```

For examples using CLI or git features, install the optional dependencies:

```bash
pip install 'feu[all]'
```

Then run any example:

```bash
python examples/check_packages.py
```

## Example Categories

### Basic Usage
- `check_packages.py` - Simple package availability checks
- `conditional_imports.py` - Graceful fallbacks when packages aren't available

### Version Management
- `version_compatibility.py` - Working with version constraints
- `install_with_compatibility.py` - Smart package installation

### Advanced
- `custom_package_config.py` - Extending feu with custom configurations
