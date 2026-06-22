# Architectural Decisions & Questions

## Critical Design Questions

### 1. LLM Integration for Research & Clustering

**Question**: Which LLM service should we use for content analysis, cluster summarization, and research?

**Options:**
- **OpenAI GPT-4/GPT-3.5**: Most capable, good API, costs per token
- **Anthropic Claude**: Strong reasoning, good for analysis, competitive pricing
- **Local Models (Ollama)**: Privacy-first, no API costs, requires local setup
- **Hybrid Approach**: Local for basic tasks, cloud for complex analysis

**Recommendation**: Start with OpenAI for development (proven, reliable), add local model support later for privacy-conscious users.

**Implementation Impact**:
```python
# research.py
class LLMProvider:
    def __init__(self, provider: str = "openai"):
        if provider == "openai":
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        elif provider == "anthropic":
            self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        elif provider == "ollama":
            self.client = OllamaClient()
    
    def summarize_cluster(self, posts: List[Post]) -> str:
        """Generate cluster summary using LLM"""
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract key themes using LLM"""
```

### 2. Text Embeddings Strategy

**Question**: How should we generate embeddings for clustering LinkedIn posts?

**Options:**
- **sentence-transformers**: Local, good quality, no API costs
- **OpenAI Embeddings**: High quality, API costs, requires internet
- **Hybrid**: sentence-transformers for clustering, OpenAI for research

**Recommendation**: sentence-transformers for core clustering (privacy + cost), OpenAI embeddings optional for enhanced research.

### 3. Clustering Algorithm Selection

**Question**: Which clustering algorithms should we prioritize?

**Current Plan**: K-means, HDBSCAN, Agglomerative

**Architectural Questions**:
- Should we support online/incremental clustering for large datasets?
- How do we handle the "optimal clusters" problem automatically?
- Should we pre-cluster by post type (text vs article vs video)?

**Recommendation**: 
1. Start with K-means (simple, predictable)
2. Add HDBSCAN (handles noise, finds natural clusters)
3. Consider hierarchical clustering for topic relationships

### 4. Research Pipeline Depth

**Question**: How deep should the research pipeline go?

**Current Plan**: Configurable depth 1-3

**Options**:
- **Level 1**: Basic keyword extraction and post summarization
- **Level 2**: Follow 1-2 links, analyze referenced content
- **Level 3**: Deep analysis, related topic discovery, trend identification

**Architectural Considerations**:
- Rate limiting for external requests
- Caching strategy for expensive operations
- Cost management for LLM API calls
- User control over research scope

### 5. Data Privacy & Storage

**Question**: How should we handle sensitive LinkedIn data?

**Current Plan**: Local SQLite storage

**Additional Considerations**:
- Should we encrypt the local database?
- How do we handle data retention/cleanup?
- Should we support data export for backup?
- How do we handle LinkedIn's terms of service?

**Recommendation**: 
- Local storage only (no cloud sync)
- Optional database encryption
- Clear data retention policies
- Respect LinkedIn's rate limits and ToS

### 6. Error Handling & Resilience

**Question**: How should we handle LinkedIn's anti-scraping measures?

**Architectural Patterns**:
```python
class ScrapingStrategy:
    def __init__(self):
        self.retry_strategies = [
            ExponentialBackoff(),
            UserAgentRotation(),
            ProxyRotation(),  # Optional
            CaptchaSolver(),  # Manual intervention
        ]
    
    def handle_detection(self, error_type: str):
        """Implement graduated response to detection"""
```

**Questions**:
- Should we support proxy rotation?
- How do we handle CAPTCHA challenges?
- Should we implement session persistence across runs?
- How do we detect and respond to rate limiting?

### 7. CLI User Experience

**Question**: How sophisticated should the CLI interface be?

**Current Plan**: Click-based with clig.dev principles

**Enhancement Options**:
- **Rich Terminal UI**: Progress bars, colors, interactive elements
- **Configuration Wizard**: Interactive setup for first-time users
- **Plugin System**: Allow custom clustering algorithms
- **Shell Completion**: Tab completion for commands and options

