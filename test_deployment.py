#!/usr/bin/env python3
"""
Quick deployment test for Streamlit environments
This simulates the Chrome failure scenario and tests fallback
"""

import sys
import os
sys.path.append('.')

def test_deployment_scenario():
    """Test the exact scenario seen in deployment"""
    print("🚀 Testing Deployment Scenario")
    print("=" * 50)
    
    # Test 1: Search Engine with fallback URLs
    try:
        from search_engine import SearchEngine
        engine = SearchEngine()
        urls = engine.get_search_urls("hi")  # Same query from your error
        
        if urls and len(urls) > 0:
            print(f"✅ Search Engine: Generated {len(urls)} URLs")
            print(f"   Sample URLs: {urls[:3]}")
        else:
            print("❌ Search Engine: No URLs generated")
            return False
            
    except Exception as e:
        print(f"❌ Search Engine failed: {e}")
        return False
    
    # Test 2: Graph Crawler with fallback (simulate Chrome failure)
    try:
        from graph_crawler import GraphWebCrawler
        
        # Create crawler that might fail Chrome setup
        crawler = GraphWebCrawler(delay=1.0, timeout=10, max_pages=3, headless=True)
        
        # Force use fallback by disabling selenium
        crawler.selenium_available = False
        
        # Test with the generated URLs
        test_urls = urls[:2]  # Test with first 2 URLs
        print(f"🧪 Testing crawl with fallback scraper...")
        
        pages = crawler.search_crawl_bfs(test_urls, max_depth=1)
        
        if pages and len(pages) > 0:
            print(f"✅ Graph Crawler: Crawled {len(pages)} pages using fallback")
            for url, page in pages.items():
                method = getattr(page, 'metadata', {}).get('method', 'unknown')
                print(f"   📄 {url[:50]}... - Method: {method}")
        else:
            print("❌ Graph Crawler: No pages crawled")
            return False
            
        crawler.close_driver()
        
    except Exception as e:
        print(f"❌ Graph Crawler failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Full Research Service
    try:
        from research_service import ResearchService
        
        # Configure for deployment-like environment
        crawler_config = {
            'delay': 1.0,
            'timeout': 10,
            'max_pages': 5,
            'headless': True
        }
        
        service = ResearchService(crawler_config=crawler_config)
        
        # Force fallback mode to simulate deployment
        if hasattr(service.crawler, 'selenium_available'):
            service.crawler.selenium_available = False
        
        analysis, pages, stats = service.search_research("hi", max_depth=1)
        
        if pages and len(pages) > 0:
            print(f"✅ Research Service: Found {len(pages)} pages")
            print(f"   Confidence: {analysis.confidence_score}")
            print(f"   Citations: {len(analysis.citations)}")
        else:
            print("❌ Research Service: No pages found")
            return False
            
        service.cleanup()
        
    except Exception as e:
        print(f"❌ Research Service failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n🎉 DEPLOYMENT TEST PASSED!")
    print("✅ Your app should work in deployment even without Chrome")
    return True

def main():
    """Main test function"""
    success = test_deployment_scenario()
    
    if success:
        print("\n🚀 READY FOR DEPLOYMENT!")
        print("📋 What was fixed:")
        print("   1. ✅ Added packages.txt for Chrome installation")
        print("   2. ✅ Enhanced Selenium with better Chrome detection")
        print("   3. ✅ Added fallback scraper using requests")
        print("   4. ✅ Modified graph crawler to use fallback")
        print("   5. ✅ Added fallback URLs in search engine")
        
        print("\n📂 Files to deploy:")
        print("   - packages.txt (for Chrome installation)")
        print("   - .streamlit/config.toml (for Streamlit config)")
        print("   - All existing Python files")
        
        print("\n🎯 The fallback system will work even if Chrome fails!")
        
    else:
        print("\n❌ DEPLOYMENT TEST FAILED")
        print("🛠️  Check the errors above and fix before deploying")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
