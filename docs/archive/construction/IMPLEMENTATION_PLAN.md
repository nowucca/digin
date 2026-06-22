# DigIn Implementation Plan

## Overview
This implementation plan details the step-by-step development of DigIn, a LinkedIn post research and clustering tool. The plan is based on proven patterns from steve-finances and follows clig.dev principles for excellent CLI UX.

## Development Strategy

### Incremental Development Approach
- **Build vertically**: Complete one feature end-to-end before moving to the next
- **Test early**: Validate each component with real LinkedIn data as soon as possible
- **Fail fast**: Identify LinkedIn scraping issues early in development
- **User feedback**: Test CLI UX continuously during development

### Risk Mitigation
- **LinkedIn Detection**: Conservative rate limiting and robust error handling
- **UI Changes**: Multiple selector fallbacks and graceful degradation
- **Complexity**: Modular architecture with clear component boundaries
- **Testing**: Mock data for development, minimal live testing

## Phase 1: Foundation (Week 1-2)

### 1.1 Project Structure Setup
**Goal**: Create professional Python package structure

```
digin/
├── digin/
│   ├── __init__.py
│   ├── cli.py              # Main CLI entry point
│   ├── scraper.py          # LinkedIn scraping logic
│   ├── models.py           # Data models (Post, Cluster)
│   ├── storage.py          # SQLite persistence layer
│   ├── config.py           # Configuration management
│   └── utils.py            # Shared utilities
├── data/                   # Local data storage
│   ├── posts/              # Scraped post data
│   ├── clusters/           # Clustering results
│   └── cache/              # Research cache
├── tests/
│   ├── __init__.py
│   ├── test_scraper.py
│   ├── test_models.py
│   └── fixtures/           # Mock data for testing
├── requirements.txt
├── setup.py
├── README.md
├── .gitignore
└── digin.json.example      # Example credentials file
```

**Tasks:**
- [ ] Create directory structure
- [ ] Setup requirements.txt with core dependencies
- [ ] Create setup.py for package installation
- [ ] Initialize git repository with .gitignore
- [ ] Create basic README with setup instructions

### 1.2 Data Models
**Goal**: Define core data structures

```python
# models.py
@dataclass
class Post:
    id: str                    # Unique identifier (hash of URL + timestamp)
    url: str                   # LinkedIn post URL
    author: str                # Post author name
    author_profile: str        # Author profile URL
    content: str               # Post text content
    timestamp: datetime        # When post was created
    saved_at: datetime         # When user saved the post
    engagement: Dict           # Likes, comments, shares
    post_type: str             # text, image, video, article
    cluster_id: Optional[int]  # Assigned cluster (null initially)
    research: Optional[Dict]   # Additional research data

@dataclass
class Cluster:
    id: int                    # Cluster identifier
    posts: List[str]           # Post IDs in this cluster
    keywords: List[str]        # Representative keywords
    summary: str               # Human-readable description
    created_at: datetime       # When cluster was created
    research: Optional[Dict]   # Deep research results
```

**Tasks:**
- [ ] Define Post dataclass with all required fields
- [ ] Define Cluster dataclass for grouping posts
- [ ] Add validation methods for data integrity
- [ ] Create serialization/deserialization methods
- [ ] Add unit tests for data models

### 1.3 Storage Layer
**Goal**: SQLite-based persistence with proper schema

```python
# storage.py
class PostStorage:
    def __init__(self, db_path: str = "~/.digin/posts.db"):
        self.db_path = Path(db_path).expanduser()
        self._init_database()
    
    def save_posts(self, posts: List[Post]) -> None:
        """Save posts to database, handling duplicates"""
    
    def load_posts(self, filters: Optional[Dict] = None) -> List[Post]:
        """Load posts with optional filtering"""
    
    def update_post_cluster(self, post_id: str, cluster_id: int) -> None:
        """Update post's cluster assignment"""
    
    def save_clusters(self, clusters: List[Cluster]) -> None:
        """Save cluster definitions"""
    
    def load_clusters(self) -> List[Cluster]:
        """Load all clusters"""
```

**Database Schema:**
```sql
CREATE TABLE posts (
    id TEXT PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    author TEXT NOT NULL,
    author_profile TEXT,
    content TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    saved_at DATETIME NOT NULL,
    engagement JSON,
    post_type TEXT NOT NULL,
    cluster_id INTEGER,
    research JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE clusters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keywords JSON NOT NULL,
    summary TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    research JSON
);
```

