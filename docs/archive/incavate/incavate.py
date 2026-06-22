#!/usr/bin/env python3
"""
Incavate - Quick prototype to download LinkedIn saved posts HTML

Usage:
1. User manually logs into LinkedIn and navigates to https://www.linkedin.com/my-items/saved-posts/
2. Run this script - it will take over the existing browser session
3. Script scrolls through posts and saves HTML of each post to files
"""

import os
import time
import json
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import hashlib

class Incavate:
    def __init__(self, output_dir="posts_html"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.driver = None
        self.posts_processed = 0
        
    def connect_to_existing_browser(self):
        """Connect to an existing Chrome browser session"""
        print("Connecting to existing Chrome browser...")
        print("Make sure you have:")
        print("1. Chrome open and logged into LinkedIn")
        print("2. Navigated to https://www.linkedin.com/my-items/saved-posts/")
        print("3. Started Chrome with remote debugging: chrome --remote-debugging-port=9222")
        
        input("Press Enter when ready...")
        
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            print(f"Connected! Current URL: {self.driver.current_url}")
            
            # Verify we're on the saved posts page
            if "saved-posts" not in self.driver.current_url:
                print("Warning: You don't appear to be on the saved posts page")
                print("Please navigate to https://www.linkedin.com/my-items/saved-posts/")
                input("Press Enter when you're on the saved posts page...")
                
            return True
        except Exception as e:
            print(f"Failed to connect to browser: {e}")
            print("\nTo fix this:")
            print("1. Close all Chrome windows")
            print("2. Start Chrome with: chrome --remote-debugging-port=9222")
            print("3. Log into LinkedIn and go to saved posts")
            print("4. Run this script again")
            return False
    
    def navigate_to_actual_posts(self):
        """Navigate from the saved posts landing page to the actual posts"""
        try:
            print("Looking for saved posts section...")
            
            # Look for the saved posts link/section
            saved_posts_selectors = [
                "a[href*='saved-posts']",
                "[data-control-name*='saved']",
                "a:contains('Saved posts')",
                ".artdeco-card a",
                "a[href*='/my-items/saved-posts/']"
            ]
            
            saved_posts_link = None
            for selector in saved_posts_selectors:
                try:
                    if ':contains(' in selector:
                        # Find all links and check their text
                        links = self.driver.find_elements(By.CSS_SELECTOR, "a")
                        for link in links:
                            if 'saved posts' in link.text.lower():
                                saved_posts_link = link
                                print(f"Found saved posts link with text: '{link.text}'")
                                break
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            saved_posts_link = elements[0]
                            print(f"Found saved posts link with selector: {selector}")
                            break
                    if saved_posts_link:
                        break
                except Exception as e:
                    print(f"Selector {selector} failed: {e}")
                    continue
            
            if saved_posts_link:
                print("Clicking on saved posts link...")
                saved_posts_link.click()
                time.sleep(3)  # Wait for navigation
                print(f"Navigated to: {self.driver.current_url}")
                return True
            else:
                print("Could not find saved posts link. You may already be on the posts page.")
                return True
                
        except Exception as e:
            print(f"Error navigating to posts: {e}")
            return False

    def wait_for_posts_to_load(self):
        """Wait for posts to load on the page"""
        try:
            print("Checking if posts are loaded on the page...")
            
            # First try to navigate to actual posts if we're on the landing page
            if "saved-posts" in self.driver.current_url and "Saved posts and articles" in self.driver.page_source:
                print("Detected saved posts landing page, navigating to actual posts...")
                if not self.navigate_to_actual_posts():
                    return False
            
            # Based on iframe analysis, we know the main page should have:
            # - 240 urn:li:activity elements
            # - 49 feed-shared elements  
            # - 873 post elements
            
            # Check if basic LinkedIn structure is loaded
            basic_selectors = [
                "[data-urn*='urn:li:activity']",  # Should find ~240
                ".feed-shared",                   # Should find ~49
                ".artdeco-card"                   # Should find some cards
            ]
            
            found_any = False
            for selector in basic_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    print(f"  Found {len(elements)} elements with selector: {selector}")
                    if elements:
                        found_any = True
                except Exception as e:
                    print(f"  Error checking selector '{selector}': {e}")
            
            if found_any:
                print("✅ Page appears to be loaded with LinkedIn content")
                return True
            else:
                print("❌ No LinkedIn content found - page may not be fully loaded")
                return False
            
        except Exception as e:
            print(f"Error checking if posts are loaded: {e}")
            return False
    
    def get_post_elements(self):
        """Get all post elements currently visible on the page"""
        print("Looking for posts on the page...")
        
        # Based on iframe analysis, we know there are urn:li:activity and feed-shared elements
        # Try multiple selectors for LinkedIn posts
        selectors = [
            # Primary selectors based on analysis
            "[data-urn*='urn:li:activity']",
            "[data-id*='urn:li:activity']", 
            ".feed-shared-update-v2",
            ".feed-shared-update",
            ".occludable-update",
            
            # Backup selectors
            "[data-urn]",
            ".artdeco-card",
            "article",
            "[role='article']"
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"  Selector '{selector}': {len(elements)} elements found")
                
                if elements:
                    # Filter elements that might actually be posts
                    post_elements = []
                    for elem in elements:
                        try:
                            # Check if element has post-like characteristics
                            data_urn = elem.get_attribute("data-urn") or ""
                            data_id = elem.get_attribute("data-id") or ""
                            classes = elem.get_attribute("class") or ""
                            text = elem.text.strip()
                            
                            # Must have some content and post indicators
                            is_post = (
                                ("urn:li:activity" in data_urn or "urn:li:activity" in data_id) or
                                ("feed-shared" in classes) or
                                (len(text) > 50)  # Has substantial content
                            )
                            
                            if is_post:
                                post_elements.append(elem)
                        except:
                            continue
                    
                    if post_elements:
                        print(f"✅ Found {len(post_elements)} actual posts using selector: {selector}")
                        return post_elements
                    else:
                        print(f"  No actual posts found with {selector} (filtered out {len(elements)} non-post elements)")
                        
            except Exception as e:
                print(f"  Error with selector '{selector}': {e}")
                continue
        
        print("❌ No posts found with any selector")
        return []
    
    def extract_post_info(self, post_element):
        """Extract basic info from a post element"""
        try:
            # Try to get post URL/ID
            post_id = None
            data_urn = post_element.get_attribute("data-urn")
            data_id = post_element.get_attribute("data-id")
            
            if data_urn:
                post_id = data_urn
            elif data_id:
                post_id = data_id
            else:
                # Generate ID from content hash
                content = post_element.text[:100]
                post_id = hashlib.md5(content.encode()).hexdigest()
            
            # Try to get author name
            author = "unknown"
            author_selectors = [
                ".feed-shared-actor__name",
                ".update-components-actor__name",
                "[data-control-name='actor_name']"
            ]
            
            for selector in author_selectors:
                try:
                    author_element = post_element.find_element(By.CSS_SELECTOR, selector)
                    author = author_element.text.strip()
                    break
                except:
                    continue
            
            # Try to get post content preview
            content_preview = ""
            content_selectors = [
                ".feed-shared-text",
                ".update-components-text",
                ".feed-shared-update-v2__description"
            ]
            
            for selector in content_selectors:
                try:
                    content_element = post_element.find_element(By.CSS_SELECTOR, selector)
                    content_preview = content_element.text.strip()[:200]
                    break
                except:
                    continue
            
            return {
                "id": post_id,
                "author": author,
                "content_preview": content_preview,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error extracting post info: {e}")
            return {
                "id": f"unknown_{int(time.time())}",
                "author": "unknown",
                "content_preview": "",
                "timestamp": datetime.now().isoformat()
            }
    
    def save_post_html(self, post_element, post_info):
        """Save the HTML of a post to a file"""
        try:
            # Clean the post ID for filename
            clean_id = "".join(c for c in str(post_info["id"]) if c.isalnum() or c in "._-")[:50]
            filename = f"post_{clean_id}_{int(time.time())}.html"
            filepath = self.output_dir / filename
            
            # Get the HTML content
            html_content = post_element.get_attribute("outerHTML")
            
            # Create a complete HTML document
            full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>LinkedIn Post - {post_info['author']}</title>
    <meta name="post-id" content="{post_info['id']}">
    <meta name="author" content="{post_info['author']}">
    <meta name="timestamp" content="{post_info['timestamp']}">
    <meta name="content-preview" content="{post_info['content_preview'][:100]}">
</head>
<body>
{html_content}
</body>
</html>"""
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(full_html)
            
            # Also save metadata as JSON
            metadata_file = filepath.with_suffix('.json')
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(post_info, f, indent=2)
            
            print(f"Saved: {filename} - {post_info['author']} - {post_info['content_preview'][:50]}...")
            return True
            
        except Exception as e:
            print(f"Error saving post HTML: {e}")
            return False
    
    def scroll_and_load_more(self):
        """Scroll down to load more posts"""
        try:
            # Scroll to bottom of page
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Wait a bit for new posts to load
            time.sleep(3)
            
            # Check if we can scroll more
            current_height = self.driver.execute_script("return document.body.scrollHeight")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            return new_height > current_height
            
        except Exception as e:
            print(f"Error scrolling: {e}")
            return False
    
    def process_all_posts(self, max_posts=None):
        """Process all posts on the saved posts page"""
        if not self.wait_for_posts_to_load():
            return
        
        processed_ids = set()
        no_new_posts_count = 0
        
        print(f"Starting to process posts (max: {max_posts or 'unlimited'})...")
        
        while True:
            # Get current posts
            post_elements = self.get_post_elements()
            
            if not post_elements:
                print("No posts found, stopping...")
                break
            
            new_posts_found = False
            
            # Process each post
            for post_element in post_elements:
                if max_posts and self.posts_processed >= max_posts:
                    print(f"Reached maximum posts limit: {max_posts}")
                    return
                
                # Extract post info
                post_info = self.extract_post_info(post_element)
                
                # Skip if we've already processed this post
                if post_info["id"] in processed_ids:
                    continue
                
                # Save the post
                if self.save_post_html(post_element, post_info):
                    processed_ids.add(post_info["id"])
                    self.posts_processed += 1
                    new_posts_found = True
            
            # If no new posts were found, try scrolling
            if not new_posts_found:
                no_new_posts_count += 1
                if no_new_posts_count >= 3:
                    print("No new posts found after 3 attempts, stopping...")
                    break
                
                print("No new posts found, scrolling to load more...")
                if not self.scroll_and_load_more():
                    print("Cannot scroll further, stopping...")
                    break
            else:
                no_new_posts_count = 0
            
            print(f"Processed {self.posts_processed} posts so far...")
            
            # Small delay to be respectful
            time.sleep(1)
    
    def run(self, max_posts=None):
        """Main method to run the scraper"""
        try:
            if not self.connect_to_existing_browser():
                return
            
            print(f"Output directory: {self.output_dir.absolute()}")
            self.process_all_posts(max_posts)
            
            print(f"\nCompleted! Processed {self.posts_processed} posts")
            print(f"HTML files saved to: {self.output_dir.absolute()}")
            
        except KeyboardInterrupt:
            print(f"\nStopped by user. Processed {self.posts_processed} posts")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            if self.driver:
                print("Leaving browser open for you to continue using...")
                # Don't close the driver since user might want to continue using browser

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Incavate - Download LinkedIn saved posts HTML")
    parser.add_argument("--max-posts", "-n", type=int, help="Maximum number of posts to process")
    parser.add_argument("--output-dir", "-o", default="posts_html", help="Output directory for HTML files")
    
    args = parser.parse_args()
    
    print("=== Incavate - LinkedIn Posts HTML Downloader ===")
    print()
    print("Instructions:")
    print("1. Start Chrome with remote debugging:")
    print("   chrome --remote-debugging-port=9222")
    print("2. Log into LinkedIn in that Chrome window")
    print("3. Navigate to https://www.linkedin.com/my-items/saved-posts/")
    print("4. Run this script")
    print()
    
    scraper = Incavate(output_dir=args.output_dir)
    scraper.run(max_posts=args.max_posts)

if __name__ == "__main__":
    main()
