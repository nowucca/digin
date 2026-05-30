from digin.paths import config_dir, data_dir, cache_dir, config_path, db_path, browser_data_dir
from pathlib import Path


def test_config_dir_default(monkeypatch):
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    result = config_dir()
    assert result == Path.home() / ".config" / "digin"


def test_config_dir_custom(monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", "/tmp/xdg_config")
    assert config_dir() == Path("/tmp/xdg_config/digin")


def test_data_dir_default(monkeypatch):
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    result = data_dir()
    assert result == Path.home() / ".local" / "share" / "digin"


def test_data_dir_custom(monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", "/tmp/xdg_data")
    assert data_dir() == Path("/tmp/xdg_data/digin")


def test_cache_dir_default(monkeypatch):
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    result = cache_dir()
    assert result == Path.home() / ".cache" / "digin"


def test_cache_dir_custom(monkeypatch):
    monkeypatch.setenv("XDG_CACHE_HOME", "/tmp/xdg_cache")
    assert cache_dir() == Path("/tmp/xdg_cache/digin")


def test_config_path(monkeypatch):
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    assert config_path().name == "config.yaml"


def test_db_path(monkeypatch):
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    assert db_path().name == "digin.db"


def test_browser_data_dir(monkeypatch):
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    assert browser_data_dir().name == "browser-data"
