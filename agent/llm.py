"""
Multi-LLM Client with Intelligent Routing

Architecture:
- Groq: Fast summarization (primary)
- Gemini: Deep synthesis (main intelligence)
- Oxlo: Fallback + idea generation

Features:
- Smart routing based on task type
- Automatic fallback on failure
- Parallel processing
- Timeout protection
"""
import os
import logging
from typing import Optional, Literal
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import time

from config import (
    GEMINI_MODEL, 
    GEMINI_API_KEY_ENV, 
    GROQ_MODEL, 
    GROQ_API_KEY_ENV,
    OXLO_MODEL,
    OXLO_API_KEY_ENV,
    OXLO_BASE_URL
)

logger = logging.getLogger(__name__)

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False
    logger.warning("Groq library not installed")

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    logger.warning("OpenAI library not installed")

HAS_GEMINI = False
try:
    from google import genai
    HAS_GEMINI = True
except ImportError:
    logger.warning("Gemini library not installed")


class MultiLLMClient:
    """
    Intelligent multi-LLM orchestrator with automatic routing and fallback.
    
    Routing Strategy:
    - FAST tasks (summaries) → Groq (fallback: Oxlo)
    - DEEP tasks (synthesis) → Gemini (fallback: Oxlo)
    - IDEAS tasks → Oxlo (fallback: Groq)
    """
    
    def __init__(self):
        self.groq_client = None
        self.gemini_client = None
        self.oxlo_client = None
        
        self.groq_available = False
        self.gemini_available = False
        self.oxlo_available = False
        
        # Load environment variables
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        
        # Initialize all providers
        self._init_groq()
        self._init_gemini()
        self._init_oxlo()
        
        # Log availability
        logger.info(f"Multi-LLM initialized: Groq={self.groq_available}, Gemini={self.gemini_available}, Oxlo={self.oxlo_available}")
    
    def _init_groq(self):
        """Initialize Groq for fast summarization."""
        groq_key = os.getenv(GROQ_API_KEY_ENV)
        if HAS_GROQ and groq_key:
            try:
                self.groq_client = Groq(api_key=groq_key)
                self.groq_available = True
                logger.info(f"Groq initialized: {GROQ_MODEL}")
            except Exception as e:
                logger.error(f"Failed to init Groq: {e}")
    
    def _init_gemini(self):
        """Initialize Gemini for deep synthesis."""
        api_key = os.getenv(GEMINI_API_KEY_ENV)
        if HAS_GEMINI and api_key:
            try:
                self.gemini_client = genai.Client(api_key=api_key)
                self.gemini_available = True
                logger.info(f"Gemini initialized: {GEMINI_MODEL}")
            except Exception as e:
                logger.error(f"Failed to init Gemini: {e}")
    
    def _init_oxlo(self):
        """Initialize Oxlo for fallback and ideas."""
        oxlo_key = os.getenv(OXLO_API_KEY_ENV)
        if HAS_OPENAI and oxlo_key:
            try:
                self.oxlo_client = OpenAI(api_key=oxlo_key, base_url=OXLO_BASE_URL)
                self.oxlo_available = True
                logger.info(f"Oxlo initialized: {OXLO_MODEL}")
            except Exception as e:
                logger.error(f"Failed to init Oxlo: {e}")
    
    @property
    def available(self) -> bool:
        """Check if at least one provider is available."""
        return self.groq_available or self.gemini_available or self.oxlo_available
    
    def generate_fast(
        self, 
        prompt: str, 
        max_tokens: int = 512,
        timeout: int = 10
    ) -> str:
        """
        Fast generation for summaries and quick tasks.
        
        Routing: Groq (primary) → Oxlo (fallback)
        Use case: Paper summarization, quick extraction
        """
        # Try Groq first (fastest)
        if self.groq_available:
            try:
                response = self._call_groq(prompt, max_tokens, timeout)
                if response and response.strip():
                    return response
                else:
                    logger.warning("[LLM] Groq returned empty, retrying once...")
                    # Retry once on empty response
                    try:
                        response = self._call_groq(prompt, max_tokens, timeout)
                        if response and response.strip():
                            logger.info("[LLM] Groq retry successful")
                            return response
                    except Exception as retry_e:
                        logger.warning(f"[LLM] Groq retry failed: {retry_e}")
                    
                    logger.info("[LLM] Fallback → Oxlo (Groq empty response)")
            except Exception as e:
                logger.warning(f"[LLM] Groq failed, falling back to Oxlo: {e}")
        
        # Fallback to Oxlo
        if self.oxlo_available:
            try:
                logger.info("[LLM] Using Oxlo fallback for fast generation")
                response = self._call_oxlo(prompt, max_tokens, timeout)
                if response and response.strip():
                    logger.info("[LLM] Oxlo fallback success")
                    return response
            except Exception as e:
                logger.warning(f"[LLM] Oxlo fallback failed: {e}")
        
        # Last resort: Gemini
        if self.gemini_available:
            try:
                logger.info("[LLM] Using Gemini as last resort for fast generation")
                response = self._call_gemini(prompt, max_tokens, timeout)
                if response and response.strip():
                    logger.info("[LLM] Gemini last resort success")
                    return response
            except Exception as e:
                logger.warning(f"[LLM] Gemini last resort failed: {e}")
        
        logger.error("[LLM] All fast generation providers failed")
        return ""
    
    def generate_deep(
        self, 
        prompt: str, 
        max_tokens: int = 2048,
        timeout: int = 30
    ) -> str:
        """
        Deep generation for synthesis and complex reasoning.
        
        Routing: Gemini (primary) → Oxlo (fallback) → Groq (last resort)
        Use case: Research synthesis, idea combination, deep analysis
        """
        # Try Gemini first (best quality)
        if self.gemini_available:
            try:
                response = self._call_gemini(prompt, max_tokens, timeout)
                if response:
                    logger.debug("Deep generation: Gemini success")
                    return response
            except Exception as e:
                logger.warning(f"Gemini deep generation failed: {e}")
        
        # Fallback to Oxlo
        if self.oxlo_available:
            try:
                response = self._call_oxlo(prompt, max_tokens, timeout)
                if response:
                    logger.info("Deep generation: Oxlo fallback success")
                    return response
            except Exception as e:
                logger.warning(f"Oxlo deep generation failed: {e}")
        
        # Last resort: Groq
        if self.groq_available:
            try:
                response = self._call_groq(prompt, max_tokens, timeout)
                if response:
                    logger.info("Deep generation: Groq last resort success")
                    return response
            except Exception as e:
                logger.warning(f"Groq deep generation failed: {e}")
        
        logger.error("All deep generation providers failed")
        return ""
    
    def generate_ideas(
        self, 
        prompt: str, 
        max_tokens: int = 1536,
        timeout: int = 20
    ) -> str:
        """
        Idea generation and creative tasks.
        
        Routing: Oxlo (primary) → Groq (fallback) → Gemini (last resort)
        Use case: Research ideas, hypothesis generation
        """
        # Try Oxlo first (good for ideas)
        if self.oxlo_available:
            try:
                response = self._call_oxlo(prompt, max_tokens, timeout)
                if response:
                    logger.debug("Idea generation: Oxlo success")
                    return response
            except Exception as e:
                logger.warning(f"Oxlo idea generation failed: {e}")
        
        # Fallback to Groq
        if self.groq_available:
            try:
                response = self._call_groq(prompt, max_tokens, timeout)
                if response:
                    logger.info("Idea generation: Groq fallback success")
                    return response
            except Exception as e:
                logger.warning(f"Groq idea generation failed: {e}")
        
        # Last resort: Gemini
        if self.gemini_available:
            try:
                response = self._call_gemini(prompt, max_tokens, timeout)
                if response:
                    logger.info("Idea generation: Gemini last resort success")
                    return response
            except Exception as e:
                logger.warning(f"Gemini idea generation failed: {e}")
        
        logger.error("All idea generation providers failed")
        return ""
    
    def _call_groq(self, prompt: str, max_tokens: int, timeout: int) -> str:
        """Call Groq with timeout protection and validation."""
        try:
            logger.info(f"[LLM] Using Groq for generation (model: {GROQ_MODEL})")
            
            chat_completion = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=GROQ_MODEL,
                max_tokens=max_tokens,
                temperature=0.7,
                timeout=float(timeout),
            )
            
            # Validate response
            if not chat_completion.choices:
                logger.warning("[LLM] Groq returned empty choices array")
                return ""
            
            content = chat_completion.choices[0].message.content
            
            if not content or content.strip() == "":
                logger.warning("[LLM] Groq returned empty content")
                return ""
            
            logger.info(f"[LLM] Groq success - generated {len(content)} chars")
            return content
            
        except Exception as e:
            error_msg = str(e)
            
            # Check for specific errors
            if "model" in error_msg.lower() and ("not found" in error_msg.lower() or "decommissioned" in error_msg.lower()):
                logger.error(f"[LLM] Groq model error: {GROQ_MODEL} may be invalid or decommissioned")
            elif "rate_limit" in error_msg.lower() or "429" in error_msg:
                logger.warning(f"[LLM] Groq rate limit hit")
            elif "authentication" in error_msg.lower() or "401" in error_msg:
                logger.error(f"[LLM] Groq authentication failed - check API key")
            else:
                logger.warning(f"[LLM] Groq call failed: {error_msg}")
            
            raise
    
    def _call_gemini(self, prompt: str, max_tokens: int, timeout: int) -> str:
        """Call Gemini with timeout protection."""
        model_name = GEMINI_MODEL.replace("models/", "") if GEMINI_MODEL else "gemini-2.0-flash"
        
        response = self.gemini_client.models.generate_content(
            model=model_name,
            contents=prompt,
            config={
                "max_output_tokens": max_tokens,
                "temperature": 0.7
            }
        )
        
        if hasattr(response, 'text') and response.text:
            return response.text
        
        return ""
    
    def _call_oxlo(self, prompt: str, max_tokens: int, timeout: int) -> str:
        """Call Oxlo with timeout protection."""
        chat_completion = self.oxlo_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=OXLO_MODEL,
            max_tokens=max_tokens,
            temperature=0.7,
            timeout=float(timeout),
        )
        
        if chat_completion.choices:
            content = chat_completion.choices[0].message.content
            if content:
                return content
        
        return ""
    
    def batch_generate_fast(
        self,
        prompts: list[str],
        max_tokens: int = 512,
        max_workers: int = 3,
        timeout_per_task: int = 10
    ) -> list[str]:
        """
        Parallel fast generation for multiple prompts with safe error handling.
        
        Use case: Batch paper summarization
        """
        results = [""] * len(prompts)
        
        def process_prompt(idx: int, prompt: str) -> tuple[int, str]:
            try:
                result = self.generate_fast(prompt, max_tokens, timeout_per_task)
                
                # Validate result is not empty
                if not result or result.strip() == "":
                    logger.warning(f"[LLM] Batch task {idx} returned empty result")
                    return (idx, "")
                
                return (idx, result)
            except Exception as e:
                logger.warning(f"[LLM] Batch task {idx} failed: {e}")
                return (idx, "")
        
        logger.info(f"[LLM] Starting batch generation for {len(prompts)} prompts with {max_workers} workers")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(process_prompt, i, prompt)
                for i, prompt in enumerate(prompts)
            ]
            
            for future in futures:
                try:
                    idx, result = future.result(timeout=timeout_per_task + 5)
                    results[idx] = result
                except FutureTimeoutError:
                    logger.warning(f"[LLM] Batch task timed out")
                except Exception as e:
                    logger.warning(f"[LLM] Batch task failed: {e}")
        
        successful = sum(1 for r in results if r and r.strip())
        logger.info(f"[LLM] Batch generation complete: {successful}/{len(prompts)} successful")
        
        return results


