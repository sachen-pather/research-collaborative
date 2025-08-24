#!/usr/bin/env python3
"""
Test core workflow components
"""
import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

def test_state_creation():
    """Test state creation"""
    print("🧪 Testing state creation...")

    try:
        from workflow.state import create_initial_state
        
        query = "Machine learning applications in drug discovery"
        state = create_initial_state(query)

        assert state['query'] == query
        assert state['current_step'] == 'literature_search'
        assert isinstance(state['papers'], list)
        assert isinstance(state['completed_steps'], list)
        
        print("✅ State creation: PASSED")
        return True
    except Exception as e:
        print(f"❌ State creation: FAILED - {e}")
        return False

def test_workflow_creation():
    """Test workflow graph creation"""
    print("🧪 Testing workflow creation...")

    try:
        from workflow.graph import ResearchWorkflow
        
        workflow = ResearchWorkflow()
        assert workflow.workflow is not None
        
        print("✅ Workflow creation: PASSED")
        return True
    except Exception as e:
        print(f"❌ Workflow creation: FAILED - {e}")
        return False

def test_workflow_execution():
    """Test basic workflow execution"""
    print("🧪 Testing workflow execution...")

    try:
        from workflow.graph import research_workflow
        
        query = "AI in healthcare"
        result = research_workflow.run(query)
        
        assert result['query'] == query
        assert isinstance(result.get('completed_steps', []), list)
        
        print("✅ Workflow execution: PASSED")
        return True
    except Exception as e:
        print(f"❌ Workflow execution: FAILED - {e}")
        return False

def test_router():
    """Test routing logic"""
    print("🧪 Testing router...")

    try:
        from workflow.router import route_next_step, should_continue, get_workflow_status
        
        # Test routing
        state = {'completed_steps': [], 'errors': []}
        next_step = route_next_step(state)
        assert next_step == "literature_search"
        
        # Test status
        status = get_workflow_status(state)
        assert 'progress' in status
        
        print("✅ Router: PASSED")
        return True
    except Exception as e:
        print(f"❌ Router: FAILED - {e}")
        return False

def main():
    """Run all tests"""
    print("🔬 Testing Core Research Collaborative Components\n")

    tests = [
        test_state_creation,
        test_workflow_creation,
        test_router,
        test_workflow_execution
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print(f"📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All core tests passed! System ready.")
        return True
    else:
        print("❌ Some tests failed. Please fix before continuing.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
