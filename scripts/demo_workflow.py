#!/usr/bin/env python3
"""
Demonstration of the research workflow
"""
import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from workflow.graph import research_workflow
from utils.llm_config import llm_config

def main():
    """Run a demonstration of the research workflow"""
    print("🎬 Research Collaborative Demonstration")
    print("=" * 50)
    
    # Test LLM setup
    print("\n1. 🔧 Testing LLM Configuration...")
    results = llm_config.verify_setup()
    working_llms = []
    
    for llm_name, status in results.items():
        print(f"   {llm_name.upper()}: {status}")
        if "✅" in status:
            working_llms.append(llm_name)
    
    if not working_llms:
        print("❌ No working LLMs found. Please check your API keys in .env file.")
        return False
    
    print(f"✅ Working LLMs: {', '.join(working_llms)}")
    
    # Test workflow
    print("\n2. 🚀 Running Research Workflow...")
    query = "Recent advances in transformer architectures for natural language processing"
    
    try:
        result = research_workflow.run(query)
        
        print(f"\n📋 Research Results for: '{query}'")
        print("-" * 50)
        print(f"Query: {result.get('query', 'N/A')}")
        print(f"Status: {result.get('current_step', 'N/A')}")
        print(f"Completed Steps: {result.get('completed_steps', [])}")
        print(f"Papers Found: {result.get('total_papers_found', 0)}")
        print(f"Synthesis: {result.get('synthesis', 'Not generated')}")
        
        if result.get('errors'):
            print(f"Errors: {result['errors']}")
        
        print("\n✅ Demonstration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Workflow demonstration failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
