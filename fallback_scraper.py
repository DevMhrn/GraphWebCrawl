"""
Fallback web scraper using requests when Selenium fails
"""

import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import Optional, Dict, Any
from urllib.parse import urljoin, urlparse
import os
from dotenv import load_dotenv

load_dotenv()

class FallbackScraper:
    """Simple requests-based scraper as fallback when Selenium fails"""
    
    def __init__(self, timeout: int = 10, delay: float = 1.0):
        self.timeout = timeout
        self.delay = delay
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        
        # Set headers to avoid blocking
        user_agent = os.getenv('USER_AGENT', 
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def get_page_content(self, url: str) -> Optional[Dict[str, Any]]:
        """Get page content using requests"""
        try:
            self.logger.info(f"🌐 Fetching with requests: {url}")
            
            # Add delay between requests
            time.sleep(self.delay)
            
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()
            
            # Parse content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else url
            
            # Extract main content
            content = self._extract_main_content(soup)
            
            # Extract links
            links = self._extract_links(soup, url)
            
            if len(content) < 100:
                self.logger.warning(f"⚠️  Minimal content extracted from {url}")
                return None
            
            self.logger.info(f"✅ Successfully scraped: {url} ({len(content)} chars, {len(links)} links)")
            
            return {
                'url': url,
                'title': title,
                'content': content,
                'links': links,
                'method': 'requests'
            }
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Request failed for {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Error scraping {url}: {e}")
            return None
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main text content from page"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
            script.decompose()
        
        # Try to find main content areas
        content_selectors = [
            'main', 'article', '[role="main"]', 
            '.content', '.main-content', '.article-body',
            '.post-content', '.entry-content', '.page-content'
        ]
        
        main_content = None
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        # Fallback to body if no main content found
        if not main_content:
            main_content = soup.find('body')
        
        if main_content:
            # Get text and clean it
            text = main_content.get_text(separator=' ', strip=True)
            # Remove extra whitespace
            text = ' '.join(text.split())
            return text[:5000]  # Limit to 5000 characters
        
        return ""
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> list:
        """Extract links from page"""
        links = []
        base_domain = urlparse(base_url).netloc
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Convert relative URLs to absolute
            absolute_url = urljoin(base_url, href)
            
            # Filter out unwanted links
            if self._is_valid_link(absolute_url, base_domain):
                links.append(absolute_url)
        
        # Remove duplicates and limit
        unique_links = list(dict.fromkeys(links))
        return unique_links[:15]
    
    def _is_valid_link(self, url: str, base_domain: str) -> bool:
        """Check if link is valid for crawling"""
        try:
            parsed = urlparse(url)
            
            # Must be http/https
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # Skip certain file types
            skip_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', 
                             '.zip', '.rar', '.tar', '.gz', '.jpg', '.jpeg', '.png', 
                             '.gif', '.svg', '.mp3', '.mp4', '.avi', '.mov']
            
            if any(url.lower().endswith(ext) for ext in skip_extensions):
                return False
            
            # Skip certain URL patterns
            skip_patterns = ['mailto:', 'tel:', 'javascript:', '#', 'void(0)']
            if any(pattern in url.lower() for pattern in skip_patterns):
                return False
            
            return True
            
        except Exception:
            return False


def test_fallback_scraper():
    """Test the fallback scraper"""
    scraper = FallbackScraper()
    
    test_urls = [
        "https://httpbin.org/html",
        "https://en.wikipedia.org/wiki/Web_scraping",
        "https://www.w3.org/"
    ]
    
    for url in test_urls:
        result = scraper.get_page_content(url)
        if result:
            print(f"✅ {url}: {len(result['content'])} chars, {len(result['links'])} links")
        else:
            print(f"❌ {url}: Failed")


if __name__ == "__main__":
    test_fallback_scraper()
