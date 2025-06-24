"""
Enhanced Selenium utilities for deployment environments
Handles common deployment issues like missing Chrome, display issues, etc.
"""

import os
import time
import logging
import subprocess
import sys
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

class DeploymentWebDriverManager:
    """Enhanced WebDriver manager for deployment environments"""
    
    def __init__(self, headless: bool = True, timeout: int = 10):
        self.headless = headless
        self.timeout = timeout
        self.driver: Optional[webdriver.Chrome] = None
        self.logger = logging.getLogger(__name__)
        self._setup_environment()
    
    def _setup_environment(self):
        """Setup environment variables for deployment"""
        # Set display for headless environments
        if not os.getenv('DISPLAY') and self.headless:
            os.environ['DISPLAY'] = ':99'
        
        # Chrome options for different environments
        self.chrome_binary_paths = [
            '/usr/bin/google-chrome',
            '/usr/bin/google-chrome-stable',
            '/usr/bin/chromium',
            '/usr/bin/chromium-browser',
            '/opt/google/chrome/chrome',
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            'google-chrome',
            'chromium'
        ]
    
    def _find_chrome_executable(self) -> Optional[str]:
        """Find Chrome executable in various locations"""
        for path in self.chrome_binary_paths:
            try:
                if os.path.exists(path):
                    self.logger.info(f"Found Chrome at: {path}")
                    return path
                    
                # Try running it as a command
                result = subprocess.run(['which', path], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    chrome_path = result.stdout.strip()
                    self.logger.info(f"Found Chrome via which: {chrome_path}")
                    return chrome_path
                    
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                continue
        
        self.logger.warning("Chrome executable not found in standard locations")
        return None
    
    def _get_deployment_chrome_options(self) -> Options:
        """Get Chrome options optimized for deployment environments"""
        chrome_options = Options()
        
        # Find Chrome binary
        chrome_binary = self._find_chrome_executable()
        if chrome_binary:
            chrome_options.binary_location = chrome_binary
        
        # Essential options for deployment
        if self.headless:
            chrome_options.add_argument("--headless")
        
        # Deployment-friendly options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        
        # Performance optimizations
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
            "profile.managed_default_content_settings.javascript": 1,
            "profile.managed_default_content_settings.plugins": 2,
            "profile.managed_default_content_settings.popups": 2,
            "profile.managed_default_content_settings.geolocation": 2,
            "profile.managed_default_content_settings.media_stream": 2,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Anti-detection
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # User agent
        user_agent = os.getenv('USER_AGENT', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        chrome_options.add_argument(f"--user-agent={user_agent}")
        
        # Memory and stability options
        chrome_options.add_argument("--memory-pressure-off")
        chrome_options.add_argument("--max_old_space_size=4096")
        chrome_options.add_argument("--single-process")  # For low-resource environments
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        
        return chrome_options
    
    def setup_driver(self) -> bool:
        """Setup Chrome WebDriver with deployment optimizations"""
        try:
            chrome_options = self._get_deployment_chrome_options()
            
            # Try to install/get ChromeDriver
            try:
                service = Service(ChromeDriverManager().install())
            except Exception as e:
                self.logger.warning(f"ChromeDriverManager failed: {e}, trying system chromedriver")
                # Try system chromedriver
                chromedriver_paths = ['/usr/bin/chromedriver', '/usr/local/bin/chromedriver']
                service = None
                for path in chromedriver_paths:
                    if os.path.exists(path):
                        service = Service(path)
                        break
                
                if not service:
                    raise Exception("ChromeDriver not found")
            
            # Create driver with options
            if service:
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                self.driver = webdriver.Chrome(options=chrome_options)
            
            # Set timeouts
            self.driver.set_page_load_timeout(self.timeout)
            self.driver.implicitly_wait(5)
            
            # Test the driver
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.logger.info("✅ Chrome WebDriver initialized successfully for deployment")
            return True
            
        except SessionNotCreatedException as e:
            self.logger.error(f"❌ Failed to create WebDriver session: {e}")
            return self._try_alternative_setup()
        except Exception as e:
            self.logger.error(f"❌ Failed to setup WebDriver: {e}")
            return self._try_alternative_setup()
    
    def _try_alternative_setup(self) -> bool:
        """Try alternative WebDriver setup methods"""
        try:
            self.logger.info("🔄 Trying alternative WebDriver setup...")
            
            # Minimal Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # Try without service
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(self.timeout)
            
            self.logger.info("✅ Alternative WebDriver setup successful")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Alternative setup also failed: {e}")
            return False
    
    def get_page(self, url: str, wait_for_element: str = "body") -> bool:
        """Navigate to a page with robust error handling"""
        if not self.driver:
            self.logger.error("WebDriver not initialized")
            return False
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.logger.debug(f"🌐 Navigating to: {url} (attempt {attempt + 1})")
                self.driver.get(url)
                
                # Wait for page to load
                wait = WebDriverWait(self.driver, self.timeout)
                wait.until(EC.presence_of_element_located((By.TAG_NAME, wait_for_element)))
                
                # Additional wait for dynamic content
                time.sleep(1)
                
                return True
                
            except TimeoutException:
                self.logger.warning(f"⏰ Timeout loading page: {url} (attempt {attempt + 1})")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
            except WebDriverException as e:
                self.logger.error(f"🚫 WebDriver error loading {url}: {e}")
                if "chrome not reachable" in str(e).lower() and attempt < max_retries - 1:
                    # Try to restart driver
                    if self.restart_driver():
                        continue
            except Exception as e:
                self.logger.error(f"❌ Error loading {url}: {e}")
                
        return False
    
    def get_page_source(self) -> str:
        """Get page source with error handling"""
        if not self.driver:
            return ""
        
        try:
            return self.driver.page_source
        except Exception as e:
            self.logger.error(f"Error getting page source: {e}")
            return ""
    
    def get_current_url(self) -> str:
        """Get current URL with error handling"""
        if not self.driver:
            return ""
        
        try:
            return self.driver.current_url
        except Exception as e:
            self.logger.error(f"Error getting current URL: {e}")
            return ""
    
    def close(self):
        """Close WebDriver safely"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("🔒 WebDriver closed successfully")
            except Exception as e:
                self.logger.error(f"Error closing WebDriver: {e}")
            finally:
                self.driver = None
    
    def restart_driver(self) -> bool:
        """Restart WebDriver"""
        self.logger.info("🔄 Restarting WebDriver...")
        self.close()
        time.sleep(3)
        return self.setup_driver()
    
    def is_alive(self) -> bool:
        """Check if WebDriver is alive"""
        if not self.driver:
            return False
        
        try:
            _ = self.driver.current_url
            return True
        except Exception:
            return False
    
    def __enter__(self):
        """Context manager entry"""
        if self.setup_driver():
            return self
        else:
            raise RuntimeError("Failed to initialize WebDriver for deployment")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


def test_deployment_driver():
    """Test deployment WebDriver setup"""
    logging.basicConfig(level=logging.INFO)
    
    try:
        with DeploymentWebDriverManager(headless=True) as driver_manager:
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
        print(f"❌ Deployment driver test failed: {e}")
        return False


if __name__ == "__main__":
    test_deployment_driver()
