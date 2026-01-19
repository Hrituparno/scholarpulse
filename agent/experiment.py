import logging
import json
import textwrap
import random
from .llm import LLMClient

logger = logging.getLogger(__name__)

class ExperimentDesigner:
    """Designs a detailed experiment from a hypothesis using an LLM.

    Generates a dict describing:
      - objective: Detailed research goal
      - techniques: List of required methods/libraries
      - dataset: Suggested dataset
      - method: Proposed approach
      - metric: Evaluation metric
    """

    def __init__(self):
        self.llm = LLMClient()

    def design(self, hypothesis: str) -> dict:
        """Design an experiment based on the hypothesis."""
        default_design = {
            "hypothesis": hypothesis,
            "objective": "Investigate the proposed hypothesis to validate its claims.",
            "techniques": ["Standard training pipeline", "Cross-validation"],
            "dataset": "Synthetic or standard benchmark",
            "method": "Baseline vs Proposed",
            "metric": "Accuracy/Loss",
            "trials": 3,
        }

        if not self.llm.available:
            return default_design

        prompt = textwrap.dedent(f"""
            You are a senior research scientist. Based on the following hypothesis, design a concrete experiment.
            
            Hypothesis: "{hypothesis}"

            Output a JSON object with the following keys:
            - "objective": A detailed paragraph explaining the specific goal of this experiment.
            - "techniques": A list of specific algorithms, libraries, or mathematical techniques required (e.g., "LoRA", "PyTorchLightning", "AdamW optimizer").
            - "dataset": Name or description of a suitable dataset.
            - "method": Brief description of the experimental method comparison.
            - "metric": Primary evaluation metric.
            - "trials": Recommended number of trials (integer).

            Return ONLY the valid JSON object. Do not include markdown formatting or backticks.
        """)

        try:
            response_text = self.llm.generate(prompt, max_tokens=1024).strip()
            # Clean up potential markdown formatting via regex or simple strip
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            design = json.loads(response_text.strip())
            # Ensure all keys are present, fallback to defaults if missing
            for k, v in default_design.items():
                if k not in design:
                    design[k] = v
            
            # Ensure 'hypothesis' is in the final dict (LLM might not return it)
            design["hypothesis"] = hypothesis
            return design

        except Exception as e:
            logger.error(f"Failed to generate experiment design with LLM: {e}")
            return default_design


class ExperimentEvaluator:
    """Runs a lightweight simulated evaluation.

    This is a placeholder that returns deterministic-looking results so the
    pipeline can run offline.
    """

    def evaluate(self, experiment):
        base = 0.70
        improvement = random.uniform(0.005, 0.03)
        results = {
            "baseline": round(base, 4),
            "proposed": round(base + improvement, 4),
            "metric": experiment.get("metric"),
            "trials": experiment.get("trials"),
        }
        return results
