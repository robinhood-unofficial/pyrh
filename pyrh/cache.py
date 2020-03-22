"""Project config/cache files."""

from pathlib import Path


CACHE_ROOT: Path = Path("~/.robinhood").expanduser()
"""The root directory where cache and config files are stores.

Creates the directory on first call.
"""
CACHE_ROOT.mkdir(parents=True, exist_ok=True)
