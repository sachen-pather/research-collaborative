"""
Enhanced LangGraph workflow with working routing - SIMPLIFIED
"""
from langgraph.graph import StateGraph, END
from loguru import logger
from typing import Dict, Any
import sys
from pathlib import Path
import time

# Add src to path
# This path correction is good, but let's make the imports absolute.
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# --- ALL IMPORTS MOVED TO THE TOP ---
from tools.literature_search import arxiv_searcher
from workflow.router import route_next_step
from workflow.verification import get_verification_agent
from utils.cache_manager import global_cache_manager
from agents.analysis_agent import AnalysisAgent
from agents.data_analyzer_agent import DataAnalyzerAgent
from agents.synthesis_agent import SynthesisAgent
from agents.publication_assistant_agent import PublicationAssistantAgent
# --- END OF IMPORTS ---

def literature_search_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Literature Scanner Agent"""
    logger.info("📚 Literature Scanner Agent: Starting paper search...")
    
    query = state.get('query', '')
    
    if not query:
        logger.warning("No query provided for literature search")
        return state
    
    try:
        papers = arxiv_searcher.search(query, max_results=8)
        state['papers_found'] = papers
        state['total_papers_found'] = len(papers)
        state['completed_steps'] = state.get('completed_steps', []) + ['literature_scanner']
        state['current_step'] = 'analysis'
        logger.info(f"✅ Literature Scanner: Found {len(papers)} papers")
        
    except Exception as e:
        logger.error(f"❌ Literature search failed: {e}")
        state['errors'] = state.get('errors', []) + [f"Literature search error: {str(e)}"]
        state['papers_found'] = []
        state['total_papers_found'] = 0
    
    return state

def analysis_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Analysis Agent"""
    logger.info("🔬 Analysis Agent: Performing deep analysis...")
    
    try:
        # The 'from agents...' import is now at the top of the file
        agent = AnalysisAgent()
        result_state = agent.execute_with_monitoring(state)
        
        completed = result_state.get('completed_steps', [])
        if 'analysis_agent' not in completed:
            result_state['completed_steps'] = completed + ['analysis_agent']
        result_state['current_step'] = 'data_analysis'
        
        verification_agent = get_verification_agent()
        if verification_agent:
            result_state = verification_agent.verify_analysis_claims(result_state)
        
        logger.info("✅ Analysis completed successfully")
        return result_state
        
    except Exception as e:
        logger.error(f"❌ Analysis agent failed: {e}")
        state['errors'] = state.get('errors', []) + [f"Analysis error: {str(e)}"]
        return state

def data_analysis_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Data Analyzer Agent"""
    logger.info("📊 Data Analyzer Agent: Processing documents...")
    
    try:
        # The 'from agents...' import is now at the top of the file
        agent = DataAnalyzerAgent()
        result_state = agent.execute_with_monitoring(state)
        
        completed = result_state.get('completed_steps', [])
        if 'data_analyzer' not in completed:
            result_state['completed_steps'] = completed + ['data_analyzer']
        result_state['current_step'] = 'hypothesis_generation'
        
        logger.info("✅ Data analysis completed successfully")
        return result_state
        
    except Exception as e:
        logger.error(f"❌ Data analyzer failed: {e}")
        state['errors'] = state.get('errors', []) + [f"Data analysis error: {str(e)}"]
        return state

def hypothesis_generation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Hypothesis Generator Agent"""
    logger.info("💡 Hypothesis Generator: Creating research hypotheses...")
    
    try:
        # The 'from agents...' import is now at the top of the file
        agent = SynthesisAgent()
        result_state = agent.execute_with_monitoring(state)
        
        completed = result_state.get('completed_steps', [])
        if 'hypothesis_generator' not in completed:
            result_state['completed_steps'] = completed + ['hypothesis_generator']
        result_state['current_step'] = 'publication'
        
        logger.info("✅ Hypothesis generation completed successfully")
        return result_state
        
    except Exception as e:
        logger.error(f"❌ Hypothesis generation failed: {e}")
        state['errors'] = state.get('errors', []) + [f"Hypothesis generation error: {str(e)}"]
        return state

