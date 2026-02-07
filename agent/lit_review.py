import logging
import json
import urllib.parse
import arxiv
import requests
import os
from dotenv import load_dotenv
from .llm import LLMClient
from config import SERPER_API_KEY_ENV

load_dotenv()

logger = logging.getLogger(__name__)

class LiteratureReviewer:
    """Fetches papers from arXiv and enriches them with LLM analysis.
    
    Results are returned as list of dicts with:
    - title, authors, summary, pdf_url, google_scholar_url
    - objective: (LLM inferred)
    - techniques: (LLM inferred)
    """

    def __init__(self, llm_provider: str = None):
        self.llm = LLMClient(provider=llm_provider)
        self.serper_key = os.getenv(SERPER_API_KEY_ENV)

    def web_search(self, query: str, num_results: int = 5) -> list[dict]:
        """Perform a live web search via Serper API."""
        if not self.serper_key:
            logger.warning("Serper API key missing. Skipping web search.")
            return []

        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query, "num": num_results})
        headers = {
            'X-API-KEY': self.serper_key,
            'Content-Type': 'application/json'
        }

        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            results = response.json().get("organic", [])
            
            web_papers = []
            for r in results:
                web_papers.append({
                    "title": r.get("title", "Untitled"),
                    "summary": r.get("snippet", "No summary available."),
                    "authors": ["Web Content"],
                    "pdf_url": r.get("link", "#"),
                    "google_scholar_url": r.get("link", "#"),
                    "objective": "Web analysis pending",
                    "application": "General Web",
                    "method": "Web Discovery",
                    "tools": "Web Search",
                    "results": "Live Data",
                    "limitations": "Non-peer reviewed"
                })
            return web_papers
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return []

    def refine_query(self, user_query: str) -> str:
        """Use LLM to translate natural language into a professional arXiv query string."""
        if not self.llm.available:
            return user_query

        prompt = (
            f"You are a professional research librarian. Translate the following user request into a precise, "
            f"highly relevant arXiv research query string using boolean operators (AND, OR, ANDNOT) if necessary. "
            f"Aim for technical depth and exclude obvious noise.\n\n"
            f"User Request: '{user_query}'\n\n"
            f"Output ONLY the optimized query string, nothing else."
        )
        
        try:
            refined = self.llm.generate(prompt, max_tokens=100).strip().replace('"', '').replace('`', '').strip()
            
            # Failsafe: If AI returns nothing or just nonsense, use the original query
            if not refined or len(refined) < 3:
                logger.warning("AI query refinement returned empty/short result. Falling back to original.")
                return user_query

            # Ensure balanced parentheses
            open_count = refined.count('(')
            close_count = refined.count(')')
            if open_count > close_count:
                refined += ')' * (open_count - close_count)
            elif close_count > open_count:
                refined = '(' * (close_count - open_count) + refined
            
            # Final sanity check: if it starts and ends with parens, don't double wrap unnecessarily
            if refined.startswith('(') and refined.endswith(')'):
                inner = refined[1:-1]
                if inner.count('(') == inner.count(')'):
                    pass 
            
            logger.info(f"Refined query: {refined}")
            return refined
        except Exception as e:
            logger.warning(f"Query refinement failed: {e}")
            return user_query

    def search(self, query, max_results=8):
        from concurrent.futures import ThreadPoolExecutor
        
        search = arxiv.Search(query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance)
        papers = []
        
        # Initial extraction
        for r in search.results():
            encoded_title = urllib.parse.quote(r.title)
            scholar_url = f"https://scholar.google.com/scholar?q={encoded_title}"
            
            papers.append({
                "title": r.title,
                "authors": [a.name for a in r.authors],
                "summary": r.summary,
                "pdf_url": r.pdf_url,
                "google_scholar_url": scholar_url,
                "objective": "Analyzing...",
                "techniques": ["Analyzing..."],
            })
            
        # Parallel Enrichment
        if self.llm.available and papers:
            with ThreadPoolExecutor(max_workers=len(papers)) as executor:
                executor.map(self._enrich_paper, papers)
                
        return papers

    def _enrich_paper(self, paper: dict) -> None:
        """Use LLM to infer details using Professional Inference (filling gaps logically)."""
        prompt = (
            f"Analyze this research abstract and extract details.\n"
            f"CRITICAL: If a field is not explicitly stated, use your technical knowledge to INFER the most likely industrial standard or methodology used in this domain. DO NOT write 'N/A' or 'Not mentioned'. Provide a logical 'Best Guess'.\n\n"
            f"STRICT RULE: Your output values must NOT contain any HTML tags, CSS styles, or Markdown formatting (like bold, links, or backticks). Provide raw text ONLY.\n\n"
            f"Abstract: {paper['summary']}\n\n"
            f"Extract:\n"
            f"1. Objective: (1 concise sentence)\n"
            f"2. Application Area: (e.g., 'Precision Agriculture', 'Edge Computing')\n"
            f"3. Core Methodology: (e.g., 'CNN', 'Reinforcement Learning')\n"
            f"4. Industrial Tools: (e.g., 'PyTorch', 'ROS', 'Kubernetes' - INFER based on the field if missing)\n"
            f"5. Key Results/Performance: (Specific metrics or 'Improved state-of-the-art accuracy' if precise numbers missing)\n"
            f"6. Primary Limitation: (1 brief point)\n\n"
            f"Output strictly as a JSON object: {{"
            f"'objective': '...', 'application': '...', 'method': '...', "
            f"'tools': '...', 'results': '...', 'limitations': '...'}}"
        )
        
        try:
            response = self.llm.generate(prompt, max_tokens=1024)
            if not response: return

            from utils import clean_json_string
            cleaned = clean_json_string(response)
            data = json.loads(cleaned)
            
            paper["objective"] = data.get("objective", "Analyzing...")
            paper["application"] = data.get("application", "Inferred from context")
            paper["method"] = data.get("method", "Inferred from domain")
            paper["tools"] = data.get("tools", "Standard domain tools")
            paper["results"] = data.get("results", "Inferred from discussion")
            paper["limitations"] = data.get("limitations", "Inferred from constraints")
            paper["techniques"] = [paper["method"], paper["tools"]]
            
        except Exception as e:
            logger.warning(f"Enrichment failed for '{paper.get('title')}': {e}")