**Tasks:**
- [ ] Implement SQLite database initialization
- [ ] Create posts and clusters tables with proper schema
- [ ] Implement CRUD operations for posts
- [ ] Implement CRUD operations for clusters
- [ ] Add duplicate detection and handling
- [ ] Create database migration system
- [ ] Add unit tests for storage operations

### 1.4 Configuration System
**Goal**: Flexible configuration with secure credential handling

```python
# config.py
@dataclass
class Config:
    # LinkedIn settings
    linkedin_username: str
    linkedin_headless: bool = True
    linkedin_scroll_delay: int = 2
    linkedin_max_posts: Optional[int] = None
    
    # Storage settings
    database_path: str = "~/.digin/posts.db"
    
    # Clustering settings
    clustering_method: str = "kmeans"
    clustering_auto_clusters: bool = True
    clustering_min_size: int = 3
    
    # Output settings
    output_format: str = "table"
    output_colors: bool = True

def load_config() -> Config:
    """Load configuration from multiple sources with precedence"""
    # 1. Command line arguments (handled by Click)
    # 2. Environment variables
    # 3. User config file (~/.digin/config.yaml)
    # 4. Project config file (./digin.yaml)
    # 5. Default values
```

**Tasks:**
- [ ] Define Config dataclass with all settings
- [ ] Implement hierarchical configuration loading
- [ ] Add secure credential handling (prompt for password)
- [ ] Create example configuration files
- [ ] Add configuration validation
- [ ] Add unit tests for configuration loading

### 1.5 LinkedIn Scraper (Core)
**Goal**: Adapt steve-finances patterns for LinkedIn saved posts

```python
# scraper.py
class LinkedInScraper:
    def __init__(self, config: Config):
        self.config = config
        self.driver = None
        
    def _setup_driver(self) -> None:
        """Setup Chrome WebDriver with appropriate options"""
        # Based on steve-finances patterns
        
    def _wait_for_element(self, by: By, value: str, timeout: int = 5):
        """Robust element waiting with fallback strategies"""
        # Multiple selector attempts with iframe fallback
        
    def login(self) -> bool:
        """Handle LinkedIn authentication with MFA support"""
        # Adapt steve-finances login flow for LinkedIn
        
    def navigate_to_saved_posts(self) -> bool:
        """Navigate to LinkedIn saved posts page"""
        # Go to https://www.linkedin.com/my-items/saved-posts/
        
    def _handle_infinite_scroll(self, max_posts: Optional[int] = None) -> None:
        """Load all saved posts via infinite scroll"""
        # Key difference from steve-finances pagination
        
    def _extract_post_data(self, post_element) -> Optional[Post]:
        """Extract post data from DOM element"""
        # Parse post content, author, date, engagement
        
    def scrape_saved_posts(self, limit: Optional[int] = None) -> List[Post]:
        """Main scraping method - orchestrates the full process"""
        
    def close(self) -> None:
        """Clean up browser resources"""
```

**Key Adaptations from steve-finances:**
1. **Authentication Flow**: Adapt for LinkedIn's login process
2. **Navigation**: Go to saved posts page instead of transactions
3. **Infinite Scroll**: Replace pagination logic with scroll handling
4. **Data Extraction**: Parse LinkedIn post structure instead of financial data
5. **Rate Limiting**: More conservative delays for LinkedIn

**Tasks:**
- [ ] Implement Chrome WebDriver setup with LinkedIn-specific options
- [ ] Adapt authentication flow for LinkedIn login
- [ ] Implement navigation to saved posts page
- [ ] Build infinite scroll handling with post loading detection
- [ ] Create post data extraction from LinkedIn DOM
- [ ] Add comprehensive error handling and logging
- [ ] Implement rate limiting and detection avoidance
- [ ] Add unit tests with mock data

### 1.6 Basic CLI Interface
**Goal**: Click-based CLI following clig.dev principles

