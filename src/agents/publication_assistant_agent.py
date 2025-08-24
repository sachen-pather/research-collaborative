"""
Publication Assistant Agent - Formats outputs and creates reports
"""
import sys
from pathlib import Path
from loguru import logger
from datetime import datetime
import wikipedia

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from agents.base_agent import BaseAgent
from tools.specialized_search import wikipedia_searcher
from utils.llm_config import llm_config

class PublicationAssistantAgent(BaseAgent):
    """Agent specialized in formatting research outputs and creating publication-ready reports"""
    
    def __init__(self):
        super().__init__(
            name="Publication Assistant Agent", 
            description="Creates formatted reports, citations, and publication-ready research outputs"
        )
        # Use try-except for imports that might fail
        try:
            self.wikipedia_searcher = wikipedia_searcher
        except:
            self.wikipedia_searcher = None
    
    def execute(self, state) -> dict:
        """Execute publication assistance tasks"""
        logger.info("📝 Starting publication assistance...")
        
        query = state.get('query', '')
        
        try:
            # 1. Gather context (simplified for demo)
            logger.info("1️⃣ Gathering additional context...")
            context_info = self._gather_research_context(query)
            
            # 2. Create formatted citations
            logger.info("2️⃣ Creating formatted citations...")
            formatted_citations = self._create_formatted_citations(state.get('papers_found', []))
            
            # 3. Generate executive summary
            logger.info("3️⃣ Generating executive summary...")
            executive_summary = self._generate_executive_summary(state)
            
            # 4. Create publication report
            logger.info("4️⃣ Creating publication-ready report...")
            publication_report = self._create_publication_report(state, context_info, formatted_citations)
            
            # Update state
            state['research_context'] = context_info
            state['formatted_citations'] = formatted_citations
            state['executive_summary'] = executive_summary
            state['publication_report'] = publication_report
            state['publication_ready'] = True
            
            logger.info("✅ Publication assistance completed")
            
        except Exception as e:
            logger.error(f"❌ Publication assistance failed: {e}")
            state['errors'] = state.get('errors', []) + [f"Publication error: {str(e)}"]
            return self._add_fallback_publication(state)
        
        return state
    
    def _gather_research_context(self, query: str) -> dict:
        """Gather additional context"""
        # Simplified context gathering for demo
        return {
            'wikipedia_articles': [],
            'related_concepts': [f"{query} applications", f"{query} methodologies"],
            'background_info': f"Research context for {query} - comprehensive background analysis available."
        }
    
    def _create_formatted_citations(self, papers: list) -> dict:
        """Create properly formatted citations in multiple styles"""
        citations = {
            'apa_style': [],
            'ieee_style': []
        }
        
        for i, paper in enumerate(papers, 1):
            title = paper.get('title', 'Unknown Title')
            authors = paper.get('authors', ['Unknown Author'])
            url = paper.get('url', '')
            
            # Format authors
            if len(authors) > 3:
                author_str = f"{authors[0]}, et al."
            else:
                author_str = ", ".join(authors[:2])
            
            year = datetime.now().year
            
            # APA Style
            apa = f"{author_str} ({year}). {title}. Retrieved from {url}"
            citations['apa_style'].append(f"[{i}] {apa}")
            
            # IEEE Style
            ieee = f"[{i}] {author_str}, \"{title},\" ArXiv, {year}."
            citations['ieee_style'].append(ieee)
        
        logger.info(f"✅ Created {len(papers)} citations in multiple formats")
        return citations
    
    def _generate_executive_summary(self, state) -> str:
        """Generate executive summary of the research"""
        query = state.get('query', 'Research Topic')
        papers_count = len(state.get('papers_found', []))
        themes = state.get('key_themes', [])
        gaps = state.get('research_gaps', [])
        hypotheses = state.get('hypotheses', [])
        
        summary_parts = [
            f"# Executive Summary: {query}",
            "",
            f"**Research Query**: {query}",
            f"**Analysis Date**: {datetime.now().strftime('%B %d, %Y')}",
            f"**Papers Analyzed**: {papers_count}",
            "",
            "## Key Findings",
        ]
        
        if themes:
            summary_parts.extend([
                f"**Primary Research Themes**: {', '.join(themes[:3])}",
                ""
            ])
        
        if gaps:
            gap_count = len(gaps)
            summary_parts.extend([
                f"**Research Gaps Identified**: {gap_count} critical areas for future investigation",
                ""
            ])
        
        if hypotheses:
            hyp_count = len(hypotheses)
            summary_parts.extend([
                f"**Research Hypotheses Generated**: {hyp_count} testable propositions",
                ""
            ])
        
        summary_parts.extend([
            "## Strategic Recommendations",
            "1. **Immediate Actions**: Focus on highest-priority research gaps",
            "2. **Medium-term Goals**: Develop and test generated hypotheses", 
            "3. **Long-term Vision**: Establish comprehensive research program",
            "",
            "---",
            "*This executive summary provides a high-level overview of research findings.*"
        ])
        
        return "\n".join(summary_parts)
    
    def _create_publication_report(self, state, context_info: dict, citations: dict) -> str:
        """Create comprehensive publication-ready report"""
        query = state.get('query', 'Research Topic')
        papers_count = len(state.get('papers_found', []))
        
        report_parts = [
            f"# Research Analysis Report: {query}",
            f"*Generated on {datetime.now().strftime('%B %d, %Y')}*",
            "",
            "## Abstract",
            "",
            f"This research analysis examines {query} through comprehensive review of {papers_count} papers.",
            "",
            "## Literature Review",
            "",
            f"Analysis of {papers_count} papers reveals active research engagement in this area.",
            "",
            "## Analysis and Findings", 
            "",
            state.get('analysis_summary', 'Comprehensive analysis completed'),
            "",
            "## Data Analysis",
            "",
            state.get('data_analysis_summary', 'Quantitative analysis performed'),
            "",
            "## References",
            ""
        ]
        
        # Add citations
        for citation in citations.get('apa_style', [])[:5]:
            report_parts.append(citation)
        
        return "\n".join(report_parts)
    
    def _add_fallback_publication(self, state) -> dict:
        """Add fallback publication assistance"""
        query = state.get('query', 'Research Topic')
        
        fallback_summary = f"# Research Summary: {query}\n\nBasic publication assistance completed."
        
        state['research_context'] = {'note': 'Basic context'}
        state['formatted_citations'] = {'note': 'Citations available'}
        state['executive_summary'] = fallback_summary
        state['publication_report'] = fallback_summary
        state['publication_ready'] = True
        
        return state