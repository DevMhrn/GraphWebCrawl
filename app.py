import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import logging
import os
from datetime import datetime
from research_service import ResearchService
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS for Dark Theme
st.markdown("""
<style>
    /* Dark theme base */
    .stApp {
        background: linear-gradient(135deg, #0c1426 0%, #1a1f3a 100%);
        color: #ffffff;
    }
    
    /* Main container styling */
    .main-container {
        background: rgba(25, 32, 56, 0.8);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        text-align: center;
        color: #a0a8b8;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    /* Algorithm Cards */
    .algorithm-card {
        background: linear-gradient(145deg, #1e2a47 0%, #2d3b5f 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        text-align: center;
        border: 2px solid transparent;
        transition: all 0.3s ease;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .algorithm-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        border-radius: 20px;
        padding: 2px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        mask-composite: exclude;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .algorithm-card:hover::before {
        opacity: 1;
    }
    
    .algorithm-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.2);
    }
    
    .bfs-card {
        background: linear-gradient(145deg, #1a2a4a 0%, #2a4a6a 100%);
    }
    
    .hybrid-card {
        background: linear-gradient(145deg, #2a1a4a 0%, #4a2a6a 100%);
    }
    
    .algorithm-card h3 {
        color: #ffffff;
        font-size: 1.5rem;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    .algorithm-card p {
        color: #b8c1d9;
        margin: 0.5rem 0;
        font-size: 0.95rem;
    }
    
    .algorithm-card strong {
        color: #ffffff;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 1rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 25px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        background: rgba(25, 32, 56, 0.8);
        border: 2px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        color: #ffffff;
        padding: 1rem;
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
    }
    
    /* Progress bars */
    .stProgress > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Metrics */
    .metric-container {
        background: rgba(25, 32, 56, 0.6);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    .metric-container:hover {
        background: rgba(25, 32, 56, 0.8);
        transform: translateY(-2px);
    }
    
    /* Research results */
    .research-results {
        background: rgba(25, 32, 56, 0.6);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .key-finding {
        background: rgba(102, 126, 234, 0.1);
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 10px 10px 0;
    }
    
    /* Citations */
    .citation-box {
        background: rgba(25, 32, 56, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .citation-box:hover {
        border-color: #667eea;
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.2);
    }
    
    /* Page summaries */
    .page-summary {
        background: rgba(25, 32, 56, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .page-summary:hover {
        background: rgba(25, 32, 56, 0.8);
        border-color: #667eea;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: rgba(12, 20, 38, 0.9);
    }
    
    /* Algorithm visualization */
    .queue-visualization {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-left: 4px solid #667eea;
        border-radius: 0 15px 15px 0;
        padding: 1.5rem;
        margin: 1rem 0;
        font-family: 'Courier New', monospace;
        color: #b8c1d9;
    }
    
    .stack-visualization {
        background: linear-gradient(135deg, rgba(233, 30, 99, 0.1) 0%, rgba(156, 39, 176, 0.1) 100%);
        border-left: 4px solid #e91e63;
        border-radius: 0 15px 15px 0;
        padding: 1.5rem;
        margin: 1rem 0;
        font-family: 'Courier New', monospace;
        color: #b8c1d9;
    }
    
    /* Status messages */
    .status-success {
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.2) 0%, rgba(139, 195, 74, 0.2) 100%);
        border: 1px solid rgba(76, 175, 80, 0.3);
        border-radius: 15px;
        padding: 1rem;
        color: #81c784;
    }
    
    .status-info {
        background: linear-gradient(135deg, rgba(33, 150, 243, 0.2) 0%, rgba(103, 58, 183, 0.2) 100%);
        border: 1px solid rgba(33, 150, 243, 0.3);
        border-radius: 15px;
        padding: 1rem;
        color: #90caf9;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(25, 32, 56, 0.6);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Method badge */
    .method-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Links */
    a {
        color: #667eea;
        text-decoration: none;
        transition: color 0.3s ease;
    }
    
    a:hover {
        color: #764ba2;
        text-decoration: underline;
    }
    
    /* Section dividers */
    .section-divider {
        height: 2px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 2px;
        margin: 2rem 0;
        opacity: 0.3;
    }
    
    /* Loading states */
    .loading-container {
        text-align: center;
        padding: 2rem;
        background: rgba(25, 32, 56, 0.6);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .algorithm-card {
            padding: 1.5rem;
        }
        
        .main-header {
            font-size: 2rem;
        }
        
        .sub-header {
            font-size: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state for chatbot"""
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []
    if 'research_service' not in st.session_state:
        # Initialize with environment variables
        st.session_state.research_service = ResearchService(
            crawler_config={
                'max_pages': int(os.getenv('MAX_PAGES_PER_CRAWL', 50)),
                'delay': float(os.getenv('DEFAULT_DELAY', 1.0)),
                'timeout': int(os.getenv('DEFAULT_TIMEOUT', 10))
            },
            llm_config={
                'api_key': os.getenv('OPENAI_API_KEY')
            }
        )

def add_message(role: str, content: str, metadata: dict = None):
    """Add message to conversation"""
    st.session_state.conversation.append({
        'role': role,
        'content': content,
        'timestamp': datetime.now(),
        'metadata': metadata or {}
    })

def display_conversation():
    """Display the conversation history"""
    for message in st.session_state.conversation:
        if message['role'] == 'user':
            st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-message">{message["content"]}</div>', unsafe_allow_html=True)
            
            # Display research results if available
            if 'research_result' in message['metadata']:
                display_research_results(message['metadata']['research_result'])

def display_research_results(research_data):
    """Display detailed research results with citations"""
    analysis_result = research_data['analysis']
    statistics = research_data['statistics']
    method = research_data['method']
    
    # Method badge
    st.markdown(f'<div class="method-badge">{method}</div>', unsafe_allow_html=True)
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Pages Analyzed", statistics.get('total_pages', 0))
    with col2:
        st.metric("Max Depth", statistics.get('max_depth', 0))
    with col3:
        st.metric("Confidence", f"{analysis_result.confidence_score:.1%}")
    with col4:
        st.metric("Time Taken", f"{statistics.get('crawl_time', 0):.1f}s")
    
    # Key findings
    st.markdown("**🔍 Key Findings:**")
    for i, point in enumerate(analysis_result.key_points, 1):
        st.markdown(f"**{i}.** {point}")
    
    # Individual page summaries with citations
    if hasattr(analysis_result, 'page_summaries') and analysis_result.page_summaries:
        with st.expander("📄 Individual Page Summaries", expanded=False):
            for i, page_summary in enumerate(analysis_result.page_summaries[:10], 1):
                st.markdown(f"""
                <div class="page-summary">
                    <strong>{i}. {page_summary.title}</strong> 
                    <span style="color: #28a745;">(Relevance: {page_summary.relevance_score:.1f})</span><br>
                    <a href="{page_summary.url}" target="_blank" style="font-size: 0.9em;">{page_summary.url}</a><br>
                    <p style="margin-top: 8px;">{page_summary.summary}</p>
                    <strong>Key Points:</strong> {', '.join(page_summary.key_points)}
                </div>
                """, unsafe_allow_html=True)
    
    # Sources & Citations
    st.markdown("**📚 Sources & Citations:**")
    for citation in analysis_result.citations:
        st.markdown(f"""
        <div class="citation-box">
            <strong>{citation.get('source', 'Unknown Source')}</strong><br>
            <a href="{citation.get('url', '#')}" target="_blank">{citation.get('url', 'No URL')}</a><br>
            <em>{citation.get('relevance', 'Relevant to the research topic')}</em>
        </div>
        """, unsafe_allow_html=True)

def process_user_query(query: str):
    """Process user query and determine the appropriate research method"""
    query_lower = query.lower()
    
    # Determine research method based on query keywords
    if any(word in query_lower for word in ['deep', 'detailed', 'comprehensive', 'thorough', 'in-depth']):
        method = 'deep'
    elif any(word in query_lower for word in ['compare', 'comparison', 'both methods', 'versus']):
        method = 'compare'
    else:
        method = 'search'  # Default to search method
    
    return method

def perform_research(query: str, method: str):
    """Perform research based on the specified method"""
    service = st.session_state.research_service
    
    try:
        if method == 'search':
            analysis_result, crawled_pages, statistics = service.search_research(
                query, max_depth=int(os.getenv('SEARCH_MAX_DEPTH', 2))
            )
            return {
                'analysis': analysis_result,
                'statistics': statistics,
                'method': 'Search (BFS)',
                'pages_count': len(crawled_pages)
            }
        
        elif method == 'deep':
            analysis_result, crawled_pages, statistics = service.deep_research(
                query, 
                bfs_pages=int(os.getenv('DEEP_BFS_PAGES', 15)),
                dfs_depth=int(os.getenv('DEEP_DFS_DEPTH', 3))
            )
            return {
                'analysis': analysis_result,
                'statistics': statistics,
                'method': 'Deep Research (BFS + DFS)',
                'pages_count': len(crawled_pages)
            }
        
        elif method == 'compare':
            comparison_result = service.get_research_comparison(query)
            # For chat interface, return the better performing method
            if comparison_result['comparison_metrics']['pages_ratio'] > 1.5:
                return {
                    'analysis': comparison_result['deep_method']['analysis'],
                    'statistics': comparison_result['deep_method']['statistics'],
                    'method': 'Deep Research (Selected from Comparison)',
                    'pages_count': comparison_result['deep_method']['pages_count']
                }
            else:
                return {
                    'analysis': comparison_result['search_method']['analysis'],
                    'statistics': comparison_result['search_method']['statistics'],
                    'method': 'Search (Selected from Comparison)',
                    'pages_count': comparison_result['search_method']['pages_count']
                }
    
    except Exception as e:
        logger.error(f"Research error: {e}")
        raise e

def display_algorithm_comparison():
    """Display algorithm comparison in sidebar with enhanced styling"""
    st.sidebar.markdown("## 🔬 Algorithm Comparison")
    
    # BFS Algorithm Card
    st.sidebar.markdown("""
    <div class="algorithm-card bfs-card" style="margin: 1rem 0;">
        <h4 style="color: #4facfe; margin-bottom: 1rem;">🔍 BFS (Search)</h4>
        <p><strong>Data Structure:</strong> Queue (FIFO)</p>
        <p><strong>Pattern:</strong> Level-by-level</p>
        <p><strong>Time:</strong> Fast (~30-60s)</p>
        <p><strong>Best for:</strong> Quick overview</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Hybrid Algorithm Card  
    st.sidebar.markdown("""
    <div class="algorithm-card hybrid-card" style="margin: 1rem 0;">
        <h4 style="color: #fa709a; margin-bottom: 1rem;">🔬 BFS+DFS (Deep)</h4>
        <p><strong>Phase 1:</strong> Queue for seeds</p>
        <p><strong>Phase 2:</strong> Stack for depth</p>
        <p><strong>Time:</strong> Thorough (~2-5min)</p>
        <p><strong>Best for:</strong> Comprehensive analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ Algorithm Properties")
    
    comparison_df = pd.DataFrame({
        'Property': ['Time Complexity', 'Space Complexity', 'Completeness', 'Optimality'],
        'BFS': ['O(V+E)', 'O(V)', 'Complete', 'Optimal'],
        'BFS+DFS': ['O(V+E)', 'O(h)', 'Complete', 'Near-optimal']
    })
    st.sidebar.dataframe(comparison_df, use_container_width=True)

def display_algorithm_visualization(statistics):
    """Display algorithm visualization based on method used"""
    if statistics.get('algorithm_type') == 'search_bfs':
        st.markdown("### 🔍 BFS Algorithm Visualization")
        st.markdown("""
        <div class="queue-visualization">
        <strong>Queue (FIFO) Operation:</strong><br>
        1. Start URLs → [url1, url2, url3] → Queue<br>
        2. Dequeue url1 → Process → Add children to rear<br>
        3. Dequeue url2 → Process → Add children to rear<br>
        4. Continue level-by-level exploration...
        </div>
        """, unsafe_allow_html=True)
        
        # Create depth distribution chart
        if 'pages_by_depth' in statistics:
            depth_data = statistics['pages_by_depth']
            fig = px.bar(
                x=list(depth_data.keys()), 
                y=list(depth_data.values()),
                title="BFS: Pages Discovered by Depth Level",
                labels={'x': 'Depth Level', 'y': 'Number of Pages'}
            )
            fig.update_traces(marker_color='#4facfe')
            st.plotly_chart(fig, use_container_width=True)
    
    elif statistics.get('algorithm_type') == 'hybrid_bfs_dfs':
        st.markdown("### 🔬 BFS+DFS Hybrid Algorithm Visualization")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="queue-visualization">
            <strong>Phase 1 - BFS Queue:</strong><br>
            • Collect seed pages<br>
            • Breadth-first exploration<br>
            • Build foundation knowledge
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="stack-visualization">
            <strong>Phase 2 - DFS Stack:</strong><br>
            • Deep dive from seeds<br>
            • Stack-based exploration<br>
            • Detailed investigation
            </div>
            """, unsafe_allow_html=True)
        
        # Create phase distribution chart
        if 'pages_by_depth' in statistics:
            depth_data = statistics['pages_by_depth']
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=list(depth_data.keys()), 
                y=list(depth_data.values()),
                name='Pages by Depth',
                marker_color=['#4facfe' if d <= 2 else '#fa709a' for d in depth_data.keys()]
            ))
            fig.update_layout(
                title="Hybrid: BFS Seeds (Blue) + DFS Deep Exploration (Pink)",
                xaxis_title="Depth Level",
                yaxis_title="Number of Pages"
            )
            st.plotly_chart(fig, use_container_width=True)

def display_enhanced_statistics(statistics):
    """Display enhanced statistics with algorithm details"""
    st.markdown("### 📊 Crawl Statistics & Algorithm Analysis")
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📄 Total Pages", statistics.get('total_pages', 0))
    with col2:
        st.metric("🏗️ Max Depth", statistics.get('max_depth', 0))
    with col3:
        st.metric("🌐 Unique Domains", statistics.get('unique_domains', 0))
    with col4:
        st.metric("⏱️ Crawl Time", f"{statistics.get('crawl_time', 0):.1f}s")
    
    # Algorithm details
    st.markdown("""
    <div class="algorithm-stats">
    <h4>🔧 Algorithm Details</h4>
    """, unsafe_allow_html=True)
    
    st.markdown(f"**Method:** {statistics.get('method', 'Unknown')}")
    st.markdown(f"**Data Structure:** {statistics.get('data_structure', 'Unknown')}")
    st.markdown(f"**Exploration Pattern:** {statistics.get('exploration_pattern', 'Unknown')}")
    st.markdown(f"**Best Use Case:** {statistics.get('best_for', 'Unknown')}")
    st.markdown(f"**Algorithm Details:** {statistics.get('algorithm_details', 'Unknown')}")
    
    if statistics.get('algorithm_type') == 'hybrid_bfs_dfs':
        st.markdown(f"**Phase 1:** {statistics.get('phase_1', 'Unknown')} ({statistics.get('bfs_pages', 0)} pages)")
        st.markdown(f"**Phase 2:** {statistics.get('phase_2', 'Unknown')} (depth {statistics.get('dfs_depth', 0)})")
    
    st.markdown("</div>", unsafe_allow_html=True)

def main():
    """Main application with enhanced dark theme UI"""
    initialize_session_state()
    
    # Main container
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Enhanced Header
    st.markdown("""
    <h1 class="main-header">🤖 AI Research Assistant</h1>
    <p class="sub-header">Choose your research method: Quick Search (BFS) or Deep Research (BFS+DFS)</p>
    <div class="section-divider"></div>
    """, unsafe_allow_html=True)
    
    # Research Method Selection with enhanced styling
    st.markdown("## 🎯 Choose Research Method")
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("""
        <div class="algorithm-card bfs-card">
            <h3>🔍 Search Research</h3>
            <p><strong>Algorithm:</strong> BFS (Breadth-First Search)</p>
            <p><strong>Data Structure:</strong> Queue (FIFO)</p>
            <p><strong>Pattern:</strong> Level-by-level exploration</p>
            <p><strong>Best for:</strong> Quick overview, broad coverage</p>
            <p><strong>Time:</strong> Fast (~30-60 seconds)</p>
            <p><strong>Pages:</strong> ~20-30 pages analyzed</p>
        </div>
        """, unsafe_allow_html=True)
        
        search_button = st.button(
            "🔍 Start Search Research", 
            key="search_btn",
            use_container_width=True,
            type="primary",
            help="Use BFS algorithm for quick, broad research"
        )
    
    with col2:
        st.markdown("""
        <div class="algorithm-card hybrid-card">
            <h3>🔬 Deep Research</h3>
            <p><strong>Algorithm:</strong> BFS + DFS (Hybrid)</p>
            <p><strong>Data Structure:</strong> Queue + Stack</p>
            <p><strong>Pattern:</strong> Broad then deep exploration</p>
            <p><strong>Best for:</strong> Comprehensive analysis</p>
            <p><strong>Time:</strong> Thorough (~2-5 minutes)</p>
            <p><strong>Pages:</strong> ~40-60 pages analyzed</p>
        </div>
        """, unsafe_allow_html=True)
        
        deep_button = st.button(
            "🔬 Start Deep Research", 
            key="deep_btn",
            use_container_width=True,
            type="secondary",
            help="Use hybrid BFS+DFS algorithm for comprehensive research"
        )
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Enhanced Query input
    st.markdown("### ✍️ Research Query")
    user_query = st.text_input(
        "",
        placeholder="e.g., 'Latest developments in artificial intelligence' or 'Best practices for software deployment'",
        key="research_query",
        help="Enter your research question - the AI will find and analyze relevant sources"
    )
    
    # Process research requests with enhanced UI
    if (search_button or deep_button) and user_query:
        research_type = "search" if search_button else "deep"
        
        # Enhanced research progress container
        st.markdown('<div class="loading-container">', unsafe_allow_html=True)
        st.markdown(f"## 🔄 {research_type.title()} Research in Progress...")
        
        # Algorithm explanation with better styling
        if research_type == "search":
            st.markdown("""
            <div class="status-info">
                🔍 <strong>BFS Algorithm Active</strong><br>
                Using queue (FIFO) for level-by-level exploration<br>
                Analyzing pages breadth-first for comprehensive coverage
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="status-info">
                🔬 <strong>Hybrid Algorithm Active</strong><br>
                Phase 1: BFS (queue) → Phase 2: DFS (stack)<br>
                Combining broad and deep exploration strategies
            </div>
            """, unsafe_allow_html=True)
        
        # Enhanced progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            with st.spinner(f"Executing {research_type} research algorithm..."):
                service = st.session_state.research_service
                
                if research_type == "search":
                    progress_bar.progress(25)
                    status_text.markdown("🔍 **Initializing BFS queue with seed URLs...**")
                    
                    analysis_result, crawled_pages, statistics = service.search_research(
                        user_query, max_depth=2
                    )
                else:
                    progress_bar.progress(25)
                    status_text.markdown("🔬 **Phase 1: BFS seed collection...**")
                    time.sleep(1)
                    progress_bar.progress(50)
                    status_text.markdown("🔬 **Phase 2: DFS deep exploration...**")
                    
                    analysis_result, crawled_pages, statistics = service.deep_research(
                        user_query, bfs_pages=15, dfs_depth=3
                    )
                
                progress_bar.progress(75)
                status_text.markdown("🤖 **AI analysis in progress...**")
                time.sleep(1)
                progress_bar.progress(100)
                status_text.markdown("✅ **Research completed successfully!**")
        
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Enhanced success message
            st.markdown(f"""
            <div class="status-success">
                🎉 <strong>{research_type.title()} Research Completed Successfully!</strong><br>
                Analyzed {len(crawled_pages)} pages using {statistics.get('method', 'Unknown')} algorithm
            </div>
            """, unsafe_allow_html=True)
            
            # Enhanced algorithm visualization
            display_algorithm_visualization(statistics)
            
            # Enhanced statistics with better layout
            display_enhanced_statistics(statistics)
            
            # Enhanced research results
            st.markdown('<div class="research-results">', unsafe_allow_html=True)
            st.markdown("## 📋 Research Results")
            
            # Enhanced summary section
            st.markdown("### 📝 Executive Summary")
            st.markdown(f"""
            <div style="background: rgba(102, 126, 234, 0.1); border-radius: 15px; padding: 1.5rem; margin: 1rem 0;">
                {analysis_result.summary}
            </div>
            """, unsafe_allow_html=True)
            
            # Enhanced key findings
            st.markdown("### 🔑 Key Findings")
            for i, point in enumerate(analysis_result.key_points, 1):
                st.markdown(f"""
                <div class="key-finding">
                    <strong>{i}.</strong> {point}
                </div>
                """, unsafe_allow_html=True)
            
            # Enhanced page summaries
            if hasattr(analysis_result, 'page_summaries') and analysis_result.page_summaries:
                with st.expander("📄 Individual Page Analysis", expanded=False):
                    for i, page_summary in enumerate(analysis_result.page_summaries[:10], 1):
                        st.markdown(f"""
                        <div class="page-summary">
                            <h4>{i}. {page_summary.title}</h4>
                            <div class="method-badge">Relevance: {page_summary.relevance_score:.1f}</div>
                            <p><strong>🔗 Source:</strong> <a href="{page_summary.url}" target="_blank">{page_summary.url}</a></p>
                            <p><strong>📄 Summary:</strong> {page_summary.summary}</p>
                            <p><strong>🎯 Key Points:</strong> {', '.join(page_summary.key_points)}</p>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Enhanced citations
            st.markdown("### 📚 Sources & Citations")
            for i, citation in enumerate(analysis_result.citations[:10], 1):
                st.markdown(f"""
                <div class="citation-box">
                    <h4>{i}. {citation.get('source', 'Unknown Source')}</h4>
                    <p><strong>🔗 URL:</strong> <a href="{citation.get('url', '#')}" target="_blank">{citation.get('url', 'No URL')}</a></p>
                    <p><strong>📝 Relevance:</strong> {citation.get('relevance', 'Relevant to research topic')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
        except Exception as e:
            st.markdown(f"""
            <div style="background: rgba(244, 67, 54, 0.2); border: 1px solid rgba(244, 67, 54, 0.3); border-radius: 15px; padding: 1rem; color: #ef5350;">
                ❌ <strong>Research failed:</strong> {str(e)}<br>
                💡 Please check your internet connection and try again.
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced sidebar
    display_algorithm_comparison()
    
    # Session statistics in sidebar
    if st.sidebar.button("📊 Show Session Stats", use_container_width=True):
        st.sidebar.markdown("### 📈 Session Statistics")
        st.sidebar.info("Session tracking feature coming soon!")

if __name__ == "__main__":
    main()
