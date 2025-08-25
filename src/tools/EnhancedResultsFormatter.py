from datetime import datetime

# 2. Create the missing EnhancedResultsFormatter class
class EnhancedResultsFormatter:
    """Enhanced Results Formatter - Creates comprehensive, actionable research outputs"""
    
    def __init__(self):
        self.confidence_threshold = 0.7
    
    def generate_executive_summary(self, state: dict) -> str:
        """Generate a comprehensive executive summary with actionable insights"""
        query = state.get('query', 'Research Topic')
        papers_count = len(state.get('papers_found', []))
        themes = state.get('key_themes', [])
        gaps = state.get('research_gaps', [])
        hypotheses = state.get('hypotheses', [])
        methodology = state.get('research_methodology', {})
        evidence_strength = state.get('evidence_strength', {})
        verification_results = state.get('verification_results', {})
        
        # Calculate key metrics
        confidence_score = verification_results.get('overall_confidence', 0.5)
        research_maturity = self._assess_research_maturity(papers_count, themes, evidence_strength)
        implementation_readiness = self._assess_implementation_readiness(gaps, hypotheses, methodology)
        
        summary_parts = [
            f"# 🔬 Research Intelligence Report",
            f"## {query}",
            "",
            f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            f"**Analysis Confidence:** {confidence_score:.1%}",
            f"**Research Maturity:** {research_maturity}",
            f"**Implementation Readiness:** {implementation_readiness}",
            "",
            "---",
            "",
            "## 🎯 Key Findings at a Glance",
            "",
            f"📊 **Literature Base:** {papers_count} peer-reviewed papers analyzed",
            f"🔍 **Research Themes:** {len(themes)} major themes identified",
            f"⚡ **Research Gaps:** {len(gaps)} high-priority gaps discovered",
            f"💡 **Testable Hypotheses:** {len(hypotheses)} hypotheses generated",
            "",
        ]
        
        # Strategic recommendations
        recommendations = self._generate_strategic_recommendations_summary(state)
        summary_parts.extend([
            "## 🚀 Strategic Recommendations",
            "",
        ])
        
        for i, rec in enumerate(recommendations[:4], 1):
            summary_parts.append(f"**{i}.** {rec}")
        
        summary_parts.extend([
            "",
            "## 🔬 Research Landscape Analysis",
            "",
        ])
        
        # Theme analysis with trajectories
        if themes:
            summary_parts.append("**Emerging Themes & Trajectories:**")
            for theme in themes[:3]:
                if isinstance(theme, dict):
                    trajectory = theme.get('trajectory', 'Developing')
                    theme_name = theme.get('theme', 'Unknown theme')
                    summary_parts.append(f"• **{theme_name}**: {trajectory}")
                else:
                    summary_parts.append(f"• **{theme}**: Active research area")
            summary_parts.append("")
        
        # Critical gaps with impact assessment
        if gaps:
            summary_parts.append("**Critical Research Gaps:**")
            for gap in gaps[:3]:
                if isinstance(gap, dict):
                    desc = gap.get('description', 'Unknown gap')
                    impact = gap.get('impact', 'Medium')
                    summary_parts.append(f"• {desc} *({impact} impact)*")
                else:
                    summary_parts.append(f"• {gap}")
            summary_parts.append("")
        
        # Research readiness assessment
        summary_parts.extend([
            "## 📈 Research Readiness Assessment",
            "",
            f"**Confidence Level:** {confidence_score:.1%} ({'High' if confidence_score >= 0.8 else 'Moderate' if confidence_score >= 0.6 else 'Developing'})",
            f"**Evidence Quality:** {evidence_strength.get('strength_assessment', 'Moderate')}",
            f"**Methodology Maturity:** {'Advanced' if methodology else 'Requires Development'}",
            "",
        ])
        
        # Call to action
        summary_parts.extend([
            "## 🎯 Immediate Next Steps",
            "",
            "**High Priority Actions:**",
            "1. Review detailed methodology and timeline",
            "2. Assess resource requirements and funding options",
            "3. Identify key collaborators and stakeholders",
            "4. Begin preliminary research planning",
            "",
            "---",
            "*This report provides a comprehensive foundation for research planning and decision-making.*"
        ])
        
        return "\n".join(summary_parts)
    
    def generate_detailed_research_plan(self, state: dict) -> str:
        """Generate a detailed, actionable research plan"""
        query = state.get('query', 'Research Topic')
        methodology = state.get('research_methodology', {})
        hypotheses = state.get('hypotheses', [])
        gaps = state.get('research_gaps', [])
        themes = state.get('key_themes', [])
        
        plan_parts = [
            f"# 📋 Detailed Research Implementation Plan",
            f"## {query}",
            "",
            f"**Plan Generated:** {datetime.now().strftime('%B %d, %Y')}",
            f"**Implementation Readiness:** {'High' if methodology else 'Moderate'}",
            "",
            "---",
            "",
        ]
        
        # Research objectives with SMART criteria
        objectives = self._create_smart_objectives(hypotheses, gaps, themes)
        plan_parts.extend([
            "## 🎯 Research Objectives",
            "",
            "**Primary Objectives (SMART criteria):**",
        ])
        
        for i, obj in enumerate(objectives[:3], 1):
            plan_parts.append(f"{i}. {obj}")
        
        plan_parts.extend([
            "",
            "## 🔬 Methodology Framework",
            "",
            f"**Research Design:** {methodology.get('research_design', 'Mixed-methods approach requiring specification')}",
            f"**Data Collection:** {methodology.get('data_collection', 'Multi-modal data collection strategy')}",
            f"**Analysis Plan:** {methodology.get('statistical_analysis', 'Comprehensive statistical analysis')}",
            "",
            "## 📊 Success Metrics & Evaluation",
            "",
            "### Primary Success Indicators",
            "• **Recruitment Success:** Achieve target sample size within timeline",
            "• **Data Quality:** <5% missing data for primary outcomes", 
            "• **Retention Rate:** >80% participant completion",
            "• **Protocol Adherence:** >90% compliance with study procedures",
            "",
            "### Scientific Impact Metrics",
            "• Statistical significance of primary hypotheses (p<0.05)",
            "• Effect sizes meeting clinical/practical significance thresholds",
            "• Peer review acceptance at target journals",
            "• Citation impact within 2 years post-publication",
            "",
            "---",
            "*This comprehensive plan provides a roadmap for successful research implementation.*"
        ])
        
        return "\n".join(plan_parts)
    
    def generate_hypothesis_testing_framework(self, state: dict) -> str:
        """Generate detailed hypothesis testing framework"""
        hypotheses = state.get('hypotheses', [])
        
        if not hypotheses:
            return "# 🧪 Hypothesis Testing Framework\n\nNo hypotheses available for testing framework development.\n\n**Recommendation:** Generate specific, testable hypotheses before developing testing protocols."
        
        framework_parts = [
            "# 🧪 Hypothesis Testing Framework",
            "",
            f"**Framework Generated:** {datetime.now().strftime('%B %d, %Y')}",
            f"**Number of Hypotheses:** {len(hypotheses)}",
            "",
            "---",
            ""
        ]
        
        for i, hypothesis in enumerate(hypotheses, 1):
            if isinstance(hypothesis, dict):
                statement = hypothesis.get('statement', f'Hypothesis {i}')
                rationale = hypothesis.get('rationale', 'No rationale provided')
                
                framework_parts.extend([
                    f"## Hypothesis {i}: Testing Protocol",
                    "",
                    f"**Statement:** {statement}",
                    "",
                    f"**Rationale:** {rationale}",
                    "",
                    "### Statistical Framework",
                    "**Null Hypothesis (H₀):** No significant difference/relationship exists",
                    f"**Alternative Hypothesis (H₁):** {statement}",
                    "**Significance Level:** α = 0.05 (two-tailed)",
                    "**Power:** β = 0.80 (80% power to detect medium effect)",
                    "",
                    "### Analysis Plan",
                    "• **Primary Analysis:** [Appropriate statistical test based on data type]",
                    "• **Secondary Analyses:** [Exploratory analyses]",
                    "• **Sensitivity Analyses:** [Robustness checks]",
                    "• **Missing Data:** [Imputation strategy]",
                    "",
                    "---",
                    ""
                ])
            else:
                framework_parts.extend([
                    f"## Hypothesis {i}",
                    f"**Statement:** {hypothesis}",
                    "**Testing protocol requires detailed specification**",
                    "",
                    "---",
                    ""
                ])
        
        return "\n".join(framework_parts)
    
    # Helper methods
    def _assess_research_maturity(self, papers_count: int, themes: list, evidence_strength: dict) -> str:
        if papers_count >= 20:
            return "Mature Field"
        elif papers_count >= 10:
            return "Developing Field" 
        elif papers_count >= 5:
            return "Emerging Field"
        else:
            return "Novel/Nascent Field"
    
    def _assess_implementation_readiness(self, gaps: list, hypotheses: list, methodology: dict) -> str:
        readiness_score = 0
        if hypotheses and len(hypotheses) >= 2:
            readiness_score += 30
        if gaps and len(gaps) >= 2:
            readiness_score += 25
        if methodology and len(methodology) >= 5:
            readiness_score += 45
        
        if readiness_score >= 80:
            return "High - Ready to implement"
        elif readiness_score >= 60:
            return "Moderate - Planning needed"
        elif readiness_score >= 40:
            return "Low - Significant preparation required"
        else:
            return "Very Low - Foundational work needed"
    
    def _generate_strategic_recommendations_summary(self, state: dict) -> list:
        recommendations = []
        papers_count = len(state.get('papers_found', []))
        gaps = state.get('research_gaps', [])
        hypotheses = state.get('hypotheses', [])
        
        if papers_count < 10:
            recommendations.append("**Expand Literature Base**: Conduct broader search across multiple databases")
        
        if gaps and len(gaps) >= 3:
            recommendations.append("**Prioritize Research Gaps**: Focus on high-impact gaps with available resources")
        
        if hypotheses and len(hypotheses) >= 2:
            recommendations.append("**Begin Pilot Testing**: Start with small-scale studies to validate hypotheses")
        
        recommendations.append("**Secure Funding**: Develop targeted grant applications based on identified opportunities")
        
        return recommendations
    
    def _create_smart_objectives(self, hypotheses: list, gaps: list, themes: list) -> list:
        objectives = []
        
        for i, hypothesis in enumerate(hypotheses[:2], 1):
            if isinstance(hypothesis, dict):
                statement = hypothesis.get('statement', f'hypothesis {i}')
                objectives.append(f"**Test and validate** {statement.lower()} **within 12 months** through rigorous experimental design")
            else:
                objectives.append(f"**Investigate** {str(hypothesis)[:100]}... **by [specific date]** using validated measures")
        
        if gaps:
            gap = gaps[0]
            if isinstance(gap, dict):
                desc = gap.get('description', 'identified research gap')
                objectives.append(f"**Address the critical gap** in {desc.lower()} **by collecting primary data** within 18 months")
        
        return objectives