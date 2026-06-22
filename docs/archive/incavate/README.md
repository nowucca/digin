# Incavate - LinkedIn Posts HTML Downloader

A quick and dirty prototype to download HTML of LinkedIn saved posts for later processing.

## How It Works

1. **You handle login**: Manually log into LinkedIn and navigate to your saved posts
2. **Script takes over**: Connects to your existing browser session and downloads HTML
3. **No authentication complexity**: Avoids LinkedIn's anti-bot measures by using your authenticated session

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. **First, save some LinkedIn posts**:
   - Go to LinkedIn in your regular browser
   - Find interesting posts and click the "Save" button (bookmark icon)
   - Save at least 5-10 posts to test with

3. Start Chrome with remote debugging:
```bash
chrome --remote-debugging-port=9222
```

4. In that Chrome window:
   - Log into LinkedIn
   - Navigate to https://www.linkedin.com/my-items/saved-posts/
   - Verify you can see your saved posts

5. Test the connection first:
```bash
python test_connection.py
```

6. If connection test passes, run the main script:
```bash
python incavate.py
```

## Usage

### Basic usage
```bash
python incavate.py
```

### Limit number of posts
```bash
python incavate.py --max-posts 50
```

### Custom output directory
```bash
python incavate.py --output-dir my_posts
```

## What It Does

1. **Connects** to your existing Chrome browser session
2. **Scrolls** through your saved posts page to load all posts
3. **Extracts** HTML content of each post
4. **Saves** each post as:
   - `post_[id]_[timestamp].html` - Full HTML content
   - `post_[id]_[timestamp].json` - Metadata (author, content preview, etc.)

## Output Structure

```
posts_html/
├── post_urn_li_activity_123_1704067200.html
├── post_urn_li_activity_123_1704067200.json
├── post_urn_li_activity_456_1704067201.html
├── post_urn_li_activity_456_1704067201.json
└── ...
```

Each HTML file contains:
- Complete post HTML with LinkedIn styling
- Metadata in HTML head (author, timestamp, content preview)

Each JSON file contains:
- Post ID
- Author name
- Content preview
- Processing timestamp

## Features

- **No authentication handling** - uses your existing login
- **Infinite scroll support** - loads all saved posts
- **Duplicate detection** - won't save the same post twice
- **Graceful error handling** - continues processing if individual posts fail
- **Progress tracking** - shows how many posts processed
- **Respectful delays** - includes pauses to avoid overwhelming LinkedIn

## Limitations

- Requires manual Chrome setup with remote debugging
- Only works with Chrome browser
- Depends on LinkedIn's current HTML structure
- No content parsing - just saves raw HTML for later processing

## Next Steps

After running this prototype, you'll have HTML files that can be processed to:
1. Extract clean text content
2. Parse author information and engagement metrics
3. Identify post types (text, image, video, article)
4. Cluster posts by topic
5. Generate summaries and insights

This approach separates data collection from data processing, making it easier to iterate on the analysis without re-scraping LinkedIn.
