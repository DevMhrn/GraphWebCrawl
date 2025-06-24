#!/usr/bin/env python3
"""
Test script to verify the DFS phase in deep research crawling.
This should show that DFS is now executing and reaching the configured depth.
"""

import os
import sys
import time
sys.path.append('/Users/devmhrn/Desktop/WorkSpace/GraphWebCrawler')

from dotenv import load_dotenv
load_dotenv()

from graph_crawler import GraphWebCrawler
from research_service import ResearchService
import logging

# Set up logging to see detailed output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_dfs_execution():
    print("=== Testing DFS Execution in Deep Research ===\n")
    
    # Show environment configuration
    print("Environment Configuration:")
    print(f"  DEEP_BFS_PAGES: {os.getenv('DEEP_BFS_PAGES', 'Not set')}")
    print(f"  DEEP_DFS_DEPTH: {os.getenv('DEEP_DFS_DEPTH', 'Not set')}")
    print(f"  DEEP_MAX_LINKS_BFS: {os.getenv('DEEP_MAX_LINKS_BFS', 'Not set')}")
    print(f"  DEEP_MAX_LINKS_DFS: {os.getenv('DEEP_MAX_LINKS_DFS', 'Not set')}")
    print(f"  DEEP_DELAY_MULTIPLIER: {os.getenv('DEEP_DELAY_MULTIPLIER', 'Not set')}")
    print()
    
    # Initialize crawler
    crawler = GraphWebCrawler(max_pages=50, delay=0.5)
    
    # Test URLs that should have good link structure
    test_urls = [
        "https://example.com",
        "https://httpbin.org/"
    ]
    
    print(f"Testing deep research crawling with {len(test_urls)} seed URLs...")
    print("Expected behavior:")
    print(f"  - BFS phase should collect up to {os.getenv('DEEP_BFS_PAGES', 15)} seed pages")
    print(f"  - DFS phase should explore {os.getenv('DEEP_DFS_DEPTH', 8)} levels deep from each seed")
    print(f"  - Graph should show nodes at depths higher than BFS depth (>2)")
    print()
    
    # Start crawling
    start_time = time.time()
    
    # Use the environment variables for configuration
    bfs_pages = int(os.getenv('DEEP_BFS_PAGES', 15))
    dfs_depth = int(os.getenv('DEEP_DFS_DEPTH', 8))
    
    print("🚀 Starting deep research crawl...")
    pages = crawler.deep_research_crawl_dfs_bfs(
        start_urls=test_urls,
        bfs_pages=bfs_pages,
        dfs_depth=dfs_depth
    )
    
    elapsed_time = time.time() - start_time
    
    print(f"\n=== Results ===")
    print(f"Total pages crawled: {len(pages)}")
    print(f"Crawl time: {elapsed_time:.2f} seconds")
    
    # Analyze depths
    if pages:
        depths = [page.depth for page in pages.values()]
        print(f"Depth range: {min(depths)} to {max(depths)}")
        print(f"Pages by depth:")
        depth_counts = {}
        for depth in depths:
            depth_counts[depth] = depth_counts.get(depth, 0) + 1
        for depth in sorted(depth_counts.keys()):
            print(f"  Depth {depth}: {depth_counts[depth]} pages")
    
    # Get detailed statistics
    stats = crawler.get_crawl_statistics(pages)
    print(f"\nDetailed Statistics:")
    print(f"  Max depth achieved: {stats.get('max_depth', 0)}")
    print(f"  Total graph nodes: {stats.get('graph_metrics', {}).get('total_nodes', 0)}")
    print(f"  Successfully crawled: {stats.get('graph_metrics', {}).get('crawled_nodes', 0)}")
    print(f"  Success rate: {stats.get('graph_metrics', {}).get('success_rate', 0):.1f}%")
    
    # Check if DFS actually happened
    max_depth = stats.get('max_depth', 0)
    expected_min_depth = 3  # BFS goes to depth 2, DFS should go deeper
    
    print(f"\n=== DFS Analysis ===")
    if max_depth >= expected_min_depth:
        print(f"✅ SUCCESS: DFS phase executed! Max depth {max_depth} >= {expected_min_depth}")
        print(f"   This indicates that DFS went beyond the BFS depth limit.")
    else:
        print(f"❌ FAILURE: DFS phase may not have executed properly.")
        print(f"   Max depth {max_depth} < {expected_min_depth}, suggesting only BFS ran.")
    
    # Close the crawler
    crawler.close_driver()
    
    return max_depth >= expected_min_depth

if __name__ == "__main__":
    success = test_dfs_execution()
    sys.exit(0 if success else 1)
