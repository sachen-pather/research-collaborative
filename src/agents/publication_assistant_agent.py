"""
Fixed Results Formatter Integration - Properly exports results
"""

# 1. First, update your PublicationAssistantAgent to use the enhanced formatter

# In src/agents/publication_assistant_agent.py
import sys
from pathlib import Path
from loguru import logger
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from agents.base_agent import BaseAgent
from tools.specialized_search import wikipedia_searcher
from utils.llm_config import llm_config
from tools.EnhancedResultsFormatter import EnhancedResultsFormatter

class PublicationAssistantAgent(BaseAgent):
    """Enhanced Publication Assistant that generates comprehensive outputs"""
    
    def __init__(self):
        super().__init__(
            name="Publication Assistant Agent", 
            description="Creates comprehensive research outputs with enhanced formatting and analysis"
        )
        # Initialize the enhanced results formatter
        self.results_formatter = EnhancedResultsFormatter()
        
        try:
            self.wikipedia_searcher = wikipedia_searcher
        except:
            self.wikipedia_searcher = None
    
    def execute(self, state) -> dict:
        """Execute enhanced publication assistance with comprehensive outputs"""
        logger.info("📝 Starting enhanced publication assistance...")
        
        query = state.get('query', 'Research Topic')
        
        try:
            # 1. Generate enhanced executive summary
            logger.info("1️⃣ Generating executive intelligence report...")
            executive_summary = self.results_formatter.generate_executive_summary(state)
            
            # 2. Create detailed research plan
            logger.info("2️⃣ Creating detailed research implementation plan...")
            detailed_research_plan = self.results_formatter.generate_detailed_research_plan(state)
            
            # 3. Generate hypothesis testing framework
            logger.info("3️⃣ Developing hypothesis testing framework...")
            hypothesis_framework = self.results_formatter.generate_hypothesis_testing_framework(state)
            
            # 4. Create formatted citations (keeping existing functionality)
            logger.info("4️⃣ Formatting citations...")
            formatted_citations = self._create_formatted_citations(state.get('papers_found', []))
            
            # 5. Generate strategic recommendations
            logger.info("5️⃣ Generating strategic recommendations...")
            strategic_recommendations = self._generate_strategic_recommendations(state)
            
            # 6. Create implementation timeline
            logger.info("6️⃣ Creating implementation timeline...")
            implementation_timeline = self._create_implementation_timeline(state)
            
            # Update state with all enhanced outputs
            state.update({
                'executive_summary': executive_summary,
                'detailed_research_plan': detailed_research_plan,
                'hypothesis_testing_framework': hypothesis_framework,
                'formatted_citations': formatted_citations,
                'strategic_recommendations': strategic_recommendations,
                'implementation_timeline': implementation_timeline,
                'publication_ready': True,
                'enhanced_outputs_generated': True
            })
            
            # Generate comprehensive final report
            final_report = self._create_comprehensive_report(state)
            state['comprehensive_research_report'] = final_report
            
            logger.info("✅ Enhanced publication assistance completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Enhanced publication assistance failed: {e}")
            state['errors'] = state.get('errors', []) + [f"Publication error: {str(e)}"]
            # Provide fallback outputs
            state = self._add_fallback_publication(state)
        
        return state
    
    def _create_formatted_citations(self, papers: list) -> dict:
        """Create properly formatted citations in multiple styles"""
        citations = {
            'apa_style': [],
            'ieee_style': [],
            'chicago_style': []
        }
        
        for i, paper in enumerate(papers, 1):
            title = paper.get('title', 'Unknown Title')
            authors = paper.get('authors', ['Unknown Author'])
            url = paper.get('url', '')
            pub_date = paper.get('published_date', datetime.now().year)
            
            # Format authors
            if len(authors) > 3:
                author_str = f"{authors[0]}, et al."
            else:
                author_str = ", ".join(authors[:3])
            
            year = pub_date[:4] if isinstance(pub_date, str) and len(pub_date) >= 4 else datetime.now().year
            
            # APA Style
            apa = f"{author_str} ({year}). {title}. Retrieved from {url}"
            citations['apa_style'].append(f"[{i}] {apa}")
            
            # IEEE Style
            ieee = f"[{i}] {author_str}, \"{title},\" ArXiv, {year}."
            citations['ieee_style'].append(ieee)
            
            # Chicago Style
            chicago = f"{author_str}. \"{title}.\" Accessed {datetime.now().strftime('%B %d, %Y')}. {url}."
            citations['chicago_style'].append(f"[{i}] {chicago}")
        
        logger.info(f"✅ Created {len(papers)} citations in multiple formats")
        return citations
    
    def _generate_strategic_recommendations(self, state: dict) -> list:
        """Generate strategic recommendations based on analysis"""
        recommendations = []
        
        papers_count = len(state.get('papers_found', []))
        gaps = state.get('research_gaps', [])
        hypotheses = state.get('hypotheses', [])
        themes = state.get('key_themes', [])
        methodology = state.get('research_methodology', {})
        
        # Literature-based recommendations
        if papers_count < 10:
            recommendations.append({
                'priority': 'High',
                'category': 'Literature Foundation',
                'recommendation': 'Expand literature search across multiple databases and include grey literature',
                'rationale': f'Current base of {papers_count} papers may limit generalizability',
                'timeline': '2-4 weeks',
                'resources': 'Research librarian, database access'
            })
        
        # Gap-based recommendations
        if gaps:
            high_impact_gaps = [g for g in gaps if isinstance(g, dict) and g.get('impact') == 'High']
            if high_impact_gaps:
                recommendations.append({
                    'priority': 'High',
                    'category': 'Research Opportunities',
                    'recommendation': f'Prioritize investigation of {len(high_impact_gaps)} high-impact research gaps',
                    'rationale': 'High-impact gaps offer significant contribution potential',
                    'timeline': '6-12 months',
                    'resources': 'Research team, funding for pilot studies'
                })
        
        # Hypothesis-based recommendations
        if hypotheses and len(hypotheses) >= 2:
            recommendations.append({
                'priority': 'Medium',
                'category': 'Experimental Design',
                'recommendation': 'Begin pilot testing of generated hypotheses',
                'rationale': f'{len(hypotheses)} testable hypotheses identified for validation',
                'timeline': '3-6 months',
                'resources': 'Pilot study budget, participant recruitment'
            })
        
        # Methodology-based recommendations
        if methodology:
            recommendations.append({
                'priority': 'High',
                'category': 'Implementation',
                'recommendation': 'Secure funding and begin research implementation',
                'rationale': 'Comprehensive methodology framework is ready for execution',
                'timeline': '1-3 months for funding applications',
                'resources': 'Grant writing support, institutional backing'
            })
        
        # Collaboration recommendations
        if themes:
            recommendations.append({
                'priority': 'Medium',
                'category': 'Collaboration',
                'recommendation': 'Establish partnerships with key researchers in identified theme areas',
                'rationale': f'{len(themes)} major themes suggest active research community',
                'timeline': '2-6 months',
                'resources': 'Conference attendance, networking events'
            })
        
        return recommendations
    
    def _create_implementation_timeline(self, state: dict) -> dict:
        """Create detailed implementation timeline"""
        methodology = state.get('research_methodology', {})
        hypotheses = state.get('hypotheses', [])
        gaps = state.get('research_gaps', [])
        
        # Use methodology timeline if available, otherwise create basic timeline
        if methodology and methodology.get('detailed_timeline'):
            return methodology['detailed_timeline']
        
        # Create basic timeline
        timeline = {
            'total_duration_months': 18,
            'phases': [
                {
                    'phase': 'Phase 1: Planning & Preparation',
                    'duration_weeks': 8,
                    'start_date': datetime.now().strftime('%Y-%m-%d'),
                    'activities': [
                        'Expand literature review',
                        'Finalize research methodology',
                        'Secure ethical approvals',
                        'Assemble research team'
                    ],
                    'deliverables': [
                        'Complete literature review',
                        'IRB approval obtained',
                        'Research protocol finalized',
                        'Team contracts signed'
                    ],
                    'milestones': ['Literature review complete', 'Ethics approval received']
                },
                {
                    'phase': 'Phase 2: Pilot & Refinement',
                    'duration_weeks': 12,
                    'activities': [
                        'Conduct pilot studies',
                        'Test data collection instruments',
                        'Refine methodology based on pilot results',
                        'Train research staff'
                    ],
                    'deliverables': [
                        'Pilot study results',
                        'Validated instruments',
                        'Refined protocols',
                        'Trained research team'
                    ],
                    'milestones': ['Pilot study complete', 'Final protocol approved']
                },
                {
                    'phase': 'Phase 3: Data Collection',
                    'duration_weeks': 24,
                    'activities': [
                        'Participant recruitment',
                        'Primary data collection',
                        'Quality assurance monitoring',
                        'Interim analyses'
                    ],
                    'deliverables': [
                        'Complete dataset',
                        'Quality assurance reports',
                        'Interim analysis results',
                        'Data management documentation'
                    ],
                    'milestones': ['50% recruitment target', 'Data collection complete']
                },
                {
                    'phase': 'Phase 4: Analysis & Dissemination',
                    'duration_weeks': 28,
                    'activities': [
                        'Statistical analysis',
                        'Results interpretation',
                        'Manuscript preparation',
                        'Conference presentations'
                    ],
                    'deliverables': [
                        'Analysis results',
                        'Research manuscripts',
                        'Conference abstracts',
                        'Final research report'
                    ],
                    'milestones': ['Analysis complete', 'First publication submitted']
                }
            ],
            'critical_dependencies': [
                'Ethics approval before data collection',
                'Funding secured before team hiring',
                'Pilot results before main study launch'
            ],
            'risk_mitigation': [
                '20% time buffer included in each phase',
                'Alternative recruitment strategies prepared',
                'Backup analysis plans developed'
            ]
        }
        
        return timeline
    
    def _create_comprehensive_report(self, state: dict) -> str:
        """Create the final comprehensive research report"""
        query = state.get('query', 'Research Topic')
        
        report_sections = [
            "# 🔬 Comprehensive Research Intelligence Report",
            f"## {query}",
            f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            f"**Analysis Type:** Comprehensive Multi-Agent Research Review",
            "",
            "---",
            "",
            "## 📊 Executive Summary",
            state.get('executive_summary', 'Executive summary not available'),
            "",
            "---",
            "",
            "## 📋 Detailed Research Plan",
            state.get('detailed_research_plan', 'Detailed research plan not available'),
            "",
            "---",
            "",
            "## 🧪 Hypothesis Testing Framework", 
            state.get('hypothesis_testing_framework', 'Hypothesis testing framework not available'),
            "",
            "---",
            "",
            "## 🚀 Strategic Recommendations",
            ""
        ]
        
        # Add strategic recommendations
        recommendations = state.get('strategic_recommendations', [])
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                report_sections.extend([
                    f"### {i}. {rec.get('recommendation', 'Recommendation')} ({rec.get('priority', 'Medium')} Priority)",
                    f"**Category:** {rec.get('category', 'General')}",
                    f"**Rationale:** {rec.get('rationale', 'Not specified')}",
                    f"**Timeline:** {rec.get('timeline', 'TBD')}",
                    f"**Resources:** {rec.get('resources', 'TBD')}",
                    ""
                ])
        
        # Add implementation timeline
        timeline = state.get('implementation_timeline', {})
        if timeline:
            report_sections.extend([
                "---",
                "",
                "## ⏱️ Implementation Timeline",
                f"**Total Duration:** {timeline.get('total_duration_months', 18)} months",
                ""
            ])
            
            for phase in timeline.get('phases', []):
                report_sections.extend([
                    f"### {phase.get('phase', 'Project Phase')}",
                    f"**Duration:** {phase.get('duration_weeks', 'TBD')} weeks",
                    "**Key Activities:**"
                ])
                
                for activity in phase.get('activities', []):
                    report_sections.append(f"• {activity}")
                
                report_sections.append("")
        
        # Add citations
        citations = state.get('formatted_citations', {})
        if citations and citations.get('apa_style'):
            report_sections.extend([
                "---",
                "",
                "## 📚 References",
                ""
            ])
            
            for citation in citations['apa_style'][:10]:  # Limit to first 10
                report_sections.append(citation)
        
        report_sections.extend([
            "",
            "---",
            "",
            f"*Report generated by Research Collaborative System v2.0 - {datetime.now().strftime('%Y-%m-%d')}*"
        ])
        
        return "\n".join(report_sections)
    
    def _add_fallback_publication(self, state) -> dict:
        """Add fallback publication assistance when processing fails"""
        query = state.get('query', 'Research Topic')
        papers_count = len(state.get('papers_found', []))
        
        fallback_summary = f"""# Research Analysis Summary: {query}

## Overview
Basic analysis completed for {papers_count} papers.

## Status
- Literature collection: {'✅' if papers_count > 0 else '❌'}
- Analysis: {'✅' if 'key_themes' in state else '❌'}
- Hypothesis generation: {'✅' if 'hypotheses' in state else '❌'}

## Next Steps
- Manual review recommended
- Consider expanding literature search
- Develop detailed methodology
"""
        
        state.update({
            'executive_summary': fallback_summary,
            'detailed_research_plan': f"Basic research plan for {query} - requires enhancement",
            'hypothesis_testing_framework': "Hypothesis testing framework requires detailed specification",
            'strategic_recommendations': [
                {'priority': 'High', 'recommendation': 'Expand analysis with additional resources'},
                {'priority': 'Medium', 'recommendation': 'Consider manual expert review'}
            ],
            'comprehensive_research_report': fallback_summary,
            'publication_ready': True,
            'enhanced_outputs_generated': False
        })
        
        return state