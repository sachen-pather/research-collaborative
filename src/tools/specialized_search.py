"""
Specialized search tools - Wikipedia API and Web Scraper
"""
import requests
import wikipedia
from typing import List, Dict, Any, Optional
from loguru import logger
from bs4 import BeautifulSoup
import re
import time

class WikipediaSearcher:
    """Wikipedia API integration for research context"""
    
    def __init__(self):
        wikipedia.set_lang("en")
        self.max_summary_length = 1000
    
    def search_topic(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search Wikipedia for topic information"""
        logger.info(f"📖 Searching Wikipedia for: {query}")
        
        try:
            # Search for pages
            search_results = wikipedia.search(query, results=max_results)
            
            if not search_results:
                logger.warning("No Wikipedia results found")
                return []
            
            articles = []
            for title in search_results[:max_results]:
                try:
                    # Get page summary
                    summary = wikipedia.summary(title, sentences=3)
                    page = wikipedia.page(title)
                    
                    articles.append({
                        'title': title,
                        'summary': summary[:self.max_summary_length],
                        'url': page.url,
                        'categories': page.categories[:5] if hasattr(page, 'categories') else [],
                        'source': 'wikipedia'
                    })
                    
                    # Rate limiting
                    time.sleep(0.1)
                    
                except (wikipedia.exceptions.DisambiguationError, wikipedia.exceptions.PageError) as e:
                    logger.warning(f"Wikipedia page error for {title}: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Error processing Wikipedia page {title}: {e}")
                    continue
            
            logger.info(f"✅ Found {len(articles)} Wikipedia articles")
            return articles
            
        except Exception as e:
            logger.error(f"❌ Wikipedia search failed: {e}")
            return []
    
    def get_related_concepts(self, query: str) -> List[str]:
        """Get related concepts from Wikipedia"""
        try:
            # Try to get the main page for the query
            page = wikipedia.page(query)
            
            # Extract related concepts from categories and links
            concepts = []
            
            # Add categories (cleaned)
            if hasattr(page, 'categories'):
                for cat in page.categories[:5]:
                    # Clean category name
                    clean_cat = cat.replace('Category:', '').replace('_', ' ')
                    if len(clean_cat.split()) <= 3:  # Only short, relevant categories
                        concepts.append(clean_cat)
            
            # Add some page links
            if hasattr(page, 'links'):
                relevant_links = [link for link in page.links[:10] if len(link.split()) <= 3]
                concepts.extend(relevant_links[:5])
            
            return concepts[:8]  # Limit to 8 concepts
            
        except Exception as e:
            logger.warning(f"Could not get related concepts for {query}: {e}")
            return []

class WebScraper:
    """Simple web scraper for research content"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.timeout = 10
    
    def scrape_research_content(self, url: str) -> Dict[str, Any]:
        """Scrape content from research-related URLs"""
        logger.info(f"🌐 Scraping content from: {url[:60]}...")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = ""
            if soup.title:
                title = soup.title.string.strip()
            
            # Extract main content
            content = self._extract_main_content(soup)
            
            # Extract metadata
            metadata = self._extract_metadata(soup)
            
            return {
                'success': True,
                'url': url,
                'title': title,
                'content': content[:2000],  # Limit content length
                'metadata': metadata,
                'word_count': len(content.split())
            }
            
        except Exception as e:
            logger.error(f"❌ Web scraping failed for {url}: {e}")
            return {
                'success': False,
                'url': url,
                'error': str(e),
                'content': '',
                'metadata': {}
            }
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main text content from HTML"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Try to find main content areas
        content_selectors = [
            'main', 'article', '.content', '#content', 
            '.post-content', '.entry-content', '.abstract'
        ]
        
        main_content = ""
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                main_content = elements[0].get_text()
                break
        
        # If no main content found, get all paragraph text
        if not main_content:
            paragraphs = soup.find_all('p')
            main_content = ' '.join([p.get_text() for p in paragraphs])
        
        # Clean the content
        main_content = re.sub(r'\s+', ' ', main_content).strip()
        
        return main_content
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract metadata from HTML"""
        metadata = {}
        
        # Meta tags
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            name = tag.get('name') or tag.get('property')
            content = tag.get('content')
            if name and content:
                metadata[name] = content
        
        # Extract specific useful metadata
        useful_metadata = {}
        for key in ['description', 'keywords', 'author', 'og:title', 'og:description']:
            if key in metadata:
                useful_metadata[key] = metadata[key][:200]  # Limit length
        
        return useful_metadata

# Global instances
wikipedia_searcher = WikipediaSearcher()
web_scraper = WebScraper()
