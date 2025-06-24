import openai
import os
from typing import List, Dict, Optional
import logging
from dataclasses import dataclass
from graph_crawler import PageInfo
import json

@dataclass
class PageSummary:
    url: str
    title: str
    summary: str
    key_points: List[str]
    relevance_score: float

@dataclass
class AnalysisResult:
    summary: str
    key_points: List[str]
    citations: List[Dict[str, str]]
    confidence_score: float
    relevant_urls: List[str]
    page_summaries: List[PageSummary]

class LLMService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            self.client = None
        self.logger = logging.getLogger(__name__)
    
    def _summarize_single_page(self, page: PageInfo, query: str) -> PageSummary:
        """AI-powered summarization of a single page with relevance to the query"""
        if not self.client:
            self.logger.warning("No OpenAI client available, using fallback summarization")
            return self._fallback_page_summary(page, query)
        
        try:
            prompt = f"""
Analyze this web page content for the research query: "{query}"

Page URL: {page.url}
Page Title: {page.title}
Content: {page.content[:1500]}

Use AI to provide a JSON response with:
1. A concise AI-generated summary (2-3 sentences) focusing on relevance to the query
2. 2-3 key points extracted by AI analysis
3. AI-calculated relevance score (0.0-1.0) indicating how relevant this page is to the query

Format:
{{
    "summary": "AI-generated brief summary focusing on query relevance...",
    "key_points": ["AI-extracted key point 1", "AI-extracted key point 2"],
    "relevance_score": 0.8
}}
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an AI research analyst. Use AI to provide concise, relevant summaries in valid JSON format. Focus on extracting the most important information using AI analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.2
            )
            
            content = response.choices[0].message.content
            analysis_data = json.loads(content)
            
            self.logger.info(f"✨ AI successfully summarized page: {page.url[:50]}...")
            
            return PageSummary(
                url=page.url,
                title=page.title,
                summary=analysis_data.get('summary', ''),
                key_points=analysis_data.get('key_points', []),
                relevance_score=analysis_data.get('relevance_score', 0.5)
            )
            
        except Exception as e:
            self.logger.error(f"❌ AI summarization failed for {page.url}: {e}")
            return self._fallback_page_summary(page, query)
    
    def _fallback_page_summary(self, page: PageInfo, query: str) -> PageSummary:
        """Fallback page summary when AI is not available"""
        # Simple keyword-based relevance scoring
        query_words = set(query.lower().split())
        content_words = set(page.content.lower().split())
        relevance = len(query_words.intersection(content_words)) / len(query_words) if query_words else 0.3
        
        return PageSummary(
            url=page.url,
            title=page.title,
            summary=page.content[:200] + "... [Non-AI summary]",
            key_points=[f"Content extracted from {page.title}"],
            relevance_score=min(relevance, 1.0)
        )
    
    def _create_comprehensive_analysis_prompt(self, query: str, page_summaries: List[PageSummary], crawl_type: str) -> str:
        """Create AI prompt using individual AI-generated page summaries"""
        
        base_prompt = f"""
You are an expert AI research analyst. I've used {crawl_type} to research: "{query}"

Each page below was ALREADY ANALYZED BY AI to extract summaries and key points:

AI-ANALYZED PAGES:
"""
        
        for i, summary in enumerate(page_summaries[:15], 1):  # Limit for token management
            base_prompt += f"""
--- AI-ANALYZED PAGE {i} (AI Relevance Score: {summary.relevance_score:.1f}) ---
URL: {summary.url}
Title: {summary.title}
AI Summary: {summary.summary}
AI-Extracted Key Points: {'; '.join(summary.key_points)}

"""
        
        analysis_instructions = f"""
COMPREHENSIVE AI ANALYSIS REQUIREMENTS:
Using the AI-generated summaries above, provide a comprehensive research analysis for: "{query}"

1. Use AI to synthesize information from all AI-analyzed pages into a coherent summary
2. Extract 5-7 key findings using AI analysis that directly address the query
3. Create proper citations referencing specific AI-analyzed pages
4. Use AI to rate overall confidence in the analysis
5. Identify most valuable sources using AI assessment

