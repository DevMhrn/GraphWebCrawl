#!/usr/bin/env python3
"""
Test script for the enhanced Graph Web Crawler with Selenium and proper graph structure
"""

import logging
import sys
import os
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from graph_crawler import GraphWebCrawler, GraphNode, PageInfo
from research_service import ResearchService
from selenium_utils import test_driver_setup

def setup_logging():
    """Setup logging for testing"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('test_crawler.log')
        ]
    )

def test_selenium_setup():
    """Test Selenium WebDriver setup"""
    print("🧪 Testing Selenium WebDriver setup...")
    
    try:
        success = test_driver_setup()
        if success:
            print("✅ Selenium WebDriver test passed")
            return True
        else:
            print("❌ Selenium WebDriver test failed")
            return False
    except Exception as e:
        print(f"❌ Selenium test error: {e}")
        return False

def test_graph_node_creation():
    """Test GraphNode creation and relationships"""
    print("\n🧪 Testing GraphNode creation...")
    
    try:
        crawler = GraphWebCrawler(delay=0.5, timeout=5, max_pages=3, headless=True)
        
        # Create root node
        root_node = crawler._create_node("https://example.com", depth=0)
        print(f"✅ Created root node: {root_node.id} - {root_node.url}")
        
        # Create child node
        child_node = crawler._create_node("https://example.com/page1", depth=1, parent_node_id=root_node.id)
        print(f"✅ Created child node: {child_node.id} - {child_node.url}")
        
        # Verify relationships
        assert child_node.parent_node_id == root_node.id
        assert child_node.id in root_node.child_node_ids
        
        print(f"✅ Graph structure: {len(crawler.graph_nodes)} nodes")
        print(f"   Root children: {len(root_node.child_node_ids)}")
        
        crawler.close_driver()
        return True
        
    except Exception as e:
        print(f"❌ Graph node test error: {e}")
        return False

def test_simple_crawl():
    """Test simple crawling with a few pages"""
    print("\n🧪 Testing simple BFS crawl...")
    
    try:
        crawler = GraphWebCrawler(delay=1.0, timeout=10, max_pages=5, headless=True)
        
        # Test with a simple, reliable site
        test_urls = ["https://httpbin.org/html"]
        
        print(f"🔍 Starting BFS crawl on: {test_urls}")
        pages = crawler.search_crawl_bfs(test_urls, max_depth=1)
        
        print(f"✅ Crawled {len(pages)} pages")
        
        for url, page in pages.items():
            print(f"   📄 {url} - {page.title[:50]}... ({len(page.content)} chars)")
        
        # Test statistics
        stats = crawler.get_crawl_statistics(pages)
        print(f"📊 Statistics: {stats}")
        
        # Test graph visualization data
        viz_data = crawler.get_graph_visualization_data()
        print(f"🕸️  Graph: {len(viz_data['nodes'])} nodes, {len(viz_data['edges'])} edges")
        
        crawler.close_driver()
        return True
        
    except Exception as e:
        print(f"❌ Simple crawl test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_research_service():
    """Test ResearchService with new crawler"""
    print("\n🧪 Testing ResearchService...")
    
    try:
        # Configure for testing
        crawler_config = {
            'delay': 1.0,
            'timeout': 10,
            'max_pages': 3,
            'headless': True
        }
        
        research_service = ResearchService(crawler_config=crawler_config)
        
        # Test search research
        query = "machine learning"
        print(f"🔍 Testing search research for: {query}")
        
        # This will use our enhanced crawler
        analysis, pages, stats = research_service.search_research(query, max_depth=1)
        
        print(f"✅ Research completed:")
        print(f"   📄 Pages: {len(pages)}")
        print(f"   📊 Analysis confidence: {analysis.confidence_score}")
        print(f"   🔗 Citations: {len(analysis.citations)}")
        
        # Test graph data
        graph_data = research_service.get_graph_visualization_data()
        print(f"🕸️  Graph data: {len(graph_data['nodes'])} nodes")
        
        # Cleanup
        research_service.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ Research service test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Graph Web Crawler Tests")
    print("=" * 50)
    
    setup_logging()
    
    tests = [
        ("Selenium Setup", test_selenium_setup),
        ("Graph Node Creation", test_graph_node_creation),
        ("Simple Crawl", test_simple_crawl),
        ("Research Service", test_research_service)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'=' * 20} {test_name} {'=' * 20}")
        try:
            result = test_func()
            results[test_name] = result
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status}: {test_name}")
        except Exception as e:
            results[test_name] = False
            print(f"❌ FAILED: {test_name} - {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The enhanced crawler is ready to use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the logs.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
