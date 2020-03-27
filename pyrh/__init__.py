"""Export pyrh sub classes."""

from pyrh import exceptions
from pyrh.robinhood import Robinhood
from pyrh.sessionmanager import SessionManager, dump_session, load_session


def _get_version() -> str:
    from pathlib import Path
    from tomlkit import parse

    pyproject_path = Path(__file__).resolve().parent.joinpath("../pyproject.toml")
    with open(pyproject_path) as file:
        pyproject = parse(file.read())

    return str(pyproject["tool"]["poetry"]["version"])


__version__ = _get_version()
__all__ = [
    "__version__",
    "Robinhood",
    "SessionManager",
    "load_session",
    "dump_session",
    "exceptions",
]

del _get_version
