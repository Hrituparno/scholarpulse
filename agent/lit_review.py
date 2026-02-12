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
        # Use new multi-LLM client for intelligent routing
        from .llm import MultiLLMClient
        self.llm = MultiLLMClient()
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

    def refine_query(self, user_query: str, timeout=5) -> str:
        """
        Fast query refinement with timeout.
        Skips LLM if not available or times out.
        """
        if not self.llm.available:
            return user_query

        prompt = (
            f"Convert to arXiv query (boolean operators OK): '{user_query}'\n"
            f"Output ONLY the query string."
        )
        
        try:
            refined = self.llm.generate(prompt, max_tokens=50, retries=1).strip().replace('"', '').replace('`', '').strip()
            
            if not refined or len(refined) < 3:
                logger.warning("Query refinement returned empty, using original")
                return user_query

            # Balance parentheses
            open_count = refined.count('(')
            close_count = refined.count(')')
            if open_count > close_count:
                refined += ')' * (open_count - close_count)
            elif close_count > open_count:
                refined = '(' * (close_count - open_count) + refined
            
            logger.info(f"Refined query: {refined}")
            return refined
        except Exception as e:
            logger.warning(f"Query refinement failed: {e}, using original")
            return user_query

    def search(self, query, max_results=5, timeout=15):
        """
        Balanced arXiv search with quality and speed.
        
        Args:
            query: Search query
            max_results: Papers to fetch (5 for quality/speed balance)
            timeout: Maximum seconds for arXiv fetch (default: 15)
            
        Returns:
            List of paper dicts with multi-LLM enrichment
        """
        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
        import signal
        
        papers = []
        
        def timeout_handler(signum, frame):
            raise TimeoutError("arXiv search timed out")
        
        try:
            # Set alarm for timeout (Unix only, fallback for Windows)
            if hasattr(signal, 'SIGALRM'):
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(timeout)
            
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            # Fetch papers with timeout protection
            result_count = 0
            for r in search.results():
                if result_count >= max_results:
                    break
                    
                encoded_title = urllib.parse.quote(r.title)
                scholar_url = f"https://scholar.google.com/scholar?q={encoded_title}"
                
                papers.append({
                    "title": r.title,
                    "authors": [a.name for a in r.authors][:5],  # Keep more authors for quality
                    "summary": r.summary[:800],  # Longer summaries for better analysis
                    "pdf_url": r.pdf_url,
                    "google_scholar_url": scholar_url,
                    "objective": "Analyzing...",
                    "techniques": ["Analyzing..."],
                })
                result_count += 1
            
            # Cancel alarm
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)
                
        except TimeoutError:
            logger.warning(f"arXiv search timed out after {timeout}s, returning {len(papers)} papers")
        except Exception as e:
            logger.error(f"arXiv search failed: {e}")
            return []
        
        # Multi-LLM parallel enrichment with intelligent routing
        if self.llm.available and papers:
            logger.info(f"Enriching {len(papers)} papers with multi-LLM system")
            
            # Prepare prompts for batch processing
            prompts = []
            for paper in papers:
                prompt = (
                    f"Extract key details from this research abstract in JSON format.\n"
                    f"Abstract: {paper['summary'][:600]}\n\n"
                    f"Return JSON: {{"
                    f"'objective': 'one clear sentence', "
                    f"'method': 'core technique', "
                    f"'tools': 'technologies used', "
                    f"'results': 'key finding', "
                    f"'application': 'domain'}}"
                )
                prompts.append(prompt)
            
            try:
                # Batch fast generation using Groq (with Oxlo fallback)
                responses = self.llm.batch_generate_fast(
                    prompts=prompts,
                    max_tokens=384,  # Balanced for quality
                    max_workers=3,
                    timeout_per_task=10
                )
                
                # Parse responses and update papers with safe JSON handling
                for i, (paper, response) in enumerate(zip(papers, responses)):
                    if response and response.strip():
                        try:
                            from utils import clean_json_string
                            cleaned = clean_json_string(response)
                            
                            # Validate cleaned string is not empty
                            if not cleaned or cleaned.strip() == "":
                                logger.warning(f"[LLM] Paper {i}: Cleaned JSON is empty, using fallback")
                                self._set_fallback_values(paper)
                                continue
                            
                            # Safe JSON parsing
                            try:
                                data = json.loads(cleaned)
                            except json.JSONDecodeError as json_err:
                                logger.warning(f"[LLM] Paper {i}: JSON parse error - {json_err}, using fallback")
                                self._set_fallback_values(paper)
                                continue
                            
                            # Validate data is a dict
                            if not isinstance(data, dict):
                                logger.warning(f"[LLM] Paper {i}: JSON is not a dict, using fallback")
                                self._set_fallback_values(paper)
                                continue
                            
                            paper["objective"] = data.get("objective", "Research analysis")
                            paper["application"] = data.get("application", "Scientific research")
                            paper["method"] = data.get("method", "Advanced methodology")
                            paper["tools"] = data.get("tools", "Research tools")
                            paper["results"] = data.get("results", "Significant findings")
                            paper["limitations"] = data.get("limitations", "Standard limitations")
                            paper["techniques"] = [paper["method"], paper["tools"]]
                            
                        except Exception as e:
                            logger.warning(f"[LLM] Failed to parse enrichment for paper {i}: {e}")
                            self._set_fallback_values(paper)
                    else:
                        logger.warning(f"[LLM] Paper {i}: Empty response, using fallback")
                        self._set_fallback_values(paper)
                        
            except Exception as e:
                logger.error(f"Batch enrichment failed: {e}")
                # Set fallback values for all papers
                for paper in papers:
                    self._set_fallback_values(paper)
                
        return papers
    
    def _set_fallback_values(self, paper: dict):
        """Set fallback values for paper enrichment."""
        paper["objective"] = "Research paper analysis"
        paper["application"] = "Scientific research"
        paper["method"] = "Scientific methodology"
        paper["tools"] = "Research tools"
        paper["results"] = "Research findings"
        paper["limitations"] = "Standard limitations"
        paper["techniques"] = [paper["method"], paper["tools"]]

    def _enrich_paper(self, paper: dict) -> None:
        """
        Fast LLM enrichment with reduced token usage.
        Uses shorter prompt and faster model for speed.
        """
        # Shortened prompt for speed
        prompt = (
            f"Extract key details from this abstract in JSON format.\n"
            f"Abstract: {paper['summary'][:400]}\n\n"  # Truncated for speed
            f"Return JSON: {{"
            f"'objective': 'one sentence', "
            f"'method': 'technique name', "
            f"'tools': 'tools used', "
            f"'results': 'key finding'}}"
        )
        
        try:
            # Use faster generation with lower token limit
            response = self.llm.generate(prompt, max_tokens=256, retries=1)
            if not response:
                return

            from utils import clean_json_string
            cleaned = clean_json_string(response)
            data = json.loads(cleaned)
            
            paper["objective"] = data.get("objective", "Research analysis")
            paper["application"] = data.get("application", "Scientific research")
            paper["method"] = data.get("method", "Advanced methodology")
            paper["tools"] = data.get("tools", "Standard tools")
            paper["results"] = data.get("results", "Significant findings")
            paper["limitations"] = data.get("limitations", "Standard limitations")
            paper["techniques"] = [paper["method"], paper["tools"]]
            
        except Exception as e:
            logger.warning(f"Fast enrichment failed for '{paper.get('title', 'Unknown')[:50]}': {e}")
            # Set fallback values
            paper["objective"] = "Research paper analysis"
            paper["method"] = "Scientific methodology"
            paper["tools"] = "Research tools"
            paper["results"] = "Research findings"

