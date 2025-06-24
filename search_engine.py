import requests
from bs4 import BeautifulSoup
import urllib.parse
from typing import List
import logging
import time
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SearchEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        # Use user agent from environment variable
        user_agent = os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        self.session.headers.update({
            'User-Agent': user_agent
        })
    
    def get_search_urls(self, query: str) -> List[str]:
        """Get actual URLs from search results and topic-specific sources"""
        all_urls = []
        
        # Try to get actual search results
        search_results = self._get_actual_search_results(query)
        all_urls.extend(search_results)
        
        # Add high-quality topic-specific URLs
        topic_urls = self._get_enhanced_topic_urls(query)
        all_urls.extend(topic_urls)
        
        # If no URLs found, add some reliable fallback URLs
        if not all_urls:
            fallback_urls = self._get_fallback_urls(query)
            all_urls.extend(fallback_urls)
            self.logger.warning(f"No search results found, using {len(fallback_urls)} fallback URLs")
        
        # Remove duplicates and limit results
        unique_urls = list(dict.fromkeys(all_urls))  # Preserves order
        
        self.logger.info(f"Generated {len(unique_urls)} quality URLs for query: {query}")
        return unique_urls[:10]  # Return top 10 quality URLs
    
    def _get_actual_search_results(self, query: str) -> List[str]:
        """Extract actual URLs from search engines"""
        urls = []
        
        # Try DuckDuckGo first (more reliable for scraping)
        duckduckgo_urls = self._get_duckduckgo_results(query)
        urls.extend(duckduckgo_urls)
        
        # Try Google search (basic extraction)
        google_urls = self._get_google_results(query)
        urls.extend(google_urls)
        
        return urls
    
    def _get_google_results(self, query: str) -> List[str]:
        """Get results from Google search"""
        try:
            encoded_query = urllib.parse.quote_plus(query)
            search_url = f"https://www.google.com/search?q={encoded_query}&num=10"
            
            response = self.session.get(search_url, timeout=10)
            if response.status_code != 200:
                self.logger.warning(f"Google search returned status {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            urls = []
            
            # Look for search result links
            for link in soup.find_all('a'):
                href = link.get('href', '')
                if href.startswith('/url?q='):
                    # Extract actual URL from Google's redirect
                    actual_url = href.split('/url?q=')[1].split('&')[0]
                    actual_url = urllib.parse.unquote(actual_url)
                    if actual_url.startswith('http') and not 'google.com' in actual_url:
                        urls.append(actual_url)
            
            self.logger.info(f"Extracted {len(urls)} URLs from Google search")
            return urls[:5]
            
        except Exception as e:
            self.logger.error(f"Error getting Google results: {e}")
            return []
    
    def _get_duckduckgo_results(self, query: str) -> List[str]:
        """Get results from DuckDuckGo"""
        try:
            encoded_query = urllib.parse.quote_plus(query)
            search_url = f"https://duckduckgo.com/html/?q={encoded_query}"
            
            response = self.session.get(search_url, timeout=10)
            if response.status_code != 200:
                self.logger.warning(f"DuckDuckGo search returned status {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            urls = []
            
            # DuckDuckGo result links
            for link in soup.find_all('a', {'class': 'result__a'}):
                href = link.get('href')
                if href and href.startswith('http') and not 'duckduckgo.com' in href:
                    urls.append(href)
            
            # Alternative selector for DuckDuckGo
            if not urls:
                for link in soup.find_all('a'):
                    href = link.get('href', '')
                    if href.startswith('http') and not any(blocked in href for blocked in ['duckduckgo.com', 'google.com', 'bing.com']):
                        urls.append(href)
            
            self.logger.info(f"Extracted {len(urls)} URLs from DuckDuckGo")
            return urls[:5]
            
        except Exception as e:
            self.logger.error(f"Error getting DuckDuckGo results: {e}")
            return []
    
    def _get_enhanced_topic_urls(self, query: str) -> List[str]:
        """Get enhanced topic-specific URLs based on query keywords"""
        urls = []
        query_lower = query.lower()
        
        # Software Engineering & Development
        if any(word in query_lower for word in ['software', 'development', 'engineering', 'programming', 'deployment', 'devops', 'ci/cd']):
            urls.extend([
                "https://martinfowler.com",
                "https://www.thoughtworks.com/insights",
                "https://github.blog/category/engineering/",
                "https://stackoverflow.blog",
                "https://www.infoq.com",
                "https://dzone.com",
                "https://medium.com/tag/software-engineering",
                "https://dev.to",
                "https://hackernoon.com",
                "https://www.freecodecamp.org/news"
            ])
        
        # AI & Machine Learning
        if any(word in query_lower for word in ['ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning', 'neural']):
            urls.extend([
                "https://ai.googleblog.com",
                "https://openai.com/blog",
                "https://blog.deepmind.com",
                "https://ai.facebook.com/blog",
                "https://distill.pub",
                "https://towardsdatascience.com",
                "https://machinelearningmastery.com",
                "https://www.analyticsvidhya.com/blog",
                "https://neptune.ai/blog",
                "https://papers.withcode.com"
            ])
        
        # DevOps & Deployment
        if any(word in query_lower for word in ['devops', 'deployment', 'docker', 'kubernetes', 'aws', 'cloud', 'infrastructure']):
            urls.extend([
                "https://aws.amazon.com/blogs/devops/",
                "https://kubernetes.io/blog/",
                "https://www.docker.com/blog/",
                "https://azure.microsoft.com/en-us/blog/",
                "https://cloud.google.com/blog/",
                "https://www.hashicorp.com/blog",
                "https://blog.digitalocean.com",
                "https://www.redhat.com/en/blog",
                "https://platform.sh/blog/",
                "https://circleci.com/blog/"
            ])
        
        # Technology News & Trends
        if any(word in query_lower for word in ['latest', 'trends', 'news', 'recent', 'current', 'practices']):
            urls.extend([
                "https://techcrunch.com",
                "https://arstechnica.com",
                "https://www.wired.com",
                "https://www.theverge.com",
                "https://hbr.org/topic/technology",
                "https://slashdot.org",
                "https://news.ycombinator.com",
                "https://www.zdnet.com"
            ])
        
        # Academic & Research
        if any(word in query_lower for word in ['research', 'study', 'academic', 'paper', 'analysis']):
            urls.extend([
                "https://arxiv.org",
                "https://www.acm.org/publications",
                "https://ieeexplore.ieee.org",
                "https://www.researchgate.net",
                "https://scholar.google.com"
            ])
        
        # Business & Industry
        if any(word in query_lower for word in ['business', 'industry', 'enterprise', 'company', 'organization']):
            urls.extend([
                "https://www.mckinsey.com/capabilities/mckinsey-digital",
                "https://www2.deloitte.com/us/en/insights/focus/tech-trends.html",
                "https://www.gartner.com/en/newsroom",
                "https://www.forrester.com/blogs/",
                "https://sloanreview.mit.edu"
            ])
        
        # Remove duplicates and return limited set
        unique_urls = list(dict.fromkeys(urls))
        return unique_urls[:8]
    
    def _get_fallback_urls(self, query: str) -> List[str]:
        """Get reliable fallback URLs when search engines fail"""
        # General knowledge and educational URLs that are likely to be accessible
        fallback_urls = [
            "https://en.wikipedia.org/wiki/Main_Page",
            "https://www.britannica.com",
            "https://www.investopedia.com",
            "https://www.howstuffworks.com",
            "https://www.sciencedirect.com",
            "https://www.nature.com",
            "https://www.nationalgeographic.com",
            "https://www.smithsonianmag.com"
        ]
        
        query_lower = query.lower()
        
        # Technology-specific fallbacks
        if any(word in query_lower for word in ['technology', 'software', 'programming', 'computer', 'web', 'internet']):
            fallback_urls.extend([
                "https://www.techrepublic.com",
                "https://www.computerworld.com",
                "https://www.infoworld.com",
                "https://www.cnet.com/tech/",
                "https://www.pcmag.com"
            ])
        
        # Science and research fallbacks
        if any(word in query_lower for word in ['research', 'science', 'study', 'analysis']):
            fallback_urls.extend([
                "https://www.sciencenews.org",
                "https://www.livescience.com",
                "https://www.popsci.com",
                "https://www.newscientist.com"
            ])
        
        # Business and finance fallbacks
        if any(word in query_lower for word in ['business', 'finance', 'market', 'economy']):
            fallback_urls.extend([
                "https://www.businessinsider.com",
                "https://www.cnbc.com",
                "https://www.bloomberg.com",
                "https://www.reuters.com"
            ])
        
        return fallback_urls[:6]  # Return up to 6 fallback URLs
