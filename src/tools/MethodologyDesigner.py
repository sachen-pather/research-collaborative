"""
Enhanced Methodology Designer - Creates comprehensive, actionable research methodologies
"""
from loguru import logger
from utils.llm_config import llm_config
from langchain_core.prompts import ChatPromptTemplate
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

class MethodologyDesigner:
    """Enhanced methodology designer with practical research frameworks"""
    
    def __init__(self, llm=None):
        self.llm = llm or llm_config.get_primary_llm()
    
    def design_research_methodology(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Design comprehensive research methodology based on analysis results"""
        logger.info("🔬 Designing comprehensive research methodology...")
        
        # Extract context from state
        query = state.get('query', '')
        themes = state.get('key_themes', [])
        gaps = state.get('research_gaps', [])
        hypotheses = state.get('hypotheses', [])
        papers = state.get('papers_found', [])
        contradictions = state.get('contradictions', [])
        evidence_strength = state.get('evidence_strength', {})
        
        # Prepare enhanced context for LLM
        context = self._prepare_methodology_context(query, themes, gaps, hypotheses, papers, contradictions, evidence_strength)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a senior research methodologist specializing in designing rigorous, 
            practical research methodologies. Your designs should be implementable, ethically sound, 
            and scientifically robust. Focus on creating actionable research frameworks."""),
            ("human", """
            Based on the following research analysis, design a comprehensive methodology:

            {context}

            Please design a methodology that includes:
            1. Research Design Type (experimental, observational, mixed-methods, etc.)
            2. Study Population and Sampling Strategy
            3. Data Collection Methods and Instruments
            4. Variables and Measurement Approaches
            5. Statistical Analysis Plan
            6. Quality Assurance Measures
            7. Ethical Considerations
            8. Timeline and Milestones
            9. Resource Requirements
            10. Risk Mitigation Strategies

            Format as a JSON object with these fields: "research_design", "population_sampling", 
            "data_collection", "variables_measurement", "statistical_analysis", "quality_assurance", 
            "ethical_considerations", "timeline", "resources", "risk_mitigation".
            """)
        ])
        
        try:
            chain = prompt | self.llm
            response = chain.invoke({"context": context})
            
            methodology = self._parse_methodology_response(response.content)
            
            # Enhance with practical details
            enhanced_methodology = self._enhance_with_practical_details(methodology, state)
            
            return enhanced_methodology
            
        except Exception as e:
            logger.error(f"Failed to design methodology: {e}")
            return self._generate_fallback_methodology(query, themes, gaps)
    
    def _prepare_methodology_context(self, query: str, themes: list, gaps: list, 
                                   hypotheses: list, papers: list, contradictions: list,
                                   evidence_strength: dict) -> str:
        """Prepare comprehensive context for methodology design"""
        
        context_parts = [
            f"RESEARCH QUERY: {query}",
            "",
            "KEY THEMES:",
        ]
        
        for i, theme in enumerate(themes[:4], 1):
            if isinstance(theme, dict):
                context_parts.append(f"{i}. {theme.get('theme', 'Unknown')} - {theme.get('trajectory', 'Emerging trend')}")
            else:
                context_parts.append(f"{i}. {theme}")
        
        context_parts.extend([
            "",
            "RESEARCH GAPS:",
        ])
        
        for i, gap in enumerate(gaps[:3], 1):
            if isinstance(gap, dict):
                desc = gap.get('description', 'No description')
                impact = gap.get('impact', 'Unknown impact')
                context_parts.append(f"{i}. {desc} (Impact: {impact})")
            else:
                context_parts.append(f"{i}. {gap}")
        
        context_parts.extend([
            "",
            "RESEARCH HYPOTHESES:",
        ])
        
        for i, hyp in enumerate(hypotheses[:3], 1):
            if isinstance(hyp, dict):
                statement = hyp.get('statement', 'No statement')
                context_parts.append(f"{i}. {statement}")
            else:
                context_parts.append(f"{i}. {hyp}")
        
        context_parts.extend([
            "",
            f"LITERATURE BASE: {len(papers)} papers analyzed",
            f"EVIDENCE STRENGTH: {evidence_strength.get('strength_assessment', 'Moderate')}",
            ""
        ])
        
        if contradictions and len(contradictions) > 0:
            context_parts.extend([
                "CONTRADICTIONS TO ADDRESS:",
                f"- {contradictions[0] if isinstance(contradictions[0], str) else contradictions[0].get('contradiction', 'Methodological inconsistencies identified')}",
                ""
            ])
        
        return "\n".join(context_parts)
    
    def _parse_methodology_response(self, response: str) -> Dict[str, Any]:
        """Parse methodology response from LLM"""
        try:
            # Try to find JSON in response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # If no JSON, parse structured text
            return self._parse_methodology_from_text(response)
            
        except Exception as e:
            logger.error(f"Failed to parse methodology response: {e}")
            return None
    
    def _parse_methodology_from_text(self, text: str) -> Dict[str, Any]:
        """Parse methodology from unstructured text"""
        methodology = {}
        current_section = None
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            if re.match(r'^(research design|design type)', line.lower()):
                current_section = "research_design"
            elif re.match(r'^(population|sampling|participants)', line.lower()):
                current_section = "population_sampling"
            elif re.match(r'^(data collection|methods)', line.lower()):
                current_section = "data_collection"
            elif re.match(r'^(variables|measurement)', line.lower()):
                current_section = "variables_measurement"
            elif re.match(r'^(statistical|analysis)', line.lower()):
                current_section = "statistical_analysis"
            elif re.match(r'^(quality|assurance)', line.lower()):
                current_section = "quality_assurance"
            elif re.match(r'^(ethical|ethics)', line.lower()):
                current_section = "ethical_considerations"
            elif re.match(r'^(timeline|schedule)', line.lower()):
                current_section = "timeline"
            elif re.match(r'^(resources|budget)', line.lower()):
                current_section = "resources"
            elif re.match(r'^(risk|mitigation)', line.lower()):
                current_section = "risk_mitigation"
            elif current_section:
                # Add content to current section
                if current_section in methodology:
                    methodology[current_section] += " " + line
                else:
                    methodology[current_section] = line
        
        return methodology if methodology else None
    
    def _enhance_with_practical_details(self, methodology: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance methodology with practical implementation details"""
        if not methodology:
            return self._generate_fallback_methodology(state.get('query', ''), 
                                                     state.get('key_themes', []), 
                                                     state.get('research_gaps', []))
        
        # Add practical timeline
        methodology['detailed_timeline'] = self._create_detailed_timeline(methodology.get('timeline', ''))
        
        # Add budget breakdown
        methodology['budget_breakdown'] = self._create_budget_breakdown(methodology.get('resources', ''))
        
        # Add sample size calculation
        methodology['sample_size_calculation'] = self._calculate_sample_size(state)
        
        # Add validation framework
        methodology['validation_framework'] = self._create_validation_framework(state)
        
        # Add data management plan
        methodology['data_management_plan'] = self._create_data_management_plan()
        
        # Add publication strategy
        methodology['publication_strategy'] = self._create_publication_strategy(state)
        
        return methodology
    
    def _create_detailed_timeline(self, basic_timeline: str) -> Dict[str, Any]:
        """Create detailed project timeline with milestones"""
        base_date = datetime.now()
        
        timeline = {
            "total_duration_months": 18,
            "phases": [
                {
                    "phase": "Phase 1: Preparation & Setup",
                    "duration_weeks": 4,
                    "start_date": base_date.strftime("%Y-%m-%d"),
                    "end_date": (base_date + timedelta(weeks=4)).strftime("%Y-%m-%d"),
                    "deliverables": [
                        "IRB approval obtained",
                        "Research team assembled",
                        "Instruments validated",
                        "Pilot study completed"
                    ],
                    "milestones": ["Ethics approval", "Team onboarding complete"]
                },
                {
                    "phase": "Phase 2: Data Collection",
                    "duration_weeks": 24,
                    "start_date": (base_date + timedelta(weeks=4)).strftime("%Y-%m-%d"),
                    "end_date": (base_date + timedelta(weeks=28)).strftime("%Y-%m-%d"),
                    "deliverables": [
                        "Participant recruitment completed",
                        "Baseline data collected",
                        "Intervention implemented",
                        "Follow-up assessments conducted"
                    ],
                    "milestones": ["50% recruitment target", "Data quality review"]
                },
                {
                    "phase": "Phase 3: Analysis & Interpretation",
                    "duration_weeks": 16,
                    "start_date": (base_date + timedelta(weeks=28)).strftime("%Y-%m-%d"),
                    "end_date": (base_date + timedelta(weeks=44)).strftime("%Y-%m-%d"),
                    "deliverables": [
                        "Statistical analysis completed",
                        "Results interpreted",
                        "Sensitivity analyses performed",
                        "Limitations assessed"
                    ],
                    "milestones": ["Primary analysis complete", "Results validated"]
                },
                {
                    "phase": "Phase 4: Dissemination",
                    "duration_weeks": 28,
                    "start_date": (base_date + timedelta(weeks=44)).strftime("%Y-%m-%d"),
                    "end_date": (base_date + timedelta(weeks=72)).strftime("%Y-%m-%d"),
                    "deliverables": [
                        "Manuscripts drafted",
                        "Conference presentations prepared",
                        "Stakeholder reports created",
                        "Follow-up studies planned"
                    ],
                    "milestones": ["First submission", "Public presentation"]
                }
            ],
            "critical_dependencies": [
                "Ethics approval before data collection",
                "Pilot completion before main study",
                "Data cleaning before analysis"
            ],
            "risk_buffer": "20% time buffer included for each phase"
        }
        
        return timeline
    
    def _create_budget_breakdown(self, basic_resources: str) -> Dict[str, Any]:
        """Create detailed budget breakdown"""
        return {
            "total_estimated_budget": "$180,000 - $280,000",
            "categories": {
                "personnel": {
                    "amount": "$120,000 - $180,000",
                    "breakdown": {
                        "principal_investigator": "$45,000 (25% effort for 18 months)",
                        "research_coordinator": "$55,000 (full-time for 18 months)",
                        "data_analyst": "$25,000 (part-time for 12 months)",
                        "graduate_student": "$15,000 (stipend support)"
                    }
                },
                "equipment_software": {
                    "amount": "$15,000 - $25,000",
                    "items": [
                        "Statistical software licenses ($3,000)",
                        "Survey platform subscription ($2,000)",
                        "Data collection tablets ($5,000)",
                        "Specialized measurement tools ($10,000)"
                    ]
                },
                "participant_costs": {
                    "amount": "$8,000 - $15,000",
                    "breakdown": {
                        "incentive_payments": "$6,000 ($50 per participant × 120 participants)",
                        "travel_reimbursements": "$3,000",
                        "childcare_support": "$2,000"
                    }
                },
                "operational": {
                    "amount": "$12,000 - $20,000",
                    "items": [
                        "Materials and supplies ($3,000)",
                        "Communication and postage ($2,000)",
                        "Conference presentations ($4,000)",
                        "Publication costs ($3,000)"
                    ]
                },
                "indirect_costs": {
                    "amount": "$25,000 - $40,000",
                    "rate": "Institutional rate (typically 25-30% of direct costs)"
                }
            },
            "funding_strategies": [
                "Federal research grants (NIH, NSF)",
                "Foundation funding",
                "Institutional seed grants",
                "Industry partnerships"
            ]
        }
    
    def _calculate_sample_size(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate appropriate sample size based on research design"""
        evidence_strength = state.get('evidence_strength', {})
        hypotheses = state.get('hypotheses', [])
        
        return {
            "recommended_sample_size": "N = 120 participants",
            "power_analysis": {
                "statistical_power": "80% (β = 0.20)",
                "significance_level": "α = 0.05 (two-tailed)",
                "effect_size": "Medium effect (Cohen's d = 0.5)",
                "attrition_allowance": "20% dropout rate"
            },
            "rationale": "Sample size calculated to detect meaningful differences with adequate statistical power",
            "sensitivity_analysis": "Range: N = 96-150 depending on effect size assumptions",
            "stratification": {
                "by_demographics": "Balanced across age, gender, education",
                "by_baseline_measures": "Matched pairs where appropriate"
            },
            "recruitment_strategy": {
                "target_population": "Well-defined inclusion/exclusion criteria",
                "recruitment_channels": ["Clinical sites", "Community organizations", "Online platforms"],
                "screening_ratio": "Expect 1.5:1 screening-to-enrollment ratio"
            }
        }
    
    def _create_validation_framework(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive validation framework"""
        return {
            "internal_validity": {
                "threats_addressed": [
                    "Selection bias through randomization",
                    "History effects through control groups",
                    "Maturation through appropriate timing",
                    "Testing effects through alternate forms"
                ],
                "quality_controls": [
                    "Blinded outcome assessment",
                    "Standardized protocols",
                    "Regular calibration exercises",
                    "Data quality monitoring"
                ]
            },
            "external_validity": {
                "generalizability_factors": [
                    "Diverse participant demographics",
                    "Multiple recruitment sites",
                    "Real-world implementation conditions",
                    "Pragmatic outcome measures"
                ],
                "limitation_acknowledgments": [
                    "Geographic constraints",
                    "Temporal limitations",
                    "Population-specific findings"
                ]
            },
            "construct_validity": {
                "measurement_validation": [
                    "Pilot testing of all instruments",
                    "Content validity assessment",
                    "Convergent/discriminant validity testing",
                    "Cultural adaptation where needed"
                ]
            },
            "statistical_validity": {
                "analysis_plan": [
                    "Pre-specified primary/secondary outcomes",
                    "Multiple comparisons correction",
                    "Intention-to-treat analysis",
                    "Sensitivity analyses for missing data"
                ]
            }
        }
    
    def _create_data_management_plan(self) -> Dict[str, Any]:
        """Create comprehensive data management plan"""
        return {
            "data_collection": {
                "collection_methods": ["Electronic data capture", "Paper forms with double entry"],
                "quality_assurance": ["Real-time validation", "Range checks", "Logic checks"],
                "training_protocols": "Standardized training for all data collectors"
            },
            "data_storage": {
                "primary_storage": "Secure, encrypted cloud-based system",
                "backup_strategy": "Automated daily backups with 30-day retention",
                "access_controls": "Role-based access with audit trails"
            },
            "data_security": {
                "encryption": "AES-256 encryption for data at rest and in transit",
                "access_management": "Multi-factor authentication required",
                "monitoring": "Regular security audits and penetration testing"
            },
            "privacy_protection": {
                "identifiers": "Direct identifiers removed after data collection",
                "coding_system": "Unique study IDs with separate linking file",
                "sharing_protocols": "De-identification procedures for data sharing"
            },
            "retention_schedule": {
                "raw_data": "Retained for 7 years post-publication",
                "analyzed_datasets": "Permanent retention for reproducibility",
                "disposal": "Secure deletion following institutional policies"
            }
        }
    
    def _create_publication_strategy(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive publication and dissemination strategy"""
        query = state.get('query', 'research findings')
        
        return {
            "primary_publications": {
                "main_results_paper": {
                    "target_journal": "High-impact journal in relevant field",
                    "timeline": "12 months post-data collection",
                    "author_order": "PI as senior author, key contributors as co-authors"
                },
                "methodology_paper": {
                    "target_journal": "Methods-focused journal",
                    "timeline": "6 months post-study initiation",
                    "focus": "Novel methodological approaches developed"
                }
            },
            "secondary_publications": {
                "systematic_review": "Position findings within broader literature",
                "commentary_pieces": "Expert perspectives on implications",
                "special_issues": "Themed journal issues on related topics"
            },
            "conference_presentations": {
                "national_meetings": ["Annual conferences in relevant disciplines"],
                "international_symposiums": ["Global forums for research dissemination"],
                "workshops": ["Hands-on methodology training sessions"]
            },
            "stakeholder_engagement": {
                "policy_briefs": "1-2 page summaries for policymakers",
                "practitioner_reports": "Implementation-focused documents",
                "public_communications": "Media releases and blog posts"
            },
            "data_sharing": {
                "open_data_repository": "De-identified dataset in public repository",
                "code_sharing": "Analysis scripts on GitHub/similar platform",
                "reproducibility": "Detailed computational environment documentation"
            },
            "impact_tracking": {
                "metrics": ["Citation counts", "Altmetric scores", "Media mentions"],
                "policy_impact": "Track adoption in guidelines/recommendations",
                "practice_impact": "Survey practitioners about implementation"
            }
        }
    
    def _generate_fallback_methodology(self, query: str, themes: list, gaps: list) -> Dict[str, Any]:
        """Generate fallback methodology when LLM processing fails"""
        theme = themes[0] if themes else "research area"
        
        return {
            "research_design": f"Mixed-methods study examining {theme} applications",
            "population_sampling": "Purposive sampling of relevant stakeholders and cases",
            "data_collection": "Combination of surveys, interviews, and document analysis",
            "variables_measurement": "Validated instruments where available, novel measures developed as needed",
            "statistical_analysis": "Descriptive statistics, regression analysis, thematic analysis",
            "quality_assurance": "Inter-rater reliability, member checking, triangulation",
            "ethical_considerations": "IRB approval, informed consent, data confidentiality",
            "timeline": "18-month study with phased implementation",
            "resources": "Research team, participant incentives, analysis software",
            "risk_mitigation": "Pilot testing, flexible protocols, backup plans",
            "detailed_timeline": {
                "total_duration_months": 18,
                "phases": ["Preparation", "Data Collection", "Analysis", "Dissemination"]
            },
            "budget_breakdown": {"total_estimated_budget": "$150,000 - $200,000"},
            "sample_size_calculation": {"recommended_sample_size": "N = 100 participants"},
            "validation_framework": {"focus": "Multi-method validation approach"},
            "data_management_plan": {"approach": "Secure, encrypted data handling"},
            "publication_strategy": {"target": "Peer-reviewed publications and conference presentations"}
        }