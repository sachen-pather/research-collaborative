"""
Automatic retry and recovery system
"""
from typing import Dict, Any, Callable
import time
from loguru import logger
import random

class RetryManager:
    """Manages automatic retry and recovery strategies"""
    
    def __init__(self):
        self.max_retries = 3
        self.base_delay = 1.0
        self.max_delay = 10.0
        self.backoff_factor = 2.0
    
    def execute_with_retry(self, func: Callable, state: Dict[str, Any], step_name: str) -> Dict[str, Any]:
        """Execute function with automatic retry logic"""
        retry_count = 0
        last_error = None
        
        # Get existing retry count for this step
        if 'retry_counts' not in state:
            state['retry_counts'] = {}
        
        retry_count = state['retry_counts'].get(step_name, 0)
        
        while retry_count < self.max_retries:
            try:
                logger.info(f"🔄 Executing {step_name} (attempt {retry_count + 1}/{self.max_retries})")
                
                result = func(state)
                
                # Success - reset retry count
                if step_name in state.get('retry_counts', {}):
                    del state['retry_counts'][step_name]
                
                logger.info(f"✅ {step_name} succeeded on attempt {retry_count + 1}")
                return result
                
            except Exception as e:
                last_error = e
                retry_count += 1
                state['retry_counts'][step_name] = retry_count
                
                logger.warning(f"❌ {step_name} failed (attempt {retry_count}/{self.max_retries}): {e}")
                
                if retry_count < self.max_retries:
                    # Calculate exponential backoff delay with jitter
                    delay = min(
                        self.base_delay * (self.backoff_factor ** (retry_count - 1)),
                        self.max_delay
                    )
                    # Add jitter to prevent thundering herd
                    jitter = random.uniform(0.1, 0.3) * delay
                    total_delay = delay + jitter
                    
                    logger.info(f"⏳ Retrying {step_name} in {total_delay:.2f}s...")
                    time.sleep(total_delay)
        
        # All retries exhausted
        logger.error(f"💥 {step_name} failed after {self.max_retries} attempts. Last error: {last_error}")
        
        # Apply recovery strategy
        return self._apply_recovery_strategy(state, step_name, last_error)
    
    def _apply_recovery_strategy(self, state: Dict[str, Any], failed_step: str, error: Exception) -> Dict[str, Any]:
        """Apply recovery strategy for failed step"""
        logger.info(f"🛠️ Applying recovery strategy for failed step: {failed_step}")
        
        recovery_strategies = {
            'literature_search': self._recover_literature_search,
            'analysis': self._recover_analysis,
            'data_analysis': self._recover_data_analysis,
            'hypothesis_generation': self._recover_hypothesis_generation,
            'publication': self._recover_publication
        }
        
        recovery_func = recovery_strategies.get(failed_step, self._generic_recovery)
        return recovery_func(state, error)
    
    def _recover_literature_search(self, state: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        """Recovery strategy for literature search failures"""
        logger.info("📚 Applying literature search recovery...")
        
        # Fallback to mock data
        fallback_papers = [
            {
                'title': 'Fallback Research Paper on Topic',
                'authors': ['Recovery Author'],
                'abstract': f"This is a fallback paper for the query: {state.get('query', 'unknown')}",
                'url': 'http://example.com/fallback',
                'source': 'recovery_system'
            }
        ]
        
        state['papers_found'] = fallback_papers
        state['recovery_applied'] = True
        state['recovery_type'] = 'literature_fallback'
        
        return state
    
    def _recover_analysis(self, state: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        """Recovery strategy for analysis failures"""
        logger.info("🔬 Applying analysis recovery...")
        
        # Simple rule-based analysis
        query = state.get('query', '')
        papers = state.get('papers_found', [])
        
        # Extract themes from query and paper titles
        themes = self._extract_themes_simple(query, papers)
        
        # Generate basic gaps
        gaps = [
            {'description': f'Limited research on practical applications of {query}', 'impact': 'High'},
            {'description': 'Need for more comprehensive evaluation methods', 'impact': 'Medium'}
        ]
        
        state['key_themes'] = themes
        state['research_gaps'] = gaps
        state['contradictions'] = ['Recovery mode - detailed contradiction analysis unavailable']
        state['analysis_summary'] = f"Recovery analysis completed for {len(papers)} papers"
        state['recovery_applied'] = True
        state['recovery_type'] = 'analysis_fallback'
        
        return state
    
    def _recover_data_analysis(self, state: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        """Recovery strategy for data analysis failures"""
        logger.info("📊 Applying data analysis recovery...")
        
        papers = state.get('papers_found', [])
        
        # Basic quantitative analysis
        basic_insights = {
            'paper_count': len(papers),
            'estimated_authors': len(papers) * 3,  # Estimate 3 authors per paper
            'analysis_mode': 'recovery'
        }
        
        state['quantitative_insights'] = basic_insights
        state['data_analysis_summary'] = f"Recovery data analysis: {len(papers)} papers processed"
        state['recovery_applied'] = True
        state['recovery_type'] = 'data_analysis_fallback'
        
        return state
    
    def _recover_hypothesis_generation(self, state: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        """Recovery strategy for hypothesis generation failures"""
        logger.info("💡 Applying hypothesis generation recovery...")
        
        query = state.get('query', 'research topic')
        themes = state.get('key_themes', [])
        
        # Generate template hypotheses
        fallback_hypotheses = [
            {
                'statement': f'Advances in {themes[0] if themes else "the field"} will improve {query}',
                'rationale': 'Based on current research trends',
                'priority': 'High',
                'source': 'recovery_system'
            },
            {
                'statement': f'Integration of multiple approaches in {query} shows promising results',
                'rationale': 'Cross-disciplinary potential identified',
                'priority': 'Medium',
                'source': 'recovery_system'
            }
        ]
        
        state['hypotheses'] = fallback_hypotheses
        state['recovery_applied'] = True
        state['recovery_type'] = 'hypothesis_fallback'
        
        return state
    
    def _recover_publication(self, state: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        """Recovery strategy for publication failures"""
        logger.info("📝 Applying publication recovery...")
        
        query = state.get('query', 'Research Topic')
        papers_count = len(state.get('papers_found', []))
        
        # Basic publication output
        basic_summary = f"""# Recovery Research Summary: {query}

## Overview
Emergency analysis completed for {papers_count} papers.

## Status
- Literature collection: {'✅' if papers_count > 0 else '❌'}
- Analysis: {'✅' if 'key_themes' in state else '❌'}  
- Hypothesis generation: {'✅' if 'hypotheses' in state else '❌'}

## Next Steps
- Manual review recommended
- Consider re-running analysis with adjusted parameters
"""
        
        state['executive_summary'] = basic_summary
        state['publication_report'] = basic_summary
        state['recovery_applied'] = True
        state['recovery_type'] = 'publication_fallback'
        
        return state
    
    def _generic_recovery(self, state: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        """Generic recovery strategy"""
        logger.info("🔧 Applying generic recovery strategy...")
        
        state['recovery_applied'] = True
        state['recovery_type'] = 'generic'
        state['recovery_message'] = f"Recovery applied due to error: {str(error)[:100]}"
        
        return state
    
    def _extract_themes_simple(self, query: str, papers: list) -> list:
        """Simple theme extraction for recovery"""
        themes = []
        
        # Extract from query
        query_words = query.lower().split()
        important_words = [w for w in query_words if len(w) > 4]
        themes.extend(important_words[:3])
        
        # Extract from paper titles
        if papers:
            all_titles = ' '.join([p.get('title', '') for p in papers])
            title_words = all_titles.lower().split()
            common_words = ['learning', 'analysis', 'model', 'data', 'system', 'method']
            
            for word in common_words:
                if word in title_words and word not in themes:
                   themes.append(word)
                   if len(themes) >= 5:
                       break
       
       # Default themes if nothing found
        if not themes:
            themes = ['research', 'analysis', 'methodology']
        
        return themes[:5]

# Global retry manager
retry_manager = RetryManager()
