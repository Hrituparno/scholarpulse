from agent.lit_review import LiteratureReviewer
from agent.hypothesis import HypothesisGenerator
from agent.experiment import ExperimentDesigner, ExperimentEvaluator
from agent.report import ReportGenerator


class ResearchAgent:
    """Reads papers and provides structured results."""

    def __init__(self):
        self.reviewer = LiteratureReviewer()

    def fetch_papers(self, query: str, max_results: int = 5):
        return self.reviewer.search(query, max_results=max_results)


class HypothesisAgent:
    """Generates testable hypotheses from paper summaries."""

    def __init__(self):
        self.generator = HypothesisGenerator()

    def generate(self, papers):
        return self.generator.generate_from_abstracts(papers)


class ExperimentAgent:
    """Designs experiments from hypotheses."""

    def __init__(self):
        self.designer = ExperimentDesigner()

    def design(self, hypothesis):
        return self.designer.design(hypothesis)


class EvaluatorAgent:
    """Evaluates experiments and returns results."""

    def __init__(self):
        self.evaluator = ExperimentEvaluator()

    def evaluate(self, experiment):
        return self.evaluator.evaluate(experiment)


class WriterAgent:
    """Produces research-style reports."""

    def __init__(self, out_dir="output"):
        self.writer = ReportGenerator(out_dir=out_dir)

    def write(self, query, papers, hypothesis, experiment, results):
        return self.writer.generate_report(query, papers, hypothesis, experiment, results)
