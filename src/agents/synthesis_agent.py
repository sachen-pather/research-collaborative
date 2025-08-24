"""
Enhanced Synthesis Agent with hypothesis generation
"""
import sys
from pathlib import Path
from loguru import logger

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from agents.base_agent import BaseAgent
from tools.hypothesis_generator import HypothesisGenerator
from utils.llm_config import llm_config

class SynthesisAgent(BaseAgent):
    """Synthesis agent that generates hypotheses and research plans"""
    
    def __init__(self):
        super().__init__(
            name="Synthesis Agent",
            description="Synthesizes analysis results into actionable hypotheses and research plans"
        )
        self.hypothesis_generator = HypothesisGenerator(self.llm)
    
    def execute(self, state) -> dict:
        """Execute synthesis and hypothesis generation"""
        logger.info("🔗 Starting research synthesis...")
        
        query = state.get('query', '')
        themes = state.get('key_themes', [])
        gaps = state.get('research_gaps', [])
        contradictions = state.get('contradictions', [])
        papers = state.get('papers_found', [])
        
        try:
            # 1. Generate research hypotheses
            logger.info("1️⃣ Generating research hypotheses...")
            hypotheses = self.hypothesis_generator.generate_hypotheses(state)
            
            # 2. Create research plan
            logger.info("2️⃣ Creating research plan...")
            research_plan = self._create_research_plan(query, hypotheses, themes, gaps)
            
            # 3. Generate final synthesis
            logger.info("3️⃣ Creating comprehensive synthesis...")
            synthesis = self._generate_comprehensive_synthesis(
                query, papers, themes, gaps, contradictions, hypotheses, research_plan
            )
            
            # Update state
            state['hypotheses'] = hypotheses
            state['research_plan'] = research_plan
            state['final_synthesis'] = synthesis
            state['synthesis_completed'] = True
            
            logger.info(f"✅ Synthesis completed: {len(hypotheses)} hypotheses generated")
            
        except Exception as e:
            logger.error(f"❌ Synthesis failed: {e}")
            state['errors'] = state.get('errors', []) + [f"Synthesis error: {str(e)}"]
            return self._add_fallback_synthesis(state, query, themes, papers)
        
        return state
    
    def _create_research_plan(self, query: str, hypotheses: list, themes: list, gaps: list) -> dict:
        """Create a structured research plan"""
        
        # Extract methodologies from hypotheses
        methodologies = []
        for hyp in hypotheses:
            if isinstance(hyp, dict) and hyp.get('methodology'):
                methodologies.append(hyp['methodology'])
        
        if not methodologies:
            methodologies = [
                "Literature review and gap analysis",
                "Experimental design and implementation",
                "Data collection and validation",
                "Comparative analysis with baselines"
            ]
        
        plan = {
            'title': f"Research Plan: {query}",
            'objectives': [
                f"Investigate {query} applications and limitations",
                f"Address identified research gaps in {themes[0] if themes else 'the field'}",
                "Develop novel approaches based on hypothesis testing",
                "Validate findings through empirical evaluation"
            ],
            'hypotheses': [hyp.get('statement', str(hyp)) for hyp in hypotheses],
            'methodology': methodologies,
            'timeline': {
                'Phase 1 (Months 1-2)': 'Comprehensive literature review and methodology design',
                'Phase 2 (Months 3-6)': 'Implementation and initial experiments',
                'Phase 3 (Months 7-9)': 'Validation, evaluation, and refinement',
                'Phase 4 (Months 10-12)': 'Analysis, documentation, and dissemination'
            },
            'resources_needed': [
                'Access to relevant datasets',
                'Computational resources for experiments',
                'Collaboration with domain experts',
                'Publication and conference venues'
            ],
            'expected_outcomes': [
                f"Novel insights into {query}",
                "Validated research hypotheses",
                "Open-source tools and datasets",
                "High-impact publications"
            ]
        }
        
        return plan
    
    def _generate_comprehensive_synthesis(self, query: str, papers: list, themes: list, 
                                         gaps: list, contradictions: list, hypotheses: list, 
                                         research_plan: dict) -> str:
        """Generate comprehensive research synthesis"""
        
        synthesis_parts = [
            f"# 🔬 Research Synthesis: {query}",
            "",
            f"## 📊 Overview",
            f"Based on analysis of **{len(papers)} research papers**, this synthesis identifies key opportunities and actionable research directions.",
            "",
            "## 🎯 Key Research Themes",
        ]
        
        for i, theme in enumerate(themes[:5], 1):
            synthesis_parts.append(f"{i}. **{theme}**")
        
        synthesis_parts.extend([
            "",
            "## 🔍 Critical Research Gaps",
        ])
        
        for i, gap in enumerate(gaps[:4], 1):
            if isinstance(gap, dict):
                desc = gap.get('description', 'No description')
                synthesis_parts.append(f"{i}. {desc}")
        
        return "\n".join(synthesis_parts)
    
    def _add_fallback_synthesis(self, state, query: str, themes: list, papers: list) -> dict:
        """Add fallback synthesis when processing fails"""
        fallback_hypotheses = [
            {'statement': f'Improving methods in {query} will enhance performance', 'rationale': 'Based on literature analysis'},
            {'statement': f'Integration of multiple approaches in {query} shows promise', 'rationale': 'Cross-methodology potential'}
        ]
        
        state['hypotheses'] = fallback_hypotheses
        state['research_plan'] = {'title': f'Research Plan: {query}', 'objectives': ['Expand research', 'Test hypotheses']}
        state['final_synthesis'] = f'Synthesis for {query} - {len(papers)} papers analyzed'
        state['synthesis_completed'] = True
        
        return state