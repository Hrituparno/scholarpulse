from agent.hypothesis import HypothesisGenerator


class HypothesisAgent:
    """Generates testable hypotheses from paper summaries."""

    def __init__(self):
        self.generator = HypothesisGenerator()

    def generate(self, papers):
        return self.generator.generate_from_abstracts(papers)
