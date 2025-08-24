"""
Literature search tools for academic papers
"""
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from loguru import logger
import time

class ArxivSearcher:
    """Search ArXiv for academic papers"""
    
    def __init__(self):
        self.base_url = "http://export.arxiv.org/api/query"
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search ArXiv for papers matching the query"""
        try:
            logger.info(f"🔍 Searching ArXiv for: {query}")
            
            # Prepare search parameters
            params = {
                'search_query': f'all:{query}',
                'start': 0,
                'max_results': max_results,
                'sortBy': 'relevance',
                'sortOrder': 'descending'
            }
            
            # Make the request
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.content)
            
            papers = []
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                paper = self._parse_entry(entry)
                papers.append(paper)
            
            logger.info(f"✅ Found {len(papers)} papers on ArXiv")
            return papers
            
        except Exception as e:
            logger.error(f"❌ ArXiv search failed: {e}")
            return []
    
    def _parse_entry(self, entry) -> Dict[str, Any]:
        """Parse an ArXiv entry into our paper format"""
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        title = entry.find('atom:title', ns).text.strip() if entry.find('atom:title', ns) is not None else "Unknown Title"
        
        # Get authors
        authors = []
        for author in entry.findall('atom:author', ns):
            name = author.find('atom:name', ns)
            if name is not None:
                authors.append(name.text)
        
        # Get abstract
        summary = entry.find('atom:summary', ns)
        abstract = summary.text.strip() if summary is not None else "No abstract available"
        
        # Get URL
        url = entry.find('atom:id', ns).text if entry.find('atom:id', ns) is not None else ""
        
        # Get published date
        published = entry.find('atom:published', ns)
        published_date = published.text[:10] if published is not None else "Unknown"
        
        return {
            'title': title,
            'authors': authors,
            'abstract': abstract,
            'url': url,
            'source': 'arxiv',
            'published_date': published_date,
            'keywords': []  # We'll extract these later
        }

# Global instance
arxiv_searcher = ArxivSearcher()
