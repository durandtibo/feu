# Get Started

It is highly recommended to install in
a [virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)
to keep your system in order.

## Installing with `pip` (recommended)

The following command installs the latest version of the library:

```shell
pip install feu
```

To make the package as slim as possible, only the packages required to use `feu` are installed.
It is possible to install all the optional dependencies by running the following command:

```shell
pip install 'feu[all]'
```

It is also possible to install specific optional dependencies:

- `feu[cli]` - Install CLI support (click): the `feu` command
- `feu[git]` - Install git support (gitpython): `feu.local_git`
- `feu[requests]` - Install HTTP request support (requests, urllib3): the calls to PyPI and
  GitHub, which a wildcard version request (`2.*`) needs
- `feu[rich]` - Install rich console/formatting support (rich): `show_compat_targets`

`feu` requires Python 3.11 or newer. Without an extra, the feature that needs it raises a
`MissingPackageError` that gives the `pip install` command. The `pytest` marks of `feu.testing`
need `pytest`, which is not a dependency of `feu`.

Installing with the `uv` installer of `feu` also needs the [`uv`](https://docs.astral.sh/uv/) tool
on the `PATH`.

For example:

```shell
pip install 'feu[cli,git]'
```

## Checking the installation

```pycon
>>> import feu
>>> from feu import is_package_available
>>> is_package_available("packaging")
True

```

The [Usage Guide](usage.md) shows the main features, and the [Design](design.md) page explains the
properties of the library and the trade-offs of its design.

## Installing from source

To install `feu` from source, you can follow the steps below. First, you will need to
install [`uv`](https://docs.astral.sh/uv/). `uv` is a fast Python package installer and resolver
used to manage dependencies in this project.

You can install `uv` using:

```shell
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

Then, clone the git repository:

```shell
git clone git@github.com:durandtibo/feu.git
cd feu
```

It is recommended to create a Python 3.11+ virtual environment. The easiest way is to use the
provided Makefile command:

```shell
make setup-venv
```

This command automatically:

1. Updates `uv` to the latest version
2. Creates a Python 3.14 virtual environment
3. Installs `invoke` task runner
4. Installs all dependencies including development and documentation dependencies

Alternatively, you can manually set up the environment:

```shell
# Create a virtual environment with uv
uv venv --python 3.14

# Activate the virtual environment
source .venv/bin/activate

# Install the package with all dependencies
uv sync --all-extras --group dev --group docs
```

After installation, you can verify everything is working by running the tests:

```shell
inv test.unit --cov
```
