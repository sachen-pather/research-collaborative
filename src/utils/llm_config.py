"""
LLM Configuration for Gemini and Groq
"""
import os
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

class LLMConfig:
    """Centralized LLM configuration and management"""

    def __init__(self):
        self.gemini_key = os.getenv("GOOGLE_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.primary_llm = os.getenv("PRIMARY_LLM", "gemini")

    def get_primary_llm(self, temperature: float = 0.1):
        """Get the primary LLM instance"""
        if self.primary_llm == "gemini" and self.gemini_key:
            return ChatGoogleGenerativeAI(
                google_api_key=self.gemini_key,
                model="gemini-1.5-flash",
                temperature=temperature
            )
        elif self.primary_llm == "groq" and self.groq_key:
            return ChatGroq(
                groq_api_key=self.groq_key,
                model="llama3-70b-8192",
                temperature=temperature
            )
        else:
            # Fallback
            if self.gemini_key:
                return ChatGoogleGenerativeAI(
                    google_api_key=self.gemini_key,
                    model="gemini-1.5-flash",
                    temperature=temperature
                )
            elif self.groq_key:
                return ChatGroq(
                    groq_api_key=self.groq_key,
                    model="llama3-70b-8192",
                    temperature=temperature
                )
            else:
                raise ValueError("No LLM API keys found! Please set GOOGLE_API_KEY or GROQ_API_KEY")

    def get_fast_llm(self, temperature: float = 0.0):
        """Get a fast LLM for quick tasks"""
        if self.groq_key:
            return ChatGroq(
                groq_api_key=self.groq_key,
                model="llama3-8b-8192",  # Faster model
                temperature=temperature
            )
        else:
            return self.get_primary_llm(temperature)

    def verify_setup(self) -> dict:
        """Verify LLM setup and return status"""
        results = {}
        
        # Test Gemini
        if self.gemini_key:
            try:
                llm = ChatGoogleGenerativeAI(
                    google_api_key=self.gemini_key,
                    model="gemini-1.5-flash"
                )
                response = llm.invoke("What is the capital of France?")
                results["gemini"] = "✅ Working"
            except Exception as e:
                results["gemini"] = f"⚠️ Error: {str(e)[:50]}"
        else:
            results["gemini"] = "⚠️ No API key"

        # Test Groq
        if self.groq_key:
            try:
                llm = ChatGroq(
                    groq_api_key=self.groq_key,
                    model="llama3-8b-8192"
                )
                response = llm.invoke("What is the capital of France?")
                results["groq"] = "✅ Working"
            except Exception as e:
                results["groq"] = f"⚠️ Error: {str(e)[:50]}"
        else:
            results["groq"] = "⚠️ No API key"

        return results

    def test_primary_llm(self) -> str:
        """Test the primary LLM with a simple query"""
        try:
            llm = self.get_primary_llm()
            response = llm.invoke("What is the capital of France? Answer in one word.")
            return response.content
        except Exception as e:
            return f"Error: {str(e)}"

# Global instance
llm_config = LLMConfig()
