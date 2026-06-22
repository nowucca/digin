#!/usr/bin/env python3
"""
Debug script to understand LinkedIn's HTML structure and scrolling behavior
This will help us identify the correct selectors and scrolling logic
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def debug_linkedin_structure():
    """Debug LinkedIn's HTML structure and scrolling behavior"""
    print("=== LinkedIn HTML Structure Debugger ===")
    print()
    print("This script will help us understand:")
    print("1. What HTML elements exist on the saved posts page")
    print("2. How scrolling and loading works")
    print("3. What selectors we should use")
    print()
    print("Instructions:")
    print("1. Make sure Chrome is running with --remote-debugging-port=9222")
    print("2. Navigate to https://www.linkedin.com/my-items/saved-posts/ in that Chrome")
    print("3. Make sure you have some saved posts visible")
    print()
    
    input("Press Enter when you're on the saved posts page...")
    
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print(f"✅ Connected to Chrome")
        print(f"Current URL: {driver.current_url}")
        print(f"Page title: {driver.title}")
        print()
        
        # Check if we're on the right page
        if "saved-posts" not in driver.current_url and "my-items" not in driver.current_url:
            print("⚠️  Warning: You don't appear to be on the saved posts page")
            print("Current URL:", driver.current_url)
            print("Please navigate to: https://www.linkedin.com/my-items/saved-posts/")
            input("Press Enter when you're on the correct page...")
        
        print("=== DEBUGGING PHASE 1: Page Structure ===")
        
        # Get page source length
        page_source = driver.page_source
        print(f"Page source length: {len(page_source)} characters")
        
        # Check for common LinkedIn elements
        print("\n--- Checking for common LinkedIn elements ---")
        common_selectors = [
            "header",
            "main",
            ".feed",
            ".scaffold-layout",
            "[data-urn]",
            "[data-id]",
            ".artdeco-card",
            ".update-components-update-v2",
            ".feed-shared-update-v2",
            ".occludable-update"
        ]
        
        for selector in common_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"  {selector}: {len(elements)} elements found")
                if elements and len(elements) < 10:  # Show details for small counts
                    for i, elem in enumerate(elements[:3]):
                        try:
                            classes = elem.get_attribute("class")
                            data_urn = elem.get_attribute("data-urn")
                            data_id = elem.get_attribute("data-id")
                            print(f"    [{i}] classes: {classes[:100]}...")
                            if data_urn:
                                print(f"    [{i}] data-urn: {data_urn}")
                            if data_id:
                                print(f"    [{i}] data-id: {data_id}")
                        except:
                            pass
            except Exception as e:
                print(f"  {selector}: Error - {e}")
        
        print("\n=== DEBUGGING PHASE 2: Post-like Elements ===")
        
        # Look for anything that might be a post
        post_indicators = [
            "post",
            "update",
            "activity",
            "feed",
            "card",
            "item"
        ]
        
        all_elements = driver.find_elements(By.CSS_SELECTOR, "*")
        print(f"Total elements on page: {len(all_elements)}")
        
        potential_posts = []
        for element in all_elements:
            try:
                classes = element.get_attribute("class") or ""
                data_urn = element.get_attribute("data-urn") or ""
                data_id = element.get_attribute("data-id") or ""
                
                # Check if this element might be a post
                is_potential_post = any(indicator in classes.lower() for indicator in post_indicators)
                is_potential_post = is_potential_post or "urn:li:activity" in data_urn
                is_potential_post = is_potential_post or "urn:li:activity" in data_id
                
                if is_potential_post:
                    potential_posts.append({
                        "tag": element.tag_name,
                        "classes": classes[:100],
                        "data_urn": data_urn[:50],
                        "data_id": data_id[:50],
                        "text_preview": element.text[:100].replace('\n', ' ')
                    })
            except:
                continue
        
        print(f"\nFound {len(potential_posts)} potential post elements:")
        for i, post in enumerate(potential_posts[:10]):  # Show first 10
            print(f"  [{i}] {post['tag']} - classes: {post['classes']}")
            if post['data_urn']:
                print(f"      data-urn: {post['data_urn']}")
            if post['data_id']:
                print(f"      data-id: {post['data_id']}")
            if post['text_preview'].strip():
                print(f"      text: {post['text_preview']}")
            print()
        
        print("\n=== DEBUGGING PHASE 3: Scrolling Behavior ===")
        
        # Test scrolling
        initial_height = driver.execute_script("return document.body.scrollHeight")
        print(f"Initial page height: {initial_height}px")
        
        # Count elements before scroll
        before_count = len(driver.find_elements(By.CSS_SELECTOR, "*"))
        print(f"Elements before scroll: {before_count}")
        
        # Scroll down
        print("Scrolling down...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Wait for content to load
        
        # Check new height and element count
        new_height = driver.execute_script("return document.body.scrollHeight")
        after_count = len(driver.find_elements(By.CSS_SELECTOR, "*"))
        
        print(f"New page height: {new_height}px (change: {new_height - initial_height}px)")
        print(f"Elements after scroll: {after_count} (change: {after_count - before_count})")
        
        if new_height > initial_height:
            print("✅ Scrolling appears to load new content")
        else:
            print("⚠️  Scrolling didn't increase page height - may have reached end")
        
        if after_count > before_count:
            print("✅ New elements were added after scrolling")
        else:
            print("⚠️  No new elements added - scrolling may not be working")
        
        print("\n=== DEBUGGING PHASE 4: Specific LinkedIn Selectors ===")
        
        # Try LinkedIn-specific selectors
        linkedin_selectors = [
            # New LinkedIn feed selectors
            "[data-urn*='urn:li:activity']",
            "[data-id*='urn:li:activity']",
            ".feed-shared-update-v2",
            ".update-components-update-v2",
            ".occludable-update",
            ".artdeco-card",
            
            # Saved posts specific
            ".saved-item",
            ".saved-post",
            "[data-test-id*='saved']",
            
            # Generic post containers
            "article",
            "[role='article']",
            ".post",
            ".update"
        ]
        
        for selector in linkedin_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"  {selector}: {len(elements)} elements")
                
                if elements:
                    # Show details of first element
                    elem = elements[0]
                    print(f"    First element tag: {elem.tag_name}")
                    print(f"    Classes: {elem.get_attribute('class')[:100]}...")
                    print(f"    Text preview: {elem.text[:100].replace(chr(10), ' ')}...")
                    print()
            except Exception as e:
                print(f"  {selector}: Error - {e}")
        
        print("\n=== DEBUGGING COMPLETE ===")
        print("Based on this output, we can determine:")
        print("1. Which selectors actually find posts")
        print("2. Whether scrolling loads new content")
        print("3. What the HTML structure looks like")
        print()
        print("Use this information to update the main scraper logic.")
        
        # Don't close the driver
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure:")
        print("1. Chrome is running with --remote-debugging-port=9222 --user-data-dir=/tmp")
        print("2. You're logged into LinkedIn")
        print("3. You're on the saved posts page")

if __name__ == "__main__":
    debug_linkedin_structure()
