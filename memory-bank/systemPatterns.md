# System Patterns

## Architecture
Monolith Python package, one module per concern.

## Modules
- `cli.py` — Click command group (sync, cluster, show, viz, export, status, schema, skill)
- `scraper.py` — Playwright with persistent context, system Chrome for headless, enrichment pipeline
- `clustering.py` — sentence-transformers (all-MiniLM-L6-v2) → K-means → TF-IDF keywords
- `viz.py` — Plotly treemap/scatter + HTML/CSS network cards
- `storage.py` — SQLite with upsert logic
- `config.py` — YAML config with XDG paths
- `paths.py` — XDG Base Directory compliance
- `models.py` — Post and Cluster dataclasses

## Key Patterns
- Persistent browser sessions (cookies survive between runs)
- Resumable sync (skip known post IDs)
- Offline clustering (HF_HUB_OFFLINE=1 after first model download)
- Stale lock file cleanup before browser launch
- Post enrichment via detail page visits for full content + external links
- LinkedIn safety redirect URL unwrapping
