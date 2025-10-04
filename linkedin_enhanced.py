"""
Enhanced LinkedIn Job Application Bot
Enterprise-grade implementation with improved architecture
"""

import os
import time
import random
import logging
import json
import platform
from typing import List, Dict, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import re
from urllib.parse import quote_plus

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, WebDriverException,
    ElementClickInterceptedException, StaleElementReferenceException
)

# Local imports
from config_enhanced import EnhancedConfig
from cv_analyzer import EnhancedCVAnalyzer, CVData
from ai_agent import EnhancedAIAgent, FormResponse

@dataclass
class JobApplication:
    """Structure for tracking job applications"""
    job_id: str
    title: str
    company: str
    location: str
    salary: str
    posted_date: str
    application_date: datetime
    status: str  # applied, failed, skipped
    reason: str = ""
    form_fields_filled: int = 0
    application_url: str = ""

@dataclass
class ApplicationStats:
    """Statistics for application session"""
    total_jobs_processed: int = 0
    successful_applications: int = 0
    failed_applications: int = 0
    skipped_applications: int = 0
    complex_forms_skipped: int = 0
    start_time: datetime = None
    end_time: datetime = None
    
    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.now()

class EnhancedLinkedInBot:
    """Enhanced LinkedIn job application bot with enterprise features"""
    
    def __init__(self, config: EnhancedConfig):
        self.config = config
        self.driver = None
        self.wait = None
        self.cv_analyzer = None
        self.ai_agent = None
        self.cv_data = None
        self.stats = ApplicationStats()
        self.applied_jobs = []
        self.session_data = {}
        
        # Setup logging
        self._setup_logging()
        
        # Initialize components
        self._initialize_components()
        
        # Load previous session data
        self._load_session_data()
    
    def _setup_logging(self):
        """Setup comprehensive logging"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        logging.basicConfig(
            level=getattr(logging, self.config.logging.log_level),
            format=log_format,
            handlers=[
                logging.FileHandler(f'logs/{self.config.logging.log_file}'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("🚀 Enhanced LinkedIn Bot initialized")
    
    def _initialize_components(self):
        """Initialize CV analyzer and AI agent"""
        try:
            # Initialize CV analyzer
            self.cv_analyzer = EnhancedCVAnalyzer(
                ollama_url=self.config.ai.ollama_url,
                model=self.config.ai.model
            )
            
            # Extract and analyze CV
            self.logger.info(f"📄 Analyzing CV: {self.config.ai.cv_path}")
            cv_text = self.cv_analyzer.extract_cv_text(self.config.ai.cv_path)
            self.cv_data = self.cv_analyzer.analyze_cv_with_ai(cv_text)
            
            # Update config with CV data if not already set
            self._update_config_from_cv()
            
            # Initialize AI agent
            self.ai_agent = EnhancedAIAgent(
                cv_data=self.cv_data,
                ollama_url=self.config.ai.ollama_url,
                model=self.config.ai.model
            )
            
            self.logger.info(f"✅ CV Analysis Complete! Found {len(self.cv_data.technical_skills)} technical skills")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing components: {e}")
            raise
    
    def _update_config_from_cv(self):
        """Update configuration with CV data where not already specified"""
        if not self.config.personal_info.full_name or self.config.personal_info.full_name == "Please update in config":
            self.config.personal_info.full_name = self.cv_data.name
        
        if not self.config.personal_info.email or '@example.com' in self.config.personal_info.email:
            self.config.personal_info.email = self.cv_data.email
        
        if not self.config.personal_info.phone or 'XXX' in self.config.personal_info.phone:
            self.config.personal_info.phone = self.cv_data.phone
        
        # Update job search keywords if not specified
        if not self.config.job_search.keywords:
            self.config.job_search.keywords = self.cv_analyzer.generate_job_search_keywords(self.cv_data)
    
    def _load_session_data(self):
        """Load previous session data"""
        session_file = f"{self.config.logging.data_dir}/session_data.json"
        if os.path.exists(session_file):
            try:
                with open(session_file, 'r') as f:
                    self.session_data = json.load(f)
                self.logger.info(f"📊 Loaded session data: {len(self.session_data.get('applied_jobs', []))} previous applications")
            except Exception as e:
                self.logger.warning(f"⚠️ Could not load session data: {e}")
    
    def _save_session_data(self):
        """Save current session data"""
        os.makedirs(self.config.logging.data_dir, exist_ok=True)
        session_file = f"{self.config.logging.data_dir}/session_data.json"
        
        try:
            session_data = {
                'applied_jobs': [job.__dict__ for job in self.applied_jobs],
                'stats': self.stats.__dict__,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"❌ Error saving session data: {e}")
    
    def setup_browser(self):
        """Setup browser with enhanced stealth and configuration"""
        try:
            if self.config.browser.browser.lower() == "chrome":
                self._setup_chrome_driver()
            elif self.config.browser.browser.lower() == "firefox":
                self._setup_firefox_driver()
            else:
                raise ValueError(f"Unsupported browser: {self.config.browser.browser}")
            
            # Setup WebDriverWait
            self.wait = WebDriverWait(self.driver, self.config.browser.element_timeout)
            
            # Apply stealth modifications
            if self.config.browser.enable_stealth:
                self._apply_stealth_modifications()
            
            self.logger.info(f"🌐 Browser setup complete: {self.config.browser.browser}")
            
        except Exception as e:
            self.logger.error(f"❌ Browser setup failed: {e}")
            raise
    
    def _setup_chrome_driver(self):
        """Setup Chrome driver with enhanced options"""
        options = ChromeOptions()
        
        # Basic stealth options
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Performance and privacy options
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-background-mode")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        
        # User agent and window size
        options.add_argument(f"--user-agent={self.config.browser.user_agent}")
        options.add_argument(f"--window-size={self.config.browser.window_size[0]},{self.config.browser.window_size[1]}")
        
        # Headless mode
        if self.config.browser.headless:
            options.add_argument("--headless")
        
        # User data directory
        if self.config.browser.user_data_dir:
            options.add_argument(f"--user-data-dir={self.config.browser.user_data_dir}")
        
        # Additional preferences
        prefs = {
            "profile.default_content_setting_values": {
                "notifications": 2,  # Block notifications
                "geolocation": 2,    # Block location sharing
            },
            "profile.default_content_settings.popups": 0,
            "managed_default_content_settings": {
                "images": 2  # Don't load images for faster loading
            }
        }
        options.add_experimental_option("prefs", prefs)
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_page_load_timeout(self.config.browser.page_load_timeout)
    
    def _setup_firefox_driver(self):
        """Setup Firefox driver with enhanced options"""
        options = FirefoxOptions()
        
        # Firefox-specific stealth options
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference('useAutomationExtension', False)
        options.set_preference("general.useragent.override", self.config.browser.user_agent)
        
        # Privacy and performance preferences
        options.set_preference("privacy.trackingprotection.enabled", False)
        options.set_preference("geo.enabled", False)
        options.set_preference("media.navigator.enabled", False)
        options.set_preference("javascript.enabled", True)
        options.set_preference("network.http.use-cache", True)
        options.set_preference("permissions.default.desktop-notification", 2)
        
        # Headless mode
        if self.config.browser.headless:
            options.add_argument("--headless")
        
        # Profile directory
        if self.config.browser.firefox_profile_dir:
            options.profile = webdriver.FirefoxProfile(self.config.browser.firefox_profile_dir)
        
        self.driver = webdriver.Firefox(options=options)
        self.driver.set_page_load_timeout(self.config.browser.page_load_timeout)
    
    def _apply_stealth_modifications(self):
        """Apply additional stealth modifications"""
        # Remove webdriver property
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Override navigator properties
        self.driver.execute_script("""
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
        """)
        
        self.driver.execute_script("""
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)
        
        # Window focus
        self.driver.execute_script("window.focus();")
    
    def human_like_delay(self, min_delay: float = None, max_delay: float = None):
        """Human-like delays with configuration"""
        if min_delay is None or max_delay is None:
            min_delay, max_delay = self.config.browser.human_delay
        
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def safe_click(self, element, max_attempts: int = 3) -> bool:
        """Safely click an element with retry logic"""
        for attempt in range(max_attempts):
            try:
                # Scroll element into view
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                self.human_like_delay(0.5, 1.0)
                
                # Wait for element to be clickable
                self.wait.until(EC.element_to_be_clickable(element))
                
                # Try to click
                element.click()
                return True
                
            except (ElementClickInterceptedException, StaleElementReferenceException) as e:
                self.logger.warning(f"⚠️ Click attempt {attempt + 1} failed: {e}")
                if attempt < max_attempts - 1:
                    self.human_like_delay(1, 2)
                    # Try to dismiss any overlays
                    self._dismiss_overlays()
                    continue
                
            except Exception as e:
                self.logger.error(f"❌ Unexpected click error: {e}")
                break
        
        return False
    
    def safe_type(self, element, text: str, clear: bool = True) -> bool:
        """Safely type text with human-like behavior"""
        try:
            # Scroll into view and focus
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            self.human_like_delay(0.3, 0.7)
            
            element.click()
            self.human_like_delay(0.2, 0.5)
            
            if clear:
                element.clear()
                self.human_like_delay(0.2, 0.4)
            
            # Type with human-like delays
            for char in str(text):
                element.send_keys(char)
                time.sleep(random.uniform(0.05, self.config.browser.typing_delay))
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Typing error: {e}")
            return False
    
    def _dismiss_overlays(self):
        """Dismiss any overlays that might be blocking interactions"""
        overlay_selectors = [
            ".artdeco-modal-overlay",
            ".search-typeahead-v2__hit",
            ".typeahead-results",
            "[data-test-single-typeahead-entity-form-search-result]",
            ".artdeco-dropdown__content",
            ".basic-typeahead__triggered-content"
        ]
        
        for selector in overlay_selectors:
            try:
                overlay = self.driver.find_element(By.CSS_SELECTOR, selector)
                if overlay.is_displayed():
                    # Try clicking outside the overlay
                    ActionChains(self.driver).move_by_offset(10, 10).click().perform()
                    self.human_like_delay(0.5, 1.0)
                    break
            except:
                continue
    
    def login(self) -> bool:
        """Enhanced login with better error handling"""
        try:
            self.logger.info("🔐 Starting LinkedIn login process...")
            
            self.driver.get("https://www.linkedin.com/login")
            self.human_like_delay(2, 4)
            
            # Find and fill username
            username_field = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            self.safe_type(username_field, self.config.security.linkedin_email)
            
            self.human_like_delay(1, 2)
            
            # Find and fill password
            password_field = self.driver.find_element(By.ID, "password")
            self.safe_type(password_field, self.config.security.linkedin_password)
            
            self.human_like_delay(2, 3)
            
            # Submit form
            login_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
            self.safe_click(login_button)
            
            # Wait for navigation and check for challenges
            self.human_like_delay(5, 8)
            
            current_url = self.driver.current_url
            if "challenge" in current_url or "checkpoint" in current_url:
                self.logger.warning("🔐 Login challenge detected - manual intervention may be required")
                input("Please complete the challenge and press Enter to continue...")
            
            # Verify login success
            if "linkedin.com/feed" in self.driver.current_url or "linkedin.com/in/" in self.driver.current_url:
                self.logger.info("✅ Login successful!")
                return True
            else:
                self.logger.error("❌ Login failed - unexpected redirect")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Login error: {e}")
            return False
    
    def generate_job_search_urls(self) -> List[str]:
        """Generate job search URLs based on configuration and CV analysis"""
        urls = []
        base_url = "https://www.linkedin.com/jobs/search/?"
        
        # Generate keyword-location combinations
        for keyword in self.config.job_search.keywords[:10]:  # Limit to top 10 keywords
            for location in self.config.job_search.locations[:5]:  # Limit to top 5 locations
                params = {
                    'keywords': keyword,
                    'location': location,
                    'f_TPR': 'r86400' if self.config.job_search.date_posted.value == "Past 24 hours" else 'r604800',
                    'f_AL': 'true',  # Easy Apply only
                    'f_E': ','.join([str(i) for i, level in enumerate([
                        "Internship", "Entry level", "Associate", "Mid-Senior level", "Director", "Executive"
                    ]) if any(exp_level.value == level for exp_level in self.config.job_search.experience_levels)]),
                    'f_JT': ','.join([str(i) for i, jtype in enumerate([
                        "Full-time", "Part-time", "Contract", "Temporary", "Volunteer", "Internship", "Other"
                    ]) if any(job_type.value == jtype for job_type in self.config.job_search.job_types)]),
                    'f_WT': ','.join([str(i+1) for i, rtype in enumerate([
                        "On-site", "Remote", "Hybrid"
                    ]) if any(remote_type.value == rtype for remote_type in self.config.job_search.remote_types)])
                }
                
                # Add salary filter if specified
                if self.config.job_search.salary_range:
                    salary_mapping = {
                        "$40,000+": "1", "$60,000+": "2", "$80,000+": "3", "$100,000+": "4",
                        "$120,000+": "5", "$140,000+": "6", "$160,000+": "7", "$180,000+": "8", "$200,000+": "9"
                    }
                    if self.config.job_search.salary_range in salary_mapping:
                        params['f_SB2'] = salary_mapping[self.config.job_search.salary_range]
                
                # Build URL
                url_params = '&'.join([f"{k}={quote_plus(str(v))}" for k, v in params.items()])
                urls.append(f"{base_url}{url_params}")
        
        self.logger.info(f"🔗 Generated {len(urls)} job search URLs")
        return urls
    
    def process_job_search_results(self, url: str) -> List[str]:
        """Process job search results page and extract job URLs"""
        try:
            self.logger.info(f"🔗 Navigating to: {url}")
            self.driver.get(url)
            self.human_like_delay(3, 5)
            
            # Wait for page to load properly
            try:
                # Wait for either job results or main content to load
                self.wait.until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                self.human_like_delay(2, 3)
            except:
                pass
            
            # Check if we were redirected or if there's an error page
            current_url = self.driver.current_url
            if '/jobs/search' not in current_url:
                self.logger.warning(f"⚠️ Redirected from jobs search. Current URL: {current_url}")
                # Try alternative URL format
                return self._try_alternative_search_format(url)
            
            # Check for LinkedIn's job search page indicators
            page_indicators = [
                ".jobs-search", ".jobs-search-results", "[role='main']", 
                ".application-outlet", ".jobs-search-two-pane"
            ]
            
            page_loaded = False
            for indicator in page_indicators:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, indicator)
                    if element:
                        page_loaded = True
                        break
                except:
                    continue
            
            if not page_loaded:
                self.logger.warning("⚠️ LinkedIn jobs page may not have loaded correctly")
                self._debug_page_structure()
            
            # Extract keyword from URL for logging
            keyword = re.search(r'keywords=([^&]+)', url)
            keyword = keyword.group(1) if keyword else "Unknown"
            
            # Get total job count with multiple selectors
            total_jobs = "Unknown"
            job_count_selectors = [
                ".results-context-header__job-count",  # Old selector
                ".jobs-search-results-list__text",  # Current selector
                ".jobs-search__results-list h1",
                ".search-results-container h1",
                "[data-test-id='search-results-count']",
                ".jobs-search-results__count-string",
                "h1 span",  # Generic count in header
                ".jobs-search-two-pane__results-count"
            ]
            
            for count_selector in job_count_selectors:
                try:
                    job_count_elem = self.wait.until(EC.presence_of_element_located((
                        By.CSS_SELECTOR, count_selector
                    )), timeout=5)
                    total_jobs = job_count_elem.text
                    self.logger.info(f"📊 Found {total_jobs} jobs for keyword: {keyword}")
                    break
                except:
                    continue
            
            if total_jobs == "Unknown":
                self.logger.warning(f"⚠️ Could not determine job count for: {keyword}")
            
            job_urls = []
            page = 1
            max_pages = 5  # Limit pages to avoid being flagged
            
            while page <= max_pages:
                # Extract jobs from current page
                page_job_urls = self._extract_jobs_from_current_page()
                
                if not page_job_urls:
                    self.logger.warning(f"⚠️ No job URLs extracted from page {page}")
                    # Debug: Try to understand the page structure
                    self._debug_page_structure()
                    break
                
                # Add new URLs to our collection
                for job_url in page_job_urls:
                    if job_url not in job_urls:
                        job_urls.append(job_url)
                
                self.logger.info(f"📄 Page {page}: Found {len(page_job_urls)} job URLs")
                
                # Try to go to next page
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, ".artdeco-pagination__button--next")
                    if next_button.is_enabled():
                        self.safe_click(next_button)
                        self.human_like_delay(3, 5)
                        page += 1
                    else:
                        break
                except:
                    break
            
            self.logger.info(f"📋 Extracted {len(job_urls)} job URLs from {page} pages")
            return job_urls
            
        except Exception as e:
            self.logger.error(f"❌ Error processing search results: {e}")
            return []
    
    def _debug_page_structure(self):
        """Debug the current page structure to understand LinkedIn's layout"""
        try:
            current_url = self.driver.current_url
            self.logger.debug(f"🔍 Debugging page structure for URL: {current_url}")
            
            # Check if we're on the right page
            if '/jobs/search' not in current_url:
                self.logger.warning(f"⚠️ Not on jobs search page. Current URL: {current_url}")
                return
            
            # Look for common LinkedIn elements
            common_elements = [
                "main", "body", ".jobs-search", ".jobs-search-results", 
                "[role='main']", ".application-outlet", ".jobs-search-two-pane"
            ]
            
            for element_selector in common_elements:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, element_selector)
                    if elements:
                        self.logger.debug(f"✅ Found {len(elements)} elements for: {element_selector}")
                except:
                    continue
            
            # Look for any elements that might contain job listings
            potential_job_containers = [
                "[data-job-id]", "li[data-job-id]", ".job", ".card", 
                "[class*='job']", "[class*='card']", "[class*='result']",
                "article", ".entity-result"
            ]
            
            for container_selector in potential_job_containers:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, container_selector)
                    if elements:
                        self.logger.debug(f"🎯 Found {len(elements)} potential job containers for: {container_selector}")
                        # If we find elements with data-job-id, that's likely our target
                        if 'data-job-id' in container_selector and elements:
                            self.logger.info(f"💡 Try using selector: {container_selector}")
                except:
                    continue
            
            # Check if there's a captcha or rate limiting
            captcha_indicators = [
                ".captcha", "[class*='captcha']", ".challenge", "[class*='challenge']",
                ".security-challenge", "iframe[src*='captcha']"
            ]
            
            for captcha_selector in captcha_indicators:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, captcha_selector)
                    if elements and any(elem.is_displayed() for elem in elements):
                        self.logger.warning(f"🚨 Possible captcha/challenge detected: {captcha_selector}")
                except:
                    continue
            
            # Save a screenshot for debugging
            try:
                screenshot_path = f"logs/debug_page_{int(time.time())}.png"
                self.driver.save_screenshot(screenshot_path)
                self.logger.debug(f"📸 Page screenshot saved: {screenshot_path}")
            except:
                pass
                
        except Exception as e:
            self.logger.error(f"❌ Error in debug method: {e}")
    
    def _try_alternative_search_format(self, original_url: str) -> List[str]:
        """Try alternative URL formats if the original fails"""
        try:
            # Extract parameters from original URL
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(original_url)
            params = parse_qs(parsed.query)
            
            keywords = params.get('keywords', [''])[0]
            location = params.get('location', [''])[0]
            
            # Try simplified URL format
            simple_url = f"https://www.linkedin.com/jobs/search/?keywords={quote_plus(keywords)}&location={quote_plus(location)}"
            
            self.logger.info(f"🔄 Trying alternative URL format: {simple_url}")
            self.driver.get(simple_url)
            self.human_like_delay(3, 5)
            
            # Check if this worked better
            if '/jobs/search' in self.driver.current_url:
                self.logger.info("✅ Alternative URL format successful")
                # Try to extract jobs with this format
                return self._extract_jobs_from_current_page()
            else:
                self.logger.warning("❌ Alternative URL format also failed")
                return []
                
        except Exception as e:
            self.logger.error(f"❌ Error trying alternative search format: {e}")
            return []
    
    def _extract_jobs_from_current_page(self) -> List[str]:
        """Extract job URLs from current page using all available methods"""
        job_urls = []
        
        # Try all possible job card selectors
        job_card_selectors = [
            ".jobs-search-results__list-item",  # Most common current selector
            ".job-search-card",  # Legacy selector  
            ".job-card-container",
            ".jobs-search-results-list__list-item",
            "[data-job-id]",  # Any element with job ID
            ".jobs-search__results-list li",
            ".job-search-card-container",
            ".entity-result",  # Generic result item
            ".job-card-list",
            "li[class*='job']",  # Any li with 'job' in class name
            ".base-search-card"
        ]
        
        job_cards = []
        working_selector = None
        
        for selector in job_card_selectors:
            try:
                cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if cards:
                    job_cards = cards
                    working_selector = selector
                    self.logger.info(f"✅ Found {len(cards)} job cards using: {selector}")
                    break
            except:
                continue
        
        if not job_cards:
            self.logger.warning("❌ No job cards found with any selector")
            return []
        
        # Extract URLs from found cards
        for i, card in enumerate(job_cards):
            try:
                job_url = self._extract_job_url_from_card(card)
                if job_url and job_url not in job_urls:
                    job_urls.append(job_url)
                    self.logger.debug(f"✅ Extracted job {i+1}: {job_url}")
            except Exception as e:
                self.logger.debug(f"⚠️ Error extracting URL from card {i+1}: {e}")
                continue
        
        self.logger.info(f"📋 Successfully extracted {len(job_urls)} job URLs")
        return job_urls
    
    def _extract_job_url_from_card(self, card) -> Optional[str]:
        """Extract job URL from a single job card"""
        link_selectors = [
            ".job-card-list__title",  # Current most common
            ".job-search-card__title-link",  # Legacy
            ".job-card-container__link",
            ".jobs-search-results__list-item-link", 
            "a[data-job-id]",
            ".job-card-list__title-link",
            ".jobs-search-results__list-item h3 a",
            ".base-search-card__title-link",
            ".entity-result__title-text a",
            "h3 a",  # Generic title link
            "a[href*='/jobs/view/']",  # Any link with job view URL
            ".job-card-container__company-name + a",  # Link after company name
            "a[aria-label*='View job']"  # Accessible link
        ]
        
        for link_selector in link_selectors:
            try:
                job_link = card.find_element(By.CSS_SELECTOR, link_selector)
                if job_link:
                    job_url = job_link.get_attribute('href')
                    if job_url and '/jobs/view/' in job_url:
                        return job_url
            except:
                continue
        
        # Last resort: try to find any link in the card
        try:
            all_links = card.find_elements(By.TAG_NAME, 'a')
            for link in all_links:
                href = link.get_attribute('href')
                if href and '/jobs/view/' in href:
                    return href
        except:
            pass
        
        return None
    
    def should_apply_to_job(self, job_data: Dict) -> Tuple[bool, str]:
        """Determine if we should apply to this job based on filtering criteria"""
        
        # Check blacklisted companies
        company_name = job_data.get('company', '').lower()
        if any(blacklisted.lower() in company_name for blacklisted in self.config.filtering.blacklisted_companies):
            return False, f"Company '{job_data.get('company')}' is blacklisted"
        
        # Check whitelisted companies (if specified)
        if self.config.filtering.whitelisted_companies:
            if not any(whitelisted.lower() in company_name for whitelisted in self.config.filtering.whitelisted_companies):
                return False, f"Company '{job_data.get('company')}' not in whitelist"
        
        # Check blacklisted titles
        job_title = job_data.get('title', '').lower()
        if any(blacklisted.lower() in job_title for blacklisted in self.config.filtering.blacklisted_titles):
            return False, f"Job title contains blacklisted term"
        
        # Check whitelisted titles (if specified)
        if self.config.filtering.whitelisted_titles:
            if not any(whitelisted.lower() in job_title for whitelisted in self.config.filtering.whitelisted_titles):
                return False, f"Job title doesn't match whitelist"
        
        return True, "Passed all filters"
    
    def extract_job_data(self) -> Dict:
        """Extract job information from current job page"""
        job_data = {
            'title': 'N/A',
            'company': 'N/A',
            'location': 'N/A',
            'salary': 'N/A',
            'posted_date': 'N/A',
            'job_type': 'N/A',
            'description': 'N/A'
        }
        
        try:
            # Job title
            title_elem = self.driver.find_element(By.CSS_SELECTOR, "h1")
            job_data['title'] = title_elem.text.strip()
        except:
            pass
        
        try:
            # Company name
            company_elem = self.driver.find_element(By.CSS_SELECTOR, ".jobs-unified-top-card__company-name")
            job_data['company'] = company_elem.text.strip()
        except:
            pass
        
        try:
            # Location
            location_elem = self.driver.find_element(By.CSS_SELECTOR, ".jobs-unified-top-card__bullet")
            job_data['location'] = location_elem.text.strip()
        except:
            pass
        
        try:
            # Posted date
            posted_elem = self.driver.find_element(By.CSS_SELECTOR, ".jobs-unified-top-card__posted-date")
            job_data['posted_date'] = posted_elem.text.strip()
        except:
            pass
        
        try:
            # Job description (first 500 chars for filtering)
            desc_elem = self.driver.find_element(By.CSS_SELECTOR, ".jobs-box__html-content")
            job_data['description'] = desc_elem.text[:1000]
        except:
            pass
        
        return job_data
    
    def find_easy_apply_button(self) -> Optional[object]:
        """Find the Easy Apply button with multiple selectors"""
        selectors = [
            "button[aria-label*='Easy Apply']",
            ".jobs-apply-button",
            "button:contains('Easy Apply')",
            "button[data-job-id]",
            ".jobs-s-apply button"
        ]
        
        for selector in selectors:
            try:
                if ':contains(' in selector:
                    # Handle jQuery-style selector
                    elements = self.driver.find_elements(By.XPATH, f"//button[contains(text(), 'Easy Apply')]")
                    if elements:
                        return elements[0]
                else:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element and element.is_displayed():
                        return element
            except:
                continue
        
        return None
    
    def handle_application_form(self, job_data: Dict) -> Tuple[bool, str, int]:
        """Enhanced form handler with intelligent field filling"""
        try:
            self.logger.info(f"📝 Processing application form for: {job_data['title']}")
            
            max_steps = 8  # Prevent infinite loops
            current_step = 0
            fields_filled = 0
            
            while current_step < max_steps:
                current_step += 1
                self.logger.info(f"🔄 Processing form step {current_step}")
                
                # Try to proceed without filling first
                if self._try_next_step():
                    self.logger.info(f"✅ Proceeded to step {current_step + 1} without filling")
                    continue
                
                # Check for form errors or required fields
                errors = self._get_form_errors()
                if errors:
                    self.logger.info(f"⚠️ Found {len(errors)} form errors, attempting to fix...")
                    filled = self._handle_form_errors(job_data)
                    fields_filled += filled
                    
                    # Try next step again after fixing errors
                    if self._try_next_step():
                        continue
                
                # Look for required empty fields
                required_fields = self._find_required_fields()
                if required_fields:
                    self.logger.info(f"📋 Found {len(required_fields)} required fields to fill")
                    filled = self._fill_required_fields(required_fields, job_data)
                    fields_filled += filled
                    
                    # Try next step after filling required fields
                    if self._try_next_step():
                        continue
                
                # Check if we're at the final submission step
                if self._is_final_step():
                    return self._handle_final_submission(job_data), "Reached final submission", fields_filled
                
                # If we can't proceed, it might be a complex form
                if current_step > 3 and fields_filled == 0:
                    return False, "Complex form detected - skipping", 0
                
                # Small delay before next iteration
                self.human_like_delay(2, 4)
            
            return False, f"Maximum steps ({max_steps}) reached", fields_filled
            
        except Exception as e:
            self.logger.error(f"❌ Form handling error: {e}")
            return False, f"Form error: {str(e)[:100]}", 0
    
    def _try_next_step(self) -> bool:
        """Try to proceed to the next step"""
        button_selectors = [
            "button[aria-label='Continue to next step']",
            "button[aria-label='Continue']",
            "button[data-easy-apply-next-button]",
            "//button[contains(text(), 'Next')]",
            "//button[contains(text(), 'Continue')]",
            "//button[contains(text(), 'Review')]",
            ".jobs-easy-apply-footer button:not([disabled])"
        ]
        
        initial_url = self.driver.current_url
        
        for selector in button_selectors:
            try:
                if selector.startswith('//'):
                    elements = self.driver.find_elements(By.XPATH, selector)
                else:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        if self.safe_click(element):
                            self.human_like_delay(2, 4)
                            
                            # Check if page changed
                            if self.driver.current_url != initial_url or self._page_content_changed():
                                return True
            except:
                continue
        
        return False
    
    def _page_content_changed(self) -> bool:
        """Check if page content has changed (simple heuristic)"""
        try:
            # Look for new form elements or changes in form structure
            current_forms = len(self.driver.find_elements(By.TAG_NAME, "form"))
            current_inputs = len(self.driver.find_elements(By.TAG_NAME, "input"))
            
            # Store previous counts if not exists
            if not hasattr(self, '_prev_forms'):
                self._prev_forms = current_forms
                self._prev_inputs = current_inputs
                return False
            
            changed = (current_forms != self._prev_forms or 
                      abs(current_inputs - self._prev_inputs) > 2)
            
            self._prev_forms = current_forms
            self._prev_inputs = current_inputs
            
            return changed
        except:
            return True  # Assume changed if we can't determine
    
    def _get_form_errors(self) -> List[str]:
        """Get form validation errors"""
        error_selectors = [
            ".artdeco-inline-feedback--error",
            ".form-element-validation-error",
            "[aria-describedby*='error']",
            ".error-message",
            "[role='alert']"
        ]
        
        errors = []
        for selector in error_selectors:
            try:
                error_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in error_elements:
                    if elem.is_displayed():
                        errors.append(elem.text.strip())
            except:
                continue
        
        return errors
    
    def _handle_form_errors(self, job_data: Dict) -> int:
        """Handle form validation errors"""
        error_fields = self._find_error_fields()
        if not error_fields:
            return 0
        
        fields_filled = 0
        for field in error_fields:
            try:
                label = self._get_field_label(field)
                if self._fill_field_intelligently(field, label, job_data):
                    fields_filled += 1
                    self.human_like_delay(0.5, 1.0)
            except Exception as e:
                self.logger.debug(f"⚠️ Error filling error field: {e}")
                continue
        
        return fields_filled
    
    def _find_error_fields(self) -> List[object]:
        """Find form fields with validation errors"""
        error_field_selectors = [
            "input[aria-invalid='true']",
            "textarea[aria-invalid='true']",
            "select[aria-invalid='true']",
            ".form-element--error input",
            ".form-element--error textarea",
            ".form-element--error select",
            "input[class*='error']",
            "select[class*='error']",
            "textarea[class*='error']"
        ]
        
        error_fields = []
        for selector in error_field_selectors:
            try:
                fields = self.driver.find_elements(By.CSS_SELECTOR, selector)
                error_fields.extend([f for f in fields if f.is_displayed()])
            except:
                continue
        
        return error_fields
    
    def _find_required_fields(self) -> List[object]:
        """Find required empty fields"""
        required_selectors = [
            "input[required]",
            "textarea[required]",
            "select[required]",
            "input[aria-required='true']",
            "textarea[aria-required='true']",
            "select[aria-required='true']"
        ]
        
        required_fields = []
        for selector in required_selectors:
            try:
                fields = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for field in fields:
                    if field.is_displayed() and self._is_field_empty(field):
                        required_fields.append(field)
            except:
                continue
        
        return required_fields
    
    def _is_field_empty(self, field) -> bool:
        """Check if a field is empty"""
        try:
            if field.tag_name == 'select':
                selected = Select(field).first_selected_option
                return not selected.get_attribute('value') or selected.get_attribute('value') == ''
            elif field.get_attribute('type') == 'checkbox':
                return not field.is_selected()
            elif field.get_attribute('type') == 'radio':
                name = field.get_attribute('name')
                if name:
                    radios = self.driver.find_elements(By.NAME, name)
                    return not any(r.is_selected() for r in radios)
                return not field.is_selected()
            else:
                value = field.get_attribute('value')
                return not value or value.strip() == ''
        except:
            return True
    
    def _fill_required_fields(self, fields: List[object], job_data: Dict) -> int:
        """Fill required fields intelligently"""
        fields_filled = 0
        
        for field in fields:
            try:
                label = self._get_field_label(field)
                if self._fill_field_intelligently(field, label, job_data):
                    fields_filled += 1
                    self.human_like_delay(0.5, 1.5)
            except Exception as e:
                self.logger.debug(f"⚠️ Error filling required field: {e}")
                continue
        
        return fields_filled
    
    def _get_field_label(self, element) -> str:
        """Get label text for form element"""
        try:
            # Try to find associated label by ID
            element_id = element.get_attribute('id')
            if element_id:
                try:
                    label = self.driver.find_element(By.XPATH, f"//label[@for='{element_id}']")
                    return label.text.strip()
                except:
                    pass
            
            # Try aria-label
            aria_label = element.get_attribute('aria-label')
            if aria_label:
                return aria_label.strip()
            
            # Try aria-labelledby
            aria_labelledby = element.get_attribute('aria-labelledby')
            if aria_labelledby:
                try:
                    label_elem = self.driver.find_element(By.ID, aria_labelledby)
                    return label_elem.text.strip()
                except:
                    pass
            
            # Look in parent containers
            try:
                parent = element.find_element(By.XPATH, "./..")
                label_elem = parent.find_element(By.TAG_NAME, "label")
                return label_elem.text.strip()
            except:
                pass
            
            # Try placeholder
            placeholder = element.get_attribute('placeholder')
            if placeholder:
                return placeholder.strip()
            
            # Try name attribute
            name = element.get_attribute('name')
            if name:
                return name.replace('_', ' ').replace('-', ' ').title()
            
            return ""
            
        except Exception as e:
            self.logger.debug(f"⚠️ Error getting field label: {e}")
            return ""
    
    def _fill_field_intelligently(self, field, label: str, job_data: Dict) -> bool:
        """Fill field using AI agent"""
        try:
            # Get options for select/radio fields
            options = []
            if field.tag_name == 'select':
                select_obj = Select(field)
                options = [opt.text.strip() for opt in select_obj.options if opt.text.strip()]
            
            # Get AI response
            response = self.ai_agent.get_smart_answer(
                question=label,
                options=options if options else None,
                job_context=job_data
            )
            
            if not response.answer:
                return False
            
            # Fill field based on type
            if field.tag_name == 'select':
                return self._fill_select_field(field, response.answer, options)
            elif field.get_attribute('type') == 'radio':
                return self._fill_radio_field(field, response.answer, label)
            elif field.get_attribute('type') == 'checkbox':
                return self._fill_checkbox_field(field, response.answer)
            elif field.tag_name in ['input', 'textarea']:
                return self.safe_type(field, response.answer)
            
            return False
            
        except Exception as e:
            self.logger.debug(f"⚠️ Error filling field intelligently: {e}")
            return False
    
    def _fill_select_field(self, field, answer: str, options: List[str]) -> bool:
        """Fill select field"""
        try:
            select_obj = Select(field)
            
            # Try exact match
            for option in select_obj.options:
                if option.text.strip().lower() == answer.lower():
                    select_obj.select_by_visible_text(option.text.strip())
                    return True
            
            # Try partial match
            for option in select_obj.options:
                if answer.lower() in option.text.strip().lower():
                    select_obj.select_by_visible_text(option.text.strip())
                    return True
            
            # Try to select by value
            if answer.isdigit():
                try:
                    select_obj.select_by_value(answer)
                    return True
                except:
                    pass
            
            return False
            
        except Exception as e:
            self.logger.debug(f"⚠️ Error filling select field: {e}")
            return False
    
    def _fill_radio_field(self, field, answer: str, label: str) -> bool:
        """Fill radio field"""
        try:
            name = field.get_attribute('name')
            if not name:
                return False
            
            radio_buttons = self.driver.find_elements(By.NAME, name)
            
            # Look for matching radio button
            for radio in radio_buttons:
                try:
                    radio_label = self._get_field_label(radio)
                    if (answer.lower() in radio_label.lower() or 
                        radio_label.lower() in answer.lower()):
                        if self.safe_click(radio):
                            return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            self.logger.debug(f"⚠️ Error filling radio field: {e}")
            return False
    
    def _fill_checkbox_field(self, field, answer: str) -> bool:
        """Fill checkbox field"""
        try:
            should_check = answer.lower() in ['yes', 'true', '1', 'on', 'checked']
            
            if should_check and not field.is_selected():
                return self.safe_click(field)
            elif not should_check and field.is_selected():
                return self.safe_click(field)
            
            return True  # Already in correct state
            
        except Exception as e:
            self.logger.debug(f"⚠️ Error filling checkbox field: {e}")
            return False
    
    def _is_final_step(self) -> bool:
        """Check if we're at the final submission step"""
        final_indicators = [
            "button[aria-label='Submit application']",
            "button[aria-label='Review your application']",
            "//button[contains(text(), 'Submit application')]",
            "//button[contains(text(), 'Submit Application')]",
            "//button[contains(text(), 'Submit')]",
            "//span[contains(text(), 'Application sent')]"
        ]
        
        for selector in final_indicators:
            try:
                if selector.startswith('//'):
                    elements = self.driver.find_elements(By.XPATH, selector)
                else:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                if any(elem.is_displayed() for elem in elements):
                    return True
            except:
                continue
        
        return False
    
    def _handle_final_submission(self, job_data: Dict) -> bool:
        """Handle final submission step"""
        try:
            self.logger.info("📝 Handling final submission...")
            
            # Unfollow company if configured
            if not self.config.application_prefs.follow_companies:
                self._unfollow_company()
            
            # Find and click submit button
            submit_selectors = [
                "button[aria-label='Submit application']",
                "button[data-easy-apply-submit-button]",
                "//button[contains(text(), 'Submit application')]",
                "//button[contains(text(), 'Submit Application')]",
                "//button[contains(text(), 'Submit')]"
            ]
            
            for selector in submit_selectors:
                try:
                    if selector.startswith('//'):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            if self.safe_click(element):
                                self.human_like_delay(3, 5)
                                
                                # Check for success indicators
                                if self._check_application_success():
                                    return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Final submission error: {e}")
            return False
    
    def _unfollow_company(self):
        """Unfollow company during application process"""
        try:
            unfollow_selectors = [
                "button[aria-label*='Unfollow']",
                "//button[contains(text(), 'Unfollow')]",
                ".follow-button[aria-pressed='true']"
            ]
            
            for selector in unfollow_selectors:
                try:
                    if selector.startswith('//'):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if element.is_displayed():
                            self.safe_click(element)
                            self.human_like_delay(0.5, 1.0)
                            return
                except:
                    continue
        except:
            pass  # Not critical if unfollowing fails
    
    def _check_application_success(self) -> bool:
        """Check if application was submitted successfully"""
        success_indicators = [
            "//span[contains(text(), 'Application sent')]",
            "//span[contains(text(), 'Application submitted')]",
            ".jobs-easy-apply-success-modal",
            "[data-test-modal-id*='success']"
        ]
        
        for selector in success_indicators:
            try:
                if selector.startswith('//'):
                    elements = self.driver.find_elements(By.XPATH, selector)
                else:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                if any(elem.is_displayed() for elem in elements):
                    return True
            except:
                continue
        
        return False
    
    def apply_to_job(self, job_url: str) -> JobApplication:
        """Apply to a single job"""
        job_id = job_url.split('/')[-1].split('?')[0]
        
        try:
            # Navigate to job
            self.driver.get(job_url)
            self.human_like_delay(3, 5)
            
            # Extract job data
            job_data = self.extract_job_data()
            self.logger.info(f"🎯 Processing: {job_data['title']} at {job_data['company']}")
            
            # Check if we should apply to this job
            should_apply, reason = self.should_apply_to_job(job_data)
            if not should_apply:
                self.stats.skipped_applications += 1
                return JobApplication(
                    job_id=job_id,
                    title=job_data['title'],
                    company=job_data['company'],
                    location=job_data['location'],
                    salary=job_data.get('salary', 'N/A'),
                    posted_date=job_data.get('posted_date', 'N/A'),
                    application_date=datetime.now(),
                    status='skipped',
                    reason=reason,
                    application_url=job_url
                )
            
            # Find Easy Apply button
            easy_apply_button = self.find_easy_apply_button()
            if not easy_apply_button:
                self.stats.skipped_applications += 1
                return JobApplication(
                    job_id=job_id,
                    title=job_data['title'],
                    company=job_data['company'],
                    location=job_data['location'],
                    salary=job_data.get('salary', 'N/A'),
                    posted_date=job_data.get('posted_date', 'N/A'),
                    application_date=datetime.now(),
                    status='skipped',
                    reason='No Easy Apply button found',
                    application_url=job_url
                )
            
            # Click Easy Apply
            if not self.safe_click(easy_apply_button):
                self.stats.failed_applications += 1
                return JobApplication(
                    job_id=job_id,
                    title=job_data['title'],
                    company=job_data['company'],
                    location=job_data['location'],
                    salary=job_data.get('salary', 'N/A'),
                    posted_date=job_data.get('posted_date', 'N/A'),
                    application_date=datetime.now(),
                    status='failed',
                    reason='Could not click Easy Apply button',
                    application_url=job_url
                )
            
            self.human_like_delay(2, 4)
            
            # Handle application form
            success, reason, fields_filled = self.handle_application_form(job_data)
            
            if success:
                self.stats.successful_applications += 1
                status = 'applied'
                self.logger.info(f"✅ Successfully applied to {job_data['title']} at {job_data['company']}")
            else:
                if 'complex form' in reason.lower():
                    self.stats.complex_forms_skipped += 1
                    status = 'skipped'
                else:
                    self.stats.failed_applications += 1
                    status = 'failed'
                self.logger.warning(f"❌ Failed to apply: {reason}")
            
            return JobApplication(
                job_id=job_id,
                title=job_data['title'],
                company=job_data['company'],
                location=job_data['location'],
                salary=job_data.get('salary', 'N/A'),
                posted_date=job_data.get('posted_date', 'N/A'),
                application_date=datetime.now(),
                status=status,
                reason=reason,
                form_fields_filled=fields_filled,
                application_url=job_url
            )
            
        except Exception as e:
            self.stats.failed_applications += 1
            self.logger.error(f"❌ Error applying to job {job_url}: {e}")
            
            return JobApplication(
                job_id=job_id,
                title='Error extracting title',
                company='Error extracting company',
                location='N/A',
                salary='N/A',
                posted_date='N/A',
                application_date=datetime.now(),
                status='failed',
                reason=f'Exception: {str(e)[:100]}',
                application_url=job_url
            )
    
    def run_application_session(self):
        """Run complete job application session"""
        try:
            self.logger.info("🚀 Starting Enhanced LinkedIn Job Application Session")
            
            # Setup browser and login
            self.setup_browser()
            if not self.login():
                self.logger.error("❌ Login failed, exiting...")
                return
            
            # Generate job search URLs
            search_urls = self.generate_job_search_urls()
            self.logger.info(f"🔗 Generated {len(search_urls)} search URLs")
            
            # Process each search URL
            all_job_urls = []
            for i, url in enumerate(search_urls[:5]):  # Limit to first 5 search URLs
                self.logger.info(f"🔍 Processing search URL {i+1}/{min(5, len(search_urls))}")
                job_urls = self.process_job_search_results(url)
                all_job_urls.extend(job_urls)
                
                # Add delay between searches
                self.human_like_delay(5, 10)
                
                # Stop if we have enough jobs
                if len(all_job_urls) >= 100:  # Limit to 100 jobs per session
                    break
            
            self.logger.info(f"📋 Total jobs to process: {len(all_job_urls)}")
            
            # Apply to jobs
            for i, job_url in enumerate(all_job_urls):
                # Check daily limit
                if self.stats.successful_applications >= self.config.application_prefs.max_applications_per_day:
                    self.logger.info(f"🎯 Reached daily application limit ({self.config.application_prefs.max_applications_per_day})")
                    break
                
                self.logger.info(f"📝 Processing job {i+1}/{len(all_job_urls)}")
                self.stats.total_jobs_processed += 1
                
                # Apply to job
                application = self.apply_to_job(job_url)
                self.applied_jobs.append(application)
                
                # Add delay between applications
                delay_min, delay_max = self.config.application_prefs.delay_between_applications
                self.human_like_delay(delay_min, delay_max)
                
                # Save progress periodically
                if i % 10 == 0:
                    self._save_session_data()
            
            # Final statistics
            self.stats.end_time = datetime.now()
            self._print_session_summary()
            
            # Save final data
            self._save_session_data()
            self._export_application_data()
            
        except Exception as e:
            self.logger.error(f"❌ Session error: {e}")
        
        finally:
            if self.driver:
                self.driver.quit()
                self.logger.info("🔚 Browser session closed")
    
    def _print_session_summary(self):
        """Print session summary statistics"""
        duration = (self.stats.end_time - self.stats.start_time).total_seconds() / 60
        
        print("\n" + "="*60)
        print("📊 SESSION SUMMARY")
        print("="*60)
        print(f"⏱️  Duration: {duration:.1f} minutes")
        print(f"📋 Total Jobs Processed: {self.stats.total_jobs_processed}")
        print(f"✅ Successful Applications: {self.stats.successful_applications}")
        print(f"❌ Failed Applications: {self.stats.failed_applications}")
        print(f"⏭️  Skipped Applications: {self.stats.skipped_applications}")
        print(f"🔄 Complex Forms Skipped: {self.stats.complex_forms_skipped}")
        
        if self.stats.total_jobs_processed > 0:
            success_rate = (self.stats.successful_applications / self.stats.total_jobs_processed) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print("="*60)
    
    def _export_application_data(self):
        """Export application data to file"""
        if not self.applied_jobs:
            return
        
        try:
            os.makedirs(self.config.logging.data_dir, exist_ok=True)
            
            # CSV export
            import csv
            csv_file = f"{self.config.logging.data_dir}/applications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Job ID', 'Title', 'Company', 'Location', 'Salary', 'Posted Date',
                    'Application Date', 'Status', 'Reason', 'Fields Filled', 'URL'
                ])
                
                for app in self.applied_jobs:
                    writer.writerow([
                        app.job_id, app.title, app.company, app.location, app.salary,
                        app.posted_date, app.application_date.strftime('%Y-%m-%d %H:%M:%S'),
                        app.status, app.reason, app.form_fields_filled, app.application_url
                    ])
            
            self.logger.info(f"📄 Application data exported to: {csv_file}")
            
        except Exception as e:
            self.logger.error(f"❌ Error exporting application data: {e}")

def main():
    """Main entry point"""
    try:
        # Load configuration
        from config_enhanced import config
        
        # Validate configuration
        errors = config.validate()
        if errors:
            print("❌ Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            return
        
        print("🚀 Enhanced LinkedIn Job Application Bot")
        print(f"📊 Configuration loaded successfully")
        print(f"👤 Profile: {config.personal_info.full_name}")
        print(f"🎯 Max applications per day: {config.application_prefs.max_applications_per_day}")
        print(f"🔍 Job keywords: {', '.join(config.job_search.keywords[:5])}...")
        
        # Create and run bot
        bot = EnhancedLinkedInBot(config)
        bot.run_application_session()
        
    except KeyboardInterrupt:
        print("\n⚠️ Session interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logging.exception("Full error details:")

if __name__ == "__main__":
    main()