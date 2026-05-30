import os
from pathlib import Path


def config_dir() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
    return Path(base) / "digin"


def data_dir() -> Path:
    base = os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))
    return Path(base) / "digin"


def cache_dir() -> Path:
    base = os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))
    return Path(base) / "digin"


def config_path() -> Path:
    return config_dir() / "config.yaml"


def db_path() -> Path:
    return data_dir() / "digin.db"


def browser_data_dir() -> Path:
    return cache_dir() / "browser-data"
