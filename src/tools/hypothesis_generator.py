"""
Enhanced Hypothesis generation tool
"""
from loguru import logger
from utils.llm_config import llm_config
from langchain_core.prompts import ChatPromptTemplate

class HypothesisGenerator:
    def __init__(self, llm=None):
        self.llm = llm or llm_config.get_primary_llm()
    
    def generate_hypotheses(self, state):
        """Generate hypotheses based on analysis results using LLM"""
        logger.info("Generating research hypotheses...")
        
        # Extract relevant information from state
        query = state.get('query', '')
        themes = state.get('key_themes', [])
        gaps = state.get('research_gaps', [])
        papers = state.get('papers_found', [])
        
        # Prepare context
        themes_str = ", ".join(themes[:3]) if themes else "unknown themes"
        gaps_str = "\n".join([
            f"- {gap.get('description', 'No description')} (Impact: {gap.get('impact', 'Unknown')})"
            for gap in gaps[:2]
        ]) if gaps else "No specific gaps identified"
        
        # Create prompt for hypothesis generation
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a research scientist specializing in generating testable hypotheses based on literature analysis."),
            ("human", """
            Based on the following research context, generate 2-4 testable research hypotheses.
            
            RESEARCH QUERY: {query}
            KEY THEMES: {themes}
            RESEARCH GAPS: {gaps}
            
            Please generate hypotheses that:
            1. Address the identified research gaps
            2. Build upon the key themes
            3. Are specific and testable
            4. Have clear practical implications
            
            For each hypothesis, provide:
            - A clear statement
            - A brief rationale
            - An indication of testability (High/Medium/Low)
            
            Format your response as a JSON array of objects with "statement", "rationale", and "testability" fields.
            """)
        ])
        
        try:
            # Use LLM to generate hypotheses
            chain = prompt | self.llm
            response = chain.invoke({
                "query": query,
                "themes": themes_str,
                "gaps": gaps_str
            })
            
            # Parse response
            hypotheses = self._parse_hypothesis_response(response.content)
            return hypotheses if hypotheses else self._generate_fallback_hypotheses(query, themes, gaps)
            
        except Exception as e:
            logger.error(f"Failed to generate hypotheses with LLM: {e}")
            return self._generate_fallback_hypotheses(query, themes, gaps)
    
    def _parse_hypothesis_response(self, response):
        """Parse LLM response for hypotheses"""
        try:
            # Try to parse as JSON
            if '[' in response and ']' in response:
                start = response.find('[')
                end = response.find(']') + 1
                json_str = response[start:end]
                import json
                return json.loads(json_str)
        except:
            pass
        
        # Fallback: extract hypotheses manually
        hypotheses = []
        lines = response.split('\n')
        current_hyp = {}
        
        for line in lines:
            line = line.strip()
            lower_line = line.lower()
            
            if 'statement:' in lower_line:
                if current_hyp:
                    hypotheses.append(current_hyp)
                current_hyp = {'statement': line.split(':', 1)[1].strip(), 'rationale': '', 'testability': 'Medium'}
            elif 'rationale:' in lower_line and current_hyp:
                current_hyp['rationale'] = line.split(':', 1)[1].strip()
            elif 'testability:' in lower_line and current_hyp:
                current_hyp['testability'] = line.split(':', 1)[1].strip()
        
        if current_hyp:
            hypotheses.append(current_hyp)
        
        return hypotheses if hypotheses else self._generate_fallback_hypotheses("", [], [])
    
    def _generate_fallback_hypotheses(self, query, themes, gaps):
        """Generate fallback hypotheses when LLM fails"""
        theme = themes[0] if themes else "the field"
        gap_desc = gaps[0].get('description', 'identified issues') if gaps else "current limitations"
        
        return [
            {
                "statement": f"Applying {theme} approaches will improve addressing {gap_desc}",
                "rationale": f"Based on the literature review, {theme} methods show promise for addressing this challenge",
                "testability": "High",
                "confidence": 0.7
            },
            {
                "statement": f"Integrating multiple methodologies will enhance outcomes in {query.split()[0]} research",
                "rationale": "Current approaches are often siloed; integration could provide more comprehensive solutions",
                "testability": "Medium",
                "confidence": 0.6
            }
        ]