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
        # Use multi-LLM client for intelligent routing
        from .llm import MultiLLMClient
        self.llm = MultiLLMClient()

    def generate_ideas_groq_only(self, papers: list[dict], max_ideas=5) -> list[dict]:
        """
        LIGHTWEIGHT idea generation using ONLY Groq (no Oxlo to save memory).
        Optimized for Render free tier.
        """
        joined_summaries = "\n".join([
            f"- {p['title']}: {p.get('summary', '')[:200]}"
            for p in papers[:5]
        ])
        
        prompt = f"""Based on these papers, propose {max_ideas} research ideas.

Papers:
{joined_summaries}

Output as JSON array:
[
  {{"title": "...", "description": "...", "requirements": ["..."]}}
]
"""
        
        try:
            if self.llm.groq_available:
                logger.info("[GROQ] Generating ideas")
                response = self.llm._call_groq(prompt, max_tokens=1200, timeout=30)
                
                if response and response.strip():
                    cleaned = clean_json_string(response)
                    if cleaned and cleaned.strip():
                        ideas = json.loads(cleaned)
                        if isinstance(ideas, list) and len(ideas) > 0:
                            logger.info(f"[GROQ] Generated {len(ideas)} ideas")
                            return ideas[:max_ideas]
        except Exception as e:
            logger.error(f"[GROQ] Idea generation failed: {e}")
        
        # Simple fallback
        return [
            {
                "title": "Enhanced Multi-Modal Learning",
                "description": "Combine methodologies from analyzed papers for improved cross-domain performance.",
                "requirements": ["GPU", "PyTorch", "Multi-modal data"]
            },
            {
                "title": "Efficient Transfer Learning",
                "description": "Develop lightweight adaptation for resource-constrained deployment.",
                "requirements": ["Edge devices", "TensorFlow Lite"]
            },
            {
                "title": "Robust Evaluation Framework",
                "description": "Create comprehensive benchmarking system for fair comparison.",
                "requirements": ["Benchmark datasets", "Evaluation metrics"]
            }
        ]

    def generate_new_ideas(self, papers: list[dict], max_ideas=5) -> list[dict]:
        """
        High-quality idea generation using Oxlo (primary) with Groq fallback.
        Generates 5 ideas for better quality while maintaining speed.
        """
        # Use more papers and longer summaries for better quality
        joined_summaries = "\n".join([
            f"- {p['title']}: {p.get('summary', '')[:250]}..."
            for p in papers[:7]  # Use more papers for context
        ])
        
        prompt = textwrap.dedent(
            f"""
            Based on these research papers, propose {max_ideas} novel and high-quality research ideas.
            
            Papers:
            {joined_summaries}
            
            For each idea provide:
            1. Title (clear and specific)
            2. Description (3 sentences explaining novelty and approach)
            3. Requirements (specific tools, datasets, hardware)

            Output as JSON array:
            [
              {{
                "title": "...",
                "description": "...",
                "requirements": ["...", "..."]
              }}
            ]
            """
        )
        
        # Use Oxlo for idea generation (primary) with fallback
        try:
            if self.llm.available:
                logger.info("[LLM] Generating ideas with Oxlo")
                response = self.llm.generate_ideas(prompt, max_tokens=1536, timeout=20)
                
                if response and response.strip():
                    try:
                        cleaned = clean_json_string(response)
                        
                        # Validate cleaned string
                        if not cleaned or cleaned.strip() == "":
                            logger.warning("[LLM] Cleaned ideas JSON is empty, using fallback")
                            raise ValueError("Empty JSON after cleaning")
                        
                        ideas = json.loads(cleaned)
                        
                        # Validate ideas is a list
                        if not isinstance(ideas, list):
                            logger.warning("[LLM] Ideas JSON is not a list, using fallback")
                            raise ValueError("Ideas is not a list")
                        
                        logger.info(f"[LLM] Successfully generated {len(ideas)} ideas")
                        return ideas[:max_ideas]  # Ensure we don't exceed max
                        
                    except (json.JSONDecodeError, ValueError) as e:
                        logger.warning(f"[LLM] Failed to parse ideas JSON: {e}, using fallback")
                else:
                    logger.warning("[LLM] Empty response from idea generation, using fallback")
        except Exception as e:
            logger.error(f"[LLM] Idea generation failed: {e}")
        
        # Quality fallback with multiple ideas
        return [
            {
                "title": "Hybrid Multi-Modal Architecture",
                "description": "Combine identified methodologies with cross-modal learning for robust performance across diverse data types.",
                "requirements": ["GPU cluster", "PyTorch", "Multi-modal datasets"]
            },
            {
                "title": "Efficient Transfer Learning Framework",
                "description": "Develop lightweight adaptation techniques for rapid deployment in resource-constrained environments.",
                "requirements": ["Edge devices", "TensorFlow Lite", "Benchmark datasets"]
            }
        ]

    def generate_report_sections(self, query, papers, use_deep_synthesis=True):
        """
        High-quality report generation using Gemini for deep synthesis.
        Uses Gemini's superior reasoning for comprehensive analysis.
        """
        if use_deep_synthesis:
            # Rich context for quality synthesis
            context = f"Research Topic: {query}\n\n"
            context += "Key Papers:\n"
            context += "\n".join([
                f"- {p['title']}\n  Objective: {p.get('objective', 'N/A')}\n  Method: {p.get('method', 'N/A')}"
                for p in papers[:5]
            ])

            prompt = textwrap.dedent(f"""
                You are a senior research scientist writing a comprehensive analysis report.
                
                Topic: {query}
                
                Context:
                {context}

                Generate 3 well-structured sections:

                1. INTRODUCTION (3-4 paragraphs)
                   - Analyze the research landscape
                   - Connect historical context with current advances
                   - Discuss significance and impact

                2. KEY FINDINGS (3-4 paragraphs)
                   - Synthesize core technical insights from papers
                   - Identify patterns and breakthroughs
                   - Discuss methodological advances

                3. CONCLUSION (2-3 paragraphs)
                   - Synthesize findings into coherent vision
                   - Predict future trajectory
                   - Offer strategic outlook

                Output as JSON:
                {{
                  "introduction": "...",
                  "the_issue": "...",
                  "conclusion": "..."
                }}
            """)

            try:
                if self.llm.available:
                    logger.info("[LLM] Generating report with Gemini deep synthesis")
                    # Use Gemini for deep synthesis (primary) with Oxlo fallback
                    response = self.llm.generate_deep(prompt, max_tokens=2048, timeout=30).strip()
                    
                    if not response or response.strip() == "":
                        logger.warning("[LLM] Empty response from report generation, using fallback")
                        raise ValueError("Empty response")
                    
                    if response.startswith("```json"):
                        response = response[7:]
                    if response.startswith("```"):
                        response = response[3:]
                    if response.endswith("```"):
                        response = response[:-3]
                    
                    response = response.strip()
                    
                    # Validate before parsing
                    if not response:
                        logger.warning("[LLM] Response empty after cleaning, using fallback")
                        raise ValueError("Empty after cleaning")
                    
                    try:
                        report_data = json.loads(response)
                        
                        # Validate structure
                        if not isinstance(report_data, dict):
                            logger.warning("[LLM] Report JSON is not a dict, using fallback")
                            raise ValueError("Not a dict")
                        
                        logger.info("[LLM] Successfully generated report sections")
                        return report_data
                        
                    except json.JSONDecodeError as json_err:
                        logger.warning(f"[LLM] Failed to parse report JSON: {json_err}, using fallback")
                        
            except Exception as e:
                logger.error(f"[LLM] Deep synthesis failed: {e}")
        
        # Quality fallback
        return {
            "introduction": f"This comprehensive report explores '{query}' through systematic analysis of recent research papers. The field has seen significant advances in methodology and application, with researchers pushing the boundaries of what's possible. Understanding these developments is crucial for future innovation.",
            "the_issue": "The core challenge involves balancing performance, efficiency, and scalability in real-world deployments. Current methodologies show promise but face limitations in generalization and resource requirements. Addressing these bottlenecks is critical for next-generation systems.",
            "conclusion": "The findings reveal substantial potential for transformative advances in this domain. By synthesizing insights from multiple research directions, we can chart a path toward more robust and efficient solutions. The next 5-10 years will likely see breakthrough innovations that reshape the field."
        }
