# Migration to 0.9

`feu` 0.9 is a breaking release (`feu` is `0.x`). The names that other repositories depend on are
kept: `from feu import compare_version`, `feu.imports.is_package_available`, the `feu.testing`
marks, `feu.local_git.get_last_version_tag_name`, and the short and long names of the CLI options
`-n`, `-v`, `-e`, `-i`, `-a`, `-p`.

## Behaviour changes

- **A target without `os` and `arch` is no longer a no-op.** `find_closest_version("numpy", "2.3.0",
Target("3.9"))` returned `"2.3.0"`; it now returns `"2.0.2"` (the union of the platforms).
  `install_package_closest_version` uses the full current target, and the examples of the README
  return what they document.
- **A version is a request.** `""`, `None` and a wildcard (`"2.*"`) are accepted wherever a version
  is, checked against the registry and resolved. A wildcard is no longer skipped by the
  compatibility check; a wildcard with no match raises `UnsupportedVersionError`.
- **Package names are canonical** (PEP 503) in the registries, the resolver registry, the
  `pyproject` reader and the PyPI functions. The `sklearn` resolver key is gone.
- **`find-closest-version`** prints only the version; an unsupported request exits `1` with the
  message on standard error (it printed `None` and exited `0`). `check-valid-version` exits `1`
  when the version is not valid. An invalid argument exits `2`.
- **`pip` installs into the interpreter that runs `feu`** (`sys.executable -m pip`), and a missing
  `pip` or `uv` raises `RuntimeError` before any command.
- **Wheels**: `macosx_*_universal2` wheels and compressed tag sets count for every platform they
  support. The shipped data changed for 10 macOS targets.

## Old to new

| Old                                                                                                                                 | New                                                                                                                                                          |
| ----------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `feu.compat.get_default_registry`                                                                                                   | `get_default_compat_registry`                                                                                                                                |
| `InstallerRegistry.add_installer(...)`, `DependencyResolverRegistry.add_resolver(PackageSpec, ...)`                                 | `register_installer(name, ...)`, `register_resolver(name, ...)`                                                                                              |
| `BaseInstaller`, `BasePipInstaller`, `PipxInstaller`, `BaseDependencyResolver`, the seven `*DependencyResolver`                     | `Installer`, `PipInstaller`, `UvInstaller`; a resolver is a function                                                                                         |
| `InstallerSpec("pip", arguments="-U")` (a string kept as is)                                                                        | the arguments are a tuple (`("-U",)`); a string is split once with `shlex.split`                                                                             |
| `feu.utils.installer.InstallerSpec`                                                                                                 | `feu.install.InstallerSpec`                                                                                                                                  |
| `run_bash_command("pip install x")`                                                                                                 | `run_command(["pip", "install", "x"])`                                                                                                                       |
| `PackageDependency`, `extract_package_name`, `extract_package_extras`, `generate_extras_string`                                     | `packaging.requirements.Requirement`                                                                                                                         |
| `BaseCompatDiscoverer`, `CompatDiscoverer`, `*CompatDiscoverer`, `CompatDiscovererRegistry`, `register_discoverers`                 | `discover_compat_targets(..., companion=...)`, which returns a `Discovery`                                                                                   |
| `feu.compat.discovered`, `feu.compat.packages.get_package_names`                                                                    | `feu/compat/data/*.json`, `CompatRegistry.packages()`                                                                                                        |
| `feu.compat.matrix`                                                                                                                 | `feu.compat.target` (`DEFAULT_TARGETS`), `feu.compat.discover` (`is_compatible`), `feu.compat.display` (`show_compat_targets`)                               |
| `WheelTags`, `parse_wheel_filename` returning a list                                                                                | `WheelTag`, a tuple                                                                                                                                          |
| `feu.version.normalize_package_name`                                                                                                | `packaging.utils.canonicalize_name`                                                                                                                          |
| `fetch_latest_{major,minor}_versions`, `fetch_sampled_latest_minor_versions`                                                        | `fetch_latest_versions(group=...)`, `fetch_package_versions`                                                                                                 |
| `fetch_pypi_versions(reverse=True)`                                                                                                 | `fetch_pypi_versions(...)[::-1]`                                                                                                                             |
| `feu.version.get_python_major_minor`                                                                                                | `feu.utils.platform.get_python_version`                                                                                                                      |
| `is_wildcard_version`, a wildcard skipped by the compatibility check, `RuntimeError` for no version                                 | `parse_version_request`; a wildcard, `""` and `None` are resolved and checked like a version                                                                 |
| `resolve_target(python_version, free_threaded, os, arch)`; CLI `--os`, `--arch`; `--free-threaded true`                             | `resolve_target(python_version=None, *, free_threaded=None)` (the platform is the current one); no `--os`/`--arch`; `--free-threaded` / `--no-free-threaded` |
| `feu.imports.{click,git,requests,rich,urllib3}`; `decorator_package_available`; `raise_*_missing_error`; `@lru_cache` on the checks | `feu.imports.optional`, `package` (a port of `coola.utils.imports`), `availability_cache`, `check_*`, `MissingPackageError`                                  |
| `feu.imports.urllib3`, `check_urllib3`, `is_urllib3_available`, the `urllib3` mark of `feu.testing`                                 | deleted (`check_requests` covers it); the `feu[requests]` extra is unchanged                                                                                 |
| `fetch_data(url, timeout, **kwargs)`                                                                                                | `fetch_data(url, *, timeout, headers, params, accept)`                                                                                                       |
| `get_last_tag_name(raise_error)`                                                                                                    | `get_last_tag_name(*, raise_error=True)`                                                                                                                     |
| `python dev/generate_discovered_compat.py`                                                                                          | `python dev/generate_compat_data.py [--new] [package ...]`                                                                                                   |

## Scripts that copy `dev/generate_versions.py`

The script is replaced by one CLI call:

```shell
feu package-versions --pyproject pyproject.toml --output dev/config/package_versions.json
```

`fetch_latest_{major,minor}_versions_map`, `read_pyproject_*`, `partition_package_bounds`,
`feu.utils.io.save_json` and `feu.utils.mapping.sort_by_keys` are kept until the repositories that
copy the script are migrated.

## Examples

```pycon
>>> from feu.compat import Target, find_closest_version
>>> find_closest_version("numpy", "2.3.0", Target("3.9"))
'2.0.2'

```

```pycon
>>> from feu.install import InstallerSpec
>>> InstallerSpec("pip", arguments="-U --pre")
InstallerSpec(name='pip', arguments=('-U', '--pre'))

```
