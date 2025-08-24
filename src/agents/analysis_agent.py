"""
Enhanced Analysis Agent with real LLM-powered insights
"""
import sys
from pathlib import Path
from loguru import logger

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from .base_agent import BaseAgent
from tools.text_analysis_tool import TextAnalyzer
from utils.llm_config import llm_config

class AnalysisAgent(BaseAgent):
    """Advanced analysis agent with LLM-powered insights"""
    
    def __init__(self):
        super().__init__(
            name="Analysis Agent",
            description="Performs deep analysis of research papers using LLM to identify gaps, contradictions, and themes"
        )
        self.text_analyzer = TextAnalyzer(self.llm)
    
    def execute(self, state) -> dict:
        """Execute comprehensive analysis"""
        logger.info("🔬 Starting comprehensive paper analysis...")
        
        papers = state.get('papers_found', [])
        query = state.get('query', '')
        
        if not papers:
            logger.warning("No papers found for analysis")
            return self._add_empty_analysis(state)
        
        try:
            # 1. Extract key themes using LLM
            logger.info("1️⃣ Extracting key themes...")
            themes = self.text_analyzer.extract_key_themes(papers, query)
            
            # 2. Identify research gaps using LLM
            logger.info("2️⃣ Identifying research gaps...")
            gaps = self.text_analyzer.extract_research_gaps(papers, query)
            
            # 3. Find contradictions between papers
            logger.info("3️⃣ Analyzing contradictions...")
            contradictions = self.text_analyzer.identify_contradictions(papers)
            
            # 4. Generate analysis summary
            logger.info("4️⃣ Creating analysis summary...")
            analysis_summary = self._generate_analysis_summary(themes, gaps, contradictions, len(papers))
            
            # Update state
            state['key_themes'] = themes
            state['research_gaps'] = gaps
            state['contradictions'] = contradictions
            state['analysis_summary'] = analysis_summary
            state['analysis_completed'] = True
            
            logger.info(f"✅ Analysis completed: {len(themes)} themes, {len(gaps)} gaps, {len(contradictions)} contradictions")
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            state['errors'] = state.get('errors', []) + [f"Analysis error: {str(e)}"]
            return self._add_fallback_analysis(state, papers, query)
        
        return state
    
    def _generate_analysis_summary(self, themes: list, gaps: list, contradictions: list, paper_count: int) -> str:
        """Generate comprehensive analysis summary"""
        
        summary_parts = [
            f"📊 **Analysis Summary** (Based on {paper_count} papers)",
            "",
            "🎯 **Key Research Themes:**"
        ]
        
        for i, theme in enumerate(themes[:5], 1):
            summary_parts.append(f"  {i}. {theme}")
        
        summary_parts.extend([
            "",
            "🔍 **Research Gaps Identified:**"
        ])
        
        for i, gap in enumerate(gaps[:4], 1):
            desc = gap.get('description', 'No description') if isinstance(gap, dict) else str(gap)
            summary_parts.append(f"  {i}. {desc[:100]}...")
        
        if contradictions and any(contradictions):
            summary_parts.extend([
                "",
                "⚖️ **Contradictory Findings:**"
            ])
            for i, contradiction in enumerate(contradictions[:3], 1):
                if contradiction and len(contradiction) > 20:
                    summary_parts.append(f"  {i}. {contradiction[:120]}...")
        
        summary_parts.extend([
            "",
            "🎯 **Research Opportunities:**",
            f"  • Focus on {themes[0].lower() if themes else 'identified themes'} applications",
            f"  • Address the {len(gaps)} identified research gaps",
            f"  • Resolve contradictory findings in the literature",
            f"  • Build upon the {paper_count} papers analyzed"
        ])
        
        return "\n".join(summary_parts)
    
    def _add_empty_analysis(self, state) -> dict:
        """Add empty analysis structure when no papers found"""
        state['key_themes'] = []
        state['research_gaps'] = []
        state['contradictions'] = []
        state['analysis_summary'] = "No papers available for analysis"
        state['analysis_completed'] = False
        return state
    
    def _add_fallback_analysis(self, state, papers: list, query: str) -> dict:
        """Add fallback analysis when LLM analysis fails"""
        # Simple theme extraction from titles
        themes = []
        if papers:
            all_titles = " ".join([p.get('title', '') for p in papers])
            common_words = ['machine learning', 'deep learning', 'neural networks', 'artificial intelligence']
            for word in common_words:
                if word.lower() in all_titles.lower():
                    themes.append(word.title())
        
        if not themes:
            themes = ['Data Analysis', 'Research Methods']
        
        state['key_themes'] = themes
        state['research_gaps'] = [
            {'description': f'Limited recent work on {query}', 'impact': 'High priority area'},
            {'description': 'Need for more comprehensive evaluation', 'impact': 'Methodological improvement'}
        ]
        state['contradictions'] = ['Analysis limited due to processing constraints']
        state['analysis_summary'] = f"Fallback analysis completed for {len(papers)} papers. Key themes: {', '.join(themes[:3])}"
        state['analysis_completed'] = True
        
        return state
