#!/usr/bin/env python3
"""
Debug the workflow step by step
"""
import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

def test_individual_nodes():
    """Test each node individually"""
    print("🔍 Testing individual workflow nodes...")
    
    try:
        from workflow.graph import literature_search_node, analysis_node, synthesis_node
        
        # Test literature search
        print("\n1. Testing Literature Search Node...")
        state = {
            'query': 'machine learning',
            'completed_steps': [],
            'papers': [],
            'total_papers_found': 0
        }
        
        result = literature_search_node(state)
        print(f"   Papers found: {result.get('total_papers_found', 0)}")
        print(f"   Completed steps: {result.get('completed_steps', [])}")
        
        # Test analysis
        print("\n2. Testing Analysis Node...")
        result = analysis_node(result)
        print(f"   Themes: {result.get('analysis_themes', [])}")
        print(f"   Completed steps: {result.get('completed_steps', [])}")
        
        # Test synthesis
        print("\n3. Testing Synthesis Node...")
        result = synthesis_node(result)
        print(f"   Synthesis length: {len(result.get('synthesis', ''))}")
        print(f"   Completed steps: {result.get('completed_steps', [])}")
        
        print("\n✅ All individual nodes working!")
        return result
        
    except Exception as e:
        print(f"❌ Individual node test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_workflow_compilation():
    """Test workflow compilation"""
    print("\n🔧 Testing workflow compilation...")
    
    try:
        from workflow.graph import ResearchWorkflow
        
        workflow = ResearchWorkflow()
        print("✅ Workflow compiled successfully")
        return workflow
        
    except Exception as e:
        print(f"❌ Workflow compilation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_workflow_execution():
    """Test workflow execution"""
    print("\n🚀 Testing workflow execution...")
    
    try:
        from workflow.graph import research_workflow
        
        query = "transformer models"
        result = research_workflow.run(query)
        
        print(f"Query: {result.get('query')}")
        print(f"Status: {result.get('current_step')}")
        print(f"Papers: {result.get('total_papers_found')}")
        print(f"Errors: {result.get('errors', [])}")
        print(f"Completed: {result.get('completed_steps', [])}")
        
        if result.get('synthesis'):
            print(f"Synthesis: {result['synthesis'][:100]}...")
        
        return result
        
    except Exception as e:
        print(f"❌ Workflow execution failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Run all debug tests"""
    print("🛠️ Debugging Research Workflow")
    print("=" * 40)
    
    # Test 1: Individual nodes
    node_result = test_individual_nodes()
    
    # Test 2: Workflow compilation
    workflow = test_workflow_compilation()
    
    # Test 3: Full execution
    if workflow:
        execution_result = test_workflow_execution()
        
        if execution_result and not execution_result.get('errors'):
            print("\n🎉 All tests passed! Workflow is working correctly.")
        else:
            print("\n⚠️ Workflow has issues that need fixing.")
    
if __name__ == "__main__":
    main()
