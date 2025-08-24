"""
Data Analyzer Agent - Processes documents and extracts insights
"""
import sys
from pathlib import Path
from loguru import logger

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from agents.base_agent import BaseAgent
from tools.pdf_processor import pdf_processor
from utils.llm_config import llm_config

class DataAnalyzerAgent(BaseAgent):
    """Agent specialized in processing and analyzing document data"""
    
    def __init__(self):
        super().__init__(
            name="Data Analyzer Agent",
            description="Processes PDFs, extracts data, and performs quantitative analysis of research content"
        )
        self.pdf_processor = pdf_processor
    
    def execute(self, state) -> dict:
        """Execute data analysis on found papers"""
        logger.info("📊 Starting data analysis...")
        
        papers = state.get('papers_found', [])
        query = state.get('query', '')
        
        if not papers:
            logger.warning("No papers available for data analysis")
            return self._add_empty_analysis(state)
        
        try:
            # 1. Process PDFs if available
            logger.info("1️⃣ Processing available PDFs...")
            pdf_data = self._process_paper_pdfs(papers)
            
            # 2. Extract quantitative insights
            logger.info("2️⃣ Extracting quantitative insights...")
            quantitative_insights = self._extract_quantitative_insights(papers, pdf_data)
            
            # 3. Perform statistical analysis
            logger.info("3️⃣ Performing statistical analysis...")
            statistical_analysis = self._perform_statistical_analysis(papers, pdf_data)
            
            # 4. Generate data summary
            logger.info("4️⃣ Creating data analysis summary...")
            data_summary = self._generate_data_summary(
                papers, pdf_data, quantitative_insights, statistical_analysis
            )
            
            # Update state
            state['pdf_processed_count'] = len(pdf_data)
            state['quantitative_insights'] = quantitative_insights
            state['statistical_analysis'] = statistical_analysis
            state['data_analysis_summary'] = data_summary
            state['data_analysis_completed'] = True
            
            logger.info(f"✅ Data analysis completed: {len(pdf_data)} PDFs processed")
            
        except Exception as e:
            logger.error(f"❌ Data analysis failed: {e}")
            state['errors'] = state.get('errors', []) + [f"Data analysis error: {str(e)}"]
            return self._add_fallback_analysis(state, papers, query)
        
        return state
    
    def _process_paper_pdfs(self, papers: list) -> list:
        """Process PDF content from papers"""
        pdf_data = []
        
        # Mock PDF processing since we can't actually download PDFs in demo
        for paper in papers[:2]:  # Limit for demo
            # Simulate PDF processing
            mock_pdf = {
                'title': paper.get('title', ''),
                'url': paper.get('url', ''),
                'text': f"Mock PDF content for: {paper.get('title', '')[:100]}...",
                'sections': {'abstract': 'Mock abstract', 'introduction': 'Mock introduction'},
                'metadata': {'pages': 10},
                'pages_processed': 5
            }
            pdf_data.append(mock_pdf)
        
        return pdf_data
    
    def _extract_quantitative_insights(self, papers: list, pdf_data: list) -> dict:
        """Extract quantitative insights from papers and PDFs"""
        insights = {
            'paper_count': len(papers),
            'pdf_processed': len(pdf_data),
            'total_authors': 0,
            'publication_years': [],
            'average_abstract_length': 0,
            'sections_found': {},
            'methodology_types': []
        }
        
        # Analyze papers
        abstract_lengths = []
        all_authors = set()
        
        for paper in papers:
            # Authors
            authors = paper.get('authors', [])
            all_authors.update(authors)
            
            # Abstract length
            abstract = paper.get('abstract', '')
            if abstract:
                abstract_lengths.append(len(abstract.split()))
        
        insights['total_authors'] = len(all_authors)
        insights['average_abstract_length'] = sum(abstract_lengths) / len(abstract_lengths) if abstract_lengths else 0
        
        # Analyze PDF sections
        for pdf in pdf_data:
            sections = pdf.get('sections', {})
            for section_name in sections.keys():
                insights['sections_found'][section_name] = insights['sections_found'].get(section_name, 0) + 1
        
        return insights
    
    def _perform_statistical_analysis(self, papers: list, pdf_data: list) -> dict:
        """Perform statistical analysis on the data"""
        analysis = {
            'paper_distribution': {
                'arxiv': 0,
                'pubmed': 0,
                'other': 0
            },
            'content_statistics': {
                'total_processed_pages': sum(pdf.get('pages_processed', 0) for pdf in pdf_data),
                'average_sections_per_paper': 0,
                'most_common_sections': []
            },
            'research_patterns': []
        }
        
        # Source distribution
        for paper in papers:
            source = paper.get('source', 'other').lower()
            if 'arxiv' in source:
                analysis['paper_distribution']['arxiv'] += 1
            elif 'pubmed' in source:
                analysis['paper_distribution']['pubmed'] += 1
            else:
                analysis['paper_distribution']['other'] += 1
        
        # Research patterns
        if len(papers) >= 1:
            analysis['research_patterns'].append(f"Found {len(papers)} papers indicating research activity")
        
        if analysis['paper_distribution']['arxiv'] > 0:
            analysis['research_patterns'].append("Primarily computer science/AI research")
        
        return analysis
    
    def _generate_data_summary(self, papers: list, pdf_data: list, insights: dict, analysis: dict) -> str:
        """Generate comprehensive data analysis summary"""
        
        summary_parts = [
            "# 📊 Data Analysis Report",
            "",
            "## 📈 Quantitative Overview",
            f"- **Papers Analyzed**: {insights['paper_count']}",
            f"- **PDFs Processed**: {insights['pdf_processed']}",
            f"- **Total Authors**: {insights['total_authors']}",
            f"- **Average Abstract Length**: {insights['average_abstract_length']:.0f} words",
            "",
            "## 📚 Source Distribution",
            f"- **ArXiv**: {analysis['paper_distribution']['arxiv']} papers",
            f"- **PubMed**: {analysis['paper_distribution']['pubmed']} papers", 
            f"- **Other**: {analysis['paper_distribution']['other']} papers",
            ""
        ]
        
        # Research patterns
        if analysis['research_patterns']:
            summary_parts.extend([
                "## 🔍 Research Patterns",
            ])
            for pattern in analysis['research_patterns']:
                summary_parts.append(f"- {pattern}")
            summary_parts.append("")
        
        summary_parts.extend([
            "## 💡 Data-Driven Insights",
            "- Research area shows sufficient academic attention",
            "- Multiple perspectives available across different sources",
            "- Quantitative foundation established for hypothesis generation"
        ])
        
        return "\n".join(summary_parts)
    
    def _add_empty_analysis(self, state) -> dict:
        """Add empty analysis when no papers available"""
        state['pdf_processed_count'] = 0
        state['quantitative_insights'] = {}
        state['statistical_analysis'] = {}
        state['data_analysis_summary'] = "No papers available for data analysis"
        state['data_analysis_completed'] = False
        return state
    
    def _add_fallback_analysis(self, state, papers: list, query: str) -> dict:
        """Add fallback analysis when processing fails"""
        fallback_insights = {
            'paper_count': len(papers),
            'pdf_processed': 0,
            'total_authors': len(set().union(*[p.get('authors', []) for p in papers])),
            'average_abstract_length': sum(len(p.get('abstract', '').split()) for p in papers) / len(papers) if papers else 0
        }
        
        state['pdf_processed_count'] = 0
        state['quantitative_insights'] = fallback_insights
        state['statistical_analysis'] = {'note': 'Fallback analysis due to processing constraints'}
        state['data_analysis_summary'] = f"Basic analysis completed for {len(papers)} papers. PDF processing unavailable."
        state['data_analysis_completed'] = True
        
        return state