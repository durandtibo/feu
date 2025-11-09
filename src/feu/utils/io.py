r"""Contain utility functions to export data to JSON format."""

from __future__ import annotations

__all__ = ["generate_unique_tmp_path", "load_json", "save_json"]

import json
import uuid
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    r"""Load the data from a given JSON file.

    Args:
        path: The path to the JSON file.

    Returns:
        The data from the JSON file.

    Example usage:

    ```pycon

    >>> import tempfile
    >>> from pathlib import Path
    >>> from feu.utils.io import save_json, load_json
    >>> with tempfile.TemporaryDirectory() as tmpdir:
    ...     path = Path(tmpdir).joinpath("data.json")
    ...     save_json({"key1": [1, 2, 3], "key2": "abc"}, path)
    ...     data = load_json(path)
    ...     data
    ...
    {'key1': [1, 2, 3], 'key2': 'abc'}

    ```
    """
    with Path.open(path, mode="rb") as file:
        return json.load(file)


def save_json(to_save: Any, path: Path, *, exist_ok: bool = False) -> None:
    r"""Save the given data in a JSON file.

    Args:
        to_save: The data to write in a JSON file.
        path: The path where to write the JSON file.
        exist_ok: If ``exist_ok`` is ``False`` (the default),
            ``FileExistsError`` is raised if the target file
            already exists. If ``exist_ok`` is ``True``,
            ``FileExistsError`` will not be raised unless the
            given path already exists in the file system and is
            not a file.

    Raises:
        FileExistsError: if the file already exists.

    Example usage:

    ```pycon

    >>> import tempfile
    >>> from pathlib import Path
    >>> from feu.utils.io import save_json
    >>> with tempfile.TemporaryDirectory() as tmpdir:
    ...     path = Path(tmpdir).joinpath("data.json")
    ...     save_json({"key1": [1, 2, 3], "key2": "abc"}, path)
    ...     data = load_json(path)
    ...     data
    ...
    {'key1': [1, 2, 3], 'key2': 'abc'}

    ```
    """
    if path.is_dir():
        msg = f"path ({path}) is a directory"
        raise IsADirectoryError(msg)
    if path.is_file() and not exist_ok:
        msg = (
            f"path ({path}) already exists. "
            f"Please use `exist_ok=True` if you want to overwrite the setter for this name"
        )
        raise FileExistsError(msg)
    path.parent.mkdir(exist_ok=True, parents=True)

    # Save to tmp, then commit by moving the file in case the job gets
    # interrupted while writing the file
    tmp_path = generate_unique_tmp_path(path)
    with Path.open(tmp_path, "w") as file:
        json.dump(to_save, file, sort_keys=False)
        file.write("\n")
    tmp_path.rename(path)


def generate_unique_tmp_path(path: Path) -> Path:
    r"""Return a unique temporary path given a path.

    This function updates the name to add a UUID.

    Args:
        path: The input path.

    Returns:
        The unique name.

    Example usage:

    ```pycon

    >>> import tempfile
    >>> from pathlib import Path
    >>> from feu.utils.io import generate_unique_tmp_path
    >>> with tempfile.TemporaryDirectory() as tmpdir:
    ...     path = generate_unique_tmp_path(Path(tmpdir).joinpath("data.json"))
    ...     path
    ...
    PosixPath('/.../data-....json')

    ```
    """
    h = uuid.uuid4().hex
    extension = "".join(path.suffixes)[1:]
    if extension:
        extension = "." + extension
        stem = path.name[: -len(extension)]
    else:
        stem = path.name
    return path.with_name(f"{stem}-{h}{extension}")
