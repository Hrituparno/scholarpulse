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
        Execute the research pipeline with MEMORY OPTIMIZATION for Render free tier.
        Target: Use < 400MB RAM
        
        Args:
            task: ResearchTask model instance
            
        Returns:
            dict with papers, ideas, report_sections, report_formats
        """
        from research.models import ResearchTask, ErrorLog
        import gc  # Garbage collection for memory management
        
        params = task.input_params
        query = params.get('query', '')
        mode = params.get('mode', 'Deep Research')
        year_filter = params.get('year_filter')
        llm_provider = params.get('llm_provider', 'groq')
        
        logger.info(f"Starting MEMORY-OPTIMIZED research task {self.task_id}: {query[:50]}")
        
        # Mark task as running
        task.mark_running()
        
        try:
            # Import only what we need, when we need it (lazy loading)
            from agent.lit_review import LiteratureReviewer
            from agent.hypothesis import HypothesisGenerator
            
            # Phase 1: Paper Search (0-40%) - MINIMAL MEMORY
            self._update_progress(task, 5, "Searching papers...")
            
            reviewer = LiteratureReviewer(llm_provider=llm_provider)
            
            # Verify LLM is available
            if not reviewer.llm.available:
                error_msg = f"LLM provider '{llm_provider}' is not available. Check API keys."
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            # Search with minimal results to save memory
            if mode == "Web Search":
                papers = reviewer.web_search(query, num_results=3)  # Reduced from 5
            else:
                search_query = query
                if year_filter and year_filter > 0:
                    search_query = f'({query}) AND submittedDate:[{year_filter}01010000 TO {year_filter}12312359]'
                
                papers = reviewer.search(search_query, max_results=3, timeout=15)  # Reduced from 5
            
            self._update_progress(task, 40, f"Found {len(papers)} papers")
            
            # Clear reviewer from memory
            del reviewer
            gc.collect()
            
            # Phase 2: Idea Generation (40-70%) - MEMORY EFFICIENT
            self._update_progress(task, 50, "Generating ideas...")
            
            hypo_generator = HypothesisGenerator(llm_provider=llm_provider)
            ideas = hypo_generator.generate_new_ideas(papers, max_ideas=3)  # Reduced from 5
            
            self._update_progress(task, 70, f"Generated {len(ideas)} ideas")
            
            # Phase 3: Report Generation (70-100%) - LIGHTWEIGHT
            self._update_progress(task, 80, "Creating report...")
            
            # Generate lightweight report sections (no deep synthesis to save memory)
            report_sections = hypo_generator.generate_report_sections(
                query, papers, use_deep_synthesis=False  # Disabled to save memory
            )
            
            # Clear generator from memory
            del hypo_generator
            gc.collect()
            
            self._update_progress(task, 90, "Finalizing report...")
            
            # Import reporter only when needed
            from agent.report import ReportGenerator
            reporter = ReportGenerator(out_dir=self.output_dir)
            
            # Generate minimal report (skip experiment design to save memory)
            report_path = reporter.generate_simple_report(
                query, papers, ideas, report_sections
            )
            
            # Build output data
            output_data = {
                'papers': papers,
                'ideas': ideas,
                'report_sections': report_sections,
                'report_formats': self._get_report_formats(report_path),
            }
            
            # Clear reporter from memory
            del reporter
            gc.collect()
            
            # Mark task as completed
            task.mark_completed(output_data)
            self._update_progress(task, 100, "Research complete")
            
            logger.info(f"Task {self.task_id} completed (memory-optimized mode)")
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
