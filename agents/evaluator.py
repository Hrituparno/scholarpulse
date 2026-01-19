from agent.experiment import ExperimentEvaluator


class EvaluatorAgent:
    """Evaluates experiments and returns results."""

    def __init__(self):
        self.evaluator = ExperimentEvaluator()

    def evaluate(self, experiment):
        return self.evaluator.evaluate(experiment)
