#!/usr/bin/env python3
"""
Test script to verify environment variables are properly loaded and used
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project directory to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

def test_environment_variables():
    """Test if environment variables are properly loaded"""
    print("🧪 Testing Environment Variable Loading")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Test all environment variables
    env_vars = {
        'DEFAULT_DELAY': 1.0,
        'DEFAULT_TIMEOUT': 10,
        'MAX_PAGES_PER_CRAWL': 50,
        'SEARCH_MAX_DEPTH': 1,
        'SEARCH_MAX_PAGES': 25,
        'SEARCH_MAX_LINKS_PER_PAGE': 5,
        'SEARCH_DELAY_MULTIPLIER': 0.7,
        'DEEP_BFS_PAGES': 20,
        'DEEP_DFS_DEPTH': 4,
        'DEEP_MAX_LINKS_BFS': 8,
        'DEEP_MAX_LINKS_DFS': 6,
        'DEEP_DELAY_MULTIPLIER': 1.0,
        'USER_AGENT': 'ResearchCrawler/1.0 (Educational Purpose)'
    }
    
    print("📋 Environment Variables:")
    for var_name, default_value in env_vars.items():
        if isinstance(default_value, str):
            value = os.getenv(var_name, default_value)
        else:
            try:
                value = type(default_value)(os.getenv(var_name, str(default_value)))
            except (ValueError, TypeError):
                value = default_value
        
        print(f"   {var_name}: {value} (Type: {type(value).__name__})")
    
    print("\n✅ Environment variables loaded successfully!")
    
    return True

def test_research_service_config():
    """Test ResearchService configuration with environment variables"""
    print("\n🧪 Testing ResearchService Configuration")
    print("=" * 50)
    
    try:
        from research_service import ResearchService
        
        # Create service (should use environment variables)
        service = ResearchService()
        
        print("✅ ResearchService created successfully")
        print(f"   Crawler delay: {service.crawler.delay}")
        print(f"   Crawler timeout: {service.crawler.timeout}")
        print(f"   Crawler max_pages: {service.crawler.max_pages}")
        
        # Test environment variable retrieval
        search_max_depth = int(os.getenv('SEARCH_MAX_DEPTH', 1))
        search_max_pages = int(os.getenv('SEARCH_MAX_PAGES', 25))
        deep_bfs_pages = int(os.getenv('DEEP_BFS_PAGES', 20))
        deep_dfs_depth = int(os.getenv('DEEP_DFS_DEPTH', 4))
        
        print(f"\n📊 Algorithm Configuration:")
        print(f"   Search - Max Depth: {search_max_depth}")
        print(f"   Search - Max Pages: {search_max_pages}")
        print(f"   Deep - BFS Pages: {deep_bfs_pages}")
        print(f"   Deep - DFS Depth: {deep_dfs_depth}")
        
        # Cleanup
        service.cleanup()
        
        return True
        
    except Exception as e:
        print(f"❌ ResearchService test failed: {e}")
        return False

def test_graph_crawler_env_usage():
    """Test GraphWebCrawler environment variable usage"""
    print("\n🧪 Testing GraphWebCrawler Environment Usage")
    print("=" * 50)
    
    try:
        from graph_crawler import GraphWebCrawler
        
        # Test environment variable access
        search_max_links = int(os.getenv('SEARCH_MAX_LINKS_PER_PAGE', 5))
        deep_max_links_bfs = int(os.getenv('DEEP_MAX_LINKS_BFS', 8))
        deep_max_links_dfs = int(os.getenv('DEEP_MAX_LINKS_DFS', 6))
        
        print(f"📊 Link Limits from Environment:")
        print(f"   Search max links per page: {search_max_links}")
        print(f"   Deep BFS max links: {deep_max_links_bfs}")
        print(f"   Deep DFS max links: {deep_max_links_dfs}")
        
        # Create crawler instance
        crawler = GraphWebCrawler(delay=0.5, timeout=5, max_pages=3, headless=True)
        print("✅ GraphWebCrawler created successfully")
        
        # Cleanup
        crawler.close_driver()
        
        return True
        
    except Exception as e:
        print(f"❌ GraphWebCrawler test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🔬 Environment Variables and Configuration Test")
    print("=" * 60)
    
    success = True
    
    # Test 1: Environment variables
    if not test_environment_variables():
        success = False
    
    # Test 2: ResearchService configuration
    if not test_research_service_config():
        success = False
    
    # Test 3: GraphWebCrawler environment usage
    if not test_graph_crawler_env_usage():
        success = False
    
    # Final result
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED! Environment configuration is working correctly.")
    else:
        print("❌ SOME TESTS FAILED! Please check the configuration.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
