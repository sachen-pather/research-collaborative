# src/agents/analysis_agent.py - IMPROVED

import sys
from pathlib import Path
from loguru import logger
import json

sys.path.append(str(Path(__file__).parent.parent))

from .base_agent import BaseAgent
from tools.text_analysis_tool import TextAnalyzer 
from utils.llm_config import llm_config

class AnalysisAgent(BaseAgent):
    """Advanced analysis agent with enhanced LLM-powered insights and comprehensive summaries"""
    
    def __init__(self):
        super().__init__(
            name="Analysis Agent",
            description="Performs deep analysis of research papers using LLM to identify gaps, contradictions, themes, and methodological trends"
        )
        self.text_analyzer = TextAnalyzer(self.llm)
    
    def execute(self, state) -> dict:
        """Execute comprehensive and enhanced analysis"""
        logger.info("🔬 Starting enhanced and comprehensive paper analysis...")
        
        papers = state.get('papers_found', [])
        query = state.get('query', '')
        
        focus_areas = state.get('analysis_focus_areas', [])
        if focus_areas:
            logger.info(f"🎯 Focusing analysis on: {', '.join(focus_areas)}")
        
        if not papers:
            logger.warning("No papers found for analysis")
            return self._add_empty_analysis(state)
        
        try:
            # 1. Extract key themes (now returns richer objects)
            logger.info("1️⃣ Extracting key themes with trajectory analysis...")
            themes = self.text_analyzer.extract_key_themes(papers, query)
            
            # 2. Identify research gaps (now returns richer objects)
            logger.info("2️⃣ Identifying research gaps with causal reasoning...")
            gaps = self.text_analyzer.extract_research_gaps(papers, query)
            
            # 3. Find contradictions (now returns richer objects)
            logger.info("3️⃣ Analyzing contradictions with resolution suggestions...")
            contradictions = self.text_analyzer.identify_contradictions(papers)
            
            # 4. NEW: Analyze methodological trends
            logger.info("4️⃣ Analyzing methodological trends...")
            method_trends = self.text_analyzer.analyze_methodological_trends(papers, query)

            # 5. NEW: Assess strength of evidence
            logger.info("5️⃣ Assessing overall strength of evidence...")
            evidence_strength = self.text_analyzer.assess_evidence_strength(papers)

            # 6. Generate an upgraded analysis summary with actionable insights
            logger.info("6️⃣ Creating enhanced analysis summary with recommendations...")
            analysis_summary = self._generate_enhanced_analysis_summary(
                themes, gaps, contradictions, method_trends, evidence_strength, 
                len(papers), query
            )
            
            # 7. Generate strategic insights and next steps
            strategic_insights = self._generate_strategic_insights(
                themes, gaps, contradictions, method_trends, evidence_strength, query
            )
            
            # Update state with new, richer data structures
            state['key_themes'] = themes
            state['research_gaps'] = gaps
            state['contradictions'] = contradictions
            state['methodological_trends'] = method_trends
            state['evidence_strength'] = evidence_strength
            state['analysis_summary'] = analysis_summary
            state['strategic_insights'] = strategic_insights
            state['analysis_completed'] = True
            
            logger.info(f"✅ Enhanced analysis completed successfully.")
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            state['errors'] = state.get('errors', []) + [f"Analysis error: {str(e)}"]
            # Fallback analysis
            return self._add_fallback_analysis(state, papers, query)
        
        return state
    
    def _generate_enhanced_analysis_summary(self, themes, gaps, contradictions, method_trends, evidence_strength, paper_count, query):
        """Generate a comprehensive, actionable analysis summary"""

        # Defensive: ensure correct types
        themes = themes if isinstance(themes, list) else []
        gaps = gaps if isinstance(gaps, list) else []
        contradictions = contradictions if isinstance(contradictions, list) else []
        method_trends = method_trends if isinstance(method_trends, dict) else {}
        evidence_strength = evidence_strength if isinstance(evidence_strength, dict) else {}

        # Extract key information for better summary
        domain = self._extract_domain_from_query(query)
        maturity_level = self._assess_field_maturity(themes, gaps, method_trends)
        priority_gaps = self._prioritize_research_gaps(gaps)
        
        summary_parts = [
            f"# 📊 Research Intelligence Report: {domain}",
            f"*Based on comprehensive analysis of {paper_count} academic papers*",
            "",
            "## 🎯 Executive Summary",
            f"**Field Maturity:** {maturity_level}",
            f"**Evidence Quality:** {evidence_strength.get('strength_assessment', 'Moderate')}",
            f"**Research Priority:** {self._determine_research_priority(gaps, contradictions)}",
            "",
            self._generate_key_takeaways(themes, gaps, evidence_strength),
            "",
            "## 📈 Research Landscape Analysis",
            ""
        ]

        # Enhanced theme analysis
        if themes:
            summary_parts.extend([
                "### 🔬 Dominant Research Themes",
                ""
            ])
            
            for i, theme in enumerate(themes[:4], 1):
                theme_name = theme.get('theme', 'Unknown') if isinstance(theme, dict) else str(theme)
                trajectory = theme.get('trajectory', 'Stable development') if isinstance(theme, dict) else 'Active research area'
                confidence = theme.get('confidence', 0.7) if isinstance(theme, dict) else 0.7
                
                trend_emoji = "📈" if "growing" in trajectory.lower() or "emerging" in trajectory.lower() else "📊" if "stable" in trajectory.lower() else "🔄"
                confidence_indicator = "🔥" if confidence > 0.8 else "⭐" if confidence > 0.6 else "💭"
                
                summary_parts.append(f"**{i}. {theme_name}** {confidence_indicator}")
                summary_parts.append(f"   *Trend:* {trend_emoji} {trajectory}")
                summary_parts.append("")
        
        # Critical gaps analysis
        if gaps:
            summary_parts.extend([
                "### 🎯 High-Priority Research Gaps",
                ""
            ])
            
            for i, gap in enumerate(priority_gaps[:3], 1):
                gap_desc = gap.get('description', 'Unknown gap') if isinstance(gap, dict) else str(gap)
                impact = gap.get('impact', 'Moderate') if isinstance(gap, dict) else 'Moderate'
                reason = gap.get('reason', 'Literature analysis') if isinstance(gap, dict) else 'Identified through analysis'
                
                impact_emoji = "🚨" if "high" in impact.lower() or "critical" in impact.lower() else "⚠️" if "medium" in impact.lower() else "💡"
                
                summary_parts.append(f"**{i}. {gap_desc}** {impact_emoji}")
                summary_parts.append(f"   *Impact Level:* {impact}")
                summary_parts.append(f"   *Root Cause:* {reason}")
                summary_parts.append("")

        # Methodological insights
        if method_trends:
            summary_parts.extend([
                "### 🛠️ Methodological Landscape",
                ""
            ])
            
            common_methods = method_trends.get('common_methods', [])
            emerging_methods = method_trends.get('emerging_methods', [])
            limitations = method_trends.get('limitations', [])
            
            if common_methods:
                methods_str = ", ".join(common_methods) if isinstance(common_methods, list) else str(common_methods)
                summary_parts.append(f"**Established Methods:** {methods_str}")
            
            if emerging_methods:
                emerging_str = ", ".join(emerging_methods) if isinstance(emerging_methods, list) else str(emerging_methods)
                summary_parts.append(f"**Emerging Approaches:** 🌟 {emerging_str}")
            
            if limitations:
                first_limitation = limitations[0] if isinstance(limitations, list) else str(limitations)
                summary_parts.append(f"**Key Limitation:** ⚠️ {first_limitation}")
            
            summary_parts.append("")

        # Contradictions and challenges
        if contradictions:
            summary_parts.extend([
                "### ⚖️ Research Challenges & Contradictions",
                ""
            ])
            
            for i, contradiction in enumerate(contradictions[:2], 1):
                if isinstance(contradiction, dict):
                    contr_text = contradiction.get('contradiction', 'Methodological inconsistency identified')
                    resolution = contradiction.get('resolution_suggestion', 'Further research needed')
                else:
                    contr_text = str(contradiction)
                    resolution = 'Requires systematic investigation'
                
                summary_parts.append(f"**{i}.** {contr_text[:200]}...")
                summary_parts.append(f"   *Suggested Resolution:* {resolution}")
                summary_parts.append("")

        # Evidence assessment
        summary_parts.extend([
            "## 📋 Evidence Assessment",
            f"**Overall Strength:** {evidence_strength.get('strength_assessment', 'Moderate')}",
            ""
        ])
        
        factors = evidence_strength.get('influencing_factors', [])
        if factors:
            factor_str = factors[0] if isinstance(factors, list) else str(factors)
            summary_parts.append(f"**Key Factor:** {factor_str}")
            summary_parts.append("")

        return "\n".join(summary_parts)
    
    def _generate_strategic_insights(self, themes, gaps, contradictions, method_trends, evidence_strength, query):
        """Generate strategic insights and actionable recommendations"""
        
        insights = {
            'research_opportunities': [],
            'methodological_recommendations': [],
            'collaboration_suggestions': [],
            'funding_priorities': [],
            'timeline_assessment': {},
            'risk_factors': []
        }
        
        # Research opportunities based on gaps
        for gap in gaps[:3] if isinstance(gaps, list) else []:
            if isinstance(gap, dict):
                insights['research_opportunities'].append({
                    'opportunity': gap.get('description', 'Unknown opportunity'),
                    'potential_impact': gap.get('impact', 'Moderate'),
                    'feasibility': 'High' if 'high' in gap.get('impact', '').lower() else 'Medium',
                    'estimated_duration': '12-24 months'
                })
        
        # Methodological recommendations
        if isinstance(method_trends, dict):
            limitations = method_trends.get('limitations', [])
            emerging = method_trends.get('emerging_methods', [])
            
            if limitations:
                for limitation in limitations[:2] if isinstance(limitations, list) else [limitations]:
                    insights['methodological_recommendations'].append({
                        'recommendation': f'Address limitation: {limitation}',
                        'priority': 'High',
                        'approach': 'Develop new methodological framework'
                    })
            
            if emerging:
                for method in emerging[:2] if isinstance(emerging, list) else [emerging]:
                    insights['methodological_recommendations'].append({
                        'recommendation': f'Investigate potential of {method}',
                        'priority': 'Medium',
                        'approach': 'Pilot study with comparative analysis'
                    })
        
        # Timeline assessment
        insights['timeline_assessment'] = {
            'short_term_goals': '3-6 months: Literature synthesis and methodology development',
            'medium_term_goals': '6-18 months: Primary research execution',
            'long_term_vision': '2-3 years: Field advancement and policy impact'
        }
        
        # Risk factors
        if contradictions:
            insights['risk_factors'].append('Contradictory findings may impact research validity')
        
        evidence_level = evidence_strength.get('strength_assessment', '').lower()
        if 'weak' in evidence_level or 'limited' in evidence_level:
            insights['risk_factors'].append('Limited evidence base requires cautious interpretation')
        
        return insights
    
    def _extract_domain_from_query(self, query):
        """Extract domain from research query"""
        query_lower = query.lower()
        
        if any(term in query_lower for term in ['machine learning', 'ai', 'neural', 'deep learning']):
            return 'Artificial Intelligence & Machine Learning'
        elif any(term in query_lower for term in ['blockchain', 'supply chain', 'transparency']):
            return 'Blockchain & Supply Chain Technology'
        elif any(term in query_lower for term in ['medical', 'clinical', 'health', 'diagnosis']):
            return 'Healthcare & Medical Research'
        elif any(term in query_lower for term in ['climate', 'environment', 'sustainability']):
            return 'Environmental & Climate Science'
        elif any(term in query_lower for term in ['quantum', 'computing', 'cryptography']):
            return 'Quantum Computing & Cryptography'
        else:
            return query.title() if len(query) < 50 else 'Multidisciplinary Research'
    
    def _assess_field_maturity(self, themes, gaps, method_trends):
        """Assess the maturity level of the research field"""
        
        # Count indicators
        theme_count = len(themes) if isinstance(themes, list) else 0
        gap_count = len(gaps) if isinstance(gaps, list) else 0
        
        method_diversity = 0
        if isinstance(method_trends, dict):
            common_methods = method_trends.get('common_methods', [])
            method_diversity = len(common_methods) if isinstance(common_methods, list) else 0
        
        # Maturity assessment logic
        if theme_count >= 4 and method_diversity >= 3 and gap_count <= 2:
            return 'Mature Field'
        elif theme_count >= 3 and method_diversity >= 2:
            return 'Developing Field'
        elif gap_count >= 4:
            return 'Emerging Field'
        else:
            return 'Evolving Field'
    
    def _prioritize_research_gaps(self, gaps):
        """Prioritize research gaps by impact and feasibility"""
        if not isinstance(gaps, list):
            return []
        
        # Sort gaps by impact level
        prioritized = []
        high_impact = []
        medium_impact = []
        other_gaps = []
        
        for gap in gaps:
            if isinstance(gap, dict):
                impact = gap.get('impact', '').lower()
                if 'high' in impact or 'critical' in impact:
                    high_impact.append(gap)
                elif 'medium' in impact or 'moderate' in impact:
                    medium_impact.append(gap)
                else:
                    other_gaps.append(gap)
            else:
                other_gaps.append(gap)
        
        return high_impact + medium_impact + other_gaps
    
    def _determine_research_priority(self, gaps, contradictions):
        """Determine overall research priority level"""
        gap_count = len(gaps) if isinstance(gaps, list) else 0
        contradiction_count = len(contradictions) if isinstance(contradictions, list) else 0
        
        high_impact_gaps = 0
        if isinstance(gaps, list):
            for gap in gaps:
                if isinstance(gap, dict) and 'high' in gap.get('impact', '').lower():
                    high_impact_gaps += 1
        
        if high_impact_gaps >= 2 or contradiction_count >= 2:
            return 'High Priority 🔥'
        elif gap_count >= 3 or contradiction_count >= 1:
            return 'Medium Priority ⭐'
        else:
            return 'Standard Priority 📊'
    
    def _generate_key_takeaways(self, themes, gaps, evidence_strength):
        """Generate 3-4 key takeaways from the analysis"""
        takeaways = []
        
        # Theme-based takeaway
        if themes and len(themes) > 0:
            dominant_theme = themes[0]
            theme_name = dominant_theme.get('theme', 'Primary research area') if isinstance(dominant_theme, dict) else str(dominant_theme)
            takeaways.append(f"• **{theme_name}** emerges as the dominant research focus")
        
        # Gap-based takeaway  
        if gaps and len(gaps) > 0:
            high_priority_gaps = [g for g in gaps if isinstance(g, dict) and 'high' in g.get('impact', '').lower()]
            if high_priority_gaps:
                takeaways.append(f"• **{len(high_priority_gaps)} critical research gaps** require immediate attention")
            else:
                takeaways.append(f"• **{len(gaps)} research opportunities** identified for advancement")
        
        # Evidence-based takeaway
        strength = evidence_strength.get('strength_assessment', '').lower()
        if 'strong' in strength:
            takeaways.append("• **Strong evidence base** supports current approaches")
        elif 'weak' in strength or 'limited' in strength:
            takeaways.append("• **Limited evidence** highlights need for rigorous studies")
        else:
            takeaways.append("• **Moderate evidence** suggests selective approach to research priorities")
        
        # Methodological takeaway (if we have fewer than 3 takeaways)
        if len(takeaways) < 3:
            takeaways.append("• **Methodological diversity** indicates maturing research field")
        
        return "\n".join(takeaways)
    
    def _add_empty_analysis(self, state) -> dict:
        """Add empty analysis structure when no papers found"""
        state['key_themes'] = []
        state['research_gaps'] = []
        state['contradictions'] = []
        state['methodological_trends'] = {}
        state['evidence_strength'] = {}
        state['analysis_summary'] = "## ⚠️ Analysis Unavailable\n\nNo papers were found for analysis. Consider:\n- Broadening search terms\n- Checking alternative databases\n- Reviewing query specificity"
        state['strategic_insights'] = {
            'research_opportunities': [],
            'methodological_recommendations': [],
            'collaboration_suggestions': [],
            'funding_priorities': [],
            'timeline_assessment': {},
            'risk_factors': ['No literature base available for analysis']
        }
        state['analysis_completed'] = False
        return state
    
    def _add_fallback_analysis(self, state, papers: list, query: str) -> dict:
        """Add fallback analysis when LLM analysis fails"""
        # Simple theme extraction from titles and abstracts
        themes = self._extract_basic_themes(papers, query)
        gaps = self._generate_basic_gaps(query, themes)
        
        state['key_themes'] = themes
        state['research_gaps'] = gaps
        state['contradictions'] = [{'contradiction': 'Analysis limited due to processing constraints', 'resolution_suggestion': 'Manual review recommended'}]
        state['methodological_trends'] = {
            'common_methods': ['Literature review', 'Empirical analysis'],
            'emerging_methods': ['Advanced computational approaches'],
            'limitations': ['Limited automated analysis capability']
        }
        state['evidence_strength'] = {
            'strength_assessment': 'Requires manual evaluation',
            'influencing_factors': ['Automated analysis limitations']
        }
        
        # Generate fallback summary
        state['analysis_summary'] = self._generate_fallback_summary(len(papers), query, themes, gaps)
        
        # Basic strategic insights
        state['strategic_insights'] = {
            'research_opportunities': [
                {'opportunity': f'Comprehensive analysis of {query}', 'potential_impact': 'High', 'feasibility': 'High', 'estimated_duration': '6-12 months'}
            ],
            'methodological_recommendations': [
                {'recommendation': 'Conduct systematic literature review', 'priority': 'High', 'approach': 'Manual analysis with domain experts'}
            ],
            'timeline_assessment': {
                'short_term_goals': '1-3 months: Manual literature review',
                'medium_term_goals': '3-9 months: Primary research design',
                'long_term_vision': '1-2 years: Research execution and publication'
            },
            'risk_factors': ['Limited automated analysis', 'Requires expert domain knowledge']
        }
        
        state['analysis_completed'] = True
        return state
    
    def _extract_basic_themes(self, papers, query):
        """Extract basic themes from paper titles and abstracts"""
        themes = []
        
        # Collect all text
        all_text = ""
        for paper in papers:
            title = paper.get('title', '')
            abstract = paper.get('abstract', '')
            all_text += f" {title} {abstract}"
        
        all_text = all_text.lower()
        
        # Domain-specific keyword extraction
        domain_themes = {
            'machine learning': ['machine learning', 'neural network', 'deep learning', 'algorithm'],
            'blockchain': ['blockchain', 'distributed ledger', 'smart contract', 'cryptocurrency'],
            'medical': ['medical', 'clinical', 'diagnosis', 'treatment', 'healthcare'],
            'climate': ['climate', 'environmental', 'sustainability', 'carbon', 'emission'],
            'quantum': ['quantum', 'qubit', 'superposition', 'entanglement']
        }
        
        for theme_category, keywords in domain_themes.items():
            keyword_count = sum(1 for keyword in keywords if keyword in all_text)
            if keyword_count >= 2:  # At least 2 keywords found
                themes.append({
                    'theme': theme_category.title(),
                    'trajectory': 'Active research area',
                    'confidence': min(0.9, keyword_count * 0.2 + 0.3)
                })
        
        # Add query-based theme if no domain themes found
        if not themes:
            query_words = query.split()[:3]  # First 3 words
            theme_name = " ".join(query_words).title()
            themes.append({
                'theme': theme_name,
                'trajectory': 'Emerging research focus',
                'confidence': 0.6
            })
        
        return themes[:4]  # Return top 4 themes
    
    def _generate_basic_gaps(self, query, themes):
        """Generate basic research gaps based on query and themes"""
        gaps = []
        
        # Generic gaps based on common research needs
        gaps.append({
            'description': f'Limited comprehensive evaluation methods for {query}',
            'impact': 'High',
            'reason': 'Methodology gap identified through literature patterns'
        })
        
        gaps.append({
            'description': 'Need for larger-scale empirical studies',
            'impact': 'Medium',
            'reason': 'Most studies appear to have limited scope'
        })
        
        if themes:
            first_theme = themes[0]
            theme_name = first_theme.get('theme', 'research area') if isinstance(first_theme, dict) else str(first_theme)
            gaps.append({
                'description': f'Integration challenges between {theme_name} and practical applications',
                'impact': 'Medium',
                'reason': 'Common gap between theoretical research and implementation'
            })
        
        return gaps
    
    def _generate_fallback_summary(self, paper_count, query, themes, gaps):
        """Generate fallback summary when automated analysis fails"""
        
        theme_names = []
        for theme in themes:
            if isinstance(theme, dict):
                theme_names.append(theme.get('theme', 'Unknown'))
            else:
                theme_names.append(str(theme))
        
        return f"""# 📊 Basic Analysis Report: {query.title()}
*Based on {paper_count} papers - Limited automated analysis*

## ⚠️ Analysis Notice
This analysis was generated using basic text processing due to advanced analysis limitations. Manual expert review is recommended for comprehensive insights.

## 📈 Identified Themes
{chr(10).join([f"• **{theme}**" for theme in theme_names[:3]])}

## 🎯 Potential Research Areas
{chr(10).join([f"• {gap.get('description', 'Unknown gap')}" for gap in gaps[:2]])}

## 📋 Recommendations
• Conduct detailed manual literature review
• Engage domain experts for comprehensive analysis  
• Consider systematic review methodology
• Validate findings through expert consultation

## 🔄 Next Steps
1. **Manual Review**: Expert analysis of {paper_count} papers
2. **Theme Validation**: Confirm identified themes with domain specialists
3. **Gap Analysis**: Detailed assessment of research opportunities
4. **Methodology Design**: Develop appropriate research approaches
"""