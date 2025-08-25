"""
Enhanced router logic with proper node name matching - BASED ON YOUR ORIGINAL
"""
from typing import Dict, Any, List
from loguru import logger
import time

def route_next_step(state: Dict[str, Any]) -> str:
    """
    Dynamic routing based on workflow state - ENHANCED with communication awareness
    """
    current_step = state.get('current_step', '')
    completed_steps = state.get('completed_steps', [])
    errors = state.get('errors', [])
    papers_found = state.get('papers_found', [])
    
    logger.info(f"🧭 Dynamic routing: current_step={current_step}, completed={len(completed_steps)}, papers={len(papers_found)}")
    
    # FIRST: Check for communication-based routing overrides
    comm_override = check_communication_routing(state)
    if comm_override and comm_override != "continue":
        return comm_override
    
    # Critical error handling - terminate if too many failures
    if len(errors) > 5:
        logger.warning("Too many errors, terminating workflow")
        return "end"
    
    # ENHANCED SEQUENTIAL ROUTING with dynamic decisions
    
    # 1. After literature search -> analysis
    if 'literature_scanner' in completed_steps and 'analysis_agent' not in completed_steps:
        # Check if we have sufficient papers
        if len(papers_found) == 0:
            logger.warning("No papers found, cannot proceed to analysis")
            return "end"
        logger.info("Literature search complete, routing to analysis")
        return "analysis"
    
    # 2. After analysis -> data analysis (conditional)
    if 'analysis_agent' in completed_steps and 'data_analyzer' not in completed_steps:
        analysis_summary = state.get('analysis_summary', '')
        
        # Check if analysis was successful
        if not analysis_summary or len(analysis_summary) < 50:
            logger.warning("Analysis appears incomplete, but proceeding to data analysis")
        
        logger.info("Analysis complete, routing to data analysis")
        return "data_analysis"
    
    # 3. After data analysis -> hypothesis generation
    if 'data_analyzer' in completed_steps and not any(step in completed_steps for step in ['hypothesis_generator', 'synthesis_agent']):
        # Check if we have themes and gaps for hypothesis generation
        themes = state.get('key_themes', [])
        gaps = state.get('research_gaps', [])
        
        if len(themes) == 0 and len(gaps) == 0:
            logger.warning("No themes or gaps found, but proceeding to hypothesis generation")
        
        logger.info("Data analysis complete, routing to hypothesis generation")
        return "hypothesis_generation"
    
    # 4. After hypothesis generation -> publication (FIXED TO CHECK BOTH POSSIBLE AGENT NAMES)
    hypothesis_complete = any(step in completed_steps for step in ['hypothesis_generator', 'synthesis_agent'])
    publication_not_done = 'publication_assistant' not in completed_steps
    
    if hypothesis_complete and publication_not_done:
        hypotheses = state.get('hypotheses', [])
        
        if len(hypotheses) == 0:
            logger.warning("No hypotheses generated, but proceeding to publication")
        
        logger.info("Hypothesis generation complete, routing to publication")
        return "publication"
    
    # 5. Enhanced: Check for insufficient papers and retry needed
    if (len(papers_found) < 3 and 
        'literature_retry' not in completed_steps and 
        len(completed_steps) < 2 and
        not state.get('literature_retry_attempted')):
        
        logger.info("Insufficient papers found, routing to literature retry")
        state['literature_retry_attempted'] = True
        return "literature_search"  # Route back to literature search for retry
    
    # 6. Enhanced: Gap enhancement if needed
    research_gaps = state.get('research_gaps', [])
    if (len(research_gaps) < 2 and 
        'gap_enhancement' not in completed_steps and 
        'analysis_agent' in completed_steps and
        not state.get('gap_enhancement_attempted')):
        
        logger.info("Few research gaps found, requesting deeper analysis")
        state['needs_deeper_analysis'] = True
        state['analysis_focus_areas'] = ['research_gaps', 'methodological_limitations']
        state['gap_enhancement_attempted'] = True
        return "analysis"  # Route back to analysis for enhancement
    
    # 7. Enhanced: Quality check routing
    quality_assessments = state.get('quality_assessments', [])
    if quality_assessments:
        low_quality_steps = [qa for qa in quality_assessments if qa.get('score', 1.0) < 0.6]
        if low_quality_steps and not state.get('quality_retry_attempted'):
            failed_step = low_quality_steps[0].get('agent', 'unknown')
            logger.info(f"Quality issues detected in {failed_step}, considering retry")
            state['quality_retry_attempted'] = True
            
            # Route back to failed step if possible
            if 'analysis' in failed_step.lower() and 'analysis_agent' in completed_steps:
                state['needs_deeper_analysis'] = True
                return "analysis"
            elif 'data' in failed_step.lower() and 'data_analyzer' in completed_steps:
                return "data_analysis"
    
    # 8. Check if all publication assistant steps are complete
    if 'publication_assistant' in completed_steps:
        # Check if we have the key outputs
        has_executive_summary = bool(state.get('executive_summary'))
        has_research_plan = bool(state.get('detailed_research_plan'))
        
        if not has_executive_summary and not state.get('publication_retry_attempted'):
            logger.info("Publication outputs incomplete, retrying publication")
            state['publication_retry_attempted'] = True
            # Remove from completed steps to retry
            completed_steps_copy = completed_steps.copy()
            if 'publication_assistant' in completed_steps_copy:
                completed_steps_copy.remove('publication_assistant')
            state['completed_steps'] = completed_steps_copy
            return "publication"
    
    # Default: end workflow
    logger.info("All major steps completed or no valid next step, ending workflow")
    return "end"

