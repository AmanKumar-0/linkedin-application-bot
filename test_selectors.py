#!/usr/bin/env python3
"""
Quick test script for LinkedIn job card selectors
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def test_linkedin_selectors():
    """Test different selectors on LinkedIn job search page"""
    
    # Setup Chrome with basic options
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # Navigate to LinkedIn jobs (you'll need to be logged in)
        test_url = "https://www.linkedin.com/jobs/search/?keywords=software%20engineer&location=India"
        print(f"🔗 Testing URL: {test_url}")
        
        driver.get(test_url)
        time.sleep(5)
        
        print(f"📍 Current URL: {driver.current_url}")
        
        # Test various selectors
        selectors_to_test = [
            ".jobs-search-results__list-item",
            ".job-search-card", 
            ".job-card-container",
            "[data-job-id]",
            ".jobs-search__results-list li",
            ".entity-result",
            "li[class*='job']",
            ".base-search-card",
            ".jobs-search-results-list__list-item"
        ]
        
        print("\n🔍 Testing job card selectors:")
        print("-" * 40)
        
        for selector in selectors_to_test:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"✅ {selector:<40} -> {len(elements)} elements")
                
                # If we found elements, test link selectors within them
                if elements and len(elements) > 0:
                    card = elements[0]
                    link_selectors = [
                        ".job-card-list__title",
                        ".job-search-card__title-link",
                        "a[href*='/jobs/view/']",
                        "h3 a",
                        ".entity-result__title-text a"
                    ]
                    
                    print(f"  🔗 Testing link selectors in first card:")
                    for link_sel in link_selectors:
                        try:
                            link = card.find_element(By.CSS_SELECTOR, link_sel)
                            href = link.get_attribute('href')
                            if href and '/jobs/view/' in href:
                                print(f"    ✅ {link_sel:<30} -> Found job URL")
                            else:
                                print(f"    ⚠️  {link_sel:<30} -> Found link but not job URL")
                        except:
                            print(f"    ❌ {link_sel:<30} -> Not found")
                
            except Exception as e:
                print(f"❌ {selector:<40} -> Error: {e}")
        
        # Test job count selectors
        print("\n📊 Testing job count selectors:")
        print("-" * 40)
        
        count_selectors = [
            ".results-context-header__job-count",
            ".jobs-search-results-list__text", 
            ".jobs-search__results-list h1",
            "[data-test-id='search-results-count']",
            ".jobs-search-results__count-string",
            "h1 span"
        ]
        
        for selector in count_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                text = element.text.strip()
                print(f"✅ {selector:<40} -> '{text}'")
            except:
                print(f"❌ {selector:<40} -> Not found")
        
        # Save screenshot for manual inspection
        driver.save_screenshot("linkedin_test_page.png")
        print(f"\n📸 Screenshot saved as: linkedin_test_page.png")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    print("🧪 LinkedIn Selector Test")
    print("=" * 50)
    print("⚠️  Make sure you're logged into LinkedIn in your default browser")
    print("⚠️  This test will open a new browser window")
    print()
    
    test_linkedin_selectors()