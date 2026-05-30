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


def test_load_config_all_fields():
    """Test load_config with all fields populated in the YAML."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump({
            "linkedin": {
                "headless": True,
                "scroll_delay": 3,
                "max_scroll_attempts": 10,
            },
            "clustering": {
                "method": "kmeans",
                "min_cluster_size": 5,
                "embedding_model": "all-MiniLM-L6-v2",
            },
            "output": {
                "default_format": "json",
                "colors": False,
            },
        }, f)
        f.flush()
        config = load_config(f.name)
    assert config.headless is True
    assert config.scroll_delay == 3
    assert config.max_scroll_attempts == 10
    assert config.clustering_method == "kmeans"
    assert config.min_cluster_size == 5
    assert config.embedding_model == "all-MiniLM-L6-v2"
    assert config.default_format == "json"
    assert config.colors is False


def test_config_post_init_sets_db_path():
    """Test that __post_init__ sets db_path from paths module when db_path is empty."""
    config = Config(db_path="")
    assert config.db_path != ""
    assert "digin.db" in config.db_path


def test_load_config_partial_linkedin():
    """Test load_config where linkedin section is missing some fields (exercises False branches)."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump({
            # Only scroll_delay present (no headless) → False branch at "headless" in linkedin
            # Only max_scroll_attempts present (no scroll_delay in later test)
            "linkedin": {"scroll_delay": 4, "max_scroll_attempts": 5},
            # Only embedding_model present (no min_cluster_size) → False branch at 45
            "clustering": {"embedding_model": "all-MiniLM-L6-v2"},
            "output": {},
        }, f)
        f.flush()
        config = load_config(f.name)
    assert config.headless is False  # default, headless not set
    assert config.scroll_delay == 4
    assert config.max_scroll_attempts == 5
    assert config.embedding_model == "all-MiniLM-L6-v2"
    assert config.min_cluster_size == 3  # default


def test_load_config_no_scroll_delay():
    """Test load_config where linkedin has headless but no scroll_delay (exercises 38->40 False branch)."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump({
            "linkedin": {"headless": True},
        }, f)
        f.flush()
        config = load_config(f.name)
    assert config.headless is True
    assert config.scroll_delay == 2  # default
