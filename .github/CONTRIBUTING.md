# Contributing to feu

Thank you for your interest in contributing to `feu`! We welcome contributions from everyone.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone git@github.com:YOUR_USERNAME/feu.git
   cd feu
   ```
3. **Set up the development environment**:
   ```bash
   make setup-venv
   ```

## Development Workflow

### Setting Up Your Environment

The project uses `uv` for dependency management. After cloning the repository:

```bash
# Create and activate a virtual environment
make setup-venv

# Or manually:
uv venv --python 3.13
source .venv/bin/activate
uv sync --all-extras --group dev --group docs
```

### Running Tests

Run the test suite to ensure everything works:

```bash
# Run all tests with coverage
inv unit-test --cov

# Run only unit tests
inv unit-test

# Run integration tests
inv integration-test

# Run functional tests
inv functional-test
```

### Code Quality

Before submitting a pull request, ensure your code meets our quality standards:

#### Formatting

We use `black` for code formatting:

```bash
# Check formatting
inv check-format
```

#### Linting

We use `ruff` for linting:

```bash
# Check linting
inv check-lint
```

#### Pre-commit Hooks

Install pre-commit hooks to automatically check your code before committing:

```bash
pre-commit install
pre-commit run --all-files
```

#### Docstring Format

We follow Google-style docstrings. Run docformatter to ensure consistency:

```bash
inv docformat
```

### Documentation

#### Building Documentation

The documentation is built using MkDocs with `mike` for versioning:

```bash
# Install documentation dependencies
uv sync --group docs

# Serve documentation locally (for development)
cd docs
mike serve

# Deploy documentation with mike (for maintainers)
# Development version:
inv publish-doc-dev
# Stable version:
inv publish-doc-latest
```

Visit `http://127.0.0.1:8000` to view the documentation locally.

#### Writing Documentation

- Add docstrings to all public functions, classes, and modules
- Follow the Google docstring format
- Include example usage in docstrings when appropriate
- Update relevant `.md` files in `docs/docs/` for user-facing documentation

## Pull Request Process

1. **Create a new branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make your changes** following the code style guidelines

3. **Write or update tests** to cover your changes

4. **Run the test suite** and ensure all tests pass:
   ```bash
   inv unit-test --cov
   ```

5. **Update documentation** if you've changed APIs or added features

6. **Commit your changes** with clear, descriptive commit messages:
   ```bash
   git commit -m "Add feature: description of what you added"
   ```

7. **Push to your fork**:
   ```bash
   git push origin feature/my-new-feature
   ```

8. **Open a Pull Request** on GitHub with:
   - A clear title describing the change
   - A detailed description of what you changed and why
   - References to any related issues

### Pull Request Checklist

Before submitting, ensure your PR:

- [ ] Passes all tests (`inv unit-test --cov`)
- [ ] Follows code style guidelines (`inv check-format` and `inv check-lint`)
- [ ] Includes tests for new functionality
- [ ] Updates documentation as needed
- [ ] Has a clear description of changes
- [ ] References related issues (if applicable)

## Types of Contributions

### Bug Reports

When filing a bug report, please include:

- A clear, descriptive title
- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- Your environment (Python version, OS, feu version)
- Any relevant code snippets or error messages

### Feature Requests

When proposing a feature:

- Explain the use case and why it would be valuable
- Provide examples of how it would be used
- Consider potential implementation approaches
- Discuss any potential downsides or alternatives

### Code Contributions

We welcome code contributions for:

- Bug fixes
- New features
- Performance improvements
- Documentation improvements
- Test coverage improvements

For significant changes, please open an issue first to discuss the proposed changes.

## Code Style Guidelines

### Python Style

- Follow PEP 8 guidelines
- Use type hints for function signatures
- Maximum line length: 100 characters
- Use meaningful variable and function names

### Docstrings

We use Google-style docstrings.

### Import Order

Follow this import order (enforced by `ruff`):

1. Standard library imports
2. Third-party imports
3. Local imports

Use absolute imports and separate groups with blank lines.

## Testing Guidelines

### Writing Tests

- Place tests in the appropriate directory (`unit/`, `integration/`, or `functional/`)
- Name test files with `test_` prefix
- Name test functions with `test_` prefix
- Use descriptive test names that explain what is being tested
- Include both positive and negative test cases
- Test edge cases and error conditions


### Test Coverage

- Aim for high test coverage (current target: >80%)
- Focus on testing behavior, not implementation details
- Include integration tests for complex interactions

## Project Structure

```
feu/
├── src/feu/              # Source code
│   ├── __init__.py       # Main package exports
│   ├── package.py        # Package configuration
│   ├── imports.py        # Import utilities
│   ├── git.py           # Git utilities
│   ├── install/         # Installation utilities
│   ├── version/         # Version management
│   └── utils/           # Utility functions
├── tests/               # Test suite
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   └── functional/     # Functional tests
├── docs/               # Documentation
│   ├── docs/          # Markdown files
│   └── mkdocs.yml     # MkDocs configuration
└── pyproject.toml     # Project configuration
```

## Release Process

Releases are managed by the project maintainers. The process includes:

1. Update version in `pyproject.toml`
2. Create a git tag
3. Build and upload to PyPI
4. Create a GitHub release with release notes

## Getting Help

If you need help or have questions:

- Open an issue on GitHub
- Check existing issues and pull requests
- Review the documentation at https://durandtibo.github.io/feu/

## Code of Conduct

Please note that this project has a [Code of Conduct](../CODE_OF_CONDUCT.md). By participating in this project, you agree to abide by its terms.

## License

By contributing to `feu`, you agree that your contributions will be licensed under the BSD-3-Clause license.

## Acknowledgments

Thank you for contributing to `feu`! Every contribution, no matter how small, is valuable and appreciated.
