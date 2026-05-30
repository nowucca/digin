from dataclasses import dataclass
from pathlib import Path
import yaml

from digin.paths import db_path as default_db_path, config_path as default_config_path


@dataclass
class Config:
    headless: bool = False
    scroll_delay: int = 2
    max_scroll_attempts: int = 3
    clustering_method: str = "kmeans"
    min_cluster_size: int = 3
    embedding_model: str = "all-MiniLM-L6-v2"
    default_format: str = "table"
    colors: bool = True
    db_path: str = ""

    def __post_init__(self):
        if not self.db_path:
            self.db_path = str(default_db_path())


def load_config(config_path_arg: str | None = None) -> Config:
    if config_path_arg is None:
        config_path_arg = str(default_config_path())
    config_path = config_path_arg
    path = Path(config_path).expanduser()
    if not path.exists():
        return Config()
    with open(path) as f:
        raw = yaml.safe_load(f) or {}
    kwargs = {}
    linkedin = raw.get("linkedin", {})
    if "headless" in linkedin:
        kwargs["headless"] = linkedin["headless"]
    if "scroll_delay" in linkedin:
        kwargs["scroll_delay"] = linkedin["scroll_delay"]
    if "max_scroll_attempts" in linkedin:
        kwargs["max_scroll_attempts"] = linkedin["max_scroll_attempts"]
    clustering = raw.get("clustering", {})
    if "method" in clustering:
        kwargs["clustering_method"] = clustering["method"]
    if "min_cluster_size" in clustering:
        kwargs["min_cluster_size"] = clustering["min_cluster_size"]
    if "embedding_model" in clustering:
        kwargs["embedding_model"] = clustering["embedding_model"]
    output = raw.get("output", {})
    if "default_format" in output:
        kwargs["default_format"] = output["default_format"]
    if "colors" in output:
        kwargs["colors"] = output["colors"]
    return Config(**kwargs)
