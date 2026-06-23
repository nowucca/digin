# Progress

## Completed
- Full MVP: sync, cluster, show, export, viz, status, schema
- Scraper with Playwright, persistent sessions, headless, resumable, enrichment
- K-means clustering with auto-K, TF-IDF keywords
- Interactive visualization (treemap, scatter, network)
- XDG compliance, 100% test coverage
- Claude Code plugin with workflow skill
- --json global flag and schema command for agents
- README, README_AGENT.md, LICENSE
- Public repo at github.com/nowucca/digin

## Example Clustering Output (Claude-powered analysis of 697 posts)
1. Claude Code & Agent Harnesses (~55 posts)
2. Cline & MCP Ecosystem (~60 posts)
3. AI Agents & Agentic Patterns (~45 posts)
4. Ethan Mollick's AI Research (~110 posts)
5. LLM Foundations & Courses (~65 posts)
6. ChatGPT Tips & Prompting (~50 posts)
7. System Design & Backend (~55 posts)
8. AI Industry & Frontier Models (~55 posts)
9. Career & Leadership (~40 posts)
10. Company Pages & Misc (~30 posts)
11. RAG & AI Engineering (~40 posts)
12. AI & Society (~35 posts)

## Known Issues
- TF-IDF keywords include URL fragments — need to strip URLs before keyword extraction
- Auto-K too conservative at large N — silhouette favors K=2
- ~15 posts failed enrichment due to browser timeout on long syncs
- PostStorage default path was hardcoded to old ~/.digin/ (fixed)
