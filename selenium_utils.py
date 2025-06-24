"""
Selenium utilities for robust web driver management
"""

import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    WebDriverException, 
    NoSuchElementException,
    SessionNotCreatedException
)
from webdriver_manager.chrome import ChromeDriverManager
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class WebDriverManager:
    """Manages Chrome WebDriver instances with robust error handling"""
    
    def __init__(self, headless: bool = True, timeout: int = 10):
        self.headless = headless
        self.timeout = timeout
        self.driver: Optional[webdriver.Chrome] = None
        self.logger = logging.getLogger(__name__)
    
    def setup_driver(self) -> bool:
        """Setup Chrome WebDriver with optimized configurations"""
        try:
            chrome_options = Options()
            
            # Basic options
            if self.headless:
                chrome_options.add_argument("--headless")
            
            # Performance and stability optimizations
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            
            # Disable loading of images, CSS, and JavaScript for faster crawling
            prefs = {
                "profile.managed_default_content_settings.images": 2,
                "profile.default_content_setting_values.notifications": 2,
                "profile.managed_default_content_settings.stylesheets": 2,
                "profile.managed_default_content_settings.javascript": 1,  # Keep JS for dynamic content
                "profile.managed_default_content_settings.plugins": 2,
                "profile.managed_default_content_settings.popups": 2,
                "profile.managed_default_content_settings.geolocation": 2,
                "profile.managed_default_content_settings.media_stream": 2,
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Additional performance options
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-features=TranslateUI")
            chrome_options.add_argument("--disable-default-apps")
            
            # Memory and CPU optimizations
            chrome_options.add_argument("--memory-pressure-off")
            chrome_options.add_argument("--max_old_space_size=4096")
            chrome_options.add_argument("--aggressive-cache-discard")
            
            # User agent
            # Set user agent from environment
            user_agent = os.getenv('USER_AGENT', 'ResearchCrawler/2.0 (Educational Purpose; Selenium)')
            chrome_options.add_argument(f"--user-agent={user_agent}")
            
            # Automation flags
            chrome_options.add_experimental_option("useAutomationExtension", False)
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            
            # Page load strategy
            chrome_options.page_load_strategy = 'eager'  # Don't wait for all resources
            
            # Setup service
            service = Service(ChromeDriverManager().install())
            
            # Create driver
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Set timeouts
            self.driver.set_page_load_timeout(self.timeout)
            self.driver.implicitly_wait(5)
            
            # Execute script to remove automation detection
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.logger.info("✅ Chrome WebDriver initialized successfully")
            return True
            
        except SessionNotCreatedException as e:
            self.logger.error(f"❌ Failed to create WebDriver session: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Failed to setup WebDriver: {e}")
            return False
    
    def get_page(self, url: str, wait_for_element: str = "body") -> bool:
        """Navigate to a page and wait for it to load"""
        if not self.driver:
            self.logger.error("WebDriver not initialized")
            return False
        
        try:
            self.logger.debug(f"🌐 Navigating to: {url}")
            self.driver.get(url)
            
            # Wait for page to load
            wait = WebDriverWait(self.driver, self.timeout)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, wait_for_element)))
            
            # Additional wait for dynamic content
            time.sleep(1)
            
            return True
            
        except TimeoutException:
            self.logger.warning(f"⏰ Timeout loading page: {url}")
            return False
        except WebDriverException as e:
            self.logger.error(f"🚫 WebDriver error loading {url}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Error loading {url}: {e}")
            return False
    
    def get_page_source(self) -> str:
        """Get the current page source"""
        if not self.driver:
            return ""
        
        try:
            return self.driver.page_source
        except Exception as e:
            self.logger.error(f"Error getting page source: {e}")
            return ""
    
    def get_current_url(self) -> str:
        """Get the current URL"""
        if not self.driver:
            return ""
        
        try:
            return self.driver.current_url
        except Exception as e:
            self.logger.error(f"Error getting current URL: {e}")
            return ""
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("🔒 WebDriver closed successfully")
            except Exception as e:
                self.logger.error(f"Error closing WebDriver: {e}")
            finally:
                self.driver = None
    
    def restart_driver(self) -> bool:
        """Restart the WebDriver (useful when it becomes unresponsive)"""
        self.logger.info("🔄 Restarting WebDriver...")
        self.close()
        time.sleep(2)
        return self.setup_driver()
    
    def is_alive(self) -> bool:
        """Check if the WebDriver is still alive and responsive"""
        if not self.driver:
            return False
        
        try:
            # Try to get current URL to test responsiveness
            _ = self.driver.current_url
            return True
        except Exception:
            return False
    
    def __enter__(self):
        """Context manager entry"""
        if self.setup_driver():
            return self
        else:
            raise RuntimeError("Failed to initialize WebDriver")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


def create_driver_manager(headless: bool = True, timeout: int = 10) -> WebDriverManager:
    """Factory function to create a WebDriverManager instance"""
    return WebDriverManager(headless=headless, timeout=timeout)


def test_driver_setup():
    """Test function to verify WebDriver setup"""
    logging.basicConfig(level=logging.INFO)
    
    try:
        with create_driver_manager(headless=True) as driver_manager:
            test_url = "https://httpbin.org/html"
            if driver_manager.get_page(test_url):
                source = driver_manager.get_page_source()
                print(f"✅ Successfully loaded {test_url}")
                print(f"📄 Page source length: {len(source)} characters")
                return True
            else:
                print(f"❌ Failed to load {test_url}")
                return False
    except Exception as e:
        print(f"❌ Driver test failed: {e}")
        return False


if __name__ == "__main__":
    test_driver_setup()
