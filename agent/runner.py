import logging
import json
import os
import time
from .lit_review import LiteratureReviewer
from .hypothesis import HypothesisGenerator
from .experiment import ExperimentDesigner, ExperimentEvaluator
from .report import ReportGenerator
from config import DEFAULT_OUTPUT_DIR, DEFAULT_QUERY, ARXIV_MAX_RESULTS

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class AgentRunner:
    def __init__(self, out_dir: str = DEFAULT_OUTPUT_DIR, callback: callable = None, llm_provider: str = None):
        self.out_dir = out_dir
        self.callback = callback
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)
            
        self.reviewer = LiteratureReviewer(llm_provider=llm_provider)
        self.hypo = HypothesisGenerator(llm_provider=llm_provider)
        self.designer = ExperimentDesigner()
        self.evaluator = ExperimentEvaluator()
        self.reporter = ReportGenerator(out_dir=self.out_dir)

    def notify(self, message: str):
        """Standard notification method for console and UI."""
        logger.info(message)
        if self.callback:
            self.callback(message)
        else:
            print(f"[ScholarPulse] {message}")

    def _save_checkpoint(self, name: str, data: any):
        """Save intermediate data to a JSON file."""
        try:
            path = os.path.join(self.out_dir, f"{name}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save checkpoint {name}: {e}")

    def run_demo(self, query: str = DEFAULT_QUERY, live: bool = False, year: int = None, mode: str = "Deep Research"):
        """Run the demo pipeline with multi-mode support."""
        query = query or DEFAULT_QUERY
        self.notify(f"Mode: {mode} | Query: {query}" + (f" (Timeline: {year})" if year else ""))

        try:
            # 1. Discovery Phase
            if mode == "Web Search":
                papers = self.reviewer.web_search(query)
                self.notify(f"Discovered {len(papers)} live web sources.")
            else:
                papers = self._run_search(query, live, year)
            
            self._save_checkpoint("step_1_papers", papers)

            # Enrich web results if needed (already mostly structured)
            if mode == "Web Search" and self.reviewer.llm.available and papers:
                from concurrent.futures import ThreadPoolExecutor
                with ThreadPoolExecutor(max_workers=len(papers)) as executor:
                    executor.map(self.reviewer._enrich_paper, papers)
            
            self._save_checkpoint("step_1_papers", papers)

            # 2. Idea Generation
            new_ideas = self._run_idea_generation(papers, live)
            self._save_checkpoint("step_2_new_ideas", new_ideas)

            # 3. Experiment Design
            first_idea_desc = new_ideas[0].get("description", "") if isinstance(new_ideas, list) and new_ideas else "No idea generated"
            experiment = self._run_experiment_design(first_idea_desc, live)
            self._save_checkpoint("step_3_experiment", experiment)

            # 4. Evaluation
            results = self._run_evaluation(experiment, live)
            self._save_checkpoint("step_4_results", results)

            # 4.5 Generate Report Narrative
            report_sections = self._run_narrative_generation(query, papers, live)
            self._save_checkpoint("step_4_5_narrative", report_sections)

            # 5. Report Generation
            report_path = self._run_report(query, papers, new_ideas, report_sections, experiment, results)
            return report_path, papers
            
        except Exception as e:
            self.notify(f"Pipeline failed: {e}")
            logger.error(f"Error details:", exc_info=True)
            return None, []

    def _run_search(self, query, live, year=None):
        # Professional Query Refinement
        refined_query = self.reviewer.refine_query(query)
        self.notify(f"Translated intent into: {refined_query}")
        
        # Emergency Failsafe: Never allow an empty query to hit the API
        if not refined_query or len(refined_query.strip()) < 2:
            refined_query = query
            
        search_query = refined_query
        if year:
            # Wrap the entire expression to prevent 400 errors with unbalanced logic
            search_query = f'({refined_query}) AND submittedDate:[{year}01010000 TO {year}12312359]'
            
        self.notify(f"Searching archives for: {search_query}")
        papers = self.reviewer.search(search_query, max_results=ARXIV_MAX_RESULTS)
        self.notify(f"Found {len(papers)} papers from {year if year else 'all time'}. analyzing...")
        
        if live and not self.callback:
            print("\n[ScholarPulse] Top Papers (Analysis):")
            for i, p in enumerate(papers, start=1):
                print(f"{i}. {p['title']}")
                print(f"   Objective: {p.get('objective', 'N/A')}")
                print(f"   Techniques: {p.get('techniques', [])}\n")
        return papers

    def _run_idea_generation(self, papers, live):
        self.notify("Generating 9 unique research ideas...")
        ideas = self.hypo.generate_new_ideas(papers)
        
        if live and isinstance(ideas, list) and not self.callback:
            print(f"[ScholarPulse] Generated {len(ideas)} Ideas:\n")
            for i, idea in enumerate(ideas, 1):
                print(f"Idea {i}: {idea.get('title')}")
                print(f" - {idea.get('description')}\n")
        return ideas

    def _run_experiment_design(self, hypothesis, live):
        self.notify("Designing detailed experiment for first idea...")
        return self.designer.design(hypothesis)

    def _run_evaluation(self, experiment, live):
        self.notify("Evaluating (Simulation)...")
        return self.evaluator.evaluate(experiment)

    def _run_narrative_generation(self, query, papers, live):
        self.notify("Synthesizing Introduction, Issue, and Conclusion...")
        return self.hypo.generate_report_sections(query, papers)

    def _run_report(self, query, papers, new_ideas, report_sections, experiment, results):
        self.notify("Generating report (saved to output)...")
        report_path = self.reporter.generate_report(query, papers, new_ideas, report_sections, experiment, results)
        self.notify(f"Report saved to: {report_path}")
        return report_path
