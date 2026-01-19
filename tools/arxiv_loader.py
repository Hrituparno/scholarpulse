from agent.lit_review import LiteratureReviewer


def load_arxiv(query: str, max_results: int = 5):
    """Convenience wrapper to fetch papers from arXiv."""
    return LiteratureReviewer().search(query, max_results=max_results)