```python
# cli.py
@click.group()
@click.option('--config', '-c', help='Path to config file')
@click.option('--verbose', '-v', is_flag=True, help='Increase output verbosity')
@click.option('--quiet', '-q', is_flag=True, help='Suppress all non-error output')
@click.version_option()
@click.pass_context
def cli(ctx, config, verbose, quiet):
    """DigIn - LinkedIn Post Research & Clustering Tool
    
    Transform your LinkedIn saved posts into organized, researched insights.
    """
    ctx.ensure_object(dict)
    ctx.obj['config'] = load_config(config)
    ctx.obj['verbose'] = verbose
    ctx.obj['quiet'] = quiet

@cli.command()
@click.option('--num', '-n', type=int, help='Number of recent posts to fetch')
@click.option('--headless/--no-headless', default=None, help='Run browser in headless mode')
@click.pass_context
def sync(ctx, num, headless):
    """Fetch your latest saved posts from LinkedIn
    
    Examples:
      digin sync                    # Sync all saved posts
      digin sync --num 50           # Sync only 50 most recent posts
      digin sync --no-headless      # Show browser window during sync
    """
    config = ctx.obj['config']
    if headless is not None:
        config.linkedin_headless = headless
    if num is not None:
        config.linkedin_max_posts = num
        
    scraper = LinkedInScraper(config)
    storage = PostStorage(config.database_path)
    
    try:
        if not scraper.login():
            click.echo("Failed to login to LinkedIn", err=True)
            return
            
        posts = scraper.scrape_saved_posts(limit=num)
        storage.save_posts(posts)
        
        click.echo(f"Successfully synced {len(posts)} posts")
        
    except Exception as e:
        click.echo(f"Error during sync: {str(e)}", err=True)
    finally:
        scraper.close()

if __name__ == '__main__':
    cli()
```

**Tasks:**
- [ ] Setup Click framework with main command group
- [ ] Implement sync command with all options
- [ ] Add comprehensive help text with examples
- [ ] Implement error handling with user-friendly messages
- [ ] Add progress indicators for long operations
- [ ] Create configuration integration
- [ ] Add unit tests for CLI commands

## Phase 2: Core Features (Week 3-4)

### 2.1 Text Processing Pipeline
**Goal**: Prepare post content for clustering

```python
# processing.py
class TextProcessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        
    def preprocess_text(self, text: str) -> str:
        """Clean and normalize text for clustering"""
        # Remove URLs, mentions, hashtags
        # Normalize whitespace and punctuation
        # Convert to lowercase
        # Remove stop words
        
    def extract_features(self, posts: List[Post]) -> np.ndarray:
        """Convert posts to feature vectors for clustering"""
        # Use sentence-transformers for embeddings
        # Better than TF-IDF for semantic similarity
```

### 2.2 Clustering System
**Goal**: Multiple clustering algorithms with evaluation

```python
# clustering.py
class PostClusterer:
    def __init__(self, method: str = 'kmeans', **kwargs):
        self.method = method
        self.kwargs = kwargs
        
    def fit_predict(self, posts: List[Post]) -> List[int]:
        """Cluster posts and return cluster labels"""
        
    def suggest_num_clusters(self, posts: List[Post]) -> int:
        """Automatically determine optimal number of clusters"""
        
    def evaluate_clusters(self, posts: List[Post], labels: List[int]) -> Dict:
        """Evaluate clustering quality with multiple metrics"""
        
    def generate_cluster_summaries(self, clusters: List[Cluster]) -> None:
        """Generate human-readable cluster descriptions"""
```

### 2.3 Additional CLI Commands
**Goal**: Complete core CLI functionality

```python
@cli.command()
@click.option('--num-clusters', '-k', type=int, help='Number of clusters to create')
@click.option('--method', type=click.Choice(['kmeans', 'hdbscan', 'agglomerative']), 
              help='Clustering algorithm to use')
@click.option('--min-size', type=int, help='Minimum cluster size')
def cluster(num_clusters, method, min_size):
    """Group saved posts into topic clusters"""

@cli.command()
@click.option('--format', '-f', type=click.Choice(['table', 'json', 'md']), 
              default='table', help='Output format')
@click.option('--cluster', '-c', type=int, help='Show specific cluster only')
def show(format, cluster):
    """Display saved posts or clustering results"""

@cli.command()
@click.option('--format', '-f', type=click.Choice(['csv', 'json', 'md']), 
              required=True, help='Export format')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
def export(format, output):
    """Export posts and clusters to file"""
```

## Phase 3: Advanced Features (Week 5-6)

### 3.1 Research Pipeline
**Goal**: Deep content analysis and research

