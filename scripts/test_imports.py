#!/usr/bin/env python3
"""
Test all imports before running full tests
"""

def test_basic_imports():
    """Test basic Python imports"""
    print("🧪 Testing basic imports...")
    
    try:
        import sys
        import os
        from datetime import datetime
        from typing import Dict, List, Optional
        print("✅ Basic Python imports: OK")
    except Exception as e:
        print(f"❌ Basic imports failed: {e}")
        return False
    
    return True

def test_langchain_imports():
    """Test LangChain imports"""
    print("🧪 Testing LangChain imports...")
    
    try:
        import langchain
        print(f"✅ LangChain version: {langchain.__version__}")
    except Exception as e:
        print(f"❌ LangChain import failed: {e}")
        return False
    
    return True

def test_langgraph_imports():
    """Test LangGraph imports"""
    print("🧪 Testing LangGraph imports...")
    
    try:
        import langgraph
        print(f"✅ LangGraph imported successfully")
        
        # Try different import patterns
        try:
            from langgraph.graph import StateGraph, END
            print("✅ StateGraph import method 1: OK")
        except:
            try:
                from langgraph import StateGraph, END
                print("✅ StateGraph import method 2: OK")
            except Exception as e:
                print(f"⚠️  StateGraph import issues: {e}")
                return False
                
    except Exception as e:
        print(f"❌ LangGraph import failed: {e}")
        return False
    
    return True

def test_llm_imports():
    """Test LLM imports"""
    print("🧪 Testing LLM imports...")
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("✅ Gemini imports: OK")
    except Exception as e:
        print(f"❌ Gemini imports failed: {e}")
        return False
    
    try:
        from langchain_groq import ChatGroq
        print("✅ Groq imports: OK")  
    except Exception as e:
        print(f"❌ Groq imports failed: {e}")
        return False
    
    return True

def test_utility_imports():
    """Test utility imports"""
    print("🧪 Testing utility imports...")
    
    try:
        from pydantic import BaseModel
        from loguru import logger
        import arxiv
        print("✅ Utility imports: OK")
    except Exception as e:
        print(f"❌ Utility imports failed: {e}")
        return False
    
    return True

def main():
    print("🔬 Testing All Imports\n")
    
    tests = [
        test_basic_imports,
        test_langchain_imports,
        test_langgraph_imports,
        test_llm_imports,
        test_utility_imports
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All imports working! Ready to test core components.")
        return True
    else:
        print("❌ Some imports failed. Please fix before continuing.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
