# Save as test_fix.py
import sys
from pathlib import Path

# Add your project path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# Test the enhanced agent
def test_enhanced_agent():
    from agents.publication_assistant_agent import PublicationAssistantAgent
    
    # Mock state
    mock_state = {
        'query': 'Machine learning for healthcare',
        'papers_found': [
            {'title': 'ML in Healthcare', 'authors': ['Smith, J.'], 'url': 'http://example.com'}
        ],
        'key_themes': [{'theme': 'Deep Learning', 'trajectory': 'Growing'}],
        'research_gaps': [{'description': 'Limited clinical validation', 'impact': 'High'}],
        'hypotheses': [{'statement': 'ML will improve diagnostic accuracy'}],
        'verification_results': {'overall_confidence': 0.8}
    }
    
    # Test the agent
    agent = PublicationAssistantAgent()
    result = agent.execute(mock_state)
    
    # Check outputs
    print("✅ Enhanced Outputs Generated:")
    print(f"   Executive Summary: {len(result.get('executive_summary', ''))} characters")
    print(f"   Research Plan: {len(result.get('detailed_research_plan', ''))} characters")
    print(f"   Comprehensive Report: {len(result.get('comprehensive_research_report', ''))} characters")
    print(f"   Recommendations: {len(result.get('strategic_recommendations', []))} items")
    
    # Save outputs to files for verification
    outputs = {
        'executive_summary.md': result.get('executive_summary', ''),
        'research_plan.md': result.get('detailed_research_plan', ''),
        'comprehensive_report.md': result.get('comprehensive_research_report', '')
    }
    
    for filename, content in outputs.items():
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"💾 Saved: {filename}")
    
    return result

if __name__ == "__main__":
    result = test_enhanced_agent()
    print("\n🎉 Test completed! Check the generated .md files.")