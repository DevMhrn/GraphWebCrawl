#!/usr/bin/env python3
"""
Debug script to diagnose web scraping issues in Streamlit deployment
"""

import os
import sys
import logging
import time
from pathlib import Path

# Add project directory to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_basic_selenium():
    """Test basic Selenium functionality"""
    print("🧪 Testing Basic Selenium Setup...")
    try:
        from selenium_utils import WebDriverManager
        
        # Test basic driver creation
        driver_manager = WebDriverManager(headless=True, timeout=10)
        success = driver_manager.setup_driver()
        
        if not success:
            print("❌ FAILED: WebDriver setup failed")
            return False
        
        # Test page loading
        test_url = "https://httpbin.org/html"
        page_success = driver_manager.get_page(test_url)
        
        if not page_success:
            print("❌ FAILED: Page loading failed")
            driver_manager.close()
            return False
        
        # Test content extraction
        source = driver_manager.get_page_source()
        if not source or len(source) < 100:
            print("❌ FAILED: No content extracted")
            driver_manager.close()
            return False
        
        print(f"✅ SUCCESS: Extracted {len(source)} characters")
        driver_manager.close()
        return True
        
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_graph_crawler():
    """Test GraphWebCrawler functionality"""
    print("\n🧪 Testing GraphWebCrawler...")
    try:
        from graph_crawler import GraphWebCrawler
        
        # Create crawler
        crawler = GraphWebCrawler(
            delay=1.0,
            timeout=10,
            max_pages=3,
            headless=True
        )
        
        # Test simple crawl
        test_urls = ["https://httpbin.org/html"]
        print(f"Testing crawl with: {test_urls}")
        
        pages = crawler.search_crawl_bfs(test_urls, max_depth=1)
        
        if not pages:
            print("❌ FAILED: No pages crawled")
            crawler.close_driver()
            return False
        
        print(f"✅ SUCCESS: Crawled {len(pages)} pages")
        for url, page in pages.items():
            print(f"   📄 {url} - {page.title[:50]}... ({len(page.content)} chars)")
        
        crawler.close_driver()
        return True
        
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_research_service():
    """Test ResearchService functionality"""
    print("\n🧪 Testing ResearchService...")
    try:
        from research_service import ResearchService
        
        # Configure for testing
        crawler_config = {
            'delay': 1.0,
            'timeout': 10,
            'max_pages': 2,
            'headless': True
        }
        
        service = ResearchService(crawler_config=crawler_config)
        
        # Test search research
        query = "python web scraping"
        print(f"Testing research query: {query}")
        
        analysis, pages, stats = service.search_research(query, max_depth=1)
        
        if not pages:
            print("❌ FAILED: No pages found in research")
            service.cleanup()
            return False
        
        print(f"✅ SUCCESS: Research found {len(pages)} pages")
        print(f"   Analysis confidence: {analysis.confidence_score}")
        
        service.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment_config():
    """Test environment configuration"""
    print("\n🧪 Testing Environment Configuration...")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check key environment variables
        openai_key = os.getenv('OPENAI_API_KEY')
        user_agent = os.getenv('USER_AGENT')
        
        print(f"OpenAI API Key: {'✅ Set' if openai_key else '❌ Missing'}")
        print(f"User Agent: {user_agent[:50]}..." if user_agent else "❌ Missing")
        
        # Check crawler settings
        search_depth = os.getenv('SEARCH_MAX_DEPTH', '1')
        search_pages = os.getenv('SEARCH_MAX_PAGES', '25')
        
        print(f"Search Max Depth: {search_depth}")
        print(f"Search Max Pages: {search_pages}")
        
        return True
        
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

def diagnose_streamlit_issues():
    """Diagnose potential Streamlit deployment issues"""
    print("\n🧪 Diagnosing Streamlit Deployment Issues...")
    
    issues_found = []
    
    # Check Chrome installation
    try:
        import subprocess
        result = subprocess.run(['which', 'google-chrome'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            result = subprocess.run(['which', 'chromium'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                issues_found.append("❌ Chrome/Chromium not found in PATH")
            else:
                print("✅ Chromium found")
        else:
            print("✅ Google Chrome found")
    except Exception as e:
        issues_found.append(f"❌ Cannot check Chrome installation: {e}")
    
    # Check system resources
    try:
        import psutil
        memory_gb = psutil.virtual_memory().total / (1024**3)
        print(f"📊 System Memory: {memory_gb:.1f} GB")
        if memory_gb < 1:
            issues_found.append("⚠️  Low system memory (< 1GB)")
    except ImportError:
        print("📊 psutil not available - cannot check memory")
    
    # Check display environment
    display = os.getenv('DISPLAY')
    if not display and not os.getenv('XVFB'):
        issues_found.append("⚠️  No DISPLAY environment and no XVFB")
        print("💡 For headless servers, consider installing xvfb")
    
    # Check permissions
    try:
        import tempfile
        with tempfile.NamedTemporaryFile() as f:
            f.write(b"test")
        print("✅ File system write access OK")
    except Exception as e:
        issues_found.append(f"❌ File system access issue: {e}")
    
    if issues_found:
        print("\n🚨 Potential Issues Found:")
        for issue in issues_found:
            print(f"   {issue}")
        return False
    else:
        print("\n✅ No obvious deployment issues found")
        return True

def main():
    """Main diagnostic function"""
    print("🔍 Web Scraping Diagnostic Tool")
    print("=" * 50)
    
    tests = [
        ("Environment Configuration", test_environment_config),
        ("Basic Selenium", test_basic_selenium),
        ("GraphWebCrawler", test_graph_crawler),
        ("ResearchService", test_research_service),
        ("Streamlit Deployment Issues", diagnose_streamlit_issues)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("📋 DIAGNOSTIC SUMMARY")
    print("="*60)
    
    passed = 0
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{len(results)} tests passed")
    
    if passed != len(results):
        print("\n🛠️  RECOMMENDATIONS:")
        if not results.get("Basic Selenium", True):
            print("   1. Install Chrome/Chromium browser")
            print("   2. Check if running in headless environment")
            print("   3. Install xvfb for headless servers: sudo apt-get install xvfb")
        
        if not results.get("Environment Configuration", True):
            print("   4. Set up .env file with required variables")
            print("   5. Set OPENAI_API_KEY for AI features")
        
        print("   6. For cloud deployment, ensure Chrome is properly installed")
        print("   7. Consider using Docker with pre-installed Chrome")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
