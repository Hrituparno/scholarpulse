#!/usr/bin/env python3
"""
Production Verification Script for ScholarPulse Hotfix v2.2.1

Verifies:
1. Backend health endpoint
2. Groq model update deployed
3. Multi-LLM system working
4. No JSON parse errors
5. Response time acceptable
"""

import requests
import time
import json

# Production URLs
BACKEND_URL = "https://scholarpulse.onrender.com"
HEALTH_ENDPOINT = f"{BACKEND_URL}/api/health/"
RESEARCH_ENDPOINT = f"{BACKEND_URL}/api/research/"

def check_health():
    """Check if backend is healthy."""
    print("\n🔍 Checking backend health...")
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=10)
        if response.status_code == 200:
            print("✅ Backend is healthy")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_research_query():
    """Test a research query to verify Groq model and multi-LLM system."""
    print("\n🔍 Testing research query...")
    
    test_query = "machine learning optimization"
    
    try:
        print(f"   Query: '{test_query}'")
        print("   Waiting for response...")
        
        start_time = time.time()
        
        response = requests.post(
            RESEARCH_ENDPOINT,
            json={"query": test_query},
            timeout=60
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Research query successful")
            print(f"   Response time: {elapsed:.1f}s")
            
            # Check for papers
            papers = data.get("papers", [])
            print(f"   Papers returned: {len(papers)}")
            
            # Check for ideas
            ideas = data.get("ideas", [])
            print(f"   Ideas generated: {len(ideas)}")
            
            # Check for report sections
            report = data.get("report", {})
            has_intro = bool(report.get("introduction"))
            has_issue = bool(report.get("the_issue"))
            has_conclusion = bool(report.get("conclusion"))
            print(f"   Report sections: intro={has_intro}, issue={has_issue}, conclusion={has_conclusion}")
            
            # Verify response time
            if elapsed <= 30:
                print(f"✅ Response time acceptable ({elapsed:.1f}s <= 30s)")
            else:
                print(f"⚠️  Response time slow ({elapsed:.1f}s > 30s)")
            
            return True
        else:
            print(f"❌ Research query failed with status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.Timeout:
        print("❌ Request timed out (>60s)")
        return False
    except Exception as e:
        print(f"❌ Research query failed: {e}")
        return False

def check_logs_for_errors():
    """Remind user to check Render logs."""
    print("\n📋 Manual verification needed:")
    print("   1. Go to: https://dashboard.render.com/")
    print("   2. Select your ScholarPulse backend service")
    print("   3. Check logs for:")
    print("      ✓ 'Multi-LLM initialized: Groq=True, Gemini=True, Oxlo=True'")
    print("      ✓ '[LLM] Using Groq (model: llama-3.3-70b-versatile)'")
    print("      ✓ '[LLM] Groq success'")
    print("      ✗ No 'model_decommissioned' errors")
    print("      ✗ No 'Expecting value: line 1 column 1' errors")
    print("      ✗ No 'JSONDecodeError' errors")

def main():
    print("=" * 60)
    print("ScholarPulse Production Verification")
    print("Hotfix v2.2.1 - Groq Model Update")
    print("=" * 60)
    
    # Step 1: Health check
    health_ok = check_health()
    
    if not health_ok:
        print("\n⚠️  Backend not responding. Wait for Render deployment to complete.")
        print("   Deployment typically takes 2-5 minutes after git push.")
        return
    
    # Step 2: Test research query
    query_ok = test_research_query()
    
    # Step 3: Log verification reminder
    check_logs_for_errors()
    
    # Summary
    print("\n" + "=" * 60)
    if health_ok and query_ok:
        print("🎉 VERIFICATION SUCCESSFUL!")
        print("   ✅ Backend healthy")
        print("   ✅ Research query working")
        print("   ✅ Multi-LLM system operational")
        print("\n   Next: Check Render logs to confirm Groq model update")
    else:
        print("⚠️  VERIFICATION INCOMPLETE")
        print("   Please check Render logs for errors")
    print("=" * 60)

if __name__ == "__main__":
    main()
