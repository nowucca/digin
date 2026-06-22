#!/usr/bin/env python3
"""
iframe-aware HTML dump tool - checks for iframes and dumps their content too
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from pathlib import Path

def dump_with_iframe_detection():
    """Connect and dump HTML, including iframe content"""
    print("=== iframe-Aware LinkedIn HTML Dumper ===")
    print()
    print("This will:")
    print("1. Connect to your Chrome browser")
    print("2. Check for iframes on the page")
    print("3. Dump main page + iframe content")
    print("4. Show you exactly what LinkedIn is serving")
    print()
    
    input("Press Enter to connect and analyze...")
    
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print(f"✅ Connected!")
        print(f"Current URL: {driver.current_url}")
        print(f"Page title: {driver.title}")
        print()
        
        # Get main page HTML
        print("=== MAIN PAGE ANALYSIS ===")
        main_html = driver.page_source
        print(f"Main page HTML length: {len(main_html):,} characters")
        
        # Check for iframes
        print("\n=== IFRAME DETECTION ===")
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"Found {len(iframes)} iframes on the page")
        
        if iframes:
            print("\nIframe details:")
            for i, iframe in enumerate(iframes):
                try:
                    src = iframe.get_attribute("src") or "No src"
                    name = iframe.get_attribute("name") or "No name"
                    id_attr = iframe.get_attribute("id") or "No id"
                    classes = iframe.get_attribute("class") or "No classes"
                    
                    print(f"  Iframe {i}:")
                    print(f"    src: {src}")
                    print(f"    name: {name}")
                    print(f"    id: {id_attr}")
                    print(f"    classes: {classes}")
                    print()
                except Exception as e:
                    print(f"    Error getting iframe {i} details: {e}")
        
        # Save main page HTML
        main_file = Path("linkedin_main_page.html")
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(main_html)
        print(f"✅ Main page HTML saved to: {main_file.absolute()}")
        
        # Try to access iframe content
        iframe_contents = []
        if iframes:
            print("\n=== IFRAME CONTENT ANALYSIS ===")
            for i, iframe in enumerate(iframes):
                try:
                    print(f"Switching to iframe {i}...")
                    driver.switch_to.frame(iframe)
                    
                    # Get iframe content
                    iframe_html = driver.page_source
                    iframe_url = driver.current_url
                    iframe_title = driver.title
                    
                    print(f"  Iframe {i} URL: {iframe_url}")
                    print(f"  Iframe {i} title: {iframe_title}")
                    print(f"  Iframe {i} HTML length: {len(iframe_html):,} characters")
                    
                    # Save iframe content
                    iframe_file = Path(f"linkedin_iframe_{i}.html")
                    with open(iframe_file, 'w', encoding='utf-8') as f:
                        f.write(f"<!-- Iframe {i} URL: {iframe_url} -->\n")
                        f.write(f"<!-- Iframe {i} Title: {iframe_title} -->\n")
                        f.write(iframe_html)
                    
                    print(f"  ✅ Iframe {i} content saved to: {iframe_file.absolute()}")
                    
                    # Look for posts in iframe
                    post_indicators = [
                        "saved posts",
                        "data-urn",
                        "urn:li:activity",
                        "feed-shared",
                        "post"
                    ]
                    
                    iframe_lower = iframe_html.lower()
                    found_indicators = []
                    for indicator in post_indicators:
                        count = iframe_lower.count(indicator.lower())
                        if count > 0:
                            found_indicators.append(f"{indicator}: {count}")
                    
                    if found_indicators:
                        print(f"  🎯 FOUND POST INDICATORS in iframe {i}:")
                        for indicator in found_indicators:
                            print(f"    - {indicator}")
                    else:
                        print(f"  ❌ No post indicators found in iframe {i}")
                    
                    iframe_contents.append({
                        'index': i,
                        'url': iframe_url,
                        'title': iframe_title,
                        'html_length': len(iframe_html),
                        'indicators': found_indicators
                    })
                    
                    # Switch back to main page
                    driver.switch_to.default_content()
                    print()
                    
                except Exception as e:
                    print(f"  ❌ Error accessing iframe {i}: {e}")
                    driver.switch_to.default_content()
                    continue
        
        # Overall analysis
        print("=== OVERALL ANALYSIS ===")
        
        # Check main page for post indicators
        main_lower = main_html.lower()
        main_indicators = []
        post_indicators = [
            "saved posts",
            "data-urn",
            "urn:li:activity", 
            "feed-shared",
            "post"
        ]
        
        for indicator in post_indicators:
            count = main_lower.count(indicator.lower())
            if count > 0:
                main_indicators.append(f"{indicator}: {count}")
        
        print(f"Main page indicators: {main_indicators if main_indicators else 'None found'}")
        
        # Summary
        if iframe_contents:
            print(f"\nIframe summary:")
            for iframe_info in iframe_contents:
                if iframe_info['indicators']:
                    print(f"  🎯 Iframe {iframe_info['index']} has post content!")
                    print(f"    URL: {iframe_info['url']}")
                    print(f"    Indicators: {iframe_info['indicators']}")
        
        print("\n=== RECOMMENDATIONS ===")
        if any(iframe_info['indicators'] for iframe_info in iframe_contents):
            print("✅ FOUND POSTS IN IFRAMES!")
            print("The LinkedIn posts are likely loaded in iframes.")
            print("Update your scraper to:")
            print("1. Find and switch to the correct iframe")
            print("2. Look for posts within that iframe")
            print("3. Extract content from the iframe context")
        elif main_indicators:
            print("✅ FOUND POSTS IN MAIN PAGE!")
            print("Posts are in the main page, not iframes.")
            print("Check the main HTML file for the correct selectors.")
        else:
            print("❌ NO POSTS FOUND")
            print("Either:")
            print("1. You're not on the right page")
            print("2. Posts are loaded dynamically after page load")
            print("3. LinkedIn is using a different structure")
        
        # Don't close the driver
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    dump_with_iframe_detection()
