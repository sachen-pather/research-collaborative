"""
Enhanced Text analysis tool for LLM-powered text processing with advanced capabilities - FIXED
"""
from loguru import logger
from utils.llm_config import llm_config
from langchain_core.prompts import ChatPromptTemplate
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Union

class TextAnalyzer:
    def __init__(self, llm=None):
        self.llm = llm or llm_config.get_primary_llm()
    
    def extract_key_themes(self, papers, query):
        """Extract key themes from papers using LLM with enhanced context"""
        logger.info("Extracting key themes from papers...")
        
        if not papers or len(papers) == 0:
            logger.warning("No papers provided for theme extraction")
            return self._extract_fallback_themes(query, [])
        
        try:
            # Extract more comprehensive context including publication dates
            paper_context = "\n\n".join([
                f"Title: {p.get('title', 'Unknown')}\n"
                f"Published: {p.get('published_date', 'Unknown')}\n"
                f"Abstract: {p.get('abstract', 'No abstract')[:400]}..."
                for p in papers[:8]  # Use more papers for better context
            ])
            
            # Enhanced prompt for theme extraction
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a senior research analyst specializing in identifying emerging trends and key themes 
                across scientific literature. Your analysis should be specific, evidence-based, and forward-looking.
                
                IMPORTANT: Return ONLY a valid JSON array. Do not include any text before or after the JSON."""),
                ("human", """
                Based on the following research papers and the query "{query}", identify the 4-6 most significant research themes.

                PAPERS:
                {paper_context}

                For each theme, provide a JSON object with these exact fields:
                - "theme": A clear, specific theme statement
                - "evidence": Evidence from the papers supporting this theme
                - "trajectory": The apparent trajectory or development of this theme (e.g., "Emerging", "Mature", "Growing")

                Return only a JSON array of these objects, nothing else.
                """)
            ])
            
            # Use LLM to extract themes
            chain = prompt | self.llm
            response = chain.invoke({
                "query": query,
                "paper_context": paper_context
            })
            
            # Parse response with better error handling
            parsed_response = self._parse_enhanced_response(response.content, "themes")

            # Validate the type of the parsed response
            if isinstance(parsed_response, list) and len(parsed_response) > 0:
                # Validate each theme has the required structure
                valid_themes = []
                for theme in parsed_response:
                    if isinstance(theme, dict) and 'theme' in theme:
                        valid_theme = self._validate_theme_structure(theme)
                        if valid_theme:
                            valid_themes.append(valid_theme)
                
                if valid_themes:
                    return valid_themes
            
            logger.warning(f"Parsed themes response was not valid (got {type(parsed_response)}). Using fallback.")
            return self._extract_fallback_themes(query, papers)
            
        except Exception as e:
            logger.error(f"Failed to extract themes with LLM: {e}")
            return self._extract_fallback_themes(query, papers)
    
    def _validate_theme_structure(self, theme_dict: dict) -> Union[dict, None]:
        """Validate and fix theme structure"""
        required_fields = ['theme', 'evidence', 'trajectory']
        
        validated = {}
        for field in required_fields:
            if field in theme_dict and theme_dict[field]:
                validated[field] = str(theme_dict[field])
            else:
                # Provide default values for missing fields
                if field == 'theme':
                    return None  # Theme is required
                elif field == 'evidence':
                    validated[field] = "Based on paper analysis"
                elif field == 'trajectory':
                    validated[field] = "Active research area"
        
        return validated if 'theme' in validated else None
        
    def extract_research_gaps(self, papers, query):
        """Identify research gaps using LLM with enhanced analysis"""
        logger.info("Identifying research gaps with enhanced analysis...")
        
        if not papers or len(papers) == 0:
            logger.warning("No papers provided for gap extraction")
            return self._extract_fallback_gaps(query, [])
        
        try:
            # Extract context with methodology information
            paper_context = "\n\n".join([
                f"Title: {p.get('title', 'Unknown')}\n"
                f"Methods: {self._extract_methodology_keywords(p.get('abstract', ''))}\n"
                f"Findings: {self._extract_key_findings(p.get('abstract', ''))}"
                for p in papers[:6]
            ])
            
            # Enhanced prompt for gap identification
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a research strategist specializing in identifying critical research gaps and 
                opportunities in scientific literature. Focus on methodological limitations, theoretical shortcomings, 
                and practical application barriers.
                
                IMPORTANT: Return ONLY a valid JSON array. Do not include any text before or after the JSON."""),
                ("human", """
                Based on the following research papers and the query "{query}", identify 3-5 significant research gaps.

                PAPERS:
                {paper_context}

                For each gap, provide a JSON object with these exact fields:
                - "description": A specific description of the gap
                - "impact": The potential impact of addressing this gap (High/Medium/Low)
                - "reason": Why this gap exists (methodological, theoretical, or practical reasons)
                - "suggested_approaches": Suggested approaches to address this gap

                Return only a JSON array of these objects, nothing else.
                """)
            ])
            
            # Use LLM to identify gaps
            chain = prompt | self.llm
            response = chain.invoke({
                "query": query,
                "paper_context": paper_context
            })
            
            # Parse response
            gaps = self._parse_enhanced_response(response.content, "gaps")
            
            if isinstance(gaps, list) and len(gaps) > 0:
                # Validate each gap structure
                valid_gaps = []
                for gap in gaps:
                    if isinstance(gap, dict) and 'description' in gap:
                        valid_gap = self._validate_gap_structure(gap)
                        if valid_gap:
                            valid_gaps.append(valid_gap)
                
                if valid_gaps:
                    return valid_gaps
            
            return self._extract_fallback_gaps(query, papers)
            
        except Exception as e:
            logger.error(f"Failed to identify gaps with LLM: {e}")
            return self._extract_fallback_gaps(query, papers)
    
    def _validate_gap_structure(self, gap_dict: dict) -> Union[dict, None]:
        """Validate and fix gap structure"""
        required_fields = ['description', 'impact', 'reason', 'suggested_approaches']
        
        validated = {}
        for field in required_fields:
            if field in gap_dict and gap_dict[field]:
                validated[field] = str(gap_dict[field])
            else:
                # Provide default values for missing fields
                if field == 'description':
                    return None  # Description is required
                elif field == 'impact':
                    validated[field] = "Medium"
                elif field == 'reason':
                    validated[field] = "Literature analysis indicates limitations"
                elif field == 'suggested_approaches':
                    validated[field] = "Further research and investigation needed"
        
        return validated if 'description' in validated else None
    
    def identify_contradictions(self, papers):
        """Identify contradictions between papers using LLM with enhanced analysis"""
        logger.info("Identifying contradictions with enhanced analysis...")
        
        if not papers or len(papers) < 2:
            logger.warning("Insufficient papers for contradiction analysis")
            return [{"contradiction": "Insufficient papers for comprehensive contradiction analysis", 
                    "resolution_suggestion": "Expand literature search for better analysis"}]
        
        try:
            # Extract context with specific findings and methodologies
            paper_context = "\n\n".join([
                f"Title: {p.get('title', 'Unknown')}\n"
                f"Methodology: {self._extract_methodology(p.get('abstract', ''))}\n"
                f"Key Findings: {self._extract_key_findings(p.get('abstract', ''))}\n"
                f"Limitations: {self._extract_limitations(p.get('abstract', ''))}"
                for p in papers[:5]
            ])
            
            # Enhanced prompt for contradiction identification
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a research analyst specializing in identifying methodological contradictions, 
                theoretical disagreements, and conflicting empirical findings across scientific literature.
                
                IMPORTANT: Return ONLY a valid JSON array. Do not include any text before or after the JSON."""),
                ("human", """
                Analyze the following research papers and identify any contradictions or conflicting findings between them.

                PAPERS:
                {paper_context}

                For each contradiction, provide a JSON object with these exact fields:
                - "contradiction": A clear description of the contradiction
                - "papers_involved": The papers involved in this contradiction
                - "potential_reasons": Potential reasons for the contradiction
                - "resolution_suggestion": Suggestions for resolving the contradiction

                If no major contradictions are found, return an array with one object explaining this.
                Return only a JSON array, nothing else.
                """)
            ])
            
            # Use LLM to identify contradictions
            chain = prompt | self.llm
            response = chain.invoke({"paper_context": paper_context})
            
            # Parse response
            contradictions = self._parse_enhanced_response(response.content, "contradictions")
            
            if isinstance(contradictions, list) and len(contradictions) > 0:
                # Validate each contradiction structure
                valid_contradictions = []
                for contr in contradictions:
                    if isinstance(contr, dict):
                        valid_contr = self._validate_contradiction_structure(contr)
                        if valid_contr:
                            valid_contradictions.append(valid_contr)
                
                if valid_contradictions:
                    return valid_contradictions
            
            return [{"contradiction": "No major contradictions identified in current literature", 
                    "resolution_suggestion": "Continue monitoring as more research becomes available"}]
            
        except Exception as e:
            logger.error(f"Failed to identify contradictions with LLM: {e}")
            return [{"contradiction": "Technical limitations prevented comprehensive contradiction analysis", 
                    "resolution_suggestion": "Manual review recommended for thorough contradiction analysis"}]
    
    def _validate_contradiction_structure(self, contr_dict: dict) -> Union[dict, None]:
        """Validate and fix contradiction structure"""
        required_fields = ['contradiction', 'papers_involved', 'potential_reasons', 'resolution_suggestion']
        
        validated = {}
        for field in required_fields:
            if field in contr_dict and contr_dict[field]:
                validated[field] = str(contr_dict[field])
            else:
                # Provide default values for missing fields
                if field == 'contradiction':
                    return None  # Contradiction description is required
                elif field == 'papers_involved':
                    validated[field] = "Multiple papers in the dataset"
                elif field == 'potential_reasons':
                    validated[field] = "Methodological differences or varying contexts"
                elif field == 'resolution_suggestion':
                    validated[field] = "Further research needed to resolve discrepancies"
        
        return validated if 'contradiction' in validated else None
    
    def analyze_methodological_trends(self, papers, query):
        """Analyze methodological trends across the literature"""
        logger.info("Analyzing methodological trends...")
        
        if not papers or len(papers) == 0:
            logger.warning("No papers provided for methodology analysis")
            return {
                "common_methods": ["Analysis unavailable - no papers"],
                "temporal_evolution": "Analysis unavailable",
                "emerging_methods": ["Analysis unavailable"],
                "methodological_assessment": "Analysis unavailable"
            }
        
        try:
            # Extract methodology information from papers
            method_context = "\n".join([
                f"Title: {p.get('title', 'Unknown')}\n"
                f"Methods: {self._extract_methodology(p.get('abstract', ''))}\n"
                f"Year: {p.get('published_date', 'Unknown')[:4] if p.get('published_date') else 'Unknown'}"
                for p in papers if p.get('abstract')
            ][:8])
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a research methodologist specializing in identifying trends, patterns, 
                and evolution in research methods across scientific literature.
                
                IMPORTANT: Return ONLY a valid JSON object. Do not include any text before or after the JSON."""),
                ("human", """
                Based on the following research papers and the query "{query}", analyze the methodological trends.

                PAPERS:
                {method_context}

                Please identify and return a JSON object with these exact fields:
                - "common_methods": Array of the most common research methods used
                - "temporal_evolution": Description of how methods have evolved over time
                - "emerging_methods": Array of emerging methodological approaches
                - "methodological_assessment": Assessment of methodological strengths and weaknesses

                Return only a JSON object with these fields, nothing else.
                """)
            ])
            
            chain = prompt | self.llm
            response = chain.invoke({
                "query": query,
                "method_context": method_context
            })
            
            parsed_response = self._parse_enhanced_response(response.content, "methodology")
            
            # Validate the type of the parsed response
            if isinstance(parsed_response, dict):
                # Ensure all required fields exist
                validated_response = self._validate_methodology_structure(parsed_response)
                return validated_response
            
            logger.warning(f"Parsed methodology response was not a dictionary (got {type(parsed_response)}). Using fallback.")
            return self._get_fallback_methodology_trends(papers, query)
            
        except Exception as e:
            logger.error(f"Failed to analyze methodological trends: {e}")
            return self._get_fallback_methodology_trends(papers, query)
    
    def _validate_methodology_structure(self, method_dict: dict) -> dict:
        """Validate and fix methodology structure"""
        required_fields = {
            'common_methods': [],
            'temporal_evolution': 'Evolution analysis not available',
            'emerging_methods': [],
            'methodological_assessment': 'Assessment not available'
        }
        
        validated = {}
        for field, default_value in required_fields.items():
            if field in method_dict and method_dict[field]:
                if field in ['common_methods', 'emerging_methods']:
                    # Ensure these are arrays
                    value = method_dict[field]
                    if isinstance(value, list):
                        validated[field] = value
                    elif isinstance(value, str):
                        validated[field] = [v.strip() for v in value.split(',') if v.strip()]
                    else:
                        validated[field] = [str(value)]
                else:
                    validated[field] = str(method_dict[field])
            else:
                validated[field] = default_value
        
        return validated
    
    def _get_fallback_methodology_trends(self, papers: list, query: str) -> dict:
        """Generate fallback methodology trends"""
        # Basic analysis based on abstracts
        common_keywords = []
        for paper in papers[:5]:
            abstract = paper.get('abstract', '').lower()
            for keyword in ['survey', 'experiment', 'analysis', 'study', 'review', 'model', 'algorithm']:
                if keyword in abstract:
                    common_keywords.append(keyword.title())
        
        return {
            'common_methods': list(set(common_keywords)) if common_keywords else ['Literature Review', 'Empirical Analysis'],
            'temporal_evolution': 'Methodological evolution analysis requires more comprehensive data',
            'emerging_methods': ['Advanced Computational Approaches', 'Data-Driven Methods'],
            'methodological_assessment': f'Methodological diversity observed in {query} research'
        }
    
    def assess_evidence_strength(self, papers):
        """Assess the strength of evidence across papers"""
        logger.info("Assessing evidence strength across papers...")
        
        if not papers or len(papers) == 0:
            logger.warning("No papers provided for evidence assessment")
            return {
                "strength_assessment": "Cannot assess - no papers available",
                "influencing_factors": ["No papers available for analysis"],
                "consistency_evaluation": "Not available",
                "recommendations": ["Expand literature search"]
            }
        
        try:
            # Extract evidence-related information
            evidence_context = "\n".join([
                f"Title: {p.get('title', 'Unknown')}\n"
                f"Sample Size: {self._extract_sample_size(p.get('abstract', ''))}\n"
                f"Methods: {self._extract_methodology(p.get('abstract', ''))}\n"
                f"Findings: {self._extract_key_findings(p.get('abstract', ''))}"
                for p in papers if p.get('abstract')
            ][:6])
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a research evaluator specializing in assessing the strength, quality, 
                and reliability of scientific evidence across multiple studies.
                
                IMPORTANT: Return ONLY a valid JSON object. Do not include any text before or after the JSON."""),
                ("human", """
                Based on the following research papers, assess the overall strength of evidence.

                PAPERS:
                {evidence_context}

                Please evaluate and return a JSON object with these exact fields:
                - "strength_assessment": Overall evidence strength (Strong/Moderate/Weak/Limited)
                - "influencing_factors": Array of key factors influencing evidence strength
                - "consistency_evaluation": Consistency of findings across studies
                - "recommendations": Array of recommendations for strengthening evidence

                Return only a JSON object with these fields, nothing else.
                """)
            ])
            
            chain = prompt | self.llm
            response = chain.invoke({"evidence_context": evidence_context})
            
            parsed_response = self._parse_enhanced_response(response.content, "evidence")
            
            if isinstance(parsed_response, dict):
                validated_response = self._validate_evidence_structure(parsed_response)
                return validated_response
            
            return self._get_fallback_evidence_assessment(papers)
            
        except Exception as e:
            logger.error(f"Failed to assess evidence strength: {e}")
            return self._get_fallback_evidence_assessment(papers)
    
    def _validate_evidence_structure(self, evidence_dict: dict) -> dict:
        """Validate and fix evidence structure"""
        required_fields = {
            'strength_assessment': 'Moderate',
            'influencing_factors': ['Analysis based on available literature'],
            'consistency_evaluation': 'Mixed consistency across studies',
            'recommendations': ['Expand sample size', 'Improve methodology']
        }
        
        validated = {}
        for field, default_value in required_fields.items():
            if field in evidence_dict and evidence_dict[field]:
                if field in ['influencing_factors', 'recommendations']:
                    # Ensure these are arrays
                    value = evidence_dict[field]
                    if isinstance(value, list):
                        validated[field] = value
                    elif isinstance(value, str):
                        validated[field] = [v.strip() for v in value.split(',') if v.strip()]
                    else:
                        validated[field] = [str(value)]
                else:
                    validated[field] = str(evidence_dict[field])
            else:
                validated[field] = default_value
        
        return validated
    
    def _get_fallback_evidence_assessment(self, papers: list) -> dict:
        """Generate fallback evidence assessment"""
        paper_count = len(papers)
        
        if paper_count >= 10:
            strength = "Moderate"
        elif paper_count >= 5:
            strength = "Moderate"
        else:
            strength = "Limited"
        
        return {
            "strength_assessment": strength,
            "influencing_factors": [f"Based on {paper_count} papers", "Limited automated analysis capabilities"],
            "consistency_evaluation": "Requires manual review for comprehensive assessment",
            "recommendations": ["Expand literature search", "Include more recent studies", "Consider systematic review methodology"]
        }
    
    def _extract_methodology(self, abstract):
        """Extract methodology information from abstract"""
        if not abstract:
            return 'Methodology not specified in abstract'
            
        methodology_keywords = [
            'randomized', 'controlled trial', 'case study', 'longitudinal', 'cross-sectional',
            'qualitative', 'quantitative', 'mixed methods', 'experiment', 'survey',
            'meta-analysis', 'systematic review', 'cohort study', 'simulation', 'modeling'
        ]
        
        sentences = abstract.split('.')
        methodology_sentences = [
            sent.strip() for sent in sentences 
            if any(keyword in sent.lower() for keyword in methodology_keywords)
        ]
        
        if methodology_sentences:
            return '. '.join(methodology_sentences[:2]) + '.'
        else:
            return 'Methodology not clearly specified in abstract'
    
    def _extract_methodology_keywords(self, abstract):
        """Extract methodology keywords from abstract"""
        if not abstract:
            return 'No methodology keywords found'
            
        methodology_keywords = [
            'randomized', 'controlled trial', 'case study', 'longitudinal', 'cross-sectional',
            'qualitative', 'quantitative', 'mixed methods', 'experiment', 'survey',
            'meta-analysis', 'systematic review', 'cohort study', 'simulation', 'modeling'
        ]
        
        found_keywords = [
            keyword for keyword in methodology_keywords 
            if keyword in abstract.lower()
        ]
        
        return ', '.join(found_keywords[:5]) if found_keywords else 'No specific methodology keywords found'
    
    def _extract_key_findings(self, abstract):
        """Extract key findings from abstract with improved logic"""
        if not abstract:
            return 'No findings available'
            
        # Look for results sections or conclusion indicators
        results_indicators = [
            'results show', 'findings indicate', 'we found', 'demonstrate that',
            'suggest that', 'conclude that', 'our analysis shows', 'revealed that'
        ]
        
        sentences = abstract.split('.')
        findings_sentences = [
            sent.strip() for sent in sentences 
            if any(indicator in sent.lower() for indicator in results_indicators)
        ]
        
        if findings_sentences:
            return '. '.join(findings_sentences[:2]) + '.'
        
        # Fallback: return middle portion of abstract (likely contains findings)
        if len(sentences) > 3:
            middle_start = len(sentences) // 3
            middle_end = min(middle_start + 2, len(sentences))
            return '. '.join(sentences[middle_start:middle_end]) + '.'
        
        return abstract[:200] + '...' if len(abstract) > 200 else abstract
    
    def _extract_limitations(self, abstract):
        """Extract limitations from abstract"""
        if not abstract:
            return 'No limitations mentioned'
            
        limitation_indicators = [
            'limitation', 'constraint', 'challenge', 'difficulty', 'shortcoming',
            'cannot', 'unable to', 'limited by', 'restricted by', 'however', 'but'
        ]
        
        sentences = abstract.split('.')
        limitation_sentences = [
            sent.strip() for sent in sentences 
            if any(indicator in sent.lower() for indicator in limitation_indicators)
        ]
        
        if limitation_sentences:
            return '. '.join(limitation_sentences[:2]) + '.'
        else:
            return 'No explicit limitations mentioned in abstract'
    
    def _extract_sample_size(self, abstract):
        """Extract sample size information from abstract"""
        if not abstract:
            return 'Sample size not available'
            
        # Look for numbers that might indicate sample size
        numbers = re.findall(r'\b(\d+)\b', abstract)
        sample_indicators = ['participants', 'subjects', 'samples', 'cases', 'patients', 'studies']
        
        for sentence in abstract.split('.'):
            sentence_lower = sentence.lower()
            if any(indicator in sentence_lower for indicator in sample_indicators):
                sentence_numbers = [num for num in numbers if num in sentence]
                if sentence_numbers:
                    return sentence.strip()
        
        return 'Sample size not specified in abstract'
    
    def _parse_enhanced_response(self, response, response_type):
        """Parse LLM response with improved error handling and formatting"""
        try:
            # Clean the response
            response = response.strip()
            
            # Try to find JSON array or object in the response
            json_match = re.search(r'(\[.*\]|\{.*\})', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                parsed = json.loads(json_str)
                return parsed
            
            # If no JSON found, try to extract structured content
            if response_type == "themes":
                return self._parse_themes_from_text(response)
            elif response_type == "gaps":
                return self._parse_gaps_from_text(response)
            elif response_type == "contradictions":
                return self._parse_contradictions_from_text(response)
            elif response_type == "methodology":
                return self._parse_methodology_from_text(response)
            elif response_type == "evidence":
                return self._parse_evidence_from_text(response)
            else:
                logger.warning(f"Unknown response type: {response_type}")
                return {"content": response[:500] + "..."}
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for {response_type}: {e}")
            return self._get_fallback_response(response_type, response)
        except Exception as e:
            logger.error(f"Failed to parse {response_type} response: {e}")
            return self._get_fallback_response(response_type, response)
    
    def _get_fallback_response(self, response_type: str, response: str):
        """Get fallback response for different types"""
        if response_type == "themes":
            return []
        elif response_type == "gaps":
            return []
        elif response_type == "contradictions":
            return []
        elif response_type == "methodology":
            return {
                "common_methods": ["Analysis failed"],
                "temporal_evolution": "Analysis failed",
                "emerging_methods": ["Analysis failed"],
                "methodological_assessment": "Analysis failed"
            }
        elif response_type == "evidence":
            return {
                "strength_assessment": "Analysis failed",
                "influencing_factors": ["Technical error"],
                "consistency_evaluation": "Analysis failed",
                "recommendations": ["Retry analysis"]
            }
        else:
            return {"error": f"Could not parse {response_type} response", "raw_response": response[:200]}
    
    def _parse_themes_from_text(self, text):
        """Parse themes from unstructured text"""
        themes = []
        lines = text.split('\n')
        current_theme = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if re.match(r'^(Theme|Topic|Area)\s*\d*[:.-]', line, re.IGNORECASE):
                if current_theme and 'theme' in current_theme:
                    themes.append(current_theme)
                theme_text = re.sub(r'^(Theme|Topic|Area)\s*\d*[:.-]\s*', '', line, flags=re.IGNORECASE)
                current_theme = {"theme": theme_text, "evidence": "Based on paper analysis", "trajectory": "Active research area"}
            elif ('evidence:' in line.lower() or 'support:' in line.lower()) and current_theme:
                current_theme["evidence"] = line.split(':', 1)[1].strip() if ':' in line else line
            elif ('trajectory:' in line.lower() or 'trend:' in line.lower()) and current_theme:
                current_theme["trajectory"] = line.split(':', 1)[1].strip() if ':' in line else line
        
        if current_theme and 'theme' in current_theme:
            themes.append(current_theme)
        
        return themes if themes else None
    
    def _parse_gaps_from_text(self, text):
        """Parse research gaps from unstructured text"""
        gaps = []
        lines = text.split('\n')
        current_gap = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if re.match(r'^(Gap|Limitation|Shortcoming)\s*\d*[:.-]', line, re.IGNORECASE):
                if current_gap and 'description' in current_gap:
                    gaps.append(current_gap)
                desc_text = re.sub(r'^(Gap|Limitation|Shortcoming)\s*\d*[:.-]\s*', '', line, flags=re.IGNORECASE)
                current_gap = {
                    "description": desc_text,
                    "impact": "Medium",
                    "reason": "Literature analysis indicates limitations",
                    "suggested_approaches": "Further research needed"
                }
            elif 'impact:' in line.lower() and current_gap:
                current_gap["impact"] = line.split(':', 1)[1].strip() if ':' in line else line
            elif 'reason:' in line.lower() and current_gap:
                current_gap["reason"] = line.split(':', 1)[1].strip() if ':' in line else line
            elif ('approach:' in line.lower() or 'suggestion:' in line.lower()) and current_gap:
                current_gap["suggested_approaches"] = line.split(':', 1)[1].strip() if ':' in line else line
        
        if current_gap and 'description' in current_gap:
            gaps.append(current_gap)
        
        return gaps if gaps else None
    
    def _parse_contradictions_from_text(self, text):
        """Parse contradictions from unstructured text"""
        contradictions = []
        lines = text.split('\n')
        current_contradiction = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if re.match(r'^(Contradiction|Conflict|Disagreement)\s*\d*[:.-]', line, re.IGNORECASE):
                if current_contradiction and 'contradiction' in current_contradiction:
                    contradictions.append(current_contradiction)
                contr_text = re.sub(r'^(Contradiction|Conflict|Disagreement)\s*\d*[:.-]\s*', '', line, flags=re.IGNORECASE)
                current_contradiction = {
                    "contradiction": contr_text,
                    "papers_involved": "Multiple papers in dataset",
                    "potential_reasons": "Methodological differences or varying contexts",
                    "resolution_suggestion": "Further research needed to resolve discrepancies"
                }
            elif 'papers:' in line.lower() and current_contradiction:
                current_contradiction["papers_involved"] = line.split(':', 1)[1].strip() if ':' in line else line
            elif 'reason:' in line.lower() and current_contradiction:
                current_contradiction["potential_reasons"] = line.split(':', 1)[1].strip() if ':' in line else line
            elif ('suggestion:' in line.lower() or 'resolution:' in line.lower()) and current_contradiction:
                current_contradiction["resolution_suggestion"] = line.split(':', 1)[1].strip() if ':' in line else line
        
        if current_contradiction and 'contradiction' in current_contradiction:
            contradictions.append(current_contradiction)
        
        return contradictions if contradictions else None
    
    def _parse_methodology_from_text(self, text):
        """Parse methodology trends from unstructured text"""
        methodology = {
            "common_methods": [],
            "temporal_evolution": "Evolution analysis not available",
            "emerging_methods": [],
            "methodological_assessment": "Assessment not available"
        }
        
        lines = text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if 'common' in line.lower() and 'method' in line.lower():
                current_section = "common_methods"
            elif 'evolution' in line.lower() or 'temporal' in line.lower():
                current_section = "temporal_evolution"
                if ':' in line:
                    methodology["temporal_evolution"] = line.split(':', 1)[1].strip()
            elif 'emerging' in line.lower() and 'method' in line.lower():
                current_section = "emerging_methods"
            elif 'assessment' in line.lower() or 'strength' in line.lower():
                current_section = "methodological_assessment"
                if ':' in line:
                    methodology["methodological_assessment"] = line.split(':', 1)[1].strip()
            elif current_section in ["common_methods", "emerging_methods"] and line.startswith('-'):
                method_name = line[1:].strip()
                if method_name:
                    methodology[current_section].append(method_name)
        
        return methodology
    
    def _parse_evidence_from_text(self, text):
        """Parse evidence assessment from unstructured text"""
        evidence = {
            "strength_assessment": "Moderate",
            "influencing_factors": [],
            "consistency_evaluation": "Mixed consistency across studies",
            "recommendations": []
        }
        
        lines = text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if 'strength' in line.lower() and ':' in line:
                evidence["strength_assessment"] = line.split(':', 1)[1].strip()
            elif 'factor' in line.lower():
                current_section = "influencing_factors"
            elif 'consistency' in line.lower() and ':' in line:
                evidence["consistency_evaluation"] = line.split(':', 1)[1].strip()
            elif 'recommendation' in line.lower():
                current_section = "recommendations"
            elif current_section in ["influencing_factors", "recommendations"] and line.startswith('-'):
                item = line[1:].strip()
                if item:
                    evidence[current_section].append(item)
        
        return evidence
    
    def _extract_fallback_themes(self, query, papers):
        """Fallback theme extraction based on query and paper titles"""
        themes = set()
        
        # Extract from query
        query_words = query.lower().split()
        important_words = [w for w in query_words if len(w) > 4 and w not in ['using', 'based', 'approach', 'method', 'study', 'analysis']]
        themes.update([w.title() for w in important_words[:3]])
        
        # Extract from paper titles
        for paper in papers[:8]:
            title = paper.get('title', '').lower()
            title_words = title.split()
            for word in title_words:
                if len(word) > 5 and word not in ['using', 'based', 'approach', 'method', 'study', 'analysis']:
                    themes.add(word.title())
        
        # If still no themes, create from query
        if not themes:
            query_parts = query.split()
            if len(query_parts) >= 2:
                themes.add(f"{query_parts[0].title()} {query_parts[1].title()}")
            else:
                themes.add(query.title())
        
        theme_list = list(themes)[:5]  # Limit to 5 themes
        
        return [
            {
                "theme": theme, 
                "evidence": f"Based on analysis of {len(papers)} papers and query terms", 
                "trajectory": "Active research area"
            } 
            for theme in theme_list
        ]
    
    def _extract_fallback_gaps(self, query, papers):
        """Fallback gap extraction based on query"""
        # Create domain-specific gaps based on query
        domain_keywords = query.lower().split()
        
        gaps = []
        
        # Generic gap based on query
        gaps.append({
            "description": f"Limited comprehensive evaluation frameworks for {query} applications",
            "impact": "High",
            "reason": "Current research often focuses on specific aspects rather than holistic evaluation",
            "suggested_approaches": "Develop standardized evaluation metrics and comprehensive benchmarking studies"
        })
        
        # Methodological gap
        gaps.append({
            "description": "Need for more longitudinal studies to assess long-term effectiveness",
            "impact": "Medium",
            "reason": "Most studies focus on short-term outcomes due to resource constraints",
            "suggested_approaches": "Secure funding for extended longitudinal research and establish research consortia"
        })
        
        # Implementation gap
        if any(word in domain_keywords for word in ['machine', 'learning', 'ai', 'algorithm']):
            gaps.append({
                "description": "Gap between theoretical advances and practical implementation in real-world settings",
                "impact": "High",
                "reason": "Academic research often focuses on controlled environments rather than deployment challenges",
                "suggested_approaches": "Increase industry-academic partnerships and focus on deployment-ready solutions"
            })
        elif any(word in domain_keywords for word in ['medical', 'clinical', 'health']):
            gaps.append({
                "description": "Limited translation of research findings into clinical practice guidelines",
                "impact": "High", 
                "reason": "Regulatory and implementation barriers slow adoption of research findings",
                "suggested_approaches": "Strengthen collaboration between researchers and clinical practitioners"
            })
        else:
            gaps.append({
                "description": "Insufficient interdisciplinary collaboration in research approaches",
                "impact": "Medium",
                "reason": "Research silos limit comprehensive understanding of complex problems",
                "suggested_approaches": "Establish interdisciplinary research centers and funding mechanisms"
            })
        
        return gaps[:3]  # Return top 3 gaps