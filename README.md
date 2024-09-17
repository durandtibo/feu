# feu :fire:

<p align="center">
    <a href="https://github.com/durandtibo/feu/actions">
        <img alt="CI" src="https://github.com/durandtibo/feu/workflows/CI/badge.svg">
    </a>
    <a href="https://github.com/durandtibo/feu/actions">
        <img alt="Nightly Tests" src="https://github.com/durandtibo/feu/workflows/Nightly%20Tests/badge.svg">
    </a>
    <a href="https://github.com/durandtibo/feu/actions">
        <img alt="Nightly Package Tests" src="https://github.com/durandtibo/feu/workflows/Nightly%20Package%20Tests/badge.svg">
    </a>
    <br/>
    <a href="https://durandtibo.github.io/feu/">
        <img alt="Documentation" src="https://github.com/durandtibo/feu/workflows/Documentation%20(stable)/badge.svg">
    </a>
    <a href="https://durandtibo.github.io/feu/">
        <img alt="Documentation" src="https://github.com/durandtibo/feu/workflows/Documentation%20(unstable)/badge.svg">
    </a>
    <br/>
    <a href="https://codecov.io/gh/durandtibo/feu">
        <img alt="Codecov" src="https://codecov.io/gh/durandtibo/feu/branch/main/graph/badge.svg">
    </a>
    <a href="https://codeclimate.com/github/durandtibo/feu/maintainability">
        <img src="https://api.codeclimate.com/v1/badges/173c4176f130dd424881/maintainability" />
    </a>
    <a href="https://codeclimate.com/github/durandtibo/feu/test_coverage">
        <img src="https://api.codeclimate.com/v1/badges/173c4176f130dd424881/test_coverage" />
    </a>
    <br/>
    <a href="https://github.com/psf/black">
        <img  alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg">
    </a>
    <a href="https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings">
        <img  alt="Doc style: google" src="https://img.shields.io/badge/%20style-google-3666d6.svg">
    </a>
    <a href="https://github.com/astral-sh/ruff">
        <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff" style="max-width:100%;">
    </a>
    <a href="https://github.com/guilatrova/tryceratops">
        <img  alt="Doc style: google" src="https://img.shields.io/badge/try%2Fexcept%20style-tryceratops%20%F0%9F%A6%96%E2%9C%A8-black">
    </a>
    <br/>
    <a href="https://pypi.org/project/feu/">
        <img alt="PYPI version" src="https://img.shields.io/pypi/v/feu">
    </a>
    <a href="https://pypi.org/project/feu/">
        <img alt="Python" src="https://img.shields.io/pypi/pyversions/feu.svg">
    </a>
    <a href="https://opensource.org/licenses/BSD-3-Clause">
        <img alt="BSD-3-Clause" src="https://img.shields.io/pypi/l/feu">
    </a>
    <br/>
    <a href="https://pepy.tech/project/feu">
        <img  alt="Downloads" src="https://static.pepy.tech/badge/feu">
    </a>
    <a href="https://pepy.tech/project/feu">
        <img  alt="Monthly downloads" src="https://static.pepy.tech/badge/feu/month">
    </a>
    <br/>
</p>

## Overview

`feu` is a light Python library to help to manage packages.

- [Documentation](https://durandtibo.github.io/feu/)
- [Installation](#installation)
- [Contributing](#contributing)
- [API stability](#api-stability)
- [License](#license)

## Installation

We highly recommend installing
a [virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/).
`feu` can be installed from pip using the following command:

```shell
pip install feu
```

To make the package as slim as possible, only the minimal packages required to use `feu` are
installed.
To include all the dependencies, you can use the following command:

```shell
pip install feu[all]
```

Please check the [get started page](https://durandtibo.github.io/feu/get_started) to see how to
install only some specific dependencies or other alternatives to install the library.
The following is the corresponding `feu` versions and supported dependencies.

| `feu`   | `packaging`    | `python`      |
|---------|----------------|---------------|
| `main`  | `>=21.0,<25.0` | `>=3.9,<3.13` |
| `0.1.1` | `>=21.0,<25.0` | `>=3.9,<3.13` |
| `0.1.0` | `>=21.0,<25.0` | `>=3.9,<3.13` |
| `0.0.7` | `>=21.0,<25.0` | `>=3.9,<3.13` |
| `0.0.6` | `>=21.0,<25.0` | `>=3.9,<3.13` |
| `0.0.5` | `>=21.0,<25.0` | `>=3.9,<3.13` |

<sup>*</sup> indicates an optional dependency

<details>
    <summary>older versions</summary>

| `feu`   | `packaging`    | `python`      |
|---------|----------------|---------------|
| `0.0.4` | `>=21.0,<25.0` | `>=3.9,<3.13` |
| `0.0.3` | `>=21.0,<25.0` | `>=3.9,<3.13` |
| `0.0.2` | `>=22.0,<24.0` | `>=3.9,<3.13` |
| `0.0.1` | `>=22.0,<23.3` | `>=3.9,<3.13` |

</details>

## Contributing

Please check the instructions in [CONTRIBUTING.md](.github/CONTRIBUTING.md).

## Suggestions and Communication

Everyone is welcome to contribute to the community.
If you have any questions or suggestions, you can
submit [Github Issues](https://github.com/durandtibo/feu/issues).
We will reply to you as soon as possible. Thank you very much.

## API stability

:warning: While `feu` is in development stage, no API is guaranteed to be stable from one
release to the next.
In fact, it is very likely that the API will change multiple times before a stable 1.0.0 release.
In practice, this means that upgrading `feu` to a new version will possibly break any code that
was using the old version of `feu`.

## License

`feu` is licensed under BSD 3-Clause "New" or "Revised" license available in [LICENSE](LICENSE)
file.
