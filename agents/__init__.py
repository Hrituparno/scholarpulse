"""High-level agents package.

This package exposes the consolidated agent classes from `agents/agents.py`.
"""

from .agents import ResearchAgent, HypothesisAgent, ExperimentAgent, EvaluatorAgent, WriterAgent

__all__ = ["ResearchAgent", "HypothesisAgent", "ExperimentAgent", "EvaluatorAgent", "WriterAgent"]