**Implementation Example**:
```python
# Enhanced CLI with rich output
from rich.console import Console
from rich.progress import Progress
from rich.table import Table

@cli.command()
def sync(ctx, num, headless):
    console = Console()
    
    with Progress() as progress:
        task = progress.add_task("Syncing posts...", total=num or 100)
        # Update progress during scraping
        
    # Display results in rich table
    table = Table(title="Sync Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    console.print(table)
```

### 8. Testing Strategy

**Question**: How do we test LinkedIn scraping without hitting their servers?

**Options**:
- **Mock WebDriver**: Simulate browser interactions
- **HTML Fixtures**: Saved LinkedIn page HTML for parsing tests
- **Integration Tests**: Limited real LinkedIn testing
- **Synthetic Data**: Generated post data for clustering tests

**Recommendation**:
```python
# tests/fixtures/linkedin_posts.html
# Saved HTML from LinkedIn saved posts page

# tests/test_scraper.py
def test_post_extraction():
    with open('fixtures/linkedin_posts.html') as f:
        html = f.read()
    
    scraper = LinkedInScraper(mock_config)
    posts = scraper._extract_posts_from_html(html)
    
    assert len(posts) > 0
    assert all(post.content for post in posts)
```

### 9. Performance & Scalability

**Question**: How do we handle users with thousands of saved posts?

**Architectural Considerations**:
- Incremental processing (sync only new posts)
- Batch clustering for large datasets
- Memory-efficient data structures
- Progress indicators for long operations
- Caching expensive operations (embeddings, LLM calls)

**Implementation Strategy**:
```python
class IncrementalProcessor:
    def sync_posts(self, since_date: Optional[datetime] = None):
        """Only sync posts newer than since_date"""
    
    def cluster_incrementally(self, new_posts: List[Post]):
        """Add new posts to existing clusters or create new ones"""
    
    def cache_embeddings(self, posts: List[Post]):
        """Cache expensive embedding calculations"""
```

### 10. Configuration Management

**Question**: How complex should the configuration system be?

**Current Plan**: YAML config files with CLI overrides

**Additional Features**:
- **Profile Support**: Different configs for different LinkedIn accounts
- **Environment-specific configs**: Dev vs production settings
- **Validation**: Schema validation for config files
- **Migration**: Handle config format changes

**Example**:
```yaml
# ~/.digin/profiles/work.yaml
profile: work
linkedin:
  username: work@company.com
  headless: true
  max_posts: 500

clustering:
  method: hdbscan
  min_cluster_size: 5

research:
  llm_provider: openai
  depth: 2
  
# ~/.digin/profiles/personal.yaml
profile: personal
linkedin:
  username: personal@gmail.com
  headless: false
  max_posts: null

clustering:
  method: kmeans
  num_clusters: 10
```

## Recommended Architecture Decisions

### Phase 1 Decisions (Must Decide Now)
1. **LLM Provider**: Start with OpenAI, add configuration for others later
2. **Embeddings**: sentence-transformers for clustering, OpenAI optional for research
3. **Database**: SQLite with optional encryption
4. **CLI Framework**: Click with rich terminal output
5. **Testing**: Mock-based with HTML fixtures

### Phase 2 Decisions (Can Defer)
1. **Advanced Clustering**: HDBSCAN and hierarchical methods
2. **Research Depth**: Configurable 1-3 levels
3. **Performance**: Incremental processing and caching
4. **Configuration**: Profile support and validation

### Phase 3 Decisions (Future Enhancement)
1. **Plugin System**: Custom clustering algorithms
2. **Advanced UI**: Interactive terminal interface
3. **Data Export**: Multiple formats and backup options
4. **Monitoring**: Usage analytics and performance metrics

## Questions for You

1. **LLM Budget**: Are you comfortable with OpenAI API costs for research features, or should we prioritize local models?

2. **Privacy Level**: How important is it that no data ever leaves your machine? This affects LLM choice and research capabilities.

3. **Complexity vs Features**: Would you prefer a simpler tool that works reliably, or more features with higher complexity?

4. **LinkedIn Risk Tolerance**: How aggressive should we be with scraping? Conservative (slower, safer) or optimized (faster, higher detection risk)?

5. **User Base**: Is this just for you, or do you envision others using it? This affects configuration complexity and documentation needs.

These decisions will significantly impact the implementation approach and should be resolved before starting Phase 1 development.
