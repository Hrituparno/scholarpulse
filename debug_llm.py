import logging
import os
import sys

# Add current dir to path
sys.path.append(os.getcwd())

from agent.llm import LLMClient
from config import GEMINI_MODEL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_llm():
    print(f"Testing LLM with model: {GEMINI_MODEL}")
    client = LLMClient()
    
    if not client.available:
        print("LLM Client is NOT available.")
        return

    try:
        response = client.generate("Hello, are you working?", max_tokens=20)
        print(f"Success! Response: {response}")
    except Exception as e:
        print(f"Error during generation: {e}")

if __name__ == "__main__":
    test_llm()
