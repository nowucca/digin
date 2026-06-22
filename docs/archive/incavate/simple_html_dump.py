#!/usr/bin/env python3
"""
Simple HTML dump tool - just connect and save the page HTML so we can examine it
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pathlib import Path

def dump_linkedin_html():
    """Connect and dump the current page HTML to a file"""
    print("=== Simple LinkedIn HTML Dumper ===")
    print()
    print("This will:")
    print("1. Connect to your Chrome browser")
    print("2. Save the current page HTML to a file")
    print("3. Let you examine the structure manually")
    print()
    
    input("Press Enter to connect and dump HTML...")
    
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print(f"✅ Connected!")
        print(f"Current URL: {driver.current_url}")
        print(f"Page title: {driver.title}")
        print()
        
        # Get the page source
        print("Getting page HTML...")
        html_content = driver.page_source
        
        # Save to file
        output_file = Path("linkedin_page_dump.html")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML saved to: {output_file.absolute()}")
        print(f"File size: {len(html_content):,} characters")
        print()
        
        # Basic stats
        print("=== BASIC PAGE STATS ===")
        print(f"Total HTML length: {len(html_content):,} characters")
        print(f"Number of <div> tags: {html_content.count('<div')}")
        print(f"Number of <a> tags: {html_content.count('<a ')}")
        print(f"Number of <article> tags: {html_content.count('<article')}")
        print(f"Contains 'data-urn': {'Yes' if 'data-urn' in html_content else 'No'}")
        print(f"Contains 'urn:li:activity': {'Yes' if 'urn:li:activity' in html_content else 'No'}")
        print(f"Contains 'saved posts': {'Yes' if 'saved posts' in html_content.lower() else 'No'}")
        print(f"Contains 'feed-shared': {'Yes' if 'feed-shared' in html_content else 'No'}")
        print()
        
        # Look for key phrases
        print("=== SEARCHING FOR KEY PHRASES ===")
        key_phrases = [
            "saved posts",
            "10+",
            "data-urn",
            "urn:li:activity",
            "feed-shared-update",
            "artdeco-card",
            "post",
            "update"
        ]
        
        for phrase in key_phrases:
            count = html_content.lower().count(phrase.lower())
            print(f"'{phrase}': {count} occurrences")
        
        print()
        print("=== NEXT STEPS ===")
        print(f"1. Open {output_file.absolute()} in a text editor")
        print("2. Search for 'saved posts' or '10+' to find the relevant section")
        print("3. Look at the HTML structure around those areas")
        print("4. Find the links or clickable elements")
        print("5. Use that info to update the scraper")
        
        # Don't close the driver
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    dump_linkedin_html()
