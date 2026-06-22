# DigIn MVP Design Spec

## Overview

DigIn is a CLI tool that scrapes LinkedIn saved posts, clusters them by topic using ML, and presents organized results. This spec covers the MVP: `sync`, `cluster`, `show`, and `export` commands. The research/explore pipeline is deferred to a later phase.

## Architecture

Monolith package with one module per concern. No pipeline abstraction — just direct function calls between modules.

```
src/digin/
    __init__.py
    cli.py          # Click command group
    scraper.py      # Playwright browser automation
    models.py       # Post and Cluster dataclasses
    storage.py      # SQLite persistence
    clustering.py   # Embeddings + K-means
    config.py       # YAML config loading
```

### Data Flow

```
sync:    Playwright → List[Post] → SQLite
cluster: SQLite → Posts → embeddings → K-means → Clusters → SQLite
show:    SQLite → Clusters/Posts → formatted terminal output
export:  SQLite → Clusters/Posts → CSV/JSON/Markdown file
```

### Dependencies

- **playwright** — browser automation (replaces Selenium from prototype)
- **click** — CLI framework
- **sentence-transformers** — text embeddings (`all-MiniLM-L6-v2`)
- **scikit-learn** — K-means clustering, TF-IDF for keyword extraction, silhouette scoring
- **pandas** — data manipulation for export
- **pyyaml** — config file parsing
- **rich** — terminal table formatting (optional, can start with plain click.echo)

## Data Models

### Post

```python
@dataclass
class Post:
    id: str                    # LinkedIn URN or hash of URL
    url: str                   # LinkedIn post URL
    author: str                # Author display name
    author_profile: str        # Author profile URL
    content: str               # Post text content
    post_type: str             # "text", "article", "video", "image"
    saved_at: datetime         # When we scraped it
    engagement: dict           # {"likes": int, "comments": int}
    links: list[str]           # URLs found in post content
    cluster_id: int | None     # Assigned after clustering
```

### Cluster

```python
@dataclass
class Cluster:
    id: int                    # Auto-increment ID
    keywords: list[str]        # Top N representative keywords
    summary: str               # Auto-generated label from keywords
    post_count: int            # Number of posts in cluster
    created_at: datetime       # When clustering was run
```

## CLI Commands

### Global Options

```
digin [--config PATH] [--verbose] [--quiet] [--version] [--help]
```

### digin sync

Scrape saved posts from LinkedIn into local storage.

```
digin sync [--num N] [--headless]
```

- `--num N` — limit to N most recent posts (default: all)
- `--headless` — run browser without visible window (default: false, because user needs to log in)

**Behavior:**
1. Launch Chromium via Playwright
2. Navigate to `https://www.linkedin.com/login`
3. Print: "Please log in to LinkedIn. The tool will continue automatically once you reach your saved posts."
4. Poll `page.url` every 2 seconds until URL contains `/my-items/saved-posts/` or user navigates there
5. Once on saved posts page, begin scraping
6. Infinite scroll: scroll to bottom, wait for new content, repeat until no new posts for 3 consecutive attempts
7. Extract post data from each post element
8. Upsert posts into SQLite (skip duplicates by ID)
9. Print summary: "Synced {N} posts ({M} new, {K} updated)"

**Login detection:** After navigating to the login page, the tool watches for URL changes. Once the URL no longer contains `/login`, navigate to the saved posts page automatically.

### digin cluster

Group stored posts into topic clusters.

```
digin cluster [--method kmeans] [--num-clusters K] [--min-size N]
```

- `--method` — clustering algorithm (default: kmeans; hdbscan deferred)
- `--num-clusters K` — number of clusters (default: auto-detect)
- `--min-size N` — minimum posts per cluster (default: 3)

**Behavior:**
1. Load all posts from SQLite
2. Validate minimum post count (need at least 6 posts to cluster meaningfully)
3. Generate embeddings using sentence-transformers (`all-MiniLM-L6-v2`)
4. If K not specified: test K=2 through K=floor(sqrt(n)), pick K with best silhouette score
5. Run K-means clustering
6. Extract top 5 keywords per cluster using TF-IDF on cluster members
7. Generate cluster summary from top keywords (e.g., "AI & ML" from ["llm", "agents", "fine-tuning", "gpt", "ml"])
8. Clear previous clusters, save new clusters and update post cluster_id in SQLite
9. Print summary table of clusters

### digin show

Display posts and clustering results.

```
digin show [--cluster N] [--format table|json]
```

- `--cluster N` — show posts in specific cluster (default: show summary)
- `--format` — output format (default: table)

**Without --cluster (summary view):**
```
  #  Cluster          Posts  Keywords
  1  AI & ML             12  llm, agents, fine-tuning
  2  Leadership           8  management, culture, hiring
  3  DevTools             6  cli, dx, tooling
```

