"""
Test script to verify Groq API integration
Run this to diagnose Groq API issues before deployment
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_groq_connection():
    """Test basic Groq API connectivity and model availability."""
    print("=" * 60)
    print("ScholarPulse - Groq API Diagnostic Test")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not found in environment")
        print("   Please set it in your .env file")
        return False
    
    print(f"✓ GROQ_API_KEY found: {api_key[:10]}...{api_key[-4:]}")
    
    # Try importing Groq
    try:
        from groq import Groq
        print("✓ Groq library imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Groq library: {e}")
        print("   Run: pip install groq>=0.30.0")
        return False
    
    # Initialize client
    try:
        client = Groq(api_key=api_key)
        print("✓ Groq client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Groq client: {e}")
        return False
    
    # Test available models
    print("\n" + "=" * 60)
    print("Testing Model: llama-3.3-70b-versatile")
    print("=" * 60)
    
    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Say 'Hello from ScholarPulse!' in exactly 5 words.",
                }
            ],
            model="llama-3.3-70b-versatile",
            max_tokens=50,
            temperature=0.7,
            timeout=30.0,
        )
        
        if response.choices:
            content = response.choices[0].message.content
            print(f"✓ Model response: {content}")
            print(f"✓ Tokens used: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
            return True
        else:
            print("❌ Empty response from model")
            return False
            
    except Exception as e:
        print(f"❌ API call failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # Provide specific guidance
        error_str = str(e).lower()
        if "authentication" in error_str or "401" in error_str:
            print("\n💡 Fix: Your API key is invalid or expired")
            print("   Get a new key from: https://console.groq.com/keys")
        elif "rate_limit" in error_str or "429" in error_str:
            print("\n💡 Fix: Rate limit exceeded")
            print("   Wait a few minutes and try again")
        elif "model" in error_str and "not found" in error_str:
            print("\n💡 Fix: Model name may be incorrect or deprecated")
            print("   Check available models at: https://console.groq.com/docs/models")
        elif "timeout" in error_str:
            print("\n💡 Fix: Request timed out")
            print("   Check your internet connection")
        
        return False

def test_llm_client():
    """Test the ScholarPulse LLMClient wrapper."""
    print("\n" + "=" * 60)
    print("Testing ScholarPulse LLMClient")
    print("=" * 60)
    
    try:
        from agent.llm import LLMClient
        
        client = LLMClient(provider="groq")
        
        if not client.available:
            print("❌ LLMClient not available")
            print(f"   Provider: {client.provider}")
            return False
        
        print(f"✓ LLMClient initialized")
        print(f"  Provider: {client.provider}")
        print(f"  Model: {client.model}")
        
        # Test generation
        response = client.generate("What is 2+2? Answer in one word.", max_tokens=10)
        
        if response:
            print(f"✓ Generation successful: {response}")
            return True
        else:
            print("❌ Generation returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ LLMClient test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all diagnostic tests."""
    results = []
    
    # Test 1: Direct Groq API
    results.append(("Groq API Connection", test_groq_connection()))
    
    # Test 2: LLMClient wrapper
    results.append(("LLMClient Wrapper", test_llm_client()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Groq API is working correctly.")
        print("   Your ScholarPulse deployment should work fine.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Fix the issues above before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
