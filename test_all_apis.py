#!/usr/bin/env python3
"""Test ALL three LLM APIs to verify they work"""

import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("Testing ALL LLM APIs")
print("=" * 60)

# Test 1: Groq
print("\n[1/3] Testing Groq API...")
groq_key = os.getenv("GROQ_API_KEY")
if not groq_key:
    print("  ❌ GROQ_API_KEY not found in .env")
else:
    print(f"  ✓ GROQ_API_KEY found: {groq_key[:10]}...{groq_key[-4:]}")
    try:
        from groq import Groq
        client = Groq(api_key=groq_key)
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": "Say 'Groq works'"}],
            model="llama-3.3-70b-versatile",
            max_tokens=10
        )
        result = response.choices[0].message.content
        print(f"  ✓ Groq response: {result}")
        print("  ✅ GROQ API WORKING")
    except Exception as e:
        print(f"  ❌ Groq failed: {e}")

# Test 2: Gemini
print("\n[2/3] Testing Gemini API...")
gemini_key = os.getenv("GOOGLE_API_KEY")
if not gemini_key:
    print("  ❌ GOOGLE_API_KEY not found in .env")
else:
    print(f"  ✓ GOOGLE_API_KEY found: {gemini_key[:10]}...{gemini_key[-4:]}")
    try:
        from google import genai
        client = genai.Client(api_key=gemini_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="Say 'Gemini works'"
        )
        result = response.text
        print(f"  ✓ Gemini response: {result}")
        print("  ✅ GEMINI API WORKING")
    except Exception as e:
        print(f"  ❌ Gemini failed: {e}")

# Test 3: Oxlo
print("\n[3/3] Testing Oxlo API...")
oxlo_key = os.getenv("OXLO_API_KEY")
if not oxlo_key:
    print("  ❌ OXLO_API_KEY not found in .env")
else:
    print(f"  ✓ OXLO_API_KEY found: {oxlo_key[:10]}...{oxlo_key[-4:]}")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=oxlo_key, base_url="https://api.oxlo.ai/v1")
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": "Say 'Oxlo works'"}],
            model="llama-3.1-70b",
            max_tokens=10
        )
        result = response.choices[0].message.content
        print(f"  ✓ Oxlo response: {result}")
        print("  ✅ OXLO API WORKING")
    except Exception as e:
        print(f"  ❌ Oxlo failed: {e}")

print("\n" + "=" * 60)
print("API Test Complete")
print("=" * 60)
