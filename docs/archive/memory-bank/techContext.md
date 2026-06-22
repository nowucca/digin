# Technical Context

## Stack
- Python 3.12+ with uv package manager
- Playwright (not Selenium) for browser automation
- Click 8+ for CLI
- scikit-learn for clustering
- sentence-transformers for text embeddings
- SQLite for local storage
- pandas for data manipulation

## Key Pattern: LinkedIn Scraping
Using Playwright with full automation approach:
1. Tool launches browser, opens LinkedIn login page
2. User logs in manually (handles MFA, avoids detection)
3. Tool takes over once on saved posts page
4. Infinite scroll to load all posts
5. Extract structured data per post
6. Graceful degradation with detailed logging

LinkedIn-specific considerations:
- Infinite scroll instead of pagination
- Different post types (text, image, video, article)
- Conservative rate limiting to avoid detection
- Navigate to https://www.linkedin.com/my-items/saved-posts/

## Project Structure (Target)
```
digin/
├── src/digin/
│   ├── __init__.py
│   ├── cli.py
│   ├── scraper.py
│   ├── models.py
│   ├── storage.py
│   └── config.py
├── tests/
├── pyproject.toml
└── README.md
```
