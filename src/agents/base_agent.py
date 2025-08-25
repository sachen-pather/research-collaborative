"""
Enhanced base agent class with bidirectional communication - COMPLETE
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import time
from loguru import logger

# Import communication system
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from utils.llm_config import llm_config

class BaseAgent(ABC):
    """Enhanced base class with bidirectional communication capabilities"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.llm = llm_config.get_primary_llm()
        self.fast_llm = llm_config.get_fast_llm()
        self.agent_id = name.lower().replace(' ', '_')
        
        # Try to initialize communication system
        try:
            from workflow.communication import communication_bus
            self.communication_bus = communication_bus
            self.communication_available = True
            logger.debug(f"Communication system available for {self.name}")
        except ImportError:
            self.communication_bus = None
            self.communication_available = False
            logger.debug(f"Communication system not available for {self.name}")
        
    @abstractmethod
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's primary function"""
        pass
    
    def request_assistance_with_fallback(self, recipient: str, request_type: str, content: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        """Request assistance with fallback for missing communication system"""
        
        # Try to use your communication system
        if self.communication_available:
            try:
                from workflow.communication import AgentMessage, MessageType
                
                message = AgentMessage(
                    sender=self.agent_id,
                    recipient=recipient,
                    message_type=MessageType.REQUEST_ASSISTANCE,
                    content={'request_type': request_type, **content}
                )
                
                result_state = self.communication_bus.send_message(message, state)
                logger.info(f"📨 Assistance request sent: {request_type} from {self.name} to {recipient}")
                return result_state
                
            except Exception as e:
                logger.warning(f"Communication system error: {e}, using fallback")
        
        # Fallback: Add request to state for manual handling
        logger.info(f"📋 Fallback assistance request: {request_type}")
        
        if 'assistance_requests' not in state:
            state['assistance_requests'] = []
        
        state['assistance_requests'].append({
            'sender': self.name,
            'recipient': recipient,
            'request_type': request_type,
            'content': content,
            'timestamp': time.time()
        })
        
        # Handle some basic requests directly
        if request_type == 'more_papers' and recipient == 'literature_scanner':
            state['needs_additional_papers'] = True
            state['additional_papers_requested'] = content.get('additional_count', 3)
            logger.info("📚 Marked for additional paper search")
            
        elif request_type == 'deeper_analysis' and recipient == 'analysis_agent':
            state['needs_deeper_analysis'] = True
            state['analysis_focus_areas'] = content.get('focus_areas', [])
            logger.info("🔬 Marked for deeper analysis")
            
        elif request_type == 'statistical_summary' and recipient == 'data_analyzer':
            state['needs_statistical_summary'] = True
            logger.info("📊 Marked for enhanced statistical summary")
        
        return state
    
    def escalate_task_with_fallback(self, reason: str, complexity: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Escalate task with fallback handling"""
        
        if self.communication_available:
            try:
                from workflow.communication import AgentMessage, MessageType
                
                message = AgentMessage(
                    sender=self.agent_id,
                    recipient='workflow_coordinator',
                    message_type=MessageType.ESCALATE_TASK,
                    content={'reason': reason, 'complexity': complexity}
                )
                
                result_state = self.communication_bus.send_message(message, state)
                logger.warning(f"🚨 Task escalated: {reason}")
                return result_state
                
            except Exception as e:
                logger.warning(f"Communication system error for escalation: {e}")
        
        # Fallback escalation handling
        logger.warning(f"⚠️ Task escalation (fallback): {reason}")
        
        if 'escalations' not in state:
            state['escalations'] = []
        
        state['escalations'].append({
            'sender': self.name,
            'reason': reason,
            'complexity': complexity,
            'timestamp': time.time(),
            'method': 'fallback'
        })
        
        # Set flags for high complexity issues
        if complexity == 'high':
            state['requires_manual_review'] = True
            state['workflow_attention_needed'] = True
        
        return state
    
    def request_quality_check_with_fallback(self, content: str, check_type: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Request quality check with fallback"""
        
        if self.communication_available:
            try:
                from workflow.communication import AgentMessage, MessageType
                
                message = AgentMessage(
                    sender=self.agent_id,
                    recipient='quality_assessor',
                    message_type=MessageType.QUALITY_CHECK,
                    content={'content': content[:500], 'check_type': check_type}
                )
                
                result_state = self.communication_bus.send_message(message, state)
                logger.info(f"🔍 Quality check requested for {check_type}")
                return result_state
                
            except Exception as e:
                logger.warning(f"Communication system error for quality check: {e}")
        
        # Fallback quality assessment
        logger.info(f"🔍 Performing self quality check for {check_type}")
        return self._perform_self_quality_check(content, check_type, state)
    
    def _perform_self_quality_check(self, content: str, check_type: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Perform self quality check when communication system unavailable"""
        if not content:
            quality_score = 0.0
            feedback = f"No content provided for {check_type} quality check"
        elif len(content) < 50:
            quality_score = 0.4
            feedback = f"{check_type} content is very brief - consider expanding"
        elif len(content) < 200:
            quality_score = 0.7
            feedback = f"{check_type} content is adequate but could be more comprehensive"
        else:
            quality_score = 0.8
            feedback = f"{check_type} content appears comprehensive"
        
        # Add quality assessment to state
        if 'quality_assessments' not in state:
            state['quality_assessments'] = []
        
        state['quality_assessments'].append({
            'agent': self.name,
            'check_type': check_type,
            'score': quality_score,
            'method': 'self_check',
            'timestamp': time.time(),
            'feedback': feedback,
            'passed': quality_score >= 0.6
        })
        
        return state
    
    def _assess_task_complexity(self, task_data: Any) -> str:
        """Assess complexity of current task"""
        if isinstance(task_data, list):
            if len(task_data) > 15:
                return 'high'
            elif len(task_data) > 8:
                return 'medium'
            else:
                return 'low'
        elif isinstance(task_data, dict):
            if len(task_data) > 10:
                return 'high'
            elif len(task_data) > 5:
                return 'medium'
            else:
                return 'low'
        elif isinstance(task_data, str):
            if len(task_data) > 1000:
                return 'high'
            elif len(task_data) > 500:
                return 'medium'
            else:
                return 'low'
        
        return 'medium'
    
    def _should_request_assistance(self, state: Dict[str, Any]) -> bool:
        """Determine if assistance should be requested"""
        # Check error history for this agent
        errors = state.get('errors', [])
        agent_errors = [e for e in errors if self.name.lower() in e.lower()]
        
        # Request help if multiple errors from this agent
        if len(agent_errors) >= 2:
            logger.info(f"{self.name} considering assistance due to {len(agent_errors)} errors")
            return True
        
        # Check data sufficiency
        papers = state.get('papers_found', [])
        if len(papers) < 2:
            logger.info(f"{self.name} considering assistance due to insufficient papers ({len(papers)})")
            return True
        
        # Check if previous steps had quality issues
        quality_assessments = state.get('quality_assessments', [])
        if quality_assessments:
            recent_scores = [qa.get('score', 1.0) for qa in quality_assessments[-2:]]
            avg_score = sum(recent_scores) / len(recent_scores)
            if avg_score < 0.6:
                logger.info(f"{self.name} considering assistance due to low quality scores")
                return True
        
        return False
    
    def _log_execution_start(self, state: Dict[str, Any]):
        """Enhanced logging with communication awareness"""
        query = state.get('query', 'Unknown query')
        logger.info(f"🤖 {self.name} starting execution for query: '{query[:50]}...'")
        
        # Log current state metrics
        papers_count = len(state.get('papers_found', []))
        errors_count = len(state.get('errors', []))
        completed_count = len(state.get('completed_steps', []))
        
        logger.debug(f"📊 State: {papers_count} papers, {errors_count} errors, {completed_count} completed steps")
        
        # Check for pending communications
        if self.communication_available and state.get('communications'):
            pending = len([c for c in state['communications'] if c.get('sender') != self.agent_id])
            if pending > 0:
                logger.info(f"📨 {pending} pending communications in system")
    
    def _log_execution_end(self, state: Dict[str, Any], execution_time: float):
        """Enhanced logging with performance metrics"""
        logger.info(f"✅ {self.name} completed in {execution_time:.2f}s")
        
        # Update processing time in state
        if 'processing_times' not in state:
            state['processing_times'] = {}
        state['processing_times'][self.agent_id] = execution_time
        
        # Log communication activities if available
        if self.communication_available and state.get('communications'):
            sent_messages = len([c for c in state['communications'] if c.get('sender') == self.agent_id])
            if sent_messages > 0:
                logger.info(f"📤 Sent {sent_messages} inter-agent messages")
    
    def _handle_error_with_communication(self, state: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        """Enhanced error handling with communication escalation"""
        error_msg = f"{self.name} error: {str(error)}"
        logger.error(error_msg)
        
        # Add to state errors
        if 'errors' not in state:
            state['errors'] = []
        state['errors'].append(error_msg)
        
        # Assess if escalation is needed
        agent_errors = [e for e in state['errors'] if self.name in e]
        if len(agent_errors) >= 2:
            logger.warning(f"Multiple errors in {self.name}, escalating")
            try:
                state = self.escalate_task_with_fallback(
                    reason=f"Multiple failures in {self.name}: {len(agent_errors)} errors",
                    complexity='high',
                    state=state
                )
            except Exception as esc_error:
                logger.error(f"Failed to escalate task: {esc_error}")
        
        return state
    
    def execute_with_monitoring(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with enhanced monitoring and communication"""
        start_time = time.time()
        
        try:
            self._log_execution_start(state)
            
            # Pre-execution validation
            if not self._validate_input_state(state):
                raise ValueError("Invalid input state for agent execution")
            
            # Check if assistance was requested or should be requested
            if self._should_request_assistance(state):
                state = self._handle_assistance_requests(state)
            
            # Update current step
            state['current_step'] = self.agent_id
            
            # Execute the agent with timeout protection
            execution_timeout = 300  # 5 minutes
            result_state = self._execute_with_timeout(state, execution_timeout)
            
            # Perform quality self-assessment
            result_state = self._perform_self_assessment(result_state)
            
            # Mark step as completed
            if 'completed_steps' not in result_state:
                result_state['completed_steps'] = []
            
            if self.agent_id not in result_state['completed_steps']:
                result_state['completed_steps'].append(self.agent_id)
            
            # Update success metrics
            result_state = self._update_success_metrics(result_state)
            
            execution_time = time.time() - start_time
            self._log_execution_end(result_state, execution_time)
            
            return result_state
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ {self.name} failed after {execution_time:.2f}s: {e}")
            return self._handle_error_with_communication(state, e)
    
    def _execute_with_timeout(self, state: Dict[str, Any], timeout: int) -> Dict[str, Any]:
        """Execute agent with timeout protection"""
        start_time = time.time()
        
        result_state = self.execute(state)
        
        execution_time = time.time() - start_time
        if execution_time > timeout:
            logger.warning(f"{self.name} execution time ({execution_time:.2f}s) exceeded timeout ({timeout}s)")
        
        return result_state
    
    def _validate_input_state(self, state: Dict[str, Any]) -> bool:
        """Validate input state before execution"""
        required_fields = ['query']
        
        for field in required_fields:
            if field not in state or not state[field]:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validate query is reasonable
        query = state.get('query', '')
        if len(query) < 3:
            logger.error("Query too short for meaningful processing")
            return False
        
        return True
    
    def _handle_assistance_requests(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle assistance requests based on agent type and current issues"""
        errors = state.get('errors', [])
        agent_errors = [e for e in errors if self.name.lower() in e.lower()]
        
        if len(agent_errors) >= 2:
            # Request assistance from workflow coordinator
            state = self.request_assistance_with_fallback(
                recipient='workflow_coordinator',
                request_type='error_assistance',
                content={
                    'error_count': len(agent_errors),
                    'recent_errors': agent_errors[-2:]
                },
                state=state
            )
        
        papers_count = len(state.get('papers_found', []))
        if papers_count < 2:
            # Request assistance from literature scanner
            state = self.request_assistance_with_fallback(
                recipient='literature_scanner',
                request_type='more_papers',
                content={
                    'current_count': papers_count,
                    'additional_count': 5,
                    'reason': 'insufficient_data_for_analysis'
                },
                state=state
            )
        
        return state
    
    def _perform_self_assessment(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Perform self-assessment of output quality"""
        
        # Track quality metrics
        if 'quality_metrics' not in state:
            state['quality_metrics'] = {}
        
        # Calculate quality score based on various factors
        quality_score = self._calculate_quality_score(state)
        
        # Store assessment
        state['quality_metrics'][self.agent_id] = {
            'quality_score': quality_score,
            'self_assessed': True,
            'assessment_timestamp': time.time(),
            'assessment_method': 'self_evaluation'
        }
        
        # Request external quality check if score is low
        if quality_score < 0.6:
            output_content = self._extract_agent_output(state)
            state = self.request_quality_check_with_fallback(
                content=output_content,
                check_type=f'{self.agent_id}_output',
                state=state
            )
        
        return state
    
    def _calculate_quality_score(self, state: Dict[str, Any]) -> float:
        """Calculate quality score for this agent's output"""
        score_factors = []
        
        # Error factor - fewer errors = higher score
        errors = state.get('errors', [])
        agent_errors = [e for e in errors if self.agent_id in e.lower()]
        error_factor = max(0.0, 1.0 - (len(agent_errors) * 0.2))
        score_factors.append(error_factor)
        
        # Completeness factor - did agent complete its key outputs?
        completeness_factor = self._assess_output_completeness(state)
        score_factors.append(completeness_factor)
        
        # Time factor - reasonable execution time
        processing_times = state.get('processing_times', {})
        agent_time = processing_times.get(self.agent_id, 60)  # Default 60s
        time_factor = 1.0 if agent_time < 120 else max(0.5, 120/agent_time)
        score_factors.append(time_factor)
        
        # Overall score is weighted average
        weights = [0.4, 0.4, 0.2]  # Emphasize errors and completeness
        quality_score = sum(f * w for f, w in zip(score_factors, weights))
        
        return max(0.0, min(1.0, quality_score))
    
    def _assess_output_completeness(self, state: Dict[str, Any]) -> float:
        """Assess completeness of agent's output - override in specific agents"""
        
        if self.agent_id == 'analysis_agent':
            has_themes = bool(state.get('key_themes'))
            has_gaps = bool(state.get('research_gaps'))
            has_summary = bool(state.get('analysis_summary'))
            return (has_themes + has_gaps + has_summary) / 3.0
            
        elif self.agent_id == 'data_analyzer_agent':
            has_insights = bool(state.get('quantitative_insights'))
            has_analysis = bool(state.get('statistical_analysis'))
            has_summary = bool(state.get('data_analysis_summary'))
            return (has_insights + has_analysis + has_summary) / 3.0
            
        elif self.agent_id == 'synthesis_agent':
            has_hypotheses = bool(state.get('hypotheses'))
            has_synthesis = bool(state.get('synthesis_summary'))
            return (has_hypotheses + has_synthesis) / 2.0
            
        else:
            # Generic completeness check
            return 0.8 if self.agent_id in state.get('completed_steps', []) else 0.3
    
    def _extract_agent_output(self, state: Dict[str, Any]) -> str:
        """Extract this agent's output for quality checking"""
        if self.agent_id == 'analysis_agent':
            return state.get('analysis_summary', '')
        elif self.agent_id == 'data_analyzer_agent':
            return state.get('data_analysis_summary', '')
        elif self.agent_id == 'synthesis_agent':
            hypotheses = state.get('hypotheses', [])
            return f"Generated {len(hypotheses)} hypotheses"
        else:
            return f"Output from {self.name}"
    
    def _update_success_metrics(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Update success metrics in state"""
        if 'success_metrics' not in state:
            state['success_metrics'] = {}
        
        # Calculate success rate for this agent
        quality_score = state.get('quality_metrics', {}).get(self.agent_id, {}).get('quality_score', 0.8)
        
        state['success_metrics'][self.agent_id] = {
            'completed': True,
            'quality_score': quality_score,
            'success_rate': quality_score,  # Simple mapping for now
            'timestamp': time.time()
        }
        
        return state
