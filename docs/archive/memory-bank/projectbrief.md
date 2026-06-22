# DigIn Project Brief

## Problem
LinkedIn users save interesting posts but never revisit them systematically. Saved posts become a digital graveyard of professional insights.

## Solution
CLI tool that scrapes saved LinkedIn posts, clusters them by topic using ML, and optionally researches the content deeper.

## Core Pipeline
```
digin sync     → Scrape saved posts from LinkedIn
digin cluster  → Group posts by topic (K-means, HDBSCAN)
digin explore  → Research clusters deeper (future)
digin show     → Display results
digin export   → Export to CSV/JSON/Markdown
```

## Target User
Solo developer (Steven) who actively saves LinkedIn posts and wants to organize and learn from them.

## Constraints
- Privacy-first: all data stored locally (SQLite)
- Must handle LinkedIn's dynamic content (infinite scroll)
- Must avoid detection (conservative rate limiting)
- CLI follows clig.dev principles
- No LinkedIn API available for saved posts — browser automation required
