# Technical Context

## Stack
Python 3.12+, uv, Playwright, Click, sentence-transformers, scikit-learn, pandas, pyyaml, plotly, umap-learn, anthropic (future)

## XDG Paths
- Config: `$XDG_CONFIG_HOME/digin/config.yaml`
- Data: `$XDG_DATA_HOME/digin/digin.db`
- Cache: `$XDG_CACHE_HOME/digin/browser-data/`

## Testing
pytest + pytest-cov, 74 tests, 100% line+branch coverage (scraper excluded)

## Plugin
`.claude-plugin/plugin.json` + `skills/digin-workflow/SKILL.md`
