import os
import logging
from typing import Optional

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

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

HAS_GEMINI = False
try:
    from google import genai
    HAS_GEMINI = True
except ImportError:
    pass

class LLMClient:
    """Unified client for LLM interactions (Groq or Gemini)."""
    
    def __init__(self, provider: Optional[str] = None):
        self.client = None
        self.provider: Optional[str] = provider
        self.model: Optional[str] = None
        self.available: bool = False
        
        # Load environment variables first
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass

        # If provider explicitly set, try to init it
        if self.provider == "oxlo":
            self._configure_oxlo()
            if self.available: return

        # Default fallback logic (Groq -> Oxlo -> Gemini)
        if not self.provider or self.provider == "groq":
            groq_key = os.getenv(GROQ_API_KEY_ENV)
            if HAS_GROQ and groq_key:
                try:
                    self.client = Groq(api_key=groq_key)
                    self.provider = "groq"
                    self.model = GROQ_MODEL
                    self.available = True
                    logger.info(f"LLM initialized with Groq ({self.model})")
                    return
                except Exception as e:
                    logger.error(f"Failed to init Groq: {e}")

        if not self.available:
            self._configure_oxlo()

        if not self.available:
            self._configure_gemini()

    def _configure_oxlo(self):
        """Configure Oxlo as an OpenAI-compatible provider."""
        oxlo_key = os.getenv(OXLO_API_KEY_ENV)
        if HAS_OPENAI and oxlo_key:
            try:
                self.client = OpenAI(api_key=oxlo_key, base_url=OXLO_BASE_URL)
                self.provider = "oxlo"
                self.model = OXLO_MODEL
                self.available = True
                logger.info(f"LLM initialized with Oxlo ({self.model})")
            except Exception as e:
                logger.error(f"Failed to init Oxlo: {e}")
        elif not HAS_OPENAI:
            logger.warning("OpenAI library not installed. Oxlo client not available.")

    def _configure_gemini(self):
        """Configure the Gemini client using the new google-genai SDK."""
        api_key = os.getenv(GEMINI_API_KEY_ENV)
        if not api_key:
            logger.warning(f"Environment variable {GEMINI_API_KEY_ENV} not set.")
            self.available = False
            return
            
        if not HAS_GEMINI:
            logger.warning("google-genai not installed. Gemini client not available.")
            self.available = False
            return

        try:
            self.client = genai.Client(api_key=api_key)
            self.provider = "gemini"
            self.model = GEMINI_MODEL.replace("models/", "") if GEMINI_MODEL else "gemini-2.0-flash"
            self.available = True
            logger.info(f"LLM initialized with Gemini ({self.model})")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self.available = False

    def generate(self, prompt: str, max_tokens: int = 2048) -> str:
        """Generate text from the LLM."""
        if not self.available:
            logger.error("LLM not available.")
            return ""

        try:
            if self.provider in ["groq", "oxlo"]:
                # Groq / Oxlo Chat Completion
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=0.7,
                )
                return chat_completion.choices[0].message.content

            elif self.provider == "gemini":
                # New Gemini SDK Generation
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config={
                        "max_output_tokens": max_tokens,
                        "temperature": 0.7
                    }
                )
                return response.text
                
        except Exception as e:
            logger.error(f"LLM generation failed ({self.provider}): {e}")
            return ""
