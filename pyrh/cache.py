"""Local machine data cache"""

from pathlib import Path


def create_dir(directory):
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def create_file(path):
    path.touch(exist_ok=True)
    return path


CACHE_ROOT = create_dir(Path("~/.robinhood").expanduser())
