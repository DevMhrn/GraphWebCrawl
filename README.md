# 🔍 AI Research Crawler (Enhanced with Selenium & Graph Structure)

An intelligent web research chatbot that uses graph algorithms (BFS & DFS) to crawl and analyze web content with AI-powered summarization. **Now enhanced with Selenium for robust web scraping and proper graph data structures.**

## 🌟 New Features (v2.0)

### 🚀 Selenium-Based Web Scraping
- **Robust Browser Automation**: Uses Selenium WebDriver for reliable page loading
- **JavaScript Support**: Handles dynamic content and SPA applications
- **Anti-Detection**: Optimized browser settings to avoid blocking
- **Auto-Recovery**: Automatic driver restart on failures
- **Performance Optimized**: Disabled images, CSS, and plugins for faster crawling

### 🕸️ True Graph Data Structure
- **GraphNode Objects**: Proper node-based representation with unique IDs
- **Parent-Child Relationships**: Maintains proper hierarchical connections
- **Queue/Stack with Nodes**: BFS/DFS operations work with actual graph nodes
- **Graph Visualization**: Generate data for network visualization
- **Enhanced Statistics**: Graph-specific metrics and connectivity analysis

### 🔍 Search Research (BFS Algorithm)
- **Algorithm**: Breadth-First Search using Node Queue (FIFO)
- **Use Case**: Comprehensive but shallow exploration
- **Implementation**: Level-by-level crawling with proper graph structure
- **Best For**: Quick overviews, general research

### 🔬 Deep Research (BFS + DFS Algorithm)
- **Phase 1**: BFS for initial seed nodes using Node Queue
- **Phase 2**: DFS for deep exploration using Node Stack (LIFO)
- **Use Case**: In-depth analysis with detailed exploration
- **Best For**: Academic research, detailed investigations

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set OpenAI API Key**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
   Or create a `.env` file:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

3. **Test the Enhanced Crawler**
   ```bash
   python test_enhanced_crawler.py
   ```

4. **Run the Application**
   ```bash
   python main.py
   ```
   Or directly:
   ```bash
   streamlit run app.py
   ```

5. **Access the Interface**
   - Open: http://localhost:8501
   - Enter your research query
   - Choose Search or Deep Research
   - View AI-powered analysis with citations

## 🧠 Enhanced Algorithm Implementation

### GraphNode Structure
```python
@dataclass
class GraphNode:
    id: str                    # Unique node identifier
    url: str                   # Page URL
    title: str                 # Page title
    content: str               # Extracted content
    depth: int                 # Crawl depth
    parent_node_id: str        # Parent node reference
    child_node_ids: List[str]  # Child node references
    outbound_links: List[str]  # Links found on page
    crawl_status: str          # pending/crawled/failed
    metadata: Dict             # Additional page metadata
```

### BFS with Graph Nodes
```python
# Uses Node Queue (FIFO) for level-by-level exploration
node_queue = deque()  # Queue of GraphNode objects
root_node = self._create_node(url, depth=0)
node_queue.append(root_node)

while node_queue:
    current_node = node_queue.popleft()  # FIFO
    # Process current node with Selenium
    # Create child nodes and add to queue
    for link in current_node.outbound_links:
        child_node = self._create_node(link, depth + 1, current_node.id)
        node_queue.append(child_node)
```

### DFS with Graph Nodes
```python
# Uses Node Stack (LIFO) for deep exploration
node_stack = []  # Stack of GraphNode objects
node_stack.append(start_node)

while node_stack:
    current_node = node_stack.pop()  # LIFO
    # Process current node with Selenium
    # Create child nodes and add to stack
    for link in current_node.outbound_links:
        child_node = self._create_node(link, depth + 1, current_node.id)
        node_stack.append(child_node)
```

## �️ Technical Improvements

### Selenium WebDriver Manager
- **Auto-Installation**: Automatic ChromeDriver management
- **Optimized Settings**: Performance-tuned browser configuration
- **Error Handling**: Robust exception handling and recovery
- **Resource Management**: Proper cleanup and session management

### Graph Analytics
- **Node Relationships**: Track parent-child connections
- **Connectivity Metrics**: Analyze graph structure and density
- **Visualization Data**: Export data for network visualization
- **Success Rates**: Monitor crawling success and failure rates

