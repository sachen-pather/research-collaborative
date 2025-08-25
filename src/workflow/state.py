"""
Enhanced state management for the Research Collaborative system - FIXED
"""
from typing import TypedDict, List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
import json

class Paper(BaseModel):
    """Represents a research paper with enhanced validation"""
    title: str = Field(..., min_length=1, description="Paper title")
    authors: List[str] = Field(default_factory=list, description="List of authors")
    abstract: str = Field(default="", description="Paper abstract")
    url: str = Field(default="", description="Paper URL")
    source: str = Field(default="unknown", description="Source database (arxiv, pubmed, web)")
    published_date: Optional[str] = Field(None, description="Publication date")
    doi: Optional[str] = Field(None, description="Digital Object Identifier")
    keywords: List[str] = Field(default_factory=list, description="Associated keywords")
    
    @validator('authors', pre=True)
    def validate_authors(cls, v):
        """Ensure authors is always a list"""
        if isinstance(v, str):
            return [v]
        elif v is None:
            return []
        return v
    
    @validator('keywords', pre=True)
    def validate_keywords(cls, v):
        """Ensure keywords is always a list"""
        if isinstance(v, str):
            return v.split(',') if ',' in v else [v]
        elif v is None:
            return []
        return v

class ResearchTheme(BaseModel):
    """Represents a research theme with trajectory analysis"""
    theme: str = Field(..., description="Theme name")
    trajectory: str = Field(default="Stable development", description="Development trajectory")
    confidence: float = Field(default=0.7, ge=0.0, le=1.0, description="Confidence score")
    supporting_papers: List[str] = Field(default_factory=list, description="Supporting paper titles")
    
class ResearchGap(BaseModel):
    """Represents an identified research gap with impact assessment"""
    description: str = Field(..., description="Gap description")
    impact: str = Field(default="Medium", description="Impact level (High/Medium/Low)")
    reason: str = Field(default="Literature analysis", description="Reason for gap")
    confidence: float = Field(default=0.7, ge=0.0, le=1.0, description="Confidence score")
    related_papers: List[str] = Field(default_factory=list, description="Related paper titles")
    supporting_evidence: List[str] = Field(default_factory=list, description="Supporting evidence")

class Contradiction(BaseModel):
    """Represents a research contradiction with resolution suggestions"""
    contradiction: str = Field(..., description="Description of contradiction")
    resolution_suggestion: str = Field(default="Further research needed", description="Suggested resolution")
    confidence: float = Field(default=0.7, ge=0.0, le=1.0, description="Confidence score")
    conflicting_papers: List[str] = Field(default_factory=list, description="Papers with conflicting findings")

class MethodologicalTrends(BaseModel):
    """Represents methodological trends in the research area"""
    common_methods: List[str] = Field(default_factory=list, description="Commonly used methods")
    emerging_methods: List[str] = Field(default_factory=list, description="Emerging methodological approaches")
    limitations: List[str] = Field(default_factory=list, description="Methodological limitations")
    recommendations: List[str] = Field(default_factory=list, description="Methodological recommendations")

class EvidenceStrength(BaseModel):
    """Represents overall evidence strength assessment"""
    strength_assessment: str = Field(default="Moderate", description="Overall strength (Strong/Moderate/Weak/Limited)")
    influencing_factors: List[str] = Field(default_factory=list, description="Factors influencing evidence strength")
    sample_size_adequacy: str = Field(default="Unknown", description="Sample size adequacy assessment")
    study_quality: str = Field(default="Mixed", description="Overall study quality")

class Hypothesis(BaseModel):
    """Represents a research hypothesis with experimental design"""
    statement: str = Field(..., description="Hypothesis statement")
    rationale: str = Field(default="", description="Rationale for hypothesis")
    experimental_design: str = Field(default="", description="Proposed experimental design")
    required_resources: str = Field(default="", description="Required resources")
    expected_outcomes: str = Field(default="", description="Expected outcomes")
    testability: str = Field(default="Medium", description="Testability level (High/Medium/Low)")

class StrategicInsights(BaseModel):
    """Represents strategic insights and recommendations"""
    research_opportunities: List[Dict[str, Any]] = Field(default_factory=list)
    methodological_recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    collaboration_suggestions: List[str] = Field(default_factory=list)
    funding_priorities: List[str] = Field(default_factory=list)
    timeline_assessment: Dict[str, str] = Field(default_factory=dict)
    risk_factors: List[str] = Field(default_factory=list)

