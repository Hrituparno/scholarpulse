# Simple configuration for ScholarPulse - MULTI-LLM SYSTEM

DEFAULT_OUTPUT_DIR = "output"
ARXIV_MAX_RESULTS = 5  # Balanced for quality/speed
DEFAULT_QUERY = "machine learning optimization 2023"
LLM_PROVIDER = "multi"  # Multi-LLM intelligent routing

# Multi-LLM Configuration - MEMORY OPTIMIZED
# Groq: Primary (fast + reliable)
# Gemini: Fallback only (to save memory)

# Groq - Primary Provider
GROQ_MODEL = "llama-3.3-70b-versatile"  # Latest stable model
GROQ_API_KEY_ENV = "GROQ_API_KEY"

# Gemini - Fallback Only (1.5 Flash for unlimited usage)
GEMINI_MODEL = "models/gemini-1.5-flash"  # Unlimited, slower but reliable
GEMINI_API_KEY_ENV = "GOOGLE_API_KEY"

# Oxlo - Disabled for memory optimization
OXLO_MODEL = "llama-3.1-70b"
OXLO_API_KEY_ENV = "OXLO_API_KEY"
OXLO_BASE_URL = "https://api.oxlo.ai/v1"

# System Configuration
LLM_MAX_RETRIES = 2
LLM_TIMEOUT = 60  # Increased for Gemini 1.5 Flash
SERPER_API_KEY_ENV = "SERPER_API_KEY"
