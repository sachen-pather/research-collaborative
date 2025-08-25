#!/usr/bin/env python3
import sys
import os
from pathlib import Path
import streamlit as st
from loguru import logger
import time
from datetime import datetime
import traceback

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

try:
    # Import your existing modules with error handling
    from workflow.graph import research_workflow
    from utils.llm_config import llm_config
    from utils.cache_manager import global_cache_manager
except ImportError as e:
    st.error(f"Import Error: {e}")
    st.info("Please ensure all dependencies are installed and paths are correct")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Research Collaborative",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
        margin: 1.5rem 0 1rem 0;
    }
    .agent-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .error-box {
        background-color: #fff2f2;
        border: 1px solid #ff6b6b;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff8e1;
        border: 1px solid #ffa726;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #f1f8e9;
        border: 1px solid #66bb6a;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state with error handling
def initialize_session_state():
    """Initialize session state with safe defaults"""
    defaults = {
        'workflow_results': None,
        'query_history': [],
        'current_query': "",
        'run_workflow': False,
        'last_error': None,
        'system_status': 'Unknown'
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def check_system_status():
    """Check system status and LLM availability"""
    try:
        # Verify LLM setup
        llm_status = llm_config.verify_setup()
        
        # Check if at least one LLM is working
        working_llms = [k for k, v in llm_status.items() if "✅" in str(v)]
        
        if working_llms:
            st.session_state.system_status = 'Ready'
            return True, llm_status
        else:
            st.session_state.system_status = 'LLM Issues'
            return False, llm_status
            
    except Exception as e:
        st.session_state.system_status = 'Error'
        logger.error(f"System status check failed: {e}")
        return False, {'error': str(e)}

def display_system_status():
    """Display system status in sidebar"""
    with st.sidebar:
        st.markdown("---")
        st.subheader("🔧 System Status")
        
        system_ready, llm_status = check_system_status()
        
        if system_ready:
            st.success("✅ System Ready")
        else:
            st.error("❌ System Issues Detected")
        
        # Show LLM status
        if isinstance(llm_status, dict):
            for provider, status in llm_status.items():
                if provider != 'error':
                    st.text(f"{provider.title()}: {status}")
        
        if not system_ready:
            st.warning("⚠️ Some features may be limited")

def safe_workflow_execution(query: str):
    """Execute workflow with comprehensive error handling"""
    try:
        # Pre-execution checks
        if not query or len(query.strip()) < 3:
            raise ValueError("Query must be at least 3 characters long")
        
        # System status check
        system_ready, _ = check_system_status()
        if not system_ready:
            st.warning("⚠️ System issues detected. Workflow may have limited functionality.")
        
        # Clear previous errors
        st.session_state.last_error = None
        
        # Execute workflow with timeout
        logger.info(f"Starting workflow execution for: {query}")
        start_time = time.time()
        
        try:
            final_state = research_workflow.run(query)
            execution_time = time.time() - start_time
            
            logger.info(f"Workflow completed in {execution_time:.2f} seconds")
            
            # Validate results
            if not isinstance(final_state, dict):
                raise ValueError("Workflow returned invalid results")
            
            # Check for workflow errors
            workflow_errors = final_state.get('errors', [])
            if workflow_errors:
                error_summary = f"Workflow completed with {len(workflow_errors)} issues"
                st.warning(f"⚠️ {error_summary}")
                
                # Show errors in expandable section
                with st.expander("View Issues"):
                    for i, error in enumerate(workflow_errors, 1):
                        st.text(f"{i}. {error}")
            
            # Store results
            st.session_state.workflow_results = final_state
            st.session_state.query_history.append({
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "execution_time": execution_time,
                "papers_found": len(final_state.get('papers_found', [])),
                "errors": len(workflow_errors),
                "completed_steps": len(final_state.get('completed_steps', []))
            })
            
            return True, final_state
            
        except Exception as workflow_error:
            logger.error(f"Workflow execution failed: {workflow_error}")
            logger.debug(f"Workflow traceback: {traceback.format_exc()}")
            
            # Create error state for display
            error_state = {
                'query': query,
                'errors': [f"Workflow execution failed: {str(workflow_error)}"],
                'papers_found': [],
                'analysis_summary': f"❌ **Execution Failed**: {str(workflow_error)}",
                'workflow_completed': False,
                'total_execution_time': time.time() - start_time
            }
            
            st.session_state.workflow_results = error_state
            st.session_state.last_error = str(workflow_error)
            
            return False, error_state
            
    except Exception as e:
        logger.error(f"Safe workflow execution failed: {e}")
        st.session_state.last_error = str(e)
        return False, None

def display_workflow_progress():
    """Display workflow progress with real-time updates"""
    progress_container = st.container()
    
    with progress_container:
        st.markdown('<div class="sub-header">🔄 Analysis in Progress</div>', unsafe_allow_html=True)
        
        # Progress indicator
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        stages = [
            ("Literature Search", "Searching academic databases..."),
            ("Analysis", "Analyzing papers and extracting themes..."),
            ("Data Processing", "Processing documents and data..."),
            ("Hypothesis Generation", "Creating research hypotheses..."),
            ("Report Creation", "Generating final reports...")
        ]
        
        # Simulate progress for user feedback
        for i, (stage, description) in enumerate(stages):
            status_text.text(f"🔄 {stage}: {description}")
            progress_bar.progress((i + 0.5) / len(stages))
            time.sleep(0.5)  # Brief pause for visual feedback
        
        return progress_bar, status_text

def display_results_safely(results):
    """Display results with comprehensive error handling"""
    try:
        if not results:
            st.error("No results to display")
            return
        
        # Check for critical errors
        if st.session_state.last_error:
            st.markdown(f'''
            <div class="error-box">
                <h4>⚠️ Execution Error</h4>
                <p>{st.session_state.last_error}</p>
                <p><em>Some results may be incomplete or unavailable.</em></p>
            </div>
            ''', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown('<div class="sub-header"> Research Results</div>', unsafe_allow_html=True)
        
        # Current query
        query = results.get('query', 'Unknown Query')
        st.markdown(f"**Research Query:** {query}")
        
        # Metrics with error handling
        papers_count = len(results.get('papers_found', []))
        gaps_count = len(results.get('research_gaps', []))
        hypotheses_count = len(results.get('hypotheses', []))
        execution_time = results.get('total_execution_time', 0)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Papers Found", papers_count)
        with col2:
            st.metric("Research Gaps", gaps_count)
        with col3:
            st.metric("Hypotheses", hypotheses_count)
        with col4:
            st.metric("Execution Time", f"{execution_time:.2f}s")
        
        # Enhanced Research Results
        st.markdown("---")
        st.markdown("### 🔬 Research Intelligence Reports")
        
        # Check if enhanced outputs were generated
        enhanced_generated = results.get('enhanced_outputs_generated', False)
        workflow_completed = results.get('workflow_completed', False)
        
        if enhanced_generated and workflow_completed:
            st.markdown('''
            <div class="success-box">
                <strong>✅ Analysis Complete</strong><br>
                Comprehensive research reports generated successfully!
            </div>
            ''', unsafe_allow_html=True)
            
            # Display enhanced outputs
            display_enhanced_outputs(results)
            
        elif workflow_completed:
            st.markdown('''
            <div class="warning-box">
                <strong>⚠️ Basic Analysis Complete</strong><br>
                Workflow completed but enhanced outputs may be limited.
            </div>
            ''', unsafe_allow_html=True)
            
            # Display basic outputs
            display_basic_outputs(results)
            
        else:
            st.markdown('''
            <div class="error-box">
                <strong>❌ Incomplete Analysis</strong><br>
                Workflow did not complete successfully. Results may be limited.
            </div>
            ''', unsafe_allow_html=True)
            
            # Display whatever we have
            display_limited_outputs(results)
        
        # Always show error summary if errors exist
        errors = results.get('errors', [])
        if errors:
            with st.expander(f"⚠️ Issues Encountered ({len(errors)})", expanded=False):
                for i, error in enumerate(errors, 1):
                    st.text(f"{i}. {error}")
        
    except Exception as e:
        logger.error(f"Failed to display results: {e}")
        st.error(f"Error displaying results: {str(e)}")

def display_enhanced_outputs(results):
    """Display enhanced research outputs"""
    try:
        # Executive Summary
        if results.get('executive_summary'):
            with st.expander(" Executive Research Summary", expanded=True):
                st.markdown(results['executive_summary'])
        
        # Research Plan
        if results.get('detailed_research_plan'):
            with st.expander(" Detailed Research Plan"):
                st.markdown(results['detailed_research_plan'])
        
        # Strategic Recommendations
        recommendations = results.get('strategic_recommendations', [])
        if recommendations:
            with st.expander(" Strategic Recommendations"):
                for i, rec in enumerate(recommendations, 1):
                    priority_color = "🔴" if rec.get('priority') == 'High' else "🟡" if rec.get('priority') == 'Medium' else "🟢"
                    st.markdown(f"{priority_color} **{rec.get('recommendation', 'No recommendation')}**")
                    st.caption(f"Category: {rec.get('category', 'General')} | Timeline: {rec.get('timeline', 'TBD')}")
        
        # Download Options
        st.markdown("### 📥 Export Research Reports")
        create_download_buttons(results)
        
    except Exception as e:
        logger.error(f"Error displaying enhanced outputs: {e}")
        st.error("Error displaying enhanced outputs")

def display_basic_outputs(results):
    """Display basic research outputs"""
    try:
        # Analysis Summary
        if results.get('analysis_summary'):
            with st.expander("Analysis Summary", expanded=True):
                st.markdown(results['analysis_summary'])
        
        # Research Hypotheses
        hypotheses = results.get('hypotheses', [])
        if hypotheses:
            with st.expander(" Research Hypotheses"):
                display_hypotheses(hypotheses)
        
        # Research Gaps
        gaps = results.get('research_gaps', [])
        if gaps:
            with st.expander("Research Gaps"):
                display_research_gaps(gaps)
        
        # Papers Found
        papers = results.get('papers_found', [])
        if papers:
            with st.expander(f"Papers Found ({len(papers)})"):
                display_papers(papers)
        
    except Exception as e:
        logger.error(f"Error displaying basic outputs: {e}")
        st.error("Error displaying basic outputs")

def display_limited_outputs(results):
    """Display limited outputs when workflow fails"""
    try:
        st.info(" Displaying available information from partial analysis")
        
        # Show whatever we have
        if results.get('analysis_summary'):
            st.markdown("### Analysis Summary")
            st.markdown(results['analysis_summary'])
        
        papers = results.get('papers_found', [])
        if papers:
            st.markdown(f"### Papers Found ({len(papers)})")
            display_papers(papers[:5])  # Show first 5 papers
        
        if results.get('performance_report'):
            with st.expander(" Performance Report"):
                st.markdown(results['performance_report'])
        
    except Exception as e:
        logger.error(f"Error displaying limited outputs: {e}")
        st.error("Error displaying limited outputs")

def display_hypotheses(hypotheses):
    """Display research hypotheses safely"""
    try:
        for i, hypothesis in enumerate(hypotheses, 1):
            if isinstance(hypothesis, dict):
                statement = hypothesis.get('statement', 'No statement available')
                rationale = hypothesis.get('rationale', '')
                testability = hypothesis.get('testability', 'Unknown')
                
                st.markdown(f"**Hypothesis {i}:** {statement}")
                if rationale:
                    st.caption(f"Rationale: {rationale}")
                if testability:
                    st.caption(f"Testability: {testability}")
            else:
                st.markdown(f"**Hypothesis {i}:** {str(hypothesis)}")
            st.divider()
    except Exception as e:
        logger.error(f"Error displaying hypotheses: {e}")
        st.error("Error displaying hypotheses")

def display_research_gaps(gaps):
    """Display research gaps safely"""
    try:
        for i, gap in enumerate(gaps, 1):
            if isinstance(gap, dict):
                description = gap.get('description', 'No description available')
                impact = gap.get('impact', 'Unknown impact')
                
                st.markdown(f"**Gap {i}:** {description}")
                st.caption(f"Impact: {impact}")
            else:
                st.markdown(f"**Gap {i}:** {str(gap)}")
            st.divider()
    except Exception as e:
        logger.error(f"Error displaying research gaps: {e}")
        st.error("Error displaying research gaps")

def display_papers(papers):
    """Display papers safely"""
    try:
        for i, paper in enumerate(papers, 1):
            title = paper.get('title', 'No title available')
            authors = paper.get('authors', ['Unknown'])
            source = paper.get('source', 'Unknown source')
            url = paper.get('url', '')
            
            st.markdown(f"**{i}. {title}**")
            
            if isinstance(authors, list):
                authors_str = ', '.join(authors)
            else:
                authors_str = str(authors)
            
            st.caption(f"Authors: {authors_str}")
            st.caption(f"Source: {source}")
            
            if url:
                st.caption(f"[View Paper]({url})")
            
            st.divider()
    except Exception as e:
        logger.error(f"Error displaying papers: {e}")
        st.error("Error displaying papers")

def create_download_buttons(results):
    """Create download buttons for reports"""
    try:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if results.get('executive_summary'):
                st.download_button(
                    label="📄 Executive Summary",
                    data=results['executive_summary'],
                    file_name=f"executive_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                    mime="text/markdown"
                )
        
        with col2:
            if results.get('detailed_research_plan'):
                st.download_button(
                    label=" Research Plan", 
                    data=results['detailed_research_plan'],
                    file_name=f"research_plan_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                    mime="text/markdown"
                )
        
        with col3:
            if results.get('comprehensive_research_report'):
                st.download_button(
                    label=" Complete Report",
                    data=results['comprehensive_research_report'],
                    file_name=f"complete_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md", 
                    mime="text/markdown"
                )
    except Exception as e:
        logger.error(f"Error creating download buttons: {e}")
        st.error("Error creating download options")

# Main application
def main():
    """Main application with comprehensive error handling"""
    try:
        # Initialize session state
        initialize_session_state()
        
        # Sidebar
        with st.sidebar:
            st.title("🔬 Research Collaborative")
            st.markdown("---")
            
            # System status
            display_system_status()
            
            # Query input
            st.subheader("Research Query")
            query = st.text_area(
                "Enter your research topic:",
                height=100,
                value="Multi-modal transformer architectures for scientific literature analysis",
                key="query_input"
            )
            
            # Example queries
            st.subheader("Example Queries")
            examples = [
                "Machine learning approaches for climate change prediction",
                "Neural networks in medical diagnosis applications", 
                "Blockchain technology for supply chain transparency",
                "Quantum computing applications in cryptography"
            ]
            
            for i, example in enumerate(examples):
                if st.button(example, key=f"example_{i}"):
                    st.session_state.current_query = example
                    st.session_state.workflow_results = None
                    st.session_state.run_workflow = True
                    st.rerun()
            
            # Run button
            st.markdown("---")
            if st.button(" Run Research Analysis", type="primary", use_container_width=True):
                if query.strip():
                    st.session_state.current_query = query
                    st.session_state.workflow_results = None
                    st.session_state.run_workflow = True
                    st.rerun()
                else:
                    st.error("Please enter a research query")
        
        # Main content
        st.markdown('<h1 class="main-header">🔬 Research Collaborative</h1>', unsafe_allow_html=True)
        st.markdown("""
        <p style='text-align: center; font-size: 1.2rem;'>
        Multi-agent system for automated literature review, hypothesis generation, and research planning
        </p>
        """, unsafe_allow_html=True)
        
        # Agent overview
        st.markdown('<div class="sub-header"> Agent Team</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        agents = [
            (" Literature Scanner", "Searches academic databases for relevant papers"),
            (" Analysis Agent", "Identifies key themes and research gaps"),
            (" Data Analyzer", "Processes documents and extracts insights"),
            (" Hypothesis Generator", "Creates testable research hypotheses"),
            (" Publication Assistant", "Formats outputs and creates reports")
        ]
        
        for col, (name, desc) in zip([col1, col2, col3, col4, col5], agents):
            with col:
                st.markdown(f'''
                <div class="agent-card">
                    <h4>{name}</h4>
                    <p style="font-size: 0.9rem;">{desc}</p>
                </div>
                ''', unsafe_allow_html=True)
        
        # Workflow execution
        if st.session_state.run_workflow and st.session_state.current_query:
            # Show progress
            progress_bar, status_text = display_workflow_progress()
            
            # Execute workflow
            success, final_state = safe_workflow_execution(st.session_state.current_query)
            
            # Update progress
            progress_bar.progress(1.0)
            if success:
                status_text.text("✅ Analysis Complete!")
                st.success("🎉 Research analysis completed successfully!")
            else:
                status_text.text("❌ Analysis Completed with Issues")
                st.error("⚠️ Research analysis completed with some issues. See results below.")
            
            st.session_state.run_workflow = False
        
        # Display results
        if st.session_state.workflow_results:
            display_results_safely(st.session_state.workflow_results)
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #6c757d;'>
            <p>Research Collaborative System • Multi-Agent Research Assistant</p>
            <p>Literature Review • Hypothesis Generation • Research Planning</p>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        logger.error(f"Main application error: {e}")
        st.error(f"Application Error: {str(e)}")
        st.info("Please refresh the page or contact support if the issue persists.")

if __name__ == "__main__":
    main()