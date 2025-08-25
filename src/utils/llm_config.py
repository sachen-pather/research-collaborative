"""
Enhanced LLM Configuration with Automatic Fallback Support
"""
import os
from typing import Optional, Union
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from loguru import logger
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from langchain_core.runnables import Runnable

load_dotenv()

class LLMConfig:
    """Enhanced LLM configuration with automatic fallback and retry logic"""

    def __init__(self):
        self.gemini_key = os.getenv("GOOGLE_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.primary_llm_name = os.getenv("PRIMARY_LLM", "gemini")
        self.gemini_rate_limited = False
        self.groq_rate_limited = False
        self.rate_limit_reset_time = {}

    def get_primary_llm(self, temperature: float = 0.1):
        """Get primary LLM with fallback capability"""
        return FallbackLLM(self, temperature)

    def get_fast_llm(self, temperature: float = 0.0):
        """Get fast LLM with fallback capability"""
        return FallbackLLM(self, temperature, prefer_fast=True)

    def _create_gemini_llm(self, temperature: float = 0.1):
        """Create Gemini LLM instance"""
        if not self.gemini_key:
            raise ValueError("GOOGLE_API_KEY not found")
        return ChatGoogleGenerativeAI(
            google_api_key=self.gemini_key,
            model="gemini-1.5-flash",
            temperature=temperature
        )

    def _create_groq_llm(self, temperature: float = 0.1, fast: bool = False):
        """Create Groq LLM instance"""
        if not self.groq_key:
            raise ValueError("GROQ_API_KEY not found")
        model = "llama3-8b-8192" if fast else "llama3-70b-8192"
        return ChatGroq(
            groq_api_key=self.groq_key,
            model=model,
            temperature=temperature
        )

    def mark_rate_limited(self, provider: str, duration: int = 3600):
        """Mark a provider as rate limited"""
        self.rate_limit_reset_time[provider] = time.time() + duration
        logger.warning(f"🚫 {provider} marked as rate limited for {duration}s")

    def is_rate_limited(self, provider: str) -> bool:
        """Check if provider is still rate limited"""
        if provider not in self.rate_limit_reset_time:
            return False
        if time.time() > self.rate_limit_reset_time[provider]:
            del self.rate_limit_reset_time[provider]
            logger.info(f"✅ {provider} rate limit expired")
            return False
        return True

    def get_available_llms(self, temperature: float = 0.1, prefer_fast: bool = False):
        """Get list of available LLMs in priority order"""
        llms = []
        if self.primary_llm_name == "gemini" and self.gemini_key and not self.is_rate_limited("gemini"):
            try:
                llms.append(("gemini", self._create_gemini_llm(temperature)))
            except Exception as e:
                logger.warning(f"Failed to create Gemini LLM: {e}")
        elif self.primary_llm_name == "groq" and self.groq_key and not self.is_rate_limited("groq"):
            try:
                llms.append(("groq", self._create_groq_llm(temperature, prefer_fast)))
            except Exception as e:
                logger.warning(f"Failed to create Groq LLM: {e}")
        if self.groq_key and not self.is_rate_limited("groq") and self.primary_llm_name != "groq":
            try:
                llms.append(("groq", self._create_groq_llm(temperature, prefer_fast)))
            except Exception as e:
                logger.warning(f"Failed to create Groq fallback: {e}")
        if self.gemini_key and not self.is_rate_limited("gemini") and self.primary_llm_name != "gemini":
            try:
                llms.append(("gemini", self._create_gemini_llm(temperature)))
            except Exception as e:
                logger.warning(f"Failed to create Gemini fallback: {e}")
        return llms

    def verify_setup(self) -> dict:
        """Verify LLM setup and return status"""
        results = {}
        if self.gemini_key:
            try:
                llm = self._create_gemini_llm()
                response = llm.invoke("Test")
                results["gemini"] = "✅ Working"
            except Exception as e:
                results["gemini"] = f"⚠️ Error: {str(e)[:50]}"
                if "quota" in str(e).lower() or "429" in str(e):
                    self.mark_rate_limited("gemini")
        else:
            results["gemini"] = "⚠️ No API key"
        if self.groq_key:
            try:
                llm = self._create_groq_llm()
                response = llm.invoke("Test")
                results["groq"] = "✅ Working"
            except Exception as e:
                results["groq"] = f"⚠️ Error: {str(e)[:50]}"
                if "rate limit" in str(e).lower() or "429" in str(e):
                    self.mark_rate_limited("groq")
        else:
            results["groq"] = "⚠️ No API key"
        return results

llm_config = LLMConfig()

class FallbackLLM(Runnable):
    """LLM wrapper with automatic fallback capability"""

    def __init__(self, config: LLMConfig, temperature: float = 0.1, prefer_fast: bool = False):
        self.config = config
        self.temperature = temperature
        self.prefer_fast = prefer_fast

    def invoke(self, *args, **kwargs):
        """Invoke LLM with automatic fallback"""
        # Accepts any number of positional arguments, uses the first as input
        if not args:
            raise ValueError("No input provided to LLM")
        input = args[0]
        available_llms = self.config.get_available_llms(self.temperature, self.prefer_fast)
        if not available_llms:
            raise ValueError("No LLM providers available!")
        last_error = None
        for provider_name, llm in available_llms:
            try:
                logger.info(f"🤖 Trying {provider_name} LLM...")
                response = llm.invoke(input, **kwargs)
                logger.info(f"✅ {provider_name} LLM succeeded")
                return response
            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                if "quota" in error_str or "rate limit" in error_str or "429" in error_str:
                    logger.warning(f"🚫 {provider_name} rate limited: {e}")
                    self.config.mark_rate_limited(provider_name)
                else:
                    logger.error(f"❌ {provider_name} LLM failed: {e}")
                continue
        raise Exception(f"All LLM providers failed. Last error: {last_error}")

    def stream(self, *args, **kwargs):
        """Stream LLM with automatic fallback"""
        if not args:
            raise ValueError("No input provided to LLM")
        input = args[0]
        available_llms = self.config.get_available_llms(self.temperature, self.prefer_fast)
        if not available_llms:
            raise ValueError("No LLM providers available!")
        for provider_name, llm in available_llms:
            try:
                logger.info(f"🤖 Streaming with {provider_name} LLM...")
                return llm.stream(input, **kwargs)
            except Exception as e:
                error_str = str(e).lower()
                if "quota" in error_str or "rate limit" in error_str or "429" in error_str:
                    logger.warning(f"🚫 {provider_name} rate limited: {e}")
                    self.config.mark_rate_limited(provider_name)
                else:
                    logger.error(f"❌ {provider_name} streaming failed: {e}")
                continue
        raise Exception("All LLM providers failed for streaming")