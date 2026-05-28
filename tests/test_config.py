import tempfile
from pathlib import Path
import yaml
from digin.config import Config, load_config

def test_default_config():
    config = Config()
    assert config.headless is False
    assert config.scroll_delay == 2
    assert config.clustering_method == "kmeans"
    assert config.min_cluster_size == 3
    assert config.default_format == "table"

def test_load_config_from_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump({
            "linkedin": {"headless": True, "scroll_delay": 5},
            "clustering": {"min_cluster_size": 10},
        }, f)
        f.flush()
        config = load_config(f.name)
    assert config.headless is True
    assert config.scroll_delay == 5
    assert config.min_cluster_size == 10
    assert config.clustering_method == "kmeans"

def test_load_config_missing_file():
    config = load_config("/nonexistent/path/config.yaml")
    assert config.headless is False

def test_config_db_path():
    config = Config()
    assert "digin.db" in config.db_path