class WorkflowMetrics(BaseModel):
    """Represents workflow execution metrics"""
    total_execution_time: float = Field(default=0.0, description="Total execution time in seconds")
    papers_processed: int = Field(default=0, description="Number of papers processed")
    llm_calls_made: int = Field(default=0, description="Number of LLM calls made")
    cache_hits: int = Field(default=0, description="Number of cache hits")
    success_rate: float = Field(default=1.0, ge=0.0, le=1.0, description="Success rate")
    
class ResearchState(TypedDict, total=False):
    """Enhanced state for the research workflow with proper typing"""
    # Input
    query: str
    
    # Papers and results
    papers_found: List[Dict[str, Any]]  # Raw paper data from search
    processed_papers: List[Paper]  # Validated paper objects
    total_papers_found: int
    
    # Analysis results (enhanced structures)
    key_themes: List[Union[ResearchTheme, Dict[str, Any], str]]
    research_gaps: List[Union[ResearchGap, Dict[str, Any], str]]
    contradictions: List[Union[Contradiction, Dict[str, Any], str]]
    methodological_trends: Union[MethodologicalTrends, Dict[str, Any]]
    evidence_strength: Union[EvidenceStrength, Dict[str, Any]]
    
    # Synthesis and outputs
    analysis_summary: str
    strategic_insights: Union[StrategicInsights, Dict[str, Any]]
    hypotheses: List[Union[Hypothesis, Dict[str, Any]]]
    
    # Enhanced publication outputs
    executive_summary: Optional[str]
    detailed_research_plan: Optional[str]
    comprehensive_research_report: Optional[str]
    strategic_recommendations: List[Dict[str, Any]]
    enhanced_outputs_generated: bool
    
    # Workflow control
    current_step: str
    completed_steps: List[str]
    next_actions: List[str]
    
    # Quality and verification
    analysis_completed: bool
    verification_results: Dict[str, Any]
    verification_report: Optional[str]
    quality_assessments: List[Dict[str, Any]]
    
    # Error handling and recovery
    errors: List[str]
    retry_counts: Dict[str, int]
    recovery_applied: bool
    escalations: List[Dict[str, Any]]
    
    # Metrics and monitoring
    workflow_metrics: Union[WorkflowMetrics, Dict[str, Any]]
    communications_sent: int
    workflow_completed: bool
    performance_report: Optional[str]
    
    # Metadata
    timestamp: datetime
    llm_usage: Dict[str, int]

def create_initial_state(query: str) -> ResearchState:
    """Create initial state for research workflow with proper initialization"""
    return ResearchState(
        query=query,
        papers_found=[],
        processed_papers=[],
        total_papers_found=0,
        
        # Initialize analysis results
        key_themes=[],
        research_gaps=[],
        contradictions=[],
        methodological_trends={},
        evidence_strength={},
        
        # Initialize outputs
        analysis_summary="",
        strategic_insights={},
        hypotheses=[],
        
        # Enhanced outputs
        executive_summary=None,
        detailed_research_plan=None,
        comprehensive_research_report=None,
        strategic_recommendations=[],
        enhanced_outputs_generated=False,
        
        # Workflow control
        current_step="literature_search",
        completed_steps=[],
        next_actions=["search_arxiv"],
        
        # Quality control
        analysis_completed=False,
        verification_results={},
        verification_report=None,
        quality_assessments=[],
        
        # Error handling
        errors=[],
        retry_counts={},
        recovery_applied=False,
        escalations=[],
        
        # Metrics
        workflow_metrics=WorkflowMetrics().dict(),
        communications_sent=0,
        workflow_completed=False,
        performance_report=None,
        
        # Metadata
        timestamp=datetime.now(),
        llm_usage={}
    )

