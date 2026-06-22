#!/usr/bin/env python3
"""
Test script to verify Incavate can connect to Chrome and basic scraping works
This version works on any LinkedIn page to test the connection
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def test_connection():
    """Test connection to Chrome remote debugging"""
    print("=== Incavate Connection Test ===")
    print()
    print("Instructions:")
    print("1. Start Chrome with: chrome --remote-debugging-port=9222")
    print("2. Open LinkedIn in that Chrome window (any page is fine)")
    print("3. Run this test script")
    print()
    
    input("Press Enter when Chrome is ready...")
    
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print(f"✅ Connected successfully!")
        print(f"Current URL: {driver.current_url}")
        print(f"Page title: {driver.title}")
        
        # Test basic element finding
        try:
            # Look for LinkedIn header
            header = driver.find_element(By.TAG_NAME, "header")
            print("✅ Can find page elements")
        except:
            print("⚠️  Could not find header element, but connection works")
        
        # Test scrolling
        try:
            initial_height = driver.execute_script("return document.body.scrollHeight")
            driver.execute_script("window.scrollTo(0, 500);")
            print("✅ Can execute JavaScript and scroll")
        except Exception as e:
            print(f"❌ JavaScript execution failed: {e}")
        
        print()
        print("Connection test completed successfully!")
        print("The incavate.py script should work once you have saved posts.")
        
        # Don't close the driver - leave browser open
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print()
        print("Troubleshooting:")
        print("1. Make sure Chrome is running with --remote-debugging-port=9222")
        print("2. Close all other Chrome windows first")
        print("3. Try restarting Chrome with the debug flag")

if __name__ == "__main__":
    test_connection()