def should_continue(state: Dict[str, Any]) -> bool:
    """Determine if workflow should continue - ENHANCED"""
    completed_steps = state.get('completed_steps', [])
    errors = state.get('errors', [])
    
    # Stop if too many errors
    if len(errors) > 5:
        logger.warning("Too many errors, stopping workflow")
        return False
    
    # Stop if workflow has been running too long (safety check)
    start_time = state.get('workflow_start_time')
    if start_time and time.time() - start_time > 1800:  # 30 minutes
        logger.warning("Workflow timeout, stopping")
        return False
        
    # Continue if we haven't completed core steps
    core_steps = ['literature_scanner', 'analysis_agent', 'data_analyzer', 'hypothesis_generator', 'publication_assistant']
    completed_core = [step for step in completed_steps if step in core_steps]
    
    # Enhanced: also check for minimum quality requirements
    if len(completed_core) >= len(core_steps):
        # All core steps done, check if we have minimum outputs
        has_papers = len(state.get('papers_found', [])) > 0
        has_analysis = bool(state.get('analysis_summary'))
        has_hypotheses = len(state.get('hypotheses', [])) > 0
        
        if has_papers and has_analysis and has_hypotheses:
            logger.info("Core workflow completed with minimum requirements met")
            return False
        elif not state.get('final_quality_check_done'):
            # One more chance to improve quality
            state['final_quality_check_done'] = True
            return True
    
    return len(completed_core) < len(core_steps)

def check_communication_routing(state: Dict[str, Any]) -> str:
    """Check communication system for routing changes - ENHANCED"""
    
    # Clear processed flags to avoid infinite loops
    processed_flags_to_clear = []
    
    # Check if additional papers were requested
    if state.get('needs_additional_papers') and not state.get('additional_papers_processing'):
        logger.info("🔄 Additional papers requested, routing back to literature search")
        state['additional_papers_processing'] = True
        processed_flags_to_clear.append('needs_additional_papers')
        return "literature_search"
    
    # Check if deeper analysis was requested  
    if state.get('needs_deeper_analysis') and not state.get('deeper_analysis_processing'):
        logger.info("🔄 Deeper analysis requested, routing back to analysis")
        state['deeper_analysis_processing'] = True
        processed_flags_to_clear.append('needs_deeper_analysis')
        return "analysis"
    
    # Check if enhanced statistical summary was requested
    if state.get('needs_statistical_summary') and not state.get('statistical_summary_processing'):
        logger.info("🔄 Enhanced statistical summary requested, routing back to data analysis")
        state['statistical_summary_processing'] = True
        processed_flags_to_clear.append('needs_statistical_summary')
        return "data_analysis"
    
    # Clear flags after one routing cycle to prevent infinite loops
    for flag in processed_flags_to_clear:
        if state.get(flag.replace('needs_', '') + '_processing'):
            if flag in state:
                del state[flag]
    
    # Check for high-priority escalations
    escalations = state.get('escalations', [])
    if escalations:
        high_priority = [e for e in escalations if e.get('complexity') == 'high']
        if high_priority:
            logger.warning("⚠️ High priority escalation detected")
            state['requires_manual_review'] = True
            
            # Check if escalation suggests specific action
            recent_escalation = high_priority[-1]
            escalation_reason = recent_escalation.get('reason', '').lower()
            
            if 'literature' in escalation_reason or 'papers' in escalation_reason:
                logger.info("Escalation suggests literature issues, routing to literature search")
                return "literature_search"
            elif 'analysis' in escalation_reason:
                logger.info("Escalation suggests analysis issues, routing to analysis")
                return "analysis"
    
    # Check assistance requests that might affect routing
    assistance_requests = state.get('assistance_requests', [])
    if assistance_requests:
        # Check for recent unprocessed requests
        recent_requests = [req for req in assistance_requests if not req.get('processed')]
        
        for request in recent_requests[-3:]:  # Check last 3 unprocessed requests
            request_type = request.get('request_type', '')
            
            if request_type == 'more_papers':
                logger.info("📚 Unprocessed paper request found, routing to literature search")
                request['processed'] = True
                return "literature_search"
                
            elif request_type == 'deeper_analysis':
                logger.info("🔬 Unprocessed analysis request found, routing to analysis")
                request['processed'] = True
                return "analysis"
                
            elif request_type == 'statistical_summary':
                logger.info("📊 Unprocessed statistical request found, routing to data analysis")
                request['processed'] = True
                return "data_analysis"
    
    # No routing override needed
    return "continue"

