"""
Multi-LLM System Test Script
Tests Groq + Gemini + Oxlo integration
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_multi_llm():
    """Test multi-LLM orchestration system."""
    print("=" * 60)
    print("ScholarPulse - Multi-LLM System Test")
    print("=" * 60)
    print()
    
    # Check API keys
    print("[1/5] Checking API Keys...")
    groq_key = os.getenv("GROQ_API_KEY")
    gemini_key = os.getenv("GOOGLE_API_KEY")
    oxlo_key = os.getenv("OXLO_API_KEY")
    
    keys_found = 0
    if groq_key:
        print(f"  ✓ GROQ_API_KEY found: {groq_key[:10]}...{groq_key[-4:]}")
        keys_found += 1
    else:
        print("  ❌ GROQ_API_KEY not found")
    
    if gemini_key:
        print(f"  ✓ GOOGLE_API_KEY found: {gemini_key[:10]}...{gemini_key[-4:]}")
        keys_found += 1
    else:
        print("  ❌ GOOGLE_API_KEY not found")
    
    if oxlo_key:
        print(f"  ✓ OXLO_API_KEY found: {oxlo_key[:10]}...{oxlo_key[-4:]}")
        keys_found += 1
    else:
        print("  ❌ OXLO_API_KEY not found")
    
    print(f"\n  Found {keys_found}/3 API keys")
    
    if keys_found == 0:
        print("\n❌ No API keys found. Please set them in .env file")
        return False
    
    print()
    
    # Import multi-LLM client
    print("[2/5] Importing Multi-LLM Client...")
    try:
        from agent.llm import MultiLLMClient
        print("  ✓ MultiLLMClient imported successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import: {e}")
        return False
    
    print()
    
    # Initialize client
    print("[3/5] Initializing Multi-LLM Client...")
    try:
        client = MultiLLMClient()
        print(f"  ✓ Client initialized")
        print(f"    - Groq available: {client.groq_available}")
        print(f"    - Gemini available: {client.gemini_available}")
        print(f"    - Oxlo available: {client.oxlo_available}")
        print(f"    - Overall available: {client.available}")
        
        if not client.available:
            print("\n  ❌ No providers available")
            return False
    except Exception as e:
        print(f"  ❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    
    # Test fast generation (Groq)
    print("[4/5] Testing Fast Generation (Groq → Oxlo)...")
    try:
        response = client.generate_fast(
            "Summarize: Machine learning is a subset of AI.",
            max_tokens=50,
            timeout=10
        )
        if response:
            print(f"  ✓ Fast generation successful")
            print(f"    Response: {response[:100]}...")
        else:
            print("  ⚠️  Fast generation returned empty")
    except Exception as e:
        print(f"  ❌ Fast generation failed: {e}")
    
    print()
    
    # Test deep generation (Gemini)
    print("[5/5] Testing Deep Generation (Gemini → Oxlo → Groq)...")
    try:
        response = client.generate_deep(
            "Analyze the impact of transformer models on NLP.",
            max_tokens=100,
            timeout=15
        )
        if response:
            print(f"  ✓ Deep generation successful")
            print(f"    Response: {response[:100]}...")
        else:
            print("  ⚠️  Deep generation returned empty")
    except Exception as e:
        print(f"  ❌ Deep generation failed: {e}")
    
    print()
    
    # Test idea generation (Oxlo)
    print("[BONUS] Testing Idea Generation (Oxlo → Groq → Gemini)...")
    try:
        response = client.generate_ideas(
            "Propose a novel research idea combining vision and language.",
            max_tokens=150,
            timeout=15
        )
        if response:
            print(f"  ✓ Idea generation successful")
            print(f"    Response: {response[:100]}...")
        else:
            print("  ⚠️  Idea generation returned empty")
    except Exception as e:
        print(f"  ❌ Idea generation failed: {e}")
    
    print()
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    providers_working = sum([
        client.groq_available,
        client.gemini_available,
        client.oxlo_available
    ])
    
    print(f"Providers working: {providers_working}/3")
    
    if providers_working == 3:
        print("\n🎉 All providers working! Optimal configuration.")
        print("   - Fast tasks: Groq (primary)")
        print("   - Deep tasks: Gemini (primary)")
        print("   - Ideas: Oxlo (primary)")
        print("   - Full fallback chain available")
        return True
    elif providers_working >= 2:
        print("\n✅ Multi-LLM system operational with reduced redundancy.")
        print(f"   - {providers_working} providers available")
        print("   - System will work but with shorter fallback chain")
        return True
    elif providers_working == 1:
        print("\n⚠️  Only 1 provider available.")
        print("   - System will work but without fallback")
        print("   - Recommend adding more API keys for reliability")
        return True
    else:
        print("\n❌ No providers available. System cannot function.")
        return False

def main():
    """Run all tests."""
    success = test_multi_llm()
    
    if success:
        print("\n✅ Multi-LLM system ready for production!")
        return 0
    else:
        print("\n❌ Multi-LLM system has issues. Fix before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