**With --cluster N (detail view):**
```
  Cluster: AI & ML (12 posts)
  Keywords: llm, agents, fine-tuning, gpt, ml

  1. Sam Altman — "The future of AI agents is..."
     linkedin.com/feed/update/urn:li:activity:123
     Likes: 2,431  Comments: 312

  2. Andrej Karpathy — "Fine-tuning is underrated..."
     linkedin.com/feed/update/urn:li:activity:456
     Likes: 1,892  Comments: 198
  ...
```

### digin export

Export clusters and posts to file.

```
digin export --format csv|json|md [--output FILE] [--cluster N]
```

- `--format` — required, export format
- `--output FILE` — output file path (default: stdout)
- `--cluster N` — export specific cluster only (default: all)

**CSV format:** flat rows with columns: cluster_id, cluster_keywords, post_id, author, content, post_type, engagement_likes, engagement_comments, url

**JSON format:** nested structure with clusters containing their posts

**Markdown format:** headers per cluster, bulleted post list with content preview and metadata

## Scraper Detail

### Post Element Extraction

Based on the prototype's selector research, extract from each post element:

| Field | Extraction Strategy |
|-------|-------------------|
| id | `data-urn` or `data-id` attribute containing `urn:li:activity:*` |
| url | Construct from URN: `linkedin.com/feed/update/{urn}` |
| author | `.feed-shared-actor__name` or `.update-components-actor__name` |
| author_profile | `a` tag href within actor element |
| content | `.feed-shared-text` or `.update-components-text` |
| post_type | Detect by presence of article card, video player, image container |
| engagement | Parse like/comment count text from social counts area |
| links | Extract `href` from `a` tags within content |

Each selector has fallbacks. If primary selector fails, try alternates. If all fail for a field, use sensible default (empty string, "unknown", 0).

### Rate Limiting

- 2-second delay between scroll actions
- 1-second delay between post extractions
- Random jitter of 0-1 seconds added to each delay
- Stop after 3 consecutive scrolls with no new posts

## Storage Detail

### SQLite Schema

```sql
CREATE TABLE IF NOT EXISTS posts (
    id TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    author TEXT NOT NULL,
    author_profile TEXT DEFAULT '',
    content TEXT NOT NULL,
    post_type TEXT DEFAULT 'text',
    saved_at TEXT NOT NULL,
    engagement TEXT DEFAULT '{}',    -- JSON
    links TEXT DEFAULT '[]',         -- JSON
    cluster_id INTEGER,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS clusters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keywords TEXT NOT NULL,          -- JSON array
    summary TEXT NOT NULL,
    post_count INTEGER NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);
```

### Upsert Logic

On sync, for each post:
- If post ID exists: update content, engagement, links, updated_at
- If post ID is new: insert full row

This handles posts whose engagement counts change between syncs.

## Clustering Detail

### Embedding Model

`all-MiniLM-L6-v2` from sentence-transformers:
- 384-dimensional embeddings
- Fast inference (can embed hundreds of posts in seconds)
- Good semantic similarity for short texts
- ~80MB model download on first use

### Auto K Selection

When `--num-clusters` is not specified:
1. Test K from 2 to floor(sqrt(number_of_posts))
2. For each K, run K-means and compute silhouette score
3. Select K with highest silhouette score
4. Minimum K is 2, maximum capped at 20

### Keyword Extraction

Per cluster:
1. Collect all post content in the cluster
2. Run TF-IDF across all clusters (each cluster as one "document")
3. Take top 5 terms by TF-IDF weight for each cluster
4. These become the cluster keywords
5. Summary is generated by joining top 2-3 keywords with " & " or similar

### Minimum Cluster Size

Posts in clusters smaller than `--min-size` are reassigned to the nearest larger cluster by centroid distance.

## Configuration

### File Location

`~/.digin/config.yaml` — created on first run with defaults if not present.

### Schema

```yaml
linkedin:
  headless: false
  scroll_delay: 2
  max_scroll_attempts: 3

clustering:
  method: kmeans
  min_cluster_size: 3
  embedding_model: all-MiniLM-L6-v2

output:
  default_format: table
  colors: true
```

### Precedence

1. CLI flags (highest)
2. Config file
3. Defaults (lowest)

No environment variable support in MVP.

## Error Handling

- **Browser launch fails:** clear error message with Playwright install instructions (`playwright install chromium`)
- **Login timeout:** after 5 minutes of no login detected, print message and exit
- **No posts found:** suggest checking URL, trying non-headless mode
- **Too few posts for clustering:** require minimum 6 posts, print clear message
- **Embedding model download:** first-run message about model download
- **SQLite errors:** wrap in clear messages, never show raw tracebacks to user

## Testing Strategy

- **Models:** unit tests for Post/Cluster serialization
- **Storage:** unit tests with in-memory SQLite
- **Clustering:** unit tests with synthetic post data
- **CLI:** click.testing.CliRunner for command tests
- **Scraper:** mock Playwright page objects, no live LinkedIn calls in tests

## Out of Scope (MVP)

- Research/explore pipeline (deferred — will use Anthropic API when built)
- HDBSCAN clustering (deferred)
- LinkedIn automated login
- Database encryption
- Profile support (multiple LinkedIn accounts)
- Plugin system
- Web interface
