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
        Execute the research pipeline with speed optimizations.
        Target: Complete in under 20 seconds.
        
        Args:
            task: ResearchTask model instance
            
        Returns:
            dict with papers, ideas, report_sections, report_formats
        """
        from research.models import ResearchTask, ErrorLog
        
        params = task.input_params
        query = params.get('query', '')
        mode = params.get('mode', 'Deep Research')
        year_filter = params.get('year_filter')
        llm_provider = params.get('llm_provider', 'groq')
        
        logger.info(f"Starting FAST research task {self.task_id}: {query[:50]}")
        
        # Mark task as running
        task.mark_running()
        
        try:
            # Import existing agent components
            from agent.lit_review import LiteratureReviewer
            from agent.hypothesis import HypothesisGenerator
            from agent.experiment import ExperimentDesigner, ExperimentEvaluator
            from agent.report import ReportGenerator
            
            # Initialize components
            reviewer = LiteratureReviewer(llm_provider=llm_provider)
            hypo_generator = HypothesisGenerator(llm_provider=llm_provider)
            designer = ExperimentDesigner()
            evaluator = ExperimentEvaluator()
            reporter = ReportGenerator(out_dir=self.output_dir)
            
            # Verify LLM is available
            if not reviewer.llm.available:
                error_msg = f"LLM provider '{llm_provider}' is not available. Check API keys and configuration."
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            # Phase 1: Quality Discovery (0-30%) - BALANCED
            self._update_progress(task, 5, "Refining search query...")
            
            if mode == "Web Search":
                papers = reviewer.web_search(query, num_results=5)
            else:
                # Use query as-is for speed (skip refinement)
                search_query = query
                if year_filter and year_filter > 0:
                    search_query = f'({query}) AND submittedDate:[{year_filter}01010000 TO {year_filter}12312359]'
                
                self._update_progress(task, 15, "Searching academic databases...")
                # BALANCED: 5 papers for quality/speed balance
                papers = reviewer.search(search_query, max_results=5, timeout=15)
            
            self._update_progress(task, 30, f"Found {len(papers)} papers, enriched with multi-LLM")
            
            # Phase 2: Quality Idea Generation (30-60%) - IMPROVED
            self._update_progress(task, 40, "Generating research ideas...")
            # QUALITY: Generate 5 ideas using Oxlo/Groq
            ideas = hypo_generator.generate_new_ideas(papers, max_ideas=5)
            self._update_progress(task, 60, f"Generated {len(ideas)} high-quality ideas")
            
            # Phase 3: Experiment Design (60-75%)
            self._update_progress(task, 65, "Designing experiments...")
            first_idea = ideas[0].get('description', '') if ideas else 'No idea generated'
            experiment = designer.design(first_idea)
            self._update_progress(task, 75, "Experiment designed")
            
            # Phase 4: Evaluation (75-85%)
            self._update_progress(task, 80, "Running evaluation...")
            results = evaluator.evaluate(experiment)
            self._update_progress(task, 85, "Evaluation complete")
            
            # Phase 5: Deep Synthesis Report (85-100%) - QUALITY
            self._update_progress(task, 90, "Generating comprehensive report...")
            # QUALITY: Use Gemini for deep synthesis
            report_sections = hypo_generator.generate_report_sections(query, papers, use_deep_synthesis=True)
            
            self._update_progress(task, 95, "Creating report files...")
            report_path = reporter.generate_report(
                query, papers, ideas, report_sections, experiment, results
            )
            
            # Build output data
            output_data = {
                'papers': papers,
                'ideas': ideas,
                'report_sections': report_sections,
                'report_formats': self._get_report_formats(report_path),
            }
            
            # Mark task as completed
            task.mark_completed(output_data)
            self._update_progress(task, 100, "Research complete")
            
            logger.info(f"Task {self.task_id} completed successfully with multi-LLM system (Groq+Gemini+Oxlo)")
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
