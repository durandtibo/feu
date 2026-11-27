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
uv venv --python 3.14
source .venv/bin/activate
uv sync --all-extras --group dev --group docs
```

### Running Tests

Run the test suite to ensure everything works:

```bash
# Run the full test suite (unit + integration + functional) with coverage
inv test.all --cov

# Run only unit tests
inv test.unit --cov

# Run integration tests
inv test.integration

# Run functional tests
inv test.functional

# Run the examples of the docstrings and of the Markdown files
inv test.doctest
```

### Code Quality

Before submitting a pull request, ensure your code meets our quality standards:

#### Formatting

We use `ruff` for code formatting:

```bash
# Check formatting
inv format.check-python

# Format the code
inv format.fix-python
```

#### Linting

We use `ruff` for linting:

```bash
# Check linting
inv lint.check-python

# Fix the issues that can be fixed automatically
inv lint.fix-python
```

#### Type Checking

We use `ty` and `pyright` for type checking:

```bash
inv types.check --complete
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
inv format.fix-docstrings
```

### Documentation

#### Building Documentation

The documentation is built using MkDocs with `mike` for versioning:

```bash
# Install documentation dependencies
uv sync --all-extras --group dev --group docs

# Serve documentation locally (for development)
inv doc.serve

# Build the documentation and fail on any warning
inv doc.build

# Deploy documentation with mike (for maintainers)
# Development version:
inv doc.publish-dev
# Stable version:
inv doc.publish-latest
```

Visit `http://127.0.0.1:8000` to view the documentation locally.

#### Writing Documentation

- Add docstrings to all modules, classes and functions, including the private ones
- Follow the Google docstring format (`Args:`, `Returns:`, `Raises:`)
- Add a `pycon` example to the public functions and classes: it runs as a doctest. Mark the lines
  that need the network or modify the environment with `# doctest: +SKIP`
- The help of a command of the CLI is its `help` argument, not its docstring
- Update relevant `.md` files in `docs/docs/` for user-facing documentation. The examples of
  `README.md` and of the main pages also run as tests (`tests/unit/test_docs.py`)

## Pull Request Process

1. **Create a new branch** named `<type>/<short-description>`, where the type is one of `feat`,
   `bugfix`, `hotfix`, `docs`, `refactor`, `perf`, `test`, `chore` or `ci`:

   ```bash
   git checkout -b feat/my-new-feature
   ```

2. **Make your changes** following the code style guidelines

3. **Write or update tests** to cover your changes

4. **Run the test suite** and ensure all tests pass:

   ```bash
   inv test.unit --cov
   ```

5. **Update documentation** if you've changed APIs or added features

6. **Commit your changes** with a short imperative sentence that starts with a verb such as `Add`,
   `Fix`, `Update`, `Remove` or `Improve`:

   ```bash
   git commit -m "Add the cache option"
   ```

7. **Push to your fork**:

   ```bash
   git push origin feat/my-new-feature
   ```

8. **Open a Pull Request** on GitHub with:
   - A clear title describing the change
   - A detailed description of what you changed and why
   - References to any related issues

### Pull Request Checklist

Before submitting, ensure your PR:

- [ ] Passes all tests (`inv test.unit --cov`)
- [ ] Follows code style guidelines (`inv format.check-python` and `inv lint.check-python`)
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

- Place tests in the appropriate directory (`unit/`, `integration/`, or `functional/`). The unit
  tests mirror the source tree and do not use the network or run installers
- Name test files with `test_` prefix
- Name test functions with `test_` prefix
- Use descriptive test names that explain what is being tested
- Include both positive and negative test cases
- Test edge cases and error conditions

### Test Coverage

- Cover all the code that you add or change
- Focus on testing behavior, not implementation details
- Include integration tests for complex interactions

## Project Structure

```text
feu/
├── src/feu/              # Source code
│   ├── __init__.py       # Main package exports
│   ├── __main__.py       # Entry point of `python -m feu`
│   ├── benchmark/        # Trend of the pytest-benchmark results
│   ├── cli.py            # Command line interface
│   ├── compat/           # Package/Python-version compatibility registry and discovery
│   ├── github/           # GitHub API utilities
│   ├── imports/          # Optional-dependency availability checks
│   ├── install/          # Installers (pip, uv) and dependency resolvers
│   ├── local_git.py      # Git tag utilities
│   ├── testing.py        # Pytest skip marks for optional dependencies
│   ├── utils/            # Utility functions
│   └── version/          # Version management
├── tests/               # Test suite
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   ├── functional/     # Functional tests
│   └── benchmarks/     # Performance benchmarks
├── dev/                  # Maintenance scripts (compatibility data, package versions)
├── docs/               # Documentation
│   ├── docs/          # Markdown files
│   └── mkdocs.yml     # MkDocs configuration
└── pyproject.toml     # Project configuration
```

## Release Process

Releases are managed by the project maintainers. The process includes:

1. Update version in `pyproject.toml`
2. Create and push a git tag `vX.Y.Z`
3. The `release-pypi` workflow builds, signs and publishes the package to PyPI, and the
   `release-docs` workflow deploys the documentation
4. Write the release notes of the GitHub release

## Getting Help

If you need help or have questions:

- Open an issue on GitHub
- Check existing issues and pull requests
- Review the documentation at <https://durandtibo.github.io/feu/>

## Code of Conduct

Please note that this project has a [Code of Conduct](CODE_OF_CONDUCT.md). By participating in this
project, you agree to abide by its terms.

## License

By contributing to `feu`, you agree that your contributions will be licensed under
the BSD-3-Clause license.

## Acknowledgments

Thank you for contributing to `feu`! Every contribution, no matter how small, is
valuable and appreciated.
