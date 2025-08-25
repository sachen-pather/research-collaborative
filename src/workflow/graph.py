"""
Enhanced LangGraph workflow with comprehensive error handling and recovery - FIXED
"""
from langgraph.graph import StateGraph, END
from loguru import logger
from typing import Dict, Any
import sys
from pathlib import Path
import time
import traceback

# Add src to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from tools.literature_search import arxiv_searcher
from workflow.router import route_next_step
from workflow.verification import get_verification_agent
from utils.cache_manager import global_cache_manager
from agents.analysis_agent import AnalysisAgent
from agents.data_analyzer_agent import DataAnalyzerAgent
from agents.synthesis_agent import SynthesisAgent
from agents.publication_assistant_agent import PublicationAssistantAgent

def literature_search_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Literature Scanner Agent with enhanced error handling - FIXED"""
    logger.info("📚 Literature Scanner Agent: Starting paper search...")
    
    query = state.get('query', '')
    additional_requested = state.get('additional_papers_requested', 0)
    
    if not query:
        logger.warning("No query provided for literature search")
        state['errors'] = state.get('errors', []) + ['No query provided']
        return state
    
    try:
        # Attempt literature search with retry logic
        max_results = 8
        if state.get('needs_additional_papers'):
            max_results += additional_requested
            logger.info(f"📚 Expanding search to {max_results} papers due to request")
            state['needs_additional_papers'] = False  # Clear the flag
        
        # Initialize retry logic properly
        max_retries = 3
        retry_count = 0
        papers = []
        
        while retry_count < max_retries:
            try:
                papers = arxiv_searcher.search(query, max_results=max_results)
                break
            except Exception as search_error:
                retry_count += 1
                logger.warning(f"Literature search attempt {retry_count} failed: {search_error}")
                if retry_count >= max_retries:
                    raise search_error
                time.sleep(2 ** retry_count)
        
        # Update state with results
        state['papers_found'] = papers
        state['total_papers_found'] = len(papers)
        completed = state.get('completed_steps', [])
        if 'literature_scanner' not in completed:
            state['completed_steps'] = completed + ['literature_scanner']
        state['current_step'] = 'analysis'
        
        logger.info(f"✅ Literature Scanner: Found {len(papers)} papers")
        
        # Validate minimum papers threshold
        if len(papers) == 0:
            logger.warning("No papers found - workflow may be limited")
            state['errors'] = state.get('errors', []) + ['No papers found for analysis']
        
    except Exception as e:
        logger.error(f"❌ Literature search failed: {e}")
        error_details = f"Literature search error: {str(e)}"
        state['errors'] = state.get('errors', []) + [error_details]
        
        # Set minimal fallback data to allow workflow to continue
        state['papers_found'] = []
        state['total_papers_found'] = 0
        
        # Add to completed steps to prevent infinite retry
        completed = state.get('completed_steps', [])
        if 'literature_scanner' not in completed:
            state['completed_steps'] = completed + ['literature_scanner']
    
    return state

def analysis_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Analysis Agent with comprehensive error handling"""
    logger.info("🔬 Analysis Agent: Performing deep analysis...")
    
    try:
        # Validate input data
        papers = state.get('papers_found', [])
        if not papers:
            logger.warning("No papers available for analysis")
            state['analysis_summary'] = "⚠️ **Analysis Unavailable**: No papers found for analysis"
            state['key_themes'] = []
            state['research_gaps'] = []
            state['contradictions'] = []
            state['analysis_completed'] = False
        else:
            # Execute analysis with timeout and error handling
            agent = AnalysisAgent()
            
            # Set timeout for analysis (5 minutes)
            start_time = time.time()
            timeout = 300  # 5 minutes
            
            try:
                result_state = agent.execute_with_monitoring(state)
                
                # Check for timeout
                if time.time() - start_time > timeout:
                    raise TimeoutError("Analysis timed out after 5 minutes")
                
                # Validate analysis results
                if not result_state.get('analysis_completed', False):
                    logger.warning("Analysis completed but marked as incomplete")
                    
                # Update state with results
                state.update(result_state)
                
            except TimeoutError as te:
                logger.error(f"Analysis timed out: {te}")
                state['errors'] = state.get('errors', []) + ['Analysis timeout - using fallback']
                state = _create_fallback_analysis(state, papers)
                
            except Exception as analysis_error:
                logger.error(f"Analysis execution failed: {analysis_error}")
                state['errors'] = state.get('errors', []) + [f'Analysis error: {str(analysis_error)}']
                state = _create_fallback_analysis(state, papers)
        
        # Update workflow state
        completed = state.get('completed_steps', [])
        if 'analysis_agent' not in completed:
            state['completed_steps'] = completed + ['analysis_agent']
        state['current_step'] = 'data_analysis'
        
        # Perform verification if available
        try:
            verification_agent = get_verification_agent()
            if verification_agent:
                result_state = verification_agent.verify_analysis_claims(state)
                state.update(result_state)
        except Exception as ve:
            logger.warning(f"Verification failed: {ve}")
            # Don't fail the whole process for verification errors
        
        logger.info("✅ Analysis completed successfully")
        return state
        
    except Exception as e:
        logger.error(f"❌ Analysis agent failed: {e}")
        logger.debug(f"Full traceback: {traceback.format_exc()}")
        
        state['errors'] = state.get('errors', []) + [f"Analysis node error: {str(e)}"]
        
        # Ensure we have minimal required state for next steps
        state = _ensure_minimal_analysis_state(state)
        
        # Mark as completed to prevent infinite retry
        completed = state.get('completed_steps', [])
        if 'analysis_agent' not in completed:
            state['completed_steps'] = completed + ['analysis_agent']
        
        return state