def validate_routing_state(state: Dict[str, Any]) -> bool:
    """Validate state before making routing decisions"""
    required_fields = ['current_step', 'completed_steps', 'papers_found', 'query']
    
    for field in required_fields:
        if field not in state:
            logger.error(f"Missing required field for routing: {field}")
            return False
    
    # Validate types
    if not isinstance(state.get('completed_steps'), list):
        logger.error("completed_steps must be a list")
        return False
    
    if not isinstance(state.get('papers_found'), list):
        logger.error("papers_found must be a list")
        return False
    
    return True

def get_routing_metrics(state: Dict[str, Any]) -> Dict[str, Any]:
    """Get metrics about routing decisions for monitoring"""
    completed_steps = state.get('completed_steps', [])
    errors = state.get('errors', [])
    papers_found = state.get('papers_found', [])
    
    # Calculate routing metrics
    core_steps = ['literature_scanner', 'analysis_agent', 'data_analyzer', 'hypothesis_generator', 'publication_assistant']
    completed_core = [step for step in completed_steps if step in core_steps]
    
    metrics = {
        'total_steps_completed': len(completed_steps),
        'core_steps_completed': len(completed_core),
        'completion_percentage': (len(completed_core) / len(core_steps)) * 100,
        'papers_found': len(papers_found),
        'errors_encountered': len(errors),
        'routing_flags': {
            'needs_additional_papers': state.get('needs_additional_papers', False),
            'needs_deeper_analysis': state.get('needs_deeper_analysis', False),
            'requires_manual_review': state.get('requires_manual_review', False)
        },
        'retry_attempts': {
            'literature_retry': state.get('literature_retry_attempted', False),
            'gap_enhancement': state.get('gap_enhancement_attempted', False),
            'quality_retry': state.get('quality_retry_attempted', False),
            'publication_retry': state.get('publication_retry_attempted', False)
        }
    }
    
    return metrics

def suggest_next_actions(state: Dict[str, Any]) -> List[str]:
    """Suggest next actions based on current state"""
    suggestions = []
    
    completed_steps = state.get('completed_steps', [])
    papers_found = state.get('papers_found', [])
    errors = state.get('errors', [])
    
    # Papers-related suggestions
    if len(papers_found) == 0:
        suggestions.append("🔍 Search for relevant papers using different keywords")
    elif len(papers_found) < 3:
        suggestions.append("📚 Consider expanding search to find more papers")
    
    # Error-related suggestions
    if len(errors) > 2:
        suggestions.append("⚠️ Review errors and consider manual intervention")
    
    # Progress-related suggestions
    if 'literature_scanner' not in completed_steps:
        suggestions.append("📖 Start with literature search")
    elif 'analysis_agent' not in completed_steps:
        suggestions.append("🔬 Proceed with paper analysis")
    elif 'hypothesis_generator' not in completed_steps:
        suggestions.append("💡 Generate research hypotheses")
    
    # Quality-related suggestions
    quality_assessments = state.get('quality_assessments', [])
    if quality_assessments:
        low_quality = [qa for qa in quality_assessments if qa.get('score', 1.0) < 0.7]
        if low_quality:
            suggestions.append("📈 Consider improving quality of analysis outputs")
    
    return suggestions

def create_routing_report(state: Dict[str, Any]) -> str:
    """Create a comprehensive routing report"""
    metrics = get_routing_metrics(state)
    suggestions = suggest_next_actions(state)
    
    report_parts = [
        "# 🧭 Workflow Routing Report",
        "",
        f"## 📊 Progress Metrics",
        f"- **Completion**: {metrics['completion_percentage']:.1f}% ({metrics['core_steps_completed']}/{len(['literature_scanner', 'analysis_agent', 'data_analyzer', 'hypothesis_generator', 'publication_assistant'])})",
        f"- **Papers Found**: {metrics['papers_found']}",
        f"- **Errors**: {metrics['errors_encountered']}",
        "",
        "## 🚩 Active Flags",
    ]
    
    routing_flags = metrics['routing_flags']
    active_flags = [flag for flag, active in routing_flags.items() if active]
    
    if active_flags:
        for flag in active_flags:
            flag_display = flag.replace('_', ' ').title()
            report_parts.append(f"- ✅ {flag_display}")
    else:
        report_parts.append("- No active routing flags")
    
    report_parts.append("")
    
    # Retry attempts
    retry_attempts = metrics['retry_attempts']
    attempted_retries = [retry for retry, attempted in retry_attempts.items() if attempted]
    
    if attempted_retries:
        report_parts.extend([
            "## 🔄 Retry Attempts",
        ])
        for retry in attempted_retries:
            retry_display = retry.replace('_', ' ').title()
            report_parts.append(f"- {retry_display}")
        report_parts.append("")
    
    # Suggestions
    if suggestions:
        report_parts.extend([
            "## 💡 Suggested Actions",
        ])
        for suggestion in suggestions:
            report_parts.append(f"- {suggestion}")
    
    return "\n".join(report_parts)