### Enhanced Error Handling
- **Selenium Failures**: Automatic driver restart on errors
- **Page Load Issues**: Graceful handling of timeouts
- **Content Filtering**: Skip invalid or minimal content
- **Graph Consistency**: Maintain graph integrity on failures

## 📊 New Features

### Graph Visualization Support
```python
# Get graph data for visualization
viz_data = crawler.get_graph_visualization_data()
# Returns: {'nodes': [...], 'edges': [...], 'stats': {...}}
```

### Enhanced Statistics
```python
statistics = crawler.get_crawl_statistics(pages)
# Includes graph metrics:
# - Total nodes vs. crawled nodes
# - Success/failure rates
# - Node connectivity metrics
# - Depth distribution
# - Graph density analysis
```

### WebDriver Management
```python
from selenium_utils import WebDriverManager

# Context manager for safe WebDriver usage
with WebDriverManager(headless=True) as driver_manager:
    success = driver_manager.get_page(url)
    content = driver_manager.get_page_source()
```

## � Configuration Options

### Crawler Settings
```python
crawler_config = {
    'delay': 1.0,          # Delay between requests
    'timeout': 10,         # Page load timeout
    'max_pages': 50,       # Maximum pages to crawl
    'headless': True       # Run browser in headless mode
}
```

### Algorithm Parameters
- **Search Depth**: 1-4 levels for BFS
- **Deep BFS Pages**: 5-25 initial seed nodes
- **Deep DFS Depth**: 1-5 levels for deep exploration

## 📁 Enhanced Project Structure

```
GraphWebCrawler/
├── graph_crawler.py         # Enhanced BFS/DFS with Selenium & Graph
├── selenium_utils.py        # WebDriver management utilities
├── llm_service.py          # OpenAI integration
├── research_service.py     # Main research logic (updated)
├── search_engine.py        # URL generation
├── app.py                  # Streamlit frontend
├── main.py                 # Application runner
├── test_enhanced_crawler.py # Comprehensive test suite
├── requirements.txt        # Updated dependencies
├── .env                    # Configuration
└── README.md               # This file
```

## 🧪 Testing

Run the comprehensive test suite:
```bash
python test_enhanced_crawler.py
```

Tests include:
- ✅ Selenium WebDriver setup
- ✅ Graph node creation and relationships
- ✅ BFS crawling with real websites
- ✅ ResearchService integration
- ✅ AI analysis pipeline

## 🚨 Enhanced Usage Guidelines

1. **Robust Crawling**: Selenium handles complex JavaScript sites
2. **Graph Structure**: Proper node relationships for analysis
3. **Performance**: Optimized browser settings for speed
4. **Error Recovery**: Automatic handling of common failures
5. **Resource Management**: Proper cleanup prevents memory leaks

## 🎯 Use Cases

- **Academic Research**: Deep literature exploration with graph analysis
- **Market Analysis**: Comprehensive industry research with relationships
- **News Investigation**: Multi-source information gathering
- **Technical Documentation**: API and framework research with dependencies
- **Competitive Intelligence**: Product analysis with connection mapping

## 📈 Performance Improvements

### Selenium Optimizations
- **Headless Mode**: Faster execution without GUI
- **Disabled Resources**: Images, CSS, plugins disabled
- **Page Load Strategy**: Eager loading for faster response
- **Memory Management**: Aggressive cache settings

### Graph Efficiency
- **O(1) Node Lookup**: HashMap-based node storage
- **Efficient Relationships**: Direct parent-child references
- **Memory Optimized**: Only essential data in nodes
- **Lazy Loading**: Content loaded only when needed

## 🔄 Migration from v1.0

The enhanced crawler is backward compatible:
- `PageInfo` objects are automatically created from `GraphNode`
- Existing APIs remain unchanged
- New graph features are opt-in
- Statistics include both old and new metrics

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Implement changes with tests
4. Run the test suite: `python test_enhanced_crawler.py`
5. Submit pull request

## 📄 License

This project is for educational purposes. Please respect website terms of service and implement appropriate rate limiting for production use.

---

**Enhanced with Selenium WebDriver and True Graph Data Structures for Robust, Intelligent Web Crawling** 🚀
