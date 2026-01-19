from agent.report import ReportGenerator


class WriterAgent:
    """Produces research-style reports."""

    def __init__(self, out_dir="output"):
        self.writer = ReportGenerator(out_dir=out_dir)

    def write(self, query, papers, hypothesis, experiment, results):
        return self.writer.generate_report(query, papers, hypothesis, experiment, results)
