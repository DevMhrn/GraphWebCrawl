import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque, defaultdict
import time
import logging
from typing import List, Dict, Set, Tuple, Optional
import validators
from dataclasses import dataclass
import re

@dataclass
class PageInfo:
    url: str
    title: str
    content: str
    links: List[str]
    depth: int
    timestamp: float
    parent_url: Optional[str] = None

class GraphWebCrawler:
    def __init__(self, delay: float = 1.0, timeout: int = 10, max_pages: int = 50):
        self.delay = delay
        self.timeout = timeout
        self.max_pages = max_pages
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ResearchCrawler/1.0 (Educational Purpose)'
        })
        self.logger = logging.getLogger(__name__)
    
    def _fetch_page(self, url: str) -> Optional[PageInfo]:
        """Fetch and parse a single page"""
        try:
            # Skip search engine URLs themselves
            if any(domain in url for domain in ['google.com/search', 'duckduckgo.com/?q=', 'bing.com/search']):
                self.logger.warning(f"Skipping search engine URL: {url}")
                return None
            
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if not any(ct in content_type for ct in ['text/html', 'application/xhtml']):
                self.logger.warning(f"Skipping non-HTML content: {url} ({content_type})")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.find('title')
            title = title.get_text(strip=True) if title else url
            
            content = self._extract_content(soup)
            
            # Skip pages with minimal content
            if len(content.strip()) < 100:
                self.logger.warning(f"Skipping page with minimal content: {url}")
                return None
            
            links = self._extract_links(soup, url)
            
            return PageInfo(
                url=url,
                title=title,
                content=content,
                links=links,
                depth=0,
                timestamp=time.time()
            )
        
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract meaningful text content from HTML with enhanced filtering"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header", "aside", "iframe", "noscript"]):
            script.decompose()
        
        # Remove common noise elements
        for element in soup.find_all(['div'], class_=re.compile(r'(ad|advertisement|sidebar|navigation|menu|footer|header)', re.I)):
            element.decompose()
        
        # Get text from meaningful content tags
        content_tags = soup.find_all([
            'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
            'article', 'main', 'section', 'div', 
            'li', 'blockquote', 'pre', 'code'
        ])
        
        content = []
        for tag in content_tags:
            text = tag.get_text(strip=True)
            # Filter out short snippets and common noise
            if (len(text) > 30 and 
                not any(noise in text.lower() for noise in [
                    'cookie', 'privacy policy', 'terms of service', 
                    'subscribe', 'newsletter', 'advertisement'
                ])):
                content.append(text)
        
        # Join content and limit length
        full_content = ' '.join(content)
        return full_content[:5000]  # Increased content length for better analysis

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract and normalize links from the page with better filtering"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            
            # Enhanced filtering
            if validators.url(full_url) and full_url.startswith(('http://', 'https://')):
                parsed = urlparse(full_url)
                
                # Skip certain file types, fragments, and search URLs
                if (not any(parsed.path.lower().endswith(ext) for ext in 
                           ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.doc', '.docx', '.ppt', '.pptx']) and
                    not any(domain in full_url for domain in ['google.com/search', 'duckduckgo.com/?q=', 'bing.com/search']) and
                    not parsed.fragment and  # Remove fragment URLs
                    len(parsed.path) > 1):  # Avoid root pages only
                    
                    links.append(full_url.split('#')[0])  # Remove fragments
        
        # Remove duplicates and limit
        unique_links = list(dict.fromkeys(links))
        return unique_links[:15]  # Increased link limit for better discovery
    
    def search_crawl_bfs(self, start_urls: List[str], max_depth: int = 2) -> Dict[str, PageInfo]:
        """
        BFS-based search crawling using a queue (FIFO)
        Implements pure breadth-first search for comprehensive but shallow exploration
        """
        visited: Set[str] = set()
        pages: Dict[str, PageInfo] = {}
        queue = deque()  # BFS uses a queue (FIFO)
        
        self.logger.info(f"🔍 BFS: Initializing queue with {len(start_urls)} seed URLs")
        
        # Initialize queue with starting URLs
        for url in start_urls:
            queue.append((url, 0, None))  # (url, depth, parent_url)
        
        pages_crawled = 0
        queue_operations = 0
        
        self.logger.info("🔍 BFS: Starting breadth-first exploration using FIFO queue")
        
        while queue and pages_crawled < self.max_pages:
            # FIFO operation: remove from front of queue
            current_url, depth, parent_url = queue.popleft()
            queue_operations += 1
            
            self.logger.debug(f"🔍 BFS Queue Operation #{queue_operations}: Dequeued {current_url} at depth {depth}")
            
            if current_url in visited or depth > max_depth:
                continue
            
            visited.add(current_url)
            
            # Add delay to be respectful
            if pages_crawled > 0:
                time.sleep(self.delay)
            
            page_info = self._fetch_page(current_url)
            if page_info:
                page_info.depth = depth
                page_info.parent_url = parent_url
                pages[current_url] = page_info
                pages_crawled += 1
                
                self.logger.info(f"🔍 BFS: Crawled page {pages_crawled}/{self.max_pages} - {current_url} at depth {depth}")
                
                # Add child links to queue for next level exploration (FIFO)
                child_count = 0
                for link in page_info.links[:10]:  # Limit links per page
                    if link not in visited:
                        queue.append((link, depth + 1, current_url))  # Add to rear of queue
                        child_count += 1
                
                self.logger.debug(f"🔍 BFS: Added {child_count} child links to queue for depth {depth + 1}")
        
        self.logger.info(f"🔍 BFS: Completed with {len(pages)} pages crawled using {queue_operations} queue operations")
        return pages
    
    def deep_research_crawl_dfs_bfs(self, start_urls: List[str], bfs_pages: int = 15, dfs_depth: int = 3) -> Dict[str, PageInfo]:
        """
        Deep research crawling: BFS for initial exploration, then DFS for deep diving
        Phase 1: BFS with queue (FIFO) to get seed pages
        Phase 2: DFS with stack (LIFO) for deep exploration of each seed
        """
        all_pages: Dict[str, PageInfo] = {}
        visited_global: Set[str] = set()
        
        # Phase 1: BFS for initial broad exploration using queue
        self.logger.info("🔬 PHASE 1: BFS exploration using FIFO queue for seed collection")
        bfs_queue = deque()  # Queue for BFS (FIFO)
        
        for url in start_urls:
            bfs_queue.append((url, 0, None))
        
        bfs_pages_collected = 0
        seed_pages = []
        bfs_queue_ops = 0
        
        while bfs_queue and bfs_pages_collected < bfs_pages:
            current_url, depth, parent_url = bfs_queue.popleft()  # FIFO for BFS
            bfs_queue_ops += 1
            
            self.logger.debug(f"🔬 BFS Queue Op #{bfs_queue_ops}: Processing {current_url}")
            
            if current_url in visited_global or depth > 2:  # Limit BFS depth
                continue
            
            visited_global.add(current_url)
            
            if bfs_pages_collected > 0:
                time.sleep(self.delay)
            
            page_info = self._fetch_page(current_url)
            if page_info:
                page_info.depth = depth
                page_info.parent_url = parent_url
                all_pages[current_url] = page_info
                seed_pages.append(page_info)
                bfs_pages_collected += 1
                
                self.logger.info(f"🔬 BFS Phase: Collected seed {bfs_pages_collected}/{bfs_pages} - {current_url}")
                
                # Add links for continued BFS
                for link in page_info.links[:8]:
                    if link not in visited_global:
                        bfs_queue.append((link, depth + 1, current_url))
        
        self.logger.info(f"🔬 PHASE 1 Complete: Collected {len(seed_pages)} seed pages using {bfs_queue_ops} queue operations")
        
        # Phase 2: DFS on each seed page for deep exploration using stack
        self.logger.info("🔬 PHASE 2: DFS deep exploration using LIFO stack")
        total_pages = len(all_pages)
        dfs_stack_ops = 0
        
        for seed_idx, seed_page in enumerate(seed_pages, 1):
            if total_pages >= self.max_pages:
                break
            
            self.logger.info(f"🔬 DFS: Deep diving from seed {seed_idx}/{len(seed_pages)} - {seed_page.url}")
            
            # DFS exploration starting from each seed page using stack
            dfs_stack = [(link, 1, seed_page.url) for link in seed_page.links[:5]]  # Stack for DFS (LIFO)
            dfs_visited = set()
            
            while dfs_stack and total_pages < self.max_pages:
                current_url, depth, parent_url = dfs_stack.pop()  # LIFO for DFS
                dfs_stack_ops += 1
                
                self.logger.debug(f"🔬 DFS Stack Op #{dfs_stack_ops}: Processing {current_url} at depth {depth}")
                
                if current_url in visited_global or current_url in dfs_visited or depth > dfs_depth:
                    continue
                
                dfs_visited.add(current_url)
                visited_global.add(current_url)
                
                time.sleep(self.delay)
                
                page_info = self._fetch_page(current_url)
                if page_info:
                    page_info.depth = len(seed_pages) + depth  # Adjust depth for display
                    page_info.parent_url = parent_url
                    all_pages[current_url] = page_info
                    total_pages += 1
                    
                    self.logger.info(f"🔬 DFS: Deep crawled {current_url} at depth {depth} (total: {total_pages})")
                    
                    # Add child links to stack for deeper exploration (LIFO)
                    child_count = 0
                    for link in page_info.links[:5]:  # Limit for DFS
                        if link not in visited_global and link not in dfs_visited:
                            dfs_stack.append((link, depth + 1, current_url))  # Add to top of stack
                            child_count += 1
                    
                    self.logger.debug(f"🔬 DFS: Added {child_count} links to stack for deeper exploration")
        
        self.logger.info(f"🔬 PHASE 2 Complete: Used {dfs_stack_ops} stack operations for deep exploration")
        self.logger.info(f"🔬 HYBRID Complete: Total {len(all_pages)} pages using BFS({bfs_queue_ops} queue ops) + DFS({dfs_stack_ops} stack ops)")
        
        return all_pages
    
    def get_crawl_statistics(self, pages: Dict[str, PageInfo]) -> Dict:
        """Generate enhanced statistics about the crawl"""
        if not pages:
            return {}
        
        depths = [page.depth for page in pages.values()]
        domains = [urlparse(url).netloc for url in pages.keys()]
        
        # Calculate depth distribution
        depth_distribution = {}
        for depth in depths:
            depth_distribution[depth] = depth_distribution.get(depth, 0) + 1
        
        return {
            'total_pages': len(pages),
            'max_depth': max(depths) if depths else 0,
            'min_depth': min(depths) if depths else 0,
            'avg_depth': sum(depths) / len(depths) if depths else 0,
            'unique_domains': len(set(domains)),
            'pages_by_depth': depth_distribution,
            'domain_distribution': {domain: domains.count(domain) for domain in set(domains)},
            'depth_range': max(depths) - min(depths) if depths else 0
        }
