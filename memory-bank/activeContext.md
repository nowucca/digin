# Active Context

## Current State (June 2026)
- 697 posts synced from LinkedIn
- Claude-powered clustering implemented as default (`digin cluster`)
- Local K-means available as fallback (`digin cluster --local`)
- Uses Claude Sonnet via Anthropic SDK, requires ANTHROPIC_API_KEY env var
- Falls back to local with clear warning if no API key
- Constellize plugins now loading (skills + agents)

## Recent Discoveries
- TF-IDF keyword extraction picks up URL fragments (https, lnkd.in) as top terms — needs URL stripping before TF-IDF
- K-means auto-K (silhouette) picks K=2 for 697 posts — too conservative
- Ethan Mollick dominates the saved posts (~110 posts) — author-aware clustering could be valuable
- Claude clustering identified 12 natural topics vs K-means' noisy 10
