from agent.experiment import ExperimentEvaluator


def run_experiment(design: dict) -> dict:
    """Run an experiment design through the default evaluator."""
    return ExperimentEvaluator().evaluate(design)
