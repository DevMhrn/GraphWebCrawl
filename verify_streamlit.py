#!/usr/bin/env python3
"""
Quick verification script for Streamlit deployment
Tests the core functionality that Streamlit uses
"""

import sys
import os
sys.path.append('.')

def test_streamlit_research():
    """Test the exact functionality used by Streamlit"""
    print("🧪 Testing Streamlit Research Functionality...")
    print("=" * 50)
    
    try:
        from research_service import ResearchService
        
        # Configure like Streamlit does
        crawler_config = {
            'delay': 1.0,
            'timeout': 10,
            'max_pages': 15,  # Reasonable for demo
            'headless': True
        }
        
        # Initialize service
        print("📡 Initializing Research Service...")
        service = ResearchService(crawler_config=crawler_config)
        
        # Test search research (used by Streamlit)
        test_query = "artificial intelligence"
        print(f"🔍 Testing search research for: '{test_query}'")
        
        analysis, pages, stats = service.search_research(test_query, max_depth=1)
        
        # Check results
        if pages and len(pages) > 0:
            print(f"✅ SUCCESS: Found {len(pages)} pages")
            print(f"📊 Analysis confidence: {analysis.confidence_score}")
            print(f"🔗 Citations: {len(analysis.citations)}")
            print(f"📝 Summary length: {len(analysis.summary)} characters")
            
            # Show some page details
            print(f"\\n📄 Sample pages scraped:")
            for i, (url, page) in enumerate(list(pages.items())[:3]):
                print(f"   {i+1}. {url[:60]}... ({len(page.content)} chars)")
            
            # Cleanup
            service.cleanup()
            
            print(f"\\n🎉 STREAMLIT READY: Your web scraping is working!")
            print(f"   Run: streamlit run app.py")
            return True
            
        else:
            print("❌ FAILED: No pages found")
            service.cleanup()
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_streamlit_deep_research():
    """Test deep research functionality"""
    print("\\n🧪 Testing Deep Research...")
    print("=" * 30)
    
    try:
        from research_service import ResearchService
        
        service = ResearchService({
            'delay': 1.0,
            'timeout': 10,
            'max_pages': 10,
            'headless': True
        })
        
        # Test deep research
        analysis, pages, stats = service.deep_research("machine learning", 
                                                       bfs_pages=5, 
                                                       dfs_depth=2)
        
        if pages and len(pages) > 0:
            print(f"✅ Deep research: {len(pages)} pages")
            service.cleanup()
            return True
        else:
            print("❌ Deep research failed")
            service.cleanup()
            return False
            
    except Exception as e:
        print(f"❌ Deep research error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Streamlit Deployment Verification")
    print("=" * 50)
    
    # Test 1: Basic search research
    search_ok = test_streamlit_research()
    
    # Test 2: Deep research (optional)
    deep_ok = test_streamlit_deep_research()
    
    # Summary
    print("\\n" + "=" * 50)
    print("📋 VERIFICATION SUMMARY")
    print("=" * 50)
    
    if search_ok:
        print("✅ SEARCH RESEARCH: Working")
        print("✅ STREAMLIT READY: Deploy with confidence!")
        
        print("\\n🚀 DEPLOYMENT COMMANDS:")
        print("   Local: streamlit run app.py")
        print("   Production: Set CHROME_HEADLESS=true")
        
        if deep_ok:
            print("✅ DEEP RESEARCH: Also working")
            
    else:
        print("❌ SEARCH RESEARCH: Failed")
        print("❌ STREAMLIT NOT READY: Check the issues above")
        
        print("\\n🛠️  TROUBLESHOOTING:")
        print("   1. Run: python3 debug_scraping.py")
        print("   2. Check Chrome installation")
        print("   3. Verify environment variables")
    
    return search_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