def validate_state(state: ResearchState) -> ResearchState:
    """Validate and clean up state structure"""
    # Ensure required fields exist
    if 'query' not in state or not state['query']:
        state['query'] = "Unknown research query"
    
    # Ensure lists are properly initialized
    list_fields = [
        'papers_found', 'processed_papers', 'key_themes', 'research_gaps',
        'contradictions', 'hypotheses', 'completed_steps', 'next_actions',
        'errors', 'quality_assessments', 'escalations', 'strategic_recommendations'
    ]
    
    for field in list_fields:
        if field not in state or not isinstance(state[field], list):
            state[field] = []
    
    # Ensure dict fields are properly initialized
    dict_fields = [
        'methodological_trends', 'evidence_strength', 'strategic_insights',
        'verification_results', 'retry_counts', 'workflow_metrics', 'llm_usage'
    ]
    
    for field in dict_fields:
        if field not in state or not isinstance(state[field], dict):
            state[field] = {}
    
    # Ensure string fields have default values
    string_fields = {
        'analysis_summary': "",
        'current_step': "literature_search",
        'executive_summary': None,
        'detailed_research_plan': None,
        'comprehensive_research_report': None,
        'verification_report': None,
        'performance_report': None
    }
    
    for field, default_value in string_fields.items():
        if field not in state:
            state[field] = default_value
    
    # Ensure boolean fields have default values
    boolean_fields = {
        'analysis_completed': False,
        'enhanced_outputs_generated': False,
        'recovery_applied': False,
        'workflow_completed': False
    }
    
    for field, default_value in boolean_fields.items():
        if field not in state or not isinstance(state[field], bool):
            state[field] = default_value
    
    # Ensure numeric fields have default values
    numeric_fields = {
        'total_papers_found': 0,
        'communications_sent': 0
    }
    
    for field, default_value in numeric_fields.items():
        if field not in state or not isinstance(state[field], (int, float)):
            state[field] = default_value
    
    # Ensure timestamp exists
    if 'timestamp' not in state:
        state['timestamp'] = datetime.now()
    
    return state

def safe_get_list(state: ResearchState, key: str, default: list = None) -> list:
    """Safely get list value from state"""
    if default is None:
        default = []
    
    value = state.get(key, default)
    return value if isinstance(value, list) else default

def safe_get_dict(state: ResearchState, key: str, default: dict = None) -> dict:
    """Safely get dict value from state"""
    if default is None:
        default = {}
    
    value = state.get(key, default)
    return value if isinstance(value, dict) else default

def safe_get_string(state: ResearchState, key: str, default: str = "") -> str:
    """Safely get string value from state"""
    value = state.get(key, default)
    return str(value) if value is not None else default

def update_state_metrics(state: ResearchState, execution_time: float = 0.0, llm_calls: int = 0) -> ResearchState:
    """Update state metrics safely"""
    
    # Get current metrics or initialize
    metrics = safe_get_dict(state, 'workflow_metrics')
    
    # Update metrics
    metrics['total_execution_time'] = metrics.get('total_execution_time', 0.0) + execution_time
    metrics['papers_processed'] = len(safe_get_list(state, 'papers_found'))
    metrics['llm_calls_made'] = metrics.get('llm_calls_made', 0) + llm_calls
    
    # Calculate success rate
    completed_steps = len(safe_get_list(state, 'completed_steps'))
    errors = len(safe_get_list(state, 'errors'))
    total_operations = completed_steps + errors
    
    if total_operations > 0:
        metrics['success_rate'] = completed_steps / total_operations
    else:
        metrics['success_rate'] = 1.0
    
    state['workflow_metrics'] = metrics
    return state

def serialize_state_for_storage(state: ResearchState) -> str:
    """Serialize state for storage with proper JSON handling"""
    # Create a copy and convert datetime objects
    serializable_state = {}
    
    for key, value in state.items():
        if isinstance(value, datetime):
            serializable_state[key] = value.isoformat()
        elif hasattr(value, 'dict'):  # Pydantic models
            serializable_state[key] = value.dict()
        else:
            serializable_state[key] = value
    
    return json.dumps(serializable_state, indent=2)

def deserialize_state_from_storage(json_str: str) -> ResearchState:
    """Deserialize state from storage with proper type conversion"""
    try:
        data = json.loads(json_str)
        
        # Convert ISO datetime strings back to datetime objects
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        # Validate and return
        return validate_state(data)
        
    except (json.JSONDecodeError, ValueError) as e:
        # Return a basic state if deserialization fails
        return create_initial_state("Error in state deserialization")

# Export main functions and classes
__all__ = [
    'ResearchState', 'Paper', 'ResearchTheme', 'ResearchGap', 'Contradiction',
    'MethodologicalTrends', 'EvidenceStrength', 'Hypothesis', 'StrategicInsights',
    'WorkflowMetrics', 'create_initial_state', 'validate_state', 'safe_get_list',
    'safe_get_dict', 'safe_get_string', 'update_state_metrics',
    'serialize_state_for_storage', 'deserialize_state_from_storage'
]