def publication_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Publication Assistant Agent"""
    logger.info("📝 Publication Assistant: Creating publication-ready outputs...")
    
    try:
        # The 'from agents...' import is now at the top of the file
        agent = PublicationAssistantAgent()
        result_state = agent.execute_with_monitoring(state)
        
        verification_agent = get_verification_agent()
        if verification_agent and result_state.get('verification_results'):
            verification_report = verification_agent.generate_verification_report(result_state)
            result_state['verification_report'] = verification_report
        
        completed = result_state.get('completed_steps', [])
        if 'publication_assistant' not in completed:
            result_state['completed_steps'] = completed + ['publication_assistant']
        result_state['current_step'] = 'completed'
        
        logger.info("✅ Publication assistance completed successfully")
        return result_state
        
    except Exception as e:
        logger.error(f"❌ Publication assistance failed: {e}")
        state['errors'] = state.get('errors', []) + [f"Publication error: {str(e)}"]
        return state

# --- The rest of your EnhancedResearchWorkflow class remains the same ---
# (No changes needed for the class itself)
class EnhancedResearchWorkflow:
    """Enhanced workflow with working conditional routing"""
    
    def __init__(self):
        self.workflow = None
        self._build_graph()
    
    def _build_graph(self):
        """Build the enhanced workflow"""
        logger.info("🔧 Building enhanced research workflow with advanced features...")
        
        try:
            # Create workflow
            workflow = StateGraph(dict)
            
            # Add core agent nodes (names must match router exactly!)
            workflow.add_node("literature_search", literature_search_node)
            workflow.add_node("analysis", analysis_node)
            workflow.add_node("data_analysis", data_analysis_node)
            workflow.add_node("hypothesis_generation", hypothesis_generation_node)
            workflow.add_node("publication", publication_node)
            
            # Set entry point
            workflow.set_entry_point("literature_search")
            
            # WORKING CONDITIONAL ROUTING
            workflow.add_conditional_edges(
                "literature_search",
                route_next_step,
                {
                    "analysis": "analysis",
                    "end": END
                }
            )
            
            workflow.add_conditional_edges(
                "analysis",
                route_next_step,
                {
                    "data_analysis": "data_analysis",
                    "end": END
                }
            )
            
            workflow.add_conditional_edges(
                "data_analysis",
                route_next_step,
                {
                    "hypothesis_generation": "hypothesis_generation",
                    "end": END
                }
            )
            
            workflow.add_conditional_edges(
                "hypothesis_generation",
                route_next_step,
                {
                    "publication": "publication",
                    "end": END
                }
            )
            
            workflow.add_edge("publication", END)
            
            # Compile workflow
            self.workflow = workflow.compile()
            logger.info("✅ Enhanced workflow built with conditional routing and advanced features")
            
        except Exception as e:
            logger.error(f"❌ Failed to build enhanced workflow: {e}")
            raise e
    
    def run(self, query: str) -> Dict[str, Any]:
        """Run the enhanced research workflow"""
        logger.info(f"🚀 Starting enhanced research workflow for: {query}")
        
        # Create initial state
        initial_state = {
            'query': query,
            'papers_found': [],
            'completed_steps': [],
            'current_step': 'literature_search',
            'errors': [],
            'retry_counts': {},
            'communications_sent': 0,
            'escalations': [],
            'quality_assessments': [],
            'verification_results': {},
            'recovery_applied': False
        }
        
        try:
            # Execute workflow
            start_time = time.time()
            final_state = self.workflow.invoke(initial_state)
            execution_time = time.time() - start_time
            
            # Add execution metrics
            final_state['total_execution_time'] = execution_time
            final_state['workflow_completed'] = True
            
            # Generate final performance report
            performance_report = self._generate_performance_report(final_state)
            final_state['performance_report'] = performance_report
            
            logger.info("🎉 Enhanced research workflow completed successfully")
            return final_state
            
        except Exception as e:
            logger.error(f"❌ Enhanced workflow execution failed: {e}")
            initial_state['errors'].append(f"Workflow failure: {str(e)}")
            initial_state['workflow_completed'] = False
            return initial_state
    
    def _generate_performance_report(self, state: Dict[str, Any]) -> str:
        """Generate performance report"""
        completed_steps = state.get('completed_steps', [])
        errors = state.get('errors', [])
        execution_time = state.get('total_execution_time', 0)
        
        # Calculate metrics
        completion_rate = len(completed_steps) / 5 * 100  # 5 core steps
        
        # Get cache statistics
        cache_stats = global_cache_manager.get_stats()
        
        report_parts = [
            "# 📊 Performance Report",
            f"**Execution Time**: {execution_time:.2f} seconds",
            f"**Completion Rate**: {completion_rate:.1f}%",
            f"**Steps Completed**: {len(completed_steps)}/5",
            f"**Errors**: {len(errors)}",
            "",
            "## Cache Performance",
            f"- Cache Entries: {cache_stats['total_entries']}",
            f"- Cache Size: {cache_stats['total_size_mb']:.2f} MB",
            "",
            "## Completed Steps:",
        ]
        
        for step in completed_steps:
            report_parts.append(f"- ✅ {step.replace('_', ' ').title()}")
        
        return "\n".join(report_parts)

# Global enhanced workflow instance  
research_workflow = EnhancedResearchWorkflow()