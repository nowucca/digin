# DigIn

Scrape, cluster, and visualize your LinkedIn saved posts.

DigIn transforms your LinkedIn saved posts from a disorganized pile into clustered, searchable, exportable knowledge. It uses ML-powered topic detection to automatically group related posts together.

## Features

- **Sync** saved posts from LinkedIn via browser automation
- **Cluster** posts by topic using sentence embeddings + K-means
- **Visualize** clusters with interactive treemap, scatter, and network views
- **Export** to CSV, JSON, or Markdown
- **Resumable** — only fetches new posts on re-sync
- **Headless** — runs without a visible browser after first login
- **Offline clustering** — no network needed after initial model download

## Install

```bash
# Clone and install
git clone https://github.com/nowucca/digin.git
cd digin
uv sync
uv run playwright install chromium
```

## Quick Start

```bash
# First run: opens browser for LinkedIn login
digin sync

# Cluster posts by topic
digin cluster

# View results
digin show                    # Summary table
digin show -c 1               # Posts in cluster 1

# Visualize
digin viz                     # Interactive HTML visualization

# Export
digin export -f json          # JSON to stdout
digin export -f csv -o data.csv
digin export -f md -o research.md
```

## Commands

| Command | Description |
|---------|-------------|
| `digin sync` | Fetch saved posts from LinkedIn |
| `digin cluster` | Group posts into topic clusters |
| `digin show` | Display cluster summary or detail |
| `digin viz` | Interactive HTML visualization |
| `digin export` | Export to CSV, JSON, or Markdown |
| `digin status` | Show database and cluster status |
| `digin skill install` | Install Claude Code skill |

## How It Works

1. **Sync**: Playwright launches Chrome, you log in to LinkedIn (first time only), and DigIn scrolls through your saved posts extracting content, authors, and links. Sessions persist — subsequent syncs can run headless.

2. **Cluster**: Posts are converted to 384-dimensional vectors using [sentence-transformers](https://www.sbert.net/) (`all-MiniLM-L6-v2`), then grouped via K-means. The optimal number of clusters is auto-detected using silhouette scoring. Each cluster gets TF-IDF keywords.

3. **Visualize**: Three interactive views in a single HTML page — treemap (proportional blocks), scatter (UMAP 2D projection), and network (card layout grouped by topic).

## Configuration

Optional config file at `$XDG_CONFIG_HOME/digin/config.yaml`:

```yaml
linkedin:
  headless: false
  scroll_delay: 2

clustering:
  method: kmeans
  min_cluster_size: 3

output:
  default_format: table
```

## Data Storage

Uses XDG-compliant directories:

| What | Location |
|------|----------|
| Config | `~/.config/digin/config.yaml` |
| Database | `~/.local/share/digin/digin.db` |
| Browser cache | `~/.cache/digin/browser-data/` |

## Claude Code Integration

DigIn ships with a skill for Claude Code:

```bash
digin skill install    # Install to ~/.claude/skills/digin/
```

Once installed, Claude Code can use `digin` commands to help you analyze your saved posts.

## Development

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=digin --cov-branch

# Run a specific test
uv run pytest tests/test_cli.py::test_full_pipeline -v
```

## License

MIT
