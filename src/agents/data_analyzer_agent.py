# File: src/agents/data_analyzer_agent.py

"""
Data Analyzer Agent - Processes documents and extracts insights
"""
import sys
from pathlib import Path
from loguru import logger

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from agents.base_agent import BaseAgent
from utils.llm_config import llm_config

class DataAnalyzerAgent(BaseAgent):
    """Agent specialized in processing and analyzing document data"""
    
    def __init__(self):
        super().__init__(
            name="Data Analyzer Agent",
            description="Processes PDFs, extracts data, and performs quantitative analysis of research content"
        )
        # Try to import your PDF processor
        try:
            from tools.pdf_processor import pdf_processor
            self.pdf_processor = pdf_processor
            self.has_pdf_processor = True
            logger.info("✅ PDF processor loaded successfully")
        except ImportError as e:
            logger.warning(f"PDF processor not available: {e}")
            self.pdf_processor = None
            self.has_pdf_processor = False
    
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
        """Process PDF content from papers using your existing PDF processor"""
        pdf_data = []
        
        if not self.has_pdf_processor:
            logger.warning("PDF processor not available, using mock data")
            # Return mock data as fallback
            for paper in papers[:2]:
                mock_pdf = {
                    'title': paper.get('title', ''),
                    'url': paper.get('url', ''),
                    'text': f"Mock PDF content for: {paper.get('title', '')[:100]}...",
                    'sections': {'abstract': 'Mock abstract', 'introduction': 'Mock introduction'},
                    'metadata': {'pages': 10},
                    'pages_processed': 5,
                    'success': True
                }
                pdf_data.append(mock_pdf)
            return pdf_data
        
        # Use your actual PDF processor
        pdf_urls = []
        for paper in papers[:3]:  # Limit to 3 PDFs to avoid timeouts
            url = paper.get('url', '')
            if url and ('.pdf' in url.lower() or 'arxiv.org' in url.lower()):
                pdf_urls.append((paper, url))
        
        logger.info(f"Found {len(pdf_urls)} potential PDF URLs to process")
        
        for paper, pdf_url in pdf_urls:
            try:
                title = paper.get('title', 'Unknown title')[:50]
                logger.info(f"Processing PDF: {title}...")
                
                # Use your existing PDF processor
                pdf_result = self.pdf_processor.extract_text_from_url(pdf_url)
                
                if pdf_result.get('success'):
                    text = pdf_result.get('text', '')
                    
                    # Limit text length to avoid token limits
                    if len(text) > 5000:
                        text = text[:5000] + "... [truncated]"
                    
                    # Extract sections if method exists
                    sections = {}
                    if hasattr(self.pdf_processor, 'extract_paper_sections'):
                        try:
                            sections = self.pdf_processor.extract_paper_sections(text)
                        except Exception as e:
                            logger.warning(f"Section extraction failed: {e}")
                            sections = {'full_text': text[:1000]}
                    else:
                        sections = {'full_text': text[:1000]}
                    
                    processed_pdf = {
                        'title': paper.get('title', ''),
                        'url': pdf_url,
                        'text': text,
                        'sections': sections,
                        'metadata': pdf_result.get('metadata', {}),
                        'pages_processed': pdf_result.get('pages_processed', 0),
                        'success': True
                    }
                    pdf_data.append(processed_pdf)
                    logger.info(f"✅ PDF processed: {len(text)} characters from {pdf_result.get('pages_processed', 0)} pages")
                else:
                    error_msg = pdf_result.get('error', 'Unknown error')
                    logger.warning(f"Failed to process PDF {title}: {error_msg}")
                    
            except Exception as e:
                logger.error(f"Error processing PDF for {paper.get('title', 'unknown')}: {e}")
                continue
        
        logger.info(f"PDF processing completed: {len(pdf_data)} PDFs processed successfully")
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
            'methodology_types': [],
            'text_analysis': {}
        }
        
        # Analyze papers
        abstract_lengths = []
        all_authors = set()
        
        for paper in papers:
            # Authors analysis
            authors = paper.get('authors', [])
            if isinstance(authors, list):
                all_authors.update(authors)
            elif isinstance(authors, str):
                all_authors.add(authors)
            
            # Abstract length analysis
            abstract = paper.get('abstract', '')
            if abstract:
                word_count = len(abstract.split())
                abstract_lengths.append(word_count)
            
            # Publication year extraction
            pub_date = paper.get('published_date', '')
            if pub_date and len(pub_date) >= 4:
                try:
                    year = int(pub_date[:4])
                    if 1990 <= year <= 2025:  # Reasonable year range
                        insights['publication_years'].append(year)
                except ValueError:
                    pass
        
        insights['total_authors'] = len(all_authors)
        insights['average_abstract_length'] = sum(abstract_lengths) / len(abstract_lengths) if abstract_lengths else 0
        
        # Analyze PDF sections
        total_text_length = 0
        for pdf in pdf_data:
            if pdf.get('success'):
                # Track sections found
                sections = pdf.get('sections', {})
                for section_name in sections.keys():
                    insights['sections_found'][section_name] = insights['sections_found'].get(section_name, 0) + 1
                
                # Track text length
                text = pdf.get('text', '')
                total_text_length += len(text)
        
        # Text analysis summary
        insights['text_analysis'] = {
            'total_characters': total_text_length,
            'average_chars_per_pdf': total_text_length / len(pdf_data) if pdf_data else 0,
            'most_common_sections': sorted(insights['sections_found'].items(), 
                                         key=lambda x: x[1], reverse=True)[:5]
        }
        
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
                'successful_pdf_extractions': len([pdf for pdf in pdf_data if pdf.get('success')]),
                'average_sections_per_paper': 0,
                'most_common_sections': []
            },
            'temporal_analysis': {},
            'research_patterns': []
        }
        
        # Source distribution analysis
        for paper in papers:
            source = paper.get('source', 'other').lower()
            if 'arxiv' in source:
                analysis['paper_distribution']['arxiv'] += 1
            elif 'pubmed' in source:
                analysis['paper_distribution']['pubmed'] += 1
            else:
                analysis['paper_distribution']['other'] += 1
        
        # Content statistics
        if pdf_data:
            section_counts = []
            all_sections = []
            
            for pdf in pdf_data:
                if pdf.get('success'):
                    sections = pdf.get('sections', {})
                    section_counts.append(len(sections))
                    all_sections.extend(sections.keys())
            
            analysis['content_statistics']['average_sections_per_paper'] = (
                sum(section_counts) / len(section_counts) if section_counts else 0
            )
            
            # Most common sections
            if all_sections:
                section_frequency = {}
                for section in all_sections:
                    section_frequency[section] = section_frequency.get(section, 0) + 1
                
                analysis['content_statistics']['most_common_sections'] = sorted(
                    section_frequency.items(), key=lambda x: x[1], reverse=True
                )[:5]
        
        # Temporal analysis
        pub_years = []
        for paper in papers:
            pub_date = paper.get('published_date', '')
            if pub_date and len(pub_date) >= 4:
                try:
                    year = int(pub_date[:4])
                    if 1990 <= year <= 2025:
                        pub_years.append(year)
                except ValueError:
                    pass
        
        if pub_years:
            analysis['temporal_analysis'] = {
                'earliest_year': min(pub_years),
                'latest_year': max(pub_years),
                'year_range': max(pub_years) - min(pub_years),
                'publications_per_year': len(pub_years) / max(1, max(pub_years) - min(pub_years))
            }
        
        # Research patterns
        if len(papers) >= 1:
            analysis['research_patterns'].append(f"Dataset contains {len(papers)} papers indicating active research area")
        
        if analysis['paper_distribution']['arxiv'] > len(papers) * 0.5:
            analysis['research_patterns'].append("Primarily computer science/AI research (ArXiv dominant)")
        elif analysis['paper_distribution']['pubmed'] > len(papers) * 0.5:
            analysis['research_patterns'].append("Primarily medical/biomedical research (PubMed dominant)")
        
        if len(pdf_data) > 0:
            success_rate = analysis['content_statistics']['successful_pdf_extractions'] / len(pdf_data)
            if success_rate >= 0.8:
                analysis['research_patterns'].append("High PDF accessibility - good for detailed analysis")
            elif success_rate >= 0.5:
                analysis['research_patterns'].append("Moderate PDF accessibility - some detailed analysis possible")
            else:
                analysis['research_patterns'].append("Limited PDF accessibility - analysis based mainly on abstracts")
        
        return analysis
    
    def _generate_data_summary(self, papers: list, pdf_data: list, insights: dict, analysis: dict) -> str:
        """Generate comprehensive data analysis summary"""
        
        summary_parts = [
            "# 📊 Data Analysis Report",
            "",
            "## 📈 Quantitative Overview",
            f"- **Papers Analyzed**: {insights['paper_count']}",
            f"- **PDFs Successfully Processed**: {insights['pdf_processed']} ({insights['pdf_processed']/max(1, insights['paper_count'])*100:.1f}%)",
            f"- **Total Authors**: {insights['total_authors']}",
            f"- **Average Abstract Length**: {insights['average_abstract_length']:.0f} words",
            f"- **Total Text Extracted**: {insights.get('text_analysis', {}).get('total_characters', 0):,} characters",
            ""
        ]
        
        # Source distribution
        dist = analysis['paper_distribution']
        summary_parts.extend([
            "## 📚 Source Distribution",
            f"- **ArXiv**: {dist['arxiv']} papers ({dist['arxiv']/max(1, insights['paper_count'])*100:.1f}%)",
            f"- **PubMed**: {dist['pubmed']} papers ({dist['pubmed']/max(1, insights['paper_count'])*100:.1f}%)", 
            f"- **Other Sources**: {dist['other']} papers ({dist['other']/max(1, insights['paper_count'])*100:.1f}%)",
            ""
        ])
        
        # Content analysis
        content_stats = analysis['content_statistics']
        summary_parts.extend([
            "## 📋 Content Analysis",
            f"- **Total Pages Processed**: {content_stats['total_processed_pages']}",
            f"- **Average Sections per Paper**: {content_stats['average_sections_per_paper']:.1f}",
        ])
        
        # Most common sections
        common_sections = content_stats.get('most_common_sections', [])
        if common_sections:
            summary_parts.append("- **Most Common Sections**:")
            for section, count in common_sections[:3]:
                summary_parts.append(f"  - {section.title()}: {count} papers")
        
        summary_parts.append("")
        
        # Temporal analysis
        temporal = analysis.get('temporal_analysis', {})
        if temporal:
            summary_parts.extend([
                "## 📅 Temporal Analysis",
                f"- **Publication Range**: {temporal.get('earliest_year', 'N/A')} - {temporal.get('latest_year', 'N/A')}",
                f"- **Time Span**: {temporal.get('year_range', 0)} years",
                f"- **Research Activity**: {temporal.get('publications_per_year', 0):.1f} papers per year",
                ""
            ])
        
        # Research patterns
        if analysis['research_patterns']:
            summary_parts.extend([
                "## 🔍 Research Patterns",
            ])
            for pattern in analysis['research_patterns']:
                summary_parts.append(f"- {pattern}")
            summary_parts.append("")
        
        # Data quality assessment
        pdf_success_rate = content_stats['successful_pdf_extractions'] / max(1, len(pdf_data)) if pdf_data else 0
        summary_parts.extend([
            "## 💡 Data Quality Assessment",
            f"- **PDF Processing Success Rate**: {pdf_success_rate*100:.1f}%",
            f"- **Data Completeness**: {'High' if pdf_success_rate >= 0.8 else 'Medium' if pdf_success_rate >= 0.5 else 'Limited'}",
            f"- **Analysis Confidence**: {'High' if insights['paper_count'] >= 5 and pdf_success_rate >= 0.7 else 'Medium'}",
            "",
            "## 📊 Recommendations",
            "- Quantitative foundation established for hypothesis generation",
            "- Statistical analysis ready for pattern identification",
        ])
        
        if pdf_success_rate < 0.5:
            summary_parts.append("- Consider expanding search to include more accessible sources")
        
        if insights['paper_count'] < 5:
            summary_parts.append("- Additional papers may strengthen analysis confidence")
        
        return "\n".join(summary_parts)
    
    def _add_empty_analysis(self, state) -> dict:
        """Add empty analysis when no papers available"""
        state['pdf_processed_count'] = 0
        state['quantitative_insights'] = {
            'paper_count': 0,
            'pdf_processed': 0,
            'message': 'No papers available for analysis'
        }
        state['statistical_analysis'] = {
            'message': 'No data available for statistical analysis'
        }
        state['data_analysis_summary'] = "## ⚠️ Data Analysis Unavailable\n\nNo papers were found for data analysis. Consider:\n- Broadening search terms\n- Checking alternative databases\n- Reviewing query specificity"
        state['data_analysis_completed'] = False
        return state
    
    def _add_fallback_analysis(self, state, papers: list, query: str) -> dict:
        """Add fallback analysis when processing fails"""
        fallback_insights = {
            'paper_count': len(papers),
            'pdf_processed': 0,
            'total_authors': len(set().union(*[p.get('authors', []) for p in papers if isinstance(p.get('authors', []), list)])),
            'average_abstract_length': sum(len(p.get('abstract', '').split()) for p in papers) / max(1, len(papers)),
            'analysis_method': 'fallback'
        }
        
        fallback_analysis = {
            'paper_distribution': {
                'arxiv': len([p for p in papers if 'arxiv' in p.get('source', '').lower()]),
                'other': len([p for p in papers if 'arxiv' not in p.get('source', '').lower()])
            },
            'content_statistics': {
                'total_processed_pages': 0,
                'analysis_method': 'abstract_based'
            },
            'research_patterns': [f"Basic analysis completed for {len(papers)} papers", "PDF processing unavailable - analysis based on metadata"]
        }
        
        state['pdf_processed_count'] = 0
        state['quantitative_insights'] = fallback_insights
        state['statistical_analysis'] = fallback_analysis
        state['data_analysis_summary'] = f"## 📊 Basic Data Analysis\n\nFallback analysis completed for {len(papers)} papers.\n\n**Key Metrics:**\n- Papers: {len(papers)}\n- Authors: {fallback_insights['total_authors']}\n- Avg Abstract Length: {fallback_insights['average_abstract_length']:.0f} words\n\n*Note: PDF processing was unavailable. Analysis based on paper metadata only.*"
        state['data_analysis_completed'] = True
        
        return state