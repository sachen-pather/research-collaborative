#!/usr/bin/env python3
"""
Test script to verify LLM configurations
"""
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.llm_config import llm_config

def main():
    print("🧪 Testing LLM Configurations...\n")
    
    # Verify setup
    results = llm_config.verify_setup()
    
    for llm_name, status in results.items():
        print(f"{llm_name.upper()}: {status}")
    
    # Test if at least one LLM works
    working_llms = [name for name, status in results.items() if "✅" in status]
    
    if working_llms:
        print(f"\n🎉 Success! Working LLMs: {', '.join(working_llms)}")
        
        # Test primary LLM
        try:
            llm = llm_config.get_primary_llm()
            response = llm.invoke("What is the capital of France?")
            print(f"📝 Sample response from primary LLM: {response.content[:100]}...")
        except Exception as e:
            print(f"❌ Primary LLM test failed: {e}")
    else:
        print("\n❌ No working LLMs found. Please check your API keys.")
        sys.exit(1)

if __name__ == "__main__":
    main()