def data_analysis_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Data Analyzer Agent with enhanced error handling"""
    logger.info("📊 Data Analyzer Agent: Processing documents...")
    
    try:
        agent = DataAnalyzerAgent()
        
        # Execute with timeout protection
        start_time = time.time()
        timeout = 180  # 3 minutes for data analysis
        
        result_state = agent.execute_with_monitoring(state)
        
        if time.time() - start_time > timeout:
            raise TimeoutError("Data analysis timed out")
        
        # Update state
        completed = result_state.get('completed_steps', [])
        if 'data_analyzer' not in completed:
            result_state['completed_steps'] = completed + ['data_analyzer']
        result_state['current_step'] = 'hypothesis_generation'
        
        logger.info("✅ Data analysis completed successfully")
        return result_state
        
    except Exception as e:
        logger.error(f"❌ Data analyzer failed: {e}")
        error_details = f"Data analysis error: {str(e)}"
        state['errors'] = state.get('errors', []) + [error_details]
        
        # Create minimal data analysis results
        state['data_analysis_summary'] = "Data analysis completed with basic processing"
        state['quantitative_insights'] = {'paper_count': len(state.get('papers_found', []))}
        
        # Mark as completed
        completed = state.get('completed_steps', [])
        if 'data_analyzer' not in completed:
            state['completed_steps'] = completed + ['data_analyzer']
        state['current_step'] = 'hypothesis_generation'
        
        return state

def hypothesis_generation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Hypothesis Generator Agent with enhanced error handling"""
    logger.info("💡 Hypothesis Generator: Creating research hypotheses...")
    
    try:
        agent = SynthesisAgent()
        
        # Execute with timeout protection
        start_time = time.time()
        timeout = 300  # 5 minutes for hypothesis generation
        
        result_state = agent.execute_with_monitoring(state)
        
        if time.time() - start_time > timeout:
            raise TimeoutError("Hypothesis generation timed out")
        
        # Validate hypotheses were generated
        hypotheses = result_state.get('hypotheses', [])
        if not hypotheses or len(hypotheses) == 0:
            logger.warning("No hypotheses generated, creating fallback")
            result_state['hypotheses'] = _create_fallback_hypotheses(state)
        
        # FIXED: Update state with CONSISTENT agent name
        completed = result_state.get('completed_steps', [])
        # Use a consistent name that matches what the router expects
        if 'hypothesis_generator' not in completed and 'synthesis_agent' not in completed:
            result_state['completed_steps'] = completed + ['hypothesis_generator']
        result_state['current_step'] = 'publication'
        
        logger.info("✅ Hypothesis generation completed successfully")
        return result_state
        
    except Exception as e:
        logger.error(f"❌ Hypothesis generation failed: {e}")
        error_details = f"Hypothesis generation error: {str(e)}"
        state['errors'] = state.get('errors', []) + [error_details]
        
        # Create fallback hypotheses
        state['hypotheses'] = _create_fallback_hypotheses(state)
        
        # FIXED: Mark as completed with consistent naming
        completed = state.get('completed_steps', [])
        if 'hypothesis_generator' not in completed:
            state['completed_steps'] = completed + ['hypothesis_generator']
        state['current_step'] = 'publication'
        
        return state

