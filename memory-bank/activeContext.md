# Active Context

## Current State (June 2026)
- 697 posts synced from LinkedIn
- 10 K-means clusters with TF-IDF naming (noisy — "Https & Lnkd" in most names)
- Claude-powered clustering done manually, dramatically better names (e.g., "Claude Code & Agent Harnesses", "Ethan Mollick's AI Research")
- Roadmap: LLM-powered cluster naming via Anthropic API, research pipeline, HDBSCAN

## Recent Discoveries
- TF-IDF keyword extraction picks up URL fragments (https, lnkd.in) as top terms — needs URL stripping before TF-IDF
- K-means auto-K (silhouette) picks K=2 for 697 posts — too conservative
- Ethan Mollick dominates the saved posts (~110 posts) — author-aware clustering could be valuable
- Claude clustering identified 12 natural topics vs K-means' noisy 10
