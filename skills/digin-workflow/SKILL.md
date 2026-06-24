---
name: digin-workflow
description: Use when the user wants to work with their LinkedIn saved posts — guides them through setup, syncing, clustering, visualization, and export. Activates on mentions of LinkedIn saved posts, bookmarks, professional content organization, or topic clustering.
---

# DigIn Workflow

Guide the user through extracting knowledge from their LinkedIn saved posts.

## Prerequisites Check

Before starting, verify the environment:

```bash
# Check if digin is installed
uv run digin --version

# If not installed yet:
uv sync
uv run playwright install chromium
```

If `uv sync` fails, the user needs to clone the repo first. If `playwright install` fails, they may need system dependencies — check the Playwright docs for their OS.

## Workflow Steps

### Step 1: Sync

Check if the user already has posts:

```bash
digin status
```

If no posts, guide them through first sync:

```bash
# First time: opens a browser window for LinkedIn login
digin sync

# After first login, sessions persist:
digin sync --headless
digin sync --headless -n 100    # limit to 100 posts
```

**First sync notes:**
- A Chrome window opens to LinkedIn's login page
- User logs in manually (handles MFA, CAPTCHAs)
- Once logged in, the tool takes over and scrolls through saved posts
- Each post is enriched by visiting its detail page for full content and links
- Posts already in the database are skipped on re-sync

**If sync fails:**
- "Error during scraping" → run `uv run playwright install chromium`
- Challenge/CAPTCHA screen → close and retry, LinkedIn sometimes blocks automated browsers on first attempt
- Timeout → increase scroll_delay in config

### Step 2: Cluster

```bash
# Claude-powered clustering (default, needs ANTHROPIC_API_KEY)
digin cluster

# Local ML fallback (offline, no API key needed)
digin cluster --local

# Local with specific cluster count
digin cluster -k 5
```

Default uses Claude API for intelligent topic detection with meaningful names.
Requires `ANTHROPIC_API_KEY` env var — falls back to local K-means if not set.
Needs at least 6 posts. More posts = better clusters.

### Step 3: Explore Results

```bash
# Summary table
digin show

# Drill into a specific cluster
digin show -c 1

# As JSON for programmatic use
digin show -f json
```

### Step 4: Visualize

```bash
# Opens interactive HTML in browser
digin viz

# Save to file without opening
digin viz -o clusters.html --no-open
```

Three views available:
- **Treemap** — proportional blocks, click to drill down
- **Scatter** — UMAP 2D projection showing topic proximity
- **Network** — card layout grouped by cluster, click cards to open posts

### Step 5: Export

```bash
digin export -f json                   # JSON to stdout
digin export -f csv -o posts.csv       # Spreadsheet-ready
digin export -f md -o research.md      # Human-readable report
digin export -f json -c 2              # Just cluster 2
```

## Iterative Refinement

After reviewing results, the user may want to:

- **More posts**: `digin sync --headless` to fetch additional posts, then `digin cluster` again
- **Different K**: `digin cluster -k 8` to try more granular clusters
- **Focus on one topic**: `digin export -f md -c 3` to deep-dive a specific cluster

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `playwright` not found | `uv run playwright install chromium` |
| LinkedIn challenge screen | Close browser, wait a few minutes, retry |
| "Need at least 6 posts" | `digin sync` to fetch more posts |
| Clustering is slow first time | Downloading 80MB embedding model — one-time only |
| "Network is unreachable" during cluster | Normal — clustering works offline after first model download |
| Posts have empty content | Some LinkedIn post types (reshares, polls) have minimal extractable text |

## Data Locations

```bash
digin status    # Shows all paths
```

- Config: `$XDG_CONFIG_HOME/digin/config.yaml` (usually `~/.config/digin/`)
- Database: `$XDG_DATA_HOME/digin/digin.db` (usually `~/.local/share/digin/`)
- Browser: `$XDG_CACHE_HOME/digin/browser-data/` (usually `~/.cache/digin/`)
