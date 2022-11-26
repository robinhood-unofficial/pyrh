"""Project config/cache files."""

from json import JSONDecodeError
from pathlib import Path
from typing import Optional, Union, cast

from pyrh.exceptions import InvalidCacheFile
from pyrh.robinhood import Robinhood, RobinhoodSchema

CACHE_ROOT: Path = Path("~/.robinhood").expanduser()
"""The root directory where cache and config files are stores.

Creates the directory on import.
"""
CACHE_ROOT.mkdir(parents=True, exist_ok=True)

CACHE_LOGIN: Path = CACHE_ROOT.joinpath("login.json")
"""Path to login.json config file.

Creates the file on import.
"""
CACHE_LOGIN.touch(exist_ok=True)

# TODO: Fix darglint issue (remove from flake8 ignore)
# https://github.com/terrencepreilly/darglint/issues/81


def dump_session(robinhood: Robinhood, path: Optional[Union[Path, str]] = None) -> None:
    """Save the current session parameters to a json file.

    Note:
        This function defaults to caching this information to
        ~/.robinhood/login.json

    Args:
        robinhood: A Robinhood instance.
        path: The location to save the file and its name.

    """
    path = CACHE_LOGIN if path is None else path
    json_str = RobinhoodSchema().dumps(robinhood, indent=4)

    with open(path, "w+") as file:
        file.write(json_str)


def load_session(path: Optional[Union[Path, str]] = None) -> Robinhood:
    """Load cached session parameters from a json file.

    Note:
        This function defaults to caching this information to
        ~/.robinhood/login.json

    Args:
        path: The location and file name to load from.

    Returns:
        A configured instance of SessionManager.

    Raises:
        InvalidCacheFile: If the cache file cannot be decoded or does not exist

    """
    path = path or CACHE_LOGIN
    try:
        with open(path) as file:
            return cast(Robinhood, RobinhoodSchema().loads(file.read()))
    except (JSONDecodeError, FileNotFoundError):
        raise InvalidCacheFile(
            f"The cache file at {path} is invalid or does not exist."
        )
