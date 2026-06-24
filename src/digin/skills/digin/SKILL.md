---
name: digin
description: Use when working with LinkedIn saved posts — syncing, clustering, analyzing, or exporting professional content collections.
---

# DigIn — LinkedIn Saved Posts Tool

CLI tool for scraping, clustering, and analyzing LinkedIn saved posts.

## When to Use

- User mentions LinkedIn saved posts, bookmarks, or saved content
- User wants to organize or analyze professional content they've collected
- User needs to export LinkedIn data for analysis
- User asks about topic clusters in their saved content

## Commands

### Sync posts from LinkedIn

```bash
digin sync                # Sync all saved posts (opens browser for login)
digin sync -n 50          # Sync up to 50 posts
digin sync --headless     # Run without visible browser (after first login)
```

First run opens a browser for manual LinkedIn login. Sessions persist — subsequent runs can use `--headless`.

### Cluster posts by topic

```bash
digin cluster             # Claude-powered clustering (default)
digin cluster --local     # Local K-means clustering (offline)
digin cluster -k 5        # Force 5 clusters (local mode)
```

Default uses Claude API for intelligent topic names. Requires `ANTHROPIC_API_KEY`. Falls back to local K-means if no key is set. Requires at least 6 posts.

### View results

```bash
digin show                # Summary table of all clusters
digin show -c 1           # Posts in cluster 1
digin show -f json        # Output as JSON
```

### Export

```bash
digin export -f json                # JSON to stdout
digin export -f csv -o posts.csv    # CSV to file
digin export -f md -o research.md   # Markdown to file
digin export -f json -c 2           # Export only cluster 2
```

### Check status

```bash
digin status              # Show DB path, post count, cluster summary
```

## Typical Workflow

```bash
digin sync --headless     # Fetch latest saved posts
digin cluster             # Group by topic
digin show                # Review clusters
digin export -f md -o weekly-research.md  # Export for reading
```

## Data Location

Uses XDG directories:
- Config: `$XDG_CONFIG_HOME/digin/config.yaml`
- Database: `$XDG_DATA_HOME/digin/digin.db`
- Browser cache: `$XDG_CACHE_HOME/digin/browser-data/`

## Configuration

Optional `config.yaml`:

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
