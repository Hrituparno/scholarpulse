# Simple configuration for ScholarPulse

DEFAULT_OUTPUT_DIR = "output"
ARXIV_MAX_RESULTS = 10
DEFAULT_QUERY = "machine learning optimization 2023"
LLM_PROVIDER = "groq"  # 'groq' or 'gemini'

# LLM Constants
GROQ_MODEL = "llama3-70b-8192"
GEMINI_MODEL = "models/gemini-2.5-flash"
LLM_MAX_RETRIES = 3
LLM_TIMEOUT = 60  # seconds

# Environment Variables
GEMINI_API_KEY_ENV = "GOOGLE_API_KEY"
GROQ_API_KEY_ENV = "GROQ_API_KEY"
SERPER_API_KEY_ENV = "SERPER_API_KEY"
OXLO_API_KEY_ENV = "OXLO_API_KEY"
OXLO_MODEL = "llama-3.1-70b" # Fix: Model name should be lowercase
OXLO_BASE_URL = "https://api.oxlo.ai/v1"
