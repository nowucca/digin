# XDG Compliance, Test Coverage, and Skill Install

## 1. XDG Compliance

### Paths Module

New `src/digin/paths.py`:

```python
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
```

### Changes Required

- `config.py`: Default `db_path` uses `paths.db_path()`. Default config file uses `paths.config_path()`.
- `scraper.py`: `BROWSER_DATA_DIR` uses `paths.browser_data_dir()`.
- `cli.py`: `status` command shows resolved paths.

### Backwards Compatibility

If `~/.digin/` exists with data, print a one-time migration hint: "Note: digin now uses XDG directories. Your data is still in ~/.digin/."

No automatic migration — too risky.

## 2. Test Coverage

### Setup

- Add `pytest-cov` dev dependency
- Add coverage config to `pyproject.toml`:

```toml
[tool.coverage.run]
source = ["digin"]
branch = true
omit = ["src/digin/scraper.py"]

[tool.coverage.report]
fail_under = 100
show_missing = true
exclude_lines = ["if __name__", "pragma: no cover"]
```

### What Needs Tests

Audit current coverage, then add tests for uncovered branches:
- `Post.from_dict` with already-parsed (non-string) engagement/links/saved_at
- `Cluster.from_dict` with already-parsed keywords/created_at
- `Config` with all YAML fields populated
- CLI error paths: export with no clusters, show with invalid cluster ID
- `storage.save_posts` return values (new_count, updated_count)
- `paths.py` with and without XDG env vars set

### Excluded

- `scraper.py` — requires live browser, excluded from coverage

## 3. Skill

### SKILL.md Content

Bundled at `src/digin/skills/digin/SKILL.md`. Teaches Claude Code:

- What digin is and when to use it
- Full command reference (sync, cluster, show, export, status)
- Common workflows (first run, re-cluster, export for analysis)
- How to interpret cluster results

### CLI Commands

```
digin skill install    Copy SKILL.md to ~/.claude/skills/digin/
digin skill list       Show install status
```

### Install Logic

1. Find bundled SKILL.md via `importlib.resources` or `__file__` relative path
2. Copy to `~/.claude/skills/digin/SKILL.md`, creating dirs as needed
3. Print confirmation with path
