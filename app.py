#!/usr/bin/env python3
import sys
import os
import json
from pathlib import Path
import streamlit as st
from loguru import logger
import io
import time
from datetime import datetime

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Import your existing modules
from workflow.graph import research_workflow
from utils.llm_config import llm_config
from utils.cache_manager import global_cache_manager

# Page configuration
st.set_page_config(
    page_title="Research Collaborative",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
        margin-top: 1.5rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .agent-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .feature-badge {
        background-color: #e9ecef;
        border-radius: 0.25rem;
        padding: 0.25rem 0.5rem;
        margin: 0.25rem;
        display: inline-block;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'workflow_results' not in st.session_state:
    st.session_state.workflow_results = None
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'show_details' not in st.session_state:
    st.session_state.show_details = False

# Sidebar
with st.sidebar:
    st.title("🔬 Research Collaborative")
    st.markdown("---")
    
    # Query input
    st.subheader("Research Query")
    query = st.text_area(
        "Enter your research topic:",
        height=100,
        value="Multi-modal transformer architectures for scientific literature analysis"
    )
    
    # Preset examples
    st.subheader("Example Queries")
    example_queries = [
        "Machine learning approaches for climate change prediction",
        "Neural networks in medical diagnosis applications",
        "Blockchain technology for supply chain transparency",
        "Quantum computing applications in cryptography"
    ]
    
    for example in example_queries:
        if st.button(example, key=f"example_{example}"):
            query = example
            st.rerun()
    
    # Advanced options
    st.subheader("Advanced Options")
    st.session_state.show_details = st.checkbox("Show Detailed Results", value=False)
    
    # Run button
    if st.button("🚀 Run Research Analysis", type="primary", use_container_width=True):
        st.session_state.run_workflow = True

# Main content area
st.markdown('<h1 class="main-header">Research Collaborative System</h1>', unsafe_allow_html=True)
st.markdown("""
<p style='text-align: center; font-size: 1.2rem;'>
A multi-agent system for automated literature review, hypothesis generation, and research planning
</p>
""", unsafe_allow_html=True)

# Agent overview
st.markdown('<div class="sub-header">Agent Team</div>', unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown('<div class="agent-card">', unsafe_allow_html=True)
    st.markdown("**📚 Literature Scanner**")
    st.markdown("Searches academic databases for relevant papers")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="agent-card">', unsafe_allow_html=True)
    st.markdown("**🔬 Analysis Agent**")
    st.markdown("Identifies key themes and research gaps")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="agent-card">', unsafe_allow_html=True)
    st.markdown("**📊 Data Analyzer**")
    st.markdown("Processes documents and extracts insights")
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="agent-card">', unsafe_allow_html=True)
    st.markdown("**💡 Hypothesis Generator**")
    st.markdown("Creates testable research hypotheses")
    st.markdown('</div>', unsafe_allow_html=True)

with col5:
    st.markdown('<div class="agent-card">', unsafe_allow_html=True)
    st.markdown("**📝 Publication Assistant**")
    st.markdown("Formats outputs and creates reports")
    st.markdown('</div>', unsafe_allow_html=True)

# Features overview
st.markdown('<div class="sub-header">System Features</div>', unsafe_allow_html=True)

features = [
    "Multi-Agent Orchestration", "Intelligent Routing", "Bidirectional Communication",
    "Autonomous Decision Making", "Error Handling & Recovery", "Performance Optimization",
    "Hallucination Mitigation", "Multi-LLM Integration"
]

st.markdown("".join([f'<span class="feature-badge">{feature}</span>' for feature in features]), unsafe_allow_html=True)

# Run workflow if requested
if st.session_state.get('run_workflow', False):
    with st.spinner("Running research analysis... This may take a few minutes."):
        # Capture logs
        log_capture = io.StringIO()
        
        # Add log capture handler
        logger.add(log_capture, level="INFO", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
        
        # Test LLM setup
        llm_status = llm_config.verify_setup()
        
        # Clear cache
        global_cache_manager.clear_expired()
        
        # Run workflow
        start_time = time.time()
        final_state = research_workflow.run(query)
        execution_time = time.time() - start_time
        
        # Store results
        st.session_state.workflow_results = final_state
        st.session_state.query_history.append({
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "execution_time": execution_time,
            "papers_found": len(final_state.get('papers_found', [])),
            "errors": len(final_state.get('errors', []))
        })
        
        # Remove log handler
        logger.remove()

# Display results if available
if st.session_state.workflow_results:
    results = st.session_state.workflow_results
    
    st.markdown("---")
    st.markdown('<div class="sub-header">Research Results</div>', unsafe_allow_html=True)
    
    # Summary cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Papers Found", len(results.get('papers_found', [])))
    
    with col2:
        st.metric("Research Gaps", len(results.get('research_gaps', [])))
    
    with col3:
        st.metric("Hypotheses", len(results.get('hypotheses', [])))
    
    with col4:
        st.metric("Execution Time", f"{results.get('total_execution_time', 0):.2f}s")
    
    # Key findings
    if 'analysis_summary' in results:
        with st.expander("📋 Executive Summary", expanded=True):
            st.markdown(results['analysis_summary'])
    
    # Research hypotheses
    if 'hypotheses' in results and results['hypotheses']:
        with st.expander("💡 Research Hypotheses"):
            for i, hypothesis in enumerate(results['hypotheses']):
                if isinstance(hypothesis, dict):
                    st.markdown(f"**Hypothesis {i+1}:** {hypothesis.get('statement', 'No statement')}")
                    if 'rationale' in hypothesis:
                        st.caption(f"Rationale: {hypothesis['rationale']}")
                else:
                    st.markdown(f"**Hypothesis {i+1}:** {hypothesis}")
                st.divider()
    
    # Research gaps
    if 'research_gaps' in results and results['research_gaps']:
        with st.expander("🔍 Research Gaps"):
            for i, gap in enumerate(results['research_gaps']):
                if isinstance(gap, dict):
                    st.markdown(f"**Gap {i+1}:** {gap.get('description', 'No description')}")
                    if 'impact' in gap:
                        st.caption(f"Impact: {gap['impact']}")
                else:
                    st.markdown(f"**Gap {i+1}:** {gap}")
                st.divider()
    
    # Detailed results
    if st.session_state.show_details:
        st.markdown("---")
        st.markdown('<div class="sub-header">Detailed Analysis</div>', unsafe_allow_html=True)
        
        # Papers found
        if 'papers_found' in results and results['papers_found']:
            with st.expander("📚 Papers Found"):
                for i, paper in enumerate(results['papers_found']):
                    st.markdown(f"**{i+1}. {paper.get('title', 'No title')}**")
                    st.caption(f"Authors: {', '.join(paper.get('authors', ['Unknown']))}")
                    st.caption(f"Source: {paper.get('source', 'Unknown')}")
                    if 'abstract' in paper:
                        with st.expander("Abstract"):
                            st.write(paper['abstract'])
                    st.divider()
        
        # Data analysis
        if 'data_analysis_summary' in results:
            with st.expander("📊 Data Analysis"):
                st.markdown(results['data_analysis_summary'])
        
        # Performance metrics
        if 'performance_report' in results:
            with st.expander("⚙️ Performance Metrics"):
                st.markdown(results['performance_report'])
        
        # Verification results
        if 'verification_results' in results:
            with st.expander("✅ Verification Results"):
                verification = results['verification_results']
                confidence = verification.get('overall_confidence', 0)
                st.metric("Overall Confidence", f"{confidence:.2f}/1.00")
                
                if confidence < 0.7:
                    st.warning("Analysis confidence is below recommended threshold. Consider refining your query.")
        
        # Logs
        with st.expander("📋 System Logs"):
            st.text_area("Execution Logs", log_capture.getvalue(), height=300)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6c757d;'>
    <p>Research Collaborative System • Multi-Agent Research Assistant</p>
    <p>Powered by LangGraph, Gemini/Groq LLMs, and Streamlit</p>
</div>
""", unsafe_allow_html=True)