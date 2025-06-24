from selenium_utils import WebDriverManager
from selenium_deployment import DeploymentWebDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque, defaultdict
import time
import logging
import os
from typing import List, Dict, Set, Tuple, Optional
import validators
from dataclasses import dataclass, field
import re
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class GraphNode:
    """Represents a node in the web graph with proper relationships"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    url: str = ""
    title: str = ""
    content: str = ""
    depth: int = 0
    timestamp: float = field(default_factory=time.time)
    parent_node_id: Optional[str] = None
    child_node_ids: List[str] = field(default_factory=list)
    outbound_links: List[str] = field(default_factory=list)
    page_rank: float = 0.0
    crawl_status: str = "pending"  # pending, crawled, failed
    metadata: Dict = field(default_factory=dict)

@dataclass
class PageInfo:
    """Legacy compatibility class - maps to GraphNode"""
    url: str
    title: str
    content: str
    links: List[str]
    depth: int
    timestamp: float
    parent_url: Optional[str] = None
    
    @classmethod
    def from_graph_node(cls, node: GraphNode):
        """Create PageInfo from GraphNode for backward compatibility"""
        return cls(
            url=node.url,
            title=node.title,
            content=node.content,
            links=node.outbound_links,
            depth=node.depth,
            timestamp=node.timestamp,
            parent_url=None  # Will be resolved from graph
        )

class GraphWebCrawler:
    def __init__(self, delay: float = 1.0, timeout: int = 10, max_pages: int = 50, headless: bool = True):
        self.delay = delay
        self.timeout = timeout
        self.max_pages = max_pages
        self.headless = headless
        
        # Initialize logger first
        self.logger = logging.getLogger(__name__)
        
        # Graph storage
        self.graph_nodes: Dict[str, GraphNode] = {}
        self.url_to_node_id: Dict[str, str] = {}
        
        # Selenium setup using deployment-friendly WebDriverManager
        try:
            self.driver_manager = DeploymentWebDriverManager(headless=headless, timeout=timeout)
            self._setup_driver()
        except Exception as e:
            self.logger.warning(f"Deployment WebDriver failed, falling back to standard: {e}")
            self.driver_manager = WebDriverManager(headless=headless, timeout=timeout)
            self._setup_driver()
    
    def _setup_driver(self):
        """Initialize Selenium WebDriver using WebDriverManager"""
        try:
            success = self.driver_manager.setup_driver()
            if success:
                self.logger.info("✅ Selenium WebDriver initialized successfully")
            else:
                self.logger.error("❌ Failed to initialize WebDriver")
        except Exception as e:
            self.logger.error(f"❌ Failed to setup WebDriver: {e}")
    
    def __del__(self):
        """Clean up WebDriver when object is destroyed"""
        self.close_driver()
    
    def close_driver(self):
        """Close the WebDriver"""
        if hasattr(self, 'driver_manager') and self.driver_manager:
            try:
                self.driver_manager.close()
                if hasattr(self, 'logger'):
                    self.logger.info("🔒 WebDriver closed successfully")
            except Exception as e:
                if hasattr(self, 'logger'):
                    self.logger.error(f"Error closing WebDriver: {e}")
    
    def _create_node(self, url: str, depth: int = 0, parent_node_id: Optional[str] = None) -> GraphNode:
        """Create a new graph node"""
        node = GraphNode(
            url=url,
            depth=depth,
            parent_node_id=parent_node_id,
            crawl_status="pending"
        )
        
        self.graph_nodes[node.id] = node
        self.url_to_node_id[url] = node.id
        
        # Update parent's children list
        if parent_node_id and parent_node_id in self.graph_nodes:
            self.graph_nodes[parent_node_id].child_node_ids.append(node.id)
        
        return node
    
    def _fetch_page_selenium(self, node: GraphNode) -> bool:
        """Fetch and parse a single page using Selenium and update the node"""
        if not self.driver_manager or not self.driver_manager.is_alive():
            self.logger.error("WebDriver not available or not responsive")
            node.crawl_status = "failed"
            return False
        
        try:
            url = node.url
            
            # Skip search engine URLs themselves
            if any(domain in url for domain in ['google.com/search', 'duckduckgo.com/?q=', 'bing.com/search']):
                self.logger.warning(f"Skipping search engine URL: {url}")
                node.crawl_status = "failed"
                return False
            
            self.logger.info(f"🌐 Fetching with Selenium: {url}")
            
            # Navigate to the page using WebDriverManager
            if not self.driver_manager.get_page(url):
                self.logger.warning(f"Failed to load page: {url}")
                node.crawl_status = "failed"
                return False
            
            # Get page source and parse with BeautifulSoup
            page_source = self.driver_manager.get_page_source()
            if not page_source:
                self.logger.warning(f"No page source received for: {url}")
                node.crawl_status = "failed"
                return False
            
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract title
            title_element = soup.find('title')
            node.title = title_element.get_text(strip=True) if title_element else url
            
            # Extract content
            node.content = self._extract_content(soup)
            
            # Skip pages with minimal content
            if len(node.content.strip()) < 100:
                self.logger.warning(f"Skipping page with minimal content: {url}")
                node.crawl_status = "failed"
                return False
            
            # Extract links
            node.outbound_links = self._extract_links(soup, url)
            
            # Update metadata
            node.metadata = {
                'content_length': len(node.content),
                'links_count': len(node.outbound_links),
                'title_length': len(node.title),
                'final_url': self.driver_manager.get_current_url()  # In case of redirects
            }
            
            node.crawl_status = "crawled"
            self.logger.info(f"✅ Successfully crawled: {url} ({len(node.content)} chars, {len(node.outbound_links)} links)")
            
            return True
        
        except Exception as e:
            self.logger.error(f"❌ Error fetching {url}: {e}")
            node.crawl_status = "failed"
            
            # Try to restart driver if it seems to be the issue
            if "session" in str(e).lower() or "chrome" in str(e).lower():
                self.logger.info("� Attempting to restart WebDriver...")
                if self.driver_manager.restart_driver():
                    self.logger.info("✅ WebDriver restarted successfully")
                else:
                    self.logger.error("❌ Failed to restart WebDriver")
            
            return False

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
        BFS-based search crawling using a queue (FIFO) with proper graph structure
        Each queue item is a GraphNode, maintaining proper parent-child relationships
        """
        visited_urls: Set[str] = set()
        node_queue = deque()  # Queue of GraphNode objects for BFS (FIFO)
        
        self.logger.info(f"🔍 BFS: Initializing node queue with {len(start_urls)} seed URLs")
        
        # Initialize queue with starting GraphNodes
        for url in start_urls:
            if url not in visited_urls:
                root_node = self._create_node(url, depth=0)
                node_queue.append(root_node)
                visited_urls.add(url)
        
        pages_crawled = 0
        queue_operations = 0
        
        self.logger.info("🔍 BFS: Starting breadth-first exploration using FIFO node queue")
        
        while node_queue and pages_crawled < self.max_pages:
            # FIFO operation: remove node from front of queue
            current_node = node_queue.popleft()
            queue_operations += 1
            
            self.logger.debug(f"🔍 BFS Queue Operation #{queue_operations}: Processing node {current_node.id} - {current_node.url} at depth {current_node.depth}")
            
            if current_node.depth > max_depth:
                continue
            
            # Add delay to be respectful
            if pages_crawled > 0:
                time.sleep(self.delay)
            
            # Fetch page content using Selenium
            if self._fetch_page_selenium(current_node):
                pages_crawled += 1
                
                self.logger.info(f"🔍 BFS: Crawled page {pages_crawled}/{self.max_pages} - Node {current_node.id} - {current_node.url} at depth {current_node.depth}")
                
                # Create child nodes and add to queue for next level exploration (FIFO)
                child_count = 0
                max_links_per_page = int(os.getenv('SEARCH_MAX_LINKS_PER_PAGE', 5))
                
                for link in current_node.outbound_links[:max_links_per_page]:  # Use env variable
                    if link not in visited_urls and validators.url(link):
                        child_node = self._create_node(
                            url=link,
                            depth=current_node.depth + 1,
                            parent_node_id=current_node.id
                        )
                        node_queue.append(child_node)  # Add to rear of queue
                        visited_urls.add(link)
                        child_count += 1
                
                self.logger.debug(f"🔍 BFS: Created {child_count} child nodes and added to queue for depth {current_node.depth + 1}")
        
        # Convert graph nodes to PageInfo for backward compatibility
        pages = {}
        for node in self.graph_nodes.values():
            if node.crawl_status == "crawled":
                page_info = PageInfo.from_graph_node(node)
                # Resolve parent URL from graph
                if node.parent_node_id and node.parent_node_id in self.graph_nodes:
                    page_info.parent_url = self.graph_nodes[node.parent_node_id].url
                pages[node.url] = page_info
        
        self.logger.info(f"🔍 BFS: Completed with {len(pages)} pages crawled using {queue_operations} queue operations")
        self.logger.info(f"📊 Graph Statistics: {len(self.graph_nodes)} nodes total, {len([n for n in self.graph_nodes.values() if n.crawl_status == 'crawled'])} successfully crawled")
        
        return pages
    
    def deep_research_crawl_dfs_bfs(self, start_urls: List[str], bfs_pages: int = 15, dfs_depth: int = 3) -> Dict[str, PageInfo]:
        """
        Deep research crawling with proper graph structure:
        Phase 1: BFS with node queue (FIFO) to get seed nodes
        Phase 2: DFS with node stack (LIFO) for deep exploration of each seed
        """
        crawled_urls: Set[str] = set()  # Only mark URLs as visited when successfully crawled
        
        # Phase 1: BFS for initial broad exploration using node queue
        self.logger.info("🔬 PHASE 1: BFS exploration using FIFO node queue for seed collection")
        bfs_node_queue = deque()  # Queue of GraphNode objects for BFS (FIFO)
        bfs_queued_urls = set()  # Track URLs queued for BFS to avoid duplicates in BFS
        
        # Initialize with root nodes
        for url in start_urls:
            if url not in bfs_queued_urls:
                root_node = self._create_node(url, depth=0)
                bfs_node_queue.append(root_node)
                bfs_queued_urls.add(url)
        
        bfs_pages_collected = 0
        seed_nodes = []
        bfs_queue_ops = 0
        
        while bfs_node_queue and bfs_pages_collected < bfs_pages:
            current_node = bfs_node_queue.popleft()  # FIFO for BFS
            bfs_queue_ops += 1
            
            self.logger.debug(f"🔬 BFS Queue Op #{bfs_queue_ops}: Processing node {current_node.id} - {current_node.url}")
            
            if current_node.depth > 2:  # Limit BFS depth
                continue
            
            if bfs_pages_collected > 0:
                time.sleep(self.delay)
            
            # Fetch page using Selenium
            if self._fetch_page_selenium(current_node):
                seed_nodes.append(current_node)
                bfs_pages_collected += 1
                crawled_urls.add(current_node.url)  # Mark as crawled only after successful fetch
                
                self.logger.info(f"🔬 BFS Phase: Collected seed {bfs_pages_collected}/{bfs_pages} - Node {current_node.id} - {current_node.url}")
                
                # Add child nodes for continued BFS
                max_links_bfs = int(os.getenv('DEEP_MAX_LINKS_BFS', 8))
                
                for link in current_node.outbound_links[:max_links_bfs]:
                    if link not in bfs_queued_urls and validators.url(link):
                        child_node = self._create_node(
                            url=link,
                            depth=current_node.depth + 1,
                            parent_node_id=current_node.id
                        )
                        bfs_node_queue.append(child_node)
                        bfs_queued_urls.add(link)  # Prevent duplicates in BFS queue
        
        self.logger.info(f"🔬 PHASE 1 Complete: Collected {len(seed_nodes)} seed nodes using {bfs_queue_ops} queue operations")
        
        # Log seed node details for debugging
        total_seed_links = sum(len(node.outbound_links) for node in seed_nodes)
        self.logger.info(f"🔬 SEED ANALYSIS: {len(seed_nodes)} seeds have {total_seed_links} total outbound links")
        for i, seed in enumerate(seed_nodes[:5], 1):  # Log first 5 seeds
            self.logger.info(f"   Seed {i}: {seed.url} ({len(seed.outbound_links)} links)")
        
        if len(seed_nodes) == 0:
            self.logger.warning("🔬 No seed nodes collected! DFS phase will be skipped.")
        elif total_seed_links == 0:
            self.logger.warning("🔬 Seed nodes have no outbound links! DFS phase may be limited.")
        
        # Phase 2: DFS on each seed node for deep exploration using node stack
        self.logger.info("🔬 PHASE 2: DFS deep exploration using LIFO node stack")
        total_pages = len([n for n in self.graph_nodes.values() if n.crawl_status == "crawled"])
        dfs_stack_ops = 0
        dfs_pages_crawled = 0
        
        self.logger.info(f"🔬 DFS: Starting with {len(seed_nodes)} seed nodes, target DFS depth: {dfs_depth}")
        
        for seed_idx, seed_node in enumerate(seed_nodes, 1):
            if total_pages >= self.max_pages:
                self.logger.info(f"🔬 DFS: Reached max pages limit ({self.max_pages}), stopping")
                break
            
            self.logger.info(f"🔬 DFS: Deep diving from seed {seed_idx}/{len(seed_nodes)} - Node {seed_node.id} - {seed_node.url}")
            self.logger.info(f"🔬 DFS: Seed node has {len(seed_node.outbound_links)} outbound links")
            self.logger.info(f"🔬 DFS: Seed node is at absolute depth {seed_node.depth}, will explore {dfs_depth} levels deeper (max absolute depth: {seed_node.depth + dfs_depth})")
            
            # Create child nodes for DFS exploration
            dfs_node_stack = []  # Stack of GraphNode objects for DFS (LIFO)
            dfs_queued_urls = set()  # Track URLs queued for DFS to avoid duplicates in this DFS branch
            max_absolute_depth = seed_node.depth + dfs_depth  # Calculate maximum absolute depth for this seed
            
            # Add child nodes to stack
            max_links_dfs = int(os.getenv('DEEP_MAX_LINKS_DFS', 6))
            
            links_added_to_stack = 0
            for link in seed_node.outbound_links[:max_links_dfs]:
                # Allow DFS to explore links that weren't successfully crawled yet
                if link not in crawled_urls and link not in dfs_queued_urls and validators.url(link):
                    child_node = self._create_node(
                        url=link,
                        depth=seed_node.depth + 1,  # Continue from seed node's depth
                        parent_node_id=seed_node.id
                    )
                    dfs_node_stack.append(child_node)
                    dfs_queued_urls.add(link)  # Prevent duplicates in this DFS branch
                    links_added_to_stack += 1
            
            self.logger.info(f"🔬 DFS: Added {links_added_to_stack} links to stack for seed {seed_idx}")
            
            if links_added_to_stack == 0:
                self.logger.warning(f"🔬 DFS: No valid links to explore from seed {seed_idx}, skipping DFS for this seed")
                continue
            
            self.logger.info(f"🔬 DFS: Starting deep exploration with {len(dfs_node_stack)} nodes in stack for seed {seed_idx}")
            
            # DFS exploration using stack (LIFO)
            while dfs_node_stack and total_pages < self.max_pages:
                current_node = dfs_node_stack.pop()  # LIFO for DFS
                dfs_stack_ops += 1
                
                self.logger.debug(f"🔬 DFS Stack Op #{dfs_stack_ops}: Processing node {current_node.id} - {current_node.url} at absolute depth {current_node.depth} (DFS levels from seed: {current_node.depth - seed_node.depth})")
                
                # Check DFS depth limit (relative to seed node)
                if current_node.depth > max_absolute_depth:
                    self.logger.debug(f"🔬 DFS: Skipping node at absolute depth {current_node.depth} (max for this seed: {max_absolute_depth})")
                    continue
                
                # Skip if already crawled (could happen if multiple seeds have same links)
                if current_node.url in crawled_urls:
                    self.logger.debug(f"🔬 DFS: Skipping already crawled URL: {current_node.url}")
                    continue
                
                # Add delay between requests
                time.sleep(self.delay)
                
                # Fetch page using Selenium
                if self._fetch_page_selenium(current_node):
                    total_pages += 1
                    dfs_pages_crawled += 1
                    crawled_urls.add(current_node.url)  # Mark as crawled only after successful fetch
                    
                    self.logger.info(f"🔬 DFS: Deep crawled Node {current_node.id} - {current_node.url} at absolute depth {current_node.depth} (DFS level {current_node.depth - seed_node.depth} from seed) (total: {total_pages}, DFS: {dfs_pages_crawled})")
                    
                    # Add child nodes to stack for deeper exploration (LIFO)
                    child_count = 0
                    if current_node.depth < max_absolute_depth:  # Only add children if we haven't reached max depth for this seed
                        for link in current_node.outbound_links[:max_links_dfs]:
                            if link not in crawled_urls and link not in dfs_queued_urls and validators.url(link):
                                child_node = self._create_node(
                                    url=link,
                                    depth=current_node.depth + 1,  # Increment absolute depth
                                    parent_node_id=current_node.id
                                )
                                dfs_node_stack.append(child_node)  # Add to top of stack (LIFO)
                                dfs_queued_urls.add(link)  # Prevent duplicates in this DFS branch
                                child_count += 1
                        
                        self.logger.debug(f"🔬 DFS: Created {child_count} child nodes at absolute depth {current_node.depth + 1} and added to stack")
                    else:
                        self.logger.debug(f"🔬 DFS: Max absolute depth {max_absolute_depth} reached for this seed, not adding more children")
        
        self.logger.info(f"🔬 PHASE 2 Complete: Used {dfs_stack_ops} stack operations, crawled {dfs_pages_crawled} pages via DFS")
        
        # Convert graph nodes to PageInfo for backward compatibility
        pages = {}
        crawled_nodes = [n for n in self.graph_nodes.values() if n.crawl_status == "crawled"]
        
        for node in crawled_nodes:
            page_info = PageInfo.from_graph_node(node)
            # Resolve parent URL from graph
            if node.parent_node_id and node.parent_node_id in self.graph_nodes:
                page_info.parent_url = self.graph_nodes[node.parent_node_id].url
            pages[node.url] = page_info
        
        self.logger.info(f"🔬 HYBRID Complete: Total {len(pages)} pages using BFS({bfs_queue_ops} queue ops) + DFS({dfs_stack_ops} stack ops)")
        self.logger.info(f"📊 Graph Statistics: {len(self.graph_nodes)} nodes total, {len(crawled_nodes)} successfully crawled")
        
        return pages
    
    def get_crawl_statistics(self, pages: Dict[str, PageInfo]) -> Dict:
        """Generate enhanced statistics about the crawl including graph metrics"""
        if not pages:
            return {}
        
        depths = [page.depth for page in pages.values()]
        domains = [urlparse(url).netloc for url in pages.keys()]
        
        # Calculate depth distribution
        depth_distribution = {}
        for depth in depths:
            depth_distribution[depth] = depth_distribution.get(depth, 0) + 1
        
        # Graph-specific statistics
        total_nodes = len(self.graph_nodes)
        crawled_nodes = len([n for n in self.graph_nodes.values() if n.crawl_status == "crawled"])
        failed_nodes = len([n for n in self.graph_nodes.values() if n.crawl_status == "failed"])
        pending_nodes = len([n for n in self.graph_nodes.values() if n.crawl_status == "pending"])
        
        # Calculate graph connectivity metrics
        nodes_with_children = len([n for n in self.graph_nodes.values() if n.child_node_ids])
        nodes_with_parents = len([n for n in self.graph_nodes.values() if n.parent_node_id])
        root_nodes = len([n for n in self.graph_nodes.values() if not n.parent_node_id])
        leaf_nodes = len([n for n in self.graph_nodes.values() if not n.child_node_ids])
        
        return {
            'total_pages': len(pages),
            'max_depth': max(depths) if depths else 0,
            'min_depth': min(depths) if depths else 0,
            'avg_depth': sum(depths) / len(depths) if depths else 0,
            'unique_domains': len(set(domains)),
            'pages_by_depth': depth_distribution,
            'domain_distribution': {domain: domains.count(domain) for domain in set(domains)},
            'depth_range': max(depths) - min(depths) if depths else 0,
            
            # Graph-specific metrics
            'graph_metrics': {
                'total_nodes': total_nodes,
                'crawled_nodes': crawled_nodes,
                'failed_nodes': failed_nodes,
                'pending_nodes': pending_nodes,
                'success_rate': (crawled_nodes / total_nodes * 100) if total_nodes > 0 else 0,
                'nodes_with_children': nodes_with_children,
                'nodes_with_parents': nodes_with_parents,
                'root_nodes': root_nodes,
                'leaf_nodes': leaf_nodes,
                'avg_children_per_node': sum(len(n.child_node_ids) for n in self.graph_nodes.values()) / total_nodes if total_nodes > 0 else 0,
                'avg_links_per_node': sum(len(n.outbound_links) for n in self.graph_nodes.values() if n.crawl_status == "crawled") / crawled_nodes if crawled_nodes > 0 else 0
            }
        }
    
    def get_graph_visualization_data(self) -> Dict:
        """Get data for graph visualization"""
        nodes = []
        edges = []
        
        for node in self.graph_nodes.values():
            nodes.append({
                'id': node.id,
                'url': node.url,
                'title': node.title[:50] + "..." if len(node.title) > 50 else node.title,
                'depth': node.depth,
                'status': node.crawl_status,
                'links_count': len(node.outbound_links),
                'content_length': len(node.content)
            })
            
            # Add edges for parent-child relationships
            if node.parent_node_id:
                edges.append({
                    'source': node.parent_node_id,
                    'target': node.id,
                    'type': 'parent_child'
                })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'stats': {
                'total_nodes': len(nodes),
                'total_edges': len(edges),
                'max_depth': max([n['depth'] for n in nodes]) if nodes else 0
            }
        }
    
    def clear_graph(self):
        """Clear the graph data for a fresh start"""
        self.graph_nodes.clear()
        self.url_to_node_id.clear()
        self.logger.info("🧹 Graph data cleared")
