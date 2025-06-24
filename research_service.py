import logging
from typing import Dict, List, Tuple
import time
from graph_crawler import GraphWebCrawler, PageInfo
from llm_service import LLMService, AnalysisResult
from search_engine import SearchEngine

class ResearchService:
    def __init__(self, crawler_config: Dict = None, llm_config: Dict = None):
        # Initialize crawler with configuration
        crawler_config = crawler_config or {}
        self.crawler = GraphWebCrawler(
            delay=crawler_config.get('delay', 1.0),
            timeout=crawler_config.get('timeout', 10),
            max_pages=crawler_config.get('max_pages', 50)
        )
        
        # Initialize LLM service
        llm_config = llm_config or {}
        self.llm_service = LLMService(api_key=llm_config.get('api_key'))
        
        # Initialize search engine
        self.search_engine = SearchEngine()
        
        # Add conversation context
        self.conversation_history = []
        self.last_research_results = {}
        
        self.logger = logging.getLogger(__name__)
    
    def add_conversation_context(self, user_query: str, research_type: str, results: dict):
        """Add conversation context for follow-up questions"""
        self.conversation_history.append({
            'timestamp': time.time(),
            'query': user_query,
            'type': research_type,
            'results': results
        })
        
        # Keep only last 5 conversations
        if len(self.conversation_history) > 5:
            self.conversation_history.pop(0)
    
    def get_conversation_context(self) -> str:
        """Get recent conversation context for better responses"""
        if not self.conversation_history:
            return ""
        
        context = "Recent conversation context:\n"
        for conv in self.conversation_history[-3:]:  # Last 3 conversations
            context += f"- Asked about: {conv['query']} (Type: {conv['type']})\n"
        
        return context
    
    def search_research(self, query: str, max_depth: int = 2) -> Tuple[AnalysisResult, Dict[str, PageInfo], Dict]:
        """
        Perform search research using BFS algorithm
        Returns: (analysis_result, crawled_pages, statistics)
        """
        self.logger.info(f"Starting SEARCH research for query: {query}")
        start_time = time.time()
        
        # Get initial URLs from search engines and topic sources
        start_urls = self.search_engine.get_search_urls(query)
        self.logger.info(f"Generated {len(start_urls)} starting URLs from search results and topic sources")
        
        # Log the types of URLs we're getting
        search_result_urls = [url for url in start_urls if any(domain in url for domain in ['google.com/search', 'duckduckgo.com'])]
        actual_content_urls = [url for url in start_urls if not any(domain in url for domain in ['google.com/search', 'duckduckgo.com'])]
        
        self.logger.info(f"Search result URLs: {len(search_result_urls)}, Content URLs: {len(actual_content_urls)}")
        
        # If we have too many search URLs and not enough content URLs, this indicates an issue
        if len(search_result_urls) > len(actual_content_urls):
            self.logger.warning("More search URLs than content URLs detected. Search extraction may need improvement.")
        
        # Perform BFS crawling
        crawled_pages = self.crawler.search_crawl_bfs(start_urls, max_depth=max_depth)
        self.logger.info(f"BFS crawling completed. Found {len(crawled_pages)} pages")
        
        # Generate enhanced statistics
        statistics = self.crawler.get_crawl_statistics(crawled_pages)
        statistics['crawl_time'] = time.time() - start_time
        statistics['method'] = 'BFS (Breadth-First Search)'
        statistics['algorithm_type'] = 'search_bfs'
        statistics['data_structure'] = 'Queue (FIFO)'
        statistics['algorithm_details'] = 'Uses queue for level-by-level exploration, ensuring comprehensive coverage at each depth'
        statistics['exploration_pattern'] = 'Breadth-first: explores all nodes at depth d before exploring nodes at depth d+1'
        statistics['best_for'] = 'Quick overview, finding shortest paths, broad topic coverage'
        statistics['search_result_urls'] = len(search_result_urls)
        statistics['content_urls'] = len(actual_content_urls)
        
        # Add conversation context to analysis
        context = self.get_conversation_context()
        if context:
            query_with_context = f"{query}\n\nContext: {context}"
        else:
            query_with_context = query
        
        # Analyze content with LLM
        analysis_result = self.llm_service.analyze_crawled_content(
            query_with_context, crawled_pages, "BFS Search"
        )
        
        # Store results for follow-up
        results = {
            'analysis': analysis_result,
            'pages': crawled_pages,
            'statistics': statistics
        }
        self.add_conversation_context(query, "search", results)
        
        self.logger.info("Search research completed")
        return analysis_result, crawled_pages, statistics
    
    def deep_research(self, query: str, bfs_pages: int = 15, dfs_depth: int = 3) -> Tuple[AnalysisResult, Dict[str, PageInfo], Dict]:
        """
        Perform deep research using combined BFS + DFS algorithm
        Returns: (analysis_result, crawled_pages, statistics)
        """
        self.logger.info(f"Starting DEEP RESEARCH for query: {query}")
        start_time = time.time()
        
        # Get initial URLs from search engines and topic sources
        start_urls = self.search_engine.get_search_urls(query)
        self.logger.info(f"Generated {len(start_urls)} starting URLs from search results and topic sources")
        
        # Log URL composition for debugging
        search_result_urls = [url for url in start_urls if any(domain in url for domain in ['google.com/search', 'duckduckgo.com'])]
        actual_content_urls = [url for url in start_urls if not any(domain in url for domain in ['google.com/search', 'duckduckgo.com'])]
        
        self.logger.info(f"Search result URLs: {len(search_result_urls)}, Content URLs: {len(actual_content_urls)}")
        
        # Perform combined BFS + DFS crawling
        crawled_pages = self.crawler.deep_research_crawl_dfs_bfs(
            start_urls, bfs_pages=bfs_pages, dfs_depth=dfs_depth
        )
        self.logger.info(f"Deep research crawling completed. Found {len(crawled_pages)} pages")
        
        # Generate enhanced statistics
        statistics = self.crawler.get_crawl_statistics(crawled_pages)
        statistics['crawl_time'] = time.time() - start_time
        statistics['method'] = 'BFS + DFS (Hybrid Deep Research)'
        statistics['algorithm_type'] = 'hybrid_bfs_dfs'
        statistics['data_structure'] = 'Queue (Phase 1) + Stack (Phase 2)'
        statistics['algorithm_details'] = f'Phase 1: BFS with queue for {bfs_pages} seed pages, Phase 2: DFS with stack for depth {dfs_depth} exploration'
        statistics['exploration_pattern'] = 'Hybrid: broad initial coverage (BFS) followed by deep focused exploration (DFS)'
        statistics['best_for'] = 'Comprehensive research, finding detailed information, exploring specialized content'
        statistics['bfs_pages'] = bfs_pages
        statistics['dfs_depth'] = dfs_depth
        statistics['phase_1'] = 'BFS for seed collection'
        statistics['phase_2'] = 'DFS for deep exploration'
        statistics['search_result_urls'] = len(search_result_urls)
        statistics['content_urls'] = len(actual_content_urls)
        
        # Add conversation context to analysis
        context = self.get_conversation_context()
        if context:
            query_with_context = f"{query}\n\nContext: {context}"
        else:
            query_with_context = query
        
        # Analyze content with LLM
        analysis_result = self.llm_service.analyze_crawled_content(
            query_with_context, crawled_pages, "Deep Research (BFS + DFS)"
        )
        
        # Store results for follow-up
        results = {
            'analysis': analysis_result,
            'pages': crawled_pages,
            'statistics': statistics
        }
        self.add_conversation_context(query, "deep", results)
        
        self.logger.info("Deep research completed")
        return analysis_result, crawled_pages, statistics
    
    def get_research_comparison(self, query: str) -> Dict:
        """
        Compare both research methods for the same query
        """
        self.logger.info(f"Running comparison research for: {query}")
        
        # Run both methods
        search_result, search_pages, search_stats = self.search_research(query, max_depth=2)
        deep_result, deep_pages, deep_stats = self.deep_research(query, bfs_pages=10, dfs_depth=2)
        
        comparison = {
            'query': query,
            'search_method': {
                'analysis': search_result,
                'pages_count': len(search_pages),
                'statistics': search_stats
            },
            'deep_method': {
                'analysis': deep_result,
                'pages_count': len(deep_pages),
                'statistics': deep_stats
            },
            'comparison_metrics': {
                'pages_ratio': len(deep_pages) / len(search_pages) if search_pages else 1,
                'time_ratio': deep_stats.get('crawl_time', 0) / search_stats.get('crawl_time', 1),
                'depth_difference': deep_stats.get('max_depth', 0) - search_stats.get('max_depth', 0)
            }
        }
        
        # Store results for follow-up
        self.add_conversation_context(query, "comparison", comparison)
        
        return comparison
    
    def handle_follow_up_question(self, question: str) -> str:
        """Handle follow-up questions based on conversation history"""
        if not self.conversation_history:
            return "I don't have any previous research context. Please ask a new research question."
        
        last_research = self.conversation_history[-1]
        
        # Check if asking for more details
        if any(keyword in question.lower() for keyword in ["more", "details", "elaborate", "expand"]):
            if 'analysis' in last_research['results']:
                analysis = last_research['results']['analysis']
                return f"Here are additional details from the research on '{last_research['query']}':\n\n" + \
                       f"**Extended Analysis:**\n{analysis.summary}\n\n" + \
                       f"**Additional Sources:** {len(analysis.sources)} sources analyzed"
        
        # Check if asking for different research method
        if "deep" in question.lower() and last_research['type'] == "search":
            return f"I can perform a deep research on '{last_research['query']}'. This will use a hybrid BFS+DFS algorithm for more comprehensive results."
        
        return "I can help you with follow-up questions about your recent research. What specific aspect would you like to explore further?"
    
    def clear_conversation_history(self):
        """Clear conversation history for new session"""
        self.conversation_history = []
        self.last_research_results = {}
