"""Test script to load `.env` and call Google Gemini (best-effort).

Usage:
  - Copy `.env.example` to `.env` and set `GOOGLE_API_KEY`.
  - Install requirements: `pip install -r requirements.txt`
  - Run: `python scripts/test_gemini.py`

This script tries `generate_text` then falls back to `chat.create` depending on
the installed `google-generativeai` package version.
"""
import os
import sys
from dotenv import load_dotenv


def main():
    # Ensure project root is on sys.path so `from config import ...` works when
    # running this script directly (python scripts/test_gemini.py).
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    env_path = os.path.join(project_root, ".env")
    load_dotenv(env_path)

    api_key = os.getenv("GOOGLE_API_KEY")
    from config import GEMINI_MODEL as DEFAULT_GEMINI_MODEL
    model = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)
    if not api_key or api_key.startswith("YOUR_"):
        print("ERROR: Set GOOGLE_API_KEY in .env (copy .env.example -> .env and paste your key).")
        return

    # Prefer new package, fall back to deprecated one
    genai = None
    try:
        import google.genai as genai
    except Exception:
        try:
            import google.generativeai as genai
        except Exception as e:
            print("ERROR: google-genai and google-generativeai are not installed:", e)
            return

    try:
        if hasattr(genai, "configure") and api_key:
            genai.configure(api_key=api_key)
    except Exception:
        # Not all package versions expose configure; env var fallback is fine.
        pass

    prompt = "Write a one-sentence hypothesis about improving transformer inference efficiency."

    # Try generate_text if available
    # Prefer the new `google.genai` client usage (Client -> models.generate_content)
    try:
        client = genai.Client(api_key=api_key) if hasattr(genai, "Client") else None
    except Exception as e:
        print("ERROR: failed to construct genai Client:", e)
        client = None

    try:
        if client and hasattr(client, "models") and hasattr(client.models, "generate_content"):
            resp = client.models.generate_content(model=model, contents=prompt)
            # Attempt to extract text
            if hasattr(resp, "output"):
                print("RESPONSE:\n", resp.output)
            elif hasattr(resp, "candidates"):
                cand = resp.candidates
                if cand:
                    first = cand[0]
                    if hasattr(first, "content"):
                        print("RESPONSE:\n", first.content)
                    elif isinstance(first, dict):
                        print("RESPONSE:\n", first.get("content") or first.get("text") or first)
                    else:
                        print("RESPONSE:\n", first)
            else:
                print("RESPONSE:\n", resp)
            return

        # Older fallback: try chat.create on module or client if available
        if client and hasattr(client, "chats") and hasattr(client.chats, "create"):
            resp = client.chats.create(model=model, history=[{"type": "input_text", "text": prompt}])
            print("RESPONSE:\n", resp)
            return

        if hasattr(genai, "chat") and hasattr(genai.chat, "create"):
            resp = genai.chat.create(model=model, messages=[{"role": "user", "content": prompt}], max_output_tokens=128)
            print("RESPONSE:\n", resp)
            return

        print("ERROR: installed genai package does not expose a supported API surface on this system.")

    except Exception as e:
        print("API request failed:", e)


if __name__ == "__main__":
    main()
