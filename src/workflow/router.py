"""
Enhanced router logic with proper node name matching
"""
from typing import Dict, Any, List
from loguru import logger

def route_next_step(state: Dict[str, Any]) -> str:
    """
    Dynamic routing based on workflow state - FIXED node names
    """
    current_step = state.get('current_step', '')
    completed_steps = state.get('completed_steps', [])
    errors = state.get('errors', [])
    papers_found = state.get('papers_found', [])
    
    logger.info(f"🧭 Dynamic routing: current_step={current_step}, completed={len(completed_steps)}, papers={len(papers_found)}")
    
    # Critical error handling - terminate if too many failures
    if len(errors) > 5:
        logger.warning("Too many errors, terminating workflow")
        return "end"
    
    # SEQUENTIAL ROUTING with dynamic decisions
    
    # 1. After literature search -> analysis
    if 'literature_scanner' in completed_steps and 'analysis_agent' not in completed_steps:
        logger.info("Literature search complete, routing to analysis")
        return "analysis"
    
    # 2. After analysis -> data analysis (conditional)
    if 'analysis_agent' in completed_steps and 'data_analyzer' not in completed_steps:
        analysis_summary = state.get('analysis_summary', '')
        # Always go to data analysis for demo purposes
        logger.info("Analysis complete, routing to data analysis")
        return "data_analysis"
    
    # 3. After data analysis -> hypothesis generation
    if 'data_analyzer' in completed_steps and 'hypothesis_generator' not in completed_steps:
        logger.info("Data analysis complete, routing to hypothesis generation")
        return "hypothesis_generation"
    
    # 4. After hypothesis generation -> publication
    if 'hypothesis_generator' in completed_steps and 'publication_assistant' not in completed_steps:
        logger.info("Hypothesis generation complete, routing to publication")
        return "publication"
    
    # 5. Check for insufficient papers and retry needed
    if len(papers_found) < 3 and 'literature_retry' not in completed_steps and len(completed_steps) < 2:
        logger.info("Insufficient papers found, routing to literature retry")
        return "literature_retry"
    
    # 6. Gap enhancement if needed
    research_gaps = state.get('research_gaps', [])
    if len(research_gaps) < 2 and 'gap_enhancement' not in completed_steps and 'analysis_agent' in completed_steps:
        logger.info("Few research gaps found, routing to gap enhancement")
        return "gap_enhancement"
    
    # Default: end workflow
    logger.info("All major steps completed or no valid next step, ending workflow")
    return "end"

def should_continue(state: Dict[str, Any]) -> bool:
    """Determine if workflow should continue"""
    completed_steps = state.get('completed_steps', [])
    errors = state.get('errors', [])
    
    # Stop if too many errors
    if len(errors) > 5:
        return False
        
    # Continue if we haven't completed core steps
    core_steps = ['literature_scanner', 'analysis_agent', 'data_analyzer', 'hypothesis_generator', 'publication_assistant']
    completed_core = [step for step in completed_steps if step in core_steps]
    
    return len(completed_core) < len(core_steps)
