# 🔍 AI Research Crawler

An intelligent web research chatbot that uses graph algorithms (BFS & DFS) to crawl and analyze web content with AI-powered summarization.

## 🌟 Features

### 🔍 Search Research (BFS Algorithm)
- **Algorithm**: Breadth-First Search using Queue (FIFO)
- **Use Case**: Comprehensive but shallow exploration
- **Implementation**: Level-by-level crawling for broad coverage
- **Best For**: Quick overviews, general research

### 🔬 Deep Research (BFS + DFS Algorithm)
- **Phase 1**: BFS for initial 15 pages using Queue
- **Phase 2**: DFS for deep exploration using Stack (LIFO)
- **Use Case**: In-depth analysis with detailed exploration
- **Best For**: Academic research, detailed investigations

### 🤖 AI Analysis
- OpenAI GPT integration for content summarization
- Automatic citation generation
- Confidence scoring
- Key points extraction

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

3. **Run the Application**
   ```bash
   python main.py
   ```
   Or directly:
   ```bash
   streamlit run app.py
   ```

4. **Access the Interface**
   - Open: http://localhost:8501
   - Enter your research query
   - Choose Search or Deep Research
   - View AI-powered analysis with citations

## 🧠 Algorithm Implementation

### BFS (Breadth-First Search)
```python
# Uses Queue (FIFO) for level-by-level exploration
queue = deque()
queue.append(start_url)

while queue:
    url = queue.popleft()  # FIFO
    # Process current page
    # Add child links to queue
```

### DFS (Depth-First Search)
```python
# Uses Stack (LIFO) for deep exploration
stack = []
stack.append(start_url)

while stack:
    url = stack.pop()  # LIFO
    # Process current page
    # Add child links to stack
```

## 📊 Features

- **Real-time Crawling**: Live progress updates
- **Algorithm Visualization**: See how BFS/DFS explores the web
- **Citation Management**: Automatic source tracking
- **Comparison Mode**: Compare both algorithms side-by-side
- **Research History**: Track previous queries
- **Configurable Parameters**: Adjust depth, pages, delays

## 🛠️ Configuration

### Crawler Settings
- **Max Pages**: 10-100 pages per crawl
- **Delay**: 0.5-3.0 seconds between requests
- **Timeout**: 5-30 seconds per request

### Algorithm Parameters
- **Search Depth**: 1-4 levels for BFS
- **Deep BFS Pages**: 5-25 initial pages
- **Deep DFS Depth**: 1-5 levels for deep exploration

## 📁 Project Structure

```
GraphWebCrawler/
├── src/
│   ├── graph_crawler.py      # Core BFS/DFS algorithms
│   ├── llm_service.py         # OpenAI integration
│   ├── research_service.py    # Main research logic
│   └── search_engine.py       # URL generation
├── app.py                     # Streamlit frontend
├── main.py                    # Application runner
├── requirements.txt           # Dependencies
├── .env                       # Configuration
└── README.md                  # This file
```

## 🔧 Technical Details

### Graph Algorithm Implementation
- **BFS**: Uses `collections.deque` for O(1) queue operations
- **DFS**: Uses Python list as stack for LIFO operations
- **Visited Tracking**: Set-based for O(1) lookup
- **URL Normalization**: Proper handling of redirects and fragments

### AI Integration
- **Model**: GPT-3.5-turbo-16k for long content
- **Prompting**: Structured prompts for consistent analysis
- **Fallback**: Works without OpenAI key (basic analysis)
- **Rate Limiting**: Respectful crawling with delays

## 🚨 Usage Guidelines

1. **Respectful Crawling**: Built-in delays prevent server overload
2. **Rate Limiting**: Configurable delays between requests
3. **Content Filtering**: Focuses on text content, filters media
4. **Error Handling**: Graceful failure recovery
5. **Legal Compliance**: Respects robots.txt and terms of service

## 🎯 Use Cases

- **Academic Research**: Deep literature exploration
- **Market Analysis**: Comprehensive industry research
- **News Investigation**: Multi-source information gathering
- **Technical Documentation**: API and framework research
- **Competitive Intelligence**: Product and service analysis

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Implement changes
4. Add tests
5. Submit pull request

## 📄 License

This project is for educational purposes. Please respect website terms of service and implement appropriate rate limiting for production use.
