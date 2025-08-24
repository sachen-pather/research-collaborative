#!/usr/bin/env python3
"""
Environment setup script for Research Collaborative
"""
import os
import subprocess
import sys
from pathlib import Path

def check_python_version():
    """Ensure Python 3.8+ is being used"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        sys.exit(1)
    print("✅ Python version:", sys.version.split()[0])

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            subprocess.run(['cp', '.env.example', '.env'])
            print("✅ Created .env file from template")
            print("⚠️  IMPORTANT: Edit .env and add your Gemini and Groq API keys!")
        else:
            print("❌ .env.example not found")
    else:
        print("✅ .env file already exists")

def verify_structure():
    """Verify project structure is correct"""
    required_dirs = [
        'src/agents', 'src/tools', 'src/workflow', 'src/utils', 'src/api',
        'tests', 'frontend', 'docs', 'scripts', 'data/cache', 'data/outputs', 'data/logs'
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print("❌ Missing directories:", missing_dirs)
        return False
    
    print("✅ Project structure verified")
    return True

def main():
    print("🚀 Setting up Research Collaborative (Gemini + Groq)...\n")
    
    # Check Python version
    check_python_version()
    
    # Verify project structure
    if not verify_structure():
        print("❌ Project structure incomplete. Please run the directory creation commands.")
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    print("\n🎉 Environment setup complete!")
    print("\n📋 Next steps:")
    print("1. Edit .env file and add your API keys:")
    print("   - GOOGLE_API_KEY (Gemini)")
    print("   - GROQ_API_KEY (Groq)")
    print("2. Test LLM setup: python scripts/test_llms.py")
    print("3. Start development!")

if __name__ == "__main__":
    main()
