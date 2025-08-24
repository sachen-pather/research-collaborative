"""
State management for the Research Collaborative system
"""
from typing import TypedDict, List, Dict, Optional, Any
from pydantic import BaseModel
from datetime import datetime

class Paper(BaseModel):
    """Represents a research paper"""
    title: str
    authors: List[str]
    abstract: str
    url: str
    source: str  # 'arxiv', 'pubmed', 'web'
    published_date: Optional[str] = None
    doi: Optional[str] = None
    keywords: List[str] = []

class ResearchGap(BaseModel):
    """Represents an identified research gap"""
    description: str
    confidence: float  # 0.0 to 1.0
    related_papers: List[str]  # Paper titles
    supporting_evidence: List[str] = []

class ResearchState(TypedDict):
    """State for the research workflow"""
    # Input
    query: str
    
    # Papers and results
    papers: List[Dict[str, Any]]  # Raw paper data
    processed_papers: List[Paper]
    
    # Analysis results
    research_gaps: List[ResearchGap]
    synthesis: str
    recommendations: List[str]
    
    # Workflow control
    current_step: str
    completed_steps: List[str]
    next_actions: List[str]
    
    # Metadata
    timestamp: datetime
    errors: List[str]
    llm_usage: Dict[str, int]
    total_papers_found: int

def create_initial_state(query: str) -> ResearchState:
    """Create initial state for research workflow"""
    return ResearchState(
        query=query,
        papers=[],
        processed_papers=[],
        research_gaps=[],
        synthesis="",
        recommendations=[],
        current_step="literature_search",
        completed_steps=[],
        next_actions=["search_arxiv", "search_pubmed"],
        timestamp=datetime.now(),
        errors=[],
        llm_usage={},
        total_papers_found=0
    )