OUTPUT FORMAT (JSON):
{{
    "summary": "AI-synthesized comprehensive analysis addressing the query based on AI-analyzed sources...",
    "key_points": [
        "AI-identified key finding 1 with evidence from sources...",
        "AI-identified key finding 2 with evidence from sources...",
        ...
    ],
    "citations": [
        {{"source": "Page Title", "url": "URL", "relevance": "AI assessment of specific contribution"}},
        ...
    ],
    "confidence_score": 0.85,
    "relevant_urls": ["AI-selected most_valuable_url1", "AI-selected most_valuable_url2", ...],
    "methodology_note": "AI-powered analysis based on {crawl_type} with {len(page_summaries)} AI-analyzed sources"
}}
"""
        
        return base_prompt + analysis_instructions
    
    def analyze_crawled_content(self, query: str, pages: Dict[str, PageInfo], crawl_type: str) -> AnalysisResult:
        """AI-powered analysis of crawled content with AI page-by-page summarization"""
        
        # First, use AI to summarize each page individually
        self.logger.info(f"🤖 Using AI to analyze and summarize {len(pages)} pages individually...")
        page_summaries = []
        
        for url, page in pages.items():
            ai_summary = self._summarize_single_page(page, query)
            page_summaries.append(ai_summary)
        
        # Sort by AI-calculated relevance score
        page_summaries.sort(key=lambda x: x.relevance_score, reverse=True)
        
        if not self.client:
            self.logger.warning("No AI client available for comprehensive analysis, using enhanced fallback")
            return self._fallback_analysis_with_summaries(query, page_summaries, crawl_type)
        
        try:
            # Create comprehensive AI analysis from AI-generated page summaries
            prompt = self._create_comprehensive_analysis_prompt(query, page_summaries, crawl_type)
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert AI research analyst. Use AI to provide thorough, well-cited analysis in valid JSON format. Focus on synthesizing AI-analyzed content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            analysis_data = json.loads(content)
            
            self.logger.info("🤖 AI comprehensive analysis completed successfully")
            
            return AnalysisResult(
                summary=analysis_data.get('summary', ''),
                key_points=analysis_data.get('key_points', []),
                citations=analysis_data.get('citations', []),
                confidence_score=analysis_data.get('confidence_score', 0.5),
                relevant_urls=analysis_data.get('relevant_urls', []),
                page_summaries=page_summaries
            )
            
        except Exception as e:
            self.logger.error(f"❌ AI comprehensive analysis failed: {e}")
            return self._fallback_analysis_with_summaries(query, page_summaries, crawl_type)
    
    def _fallback_analysis_with_summaries(self, query: str, page_summaries: List[PageSummary], crawl_type: str) -> AnalysisResult:
        """Enhanced fallback analysis when AI is not available"""
        
        # Create summary from AI-generated page summaries (if available) or fallback summaries
        high_relevance_pages = [p for p in page_summaries if p.relevance_score > 0.6]
        
        ai_status = "AI-assisted" if any("Non-AI" not in p.summary for p in page_summaries) else "Non-AI"
        
        summary = f"""
{ai_status} Research Analysis for: "{query}"
Method: {crawl_type}

Found {len(page_summaries)} relevant sources with {len(high_relevance_pages)} highly relevant pages.
The research covers multiple perspectives and authoritative sources on the topic.
{f"Note: Some pages were analyzed using AI assistance." if ai_status == "AI-assisted" else "Note: Analysis performed without AI assistance."}
"""
        
        # Extract key points from high-relevance summaries
        key_points = []
        for i, page_summary in enumerate(high_relevance_pages[:7], 1):
            key_points.append(f"From {page_summary.title}: {page_summary.summary}")
        
        # Create citations from page summaries
        citations = []
        for page_summary in page_summaries[:10]:
            citations.append({
                "source": page_summary.title,
                "url": page_summary.url,
                "relevance": f"Relevance score: {page_summary.relevance_score:.1f} - {page_summary.summary[:100]}..."
            })
        
        return AnalysisResult(
            summary=summary.strip(),
            key_points=key_points,
            citations=citations,
            confidence_score=0.7,
            relevant_urls=[p.url for p in high_relevance_pages[:5]],
            page_summaries=page_summaries
        )
    
    def generate_search_urls(self, query: str) -> List[str]:
        """Generate search URLs for a given query"""
        encoded_query = query.replace(' ', '+')
        
        search_urls = [
            f"https://www.google.com/search?q={encoded_query}",
            f"https://duckduckgo.com/?q={encoded_query}",
            f"https://www.bing.com/search?q={encoded_query}"
        ]
        
        # Add some topic-specific URLs based on keywords
        if any(word in query.lower() for word in ['science', 'research', 'study']):
            search_urls.extend([
                f"https://scholar.google.com/scholar?q={encoded_query}",
                f"https://www.ncbi.nlm.nih.gov/pubmed/?term={encoded_query}"
            ])
        
        if any(word in query.lower() for word in ['technology', 'programming', 'software']):
            search_urls.extend([
                f"https://stackoverflow.com/search?q={encoded_query}",
                f"https://github.com/search?q={encoded_query}"
            ])
        
        if any(word in query.lower() for word in ['news', 'current', 'recent']):
            search_urls.extend([
                f"https://news.google.com/search?q={encoded_query}",
                f"https://www.reuters.com/search/news?blob={encoded_query}"
            ])
        
        return search_urls[:3]  # Return top 3 to avoid overwhelming