```python
# research.py
class ResearchPipeline:
    def __init__(self, depth: int = 2, cache_enabled: bool = True):
        self.depth = depth
        self.cache_enabled = cache_enabled
        
    def research_cluster(self, cluster: Cluster) -> Dict:
        """Perform deep research on cluster topics"""
        # Stage 1: Keyword extraction and analysis
        # Stage 2: Related content discovery
        # Stage 3: Deep analysis and summarization
```

### 3.2 Enhanced Output
**Goal**: Rich terminal output with colors and formatting

```python
# output.py
class OutputFormatter:
    def format_posts_table(self, posts: List[Post]) -> str:
        """Format posts as a rich table"""
        
    def format_clusters_summary(self, clusters: List[Cluster]) -> str:
        """Format cluster summary with colors"""
        
    def format_research_results(self, research: Dict) -> str:
        """Format research results with rich formatting"""
```

## Phase 4: Polish & Optimization (Week 7-8)

### 4.1 Performance Optimization
- Optimize clustering for large datasets
- Implement incremental processing
- Add caching for expensive operations
- Memory usage optimization

### 4.2 Testing & Quality
- Comprehensive unit test suite
- Integration tests with mock data
- Performance benchmarking
- Error handling validation

### 4.3 Documentation
- Complete README with examples
- API documentation
- Troubleshooting guide
- Configuration reference

## Testing Strategy

### Unit Testing
```python
# tests/test_scraper.py
class TestLinkedInScraper:
    def test_login_success(self, mock_driver):
        """Test successful login flow"""
        
    def test_post_extraction(self, sample_post_html):
        """Test post data extraction from HTML"""
        
    def test_infinite_scroll(self, mock_driver):
        """Test infinite scroll handling"""

# tests/test_clustering.py
class TestPostClusterer:
    def test_kmeans_clustering(self, sample_posts):
        """Test K-means clustering with sample data"""
        
    def test_cluster_evaluation(self, clustered_posts):
        """Test clustering quality metrics"""
```

### Integration Testing
```python
# tests/test_integration.py
class TestFullPipeline:
    def test_sync_to_cluster_pipeline(self, mock_linkedin_data):
        """Test complete sync -> cluster -> show pipeline"""
        
    def test_export_functionality(self, sample_clusters):
        """Test export in all supported formats"""
```

### Mock Data Strategy
- Create realistic LinkedIn post HTML fixtures
- Generate diverse post content for clustering tests
- Mock WebDriver responses for scraping tests
- Avoid hitting LinkedIn during automated testing

## Deployment & Distribution

### Development Installation
```bash
# Clone repository
git clone <repo-url>
cd digin

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install in development mode
pip install -e .

# Setup credentials
cp digin.json.example digin.json
# Edit digin.json with LinkedIn credentials
```

### Production Installation (Future)
```bash
pip install digin
```

## Risk Mitigation Plan

### LinkedIn Detection
- **Conservative Rate Limiting**: 2-3 second delays between actions
- **Human-like Behavior**: Random delays, realistic scroll speeds
- **Error Monitoring**: Detect and respond to rate limiting
- **Graceful Degradation**: Continue processing even if some posts fail

### UI Changes
- **Multiple Selectors**: Fallback strategies for element selection
- **Robust Parsing**: Handle missing or changed elements gracefully
- **Version Detection**: Detect LinkedIn interface changes
- **User Feedback**: Clear error messages when scraping fails

### Performance Issues
- **Incremental Processing**: Handle large datasets in batches
- **Memory Management**: Efficient data structures and cleanup
- **Caching**: Cache expensive operations like embeddings
- **Progress Indicators**: Show progress for long-running operations

## Success Criteria

### Phase 1 Success
- [ ] Can successfully login to LinkedIn
- [ ] Can navigate to saved posts page
- [ ] Can scrape at least 10 saved posts
- [ ] Can store posts in SQLite database
- [ ] CLI sync command works end-to-end

### Phase 2 Success
- [ ] Can cluster posts into meaningful groups
- [ ] Clustering produces interpretable results
- [ ] Can display results in multiple formats
- [ ] Can export data for external use

### Phase 3 Success
- [ ] Research pipeline provides valuable insights
- [ ] Output is well-formatted and readable
- [ ] Tool feels professional and polished

### Phase 4 Success
- [ ] Handles large datasets efficiently
- [ ] Comprehensive test coverage
- [ ] Complete documentation
- [ ] Ready for broader use

This implementation plan provides a clear roadmap for building DigIn incrementally, with each phase building on the previous one and delivering working functionality that can be tested and validated.
