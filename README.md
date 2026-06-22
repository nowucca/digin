# DigIn

Scrape, cluster, and visualize your LinkedIn saved posts.

DigIn transforms your LinkedIn saved posts from a disorganized pile into clustered, searchable, exportable knowledge. It uses ML-powered topic detection to automatically group related posts together.

## Features

- **Sync** saved posts from LinkedIn via browser automation
- **Cluster** posts by topic using sentence embeddings + K-means
- **Visualize** clusters with interactive treemap, scatter, and network views
- **Export** to CSV, JSON, or Markdown
- **Agent-friendly** — `--json` flag on every command, `schema` for tool discovery
- **Resumable** — only fetches new posts on re-sync
- **Headless** — runs without a visible browser after first login
- **Offline clustering** — no network needed after initial model download
- **Claude Code plugin** — clone the repo and get a workflow skill automatically

## Install

```bash
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
| `digin schema` | Output full command schema as JSON |
| `digin skill install` | Install Claude Code skill |

## Agent Integration

DigIn is designed to be used by AI agents. Every command supports a `--json` flag for structured output:

```bash
digin --json status          # JSON status with paths, counts, clusters
digin --json show            # JSON cluster summary
digin --json show -c 1       # JSON posts in cluster 1
digin --json cluster         # JSON cluster results
```

Agents can discover all commands programmatically:

```bash
digin schema                 # Full JSON: commands, options, types, workflow
digin schema | jq '.commands[].name'
```

### Claude Code Plugin

This repo is a Claude Code plugin. After cloning, the `digin-workflow` skill is automatically available and guides you through the full workflow. You can also install the skill globally:

```bash
digin skill install          # Install to ~/.claude/skills/digin/
```

## How It Works

1. **Sync**: Playwright launches Chrome, you log in to LinkedIn (first time only), and DigIn scrolls through your saved posts extracting content, authors, and links. Each post is enriched by visiting its detail page for full text and external URLs. Sessions persist — subsequent syncs can run headless.

2. **Cluster**: Posts are converted to 384-dimensional vectors using [sentence-transformers](https://www.sbert.net/) (`all-MiniLM-L6-v2`), then grouped via K-means. The optimal number of clusters is auto-detected using silhouette scoring. Each cluster gets TF-IDF keywords.

3. **Visualize**: Three interactive views in a single HTML page:
   - **Treemap** — proportional blocks sized by cluster, click to drill down
   - **Scatter** — UMAP 2D projection showing topic proximity
   - **Network** — card layout grouped by cluster, click to open posts

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

## Development

```bash
# Run tests (74 tests, 100% coverage excluding scraper)
uv run pytest

# Run with coverage
uv run pytest --cov=digin --cov-branch

# Run a specific test
uv run pytest tests/test_cli.py::test_full_pipeline -v
```

## License

MIT