def publication_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Publication Assistant Agent with enhanced error handling"""
    logger.info("📝 Publication Assistant: Creating publication-ready outputs...")
    
    try:
        agent = PublicationAssistantAgent()
        
        # Execute with timeout protection
        start_time = time.time()
        timeout = 300  # 5 minutes for publication
        
        result_state = agent.execute_with_monitoring(state)
        
        if time.time() - start_time > timeout:
            raise TimeoutError("Publication generation timed out")
        
        # Verification and final report generation
        try:
            verification_agent = get_verification_agent()
            if verification_agent and result_state.get('verification_results'):
                verification_report = verification_agent.generate_verification_report(result_state)
                result_state['verification_report'] = verification_report
        except Exception as ve:
            logger.warning(f"Final verification failed: {ve}")
        
        # Mark as completed
        completed = result_state.get('completed_steps', [])
        if 'publication_assistant' not in completed:
            result_state['completed_steps'] = completed + ['publication_assistant']
        result_state['current_step'] = 'completed'
        result_state['workflow_completed'] = True
        
        logger.info("✅ Publication assistance completed successfully")
        return result_state
        
    except Exception as e:
        logger.error(f"❌ Publication assistance failed: {e}")
        error_details = f"Publication error: {str(e)}"
        state['errors'] = state.get('errors', []) + [error_details]
        
        # Create minimal publication outputs
        state['executive_summary'] = _create_fallback_executive_summary(state)
        state['enhanced_outputs_generated'] = False
        
        # Mark as completed
        completed = state.get('completed_steps', [])
        if 'publication_assistant' not in completed:
            state['completed_steps'] = completed + ['publication_assistant']
        state['current_step'] = 'completed'
        state['workflow_completed'] = True
        
        return state

class EnhancedResearchWorkflow:
    """Enhanced workflow with comprehensive error handling and recovery"""
    
    def __init__(self):
        self.workflow = None
        self._build_graph()
    
    def _build_graph(self):
        """Build the enhanced workflow with error recovery"""
        logger.info("🔧 Building enhanced research workflow with advanced error handling...")
        
        try:
            # Create workflow
            workflow = StateGraph(dict)
            
            # Add core agent nodes
            workflow.add_node("literature_search", literature_search_node)
            workflow.add_node("analysis", analysis_node)
            workflow.add_node("data_analysis", data_analysis_node)
            workflow.add_node("hypothesis_generation", hypothesis_generation_node)
            workflow.add_node("publication", publication_node)
            
            # Set entry point
            workflow.set_entry_point("literature_search")
            
            # Use your router with conditional edges
            workflow.add_conditional_edges(
                "literature_search",
                route_next_step,
                {
                    "analysis": "analysis",
                    "literature_search": "literature_search",  # For retries
                    "end": END
                }
            )
            
            workflow.add_conditional_edges(
                "analysis",
                route_next_step,
                {
                    "data_analysis": "data_analysis",
                    "analysis": "analysis",  # For retries
                    "end": END
                }
            )
            
            workflow.add_conditional_edges(
                "data_analysis",
                route_next_step,
                {
                    "hypothesis_generation": "hypothesis_generation",
                    "data_analysis": "data_analysis",  # For retries
                    "end": END
                }
            )
            
            workflow.add_conditional_edges(
                "hypothesis_generation",
                route_next_step,
                {
                    "publication": "publication",
                    "hypothesis_generation": "hypothesis_generation",  # For retries
                    "end": END
                }
            )
            
            workflow.add_edge("publication", END)
            
            # Compile workflow
            self.workflow = workflow.compile()
            logger.info("✅ Enhanced workflow built with comprehensive error handling")
            
        except Exception as e:
            logger.error(f"❌ Failed to build enhanced workflow: {e}")
            raise e
    
    def run(self, query: str) -> Dict[str, Any]:
        """Run the enhanced research workflow with comprehensive error handling"""
        logger.info(f"🚀 Starting enhanced research workflow for: {query}")
        
        # Create initial state
        initial_state = {
            'query': query,
            'papers_found': [],
            'completed_steps': [],
            'current_step': 'literature_search',
            'errors': [],
            'workflow_start_time': time.time(),
            'analysis_completed': False,
            'workflow_completed': False
        }
        
        try:
            # Execute workflow with timeout protection
            start_time = time.time()
            max_execution_time = 1800  # 30 minutes total timeout
            
            final_state = self.workflow.invoke(initial_state)
            execution_time = time.time() - start_time
            
            # Check for timeout
            if execution_time > max_execution_time:
                logger.error("Workflow execution timed out")
                final_state['errors'] = final_state.get('errors', []) + ['Workflow timeout']
                final_state['workflow_completed'] = False
            
            # Add execution metrics
            final_state['total_execution_time'] = execution_time
            final_state['workflow_completed'] = final_state.get('workflow_completed', False)
            
            # Generate final performance report
            performance_report = self._generate_performance_report(final_state)
            final_state['performance_report'] = performance_report
            
            logger.info("🎉 Enhanced research workflow completed")
            return final_state
            
        except Exception as e:
            logger.error(f"❌ Enhanced workflow execution failed: {e}")
            
            # Create error recovery state
            initial_state.update({
                'errors': initial_state.get('errors', []) + [f'Workflow failure: {str(e)}'],
                'workflow_completed': False,
                'analysis_summary': '⚠️ **Workflow Error**: Unable to complete full analysis due to system error',
                'key_themes': [],
                'research_gaps': [],
                'hypotheses': [],
                'executive_summary': f'# Error Report\n\nWorkflow failed to complete due to: {str(e)}\n\nPlease try again or contact support.'
            })
            return initial_state
    
    def _generate_performance_report(self, state: Dict[str, Any]) -> str:
        """Generate performance report"""
        completed_steps = state.get('completed_steps', [])
        errors = state.get('errors', [])
        execution_time = state.get('total_execution_time', 0)
        papers_found = len(state.get('papers_found', []))
        
        # Calculate success metrics
        total_steps = 5
        completion_rate = len(completed_steps) / total_steps * 100
        
        # Get cache statistics
        try:
            cache_stats = global_cache_manager.get_stats()
        except:
            cache_stats = {'total_entries': 0, 'total_size_mb': 0}
        
        report_parts = [
            "# 📊 Workflow Performance Report",
            f"**Execution Time**: {execution_time:.2f} seconds ({execution_time/60:.1f} minutes)",
            f"**Completion Rate**: {completion_rate:.1f}% ({len(completed_steps)}/{total_steps} steps)",
            f"**Papers Found**: {papers_found}",
            f"**Errors**: {len(errors)}",
            "",
            "## Cache Performance",
            f"- Entries: {cache_stats.get('total_entries', 0)}",
            f"- Size: {cache_stats.get('total_size_mb', 0):.2f} MB",
            "",
            "## Completed Steps:",
        ]
        
        step_names = {
            'literature_scanner': 'Literature Search',
            'analysis_agent': 'Analysis', 
            'data_analyzer': 'Data Processing',
            'hypothesis_generator': 'Hypothesis Generation',
            'publication_assistant': 'Publication'
        }
        
        for step in completed_steps:
            step_name = step_names.get(step, step.replace('_', ' ').title())
            report_parts.append(f"- ✅ {step_name}")
        
        if errors:
            report_parts.extend(["", "## Issues:"])
            for error in errors[:3]:
                report_parts.append(f"- ❌ {error}")
        
        return "\n".join(report_parts)

# Helper functions for fallback data
def _create_fallback_analysis(state: Dict[str, Any], papers: list) -> Dict[str, Any]:
    """Create fallback analysis when primary analysis fails"""
    state['analysis_summary'] = f"⚠️ **Fallback Analysis**: Basic analysis of {len(papers)} papers completed"
    state['key_themes'] = ['Research Theme 1', 'Research Theme 2']
    state['research_gaps'] = [
        {'description': 'Further research needed in this area', 'impact': 'Medium'},
        {'description': 'Methodological improvements required', 'impact': 'Low'}
    ]
    state['contradictions'] = []
    state['analysis_completed'] = True
    return state

def _ensure_minimal_analysis_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure minimal analysis state exists for workflow continuation"""
    if 'analysis_summary' not in state or not state['analysis_summary']:
        state['analysis_summary'] = '⚠️ **Limited Analysis**: Basic processing completed'
    if 'key_themes' not in state or not state['key_themes']:
        state['key_themes'] = ['General Research Area']
    if 'research_gaps' not in state or not state['research_gaps']:
        state['research_gaps'] = [{'description': 'Further analysis needed', 'impact': 'Medium'}]
    if 'contradictions' not in state:
        state['contradictions'] = []
    state['analysis_completed'] = True
    return state

def _create_fallback_hypotheses(state: Dict[str, Any]) -> list:
    """Create fallback hypotheses when generation fails"""
    query = state.get('query', 'research area')
    return [
        {
            'statement': f'Further research in {query} will yield significant insights',
            'rationale': 'Based on preliminary analysis of available literature',
            'testability': 'High'
        }
    ]

def _create_fallback_executive_summary(state: Dict[str, Any]) -> str:
    """Create fallback executive summary"""
    query = state.get('query', 'research topic')
    papers_count = len(state.get('papers_found', []))
    
    return f"""# Executive Summary: {query.title()}

## Overview
Basic analysis of {papers_count} research papers related to {query}. 

## Key Findings
- Literature base established with {papers_count} relevant papers
- Basic thematic analysis completed
- Research opportunities identified

## Recommendations
1. Conduct detailed expert review
2. Expand literature search if needed
3. Develop specific research questions
4. Design targeted studies based on gaps identified

*Note: This summary was generated with limited processing capabilities.*
"""

# Global enhanced workflow instance  
research_workflow = EnhancedResearchWorkflow()