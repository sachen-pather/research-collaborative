"""
Enhanced Text analysis tool for LLM-powered text processing
"""
from loguru import logger
from utils.llm_config import llm_config
from langchain_core.prompts import ChatPromptTemplate

class TextAnalyzer:
    def __init__(self, llm=None):
        self.llm = llm or llm_config.get_primary_llm()
    
    def extract_key_themes(self, papers, query):
        """Extract key themes from papers using LLM"""
        logger.info("Extracting key themes from papers...")
        
        # Extract titles and abstracts for context
        paper_context = "\n".join([
            f"Title: {p.get('title', 'Unknown')}\nAbstract: {p.get('abstract', 'No abstract')[:300]}..."
            for p in papers[:5]  # Limit to first 5 papers to avoid token limits
        ])
        
        # Create prompt for theme extraction
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a research analyst specializing in identifying key themes across scientific literature."),
            ("human", """
            Based on the following research papers and the query "{query}", identify the 3-5 most important research themes.
            
            PAPERS:
            {paper_context}
            
            Please provide a concise list of key themes that represent the main research directions in this area.
            Format your response as a JSON array of theme strings.
            """)
        ])
        
        try:
            # Use LLM to extract themes
            chain = prompt | self.llm
            response = chain.invoke({
                "query": query,
                "paper_context": paper_context
            })
            
            # Parse response (this is simplified - you might need more robust parsing)
            themes = self._parse_llm_response(response.content)
            return themes if themes else ["Machine Learning Applications", "Medical Diagnosis", "Neural Networks"]
            
        except Exception as e:
            logger.error(f"Failed to extract themes with LLM: {e}")
            # Fallback to query-based themes
            return self._extract_fallback_themes(query, papers)
    
    def extract_research_gaps(self, papers, query):
        """Identify research gaps using LLM"""
        logger.info("Identifying research gaps...")
        
        # Extract titles and abstracts for context
        paper_context = "\n".join([
            f"Title: {p.get('title', 'Unknown')}\nAbstract: {p.get('abstract', 'No abstract')[:300]}..."
            for p in papers[:5]  # Limit to first 5 papers
        ])
        
        # Create prompt for gap identification
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a research analyst specializing in identifying gaps in scientific literature."),
            ("human", """
            Based on the following research papers and the query "{query}", identify 2-4 significant research gaps.
            
            PAPERS:
            {paper_context}
            
            For each gap, provide:
            1. A clear description of the gap
            2. The potential impact of addressing this gap
            
            Format your response as a JSON array of objects with "description" and "impact" fields.
            """)
        ])
        
        try:
            # Use LLM to identify gaps
            chain = prompt | self.llm
            response = chain.invoke({
                "query": query,
                "paper_context": paper_context
            })
            
            # Parse response
            gaps = self._parse_gap_response(response.content)
            return gaps if gaps else [
                {"description": "Limited validation of methods across diverse datasets", "impact": "High"},
                {"description": "Need for more interpretable and explainable models", "impact": "Medium"}
            ]
            
        except Exception as e:
            logger.error(f"Failed to identify gaps with LLM: {e}")
            # Fallback to query-based gaps
            return self._extract_fallback_gaps(query, papers)
    
    def identify_contradictions(self, papers):
        """Identify contradictions between papers using LLM"""
        logger.info("Identifying contradictions...")
        
        # Extract titles and key findings for context
        paper_context = "\n".join([
            f"Title: {p.get('title', 'Unknown')}\nKey Findings: {self._extract_key_findings(p.get('abstract', ''))}"
            for p in papers[:4]  # Compare first 4 papers
        ])
        
        # Create prompt for contradiction identification
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a research analyst specializing in identifying contradictions in scientific literature."),
            ("human", """
            Analyze the following research papers and identify any contradictions or conflicting findings between them.
            
            PAPERS:
            {paper_context}
            
            Identify 1-3 contradictions or areas where the research findings disagree.
            Format your response as a JSON array of contradiction descriptions.
            """)
        ])
        
        try:
            # Use LLM to identify contradictions
            chain = prompt | self.llm
            response = chain.invoke({"paper_context": paper_context})
            
            # Parse response
            contradictions = self._parse_contradiction_response(response.content)
            return contradictions if contradictions else [
                "Different evaluation metrics make direct comparison of results challenging",
                "Varied dataset sizes and quality affect the generalizability of findings"
            ]
            
        except Exception as e:
            logger.error(f"Failed to identify contradictions with LLM: {e}")
            return ["Limited data available for comprehensive contradiction analysis"]
    
    def _extract_key_findings(self, abstract):
        """Extract key findings from abstract (simplified)"""
        # This is a simplified implementation - in a real system, you'd use more sophisticated NLP
        sentences = abstract.split('.')
        return '.'.join(sentences[:2]) + '.' if len(sentences) > 2 else abstract[:150] + '...'
    
    def _parse_llm_response(self, response):
        """Parse LLM response for themes"""
        # Simple parsing - you might want to implement more robust JSON parsing
        try:
            # Look for array-like structure
            if '[' in response and ']' in response:
                start = response.find('[')
                end = response.find(']') + 1
                json_str = response[start:end]
                import json
                return json.loads(json_str)
        except:
            pass
        
        # Fallback: extract themes by lines or bullets
        themes = []
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) > 10 and not line.startswith(('{', '[', '```')):
                # Remove numbering or bullets
                if line.startswith(('- ', '* ', '1. ', '2. ', '3. ', '4. ', '5. ')):
                    line = line[2:].strip()
                themes.append(line)
        
        return themes[:5]  # Return at most 5 themes
    
    def _parse_gap_response(self, response):
        """Parse LLM response for research gaps"""
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
        
        # Fallback: extract gaps manually
        gaps = []
        lines = response.split('\n')
        current_gap = {}
        
        for line in lines:
            line = line.strip().lower()
            if 'description:' in line:
                if current_gap:
                    gaps.append(current_gap)
                current_gap = {'description': line.split('description:')[1].strip(), 'impact': 'Unknown'}
            elif 'impact:' in line and current_gap:
                current_gap['impact'] = line.split('impact:')[1].strip()
        
        if current_gap:
            gaps.append(current_gap)
        
        return gaps if gaps else [
            {"description": "Limited validation of methods across diverse datasets", "impact": "High"},
            {"description": "Need for more interpretable and explainable models", "impact": "Medium"}
        ]
    
    def _parse_contradiction_response(self, response):
        """Parse LLM response for contradictions"""
        # Similar to theme parsing but for contradictions
        contradictions = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and len(line) > 20 and not line.startswith(('{', '[', '```')):
                if line.startswith(('- ', '* ', '1. ', '2. ', '3. ')):
                    line = line[2:].strip()
                contradictions.append(line)
        
        return contradictions[:3]  # Return at most 3 contradictions
    
    def _extract_fallback_themes(self, query, papers):
        """Fallback theme extraction based on query and paper titles"""
        themes = set()
        
        # Extract from query
        query_words = query.lower().split()
        important_words = [w for w in query_words if len(w) > 5]
        themes.update(important_words[:3])
        
        # Extract from paper titles
        for paper in papers[:5]:
            title = paper.get('title', '').lower()
            title_words = title.split()
            for word in title_words:
                if len(word) > 6 and word not in ['using', 'based', 'approach', 'method']:
                    themes.add(word.title())
        
        return list(themes)[:5] if themes else ["Machine Learning", "Neural Networks", "Medical Applications"]
    
    def _extract_fallback_gaps(self, query, papers):
        """Fallback gap extraction based on query"""
        return [
            {"description": f"Limited research on practical applications of {query.split()[0]}", "impact": "High"},
            {"description": "Need for more comprehensive evaluation methods", "impact": "Medium"},
            {"description": "Lack of standardized benchmarking across studies", "impact": "High"}
        ]