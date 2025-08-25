"""
Enhanced Methodology Designer Agent - Creates comprehensive research methodologies
"""
import sys
from pathlib import Path
from loguru import logger
from datetime import datetime
import json

sys.path.append(str(Path(__file__).parent.parent))

from agents.base_agent import BaseAgent
from tools.methodology_designer import MethodologyDesigner
from utils.llm_config import llm_config

class MethodologyDesignerAgent(BaseAgent):
    """Agent specialized in designing comprehensive research methodologies"""
    
    def __init__(self):
        super().__init__(
            name="Methodology Designer Agent",
            description="Designs rigorous, practical research methodologies with experimental frameworks and validation protocols"
        )
        self.methodology_designer = MethodologyDesigner(self.llm)
    
    def execute(self, state) -> dict:
        """Execute comprehensive methodology design"""
        logger.info("🔬 Starting comprehensive methodology design...")
        
        query = state.get('query', '')
        themes = state.get('key_themes', [])
        gaps = state.get('research_gaps', [])
        hypotheses = state.get('hypotheses', [])
        papers = state.get('papers_found', [])
        contradictions = state.get('contradictions', [])
        
        try:
            # 1. Design core research methodology
            logger.info("1️⃣ Designing core research methodology...")
            methodology = self.methodology_designer.design_research_methodology(state)
            
            # 2. Create experimental framework
            logger.info("2️⃣ Creating experimental framework...")
            experimental_framework = self._create_experimental_framework(hypotheses, methodology, themes)
            
            # 3. Design validation protocols
            logger.info("3️⃣ Designing validation protocols...")
            validation_protocols = self._design_validation_protocols(hypotheses, gaps)
            
            # 4. Create resource planning
            logger.info("4️⃣ Creating resource planning...")
            resource_plan = self._create_resource_plan(methodology, experimental_framework)
            
            # 5. Generate methodology report
            logger.info("5️⃣ Generating comprehensive methodology report...")
            methodology_report = self._generate_methodology_report(
                query, methodology, experimental_framework, validation_protocols, resource_plan
            )
            
            # Update state
            state['research_methodology'] = methodology
            state['experimental_framework'] = experimental_framework
            state['validation_protocols'] = validation_protocols
            state['resource_plan'] = resource_plan
            state['methodology_report'] = methodology_report
            state['methodology_design_completed'] = True
            
            logger.info("✅ Comprehensive methodology design completed")
            
        except Exception as e:
            logger.error(f"❌ Methodology design failed: {e}")
            state['errors'] = state.get('errors', []) + [f"Methodology design error: {str(e)}"]
            return self._add_fallback_methodology(state, query, themes, gaps)
        
        return state
    
    def _create_experimental_framework(self, hypotheses: list, methodology: dict, themes: list) -> dict:
        """Create detailed experimental framework"""
        
        if not hypotheses or not methodology:
            return self._fallback_experimental_framework(themes)
        
        framework = {
            'study_design': methodology.get('research_design', 'Mixed-methods approach'),
            'phases': [],
            'variables': {
                'independent': [],
                'dependent': [],
                'control': []
            },
            'measurement_instruments': [],
            'data_collection_schedule': {},
            'quality_assurance': []
        }
        
        # Create phases based on hypotheses
        for i, hypothesis in enumerate(hypotheses[:3]):
            phase = {
                'phase_number': i + 1,
                'hypothesis_tested': hypothesis.get('statement', str(hypothesis)),
                'duration_weeks': 4 + i * 2,  # Progressive phases
                'activities': [
                    'Participant recruitment and screening',
                    'Baseline data collection',
                    'Intervention implementation',
                    'Follow-up assessments',
                    'Data analysis and interpretation'
                ],
                'success_criteria': [
                    'Minimum 80% participant retention',
                    'Complete data collection protocols',
                    'Statistical significance threshold p<0.05'
                ],
                'risk_mitigation': [
                    'Pilot testing of all instruments',
                    'Regular monitoring and adjustment protocols',
                    'Backup data collection methods'
                ]
            }
            framework['phases'].append(phase)
        
        # Define variables based on first hypothesis
        if hypotheses:
            first_hyp = hypotheses[0]
            if isinstance(first_hyp, dict):
                statement = first_hyp.get('statement', '')
                # Extract potential variables from hypothesis
                if 'improve' in statement.lower():
                    framework['variables']['dependent'].append('Performance improvement measure')
                if 'method' in statement.lower() or 'approach' in statement.lower():
                    framework['variables']['independent'].append('Methodological approach type')
                framework['variables']['control'].extend([
                    'Participant demographics',
                    'Baseline competency levels',
                    'Environmental conditions'
                ])
        
        # Define measurement instruments
        framework['measurement_instruments'] = [
            'Pre/post assessment surveys',
            'Performance metrics tracking',
            'Qualitative interview protocols',
            'Observation checklists',
            'Digital analytics tools'
        ]
        
        # Create data collection schedule
        framework['data_collection_schedule'] = {
            'baseline': 'Week 0',
            'mid_intervention': 'Week 2-4 (per phase)',
            'post_intervention': 'Week 6-8 (per phase)',
            'follow_up': 'Week 12-16 (per phase)'
        }
        
        # Quality assurance measures
        framework['quality_assurance'] = [
            'Inter-rater reliability checks',
            'Double data entry and verification',
            'Regular calibration of instruments',
            'Audit trail maintenance',
            'Blind data analysis protocols'
        ]
        
        return framework
    
    def _design_validation_protocols(self, hypotheses: list, gaps: list) -> dict:
        """Design validation protocols for research findings"""
        
        protocols = {
            'internal_validation': {
                'methods': [
                    'Cross-validation techniques',
                    'Bootstrap resampling',
                    'Sensitivity analysis',
                    'Robustness checks'
                ],
                'criteria': [
                    'Consistent results across validation methods',
                    'Effect size stability',
                    'Minimal sensitivity to outliers'
                ]
            },
            'external_validation': {
                'methods': [
                    'Independent dataset validation',
                    'Multi-site replication',
                    'Different population testing',
                    'Temporal validation'
                ],
                'criteria': [
                    'Generalizability across contexts',
                    'Replication of key findings',
                    'Maintained effect sizes'
                ]
            },
            'construct_validation': {
                'methods': [
                    'Convergent validity testing',
                    'Discriminant validity testing',
                    'Factor analysis',
                    'Content validity assessment'
                ],
                'criteria': [
                    'Strong correlations with related measures',
                    'Weak correlations with unrelated measures',
                    'Theoretical consistency'
                ]
            },
            'statistical_validation': {
                'power_analysis': 'Minimum 80% power to detect medium effect size',
                'multiple_testing_correction': 'Bonferroni or FDR correction',
                'effect_size_reporting': 'Cohen\'s d or eta-squared',
                'confidence_intervals': '95% confidence intervals for all estimates'
            }
        }
        
        # Add hypothesis-specific validation
        if hypotheses:
            protocols['hypothesis_specific'] = []
            for i, hyp in enumerate(hypotheses[:2]):
                statement = hyp.get('statement', str(hyp))
                protocols['hypothesis_specific'].append({
                    'hypothesis': statement,
                    'primary_validation': 'Randomized controlled comparison',
                    'secondary_validation': 'Propensity score matching',
                    'null_hypothesis': f'No significant difference in outcomes',
                    'alternative_hypothesis': f'Significant improvement demonstrated'
                })
        
        return protocols
    
    def _create_resource_plan(self, methodology: dict, framework: dict) -> dict:
        """Create comprehensive resource planning"""
        
        phases = framework.get('phases', [])
        total_duration = sum(phase.get('duration_weeks', 4) for phase in phases)
        
        resource_plan = {
            'timeline': {
                'total_duration_weeks': max(total_duration, 24),  # Minimum 24 weeks
                'preparation_phase': '4 weeks',
                'execution_phase': f'{total_duration} weeks',
                'analysis_phase': '8 weeks',
                'dissemination_phase': '6 weeks'
            },
            'personnel': {
                'principal_investigator': {
                    'effort_percentage': 25,
                    'responsibilities': ['Overall project management', 'Data analysis', 'Report writing']
                },
                'research_coordinator': {
                    'effort_percentage': 50,
                    'responsibilities': ['Participant recruitment', 'Data collection', 'Quality assurance']
                },
                'data_analyst': {
                    'effort_percentage': 30,
                    'responsibilities': ['Statistical analysis', 'Data visualization', 'Results interpretation']
                },
                'domain_expert': {
                    'effort_percentage': 15,
                    'responsibilities': ['Methodology review', 'Results validation', 'Clinical guidance']
                }
            },
            'budget_estimate': {
                'personnel_costs': '$120,000 - $180,000',
                'equipment_software': '$15,000 - $25,000',
                'participant_incentives': '$8,000 - $15,000',
                'data_collection_costs': '$10,000 - $20,000',
                'dissemination_costs': '$5,000 - $10,000',
                'total_range': '$158,000 - $250,000'
            },
            'equipment_software': [
                'Statistical software licenses (R, SPSS, or SAS)',
                'Survey platform subscriptions',
                'Data storage and backup systems',
                'Analysis computing resources',
                'Measurement instruments and devices'
            ],
            'infrastructure': {
                'data_management': 'Secure cloud-based system with backup',
                'participant_space': 'Private rooms for interviews/assessments',
                'technology_requirements': 'High-speed internet, video conferencing',
                'ethics_compliance': 'IRB approval and ongoing monitoring'
            },
            'risk_management': {
                'low_recruitment': 'Multiple recruitment channels, extended timeline',
                'high_attrition': 'Over-recruitment by 20%, enhanced engagement',
                'data_quality_issues': 'Pilot testing, regular quality checks',
                'technical_failures': 'Backup systems, vendor support contracts'
            }
        }
        
        return resource_plan
    
    def _generate_methodology_report(self, query: str, methodology: dict, 
                                   framework: dict, protocols: dict, resources: dict) -> str:
        """Generate comprehensive methodology report"""
        
        report_parts = [
            f"# 🔬 Comprehensive Research Methodology",
            f"## Research Question: {query}",
            f"*Generated: {datetime.now().strftime('%B %d, %Y')}*",
            "",
            "## 🎯 Research Design Overview",
            f"**Design Type**: {methodology.get('research_design', 'Mixed-methods approach')}",
            f"**Data Collection**: {methodology.get('data_collection', 'Multi-modal data collection strategy')}",
            f"**Analysis Plan**: {methodology.get('analysis_plan', 'Comprehensive statistical analysis')}",
            "",
            "## 📋 Experimental Framework",
        ]
        
        # Add phases
        phases = framework.get('phases', [])
        if phases:
            report_parts.extend([
                f"**Study Phases**: {len(phases)} sequential phases",
                f"**Total Duration**: {sum(p.get('duration_weeks', 4) for p in phases)} weeks",
                ""
            ])
            
            for phase in phases[:2]:  # Show first 2 phases
                report_parts.extend([
                    f"### Phase {phase.get('phase_number', 1)}",
                    f"- **Hypothesis**: {phase.get('hypothesis_tested', 'Primary research question')}",
                    f"- **Duration**: {phase.get('duration_weeks', 4)} weeks",
                    f"- **Key Activities**: {', '.join(phase.get('activities', [])[:3])}",
                    ""
                ])
        
        # Add validation protocols
        report_parts.extend([
            "## ✅ Validation Protocols",
            "**Internal Validation**:",
            f"- {', '.join(protocols.get('internal_validation', {}).get('methods', [])[:2])}",
            "",
            "**External Validation**:",
            f"- {', '.join(protocols.get('external_validation', {}).get('methods', [])[:2])}",
            "",
        ])
        
        # Add resource requirements
        timeline = resources.get('timeline', {})
        budget = resources.get('budget_estimate', {})
        report_parts.extend([
            "## 📊 Resource Requirements",
            f"**Timeline**: {timeline.get('total_duration_weeks', 24)} weeks total",
            f"**Budget Range**: {budget.get('total_range', '$150,000 - $250,000')}",
            f"**Team Size**: {len(resources.get('personnel', {}))} key personnel",
            "",
            "## 🎯 Expected Outcomes",
            "- Validated research hypotheses with statistical significance",
            "- Replicable methodology for future studies",
            "- Actionable insights for practical implementation",
            "- High-impact publication opportunities",
            "",
            "## 📈 Success Metrics",
            "- **Statistical Power**: ≥80% power to detect medium effect size",
            "- **Participant Retention**: ≥80% completion rate",
            "- **Data Quality**: ≥95% complete data collection",
            "- **Publication Goal**: 2-3 peer-reviewed articles"
        ])
        
        return "\n".join(report_parts)
    
    def _fallback_experimental_framework(self, themes: list) -> dict:
        """Fallback experimental framework"""
        theme = themes[0] if themes else "research topic"
        
        return {
            'study_design': 'Mixed-methods exploratory study',
            'phases': [
                {
                    'phase_number': 1,
                    'hypothesis_tested': f'Investigation of {theme} effectiveness',
                    'duration_weeks': 8,
                    'activities': ['Literature review', 'Data collection', 'Analysis'],
                    'success_criteria': ['Complete data collection', 'Meaningful insights generated']
                }
            ],
            'variables': {
                'independent': [f'{theme} implementation'],
                'dependent': ['Performance outcomes'],
                'control': ['Baseline measures']
            },
            'measurement_instruments': ['Surveys', 'Interviews', 'Performance metrics']
        }
    
    def _add_fallback_methodology(self, state, query: str, themes: list, gaps: list) -> dict:
        """Add fallback methodology when design fails"""
        theme = themes[0] if themes else "the research area"
        
        fallback_methodology = {
            'research_design': f'Exploratory study of {theme}',
            'data_collection': 'Multi-method data collection approach',
            'analysis_plan': 'Descriptive and inferential statistical analysis',
            'timeline': '6-12 month study duration'
        }
        
        state['research_methodology'] = fallback_methodology
        state['experimental_framework'] = self._fallback_experimental_framework(themes)
        state['validation_protocols'] = {'note': 'Basic validation protocols'}
        state['resource_plan'] = {'budget': 'Standard research budget required'}
        state['methodology_report'] = f"Fallback methodology designed for {query}"
        state['methodology_design_completed'] = True
        
        return state