# Properties

These are the rules `feu` follows. Each one is enforced in one place, not by the discipline of each
function, and says how you can rely on it.

| #   | Property                                  | What you can rely on                                                                                                                                                                                                                       |
| --- | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | **Lightweight**                           | The only required dependency is `packaging`. `import feu`, `import feu.compat` and `import feu.install` import no optional library, read no file other than code, and do no network call.                                                  |
| 2   | **Explicit optional dependencies**        | A feature that needs `click`, `gitpython`, `requests` or `rich` checks it first. A missing package raises `MissingPackageError` (a `ModuleNotFoundError` and a `RuntimeError`) whose message gives the `pip` and `uv pip` command.          |
| 3   | **Target-aware**                          | A compatibility answer is a function of `(package, version, Target)`. Code that acts on the current environment uses the full current target (`resolve_target()`).                                                                          |
| 4   | **No silent no-op**                       | Every field of the target is used or the call fails. A field left to `None` means "any platform". An unknown package is permissive and can be detected with `registry.has_package`.                                                        |
| 5   | **Data-driven and reproducible**          | The built-in constraints are generated from the wheels published on PyPI by one command (`dev/generate_compat_data.py`), sorted and dated. No constraint is written by hand.                                                               |
| 6   | **Extensible by registration**            | A package constraint, an installer or a dependency resolver is added by registering one value in a registry instance. No subclassing is needed to add data, and no registry is process-global class state.                                 |
| 7   | **Standards compliant**                   | Package names are canonicalised once (PEP 503), versions are `packaging` versions (PEP 440), requirements are `packaging` requirements (PEP 508) and wheel names are parsed by `packaging`.                                                |
| 8   | **No shell, no string-built command**     | An external command is an argument vector. `pip` runs as `sys.executable -m pip`, so it installs into the interpreter that runs `feu`. The command is logged before it runs.                                                              |
| 9   | **Fresh and immutable**                   | Availability checks are cached and `clear_availability_caches()` resets them (`install_package` calls it after a success). The PyPI and GitHub values that are cached are immutable, so no caller can corrupt a cache.                    |
| 10  | **Deterministic order**                   | Versions are ordered by PEP 440, never as strings. A mapping that is returned or written is sorted. The generated data has a date and no timestamp.                                                                                        |
| 11  | **A thin CLI**                            | The CLI is the same API behind `click`. Standard output holds only the answer (it is used in `$(...)`), logs go to standard error, the exit status carries the result (`0` ok, `1` negative answer, `2` usage error).                      |
| 12  | **Strict, typed, documented**             | Options are keyword-only. Invalid input raises `ValueError` or `TypeError` with an explicit message. Every public function has a doctest, and the examples of this guide are doctests too.                                                 |
| 13  | **Layered**                               | The imports go one way: `imports`, `utils`, `version`, `compat`, `install`, `cli`. `imports` imports nothing from `feu`. A test checks it.                                                                                                 |
| 14  | **Cross-platform, Python 3.11 and newer** | Linux, macOS and Windows behave the same: there is no `shlex` rule that depends on `os.name` and no `PATH` lookup of `pip`.                                                                                                                |
| 15  | **A version is a request**                | Wherever a function takes the version of a package to install or to validate, it accepts an exact version (`2.4.0`), a wildcard (`2.4.*`) or an empty string / `None` (the latest). A request with no compatible version raises `UnsupportedVersionError`, never crashes. |

## A few of them, as examples

The target is used entirely (property 4), and the answer for a target without a platform is the
union over the platforms:

```pycon
>>> from feu.compat import Target, find_closest_version
>>> find_closest_version("numpy", "99.0.0", Target("3.9"))
'2.0.2'

```

Package names are canonical (property 7), so the spelling does not matter:

```pycon
>>> from feu.compat import get_default_compat_registry
>>> registry = get_default_compat_registry()
>>> registry.has_package("Scikit_Learn")
True

```

A version request is parsed by one parser (property 15):

```pycon
>>> from feu.version import parse_version_request
>>> [str(parse_version_request(text)) for text in (None, "", "2.4.0", "2.*")]
['', '', '2.4.0', '2.*']

```

The orders are PEP 440 orders (property 10):

```pycon
>>> from feu.version import sort_versions
>>> sort_versions(["1.10.0", "1.9.0", "1.2.0"])
['1.2.0', '1.9.0', '1.10.0']

```

An external command is an argument vector built from the interpreter (property 8):

```pycon
>>> import sys
>>> from feu.install import PipInstaller
>>> PipInstaller.prefix == (sys.executable, "-m", "pip", "install")
True

```
