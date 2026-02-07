import logging
import json
import textwrap
from typing import Any
from utils import clean_json_string
from .llm import LLMClient

logger = logging.getLogger(__name__)

class HypothesisGenerator:
    """Generates novel research ideas from a list of paper summaries."""

    def __init__(self, llm_provider: str = None):
        self.llm = LLMClient(provider=llm_provider)

    def generate_new_ideas(self, papers: list[dict]) -> list[dict]:
        """Generates 9 new research ideas based on the provided papers."""
        joined_summaries = "\n\n".join([f"- {p['title']}: {p.get('summary', '')[:200]}..." for p in papers])
        
        prompt = textwrap.dedent(
            f"""
            Based on the following research papers, propose 9 NOVEL and DISTINCT research ideas/directions for future work.
            
            Papers:
            {joined_summaries}
            
            For each idea, provide:
            1. Title (Academic & Technical)
            2. Description (3-4 sentences detailing the methodology and why it's novel)
            3. Detailed Requirements (Hardware, specific Python libraries, and datasets)

            STRICT RULE: Your output values must NOT contain any HTML tags, CSS styles, or Markdown formatting (like bold, links, or backticks). Provide raw text ONLY.

            Output strictly as a JSON list of objects:
            [
              {{
                "title": "...",
                "description": "...",
                "requirements": ["...", "..."]
              }},
              ...
            ]
            """
        )
        
        
        
        # Add retry logic for ideas generation
        # We can implement a simple loop here or rely on LLM client stability
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if self.llm.available:
                    response = self.llm.generate(prompt, max_tokens=2048)
                    if not response:
                        continue
                        
                    cleaned = clean_json_string(response)
                    return json.loads(cleaned)
            except Exception as e:
                logger.error(f"Failed to generate new ideas (attempt {attempt+1}): {e}")
                if attempt == max_retries - 1:
                    pass
            
        # Fallback
        return [
            {
                "title": "Hybrid Architecture Exploration",
                "description": "Combine the strengths of identified methods to create a robust hybrid model.",
                "requirements": ["Standard GPU cluster", "PyTorch"]
            }
        ]

    def generate_report_sections(self, query, papers):
        """Generates broadly synthesized Intro, Issue, and Conclusion sections."""
        import time
        max_retries = 3
        
        # Prepare context (use more paper objectives for better synthesis)
        context = f"Research Theme: {query}\n"
        context += "\n".join([f"- {p['title']}: {p.get('objective', '')}" for p in papers[:10]])

        prompt = textwrap.dedent(f"""
            You are a lead research scientist writing a comprehensive state-of-the-art report.
            Contextual Papers:
            {context}

            Generate three deep-dive sections for the final report. 
            CRITICAL: Use multiple full paragraphs (minimum 3-4 paragraphs) for each section. Do not use bullet points here.
            
            1. INTRODUCTION (Academic Narrative)
               - Deeply analyze the research landscape of {query}.
               - Connect historical context with modern-day technological shifts.
               - Discuss the industrial and societal significance in detail.

            2. THE ISSUE (Technical Analysis)
               - Breakdown the fundamental technical bottlenecks identified in the provided papers.
               - Discuss the limitations of current methodologies (precision, complexity, resource consumption).
               - Explain why these issues are critical to solve for next-gen deployment.

            3. CONCLUSION (Strategic Outlook)
               - Synthesize the findings into a coherent future vision.
               - Predict the long-term trajectory of this specific research path.
               - Offer a visionary outlook on how this field will transform in the next 5-10 years.

            STRICT RULE: Your output values must NOT contain any HTML tags, CSS styles, or Markdown formatting (like bold, links, or backticks). Provide raw text ONLY.

            Output strictly as a JSON object:
            {{
              "introduction": "...",
              "the_issue": "...",
              "conclusion": "..."
            }}
        """)

        for attempt in range(max_retries):
            try:
                if self.llm.available:
                    # Request more tokens for the broader narrative
                    response = self.llm.generate(prompt, max_tokens=3072).strip()
                    if response.startswith("```json"):
                        response = response[7:]
                    if response.startswith("```"):
                        response = response[3:]
                    if response.endswith("```"):
                        response = response[:-3]
                    return json.loads(response.strip())
            except Exception as e:
                logger.error(f"Failed to generate report sections (attempt {attempt+1}): {e}")
        
        # Fallback
        return {
            "introduction": f"This report explores '{query}' through analysis of top research papers.",
            "the_issue": "The core issue involves optimizing performance and accuracy in this domain.",
            "conclusion": "The findings suggest significant potential for future improvements."
        }
