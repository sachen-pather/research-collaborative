"""
Enhanced base agent class with bidirectional communication
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
from workflow.communication import communication_bus, AgentMessage, MessageType

class BaseAgent(ABC):
    """Enhanced base class with bidirectional communication capabilities"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.llm = llm_config.get_primary_llm()
        self.fast_llm = llm_config.get_fast_llm()
        self.communication_bus = communication_bus
        
    @abstractmethod
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's primary function"""
        pass
    
    def request_assistance(self, recipient: str, request_type: str, content: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        """Request assistance from another agent"""
        message = AgentMessage(
            sender=self.name.lower().replace(' ', '_'),
            recipient=recipient,
            message_type=MessageType.REQUEST_ASSISTANCE,
            content={'request_type': request_type, **content}
        )
        
        return self.communication_bus.send_message(message, state)
    
    def escalate_task(self, reason: str, complexity: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Escalate complex task to workflow coordinator"""
        message = AgentMessage(
            sender=self.name.lower().replace(' ', '_'),
            recipient='workflow_coordinator',
            message_type=MessageType.ESCALATE_TASK,
            content={'reason': reason, 'complexity': complexity}
        )
        
        return self.communication_bus.send_message(message, state)
    
    def request_quality_check(self, recipient: str, content: str, check_type: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Request quality check from another agent"""
        message = AgentMessage(
            sender=self.name.lower().replace(' ', '_'),
            recipient=recipient,
            message_type=MessageType.QUALITY_CHECK,
            content={'content': content, 'check_type': check_type}
        )
        
        return self.communication_bus.send_message(message, state)
    
    def _assess_task_complexity(self, task_data: Any) -> str:
        """Assess complexity of current task"""
        if isinstance(task_data, list):
            if len(task_data) > 10:
                return 'high'
            elif len(task_data) > 5:
                return 'medium'
            else:
                return 'low'
        
        return 'medium'
    
    def _should_request_assistance(self, state: Dict[str, Any]) -> bool:
        """Determine if assistance should be requested"""
        errors = state.get('errors', [])
        current_step_errors = [e for e in errors if self.name.lower() in e.lower()]
        
        # Request help if multiple errors in current agent
        if len(current_step_errors) >= 2:
            return True
        
        # Request help if insufficient data
        papers = state.get('papers_found', [])
        if len(papers) < 3:
            return True
        
        return False
    
    def _log_execution_start(self, state: Dict[str, Any]):
        """Enhanced logging with communication awareness"""
        logger.info(f"🤖 {self.name} starting execution for query: '{state['query'][:50]}...'")
        
        # Check for pending communications
        pending_requests = state.get('communication_requests', [])
        if pending_requests:
            logger.info(f"📨 {len(pending_requests)} pending communications")
    
    def _log_execution_end(self, state: Dict[str, Any], execution_time: float):
        """Enhanced logging with performance metrics"""
        logger.info(f"✅ {self.name} completed in {execution_time:.2f}s")
        
        # Update processing time in state
        if 'processing_time' not in state:
            state['processing_time'] = {}
        state['processing_time'][self.name.lower()] = execution_time
        
        # Log communication activities
        communications_sent = state.get('communications_sent', 0)
        if communications_sent > 0:
            logger.info(f"📤 Sent {communications_sent} inter-agent messages")
    
    def _handle_error_with_communication(self, state: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        """Enhanced error handling with communication escalation"""
        error_msg = f"{self.name} error: {str(error)}"
        logger.error(error_msg)
        
        if 'errors' not in state:
            state['errors'] = []
        state['errors'].append(error_msg)
        
        # Assess if escalation is needed
        error_count = len([e for e in state['errors'] if self.name in e])
        if error_count >= 2:
            # Escalate to workflow coordinator
            state = self.escalate_task(
                reason=f"Multiple failures in {self.name}",
                complexity='high',
                state=state
            )
        
        return state
    
    def execute_with_monitoring(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with enhanced monitoring and communication"""
        start_time = time.time()
        
        try:
            self._log_execution_start(state)
            
            # Check if assistance was requested
            if self._should_request_assistance(state):
                state = self._handle_assistance_requests(state)
            
            # Update current step
            state['current_step'] = self.name.lower().replace(' ', '_')
            
            # Execute the agent
            result_state = self.execute(state)
            
            # Perform quality self-assessment
            result_state = self._perform_self_assessment(result_state)
            
            # Mark step as completed
            if 'completed_steps' not in result_state:
                result_state['completed_steps'] = []
            result_state['completed_steps'].append(self.name.lower().replace(' ', '_'))
            
            execution_time = time.time() - start_time
            self._log_execution_end(result_state, execution_time)
            
            return result_state
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ {self.name} failed after {execution_time:.2f}s: {e}")
            return self._handle_error_with_communication(state, e)
    
    def _handle_assistance_requests(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle assistance requests based on agent type"""
        # This will be overridden by specific agents
        return state
    
    def _perform_self_assessment(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Perform self-assessment of output quality"""
        # Basic self-assessment - can be enhanced by specific agents
        agent_key = self.name.lower().replace(' ', '_')
        
        # Track quality metrics
        if 'quality_metrics' not in state:
            state['quality_metrics'] = {}
        
        # Simple quality assessment
        errors = state.get('errors', [])
        agent_errors = [e for e in errors if agent_key in e.lower()]
        
        quality_score = 1.0 - (len(agent_errors) * 0.2)  # Deduct 0.2 per error
        quality_score = max(0.0, min(1.0, quality_score))  # Clamp between 0-1
        
        state['quality_metrics'][agent_key] = {
            'quality_score': quality_score,
            'error_count': len(agent_errors),
            'self_assessed': True
        }
        
        return state
