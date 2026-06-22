# Active Context

## Current State (May 2026)
- Project has been in planning since August 2025
- No production code written yet
- Exploratory scraping scripts exist in `incavate/` (HTML dumps, debug scripts)
- `pyproject.toml` exists with basic config (Python 3.12+, selenium, webdriver-manager)
- No git repository initialized

## Decisions Made
- **Language**: Python 3.12+
- **Scraping**: Selenium + Chrome (adapted from steve-finances patterns)
- **CLI framework**: Click
- **Storage**: SQLite (local, ~/.digin/posts.db)
- **Embeddings**: sentence-transformers for clustering
- **Clustering**: Start with K-means, add HDBSCAN later
- **Package manager**: uv (pyproject.toml + uv.lock already exist)

## Decisions Made (May 2026)
- **LLM provider**: Anthropic (Claude) for research/summarization (when we get to it)
- **MVP scope**: sync + cluster + show/export only. Research/explore deferred.
- **Authentication**: Config file for LinkedIn credentials (local, not committed)

## What Exists in incavate/
- `incavate.py` — main scraping script (18KB, most substantial code)
- `debug_linkedin.py`, `debug_saved_posts.py` — debugging tools
- `simple_html_dump.py`, `iframe_aware_dump.py` — HTML capture utilities  
- `test_connection.py` — basic connection testing
- Several saved LinkedIn HTML dumps for offline analysis
- These are exploratory/prototype quality, not production code

## Next Step
Initialize git, set up proper package structure, and build Phase 1 (scraper + storage + basic CLI).