# Legacy compatibility wrapper
class LLMClient:
    """
    Legacy single-provider client for backward compatibility.
    Now wraps MultiLLMClient with intelligent routing.
    """
    
    def __init__(self, provider: Optional[str] = None):
        self.multi_client = MultiLLMClient()
        self.provider = provider or "multi"
        self.available = self.multi_client.available
        
        # For compatibility
        self.model = "multi-llm-router"
    
    def generate(self, prompt: str, max_tokens: int = 2048, retries: int = 2) -> str:
        """
        Generate with automatic routing based on task complexity.
        
        Automatically detects task type and routes to appropriate provider.
        """
        if not self.available:
            logger.error("LLM not available.")
            return ""
        
        # Detect task type from prompt
        prompt_lower = prompt.lower()
        
        # Fast tasks: summaries, extraction
        if any(word in prompt_lower for word in ['summarize', 'extract', 'brief', 'key points']):
            return self.multi_client.generate_fast(prompt, min(max_tokens, 512), timeout=10)
        
        # Idea tasks: generation, hypothesis
        elif any(word in prompt_lower for word in ['generate', 'propose', 'ideas', 'hypothesis']):
            return self.multi_client.generate_ideas(prompt, min(max_tokens, 1536), timeout=20)
        
        # Deep tasks: synthesis, analysis, combination
        else:
            return self.multi_client.generate_deep(prompt, max_tokens, timeout=30)
