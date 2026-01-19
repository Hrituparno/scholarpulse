from agent.experiment import ExperimentDesigner


class ExperimentAgent:
    """Designs experiments from hypotheses."""

    def __init__(self):
        self.designer = ExperimentDesigner()

    def design(self, hypothesis):
        return self.designer.design(hypothesis)
