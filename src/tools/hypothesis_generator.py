"""
Enhanced Hypothesis generation tool with experimental design capabilities - FIXED
"""
from loguru import logger
from utils.llm_config import llm_config
from langchain_core.prompts import ChatPromptTemplate
import json
import re

class HypothesisGenerator:
    def __init__(self, llm=None):
        self.llm = llm or llm_config.get_primary_llm()
    
    def generate_hypotheses(self, state):
        """Generate hypotheses with experimental designs based on analysis results"""
        logger.info("Generating research hypotheses with experimental designs...")
        
        # Extract relevant information from state
        query = state.get('query', '')
        themes = state.get('key_themes', [])
        gaps = state.get('research_gaps', [])
        papers = state.get('papers_found', [])
        contradictions = state.get('contradictions', [])
        
        # Prepare enhanced context with better error handling
        themes_str = self._extract_themes_string(themes)
        gaps_str = self._extract_gaps_string(gaps)
        contradictions_str = self._extract_contradictions_string(contradictions)
        
        # Enhanced prompt for hypothesis generation
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a senior research scientist specializing in generating innovative, 
            testable hypotheses and designing rigorous experimental approaches based on literature analysis.
            Your hypotheses should be specific, falsifiable, and address important research gaps.
            
            IMPORTANT: Return ONLY a valid JSON array. Do not include any text before or after the JSON."""),
            ("human", """
            Based on the following research context, generate 3-4 testable research hypotheses with detailed experimental designs.

            RESEARCH QUERY: {query}
            KEY THEMES: {themes}
            RESEARCH GAPS: {gaps}
            CONTRADICTIONS: {contradictions}

            For each hypothesis, provide a JSON object with these exact fields:
            - "statement": A clear, specific hypothesis statement
            - "rationale": Brief rationale linking it to the literature
            - "experimental_design": An experimental design to test the hypothesis
            - "required_resources": Required resources and methodologies
            - "expected_outcomes": Expected outcomes and potential implications
            - "testability": Testability assessment (High/Medium/Low)

            Return only a JSON array of these objects, nothing else.
            """)
        ])
        
        try:
            # Use LLM to generate hypotheses
            chain = prompt | self.llm
            response = chain.invoke({
                "query": query,
                "themes": themes_str,
                "gaps": gaps_str,
                "contradictions": contradictions_str
            })
            
            # Parse response with better error handling
            hypotheses = self._parse_enhanced_hypothesis_response(response.content)
            
            if not hypotheses or len(hypotheses) == 0:
                logger.warning("LLM returned empty hypotheses, using fallback")
                return self._generate_fallback_hypotheses(query, themes, gaps)
            
            return hypotheses
            
        except Exception as e:
            logger.error(f"Failed to generate hypotheses with LLM: {e}")
            return self._generate_fallback_hypotheses(query, themes, gaps)
    
    def _extract_themes_string(self, themes):
        """Safely extract themes string"""
        if not themes:
            return "No specific themes identified"
        
        theme_strs = []
        for theme in themes[:3]:
            if isinstance(theme, dict):
                theme_name = theme.get('theme', 'Unknown theme')
                trajectory = theme.get('trajectory', '')
                if trajectory:
                    theme_strs.append(f"{theme_name} ({trajectory})")
                else:
                    theme_strs.append(theme_name)
            elif isinstance(theme, str):
                theme_strs.append(theme)
            else:
                theme_strs.append(str(theme))
        
        return ", ".join(theme_strs) if theme_strs else "General research themes"
    
    def _extract_gaps_string(self, gaps):
        """Safely extract gaps string"""
        if not gaps:
            return "No specific gaps identified"
        
        gap_strs = []
        for gap in gaps[:3]:
            if isinstance(gap, dict):
                desc = gap.get('description', 'Unknown gap')
                impact = gap.get('impact', '')
                if impact:
                    gap_strs.append(f"- {desc} (Impact: {impact})")
                else:
                    gap_strs.append(f"- {desc}")
            elif isinstance(gap, str):
                gap_strs.append(f"- {gap}")
            else:
                gap_strs.append(f"- {str(gap)}")
        
        return "\n".join(gap_strs) if gap_strs else "- General research limitations identified"
    
    def _extract_contradictions_string(self, contradictions):
        """Safely extract contradictions string"""
        if not contradictions:
            return "No major contradictions identified"
        
        contr_strs = []
        for contradiction in contradictions[:2]:
            if isinstance(contradiction, dict):
                contr = contradiction.get('contradiction', 'Unknown contradiction')
                contr_strs.append(f"- {contr}")
            elif isinstance(contradiction, str):
                contr_strs.append(f"- {contradiction}")
            else:
                contr_strs.append(f"- {str(contradiction)}")
        
        return "\n".join(contr_strs) if contr_strs else "- No major contradictions identified"
    
    def _parse_enhanced_hypothesis_response(self, response):
        """Parse enhanced hypothesis response with experimental designs - FIXED"""
        try:
            # Clean the response
            response = response.strip()
            
            # Try to find JSON array in the response
            json_match = re.search(r'\[[\s\S]*\]', response)
            if json_match:
                json_str = json_match.group()
                parsed = json.loads(json_str)
                
                # Validate the structure
                if isinstance(parsed, list) and len(parsed) > 0:
                    # Ensure each hypothesis has the required fields
                    validated_hypotheses = []
                    for hyp in parsed:
                        if isinstance(hyp, dict):
                            validated_hyp = self._validate_hypothesis_structure(hyp)
                            if validated_hyp:
                                validated_hypotheses.append(validated_hyp)
                    
                    if validated_hypotheses:
                        return validated_hypotheses
            
            # If JSON parsing fails, try to extract from text
            return self._parse_hypotheses_from_text(response)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return self._parse_hypotheses_from_text(response)
        except Exception as e:
            logger.error(f"Failed to parse hypothesis response: {e}")
            return None
    
    def _validate_hypothesis_structure(self, hyp_dict):
        """Validate and fix hypothesis structure"""
        required_fields = ['statement', 'rationale', 'experimental_design', 'required_resources', 'expected_outcomes', 'testability']
        
        validated = {}
        for field in required_fields:
            if field in hyp_dict and hyp_dict[field]:
                validated[field] = str(hyp_dict[field])
            else:
                # Provide default values for missing fields
                if field == 'statement':
                    validated[field] = "Research hypothesis requires further specification"
                elif field == 'rationale':
                    validated[field] = "Based on literature analysis"
                elif field == 'experimental_design':
                    validated[field] = "Empirical study with appropriate controls"
                elif field == 'required_resources':
                    validated[field] = "Research team and standard laboratory resources"
                elif field == 'expected_outcomes':
                    validated[field] = "Significant findings supporting the hypothesis"
                elif field == 'testability':
                    validated[field] = "Medium"
        
        return validated if validated.get('statement') != "Research hypothesis requires further specification" else None
    
    def _parse_hypotheses_from_text(self, text):
        """Parse hypotheses from unstructured text - IMPROVED"""
        hypotheses = []
        lines = text.split('\n')
        current_hyp = {}
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for hypothesis indicator
            if re.match(r'^(Hypothesis|H)\s*\d*[:.-]', line, re.IGNORECASE):
                if current_hyp and current_hyp.get('statement'):
                    hypotheses.append(self._validate_hypothesis_structure(current_hyp))
                current_hyp = {"statement": re.sub(r'^(Hypothesis|H)\s*\d*[:.-]\s*', '', line, flags=re.IGNORECASE)}
                current_section = None
            
            # Check for section indicators
            elif re.match(r'^(Rationale|Reasoning|Basis)[:.-]', line, re.IGNORECASE):
                current_section = "rationale"
                content = re.sub(r'^(Rationale|Reasoning|Basis)[:.-]\s*', '', line, flags=re.IGNORECASE)
                if content:
                    current_hyp["rationale"] = content
            elif re.match(r'^(Design|Method|Experimental Design)[:.-]', line, re.IGNORECASE):
                current_section = "experimental_design"
                content = re.sub(r'^(Design|Method|Experimental Design)[:.-]\s*', '', line, flags=re.IGNORECASE)
                if content:
                    current_hyp["experimental_design"] = content
            elif re.match(r'^(Resources|Materials|Required)[:.-]', line, re.IGNORECASE):
                current_section = "required_resources"
                content = re.sub(r'^(Resources|Materials|Required)[:.-]\s*', '', line, flags=re.IGNORECASE)
                if content:
                    current_hyp["required_resources"] = content
            elif re.match(r'^(Outcomes|Expectations|Predictions)[:.-]', line, re.IGNORECASE):
                current_section = "expected_outcomes"
                content = re.sub(r'^(Outcomes|Expectations|Predictions)[:.-]\s*', '', line, flags=re.IGNORECASE)
                if content:
                    current_hyp["expected_outcomes"] = content
            elif re.match(r'^(Testability|Testable|Feasibility)[:.-]', line, re.IGNORECASE):
                current_section = "testability"
                content = re.sub(r'^(Testability|Testable|Feasibility)[:.-]\s*', '', line, flags=re.IGNORECASE)
                if content:
                    current_hyp["testability"] = content
            
            # Add to current section
            elif current_section and current_hyp and line:
                if current_section in current_hyp:
                    current_hyp[current_section] += " " + line
                else:
                    current_hyp[current_section] = line
        
        # Add the last hypothesis
        if current_hyp and current_hyp.get('statement'):
            validated = self._validate_hypothesis_structure(current_hyp)
            if validated:
                hypotheses.append(validated)
        
        # Filter out None values and return
        valid_hypotheses = [h for h in hypotheses if h is not None]
        return valid_hypotheses if valid_hypotheses else None
    
    def _generate_fallback_hypotheses(self, query, themes, gaps):
        """Generate fallback hypotheses when LLM fails - IMPROVED"""
        # Extract meaningful information for fallback
        theme_text = "the research area"
        if themes:
            first_theme = themes[0]
            if isinstance(first_theme, dict):
                theme_text = first_theme.get('theme', 'the research area')
            elif isinstance(first_theme, str):
                theme_text = first_theme
        
        gap_text = "current limitations in the field"
        if gaps:
            first_gap = gaps[0]
            if isinstance(first_gap, dict):
                gap_text = first_gap.get('description', 'current limitations')
            elif isinstance(first_gap, str):
                gap_text = first_gap
        
        # Create domain-specific hypotheses
        domain_keywords = query.lower().split()
        is_ml_related = any(word in domain_keywords for word in ['machine', 'learning', 'neural', 'ai', 'algorithm'])
        is_medical = any(word in domain_keywords for word in ['medical', 'clinical', 'health', 'diagnosis', 'treatment'])
        is_tech_related = any(word in domain_keywords for word in ['blockchain', 'technology', 'software', 'system'])
        
        fallback_hypotheses = []
        
        # Hypothesis 1: Improvement hypothesis
        fallback_hypotheses.append({
            "statement": f"Implementing advanced approaches in {theme_text} will significantly improve outcomes compared to traditional methods",
            "rationale": f"Literature analysis suggests that current approaches have limitations in addressing {gap_text}. Advanced methodologies show promise for overcoming these challenges",
            "experimental_design": "Randomized controlled trial comparing advanced approach with standard practice, measuring primary and secondary outcomes over appropriate follow-up period",
            "required_resources": "Research team including domain experts, participant recruitment infrastructure, measurement instruments, statistical analysis software, funding for personnel and materials",
            "expected_outcomes": "Statistically significant improvement in primary outcomes (p<0.05) with moderate to large effect size (Cohen's d ≥ 0.5), secondary benefits in related measures",
            "testability": "High"
        })
        
        # Hypothesis 2: Integration hypothesis
        integration_approach = "multi-modal" if is_ml_related else "interdisciplinary" if is_medical else "integrated systems"
        fallback_hypotheses.append({
            "statement": f"A {integration_approach} approach will provide more comprehensive solutions than single-method approaches in {query}",
            "rationale": "Current research often employs isolated methodologies. Integration of multiple approaches may address limitations of individual methods and provide synergistic benefits",
            "experimental_design": "Mixed-methods study combining quantitative measurements with qualitative assessments, using before-after design with multiple treatment arms",
            "required_resources": "Multidisciplinary research team, diverse measurement tools, qualitative analysis software, training in mixed-methods approaches",
            "expected_outcomes": "Enhanced understanding of complex phenomena, identification of contextual factors, improved predictive accuracy, and more robust findings",
            "testability": "Medium"
        })
        
        # Add domain-specific hypothesis
        if is_ml_related:
            fallback_hypotheses.append({
                "statement": f"Deep learning models will outperform traditional machine learning approaches for {query} tasks",
                "rationale": "Deep learning has shown superior performance in many domains due to its ability to learn complex patterns and representations from data",
                "experimental_design": "Comparative study using standardized datasets, cross-validation methodology, multiple performance metrics",
                "required_resources": "Computing infrastructure, labeled datasets, deep learning frameworks, model evaluation tools",
                "expected_outcomes": "Significant improvement in accuracy, precision, recall, and F1-score compared to baseline methods",
                "testability": "High"
            })
        elif is_medical:
            fallback_hypotheses.append({
                "statement": f"Early intervention strategies will improve long-term outcomes in {query}",
                "rationale": "Medical literature consistently shows that early detection and intervention lead to better patient outcomes across many conditions",
                "experimental_design": "Longitudinal cohort study comparing early intervention group with standard care, measuring outcomes at multiple time points",
                "required_resources": "Clinical sites, patient recruitment, medical expertise, long-term follow-up infrastructure",
                "expected_outcomes": "Improved clinical outcomes, reduced complications, enhanced quality of life measures",
                "testability": "High"
            })
        elif is_tech_related:
            fallback_hypotheses.append({
                "statement": f"Implementation of {theme_text} will increase system efficiency and user satisfaction",
                "rationale": "Technology implementations typically aim to improve efficiency and user experience, with measurable impacts on performance metrics",
                "experimental_design": "Before-after implementation study with control groups, measuring system performance and user satisfaction metrics",
                "required_resources": "Technology infrastructure, user testing facilities, performance monitoring tools, survey instruments",
                "expected_outcomes": "Measurable improvements in system performance, increased user satisfaction scores, reduced processing time",
                "testability": "High"
            })
        
        return fallback_hypotheses