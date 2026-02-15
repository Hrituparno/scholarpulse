"""
Agent Service - Bridges Django backend with existing research agents.

This service wraps the existing AgentRunner logic and integrates it
with Django's database and error handling.
"""
import sys
import os
import logging
import traceback
from pathlib import Path
from typing import Optional, Callable
from django.conf import settings

# Add parent directory to path to import existing agent modules
AGENT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(AGENT_ROOT))

logger = logging.getLogger(__name__)


class AgentService:
    """
    Service layer for executing research tasks.
    
    Wraps the existing AgentRunner with:
    - Progress tracking callbacks
    - Database state updates
    - Structured error handling
    - Partial result support
    """
    
    def __init__(self, task_id: str, on_progress: Optional[Callable] = None):
        self.task_id = task_id
        self.on_progress = on_progress
        self.output_dir = getattr(settings, 'SCHOLARPULSE_OUTPUT_DIR', str(AGENT_ROOT / 'output'))
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
    def execute(self, task) -> dict:
        """
        Execute research pipeline - ULTRA LIGHTWEIGHT for Render Free Tier.
        Strategy: Use ONLY Groq (fast + reliable), skip heavy operations.
        
        Args:
            task: ResearchTask model instance
            
        Returns:
            dict with papers, ideas, report_sections, report_formats
        """
        from research.models import ResearchTask, ErrorLog
        import gc
        
        params = task.input_params
        query = params.get('query', '')
        mode = params.get('mode', 'Deep Research')
        year_filter = params.get('year_filter')
        llm_provider = 'groq'  # Force Groq only for memory efficiency
        
        logger.info(f"[LIGHTWEIGHT] Starting task {self.task_id}: {query[:50]}")
        task.mark_running()
        
        try:
            # Phase 1: Paper Search (0-50%)
            self._update_progress(task, 10, "Searching papers...")
            
            from agent.lit_review import LiteratureReviewer
            reviewer = LiteratureReviewer(llm_provider=llm_provider)
            
            if not reviewer.llm.available:
                raise RuntimeError(f"Groq API not available. Check GROQ_API_KEY.")
            
            # Search papers
            if mode == "Web Search":
                papers = reviewer.web_search(query, num_results=5)
            else:
                search_query = query
                if year_filter and year_filter > 0:
                    search_query = f'({query}) AND submittedDate:[{year_filter}01010000 TO {year_filter}12312359]'
                papers = reviewer.search(search_query, max_results=5, timeout=20)
            
            self._update_progress(task, 50, f"Found {len(papers)} papers")
            
            # Clear reviewer
            del reviewer
            gc.collect()
            
            # Phase 2: Generate Ideas (50-80%)
            self._update_progress(task, 60, "Generating ideas...")
            
            from agent.hypothesis import HypothesisGenerator
            hypo_gen = HypothesisGenerator(llm_provider=llm_provider)
            
            # Generate ideas using ONLY Groq (skip Oxlo)
            ideas = hypo_gen.generate_ideas_groq_only(papers, max_ideas=5)
            
            self._update_progress(task, 80, f"Generated {len(ideas)} ideas")
            
            # Phase 3: Create Report (80-100%)
            self._update_progress(task, 90, "Creating report...")
            
            # Generate simple report sections
            report_sections = {
                "introduction": self._generate_intro(query, papers, hypo_gen),
                "the_issue": self._generate_issue(query, hypo_gen),
                "conclusion": self._generate_conclusion(query, ideas, hypo_gen)
            }
            
            # Clear generator
            del hypo_gen
            gc.collect()
            
            # Save report
            from agent.report import ReportGenerator
            reporter = ReportGenerator(out_dir=self.output_dir)
            report_path = reporter.generate_simple_report(query, papers, ideas, report_sections)
            
            output_data = {
                'papers': papers,
                'ideas': ideas,
                'report_sections': report_sections,
                'report_formats': self._get_report_formats(report_path),
            }
            
            del reporter
            gc.collect()
            
            task.mark_completed(output_data)
            self._update_progress(task, 100, "Complete!")
            
            logger.info(f"[LIGHTWEIGHT] Task {self.task_id} completed successfully")
            return output_data
            
        except Exception as e:
            error_msg = str(e)
            error_traceback = traceback.format_exc()
            
            logger.error(f"Task {self.task_id} failed: {error_msg}", exc_info=True)
            
            # Log error to database
            ErrorLog.objects.create(
                source=ErrorLog.Source.BACKEND,
                error_code='AGENT_EXECUTION_ERROR',
                message=error_msg,
                context={'task_id': self.task_id, 'query': query[:100]},
                stack_trace=error_traceback,
                task=task
            )
            
            # Mark task as failed
            task.mark_failed(
                error_code='AGENT_EXECUTION_ERROR',
                error_message=error_msg,
                traceback=error_traceback
            )
            
            raise
    
    def _update_progress(self, task, progress: int, step: str):
        """Update task progress in database."""
        task.update_progress(progress, step)
        
        if self.on_progress:
            self.on_progress(step, progress)
        
        logger.debug(f"Task {self.task_id}: {progress}% - {step}")
    
    def _generate_intro(self, query, papers, hypo_gen):
        """Generate introduction using Groq."""
        try:
            prompt = f"Write a brief introduction for a research report on: {query}. Mention that {len(papers)} papers were analyzed."
            return hypo_gen.llm.generate(prompt, max_tokens=300)
        except:
            return f"This report analyzes {len(papers)} recent papers on {query}."
    
    def _generate_issue(self, query, hypo_gen):
        """Generate issue section using Groq."""
        try:
            prompt = f"Describe the main research challenge or issue in the field of: {query}"
            return hypo_gen.llm.generate(prompt, max_tokens=300)
        except:
            return f"The field of {query} faces several challenges that require further investigation."
    
    def _generate_conclusion(self, query, ideas, hypo_gen):
        """Generate conclusion using Groq."""
        try:
            prompt = f"Write a conclusion for a research report on {query}. We generated {len(ideas)} new research ideas."
            return hypo_gen.llm.generate(prompt, max_tokens=300)
        except:
            return f"This analysis of {query} has identified {len(ideas)} promising research directions for future work."
    
    def _get_report_formats(self, report_md_path: str) -> dict:
        """Get paths to all generated report formats."""
        if not report_md_path:
            return {}
        
        base_path = report_md_path.rsplit('.', 1)[0]
        formats = {}
        
        for ext, label in [('.md', 'markdown'), ('.docx', 'word'), ('.txt', 'text'), ('.json', 'json')]:
            path = f"{base_path}{ext}"
            if os.path.exists(path):
                formats[label] = path
        
        return formats
