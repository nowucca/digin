#!/usr/bin/env python3
"""
Specific debug script for LinkedIn saved posts navigation
This will help us find the right way to get to the actual posts
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def debug_saved_posts_navigation():
    """Debug the saved posts page navigation"""
    print("=== LinkedIn Saved Posts Navigation Debugger ===")
    print()
    print("This will help us understand how to navigate from the saved posts")
    print("landing page to the actual posts feed.")
    print()
    print("Make sure you're on: https://www.linkedin.com/my-items/saved-posts/")
    print()
    
    input("Press Enter when ready...")
    
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print(f"✅ Connected to Chrome")
        print(f"Current URL: {driver.current_url}")
        print()
        
        # Look for all links on the page
        print("=== FINDING ALL LINKS ===")
        links = driver.find_elements(By.CSS_SELECTOR, "a")
        saved_posts_links = []
        
        for i, link in enumerate(links):
            try:
                href = link.get_attribute("href") or ""
                text = link.text.strip()
                
                # Look for saved posts related links
                if any(keyword in href.lower() for keyword in ['saved', 'posts']) or \
                   any(keyword in text.lower() for keyword in ['saved', 'posts']):
                    saved_posts_links.append({
                        'index': i,
                        'href': href,
                        'text': text,
                        'classes': link.get_attribute("class")
                    })
            except:
                continue
        
        print(f"Found {len(saved_posts_links)} potentially relevant links:")
        for link in saved_posts_links:
            print(f"  [{link['index']}] {link['text']}")
            print(f"      href: {link['href']}")
            print(f"      classes: {link['classes']}")
            print()
        
        # Look for cards or sections
        print("=== FINDING CARDS AND SECTIONS ===")
        cards = driver.find_elements(By.CSS_SELECTOR, ".artdeco-card")
        print(f"Found {len(cards)} artdeco cards:")
        
        for i, card in enumerate(cards):
            try:
                text = card.text.strip()[:200]
                links_in_card = card.find_elements(By.CSS_SELECTOR, "a")
                print(f"  Card {i}: {text}")
                print(f"    Links in card: {len(links_in_card)}")
                for j, link in enumerate(links_in_card[:3]):  # Show first 3 links
                    try:
                        print(f"      Link {j}: {link.text.strip()} -> {link.get_attribute('href')}")
                    except:
                        pass
                print()
            except:
                continue
        
        # Look for specific saved posts indicators
        print("=== LOOKING FOR SAVED POSTS INDICATORS ===")
        
        # Check page source for saved posts count
        page_source = driver.page_source
        if "10+" in page_source and "saved posts" in page_source.lower():
            print("✅ Found '10+' saved posts indicator in page source")
        
        # Look for clickable elements with saved posts text
        all_elements = driver.find_elements(By.CSS_SELECTOR, "*")
        clickable_saved_elements = []
        
        for element in all_elements:
            try:
                text = element.text.strip().lower()
                if 'saved posts' in text and len(text) < 100:  # Reasonable length
                    tag = element.tag_name
                    classes = element.get_attribute("class")
                    clickable = element.is_enabled() and element.is_displayed()
                    
                    clickable_saved_elements.append({
                        'tag': tag,
                        'text': element.text.strip(),
                        'classes': classes,
                        'clickable': clickable
                    })
            except:
                continue
        
        print(f"Found {len(clickable_saved_elements)} elements with 'saved posts' text:")
        for elem in clickable_saved_elements:
            print(f"  {elem['tag']}: '{elem['text']}'")
            print(f"    Classes: {elem['classes']}")
            print(f"    Clickable: {elem['clickable']}")
            print()
        
        # Try to find the specific saved posts section
        print("=== ATTEMPTING TO FIND SAVED POSTS SECTION ===")
        
        # Look for elements that might contain the saved posts count
        count_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '10+')]")
        print(f"Found {len(count_elements)} elements containing '10+':")
        
        for i, elem in enumerate(count_elements):
            try:
                parent = elem.find_element(By.XPATH, "..")
                grandparent = parent.find_element(By.XPATH, "..")
                
                print(f"  Element {i}: {elem.text}")
                print(f"    Parent: {parent.tag_name} - {parent.get_attribute('class')}")
                print(f"    Grandparent: {grandparent.tag_name} - {grandparent.get_attribute('class')}")
                
                # Look for links in the parent/grandparent
                links_nearby = grandparent.find_elements(By.CSS_SELECTOR, "a")
                print(f"    Links nearby: {len(links_nearby)}")
                for link in links_nearby[:2]:
                    try:
                        print(f"      -> {link.text.strip()} ({link.get_attribute('href')})")
                    except:
                        pass
                print()
            except:
                continue
        
        print("=== MANUAL NAVIGATION TEST ===")
        print("Now let's try to manually click on what looks like the saved posts section...")
        
        # Try to find and click the most likely saved posts link
        best_candidates = []
        
        # Look for links in cards that mention saved posts
        for card in cards:
            try:
                card_text = card.text.lower()
                if 'saved posts' in card_text:
                    links = card.find_elements(By.CSS_SELECTOR, "a")
                    for link in links:
                        href = link.get_attribute("href") or ""
                        if 'saved-posts' in href or 'saved' in link.text.lower():
                            best_candidates.append(link)
            except:
                continue
        
        if best_candidates:
            print(f"Found {len(best_candidates)} candidate links to try:")
            for i, candidate in enumerate(best_candidates):
                try:
                    print(f"  {i}: {candidate.text.strip()} -> {candidate.get_attribute('href')}")
                except:
                    pass
            
            # Try clicking the first candidate
            try:
                print(f"\nTrying to click the first candidate...")
                best_candidates[0].click()
                time.sleep(3)
                
                print(f"After click - URL: {driver.current_url}")
                print(f"Page title: {driver.title}")
                
                # Check if we now have posts
                post_selectors = [
                    "[data-urn*='urn:li:activity']",
                    ".feed-shared-update-v2",
                    ".update-components-update-v2",
                    "article"
                ]
                
                for selector in post_selectors:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"✅ Found {len(elements)} posts with selector: {selector}")
                        break
                else:
                    print("❌ Still no posts found after clicking")
                    
            except Exception as e:
                print(f"Error clicking candidate: {e}")
        else:
            print("No good candidates found for clicking")
        
        print("\n=== DEBUG COMPLETE ===")
        print("Use this information to update the navigation logic.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_saved_posts_navigation()
