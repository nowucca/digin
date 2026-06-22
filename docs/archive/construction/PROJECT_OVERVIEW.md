# DigIn: LinkedIn Post Research & Clustering Tool

## Project Vision

DigIn is a personal CLI tool designed to transform your LinkedIn saved posts into organized, researched insights. The tool scrapes your saved LinkedIn posts, intelligently clusters them by topic, and performs deep research to understand what each article is truly about, creating a curated knowledge base from your professional interests.

## Core Concept

The fundamental idea behind DigIn is to solve the common problem of saving interesting LinkedIn posts but never revisiting them in a meaningful way. Instead of letting saved posts become a digital graveyard, DigIn:

1. **Extracts** your saved LinkedIn posts automatically
2. **Clusters** them into coherent topic groups using machine learning
3. **Researches** each cluster deeply to understand the core themes and insights
4. **Presents** the results in an organized, searchable format

## Key Features

### 1. Intelligent Post Scraping
- Automated LinkedIn saved post extraction
- Configurable fetch limits and authentication
- Incremental sync capabilities to avoid re-processing

### 2. Advanced Clustering
- Multiple clustering algorithms (K-means, HDBSCAN, Agglomerative)
- Automatic cluster number detection
- Minimum cluster size controls for quality results

### 3. Deep Research Engine
- Configurable link traversal depth
- Content analysis and summarization
- Caching system to avoid redundant research

### 4. Flexible Output & Export
- Multiple display formats (table, JSON, Markdown)
- Export capabilities (CSV, JSON, Markdown)
- Terminal-friendly colorized output

## Technical Architecture

### CLI Design Philosophy
The tool follows [clig.dev](https://clig.dev) recommendations for excellent command-line UX:

- **Verb-based subcommands** for clear action separation
- **Short and long flags** for both convenience and clarity
- **Descriptive help text** for self-documentation
- **Consistent global options** across all commands

### Command Structure
```bash
digin [global options] <command> [command options] [arguments...]

Commands:
  sync       Fetch your latest saved posts from LinkedIn
  cluster    Group saved posts into topic clusters  
  explore    Do deep research on clustered topics
  show       Display saved posts or research results
  export     Save results to JSON, CSV, or Markdown
```

### Example Workflows
```bash
# Complete research pipeline
digin sync && digin cluster --num-clusters 5
digin explore --depth 3
digin show --format md

# Export results for external use
digin export -f csv -o my-research-clusters.csv
```

## Use Cases

### Personal Knowledge Management
- Transform scattered LinkedIn saves into organized research
- Identify patterns in your professional interests
- Create a searchable knowledge base of industry insights

### Content Strategy
- Understand trending topics in your saved content
- Identify content gaps and opportunities
- Research competitive landscape through saved competitor posts

### Professional Development
- Track learning themes and knowledge areas
- Identify skill development opportunities
- Create study guides from saved educational content

## Technical Implementation

### Core Technologies
- **Python** for main application logic
- **Machine Learning** libraries for clustering (scikit-learn, HDBSCAN)
- **Web Scraping** tools for LinkedIn integration
- **NLP** libraries for content analysis and research
- **CLI Framework** (Click or Typer) for command-line interface

### Data Pipeline
1. **Authentication** → LinkedIn login and session management
2. **Extraction** → Scrape saved posts with metadata
3. **Processing** → Clean and normalize post content
4. **Clustering** → Apply ML algorithms to group similar posts
5. **Research** → Follow links and analyze content depth
6. **Storage** → Cache results and maintain state
7. **Output** → Format and present results to user

## Configuration & Customization

### Config File Structure
```yaml
# ~/.digin/config.yaml
linkedin:
  username: your-email@example.com
  # password handled securely

clustering:
  default_method: kmeans
  auto_clusters: true
  min_cluster_size: 3

research:
  default_depth: 2
  timeout_seconds: 10
  cache_enabled: true

output:
  default_format: table
  colors_enabled: true
```

### Extensibility
- Plugin architecture for new clustering algorithms
- Configurable research depth and strategies
- Custom output formatters
- Integration hooks for external tools

## Development Roadmap

### Phase 1: Core Functionality
- [ ] LinkedIn authentication and post scraping
- [ ] Basic clustering with K-means
- [ ] Simple research pipeline
- [ ] Terminal output with basic formatting

### Phase 2: Enhanced Features
- [ ] Multiple clustering algorithms
- [ ] Advanced research with link following
- [ ] Export capabilities
- [ ] Configuration system

### Phase 3: Polish & Optimization
- [ ] Caching and performance optimization
- [ ] Rich terminal UI with colors and progress bars
- [ ] Comprehensive error handling
- [ ] Documentation and help system

### Future Possibilities
- [ ] Web interface for visual cluster exploration
- [ ] Integration with note-taking apps (Obsidian, Notion)
- [ ] Collaborative features for team research
- [ ] API for programmatic access

## Success Metrics

- **Utility**: Users regularly use the tool to organize their saved posts
- **Insight Quality**: Clusters provide meaningful topic groupings
- **Research Depth**: Deep research provides valuable additional context
- **Usability**: CLI interface feels natural and efficient to use

## Conclusion

DigIn represents a new approach to personal knowledge management in the professional sphere. By automatically organizing and researching your LinkedIn saved posts, it transforms passive content consumption into active knowledge building. The tool bridges the gap between saving interesting content and actually deriving insights from it, making your professional learning more systematic and valuable.

The focus on excellent CLI UX, following clig.dev principles, ensures that the tool feels professional and polished despite being a personal utility. This attention to user experience details makes the difference between a script that gets used once and a tool that becomes part of your regular workflow.
