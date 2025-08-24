"""
Bidirectional communication system for agent collaboration
"""
from typing import Dict, Any, List, Optional
from loguru import logger
from enum import Enum

class MessageType(Enum):
    REQUEST_ASSISTANCE = "request_assistance"
    ESCALATE_TASK = "escalate_task"
    SHARE_RESOURCE = "share_resource"
    REQUEST_RETRY = "request_retry"
    QUALITY_CHECK = "quality_check"

class AgentMessage:
    def __init__(self, sender: str, recipient: str, message_type: MessageType, content: Dict[str, Any]):
        self.sender = sender
        self.recipient = recipient
        self.message_type = message_type
        self.content = content
        self.timestamp = None

class CommunicationBus:
    """Central communication hub for agent interactions"""
    
    def __init__(self):
        self.message_queue: List[AgentMessage] = []
        self.agent_registry = {
            'literature_scanner': ['data_analyzer', 'analysis_agent'],
            'analysis_agent': ['literature_scanner', 'hypothesis_generator'],
            'data_analyzer': ['literature_scanner', 'analysis_agent'],
            'hypothesis_generator': ['analysis_agent', 'publication_assistant'],
            'publication_assistant': ['analysis_agent', 'hypothesis_generator']
        }
    
    def send_message(self, message: AgentMessage, state: Dict[str, Any]) -> Dict[str, Any]:
        """Send message between agents"""
        logger.info(f"📨 {message.sender} → {message.recipient}: {message.message_type.value}")
        
        # Route message to appropriate handler
        if message.message_type == MessageType.REQUEST_ASSISTANCE:
            return self._handle_assistance_request(message, state)
        elif message.message_type == MessageType.ESCALATE_TASK:
            return self._handle_task_escalation(message, state)
        elif message.message_type == MessageType.QUALITY_CHECK:
            return self._handle_quality_check(message, state)
        
        return state
    
    def _handle_assistance_request(self, message: AgentMessage, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle requests for assistance between agents"""
        sender = message.sender
        recipient = message.recipient
        request_type = message.content.get('request_type', '')
        
        logger.info(f"🤝 Processing assistance request: {request_type}")
        
        # Literature Scanner requests
        if sender == 'analysis_agent' and recipient == 'literature_scanner':
            if request_type == 'more_papers':
                return self._request_additional_papers(message, state)
        
        # Analysis Agent requests
        elif sender == 'hypothesis_generator' and recipient == 'analysis_agent':
            if request_type == 'deeper_analysis':
                return self._request_deeper_analysis(message, state)
        
        # Data Analyzer requests
        elif sender == 'publication_assistant' and recipient == 'data_analyzer':
            if request_type == 'statistical_summary':
                return self._request_statistical_summary(message, state)
        
        return state
    
    def _handle_task_escalation(self, message: AgentMessage, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle task escalation when agents need help"""
        escalation_reason = message.content.get('reason', '')
        complexity_level = message.content.get('complexity', 'medium')
        
        logger.warning(f"⚠️ Task escalation from {message.sender}: {escalation_reason}")
        
        # Add escalation to state for workflow awareness
        if 'escalations' not in state:
            state['escalations'] = []
        
        state['escalations'].append({
            'sender': message.sender,
            'reason': escalation_reason,
            'complexity': complexity_level,
            'timestamp': message.timestamp
        })
        
        # Trigger additional processing based on escalation
        if complexity_level == 'high':
            state['requires_human_review'] = True
        
        return state
    
    def _handle_quality_check(self, message: AgentMessage, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle quality check requests between agents"""
        check_type = message.content.get('check_type', '')
        content_to_check = message.content.get('content', '')
        
        logger.info(f"🔍 Quality check requested: {check_type}")
        
        # Perform quality validation
        quality_score = self._calculate_quality_score(content_to_check, check_type)
        
        # Add quality assessment to state
        if 'quality_assessments' not in state:
            state['quality_assessments'] = []
        
        state['quality_assessments'].append({
            'checker': message.recipient,
            'content_type': check_type,
            'quality_score': quality_score,
            'passed': quality_score >= 0.7
        })
        
        return state
    
    def _request_additional_papers(self, message: AgentMessage, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request for additional papers"""
        current_papers = len(state.get('papers_found', []))
        requested_count = message.content.get('additional_count', 3)
        
        logger.info(f"📚 Requesting {requested_count} additional papers (current: {current_papers})")
        
        # Mark for additional literature search
        state['needs_additional_papers'] = True
        state['additional_papers_requested'] = requested_count
        
        # Add to next actions
        next_actions = state.get('next_actions', [])
        next_actions.append('search_additional_papers')
        state['next_actions'] = next_actions
        
        return state
    
    def _request_deeper_analysis(self, message: AgentMessage, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request for deeper analysis"""
        analysis_type = message.content.get('analysis_type', 'general')
        focus_areas = message.content.get('focus_areas', [])
        
        logger.info(f"🔬 Requesting deeper analysis: {analysis_type}")
        
        # Mark for enhanced analysis
        state['needs_deeper_analysis'] = True
        state['analysis_focus_areas'] = focus_areas
        
        return state
    
    def _request_statistical_summary(self, message: AgentMessage, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request for statistical summary"""
        summary_type = message.content.get('summary_type', 'basic')
        
        logger.info(f"📊 Requesting statistical summary: {summary_type}")
        
        # Generate enhanced statistical summary
        if 'quantitative_insights' in state:
            insights = state['quantitative_insights']
            enhanced_summary = self._create_enhanced_statistical_summary(insights, summary_type)
            state['enhanced_statistical_summary'] = enhanced_summary
        
        return state
    
    def _calculate_quality_score(self, content: str, check_type: str) -> float:
        """Calculate quality score for content"""
        if not content:
            return 0.0
        
        # Basic quality metrics
        length_score = min(len(content) / 500, 1.0)  # Optimal around 500 chars
        
        # Content-specific scoring
        if check_type == 'hypothesis':
            # Check for testability indicators
            testability_keywords = ['measure', 'compare', 'evaluate', 'test', 'validate']
            keyword_score = sum(1 for keyword in testability_keywords if keyword in content.lower()) / len(testability_keywords)
            return (length_score + keyword_score) / 2
        
        elif check_type == 'analysis':
            # Check for analytical depth
            analysis_keywords = ['gap', 'trend', 'pattern', 'relationship', 'finding']
            keyword_score = sum(1 for keyword in analysis_keywords if keyword in content.lower()) / len(analysis_keywords)
            return (length_score + keyword_score) / 2
        
        return length_score
    
    def _create_enhanced_statistical_summary(self, insights: Dict[str, Any], summary_type: str) -> str:
        """Create enhanced statistical summary"""
        if summary_type == 'detailed':
            return f"""Enhanced Statistical Analysis:
- Papers Analyzed: {insights.get('paper_count', 0)}
- Author Network Size: {insights.get('total_authors', 0)}
- Average Abstract Complexity: {insights.get('average_abstract_length', 0):.1f} words
- Research Velocity: {insights.get('publication_trend', 'stable')}
- Domain Coverage: {insights.get('domain_diversity', 'moderate')}"""
        
        return "Basic statistical summary available"

# Global communication bus
communication_bus = CommunicationBus()
