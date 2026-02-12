"""
Production Debugging Script for ScholarPulse
Helps diagnose issues in deployed environments
"""
import os
import sys
import json
import requests
from datetime import datetime

def check_backend_health(backend_url):
    """Check if backend is responding."""
    print("\n" + "=" * 60)
    print("Backend Health Check")
    print("=" * 60)
    
    health_url = f"{backend_url}/api/health/"
    
    try:
        response = requests.get(health_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Backend is healthy")
            print(f"  Status: {data.get('status')}")
            print(f"  Service: {data.get('service')}")
            print(f"  Timestamp: {data.get('timestamp')}")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ Backend health check timed out")
        print(f"   URL: {health_url}")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to backend")
        print(f"   URL: {health_url}")
        print(f"   Check if backend is running")
        return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_research_submission(backend_url):
    """Test submitting a research query."""
    print("\n" + "=" * 60)
    print("Research Submission Test")
    print("=" * 60)
    
    submit_url = f"{backend_url}/api/research/submit/"
    
    payload = {
        "query": "test query for debugging",
        "mode": "Deep Research",
        "llm_provider": "groq"
    }
    
    try:
        print(f"Submitting test query...")
        response = requests.post(
            submit_url,
            json=payload,
            timeout=60,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            task_id = data.get('task_id')
            status = data.get('status')
            
            print(f"✓ Query submitted successfully")
            print(f"  Task ID: {task_id}")
            print(f"  Status: {status}")
            
            if status == 'FAILED':
                print(f"  Message: {data.get('message')}")
                return False
            
            return True
        else:
            print(f"❌ Submission failed with status {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            
            # Try to parse error details
            try:
                error_data = response.json()
                print(f"   Error details: {json.dumps(error_data, indent=2)}")
            except:
                pass
            
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out (>60s)")
        print(f"   This might indicate backend processing issues")
        return False
    except Exception as e:
        print(f"❌ Submission test failed: {e}")
        return False

def check_environment_variables():
    """Check if required environment variables are set."""
    print("\n" + "=" * 60)
    print("Environment Variables Check")
    print("=" * 60)
    
    required_vars = {
        "GROQ_API_KEY": "Groq API key for LLM",
        "DJANGO_SECRET_KEY": "Django secret key",
    }
    
    optional_vars = {
        "GOOGLE_API_KEY": "Google Gemini API (fallback)",
        "SERPER_API_KEY": "Web search API",
        "OXLO_API_KEY": "Oxlo API (alternative LLM)",
        "DJANGO_DEBUG": "Debug mode setting",
    }
    
    all_good = True
    
    print("\nRequired Variables:")
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            masked = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            print(f"  ✓ {var}: {masked}")
        else:
            print(f"  ❌ {var}: NOT SET - {description}")
            all_good = False
    
    print("\nOptional Variables:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            if var == "DJANGO_DEBUG":
                print(f"  ✓ {var}: {value}")
            else:
                masked = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
                print(f"  ✓ {var}: {masked}")
        else:
            print(f"  ⚠ {var}: Not set - {description}")
    
    return all_good

def check_groq_api_directly():
    """Test Groq API directly."""
    print("\n" + "=" * 60)
    print("Direct Groq API Test")
    print("=" * 60)
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not set")
        return False
    
    try:
        from groq import Groq
        
        client = Groq(api_key=api_key)
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": "Say 'API working' in 2 words"}],
            model="llama-3.3-70b-versatile",
            max_tokens=10,
            timeout=30.0,
        )
        
        if response.choices:
            content = response.choices[0].message.content
            print(f"✓ Groq API is working")
            print(f"  Response: {content}")
            return True
        else:
            print(f"❌ Empty response from Groq")
            return False
            
    except ImportError:
        print(f"❌ Groq library not installed")
        print(f"   Run: pip install groq>=0.30.0")
        return False
    except Exception as e:
        print(f"❌ Groq API test failed: {e}")
        
        error_str = str(e).lower()
        if "authentication" in error_str or "401" in error_str:
            print(f"\n💡 Your API key is invalid")
            print(f"   Get new key: https://console.groq.com/keys")
        elif "model" in error_str and "not found" in error_str:
            print(f"\n💡 Model not found - may be deprecated")
            print(f"   Check: https://console.groq.com/docs/models")
        
        return False

def main():
    """Run all diagnostic checks."""
    print("=" * 60)
    print("ScholarPulse Production Diagnostics")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # Get backend URL
    backend_url = os.getenv("SCHOLARPULSE_API_URL")
    if not backend_url:
        backend_url = input("\nEnter backend URL (e.g., https://your-app.onrender.com): ").strip()
        if not backend_url:
            print("❌ Backend URL required")
            return 1
    
    # Remove trailing slash
    backend_url = backend_url.rstrip('/')
    
    print(f"\nBackend URL: {backend_url}")
    
    # Run checks
    results = []
    
    results.append(("Environment Variables", check_environment_variables()))
    results.append(("Groq API Direct", check_groq_api_directly()))
    results.append(("Backend Health", check_backend_health(backend_url)))
    results.append(("Research Submission", test_research_submission(backend_url)))
    
    # Summary
    print("\n" + "=" * 60)
    print("Diagnostic Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All diagnostics passed!")
        print("   Your deployment appears to be working correctly.")
        return 0
    else:
        print("\n⚠️  Some diagnostics failed.")
        print("   Review the errors above and fix before using in production.")
        print("\nCommon fixes:")
        print("  1. Verify all environment variables are set in Render")
        print("  2. Check Render logs for detailed error messages")
        print("  3. Ensure Groq API key is valid and has credits")
        print("  4. Verify model name is correct: llama-3.3-70b-versatile")
        print("  5. Check backend service is running (not sleeping)")
        return 1

if __name__ == "__main__":
    # Load .env if running locally
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    sys.exit(main())
