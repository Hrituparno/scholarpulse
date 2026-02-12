# Simple configuration for ScholarPulse - MULTI-LLM SYSTEM

DEFAULT_OUTPUT_DIR = "output"
ARXIV_MAX_RESULTS = 5  # Balanced for quality/speed
DEFAULT_QUERY = "machine learning optimization 2023"
LLM_PROVIDER = "multi"  # Multi-LLM intelligent routing

# Multi-LLM Configuration - INTELLIGENT ROUTING
# Groq: Fast summarization (primary for speed)
# Gemini: Deep synthesis (primary for quality)
# Oxlo: Fallback + idea generation

# Groq - Fast Summarization
GROQ_MODEL = "llama-3.3-70b-versatile"  # Updated: Latest stable model (Feb 2026)
GROQ_API_KEY_ENV = "GROQ_API_KEY"

# Gemini - Deep Synthesis
GEMINI_MODEL = "models/gemini-2.0-flash"  # Fast + quality balance
GEMINI_API_KEY_ENV = "GOOGLE_API_KEY"

# Oxlo - Fallback + Ideas
OXLO_MODEL = "llama-3.1-70b"  # Powerful fallback
OXLO_API_KEY_ENV = "OXLO_API_KEY"
OXLO_BASE_URL = "https://api.oxlo.ai/v1"

# System Configuration
LLM_MAX_RETRIES = 2
LLM_TIMEOUT = 30  # seconds
SERPER_API_KEY_ENV = "SERPER_API_KEY"
