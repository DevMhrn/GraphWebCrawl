#!/usr/bin/env python3
"""
Test script to specifically test deep research DFS functionality
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

# Add project directory to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Load environment variables
load_dotenv()

def test_deep_research_config():
    """Test deep research configuration and DFS functionality"""
    print("🔬 Testing Deep Research DFS Configuration")
    print("=" * 50)
    
    try:
        # Import after environment is loaded
        from research_service import ResearchService
        
        # Create service with test configuration
        crawler_config = {
            'delay': 0.5,
            'timeout': 10,
            'max_pages': 10,  # Small limit for testing
            'headless': True
        }
        
        service = ResearchService(crawler_config=crawler_config)
        
        # Show environment configuration
        bfs_pages = int(os.getenv('DEEP_BFS_PAGES', 20))
        dfs_depth = int(os.getenv('DEEP_DFS_DEPTH', 4))
        max_links_bfs = int(os.getenv('DEEP_MAX_LINKS_BFS', 8))
        max_links_dfs = int(os.getenv('DEEP_MAX_LINKS_DFS', 6))
        delay_multiplier = float(os.getenv('DEEP_DELAY_MULTIPLIER', 1.0))
        
        print(f"📊 Deep Research Environment Configuration:")
        print(f"   BFS Pages: {bfs_pages}")
        print(f"   DFS Depth: {dfs_depth}")
        print(f"   Max Links BFS: {max_links_bfs}")
        print(f"   Max Links DFS: {max_links_dfs}")
        print(f"   Delay Multiplier: {delay_multiplier}")
        
        # Test with a simple query
        print(f"\n🧪 Testing Deep Research with sample query...")
        query = "python programming"
        
        try:
            # This should use the environment variables we just displayed
            analysis, pages, stats = service.deep_research(query)
            
            print(f"\n✅ Deep Research completed successfully!")
            print(f"   Pages crawled: {len(pages)}")
            print(f"   Method: {stats.get('method', 'Unknown')}")
            print(f"   Algorithm: {stats.get('algorithm_type', 'Unknown')}")
            print(f"   BFS Pages config: {stats.get('bfs_pages', 'Unknown')}")
            print(f"   DFS Depth config: {stats.get('dfs_depth', 'Unknown')}")
            
            # Check if DFS was actually used
            if 'graph_metrics' in stats:
                graph_metrics = stats['graph_metrics']
                print(f"   Total nodes: {graph_metrics.get('total_nodes', 0)}")
                print(f"   Crawled nodes: {graph_metrics.get('crawled_nodes', 0)}")
            
        except Exception as e:
            print(f"❌ Deep research failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Cleanup
        service.cleanup()
        
        return True
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🔍 Deep Research DFS Test")
    print("=" * 40)
    
    success = test_deep_research_config()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 Deep Research DFS test completed!")
    else:
        print("❌ Deep Research DFS test failed!")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
